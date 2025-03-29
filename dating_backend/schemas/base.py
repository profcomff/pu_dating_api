from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, conint


class CommentBase(BaseModel):
    author_name: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)


class CommentCreate(CommentBase):
    pass


class Comment(CommentBase):
    id: int
    profile_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProfileBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    age: conint(ge=18, le=120)
    gender: str = Field(..., pattern="^(мужской|женский)$")
    description: Optional[str] = None
    interests: Optional[str] = None
    contact: str = Field(..., min_length=1)


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    age: Optional[conint(ge=18, le=120)] = None
    gender: Optional[str] = Field(None, pattern="^(мужской|женский)$")
    contact: Optional[str] = Field(None, min_length=1)


class Profile(ProfileBase):
    id: int
    created_ts: datetime
    updated_ts: datetime

    class Config:
        from_attributes = True


class ProfileWithComments(Profile):
    comments: List[Comment] = []

    class Config:
        from_attributes = True


# Пагинация
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)


# Параметры фильтрации
class ProfileFilterParams(BaseModel):
    min_age: Optional[int] = Field(None, ge=18, le=120)
    max_age: Optional[int] = Field(None, ge=18, le=120)
    gender: Optional[str] = Field(None, pattern="^(мужской|женский)$") 