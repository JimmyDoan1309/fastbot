from pydantic import BaseModel


class Pagination(BaseModel):
    skip: int = 0
    limit: int = 10
