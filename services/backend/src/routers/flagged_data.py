from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..authentication.token import get_current_user
from ..commons.db_storage.models import FlaggedData, Image, SearchSetting, User
from ..placeholder.get_db import get_db
from ..schemas.schemas import FlaggedDataDetail, ImageDetail

router = APIRouter()


@router.get("/flagged-data/{data_id}/", response_model=FlaggedDataDetail)
def get_flagged_data_detail(data_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):  # noqa: B008
    flagged_data = db.query(FlaggedData).filter(FlaggedData.id == data_id).first()

    if not flagged_data:
        raise HTTPException(status_code=404, detail="Flagged data not found")

    search_setting = db.query(SearchSetting).filter(SearchSetting.id == flagged_data.search_setting_id).first()

    if not search_setting:
        raise HTTPException(status_code=404, detail="Search setting not found")
    if not current_user.is_admin and current_user.id != search_setting.owner_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this data")

    images = db.query(Image).filter(Image.flag_id == data_id).all()
    image_details = [
        ImageDetail(
            id=img.id, name=img.name, image_url=img.image_url, local_path=img.local_path, format=img.format, created=img.created.isoformat(), note=img.note
        )
        for img in images
    ]

    logo = None
    if search_setting.logo:
        logo = ImageDetail(
            id=search_setting.logo.id,
            name=search_setting.logo.name,
            image_url=search_setting.logo.image_url,
            local_path=search_setting.logo.local_path,
            format=search_setting.logo.format,
            created=search_setting.logo.created,
            note=search_setting.logo.note,
        )

    return FlaggedDataDetail(
        id=flagged_data.id,
        domain=flagged_data.domain,
        searched_domain=f"{search_setting.domain_base}.{search_setting.tld}",
        searched_logo=logo,
        algorithm=flagged_data.algorithm,
        flagged_time=flagged_data.flagged_time,
        successfully_scraped=flagged_data.images_scraped,
        suspected_logo=flagged_data.suspected_logo.image_url if flagged_data.suspected_logo else None,
        scraped_images_count=len(images),
        images=image_details,
    )
