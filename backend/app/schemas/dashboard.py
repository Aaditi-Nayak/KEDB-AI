from pydantic import BaseModel

class DashboardSummary(BaseModel):

    total_known_errors:int
    open_errors:int
    resolved_errors:int
    total_categories:int