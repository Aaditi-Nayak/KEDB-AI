import json
import numpy as np
from sentence_transformers import util

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.known_error import KnownError
from app.schemas.known_error import (
    KnownErrorCreate,
    KnownErrorResponse,
    KnownErrorUpdate,
    KnownErrorDetail
)

from app.dependencies import get_current_user,get_db
from app.models.user import User
from app.ai.embedding import get_embedding
from sklearn.metrics.pairwise import cosine_similarity


router=APIRouter(
    prefix="/known-errors",
    tags=["Known Errors"]
)

# create known errors
@router.post("/",response_model=KnownErrorResponse)
def create_known_error(
    error: KnownErrorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)

):
    text=f"""
    {error.title}
    {error.symptoms}
    {error.root_cause}
    {error.workaround}
    {error.resolution}
    """
    embedding=get_embedding(text)
    embedding_json=json.dumps(embedding)

    new_error=KnownError(
        title=error.title,
        application=error.application,
        category_id=error.category_id,
        symptoms=error.symptoms,
        root_cause=error.root_cause,
        workaround=error.workaround,
        resolution=error.resolution,
        embedding=embedding_json,
        created_by=current_user.id
    )

    db.add(new_error)
    db.commit()
    db.refresh(new_error)

    return {
    "id": new_error.id,
    "title": new_error.title,
    "application": new_error.application,
    "category_id": new_error.category_id,
    "category": new_error.category.name if new_error.category else "-",
    "symptoms": new_error.symptoms,
    "root_cause": new_error.root_cause,
    "workaround": new_error.workaround,
    "resolution": new_error.resolution,
    "status": new_error.status,
    "created_by": new_error.created_by,
    "created_at": new_error.created_at
}

# get all known errors
@router.get("/",response_model=list[KnownErrorResponse])
def get_all_known_errors(
    title:str|None=None,
    status:str|None=None,
    category_id:int|None=None,
    search: str | None = None,
    db:Session=Depends(get_db)
):
        
    query=db.query(KnownError)

    if title:
        query = query.filter(
            KnownError.title.ilike(f"%{title}%")
        )

    if status:
        query = query.filter(
            KnownError.status == status
        )

    if category_id:
        query = query.filter(
            KnownError.category_id == category_id
            ) 

    if search:
        query = query.filter(
            (KnownError.title.ilike(f"%{search}%")) |
            (KnownError.application.ilike(f"%{search}%"))
        )

    errors=query.all()

    return [
    {
        "id": error.id,
        "title": error.title,
        "application": error.application,
        "category_id": error.category_id,
        "category": error.category.name if error.category else "-",
        "symptoms": error.symptoms,
        "root_cause": error.root_cause,
        "workaround": error.workaround,
        "resolution": error.resolution,
        "status": error.status,
        "created_by": error.created_by,
        "created_at": error.created_at
    }
    for error in errors
]

# get known errors by id
@router.get("/{error_id}",response_model=KnownErrorDetail)
def get_known_error(error_id:int,
                    db:Session=Depends(get_db),
                    current_user=Depends(get_current_user)):
    
    error=db.query(KnownError).filter(KnownError.id==error_id).first()

    if error is None:
        raise HTTPException(
            status_code=404,
            detail="Known Error not found"
        )
    
    return{
        "id": error.id,
        "title": error.title,
        "application": error.application,
        "category_id":error.category_id,
        "category": error.category.name if error.category else "-",
        "symptoms": error.symptoms,
        "root_cause": error.root_cause,
        "workaround": error.workaround,
        "resolution": error.resolution,
        "status": error.status
    }

# update known error 
@router.put("/{error_id}",response_model=KnownErrorResponse)
def update_known_error(
    error_id:int,
    updated_error:KnownErrorUpdate,
    db:Session=Depends(get_db)
):
    
    error=db.query(KnownError).filter(KnownError.id==error_id).first()

    if error is None:
        raise HTTPException(
            status_code=404,
            detail="Known error not found"
        )
    
    error.title=updated_error.title
    error.application = updated_error.application
    error.category_id = updated_error.category_id
    error.symptoms = updated_error.symptoms
    error.root_cause = updated_error.root_cause
    error.workaround = updated_error.workaround
    error.resolution = updated_error.resolution
    error.status = updated_error.status

    db.commit()
    db.refresh(error)
    return error

