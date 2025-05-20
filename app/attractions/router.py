from fastapi import APIRouter, Depends, HTTPException, status

from app.attractions.dao import AttractionDAO
from app.attractions.schemas import SAttractionOut, SAttractionUpdate
from app.users.dependencies import get_current_admin_user
from app.users.models import User

router = APIRouter(
    prefix="/attractions",
    tags=["Достопримечательности"]
)

@router.get(
    "/{attraction_id}",
    response_model=SAttractionOut,
    summary="Получить достопримечательность по ID"
)
async def get_attraction(attraction_id: int):
    attraction = await AttractionDAO.find_by_id(attraction_id)
    if not attraction:
        raise HTTPException(status_code=404, detail="Достопримечательность не найдена")
    return attraction

@router.put(
    "/{attraction_id}",
    response_model=SAttractionOut,
    summary="Обновить достопримечательность (только админ)"
)
async def update_attraction(
    attraction_id: int,
    data: SAttractionUpdate,
    current_user: User = Depends(get_current_admin_user)
):
    updated = await AttractionDAO.update(
        attraction_id,
        **data.model_dump(exclude_none=True)
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Достопримечательность не найдена")
    return updated

@router.delete(
    "/{attraction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить достопримечательность (только админ)"
)
async def delete_attraction(
    attraction_id: int,
    current_user: User = Depends(get_current_admin_user)
):
    await AttractionDAO.delete(attraction_id)
    return 
