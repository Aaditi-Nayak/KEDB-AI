from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.category import Category
from app.schemas.category import (
    CategoryCreate,
    CategoryResponse
)
from app.dependencies import get_current_user
from app.models.user import User

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

router=APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

@router.post("/",response_model=CategoryResponse)
def create_category(
    category:CategoryCreate,
    db:Session=Depends(get_db)
):
    
    existing=db.query(Category).filter(Category.name==category.name).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Category already exists"
        )
    
    new_category=Category(
        name=category.name,
        description=category.description
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


@router.get("/",response_model=list[CategoryResponse]
)
def get_categories(
    db: Session = Depends(get_db)
):

    return db.query(Category).all()


@router.get("/{category_id}",response_model=CategoryResponse)
def get_category(category_id:int,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):

    category=db.query(Category).filter(Category.id==category_id).first()

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return category


@router.put("/{category_id}",response_model=CategoryResponse)
def update_category(
    category_id:int,
    updated_category:CategoryCreate,
    db:Session=Depends(get_db),
    current_user:User=Depends(get_current_user)
):

    category=db.query(Category).filter(Category.id==category_id).first()

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    category.name=updated_category.name
    category.description=updated_category.description

    db.commit()
    db.refresh(category)

    return category


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    db.delete(category)
    db.commit()

    return {
        "message": "Category deleted successfully"
    }