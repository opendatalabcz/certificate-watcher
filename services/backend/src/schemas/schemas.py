from datetime import datetime

from pydantic import BaseModel

from ..commons.db_storage.models import FlaggedData, Image, ScanHistory, SearchSetting


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
    image_url: str | None
    local_path: str | None
    format: str | None
    created: datetime
    note: str | None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_instance(cls, image: "Image") -> "ImageDetail":
        image_url = None
        if image.image_url:
            image_url = image.image_url if len(image.image_url) < 2000 else "invalid url"

        return cls(
            id=image.id,
            name=image.name,
            image_url=image_url,
            local_path=image.local_path,
            format=image.format,
            created=image.created,
            note=image.note,
        )


class ScanHistoryData(BaseModel):
    id: int
    scan_time: datetime
    images_scraped: bool
    notes: str | None
    images: list[ImageDetail]

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_instance(cls, scan_history: "ScanHistory") -> "ScanHistoryData":
        return cls(
            id=scan_history.id,
            scan_time=scan_history.scan_time,
            images_scraped=scan_history.images_scraped,
            notes=scan_history.notes,
            images=[ImageDetail.from_orm_instance(image) for image in scan_history.images],
        )


class FlaggedDataListDetail(BaseModel):
    id: int
    domain: str
    algorithm: str
    flagged_time: datetime
    successfully_scraped: bool
    suspected_logo: bool
    scraped_images_count: int

    class Config:
        orm_mode = True

    @classmethod
    def from_orm_instance(cls, flagged_data: "FlaggedData") -> "FlaggedDataListDetail":
        images_count = 0
        for scan_history in flagged_data.scan_histories:
            images_count += len(scan_history.images)

        suspected_logo = False
        for scan_history in flagged_data.scan_histories:
            if scan_history.suspected_logo_found:
                suspected_logo = True
                break

        successfully_scraped = False
        for scan_history in flagged_data.scan_histories:
            if scan_history.images_scraped:
                successfully_scraped = True
                break

        return cls(
            id=flagged_data.id,
            domain=flagged_data.domain,
            algorithm=flagged_data.algorithm,
            flagged_time=flagged_data.flagged_time,
            successfully_scraped=successfully_scraped,
            suspected_logo=suspected_logo,
            scraped_images_count=images_count,
        )


class FlaggedDataDetail(BaseModel):
    id: int
    searched_domain: str
    searched_logo: ImageDetail | None
    domain: str
    algorithm: str
    flagged_time: datetime
    scan_history: list[ScanHistoryData]

    @classmethod
    def from_orm_instance(cls, flagged_data: "FlaggedData") -> "FlaggedDataDetail":
        logo = None
        if flagged_data.search_setting.logo:
            logo = ImageDetail.from_orm_instance(flagged_data.search_setting.logo)

        return cls(
            id=flagged_data.id,
            searched_domain=flagged_data.search_setting.domain_base,
            searched_logo=logo,
            domain=flagged_data.domain,
            algorithm=flagged_data.algorithm,
            flagged_time=flagged_data.flagged_time,
            scan_history=[ScanHistoryData.from_orm_instance(sh) for sh in flagged_data.scan_histories],
        )


class SearchSettingDetail(BaseModel):
    id: int
    owner: str
    domain_base: str
    tld: str
    logo: ImageDetail | None
    additional_settings: dict | None
    flagged_data: list[FlaggedDataListDetail]

    class Config:
        from_attributes = True
        orm_mode = True

    @classmethod
    def from_orm_instance(cls, search_setting: "SearchSetting") -> "SearchSettingDetail":
        return cls(
            id=search_setting.id,
            owner=search_setting.owner.username,
            domain_base=search_setting.domain_base,
            logo=ImageDetail.from_orm_instance(search_setting.logo) if search_setting.logo else None,
            tld=search_setting.tld,
            additional_settings=search_setting.additional_settings,
            flagged_data=[FlaggedDataListDetail.from_orm_instance(fd) for fd in search_setting.flagged_data],
        )


class SearchSettingCreate(BaseModel):
    domain_base: str
    tld: str
    additional_settings: dict | None = None
    logo_url: str | None = None

    class Config:
        from_attributes = True
