from pydantic import BaseModel

class DuplicateRequest(BaseModel):
    
    title:str
    symptoms:str
    root_cause:str
    workaround:str
    resolution:str

class DuplicateResponse(BaseModel):

    duplicate:bool
    similarity:float
    existing_error:dict|None=None


class KnownErrorAI(BaseModel):

    id:int
    title: str
    application: str
    category:str
    symptoms: str
    root_cause: str
    workaround: str
    resolution: str
    status: str

class ChatRequest(BaseModel):

    question:str

class ChatResponse(BaseModel):

    answer: str
    similarity: float
    known_error: KnownErrorAI | None = None