# src/main.py
import logging
import uvicorn
from fastapi import Body, FastAPI, HTTPException, Query
from app.core.use_cases.manage_strategies_use_case import ManageStrategiesUseCase
from app.logging_config import setup_logging
from app.adapters.scraper_factory import ScraperFactory
from app.services.scraping_service import ScrapingService
from app.services.strategy_service import StrategyService
from app.services.data_cleaning_service import DataCleaningService
from app.core.use_cases.extract_data_use_case import ExtractDataUseCase
from app.core.database.mongo_repository import MongoRepository, MongoStrategyRepository
from app.adapters.ocr.tesseract import TesseractOCR
import os

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

data_cleaning_service = DataCleaningService()
mongo_strategy_repo = MongoStrategyRepository(os.getenv('MONGO_URI'), 'scraping_db')
strategy_service = StrategyService(mongo_strategy_repo)

mongo_repo = MongoRepository(os.getenv('MONGO_URI'), 'scraping_db', 'scraping_collection')

tesseract_ocr = TesseractOCR()
extract_data_use_case = ExtractDataUseCase(mongo_repo, data_cleaning_service)

@app.get("/api/scrape")
async def scrape(url: str, max_pages: int = Query(5, description="Maximum number of pages to scrape")):
    logger.info(f"Received scrape request for URL: {url} with max_pages: {max_pages}")
    try:
        scraper = ScraperFactory.get_scraper(url, ManageStrategiesUseCase(mongo_strategy_repo), mongo_repo)
        scraping_service = ScrapingService(scraper, mongo_repo)
        data = scraping_service.scrape(url, max_pages)
        logger.info(f"Scraping successful for URL: {url}")
        return data
    except ValueError as e:
        logger.error(f"ScraperFactory error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.get("/api/extract")
async def extract(criteria: str):
    try:
        data = extract_data_use_case.extract_and_clean_data(criteria)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ocr")
async def ocr(image_path: str):
    try:
        text = tesseract_ocr.extract_text(image_path)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/strategies")
async def add_strategy(strategy: dict = Body(...)):
    try:
        strategy_service.add_strategy(strategy)
        return {"message": "Strategy added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/strategies")
async def get_strategies():
    try:
        return strategy_service.get_strategies()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/strategies/{website}")
async def delete_strategy(website: str):
    try:
        strategy_service.delete_strategy(website)
        return {"message": "Strategy deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
