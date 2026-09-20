from pydantic import BaseModel
from typing import Optional


class MenuItemCreate(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    price: float
    available: bool = True


class MenuItemResponse(BaseModel):
    id: int
    name: str
    category: str
    description: Optional[str]
    price: float
    available: bool

    class Config:
        from_attributes = True