"""
This file is responsible for routing the incoming requests to the respective endpoints.
"""

from fastapi.responses import JSONResponse
from fastapi import APIRouter
from pydantic import BaseModel
import logging
from typing import Optional, Dict, Any

from services.chat import ChatService
from models.company import Company
from services.embedding import Embedding
from models.database import get_db_session
from services.redis_service import RedisService
from fastapi import HTTPException
import httpx
from config.main import config

api_router = APIRouter()
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
    # Optional client-provided weights for MCDA
    weights: Optional[Dict[str, float]] = None
    # Optional flag to enable MCDA re-ranking
    sort_by: Optional[str] = None  # "relevance" | "name" | "mcda"
    # Optional: if true, enable web search tool instead of DB search
    web_search: Optional[bool] = False

@api_router.post("/companies")
async def add_company(company: CompanyCreate):
    content = f"{company.name}\n{company.description}\n{company.industry}\n{company.size}\n{company.location}"
    
    # Guard against duplicates (same name + location)
    try:
        with get_db_session() as session:
            exists = session.query(Company).filter(
                Company.name == company.name,
                Company.location == company.location,
            ).first()
            if exists:
                return {"message": "Company already exists; skipped"}
    except Exception as e:
        logger.error(f"Error checking for duplicates: {e}")

    try:
        logger.info(f"Generating Pinecone embedding for company: {company.name}")
        embedding = embedding_util.generate_pinecone(content, 1024)
        logger.info(f"Successfully generated Pinecone embedding for company: {company.name}")
    except Exception as e:
        logger.error(f"Error generating Pinecone embedding: {e}")
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
    
    # Sync to vector DB not required; using PostgreSQL only
    
    await redis_service.delete("all_companies")
    await redis_service.scan_and_delete("search_company:*")
    
    return {"message": "Company added successfully"}


@api_router.post("/search-company", response_class=JSONResponse)
async def search_company(search_request: SearchRequest):
    logger.info(
        "Incoming search request: q='%s', sort_by=%s, web_search=%s",
        search_request.query,
        search_request.sort_by,
        bool(search_request.web_search),
    )
    # Determine if web search tool will actually be enabled (requires SERP_API_KEY)
    web_enabled = bool(search_request.web_search) and bool(config.SERP_API_KEY)
    cache_key = (
        f"search_company:{search_request.query}:{search_request.sort_by}:"
        f"{search_request.weights}:tool={'web' if web_enabled else 'db'}"
    )
    cached_results = await redis_service.get(cache_key)
    
    if cached_results:
        logger.info("Cache hit for key=%s; skipping tool call", cache_key)
        return {
            "response": cached_results["response"],
            "company_recommendations": cached_results["company_recommendations"],
            "source": "cache"
        }

    response, company_recommendations = chat_service.generate_response(
        search_request.query,
        web_search=web_enabled,
    )

    # Optional MCDA re-ranking via Haskell microservice
    if search_request.sort_by == "mcda" and company_recommendations:
        try:
            # Derive simple features for MCDA
            candidates = []
            for company in company_recommendations:
                # Basic binary features using query keyword presence (placeholder/simple heuristic)
                q = search_request.query.lower()
                # Support both ORM objects and plain dicts
                if isinstance(company, dict):
                    description = (company.get("description") or "")
                    industry = (company.get("industry") or "")
                    location = (company.get("location") or "")
                    cid = company.get("id")
                else:
                    description = (company.description or "")
                    industry = (company.industry or "")
                    location = (company.location or "")
                    cid = company.id
                text_blob = f"{description} {industry} {location}".lower()
                text_match = 1.0 if any(token in text_blob for token in q.split()) else 0.0
                # Without direct access to vector similarity score per item here, approximate with position
                # Earlier items presumed more relevant. Convert index to decreasing score.
                # Normalize later in service, but give a hint here.
                candidates.append({
                    "id": cid,
                    "features": {
                        "text": float(text_match),
                        # Placeholder relevance using order; real impl could retrieve similarity from DB
                        "relevance": 1.0,
                        # Simple categorical matches if user query mentions them
                        "industry": 1.0 if industry and industry.lower() in q else 0.0,
                        "location": 1.0 if location and location.lower() in q else 0.0,
                    }
                })

            payload = {
                "candidates": candidates,
                "weights": search_request.weights or {"relevance": 0.6, "text": 0.25, "location": 0.1, "industry": 0.05},
                "method": "topsis"
            }
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.post(f"{config.MCDA_URL}/rank", json=payload)
                r.raise_for_status()
                data = r.json()
            order = {item["id"]: item["score"] for item in data.get("rankedCandidates", [])}
            # Sort supporting both ORM objects and dicts
            def get_id(c):
                return c.get("id") if isinstance(c, dict) else c.id
            company_recommendations.sort(key=lambda c: order.get(get_id(c), 0), reverse=True)
        except Exception as e:  # on failure, fall back silently
            logger.error(f"MCDA ranking failed: {e}")
    
    # Deduplicate by company id while preserving order
    seen_ids: set[int] = set()
    unique_companies = []
    for company in company_recommendations:
        cid = company.get("id") if isinstance(company, dict) else company.id
        if cid not in seen_ids:
            seen_ids.add(cid)
            unique_companies.append(company)

    results = {
        "response": response,
        "company_recommendations": [
            company if isinstance(company, dict) else company.to_dict()
            for company in unique_companies
        ]
    }
    
    await redis_service.set(cache_key, results, 3600)
    
    return {
        **results,
        "source": "web" if web_enabled else "database"
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


@api_router.get("/companies/{company_id}", response_class=JSONResponse)
async def get_company(company_id: int):
    """Get a single company by id."""
    try:
        with get_db_session() as session:
            company = session.query(Company).filter(Company.id == company_id).first()
            if not company:
                raise HTTPException(status_code=404, detail="Company not found")
            return company.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
