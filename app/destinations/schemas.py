from typing import Dict, List, Optional
from pydantic import BaseModel, field_validator


class SDestinationUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None
    
class SDestinationCreate(BaseModel):
    name: str
    description: Optional[str] = None
    country: str
    climate: str
    approximate_price: float
    latitude: float
    longitude: float
    image_url: Optional[str] = None
    
    @field_validator('name') 
    def name_must_be_longer_than_two_characters(cls, value):
        if len(value) <= 2:
            raise ValueError('Название должно быть длиннее 2 символов')
        return value

    @field_validator('country')
    def country_must_be_longer_than_two_characters(cls, value):
        if len(value) <= 2:
            raise ValueError('Страна должна быть длиннее 2 символов')
        return value

    @field_validator('climate')
    def climate_must_be_longer_than_two_characters(cls, value):
        if len(value) <= 2:
            raise ValueError('Климат должен быть длиннее 2 символов')
        return value

    @field_validator('approximate_price')
    def price_must_be_positive(cls, value):
        if value <= 0:
            raise ValueError('Цена должна быть положительным числом')
        return value

    @field_validator('latitude')
    def latitude_must_be_valid(cls, value):
        if not (-90 <= value <= 90):
            raise ValueError('Широта должна быть в диапазоне от -90 до 90')
        return value

    @field_validator('longitude')
    def longitude_must_be_valid(cls, value):
        if not (-180 <= value <= 180):
            raise ValueError('Долгота должна быть в диапазоне от -180 до 180')
        return value

    @field_validator('image_url')
    def image_url_must_be_valid(cls, value):
        if value is not None and not value.startswith(('http://', 'https://')):
            raise ValueError('URL изображения должен начинаться с http:// или https://')
        return value