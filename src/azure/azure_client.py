import json
import logging
import os
from collections import defaultdict
from typing import List

import numpy as np
import openai
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity

openai.api_key = os.environ.get('AZURE_API_KEY')
openai.api_type = "azure"
openai.api_base = "https://hackathon-ai-2.openai.azure.com/"

# Configuration
API_KEY = os.environ.get("AZURE_API_KEY")

logger = logging.getLogger(__name__)


def generate_fr_from_call(transcription: str):
    logger.info(f"Generating feature requests from transcription")
    response = openai.ChatCompletion.create(
        engine="gpt-4",
        messages=[
            {"role": "system",
             "content": [{"type": "text", "text": "Title: Feature Request Extraction for Anecdotes.ai Product Enhancements Instructions: Review Background Material: Familiarize yourself with the existing features and capabilities of the Anecdotes.ai product by visiting the help section on help.anecdotes.ai. Understand the current functionalities offered to GRC managers in tech, healthcare, and finance sectors. Analyze Customer Transcripts: You will be provided with transcripts from customer calls recorded on the Gong platform. Read through these transcripts carefully. Identify Feature Requests: Extract statements or discussions where customers mention specific needs, suggestions, or improvements related to the Anecdotes.ai product. Focus on capturing direct quotes that reflect the customer's voice and specific requests. Categorize Requests: Classify the extracted features into relevant categories such as usability enhancements, new feature suggestions, integration requests, performance improvements, etc. If applicable, note which sector (tech, healthcare, finance) the feature request is most relevant to. Summarize and Report: Create a concise summary of each feature request. Provide context or additional comments from the transcript that help clarify the customer's need or the potential impact of the requested feature. Prioritize for Impact: Optionally, you can add your own assessment of the potential impact or value of each feature request based on the frequency of the request across different transcripts and its relevance to the current market needs. can you share in the following template: JSON file one liner - array of all requests (without category / summary - only the requests) in one liner For example: [\"feature request 1 (\\\"original quote from the customer\\\"),  \"feature request 2\" (\\\"original quote from the customer\\\")......] in one line Context: As a product manager at Anecdotes.ai, your role involves continually enhancing the product to meet the evolving needs of GRC managers in various sectors. The insights gathered from customer calls are crucial for driving product development that is closely aligned with user requirements. Accurate extraction and analysis of feature requests from these calls will directly influence the prioritization and implementation of new features in the Anecdotes.ai roadmap. Your work will contribute to the product's effectiveness and customer satisfaction, ensuring that Anecdotes.ai remains a competitive and valuable tool for GRC managers."}]},
            {"role": "user", "content": [
                {"type": "text", "text": transcription}]}
        ],
        max_tokens=800,
        temperature=0.7,
        api_version="2024-02-15-preview")
    logger.info(response.get(
        "choices")[0].get("message").get("content"))
    # return response.get("choices")[0].get("message").get("content")
    feature_requests = json.loads(response.get(
        "choices")[0].get("message").get("content"))
    return feature_requests


def _get_embedding(text: str):
    response = openai.Embedding.create(
        input=text,
        engine="text-embedding-ada-002",
        api_version="2023-05-15"
    )
    logger.info(f"Embedding generated for text: {text[:50]}...")
    return response['data'][0]['embedding']  # type: ignore


def _generate_group_title(requirements: List[str]) -> str:
    """Generate a title for a group of requirements using GPT-4 and clean it up."""
    prompt = (
        "Create a concise and descriptive title for a group of customer requirements "
        "that share a common theme:\n\nRequirements:\n" +
        "\n".join(f"- {req}" for req in requirements) +
        "\n\nTitle:"
    )

    # Using GPT-4 model deployed on Azure
    response = openai.ChatCompletion.create(
        engine="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=10,
        temperature=0.7,
        api_version="2024-08-01-preview"
    )

    # Clean up the title to ensure it doesn't have any stray quotation marks
    title = response['choices'][0]['message']['content'].strip().strip(
        '"').strip("'")  # type: ignore
    logger.info(f"Generated title: {title}")
    return title


class FeatureRequestGroup:
    def __init__(self, title: str, feature_requests: List[str]):
        self.title = title
        self.feature_requests = feature_requests

    def __repr__(self):
        return f"FeatureRequestGroup(title={self.title}, feature_requests={self.feature_requests})"


def process_feature_requests(feature_requests: List[str], distance_threshold: float = 0.6, titles: List[str] = []) -> List[FeatureRequestGroup]:
    """
    Process a list of requirements, assign them to existing titles based on similarity,
    and cluster unassigned requirements to generate new titles.
    """
    logger.info(
        f"Processing {len(feature_requests)} requirements with distance_threshold={distance_threshold}.")

    # Generate embeddings for requirements
    embeddings = []
    for req in feature_requests:
        embedding = _get_embedding(req)
        embeddings.append(embedding)
    logger.info("All embeddings for requirements generated successfully.")

    groups_with_titles = []
    unassigned_requirements = []
    unassigned_embeddings = []

    if titles:
        # Generate embeddings for titles
        title_embeddings = []
        for title in titles:
            embedding = _get_embedding(title)
            title_embeddings.append(embedding)
        title_embeddings = np.array(title_embeddings)
        logger.info("All embeddings for titles generated successfully.")

        # Initialize groups_with_titles with existing titles
        groups_with_titles = [FeatureRequestGroup(
            title, []) for title in titles]

        # For each requirement, compute similarity to each title
        for idx, (req_embedding, req_text) in enumerate(zip(embeddings, feature_requests)):
            similarities = cosine_similarity(
                [req_embedding], title_embeddings)[0]
            max_similarity = np.max(similarities)
            max_index = np.argmax(similarities)
            # Set a similarity threshold
            similarity_threshold = 0.7
            if max_similarity >= similarity_threshold:
                # Assign to the group with max similarity
                groups_with_titles[max_index].feature_requests.append(req_text)
            else:
                # Requirement does not fit any existing title
                unassigned_requirements.append(req_text)
                unassigned_embeddings.append(req_embedding)
        logger.info(
            f"Assigned requirements to existing titles. {len(unassigned_requirements)} requirements unassigned.")

    else:
        # If no titles provided, consider all requirements as unassigned
        unassigned_requirements = feature_requests
        unassigned_embeddings = embeddings
        logger.info(
            "No existing titles provided. All requirements are unassigned.")

    # Handle unassigned requirements
    if unassigned_requirements:
        if len(unassigned_embeddings) >= 2:
            # Perform hierarchical clustering on unassigned requirements
            cluster = AgglomerativeClustering(
                n_clusters=None,
                metric='euclidean',
                linkage='ward',
                distance_threshold=distance_threshold
            )
            cluster.fit(unassigned_embeddings)
            labels = cluster.labels_
            logger.info(
                "Clustering unassigned requirements completed successfully.")

            # Organize unassigned requirements into groups and generate titles
            unassigned_groups = defaultdict(list)
            for label, requirement in zip(labels, unassigned_requirements):
                unassigned_groups[label].append(requirement)

            for group_reqs in unassigned_groups.values():
                title = _generate_group_title(group_reqs)
                groups_with_titles.append(
                    FeatureRequestGroup(title, group_reqs))

        else:
            # Only one unassigned requirement, generate a title for it
            req_text = unassigned_requirements[0]
            title = _generate_group_title([req_text])
            groups_with_titles.append(FeatureRequestGroup(title, [req_text]))
        logger.info(
            f"Generated titles for {len(groups_with_titles)} groups including unassigned requirements.")

    return groups_with_titles
