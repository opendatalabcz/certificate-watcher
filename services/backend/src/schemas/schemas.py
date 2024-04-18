from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    username: str
    is_admin: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = None


class SearchSettingOut(BaseModel):
    id: int
    owner: str
    domain_base: str
    tld: str
    flagged_data_count: int

    class Config:
        from_attributes = True
