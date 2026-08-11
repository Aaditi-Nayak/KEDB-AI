from pydantic import BaseModel
from datetime import datetime

class KnownErrorCreate(BaseModel):

    title:str
    application:str
    category_id:int
    symptoms:str
    root_cause:str
    workaround:str
    resolution:str

class KnownErrorResponse(BaseModel):

    id: int
    title: str
    application: str
    category_id: int
    category:str|None=None
    symptoms: str
    root_cause: str
    workaround: str
    resolution: str
    status: str
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True

class KnownErrorUpdate(BaseModel):
    title:str
    application:str
    category_id:int
    symptoms:str
    root_cause:str
    workaround:str
    resolution:str
    status:str



class KnownErrorDetail(BaseModel):

    id: int
    title: str
    application: str
    category: str
    symptoms: str
    root_cause: str
    workaround: str
    resolution: str
    status: str