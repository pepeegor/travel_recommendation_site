from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc

from app.destinations.dao import DestinationDAO
from app.reviews.dao import ReviewDAO
from app.reviews.models import Review
from app.reviews.schemas import (
    SReviewCreate,
    SReviewUpdate,
    SReviewOut,
    SReviewList,
    SUserReviewOut,
    SUserReviewsList,
)
from app.users.dependencies import get_current_user
from app.users.models import User

router = APIRouter(
    prefix="/reviews",
    tags=["Отзывы"]
)

@router.post(
    "",
    response_model=SReviewOut,
    status_code=status.HTTP_201_CREATED
)
async def create_review(
    review_data: SReviewCreate,
    current_user: User = Depends(get_current_user)
):
    dest = await DestinationDAO.find_by_id(review_data.destination_id)
    if not dest:
        raise HTTPException(404, "Место назначения не найдено")

    exists = await ReviewDAO.find_one_or_none(
        user_id=current_user.id,
        destination_id=review_data.destination_id
    )
    if exists:
        raise HTTPException(400, "Вы уже оставили отзыв для этого места")

    review = await ReviewDAO.add(
        user_id=current_user.id,
        destination_id=review_data.destination_id,
        rating=review_data.rating,
        comment=review_data.comment,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None)
    )
    return review  # SReviewOut.from_attributes=True

@router.get(
    "/destination/{destination_id}",
    response_model=SReviewList
)
async def get_destination_reviews(
    destination_id: int,
    page: int = 1,
    limit: int = 20
):
    dest = await DestinationDAO.find_by_id(destination_id)
    if not dest:
        raise HTTPException(404, "Место назначения не найдено")

    total = await ReviewDAO.count(where_clause=(Review.destination_id == destination_id))
    pages = (total + limit - 1) // limit
    offset = (page - 1) * limit

    # <-- меняем find_all на find_by_destination_id
    reviews: List[SReviewOut] = await ReviewDAO.find_by_destination_id(destination_id)
    avg = await ReviewDAO.get_average_rating(destination_id) or 0.0

    return SReviewList(
        total=total,
        page=page,
        pages=pages,
        average_rating=float(avg),
        reviews=reviews
    )


@router.get(
    "/user",
    response_model=SUserReviewsList
)
async def get_user_reviews(
    current_user: User = Depends(get_current_user)
):
    reviews = await ReviewDAO.find_all(
        where_clause={ "user_id": current_user.id },
        order_by=[desc(Review.created_at)]
    )
    result = []
    for rv in reviews:
        dest = await DestinationDAO.find_by_id(rv.destination_id)
        result.append({
            "id": rv.id,
            "rating": rv.rating,
            "comment": rv.comment,
            "created_at": rv.created_at,
            "destination": {
                "id": dest.id,
                "name": dest.name,
                "country": dest.country,
                "image_url": dest.image_url
            }
        })
    return {
        "total": len(result),
        "reviews": result
    }

@router.put(
    "/{review_id}",
    response_model=SReviewOut
)
async def update_review(
    review_id: int,
    review_data: SReviewUpdate,
    current_user: User = Depends(get_current_user)
):
    review = await ReviewDAO.find_by_id(review_id)
    if not review:
        raise HTTPException(404, "Отзыв не найден")
    if review.user_id != current_user.id:
        raise HTTPException(403, "Нет прав на редактирование")

    data = review_data.model_dump(exclude_none=True)
    updated = await ReviewDAO.update(review_id, **data)
    return updated

@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user)
):
    review = await ReviewDAO.find_by_id(review_id)
    if not review:
        raise HTTPException(404, "Отзыв не найден")
    if review.user_id != current_user.id:
        raise HTTPException(403, "Нет прав на удаление")

    await ReviewDAO.delete(review_id)
    return
