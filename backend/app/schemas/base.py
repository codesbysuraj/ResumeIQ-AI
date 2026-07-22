"""
Base Pydantic schema configuration and standard API wrapper response models.
"""
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class BaseSchema(BaseModel):
    """
    Base Pydantic schema configured for ORM compatibility.
    Allows seamlessly instantiating Pydantic schemas directly from SQLAlchemy models.
    """
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class APIResponse(BaseModel, Generic[T]):
    """Standard generic API response wrapper."""
    success: bool = True
    message: str = "Operation successful"
    data: Optional[T] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated list response wrapper."""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
