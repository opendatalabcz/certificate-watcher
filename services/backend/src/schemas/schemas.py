from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, HttpUrl


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


class ImageDetail(BaseModel):
    id: int
    name: str
    image_url: Optional[HttpUrl]
    local_path: Optional[str]
    format: Optional[str]
    created: datetime
    note: Optional[str]


class FlaggedDataListDetail(BaseModel):
    id: int
    domain: str
    algorithm: str
    flagged_time: datetime
    successfully_scraped: bool
    suspected_logo: Optional[HttpUrl]
    scraped_images_count: int


class FlaggedDataDetail(BaseModel):
    id: int
    searched_domain: str
    searched_logo: Optional[ImageDetail]
    domain: str
    algorithm: str
    flagged_time: datetime
    successfully_scraped: bool
    suspected_logo: Optional[str]  # Assuming this is a URL or None
    scraped_images_count: int
    images: List[ImageDetail]


class SearchSettingDetail(BaseModel):
    id: int
    owner: str
    domain_base: str
    tld: str
    additional_settings: Optional[dict]
    flagged_data: List[FlaggedDataListDetail]

    class Config:
        from_attributes = True
