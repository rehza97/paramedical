from contextlib import contextmanager
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


def validate_positive_int(value: int, field_name: str):
    """Ensure a field is a positive integer."""
    if value <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{field_name} doit être un entier positif."
        )


def validate_string_length(value: str, field_name: str, min_length: int, max_length: int):
    """Ensure a string field is within min/max length."""
    if not value or len(value.strip()) < min_length:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{field_name} doit contenir au moins {min_length} caractères."
        )
    if len(value.strip()) > max_length:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{field_name} ne peut pas dépasser {max_length} caractères."
        )


def handle_db_commit(db, error_message: str):
    """Try to commit the session, rollback and raise HTTPException on error."""
    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{error_message}: {str(e)}"
        )


def handle_unique_constraint(error: Exception, field_name: str):
    """Raise HTTPException for unique constraint violations."""
    if isinstance(error, IntegrityError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{field_name} doit être unique."
        )
    raise error


@contextmanager
def db_commit_context(db, error_message: str):
    """Context manager for db commit/rollback with error handling."""
    try:
        yield
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{error_message}: {str(e)}"
        )
