from pydantic import BaseModel, Field


class ResetDataRequest(BaseModel):
    password: str = Field(min_length=1)
    confirmation: str = Field(min_length=1)


class ResetDataResponse(BaseModel):
    message: str
    deleted: dict[str, int]
    preserved_users: list[str]