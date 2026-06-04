from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class UserMe(BaseModel):
    id: int
    username: str
    full_name: str | None = None
    role: str

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserMe
