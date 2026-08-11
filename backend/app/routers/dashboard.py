from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.dependencies import get_current_user
from app.models.known_error import KnownError
from app.models.category import Category

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("")
def dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    total_errors = db.query(KnownError).count()

    total_categories = db.query(Category).count()

    open_issues = db.query(KnownError).filter(
        KnownError.status == "Open"
    ).count()

    resolved_issues = db.query(KnownError).filter(
        KnownError.status == "Resolved"
    ).count()

    recent_errors = (
        db.query(KnownError)
        .order_by(KnownError.id.desc())
        .limit(3)
        .all()
    )

    for error in recent_errors:
        print(
            "ERROR:", error.id,
            "CATEGORY_ID:", error.category_id,
            "CATEGORY OBJECT:", error.category,
            "CATEGORY NAME:", error.category.name if error.category else None
        )


    return {

        "total_errors": total_errors,
        "total_categories": total_categories,
        "open_issues": open_issues,
        "resolved_issues": resolved_issues,

        "recent_errors": [
            {
                "id": error.id,
                "error": error.title,
                "category": error.category.name if error.category else "-",
                "status": error.status
            }
            for error in recent_errors
        ]
    }