# delete known error
@router.delete("/{error_id}")
def delete_known_error(error_id:int,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):

    error=db.query(KnownError).filter(KnownError.id==error_id).first()

    if error is None:
        raise HTTPException(
            status_code=404,
            detail="Known Error not found"
        )

    db.delete(error)
    db.commit()

    return{
        "message":"Known Error deleted successfully"
    }

# search api
@router.get("/semantic-search")
def semantic_search(query:str,db:Session=Depends(get_db)):
    
    search_embedding=get_embedding(query)
    known_errors=db.query(KnownError).all()

    results=[]

    for error in known_errors:
        
        stored_embedding=json.loads(error.embedding)
        
        stored_embedding=np.array(stored_embedding)
        
        similarity=util.cos_sim(search_embedding,stored_embedding).item()

        if similarity>=0.60:
            if similarity>0.90:
                confidence="Very High"
            elif similarity>0.75:
                confidence="High"
            elif similarity>0.60:
                confidence="Medium"
        else:
            confidence="Low"

        results.append(
            {
                "id": error.id,
                "title": error.title,
                "application": error.application,
                "symptoms": error.symptoms,
                "root_cause": error.root_cause,
                "workaround": error.workaround,
                "resolution": error.resolution,
                "status": error.status,
                "similarity": round(similarity, 3),
                "confidence":confidence
            }
        )
    
    results.sort(
        key=lambda x: x["similarity"],
        reverse=True
    )

    return results[:5]


@router.post("/recommend")
def recommend_solution(incident:str,db:Session=Depends(get_db)):

    query_embedding=get_embedding(incident)
    known_errors=db.query(KnownError).all()

    best_match=None
    best_similarity=0

    for error in known_errors:
        stored_embedding=np.array(json.loads(error.embedding))

        similarity=util.cos_sim(query_embedding,stored_embedding).item()

        if similarity>best_similarity:
            best_similarity=similarity
            best_match=error
    
    if best_match is None:
        return{
            "message":"No matching known error found"
        }
    
    if best_similarity > 0.90:
        confidence = "Very High"
    elif best_similarity > 0.75:
        confidence = "High"
    elif best_similarity > 0.60:
        confidence = "Medium"
    else:
        confidence = "Low"

    return{
        "id": best_match.id,
        "title": best_match.title,
        "application": best_match.application,
        "category_id": best_match.category_id,
        "symptoms": best_match.symptoms,
        "root_cause": best_match.root_cause,
        "workaround": best_match.workaround,
        "resolution": best_match.resolution,
        "status": best_match.status,
        "similarity": round(best_similarity, 3),
        "confidence": confidence
    }


# check duplicate
@router.post("/check-duplicate")
def check_duplicate(
    known_error:KnownErrorCreate,
    db:Session=Depends(get_db)
):
    
    text=f"""
Title:{known_error.title}
Symptoms:{known_error.symptoms}
Root Cause:{known_error.root_cause}
Workaround:{known_error.workaround}
Resolution:{known_error.resolution}
"""
    
    query_embedding=get_embedding(text)
    errors=db.query(KnownError).all()   

    best_match=None
    best_score=0

    for error in errors:

        if error.embedding is None:
            continue

        stored_embedding=json.loads(error.embedding)
        
        score=cosine_similarity([query_embedding],[stored_embedding])[0][0]

        if score>best_score:
            best_score=score
            best_match=error

    if best_score>=0.90:

        return{
           "duplicate": True,
            "similarity": round(best_score, 3),
            "existing_error": {
                "id": best_match.id,
                "title": best_match.title,
                "application": best_match.application,
                "status": best_match.status
            } 
        }
    
    return {
        "duplicate": False,
        "similarity": round(best_score, 3)
    }