"""
Base repository class for SciTrace

Provides common database query patterns and operations.
"""

from typing import List, Optional, Dict, Any, Type, TypeVar
from sqlalchemy.orm import Query
from sqlalchemy.exc import SQLAlchemyError

from ..models import db
from ..exceptions import DatabaseError, ValidationError

T = TypeVar('T')


class BaseRepository:
    """Base repository class with common database operations."""
    
    def __init__(self, model_class: Type[T]):
        """
        Initialize repository with a model class.
        
        Args:
            model_class: SQLAlchemy model class
        """
        self.model_class = model_class
    
    def get_by_id(self, id: int) -> Optional[T]:
        """
        Get a record by ID.
        
        Args:
            id: Record ID
        
        Returns:
            Model instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return self.model_class.query.get(id)
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to get {self.model_class.__name__} by ID: {str(e)}")
    
    def get_by_id_or_404(self, id: int) -> T:
        """
        Get a record by ID or raise 404 error.
        
        Args:
            id: Record ID
        
        Returns:
            Model instance
        
        Raises:
            DatabaseError: If database operation fails
            ValidationError: If record not found
        """
        record = self.get_by_id(id)
        if not record:
            raise ValidationError(f"{self.model_class.__name__} with ID {id} not found")
        return record
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """
        Get all records with optional pagination.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
        
        Returns:
            List of model instances
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            query = self.model_class.query.offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to get all {self.model_class.__name__} records: {str(e)}")
    
    def count(self) -> int:
        """
        Get total count of records.
        
        Returns:
            Total count
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return self.model_class.query.count()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to count {self.model_class.__name__} records: {str(e)}")
    
    def create(self, **kwargs) -> T:
        """
        Create a new record.
        
        Args:
            **kwargs: Model attributes
        
        Returns:
            Created model instance
        
        Raises:
            DatabaseError: If database operation fails
            ValidationError: If validation fails
        """
        try:
            record = self.model_class(**kwargs)
            db.session.add(record)
            db.session.commit()
            return record
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to create {self.model_class.__name__}: {str(e)}")
        except Exception as e:
            db.session.rollback()
            raise ValidationError(f"Validation failed for {self.model_class.__name__}: {str(e)}")
    
    def update(self, id: int, **kwargs) -> Optional[T]:
        """
        Update a record by ID.
        
        Args:
            id: Record ID
            **kwargs: Attributes to update
        
        Returns:
            Updated model instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            record = self.get_by_id(id)
            if not record:
                return None
            
            for key, value in kwargs.items():
                if hasattr(record, key):
                    setattr(record, key, value)
            
            db.session.commit()
            return record
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to update {self.model_class.__name__}: {str(e)}")
    
    def delete(self, id: int) -> bool:
        """
        Delete a record by ID.
        
        Args:
            id: Record ID
        
        Returns:
            True if deleted, False if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            record = self.get_by_id(id)
            if not record:
                return False
            
            db.session.delete(record)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to delete {self.model_class.__name__}: {str(e)}")
    
    def filter_by(self, **kwargs) -> Query:
        """
        Get query filtered by attributes.
        
        Args:
            **kwargs: Filter attributes
        
        Returns:
            SQLAlchemy query object
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return self.model_class.query.filter_by(**kwargs)
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to filter {self.model_class.__name__}: {str(e)}")
    
    def filter_by_first(self, **kwargs) -> Optional[T]:
        """
        Get first record matching filter criteria.
        
        Args:
            **kwargs: Filter attributes
        
        Returns:
            Model instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return self.model_class.query.filter_by(**kwargs).first()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to filter {self.model_class.__name__}: {str(e)}")
    
    def filter_by_all(self, **kwargs) -> List[T]:
        """
        Get all records matching filter criteria.
        
        Args:
            **kwargs: Filter attributes
        
        Returns:
            List of model instances
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return self.model_class.query.filter_by(**kwargs).all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to filter {self.model_class.__name__}: {str(e)}")
    
    def exists(self, **kwargs) -> bool:
        """
        Check if a record exists with given criteria.
        
        Args:
            **kwargs: Filter attributes
        
        Returns:
            True if record exists, False otherwise
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return self.model_class.query.filter_by(**kwargs).first() is not None
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to check existence of {self.model_class.__name__}: {str(e)}")
    
    def bulk_create(self, records_data: List[Dict[str, Any]]) -> List[T]:
        """
        Create multiple records in bulk.
        
        Args:
            records_data: List of dictionaries with record data
        
        Returns:
            List of created model instances
        
        Raises:
            DatabaseError: If database operation fails
            ValidationError: If validation fails
        """
        try:
            records = []
            for data in records_data:
                record = self.model_class(**data)
                records.append(record)
                db.session.add(record)
            
            db.session.commit()
            return records
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to bulk create {self.model_class.__name__}: {str(e)}")
        except Exception as e:
            db.session.rollback()
            raise ValidationError(f"Validation failed for bulk create {self.model_class.__name__}: {str(e)}")
    
    def bulk_update(self, updates: List[Dict[str, Any]]) -> int:
        """
        Update multiple records in bulk.
        
        Args:
            updates: List of dictionaries with 'id' and update data
        
        Returns:
            Number of records updated
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            updated_count = 0
            for update_data in updates:
                record_id = update_data.pop('id')
                record = self.get_by_id(record_id)
                if record:
                    for key, value in update_data.items():
                        if hasattr(record, key):
                            setattr(record, key, value)
                    updated_count += 1
            
            db.session.commit()
            return updated_count
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to bulk update {self.model_class.__name__}: {str(e)}")
    
    def bulk_delete(self, ids: List[int]) -> int:
        """
        Delete multiple records by IDs.
        
        Args:
            ids: List of record IDs to delete
        
        Returns:
            Number of records deleted
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            deleted_count = 0
            for record_id in ids:
                record = self.get_by_id(record_id)
                if record:
                    db.session.delete(record)
                    deleted_count += 1
            
            db.session.commit()
            return deleted_count
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to bulk delete {self.model_class.__name__}: {str(e)}")
    
    def search(self, search_term: str, search_fields: List[str]) -> List[T]:
        """
        Search records by text in specified fields.
        
        Args:
            search_term: Text to search for
            search_fields: List of field names to search in
        
        Returns:
            List of matching model instances
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            from sqlalchemy import or_
            
            if not search_term or not search_fields:
                return []
            
            # Build search conditions
            conditions = []
            for field in search_fields:
                if hasattr(self.model_class, field):
                    column = getattr(self.model_class, field)
                    conditions.append(column.ilike(f'%{search_term}%'))
            
            if not conditions:
                return []
            
            return self.model_class.query.filter(or_(*conditions)).all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to search {self.model_class.__name__}: {str(e)}")
    
    def paginate(self, page: int = 1, per_page: int = 20, **filters) -> Dict[str, Any]:
        """
        Get paginated results with optional filters.
        
        Args:
            page: Page number (1-based)
            per_page: Number of items per page
            **filters: Filter criteria
        
        Returns:
            Dictionary with pagination data
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            query = self.model_class.query
            
            # Apply filters
            for key, value in filters.items():
                if hasattr(self.model_class, key) and value is not None:
                    column = getattr(self.model_class, key)
                    query = query.filter(column == value)
            
            # Get pagination
            pagination = query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            return {
                'items': pagination.items,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': pagination.page,
                'per_page': pagination.per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev,
                'next_num': pagination.next_num,
                'prev_num': pagination.prev_num
            }
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to paginate {self.model_class.__name__}: {str(e)}")
