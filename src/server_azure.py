# server.py

import requests
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from collections import defaultdict
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import Dict, List, Any
import uvicorn
import logging
import time

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = "https://<your-resource-name>.openai.azure.com/"  # Replace with your Azure OpenAI endpoint
AZURE_OPENAI_API_KEY = "<your-azure-api-key>"  # Replace with your Azure API key
AZURE_DEPLOYMENT_CHAT = "<your-chat-deployment-name>"  # Replace with your chat model deployment name
AZURE_DEPLOYMENT_EMBEDDING = "<your-embedding-deployment-name>"  # Replace with your embedding model deployment name

# Initialize logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()

# Serve static files for HTML and assets
app.mount("/static", StaticFiles(directory="."), name="static")

# Define a function to handle retries in case of rate limit errors
def get_embedding_with_retry(text, retries=3, delay=5):
    """Fetch embedding from Azure OpenAI with retries."""
    for attempt in range(retries):
        try:
            url = f"{AZURE_OPENAI_ENDPOINT}openai/deployments/{AZURE_DEPLOYMENT_EMBEDDING}/embeddings?api-version=2023-03-15-preview"
            headers = {"Content-Type": "application/json", "api-key": AZURE_OPENAI_API_KEY}
            payload = {"input": text}
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            embedding = response.json()["data"][0]["embedding"]
            logger.info(f"Embedding generated for text: {text[:50]}...")
            return embedding
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error fetching embedding: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
    logger.error(f"Failed to get embedding after {retries} retries for text: {text[:50]}")
    raise Exception("Failed to get embedding after retries")

# Generate a title for each group based on its content
def generate_group_title(requirements: List[str]) -> str:
    """Generate a title for a group of requirements using Azure GPT."""
    prompt = (
        "Create a concise and descriptive title for a group of customer requirements "
        "that share a common theme:\n\nRequirements:\n" +
        "\n".join(f"- {req}" for req in requirements) +
        "\n\nTitle:"
    )
    
    url = f"{AZURE_OPENAI_ENDPOINT}openai/deployments/{AZURE_DEPLOYMENT_CHAT}/chat/completions?api-version=2023-03-15-preview"
    headers = {"Content-Type": "application/json", "api-key": AZURE_OPENAI_API_KEY}
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 10,
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        title = response.json()["choices"][0]["message"]["content"].strip()
        title = title.strip('"').strip("'")  # Clean up stray quotes
        logger.info(f"Generated title: {title}")
        return title
    except requests.exceptions.RequestException as e:
        logger.error(f"Error generating title: {e}")
        raise Exception("Failed to generate title")


# Endpoint to serve the HTML interface
@app.get("/", response_class=HTMLResponse)
async def read_index():
    """Serve the HTML page for the web interface."""
    try:
        with open("index.html", "r") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        logger.error("index.html file not found.")
        raise HTTPException(status_code=404, detail="index.html not found")

# Endpoint to perform clustering on customer requirements
@app.get("/cluster-requirements", response_model=Dict[int, Dict[str, Any]])
async def cluster_requirements(distance_threshold: float = Query(0.7, description="Distance threshold for clustering")):
    logger.info(f"Received request to /cluster-requirements with distance_threshold={distance_threshold}")

    # Read customer requirements from a file
    try:
        with open('customer_requirements.txt', 'r') as f:
            customer_requirements = [line.strip() for line in f if line.strip()]
        logger.info(f"Loaded {len(customer_requirements)} customer requirements from file.")
    except FileNotFoundError:
        logger.error("customer_requirements.txt file not found.")
        raise HTTPException(status_code=404, detail="customer_requirements.txt not found")
    
    # Generate embeddings
    embeddings = []
    for req in customer_requirements:
        embedding = get_embedding_with_retry(req)
        embeddings.append(embedding)
    logger.info("All embeddings generated successfully.")

    # Convert embeddings to a NumPy array
    embedding_array = np.array(embeddings)

    # Perform hierarchical clustering using the user-specified distance_threshold
    cluster = AgglomerativeClustering(n_clusters=None, 
                                      metric='euclidean', 
                                      linkage='ward',
                                      distance_threshold=distance_threshold)
    
    cluster.fit(embedding_array)
    labels = cluster.labels_
    logger.info("Clustering completed successfully.")

    # Organize requirements into groups and generate titles
    groups_with_titles = {}
    groups = defaultdict(list)
    for label, requirement in zip(labels, customer_requirements):
        groups[label].append(requirement)

    for label, requirements in groups.items():
        title = generate_group_title(requirements)
        groups_with_titles[label] = {"title": title, "requirements": requirements}

    logger.info(f"Organized requirements into {len(groups_with_titles)} groups with titles.")

    # Return groups with titles as JSON
    return groups_with_titles

# Run the FastAPI app
if __name__ == "__main__":
    logger.info("Starting the FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8100)
