"""
This file is responsible for routing the incoming requests to the respective endpoints.
"""

from fastapi.responses import JSONResponse
from fastapi import APIRouter, Request
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
import logging

from services.chat import ChatService
from models.company import Company
from services.embedding import Embedding
from models.database import get_db_session
from services.redis_service import RedisService
from services.qdrant_searcher import QdrantSearcher
from fastapi import HTTPException

api_router = APIRouter()
templates = Jinja2Templates(directory="templates")
chat_service = ChatService()
embedding_util = Embedding()
redis_service = RedisService()
logger = logging.getLogger(__name__)

class CompanyCreate(BaseModel):
    name: str
    description: str
    industry: str
    size: str
    location: str


class SearchRequest(BaseModel):
    query: str

@api_router.post("/companies")
async def add_company(company: CompanyCreate):
    content = f"{company.name}\n{company.description}\n{company.industry}\n{company.size}\n{company.location}"
    
    try:
        logger.info(f"Generating Pinecone embedding for company: {company.name}")
        embedding = embedding_util.generate_pinecone(content, 1024)
        logger.info(f"Successfully generated Pinecone embedding for company: {company.name}")
    except Exception as e:
        logger.error(f"Error generating Pinecone embedding: {e}")
        logger.info(f"Falling back to OpenAI embedding for company: {company.name}")
        try:
            embedding = embedding_util.generate(content, 1024)
        except Exception as openai_error:
            logger.error(f"Error generating OpenAI embedding: {openai_error}")
            raise HTTPException(status_code=500, detail="Failed to generate embeddings")
    
    new_company = Company(
        name=company.name,
        description=company.description,
        industry=company.industry,
        size=company.size,
        location=company.location,
        content=content,
        embedding=embedding
    )
    
    with get_db_session() as session:
        session.add(new_company)
        session.commit()
        session.refresh(new_company)
    
    if chat_service.use_qdrant:
        qdrant_searcher = QdrantSearcher(Company)
        qdrant_searcher.upsert_company(new_company)
    
    await redis_service.delete("all_companies")
    await redis_service.scan_and_delete("search_company:*")
    
    return {"message": "Company added successfully"}


@api_router.post("/search-company", response_class=JSONResponse)
async def search_company(search_request: SearchRequest):
    cache_key = f"search_company:{search_request.query}"
    cached_results = await redis_service.get(cache_key)
    
    if cached_results:
        return {
            "response": cached_results["response"],
            "company_recommendations": cached_results["company_recommendations"],
            "source": "cache"
        }

    response, company_recommendations = chat_service.generate_response(
        search_request.query
    )
    
    results = {
        "response": response,
        "company_recommendations": [company.to_dict() for company in company_recommendations]
    }
    
    await redis_service.set(cache_key, results, 3600)
    
    return {
        **results,
        "source": "database"
    }


@api_router.get("/companies", response_class=JSONResponse)
async def get_companies():
    """Get all companies with Redis caching"""
    cache_key = "all_companies"
    
    cached_companies = await redis_service.get(cache_key)
    if cached_companies:
        return {
            "companies": cached_companies,
            "source": "cache"
        }

    try:
        with get_db_session() as session:
            companies = session.query(Company).order_by(Company.created_at.desc()).all()
            companies_dict = [company.to_dict() for company in companies]
            
            await redis_service.set(cache_key, companies_dict, 3600)
            
            return {
                "companies": companies_dict,
                "source": "database"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/companies/{company_id}")
async def delete_company(company_id: int):
    try:
        with get_db_session() as session:
            company = session.query(Company).filter(Company.id == company_id).first()
            if not company:
                raise HTTPException(status_code=404, detail="Company not found")
            
            session.delete(company)
            session.commit()
            
        # Clear cache after deletion
        await redis_service.delete("all_companies")
        await redis_service.scan_and_delete("search_company:*")
        
        return {"message": "Company deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
