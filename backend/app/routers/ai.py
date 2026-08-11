import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sklearn.metrics.pairwise import cosine_similarity

from app.database import SessionLocal
from app.models.known_error import KnownError

from app.ai.embedding import get_embedding
from app.ai.llm import generate_answer

from app.schemas.ai import ChatRequest, ChatResponse
from app.models.category import Category

router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):

    # Step 1: User question
    question = request.question

    # Step 2: Convert question into embedding
    question_embedding = get_embedding(question)

    # Step 3: Fetch all known errors
    errors = db.query(KnownError).join(Category).all()

    best_match = None
    best_score = 0

    # Step 4: Compare with every Known Error
    for error in errors:

        if error.embedding is None:
            continue

        stored_embedding = json.loads(error.embedding)

        score = cosine_similarity(
            [question_embedding],
            [stored_embedding]
        )[0][0]

        if score > best_score:
            best_score = score
            best_match = error

    # Step 5: No suitable match found
    if best_match is None or best_score < 0.60:

        return ChatResponse(
            answer="Sorry, I couldn't find any relevant Known Error in the database.",
            similarity=round(best_score, 3),
            known_error=None
        )

    # Step 6: Build prompt for Gemini
    prompt = f"""
You are an experienced IT Support Engineer.

A user asked:

{question}

The following Known Error was retrieved from the KEDB.

Title:
{best_match.title}

Application:
{best_match.application}

Symptoms:
{best_match.symptoms}

Root Cause:
{best_match.root_cause}

Workaround:
{best_match.workaround}

Resolution:
{best_match.resolution}

Status:
{best_match.status}

Instructions:
- Answer the user's question professionally.
- Use only the information given above.
- Explain the root cause clearly.
- Mention the workaround if available.
- Mention the final resolution if available.
- Do not invent information.
"""

    # Step 7: Ask Gemini
    answer = generate_answer(prompt)

    category=(db.query(Category).filter(Category.id==best_match.category_id).first())

    # Step 8: Return response
    return ChatResponse(
        answer=answer,
        similarity=round(best_score, 3),
        known_error={

            "id":best_match.id,

            "title": best_match.title,

            "application": best_match.application,

            "category": category.name if category else "Unknown",

            "symptoms": best_match.symptoms,

            "root_cause": best_match.root_cause,

            "workaround": best_match.workaround,

            "resolution": best_match.resolution,

            "status": best_match.status

        }
    )