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
from src.db.db_models import Customer

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


@router.get("/calls/{call_id}/transcription")
async def get_transcription(call_id: str):
    try:
        transcription: dict = gong_client.get_transcription([call_id]) # type: ignore
        prompt_result = azure_client.generate_fr_from_call(str(transcription.get("callTranscripts")))
        processed_result = azure_client.process_requirements(prompt_result, distance_threshold=0.6)

        return processed_result

    except HTTPError as e:
        logger.error("Failed to get transcription for call %s: %s", call_id, e.response.text)
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
