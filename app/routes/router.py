from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.routes.dao import RouteDAO
from app.routes.schemas import (
    SRouteAttractionCreate,
    SRouteAttractionMove,
    SRouteOut,
    SRouteUpdate,
)
from app.routes.schemas import RouteAttractionOut, RouteOut
from app.users.dependencies import get_current_user
from app.users.models import User

router = APIRouter(prefix="/routes", tags=["Маршруты"])


async def _build_route_out(route) -> SRouteOut:
    points = [RouteAttractionOut.model_validate(assoc) for assoc in route.attractions]
    return SRouteOut.model_validate(
        {
            "id": route.id,
            "name": route.name,
            "user_id": route.user_id,
            "trip_id": route.trip_id,
            "destination_id": route.destination_id,
            "total_budget": route.total_budget,
            "published": route.published,
            "created_at": route.created_at,
            "points": points,
        }
    )


@router.get("/{route_id}", response_model=SRouteOut)
async def get_route(route_id: int):
    route = await RouteDAO.find_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Маршрут не найден")
    return await _build_route_out(route)


@router.put("/{route_id}", response_model=SRouteOut)
async def update_route(
    route_id: int,
    data: SRouteUpdate,  # теперь в SRouteUpdate есть необязательное поле attractions: List[SRouteAttractionCreate]
    current_user: User = Depends(get_current_user)
):
    update_data = data.model_dump(exclude_none=True)
    if not update_data:
        # ничего не меняем — просто возвращаем
        route = await RouteDAO.find_by_id(route_id)
        if not route:
            raise HTTPException(404, "Маршрут не найден")
        return await _build_route_out(route)

    route = await RouteDAO.update(route_id, **update_data)
    if not route:
        raise HTTPException(404, "Маршрут не найден")
    return await _build_route_out(route)


@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_route(route_id: int, current_user: User = Depends(get_current_user)):
    await RouteDAO.delete(route_id)
    return  # 204 No Content


@router.post("/{route_id}/attractions", response_model=SRouteOut)
async def add_attraction_to_route(
    route_id: int,
    payload: SRouteAttractionCreate,
    current_user: User = Depends(get_current_user),
):
    await RouteDAO.add_attraction(route_id, payload.attraction_id, payload.position)
    route = await RouteDAO.find_by_id(route_id)
    return await _build_route_out(route)


@router.put("/{route_id}/attractions/{assoc_id}", response_model=SRouteOut)
async def move_attraction_in_route(
    route_id: int,
    assoc_id: int,
    payload: SRouteAttractionMove,
    current_user: User = Depends(get_current_user),
):
    await RouteDAO.move_attraction(route_id, assoc_id, payload.position)
    route = await RouteDAO.find_by_id(route_id)
    return await _build_route_out(route)


@router.delete(
    "/{route_id}/attractions/{assoc_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_attraction_from_route(
    route_id: int, assoc_id: int, current_user: User = Depends(get_current_user)
):
    await RouteDAO.remove_attraction(route_id, assoc_id)
    return


@router.post("/{route_id}/publish", response_model=SRouteOut)
async def publish_route(route_id: int, current_user: User = Depends(get_current_user)):
    route = await RouteDAO.publish_route(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Маршрут не найден")
    return await _build_route_out(route)


@router.get("", response_model=List[SRouteOut])
async def list_published_routes(
    published: bool = Query(True, description="Только опубликованные?"),
    min_budget: Optional[float] = None,
    max_budget: Optional[float] = None,
    types: Optional[List[str]] = Query(None),
    destination_id: Optional[int] = None,
    offset: int = 0,
    limit: int = 20,
):
    # получаем ORM-модели
    routes = await RouteDAO.find_published(
        min_budget=min_budget,
        max_budget=max_budget,
        types=types,
        destination_id=destination_id,
        offset=offset,
        limit=limit,
    )
    result: List[SRouteOut] = []
    for r in routes:
        result.append(SRouteOut.model_validate(r))
    return result


@router.get("/search", response_model=List[SRouteOut])
async def search_routes(q: str = Query(..., min_length=1)):
    routes = await RouteDAO.search(q)
    return [await _build_route_out(r) for r in routes]


@router.get("/mine", response_model=List[SRouteOut])
async def get_my_routes(current_user: User = Depends(get_current_user)):
    routes = await RouteDAO.find_by_user(current_user.id)
    return [await _build_route_out(r) for r in routes]

@router.put(
    "/{route_id}/publish",
    response_model=SRouteOut,
    summary="Снять публикацию маршрута"
)
async def unpublish_route(
    route_id: int,
    current_user: User = Depends(get_current_user)
):
    route = await RouteDAO.find_by_id(route_id)
    if not route or route.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Маршрут не найден")
    updated = await RouteDAO.update(route_id, published=False)
    return await _build_route_out(updated)
