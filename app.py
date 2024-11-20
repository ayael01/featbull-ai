import logging
import logging.config
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

from src.routes import calls_route



# Load environment variables from .env file
load_dotenv()

# Basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: [%(name)s] - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

app = FastAPI()

# Include API routers
app.include_router(calls_route.router)

# Load index.html
@app.get("/", response_class=HTMLResponse)
async def read_index():
    """Serve the HTML page for the web interface."""
    with open("static/index.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    logger.info("Serving index.html")
    return HTMLResponse(content=html_content)
