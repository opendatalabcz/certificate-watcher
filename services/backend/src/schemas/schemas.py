from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, HttpUrl

from ..commons.db_storage.models import FlaggedData, SearchSetting


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
    # successfully_scraped: bool
    # suspected_logo: Optional[HttpUrl]
    # scraped_images_count: int

    class Config:
        orm_mode = True

    @classmethod
    def from_orm_instance(cls, flagged_data: "FlaggedData") -> "FlaggedDataListDetail":
        return cls(
            id=flagged_data.id,
            domain=flagged_data.domain,
            algorithm=flagged_data.algorithm,
            flagged_time=flagged_data.flagged_time,
        )


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
        orm_mode = True

    @classmethod
    def from_orm_instance(cls, search_setting: "SearchSetting") -> "SearchSettingDetail":
        return cls(
            id=search_setting.id,
            owner=search_setting.owner.username,
            domain_base=search_setting.domain_base,
            tld=search_setting.tld,
            additional_settings=search_setting.additional_settings,
            flagged_data=[FlaggedDataListDetail.from_orm_instance(fd) for fd in search_setting.flagged_data],
        )
