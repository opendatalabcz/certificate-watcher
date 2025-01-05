from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from ..authentication.token import get_current_user
from ..commons.db_storage.models import FlaggedData, ScanHistory, User
from ..placeholder.get_db import get_db
from ..schemas.schemas import FlaggedDataDetail

router = APIRouter()


@router.get("/flagged-data/{data_id}/", response_model=FlaggedDataDetail)
def get_flagged_data_detail(data_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):  # noqa: B008
    flagged_data = (
        db.query(FlaggedData)
        .filter(FlaggedData.id == data_id)
        .options(joinedload(FlaggedData.scan_histories).joinedload(ScanHistory.images), joinedload(FlaggedData.search_setting))
        .first()
    )

    if not flagged_data:
        raise HTTPException(status_code=404, detail="Flagged data not found")

    if not current_user.is_admin and current_user.id != flagged_data.search_setting.owner_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this data")

    return FlaggedDataDetail.from_orm_instance(flagged_data)
