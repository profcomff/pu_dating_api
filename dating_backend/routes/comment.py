from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from fastapi_sqlalchemy import db
from dating_backend.models.db import Comment as CommentModel, Profile as ProfileModel
from dating_backend.schemas.base import Comment, CommentCreate

router = APIRouter()


@router.get("/profiles/{profile_id}/comments", response_model=List[Comment])
def get_comments_for_profile(
    profile_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Получить все комментарии к анкете с пагинацией.
    """
    # Проверяем существование анкеты
    db_profile = db.session.query(ProfileModel).filter(ProfileModel.id == profile_id).first()
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Анкета не найдена")
    
    skip = (page - 1) * limit
    
    comments = db.session.query(CommentModel) \
        .filter(CommentModel.profile_id == profile_id) \
        .order_by(CommentModel.created_at.desc()) \
        .offset(skip) \
        .limit(limit) \
        .all()
    
    return comments


@router.post("/profiles/{profile_id}/comments", response_model=Comment, status_code=status.HTTP_201_CREATED)
def create_comment_for_profile(
    profile_id: int,
    comment: CommentCreate,
):
    """
    Создать новый комментарий к анкете.
    """
    # Проверяем существование анкеты
    db_profile = db.session.query(ProfileModel).filter(ProfileModel.id == profile_id).first()
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Анкета не найдена")
    
    db_comment = CommentModel(**comment.model_dump(), profile_id=profile_id)
    db.session.add(db_comment)
    db.session.commit()
    db.session.refresh(db_comment)
    return db_comment


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int):
    """
    Удалить комментарий.
    """
    db_comment = db.session.query(CommentModel).filter(CommentModel.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    
    db.session.delete(db_comment)
    db.session.commit()
    return None 