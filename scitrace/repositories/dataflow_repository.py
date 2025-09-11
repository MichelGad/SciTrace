"""
Dataflow repository for SciTrace

Provides data access methods for dataflow-related operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import json

from .base_repository import BaseRepository
from ..models import Dataflow
from ..exceptions import DatabaseError, ValidationError


class DataflowRepository(BaseRepository):
    """Repository for dataflow data access operations."""
    
    def __init__(self):
        super().__init__(Dataflow)
    
    def get_by_project(self, project_id: int) -> List[Dataflow]:
        """
        Get dataflows by project ID.
        
        Args:
            project_id: Project ID
        
        Returns:
            List of dataflows in the project
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.filter_by_all(project_id=project_id)
    
    def get_by_name(self, name: str) -> Optional[Dataflow]:
        """
        Get dataflow by name.
        
        Args:
            name: Dataflow name
        
        Returns:
            Dataflow instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.filter_by_first(name=name)
    
    def get_project_dataflow_by_name(self, project_id: int, name: str) -> Optional[Dataflow]:
        """
        Get dataflow by project ID and name.
        
        Args:
            project_id: Project ID
            name: Dataflow name
        
        Returns:
            Dataflow instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return Dataflow.query.filter_by(project_id=project_id, name=name).first()
        except Exception as e:
            raise DatabaseError(f"Failed to get project dataflow by name: {str(e)}")
    
    def create_dataflow(self, name: str, description: str, project_id: int,
                       nodes: List[Dict] = None, edges: List[Dict] = None,
                       metadata: Dict = None) -> Dataflow:
        """
        Create a new dataflow.
        
        Args:
            name: Dataflow name
            description: Dataflow description
            project_id: Project ID
            nodes: List of nodes (optional)
            edges: List of edges (optional)
            metadata: Additional metadata (optional)
        
        Returns:
            Created dataflow instance
        
        Raises:
            DatabaseError: If database operation fails
            ValidationError: If validation fails
        """
        # Check if dataflow with same name exists in project
        if self.get_project_dataflow_by_name(project_id, name):
            raise ValidationError(f"Dataflow '{name}' already exists in this project")
        
        # Convert data to JSON strings
        nodes_json = json.dumps(nodes) if nodes else None
        edges_json = json.dumps(edges) if edges else None
        metadata_json = json.dumps(metadata) if metadata else None
        
        return self.create(
            name=name,
            description=description,
            project_id=project_id,
            nodes=nodes_json,
            edges=edges_json,
            flow_metadata=metadata_json
        )
    
    def update_nodes(self, dataflow_id: int, nodes: List[Dict]) -> Optional[Dataflow]:
        """
        Update dataflow nodes.
        
        Args:
            dataflow_id: Dataflow ID
            nodes: List of nodes
        
        Returns:
            Updated dataflow instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        nodes_json = json.dumps(nodes)
        return self.update(dataflow_id, nodes=nodes_json, updated_at=datetime.now(timezone.utc))
    
    def update_edges(self, dataflow_id: int, edges: List[Dict]) -> Optional[Dataflow]:
        """
        Update dataflow edges.
        
        Args:
            dataflow_id: Dataflow ID
            edges: List of edges
        
        Returns:
            Updated dataflow instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        edges_json = json.dumps(edges)
        return self.update(dataflow_id, edges=edges_json, updated_at=datetime.now(timezone.utc))
    
    def update_metadata(self, dataflow_id: int, metadata: Dict) -> Optional[Dataflow]:
        """
        Update dataflow metadata.
        
        Args:
            dataflow_id: Dataflow ID
            metadata: Metadata dictionary
        
        Returns:
            Updated dataflow instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        metadata_json = json.dumps(metadata)
        return self.update(dataflow_id, flow_metadata=metadata_json, updated_at=datetime.now(timezone.utc))
    
    def update_structure(self, dataflow_id: int, nodes: List[Dict], edges: List[Dict],
                        metadata: Dict = None) -> Optional[Dataflow]:
        """
        Update dataflow structure (nodes, edges, and metadata).
        
        Args:
            dataflow_id: Dataflow ID
            nodes: List of nodes
            edges: List of edges
            metadata: Additional metadata (optional)
        
        Returns:
            Updated dataflow instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        update_data = {
            'nodes': json.dumps(nodes),
            'edges': json.dumps(edges),
            'updated_at': datetime.now(timezone.utc)
        }
        
        if metadata is not None:
            update_data['flow_metadata'] = json.dumps(metadata)
        
        return self.update(dataflow_id, **update_data)
    
    def get_nodes(self, dataflow_id: int) -> List[Dict]:
        """
        Get dataflow nodes.
        
        Args:
            dataflow_id: Dataflow ID
        
        Returns:
            List of nodes
        
        Raises:
            DatabaseError: If database operation fails
        """
        dataflow = self.get_by_id(dataflow_id)
        if not dataflow:
            return []
        
        return dataflow.get_nodes()
    
    def get_edges(self, dataflow_id: int) -> List[Dict]:
        """
        Get dataflow edges.
        
        Args:
            dataflow_id: Dataflow ID
        
        Returns:
            List of edges
        
        Raises:
            DatabaseError: If database operation fails
        """
        dataflow = self.get_by_id(dataflow_id)
        if not dataflow:
            return []
        
        return dataflow.get_edges()
    
    def get_metadata(self, dataflow_id: int) -> Dict:
        """
        Get dataflow metadata.
        
        Args:
            dataflow_id: Dataflow ID
        
        Returns:
            Metadata dictionary
        
        Raises:
            DatabaseError: If database operation fails
        """
        dataflow = self.get_by_id(dataflow_id)
        if not dataflow:
            return {}
        
        return dataflow.get_metadata()
    
    def get_structure(self, dataflow_id: int) -> Dict[str, Any]:
        """
        Get complete dataflow structure.
        
        Args:
            dataflow_id: Dataflow ID
        
        Returns:
            Dictionary with nodes, edges, and metadata
        
        Raises:
            DatabaseError: If database operation fails
        """
        dataflow = self.get_by_id(dataflow_id)
        if not dataflow:
            return {'nodes': [], 'edges': [], 'metadata': {}}
        
        return {
            'nodes': dataflow.get_nodes(),
            'edges': dataflow.get_edges(),
            'metadata': dataflow.get_metadata()
        }
    
    def search_dataflows(self, search_term: str) -> List[Dataflow]:
        """
        Search dataflows by name or description.
        
        Args:
            search_term: Search term
        
        Returns:
            List of matching dataflows
        
        Raises:
            DatabaseError: If database operation fails
        """
        search_fields = ['name', 'description']
        return self.search(search_term, search_fields)
    
    def get_recent_dataflows(self, limit: int = 10) -> List[Dataflow]:
        """
        Get recently created dataflows.
        
        Args:
            limit: Maximum number of dataflows to return
        
        Returns:
            List of recent dataflows
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return Dataflow.query.order_by(Dataflow.created_at.desc()).limit(limit).all()
        except Exception as e:
            raise DatabaseError(f"Failed to get recent dataflows: {str(e)}")
    
    def get_dataflow_stats(self) -> Dict[str, int]:
        """
        Get dataflow statistics.
        
        Returns:
            Dictionary with dataflow statistics
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            total_dataflows = self.count()
            
            # Count dataflows with nodes
            dataflows_with_nodes = Dataflow.query.filter(Dataflow.nodes.isnot(None)).count()
            
            # Count dataflows with edges
            dataflows_with_edges = Dataflow.query.filter(Dataflow.edges.isnot(None)).count()
            
            # Count dataflows with metadata
            dataflows_with_metadata = Dataflow.query.filter(Dataflow.flow_metadata.isnot(None)).count()
            
            return {
                'total_dataflows': total_dataflows,
                'dataflows_with_nodes': dataflows_with_nodes,
                'dataflows_with_edges': dataflows_with_edges,
                'dataflows_with_metadata': dataflows_with_metadata
            }
        except Exception as e:
            raise DatabaseError(f"Failed to get dataflow stats: {str(e)}")
    
    def get_project_dataflow_stats(self, project_id: int) -> Dict[str, int]:
        """
        Get dataflow statistics for a specific project.
        
        Args:
            project_id: Project ID
        
        Returns:
            Dictionary with project's dataflow statistics
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            project_dataflows = self.get_by_project(project_id)
            total = len(project_dataflows)
            
            with_nodes = len([d for d in project_dataflows if d.nodes])
            with_edges = len([d for d in project_dataflows if d.edges])
            with_metadata = len([d for d in project_dataflows if d.flow_metadata])
            
            return {
                'total_dataflows': total,
                'dataflows_with_nodes': with_nodes,
                'dataflows_with_edges': with_edges,
                'dataflows_with_metadata': with_metadata
            }
        except Exception as e:
            raise DatabaseError(f"Failed to get project dataflow stats: {str(e)}")
    
    def get_dataflows_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Dataflow]:
        """
        Get dataflows created within a date range.
        
        Args:
            start_date: Start date
            end_date: End date
        
        Returns:
            List of dataflows created in the date range
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return Dataflow.query.filter(
                Dataflow.created_at >= start_date,
                Dataflow.created_at <= end_date
            ).all()
        except Exception as e:
            raise DatabaseError(f"Failed to get dataflows by date range: {str(e)}")
    
    def get_dataflows_with_nodes(self) -> List[Dataflow]:
        """
        Get dataflows that have nodes defined.
        
        Returns:
            List of dataflows with nodes
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return Dataflow.query.filter(Dataflow.nodes.isnot(None)).all()
        except Exception as e:
            raise DatabaseError(f"Failed to get dataflows with nodes: {str(e)}")
    
    def get_dataflows_with_edges(self) -> List[Dataflow]:
        """
        Get dataflows that have edges defined.
        
        Returns:
            List of dataflows with edges
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return Dataflow.query.filter(Dataflow.edges.isnot(None)).all()
        except Exception as e:
            raise DatabaseError(f"Failed to get dataflows with edges: {str(e)}")
    
    def get_dataflows_with_metadata(self) -> List[Dataflow]:
        """
        Get dataflows that have metadata defined.
        
        Returns:
            List of dataflows with metadata
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return Dataflow.query.filter(Dataflow.flow_metadata.isnot(None)).all()
        except Exception as e:
            raise DatabaseError(f"Failed to get dataflows with metadata: {str(e)}")
    
    def is_name_available_in_project(self, project_id: int, name: str) -> bool:
        """
        Check if dataflow name is available in a project.
        
        Args:
            project_id: Project ID
            name: Dataflow name to check
        
        Returns:
            True if available, False if taken
        
        Raises:
            DatabaseError: If database operation fails
        """
        return not self.get_project_dataflow_by_name(project_id, name)
    
    def clone_dataflow(self, source_dataflow_id: int, new_name: str, new_description: str = None) -> Optional[Dataflow]:
        """
        Clone an existing dataflow.
        
        Args:
            source_dataflow_id: Source dataflow ID
            new_name: New dataflow name
            new_description: New dataflow description (optional)
        
        Returns:
            Cloned dataflow instance or None if source not found
        
        Raises:
            DatabaseError: If database operation fails
            ValidationError: If validation fails
        """
        source_dataflow = self.get_by_id(source_dataflow_id)
        if not source_dataflow:
            return None
        
        # Check if new name is available in the project
        if not self.is_name_available_in_project(source_dataflow.project_id, new_name):
            raise ValidationError(f"Dataflow name '{new_name}' already exists in this project")
        
        # Clone the dataflow
        return self.create_dataflow(
            name=new_name,
            description=new_description or source_dataflow.description,
            project_id=source_dataflow.project_id,
            nodes=source_dataflow.get_nodes(),
            edges=source_dataflow.get_edges(),
            metadata=source_dataflow.get_metadata()
        )
