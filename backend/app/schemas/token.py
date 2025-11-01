from pydantic import BaseModel


class Token(BaseModel):
    """
    Token schema for JWT authentication response.
    """
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Token data schema for extracting information from JWT token.
    """
    email: str | None = None
