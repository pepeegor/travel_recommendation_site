from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc

from app.destinations.dao import DestinationDAO
from app.reviews.dao import ReviewDAO
from app.reviews.models import Review
from app.reviews.schemas import SReviewCreate, SReviewUpdate
from app.users.dependencies import get_current_user
from app.users.models import User

router = APIRouter(
    prefix="/reviews",
    tags=["Отзывы"]
)

@router.post("")
async def create_review(
    review_data: SReviewCreate,
    current_user: User = Depends(get_current_user)
):
    destination = await DestinationDAO.find_by_id(review_data.destination_id)
    if not destination:
        raise HTTPException(
            status_code=404,
            detail="Указанное место назначения не найдено"
        )
        
    existing_review = await ReviewDAO.find_one_or_none(
        user_id=current_user.id, 
        destination_id=review_data.destination_id
    ) 
    if existing_review:
        raise HTTPException(
            status_code=400,
            detail="Вы уже оставили отзыв для этого места"
        )

    new_review = await ReviewDAO.add(
        user_id=current_user.id,
        destination_id=review_data.destination_id,
        rating=review_data.rating,
        comment=review_data.comment,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None)
    )
    
    return {
        "status": "success",
        "message": "Отзыв успешно создан"
    }

@router.get("/destination/{destination_id}")
async def get_destination_reviews(
    destination_id: int,
    page: int = 1,
    limit: int = 20
):
    try:
        destination = await DestinationDAO.find_by_id(destination_id)
        if not destination:
            raise HTTPException(status_code=404, detail="Место назначения не найдено")

        offset = (page - 1) * limit

        # Fetch reviews with user information using the DAO
        reviews = await ReviewDAO.find_by_destination_id(destination_id)  

        total_reviews = await ReviewDAO.count(where_clause=Review.destination_id == destination_id)
        avg_rating = await ReviewDAO.get_average_rating(destination_id) or 0

        return {
            "total": total_reviews,
            "page": page,
            "pages": (total_reviews + limit - 1) // limit,
            "average_rating": avg_rating,
            "reviews": reviews  # Return reviews from the DAO
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching reviews: {e}")

@router.get("/user")
async def get_user_reviews(
    current_user: User = Depends(get_current_user)
):    
    reviews = await ReviewDAO.find_all(
        {"user_id": current_user.id},
        order_by=[desc(Review.created_at)]
    )
    
    reviews_with_destinations = []
    for review in reviews:
        destination = await DestinationDAO.find_by_id(review.destination_id)
        reviews_with_destinations.append({
            "id": review.id,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at,
            "destination": {
                "id": destination.id,
                "name": destination.name,
                "country": destination.country,
                "image_url": destination.image_url
            }
        })
    
    return {
        "total": len(reviews),
        "reviews": reviews_with_destinations
    }
    

@router.put("/{review_id}")
async def update_review(
    review_id: int,
    review_data: SReviewUpdate,  # Use the schema here
    current_user: User = Depends(get_current_user)
):
    review = await ReviewDAO.find_by_id(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Отзыв не найден")

    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="У вас нет прав на редактирование этого отзыва")

    update_data = review_data.dict(exclude_unset=True)  # Use Pydantic's helper

    if not update_data:
        return review

    updated_review = await ReviewDAO.update(
        review_id,
        **update_data  # Pass update_data as keyword arguments
    )

    return updated_review


@router.delete("/{review_id}")
async def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user)
):
    review = await ReviewDAO.find_by_id(review_id)
    if not review:
        raise HTTPException(
            status_code=404,
            detail="Отзыв не найден"
        )
    
    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="У вас нет прав на удаление этого отзыва"
        )
    
    await ReviewDAO.delete(review_id)
    
    return {
        "status": "success",
        "message": "Отзыв успешно удален"
    }
