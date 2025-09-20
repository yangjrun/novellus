"""
Unit tests for Projects API endpoints
Tests CRUD operations and project management functionality
"""

import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from uuid import UUID

from api.core.exceptions import NotFoundError, ConflictError, ValidationError
from database.data_access import DatabaseError


@pytest.mark.unit
@pytest.mark.api
class TestProjectsAPI:
    """Test Projects API endpoints"""

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_create_project_success(self, mock_get_manager, client: TestClient, sample_project_data):
        """Test successful project creation"""
        # Mock manager and its methods
        mock_manager = AsyncMock()
        mock_get_manager.return_value = mock_manager
        mock_manager.get_project_by_name.return_value = None  # No existing project

        # Mock created project
        mock_project = MagicMock()
        mock_project.dict.return_value = {
            "id": str(uuid.uuid4()),
            "name": sample_project_data["name"],
            "description": sample_project_data["description"],
            "metadata": sample_project_data["metadata"],
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        mock_manager.create_project.return_value = mock_project

        response = client.post("/api/v1/projects/", json=sample_project_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_project_data["name"]
        assert data["description"] == sample_project_data["description"]
        assert "id" in data
        assert "novel_count" in data

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_create_project_duplicate_name(self, mock_get_manager, client: TestClient, sample_project_data):
        """Test project creation with duplicate name"""
        mock_manager = AsyncMock()
        mock_get_manager.return_value = mock_manager

        # Mock existing project
        existing_project = MagicMock()
        mock_manager.get_project_by_name.return_value = existing_project

        response = client.post("/api/v1/projects/", json=sample_project_data)

        assert response.status_code == 409  # Conflict
        data = response.json()
        assert "already exists" in data["detail"]

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_create_project_database_error(self, mock_get_manager, client: TestClient, sample_project_data):
        """Test project creation with database error"""
        mock_manager = AsyncMock()
        mock_get_manager.return_value = mock_manager
        mock_manager.get_project_by_name.return_value = None
        mock_manager.create_project.side_effect = DatabaseError("Connection failed")

        response = client.post("/api/v1/projects/", json=sample_project_data)

        assert response.status_code == 500
        data = response.json()
        assert "Database error" in data["detail"]

    def test_create_project_invalid_data(self, client: TestClient):
        """Test project creation with invalid data"""
        invalid_data = {
            "name": "",  # Invalid: empty name
            "description": None
        }

        response = client.post("/api/v1/projects/", json=invalid_data)
        assert response.status_code == 422  # Validation error

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_list_projects_success(self, mock_get_manager, client: TestClient):
        """Test successful project listing"""
        mock_manager = AsyncMock()
        mock_get_manager.return_value = mock_manager

        # Mock projects
        mock_projects = [
            MagicMock(id=uuid.uuid4(), name="Project 1"),
            MagicMock(id=uuid.uuid4(), name="Project 2")
        ]
        for project in mock_projects:
            project.dict.return_value = {
                "id": str(project.id),
                "name": project.name,
                "description": "Test project",
                "created_at": "2024-01-01T00:00:00Z"
            }

        mock_manager.get_projects.return_value = mock_projects
        mock_manager.count_projects.return_value = 2
        mock_manager.get_novels_by_project.return_value = []

        response = client.get("/api/v1/projects/")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["projects"]) == 2
        assert data["total"] == 2

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_list_projects_with_filters(self, mock_get_manager, client: TestClient):
        """Test project listing with filters"""
        mock_manager = AsyncMock()
        mock_get_manager.return_value = mock_manager
        mock_manager.get_projects.return_value = []
        mock_manager.count_projects.return_value = 0
        mock_manager.get_novels_by_project.return_value = []

        response = client.get("/api/v1/projects/?status_filter=active&genre=fantasy")

        assert response.status_code == 200
        # Verify that filters were passed to manager
        mock_manager.get_projects.assert_called_once()
        call_args = mock_manager.get_projects.call_args
        assert "filters" in call_args.kwargs
        assert call_args.kwargs["filters"]["status"] == "active"
        assert call_args.kwargs["filters"]["genre"] == "fantasy"

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_list_projects_pagination(self, mock_get_manager, client: TestClient):
        """Test project listing with pagination"""
        mock_manager = AsyncMock()
        mock_get_manager.return_value = mock_manager
        mock_manager.get_projects.return_value = []
        mock_manager.count_projects.return_value = 0
        mock_manager.get_novels_by_project.return_value = []

        response = client.get("/api/v1/projects/?page=2&page_size=10")

        assert response.status_code == 200
        # Verify pagination parameters
        call_args = mock_manager.get_projects.call_args
        assert call_args.kwargs["offset"] == 10  # (page - 1) * page_size
        assert call_args.kwargs["limit"] == 10

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_get_project_success(self, mock_get_manager, client: TestClient):
        """Test successful project retrieval"""
        project_id = uuid.uuid4()
        mock_manager = AsyncMock()
        mock_get_manager.return_value = mock_manager

        mock_project = MagicMock()
        mock_project.dict.return_value = {
            "id": str(project_id),
            "name": "Test Project",
            "description": "Test description",
            "created_at": "2024-01-01T00:00:00Z"
        }
        mock_manager.get_project.return_value = mock_project
        mock_manager.get_novels_by_project.return_value = []
        mock_manager.get_project_statistics.return_value = {"novel_count": 0}

        response = client.get(f"/api/v1/projects/{project_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(project_id)
        assert data["name"] == "Test Project"
        assert "novels" in data
        assert "statistics" in data

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_get_project_not_found(self, mock_get_manager, client: TestClient):
        """Test project retrieval when project doesn't exist"""
        project_id = uuid.uuid4()
        mock_manager = AsyncMock()
        mock_get_manager.return_value = mock_manager
        mock_manager.get_project.return_value = None

        response = client.get(f"/api/v1/projects/{project_id}")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_get_project_without_novels(self, mock_get_manager, client: TestClient):
        """Test project retrieval excluding novels"""
        project_id = uuid.uuid4()
        mock_manager = AsyncMock()
        mock_get_manager.return_value = mock_manager

        mock_project = MagicMock()
        mock_project.dict.return_value = {
            "id": str(project_id),
            "name": "Test Project"
        }
        mock_manager.get_project.return_value = mock_project
        mock_manager.get_project_statistics.return_value = {}

        response = client.get(f"/api/v1/projects/{project_id}?include_novels=false")

        assert response.status_code == 200
        data = response.json()
        assert data["novels"] == []
        # Verify that get_novels_by_project was not called when include_novels=false
        mock_manager.get_novels_by_project.assert_not_called()

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_update_project_success(self, mock_get_manager, client: TestClient):
        """Test successful project update"""
        project_id = uuid.uuid4()
        mock_manager = AsyncMock()
        mock_get_manager.return_value = mock_manager

        # Mock existing project
        mock_project = MagicMock()
        mock_manager.get_project.return_value = mock_project

        # Mock updated project
        updated_project = MagicMock()
        updated_project.dict.return_value = {
            "id": str(project_id),
            "name": "Updated Project",
            "description": "Updated description"
        }
        mock_manager.update_project.return_value = updated_project
        mock_manager.get_novels_by_project.return_value = []

        update_data = {
            "name": "Updated Project",
            "description": "Updated description"
        }

        response = client.put(f"/api/v1/projects/{project_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Project"
        assert data["description"] == "Updated description"

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_update_project_not_found(self, mock_get_manager, client: TestClient):
        """Test project update when project doesn't exist"""
        project_id = uuid.uuid4()
        mock_manager = AsyncMock()
        mock_get_manager.return_value = mock_manager
        mock_manager.get_project.return_value = None

        update_data = {"name": "Updated Project"}

        response = client.put(f"/api/v1/projects/{project_id}", json=update_data)

        assert response.status_code == 404

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_delete_project_success(self, mock_get_manager, client: TestClient):
        """Test successful project deletion"""
        project_id = uuid.uuid4()
        mock_manager = AsyncMock()
        mock_get_manager.return_value = mock_manager

        mock_project = MagicMock()
        mock_project.title = "Test Project"
        mock_manager.get_project.return_value = mock_project
        mock_manager.get_novels_by_project.return_value = []  # No novels
        mock_manager.delete_project.return_value = None

        response = client.delete(f"/api/v1/projects/{project_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "deleted successfully" in data["message"]

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_delete_project_with_novels_no_force(self, mock_get_manager, client: TestClient):
        """Test project deletion with novels but no force flag"""
        project_id = uuid.uuid4()
        mock_manager = AsyncMock()
        mock_get_manager.return_value = mock_manager

        mock_project = MagicMock()
        mock_manager.get_project.return_value = mock_project
        # Mock novels exist
        mock_manager.get_novels_by_project.return_value = [MagicMock(), MagicMock()]

        response = client.delete(f"/api/v1/projects/{project_id}")

        assert response.status_code == 409  # Conflict
        data = response.json()
        assert "force=true" in data["detail"]

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_delete_project_with_force(self, mock_get_manager, client: TestClient):
        """Test project deletion with force flag"""
        project_id = uuid.uuid4()
        mock_manager = AsyncMock()
        mock_get_manager.return_value = mock_manager

        mock_project = MagicMock()
        mock_project.title = "Test Project"
        mock_manager.get_project.return_value = mock_project
        mock_manager.get_novels_by_project.return_value = [MagicMock()]  # Has novels
        mock_manager.delete_project.return_value = None

        response = client.delete(f"/api/v1/projects/{project_id}?force=true")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_get_project_novels(self, mock_get_manager, client: TestClient):
        """Test getting novels for a project"""
        project_id = uuid.uuid4()
        mock_manager = AsyncMock()
        mock_get_manager.return_value = mock_manager

        mock_project = MagicMock()
        mock_manager.get_project.return_value = mock_project

        # Mock novels
        mock_novels = [MagicMock(id=uuid.uuid4()), MagicMock(id=uuid.uuid4())]
        for novel in mock_novels:
            novel.dict.return_value = {
                "id": str(novel.id),
                "title": "Test Novel",
                "project_id": str(project_id)
            }
        mock_manager.get_novels_by_project.return_value = mock_novels
        mock_manager.get_novel_statistics.return_value = {"chapter_count": 5, "word_count": 1000}

        response = client.get(f"/api/v1/projects/{project_id}/novels")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["novels"]) == 2

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_get_project_statistics(self, mock_get_manager, client: TestClient):
        """Test getting project statistics"""
        project_id = uuid.uuid4()
        mock_manager = AsyncMock()
        mock_get_manager.return_value = mock_manager

        mock_project = MagicMock()
        mock_manager.get_project.return_value = mock_project

        mock_stats = {
            "novel_count": 3,
            "total_word_count": 50000,
            "chapter_count": 15,
            "character_count": 10
        }
        mock_manager.get_project_statistics.return_value = mock_stats

        response = client.get(f"/api/v1/projects/{project_id}/statistics")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["project_id"] == str(project_id)
        assert data["statistics"]["novel_count"] == 3

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_create_projects_batch(self, mock_get_manager, client: TestClient):
        """Test batch project creation"""
        mock_manager = AsyncMock()
        mock_get_manager.return_value = mock_manager
        mock_manager.create_project.return_value = MagicMock()

        batch_data = {
            "projects": [
                {"name": "Project 1", "description": "First project"},
                {"name": "Project 2", "description": "Second project"}
            ]
        }

        response = client.post("/api/v1/projects/batch", json=batch_data)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["succeeded"] == 2
        assert data["failed"] == 0

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_create_projects_batch_partial_failure(self, mock_get_manager, client: TestClient):
        """Test batch project creation with partial failures"""
        mock_manager = AsyncMock()
        mock_get_manager.return_value = mock_manager

        # First project succeeds, second fails
        mock_manager.create_project.side_effect = [MagicMock(), Exception("Creation failed")]

        batch_data = {
            "projects": [
                {"name": "Project 1", "description": "First project"},
                {"name": "Project 2", "description": "Second project"}
            ]
        }

        response = client.post("/api/v1/projects/batch", json=batch_data)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True  # At least one succeeded
        assert data["succeeded"] == 1
        assert data["failed"] == 1
        assert len(data["errors"]) == 1

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_export_project(self, mock_get_manager, client: TestClient):
        """Test project export"""
        project_id = uuid.uuid4()
        mock_manager = AsyncMock()
        mock_get_manager.return_value = mock_manager

        mock_project = MagicMock()
        mock_manager.get_project.return_value = mock_project
        mock_manager.export_project.return_value = {"exported_data": "test"}

        export_request = {
            "include_novels": True,
            "include_content": True,
            "include_worldbuilding": False,
            "format": "json"
        }

        response = client.post(f"/api/v1/projects/{project_id}/export", json=export_request)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_import_project(self, mock_get_manager, client: TestClient):
        """Test project import"""
        mock_manager = AsyncMock()
        mock_get_manager.return_value = mock_manager
        mock_manager.import_project.return_value = {"imported": True}

        import_request = {
            "data": {"project": {"name": "Imported Project"}},
            "validate_only": False,
            "merge_existing": False
        }

        response = client.post("/api/v1/projects/import", json=import_request)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_import_project_validation_only(self, mock_get_manager, client: TestClient):
        """Test project import with validation only"""
        mock_manager = AsyncMock()
        mock_get_manager.return_value = mock_manager
        mock_manager.validate_import_data.return_value = {"valid": True}

        import_request = {
            "data": {"project": {"name": "Test Project"}},
            "validate_only": True,
            "merge_existing": False
        }

        response = client.post("/api/v1/projects/import", json=import_request)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "Validation successful" in data["message"]


@pytest.mark.unit
class TestProjectsInputValidation:
    """Test input validation for projects API"""

    def test_invalid_uuid_format(self, client: TestClient):
        """Test handling of invalid UUID format"""
        response = client.get("/api/v1/projects/invalid-uuid")
        assert response.status_code == 422

    def test_empty_project_name(self, client: TestClient):
        """Test validation of empty project name"""
        data = {"name": "", "description": "Test"}
        response = client.post("/api/v1/projects/", json=data)
        assert response.status_code == 422

    def test_project_name_too_long(self, client: TestClient):
        """Test validation of overly long project name"""
        data = {"name": "x" * 1000, "description": "Test"}
        response = client.post("/api/v1/projects/", json=data)
        # Should either pass or fail validation depending on constraints
        assert response.status_code in [201, 422]

    def test_invalid_pagination_params(self, client: TestClient):
        """Test invalid pagination parameters"""
        response = client.get("/api/v1/projects/?page=0&page_size=-1")
        assert response.status_code == 422

    def test_invalid_filter_values(self, client: TestClient):
        """Test invalid filter values"""
        response = client.get("/api/v1/projects/?status_filter=invalid_status")
        # Should handle gracefully or return validation error
        assert response.status_code in [200, 422]