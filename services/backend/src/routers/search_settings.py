from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from ..authentication.token import get_current_user
from ..commons.db_storage.models import FlaggedData, SearchSetting, User
from ..placeholder.get_db import get_db
from ..schemas.schemas import SearchSettingDetail, SearchSettingOut

router = APIRouter()


@router.get("/search-settings/", response_model=List[SearchSettingOut])
def read_search_settings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):  # noqa: B008
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")

    if current_user.is_admin:
        search_settings = (
            db.query(
                SearchSetting.id,
                User.username.label("owner"),
                SearchSetting.domain_base,
                SearchSetting.tld,
                func.count(FlaggedData.id).label("flagged_data_count"),
            )
            .join(User, SearchSetting.owner_id == User.id)
            .outerjoin(FlaggedData, SearchSetting.id == FlaggedData.search_setting_id)
            .group_by(SearchSetting.id, User.username)
            .all()
        )
    else:
        search_settings = (
            db.query(
                SearchSetting.id,
                User.username.label("owner"),
                SearchSetting.domain_base,
                SearchSetting.tld,
                func.count(FlaggedData.id).label("flagged_data_count"),
            )
            .join(User, SearchSetting.owner_id == User.id)
            .outerjoin(FlaggedData, SearchSetting.id == FlaggedData.search_setting_id)
            .filter(SearchSetting.owner_id == current_user.id)
            .group_by(SearchSetting.id, User.username)
            .all()
        )

    return search_settings


@router.get("/search-settings/{setting_id}/", response_model=SearchSettingDetail)
def get_search_setting_detail(setting_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):  # noqa: B008
    search_setting = db.query(SearchSetting).filter(SearchSetting.id == setting_id).options(joinedload(SearchSetting.flagged_data)).first()

    if not search_setting:
        raise HTTPException(status_code=404, detail="Search setting not found")

    if not current_user.is_admin and current_user.id != search_setting.owner_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this setting")

    return SearchSettingDetail.from_orm_instance(search_setting)
