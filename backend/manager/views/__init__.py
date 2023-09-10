from pydantic import BaseModel


class ErrorContent(BaseModel):
    detail: str
    key: str


class PaginationView(BaseModel):
    current_page: int
    last_page: int
    total: int


class CountersView(BaseModel):
    locations: int
    stations: int
    transactions: int

    class Config:
        orm_mode = True