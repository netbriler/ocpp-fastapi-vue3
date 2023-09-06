from pydantic import BaseModel


class CreateAccountView(BaseModel):
    name: str

    class Config:
        orm_mode = True


class AccountView(BaseModel):
    id: str
    name: str
    is_active: bool

    class Config:
        orm_mode = True