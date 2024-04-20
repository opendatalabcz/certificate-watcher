import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from ..authentication.token import get_current_user
from ..commons.db_storage.models import User

router = APIRouter()

FILES_DIRECTORY = "/assets"


@router.get("/files/{filename:path}", response_class=FileResponse)
async def read_file(filename: str, user: User = Depends(get_current_user)):  # noqa: B008
    safe_path = os.path.normpath(filename).replace("\\", "/")
    if ".." in safe_path.split("/"):
        raise HTTPException(status_code=400, detail="Bad Request")

    complete_path = os.path.join(FILES_DIRECTORY, safe_path)
    if not os.path.exists(complete_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Assuming username is directly in path just after base directory
    _, username, *_ = safe_path.split("/")
    if not user.is_admin and user.username != username:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    return FileResponse(path=complete_path)
