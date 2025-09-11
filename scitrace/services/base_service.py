"""
Base service class for SciTrace

Provides common database and error handling patterns for all services.
"""

import logging
from typing import Any, Dict, List, Optional, Type, TypeVar
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from flask_sqlalchemy import SQLAlchemy

from ..exceptions import (
    DatabaseError, ServiceError, ResourceNotFoundError, 
    ResourceConflictError, ValidationError
)
from ..utils.response_utils import APIResponse

# Type variable for model classes
ModelType = TypeVar('ModelType')

logger = logging.getLogger(__name__)


class BaseService:
    """Base service class with common database and error handling patterns."""
    
    def __init__(self, db: SQLAlchemy):
        """
        Initialize base service.
        
        Args:
            db: SQLAlchemy database instance
        """
        self.db = db
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _handle_database_error(self, operation: str, error: Exception) -> None:
        """
        Handle database errors with standardized logging and exceptions.
        
        Args:
            operation: Description of the operation that failed
            error: The database error that occurred
        
        Raises:
            DatabaseError: Standardized database error
        """
        self.logger.error(f"Database error during {operation}: {str(error)}", exc_info=error)
        raise DatabaseError(
            message=f"Database operation failed: {operation}",
            operation=operation,
            details={'original_error': str(error)}
        )
    
    def _handle_service_error(self, operation: str, error: Exception) -> None:
        """
        Handle service errors with standardized logging and exceptions.
        
        Args:
            operation: Description of the operation that failed
            error: The service error that occurred
        
        Raises:
            ServiceError: Standardized service error
        """
        self.logger.error(f"Service error during {operation}: {str(error)}", exc_info=error)
        raise ServiceError(
            message=f"Service operation failed: {operation}",
            service_name=self.__class__.__name__,
            details={'original_error': str(error)}
        )
    
    def get_by_id(self, model_class: Type[ModelType], id: Any) -> Optional[ModelType]:
        """
        Get a model instance by ID.
        
        Args:
            model_class: The model class to query
            id: The ID to search for
        
        Returns:
            Model instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return model_class.query.get(id)
        except SQLAlchemyError as e:
            self._handle_database_error(f"get_by_id for {model_class.__name__}", e)
    
    def get_by_id_or_404(self, model_class: Type[ModelType], id: Any) -> ModelType:
        """
        Get a model instance by ID or raise 404 error.
        
        Args:
            model_class: The model class to query
            id: The ID to search for
        
        Returns:
            Model instance
        
        Raises:
            ResourceNotFoundError: If model not found
            DatabaseError: If database operation fails
        """
        instance = self.get_by_id(model_class, id)
        if not instance:
            raise ResourceNotFoundError(
                message=f"{model_class.__name__} not found",
                resource_type=model_class.__name__,
                resource_id=str(id)
            )
        return instance
    
    def get_all(self, model_class: Type[ModelType], **filters) -> List[ModelType]:
        """
        Get all instances of a model with optional filters.
        
        Args:
            model_class: The model class to query
            **filters: Optional filters to apply
        
        Returns:
            List of model instances
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            query = model_class.query
            for key, value in filters.items():
                if hasattr(model_class, key):
                    query = query.filter(getattr(model_class, key) == value)
            return query.all()
        except SQLAlchemyError as e:
            self._handle_database_error(f"get_all for {model_class.__name__}", e)
    
    def create(self, model_class: Type[ModelType], **data) -> ModelType:
        """
        Create a new model instance.
        
        Args:
            model_class: The model class to create
            **data: Data for the new instance
        
        Returns:
            Created model instance
        
        Raises:
            DatabaseError: If database operation fails
            ValidationError: If validation fails
        """
        try:
            # Validate required fields
            self._validate_required_fields(model_class, data)
            
            instance = model_class(**data)
            self.db.session.add(instance)
            self.db.session.commit()
            
            self.logger.info(f"Created {model_class.__name__} with ID: {instance.id}")
            return instance
            
        except SQLAlchemyError as e:
            self.db.session.rollback()
            self._handle_database_error(f"create for {model_class.__name__}", e)
        except Exception as e:
            self.db.session.rollback()
            self._handle_service_error(f"create for {model_class.__name__}", e)
    
    def update(self, instance: ModelType, **data) -> ModelType:
        """
        Update a model instance.
        
        Args:
            instance: The model instance to update
            **data: Data to update
        
        Returns:
            Updated model instance
        
        Raises:
            DatabaseError: If database operation fails
            ValidationError: If validation fails
        """
        try:
            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
                else:
                    raise ValidationError(
                        message=f"Invalid field: {key}",
                        field=key,
                        value=value
                    )
            
            self.db.session.commit()
            
            self.logger.info(f"Updated {instance.__class__.__name__} with ID: {instance.id}")
            return instance
            
        except SQLAlchemyError as e:
            self.db.session.rollback()
            self._handle_database_error(f"update for {instance.__class__.__name__}", e)
        except Exception as e:
            self.db.session.rollback()
            self._handle_service_error(f"update for {instance.__class__.__name__}", e)
    
    def delete(self, instance: ModelType) -> bool:
        """
        Delete a model instance.
        
        Args:
            instance: The model instance to delete
        
        Returns:
            True if deletion was successful
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            instance_id = instance.id
            instance_class = instance.__class__.__name__
            
            self.db.session.delete(instance)
            self.db.session.commit()
            
            self.logger.info(f"Deleted {instance_class} with ID: {instance_id}")
            return True
            
        except SQLAlchemyError as e:
            self.db.session.rollback()
            self._handle_database_error(f"delete for {instance.__class__.__name__}", e)
    
    def delete_by_id(self, model_class: Type[ModelType], id: Any) -> bool:
        """
        Delete a model instance by ID.
        
        Args:
            model_class: The model class to delete from
            id: The ID of the instance to delete
        
        Returns:
            True if deletion was successful
        
        Raises:
            ResourceNotFoundError: If model not found
            DatabaseError: If database operation fails
        """
        instance = self.get_by_id_or_404(model_class, id)
        return self.delete(instance)
    
    def exists(self, model_class: Type[ModelType], **filters) -> bool:
        """
        Check if a model instance exists with given filters.
        
        Args:
            model_class: The model class to query
            **filters: Filters to apply
        
        Returns:
            True if instance exists, False otherwise
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            query = model_class.query
            for key, value in filters.items():
                if hasattr(model_class, key):
                    query = query.filter(getattr(model_class, key) == value)
            return query.first() is not None
        except SQLAlchemyError as e:
            self._handle_database_error(f"exists check for {model_class.__name__}", e)
    
    def count(self, model_class: Type[ModelType], **filters) -> int:
        """
        Count instances of a model with optional filters.
        
        Args:
            model_class: The model class to query
            **filters: Optional filters to apply
        
        Returns:
            Number of matching instances
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            query = model_class.query
            for key, value in filters.items():
                if hasattr(model_class, key):
                    query = query.filter(getattr(model_class, key) == value)
            return query.count()
        except SQLAlchemyError as e:
            self._handle_database_error(f"count for {model_class.__name__}", e)
    
    def paginate(
        self, 
        model_class: Type[ModelType], 
        page: int = 1, 
        per_page: int = 20, 
        **filters
    ) -> Dict[str, Any]:
        """
        Get paginated results for a model.
        
        Args:
            model_class: The model class to query
            page: Page number (1-based)
            per_page: Number of items per page
            **filters: Optional filters to apply
        
        Returns:
            Dict containing paginated results and metadata
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            query = model_class.query
            for key, value in filters.items():
                if hasattr(model_class, key):
                    query = query.filter(getattr(model_class, key) == value)
            
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
                'has_prev': pagination.has_prev
            }
            
        except SQLAlchemyError as e:
            self._handle_database_error(f"paginate for {model_class.__name__}", e)
    
    def _validate_required_fields(self, model_class: Type[ModelType], data: Dict[str, Any]) -> None:
        """
        Validate that required fields are present in the data.
        
        Args:
            model_class: The model class to validate against
            data: The data to validate
        
        Raises:
            ValidationError: If required fields are missing
        """
        # This is a basic implementation - can be extended based on model requirements
        # For now, we'll just check for common required fields
        required_fields = ['name', 'title']  # Add more as needed
        
        for field in required_fields:
            if hasattr(model_class, field) and field not in data:
                raise ValidationError(
                    message=f"Required field missing: {field}",
                    field=field
                )
    
    def bulk_create(self, model_class: Type[ModelType], data_list: List[Dict[str, Any]]) -> List[ModelType]:
        """
        Create multiple model instances in a single transaction.
        
        Args:
            model_class: The model class to create
            data_list: List of data dictionaries for new instances
        
        Returns:
            List of created model instances
        
        Raises:
            DatabaseError: If database operation fails
            ValidationError: If validation fails
        """
        try:
            instances = []
            for data in data_list:
                self._validate_required_fields(model_class, data)
                instance = model_class(**data)
                instances.append(instance)
                self.db.session.add(instance)
            
            self.db.session.commit()
            
            self.logger.info(f"Bulk created {len(instances)} {model_class.__name__} instances")
            return instances
            
        except SQLAlchemyError as e:
            self.db.session.rollback()
            self._handle_database_error(f"bulk_create for {model_class.__name__}", e)
        except Exception as e:
            self.db.session.rollback()
            self._handle_service_error(f"bulk_create for {model_class.__name__}", e)
    
    def bulk_update(self, instances: List[ModelType], data_list: List[Dict[str, Any]]) -> List[ModelType]:
        """
        Update multiple model instances in a single transaction.
        
        Args:
            instances: List of model instances to update
            data_list: List of data dictionaries for updates
        
        Returns:
            List of updated model instances
        
        Raises:
            DatabaseError: If database operation fails
            ValidationError: If validation fails
        """
        if len(instances) != len(data_list):
            raise ValidationError(
                message="Number of instances must match number of data dictionaries",
                details={'instances_count': len(instances), 'data_count': len(data_list)}
            )
        
        try:
            for instance, data in zip(instances, data_list):
                for key, value in data.items():
                    if hasattr(instance, key):
                        setattr(instance, key, value)
                    else:
                        raise ValidationError(
                            message=f"Invalid field: {key}",
                            field=key,
                            value=value
                        )
            
            self.db.session.commit()
            
            self.logger.info(f"Bulk updated {len(instances)} instances")
            return instances
            
        except SQLAlchemyError as e:
            self.db.session.rollback()
            self._handle_database_error("bulk_update", e)
        except Exception as e:
            self.db.session.rollback()
            self._handle_service_error("bulk_update", e)
    
    def execute_raw_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute a raw SQL query.
        
        Args:
            query: SQL query string
            params: Optional query parameters
        
        Returns:
            List of result dictionaries
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            result = self.db.session.execute(query, params or {})
            return [dict(row) for row in result]
        except SQLAlchemyError as e:
            self._handle_database_error("raw query execution", e)
    
    def get_session(self) -> Session:
        """
        Get the current database session.
        
        Returns:
            SQLAlchemy session
        """
        return self.db.session
