# server.py

import openai
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from collections import defaultdict
import time
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import Dict, List, Any
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

# Generate a title for each group based on its content
def generate_group_title(requirements: List[str]) -> str:
    """Generate a title for a group of requirements using GPT-3.5 and clean it up."""
    prompt = (
        "Create a concise and descriptive title for a group of customer requirements "
        "that share a common theme:\n\nRequirements:\n" +
        "\n".join(f"- {req}" for req in requirements) +
        "\n\nTitle:"
    )
    
    # Using gpt-3.5-turbo model
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=10,
        temperature=0.7
    )
    
    # Clean up the title to ensure it doesn't have any stray quotation marks
    title = response['choices'][0]['message']['content'].strip()
    title = title.strip('"').strip("'")  # Remove any leading or trailing quotes
    logger.info(f"Generated title: {title}")
    return title

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
