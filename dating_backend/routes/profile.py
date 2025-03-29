from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from fastapi_sqlalchemy import db
from dating_backend.models.db import Profile as ProfileModel
from dating_backend.schemas.base import ProfileCreate, ProfileUpdate, ProfileWithComments, Profile

router = APIRouter()


@router.get("/", response_model=List[Profile])
def get_profiles(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    min_age: Optional[int] = Query(None, ge=18, le=120),
    max_age: Optional[int] = Query(None, ge=18, le=120),
    gender: Optional[str] = Query(None, pattern="^(мужской|женский)$"),
):
    """
    Получить список всех анкет с пагинацией и фильтрацией.
    """
    skip = (page - 1) * limit
    
    query = db.session.query(ProfileModel).order_by(ProfileModel.created_ts.desc())
    
    # Применяем фильтры, если они указаны
    if min_age is not None:
        query = query.filter(ProfileModel.age >= min_age)
    if max_age is not None:
        query = query.filter(ProfileModel.age <= max_age)
    if gender is not None:
        query = query.filter(ProfileModel.gender == gender)
    
    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=Profile, status_code=status.HTTP_201_CREATED)
def create_profile(profile: ProfileCreate):
    """
    Создать новую анкету.
    """
    db_profile = ProfileModel(**profile.model_dump())
    db.session.add(db_profile)
    db.session.commit()
    db.session.refresh(db_profile)
    return db_profile


@router.get("/{profile_id}", response_model=ProfileWithComments)
def get_profile(profile_id: int):
    """
    Получить анкету по ID вместе с комментариями.
    """
    db_profile = db.session.query(ProfileModel).filter(ProfileModel.id == profile_id).first()
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Анкета не найдена")
    return db_profile


@router.put("/{profile_id}", response_model=Profile)
def update_profile(profile_id: int, profile: ProfileUpdate):
    """
    Обновить существующую анкету.
    """
    db_profile = db.session.query(ProfileModel).filter(ProfileModel.id == profile_id).first()
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Анкета не найдена")
    
    profile_data = profile.model_dump(exclude_unset=True)
    for key, value in profile_data.items():
        setattr(db_profile, key, value)
    
    db.session.commit()
    db.session.refresh(db_profile)
    return db_profile


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(profile_id: int):
    """
    Удалить анкету.
    """
    db_profile = db.session.query(ProfileModel).filter(ProfileModel.id == profile_id).first()
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Анкета не найдена")
    
    db.session.delete(db_profile)
    db.session.commit()
    return None 