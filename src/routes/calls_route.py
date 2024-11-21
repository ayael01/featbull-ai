import logging
import os

from fastapi import APIRouter, Depends, HTTPException
from requests import HTTPError
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.azure import azure_client
from src.schemas.schemas import CallResponse
from src.db.db_client import get_session
from src.gong.gong_client import GongClient
from src.db.db_models import Customer, FeatureRequest, Topic

logger = logging.getLogger(__name__)

router = APIRouter()
gong_client = GongClient(os.getenv('GONG_USERNAME'),  # type: ignore
                         os.getenv('GONG_PASSWORD'))  # type: ignore


@router.get("/calls")
async def get_calls(db: Session = Depends(get_session)):
    try:
        calls = gong_client.get_extensive_calls()
        if calls:
            return _filter_calls(calls, db)

    except HTTPError as e:
        logger.error("Failed to get calls: %s", e.response.text)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/calls/{call_id}/process")
async def get_transcription(call_id: str, db: Session = Depends(get_session)):
    try:
        transcription: dict = gong_client.get_transcription(
            [call_id])  # type: ignore
        prompt_result = azure_client.generate_fr_from_call(
            str(transcription.get("callTranscripts")))
        topics = db.query(Topic).all()
        topic_titles = [topic.title for topic in topics]
        processed_result = azure_client.process_feature_requests(
            prompt_result, distance_threshold=0.6, titles=topic_titles)

        call_extensive_data = gong_client.get_extensive_calls(
            call_id)[0]  # type: ignore
        customer_name = call_extensive_data.customer_name  # type: ignore
        time = call_extensive_data.started
        new_titles = []
        for item in processed_result:
            if item.title not in topic_titles:
                new_titles.append(item.title)
                new_topic = Topic(title=item.title)
                db.add(new_topic)

            for feature_request in item.feature_requests:
                new_feature_request = FeatureRequest(
                    title=item.title,
                    customer_name=customer_name,
                    description=feature_request,
                    time=time
                )
                db.add(new_feature_request)
        db.commit()

        return processed_result

    except HTTPError as e:
        logger.error("Failed to get transcription for call %s: %s",
                     call_id, e.response.text)
        raise HTTPException(status_code=500, detail=str(e)) from e
    
@router.get("/calls/processed")
async def get_processed_calls(db: Session = Depends(get_session)):
    try:
        feature_requests = db.query(FeatureRequest).all()
        result = {}
        for fr in feature_requests:
            if fr.title not in result:
                result[fr.title] = {
                    "title": fr.title,
                    "feature_requests": [],
                    "score": 0
                }
            customer = db.query(Customer).filter(Customer.name == fr.customer_name).first()
            customer_score = customer.score if customer else 0
            result[fr.title]["feature_requests"].append({
                "time": fr.time,
                "score": customer_score,
                "description": fr.description,
                "customer": fr.customer_name
            })
            result[fr.title]["score"] += customer_score

        return list(result.values())

    except Exception as e:
        logger.error("Failed to get processed calls: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


def _filter_calls(calls: list[CallResponse], db: Session):
    filtered_calls = []
    for call in calls:
        customer_name = call.customer_name
        if customer_name:
            customer = db.query(Customer).filter(func.lower(
                Customer.name) == customer_name.lower()).first()
            if customer:
                filtered_calls.append(call)
    return filtered_calls
