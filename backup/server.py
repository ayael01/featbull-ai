# server.py

import openai
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from collections import defaultdict
import json
import time
import scipy.cluster.hierarchy as sch
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import Dict, List
import uvicorn
import logging
import os

# Initialize logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()

# Load the API key from a file
try:
    with open('api_key.txt', 'r') as f:
        openai.api_key = f.read().strip()
    logger.info("API key loaded successfully.")
except FileNotFoundError:
    logger.error("API key file 'api_key.txt' not found.")
    raise

# Serve static files for HTML and assets
app.mount("/static", StaticFiles(directory="."), name="static")

# Define a function to handle retries in case of rate limit errors
def get_embedding_with_retry(text, retries=3, delay=5):
    """Fetch embedding with retries and delay in case of rate limit errors."""
    for attempt in range(retries):
        try:
            response = openai.Embedding.create(
                input=text,
                model="text-embedding-ada-002"
            )
            logger.info(f"Embedding generated for text: {text[:50]}...")
            return response['data'][0]['embedding']
        except openai.error.RateLimitError:
            logger.warning(f"Rate limit hit for text: {text[:50]}. Retrying in {delay} seconds...")
            time.sleep(delay)  # Wait before retrying
    logger.error(f"Failed to get embedding after {retries} retries for text: {text[:50]}")
    raise Exception("Failed to get embedding after retries")

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
@app.get("/cluster-requirements", response_model=Dict[int, List[str]])
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

    # Organize requirements into groups
    groups = defaultdict(list)
    for label, requirement in zip(labels, customer_requirements):
        groups[label].append(requirement)
    logger.info(f"Organized requirements into {len(groups)} groups.")

    # Return groups as JSON
    return {int(k): v for k, v in groups.items()}

# Run the FastAPI app
if __name__ == "__main__":
    logger.info("Starting the FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8100)
