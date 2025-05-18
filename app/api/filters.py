from fastapi import APIRouter, HTTPException
from app.models.schemas import FilterRequest
from app.db.mongodb import db
import logging

router = APIRouter()
logger = logging.getLogger("gradguide")

@router.post("/filter")
def filter_colleges(request: FilterRequest):
    try:
        logger.info(f"Received filter request: {request.dict()}")
        if not request.exams or not request.ranks:
            logger.warning("Missing exams or ranks")
            raise HTTPException(status_code=422, detail="Exams and ranks are required")

        query = {"exam": {"$in": request.exams}}
        for exam, rank in request.ranks.items():
            query["cutoff_rank"] = {"$gte": rank}
        if request.min_average_placement is not None:
            query["average_placement"] = {"$gte": request.min_average_placement}
        if request.min_median_placement is not None:
            query["median_placement"] = {"$gte": request.min_median_placement}
        if request.min_highest_placement is not None:
            query["highest_placement"] = {"$gte": request.min_highest_placement}

        results = []
        for doc in db.db.college_data.find(query, {"_id": 0}):
            results.append(doc)
        
        if not results:
            logger.warning("No colleges found")
            return {"results": []}
        logger.info(f"Returning {len(results)} colleges")
        return {"results": results}
    except Exception as e:
        logger.error(f"Filter error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to filter colleges: {str(e)}")