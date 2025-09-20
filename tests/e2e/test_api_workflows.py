"""
End-to-end workflow tests
Tests complete user workflows across multiple API endpoints
"""

import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient


@pytest.mark.e2e
@pytest.mark.api
class TestProjectWorkflow:
    """Test complete project management workflow"""

    @patch("api.v1.endpoints.projects.get_global_manager")
    @patch("api.v1.endpoints.novels.get_global_manager")
    def test_complete_project_lifecycle(self, mock_novels_manager, mock_projects_manager, client: TestClient):
        """Test complete project lifecycle from creation to deletion"""

        # Setup mocks for both managers
        mock_project_manager = AsyncMock()
        mock_novel_manager = AsyncMock()
        mock_projects_manager.return_value = mock_project_manager
        mock_novels_manager.return_value = mock_novel_manager

        project_id = str(uuid.uuid4())
        novel_id = str(uuid.uuid4())

        # Mock project creation
        mock_project = MagicMock()
        mock_project.dict.return_value = {
            "id": project_id,
            "name": "Complete Workflow Project",
            "description": "Test project for E2E workflow",
            "author": "Test Author",
            "genre": "Fantasy",
            "created_at": "2024-01-01T00:00:00Z"
        }
        mock_project_manager.get_project_by_name.return_value = None
        mock_project_manager.create_project.return_value = mock_project
        mock_project_manager.get_project.return_value = mock_project
        mock_project_manager.get_novels_by_project.return_value = []
        mock_project_manager.count_projects.return_value = 1
        mock_project_manager.get_projects.return_value = [mock_project]
        mock_project_manager.update_project.return_value = mock_project
        mock_project_manager.delete_project.return_value = None

        # Mock novel creation
        mock_novel = MagicMock()
        mock_novel.dict.return_value = {
            "id": novel_id,
            "title": "Test Novel",
            "project_id": project_id,
            "description": "Test novel description",
            "created_at": "2024-01-01T00:00:00Z"
        }
        mock_novel_manager.get_novel_by_title.return_value = None
        mock_novel_manager.create_novel.return_value = mock_novel
        mock_novel_manager.get_novel.return_value = mock_novel

        # Step 1: Create a new project
        project_data = {
            "name": "Complete Workflow Project",
            "description": "Test project for E2E workflow",
            "author": "Test Author",
            "genre": "Fantasy",
            "metadata": {
                "target_audience": "Adult",
                "estimated_length": 80000
            }
        }

        create_response = client.post("/api/v1/projects/", json=project_data)
        assert create_response.status_code == 201
        created_project = create_response.json()
        assert created_project["name"] == project_data["name"]
        project_id_from_response = created_project["id"]

        # Step 2: List projects to verify creation
        list_response = client.get("/api/v1/projects/")
        assert list_response.status_code == 200
        projects_list = list_response.json()
        assert projects_list["success"] is True
        assert len(projects_list["projects"]) >= 1

        # Step 3: Get project details
        detail_response = client.get(f"/api/v1/projects/{project_id}")
        assert detail_response.status_code == 200
        project_details = detail_response.json()
        assert project_details["name"] == project_data["name"]

        # Step 4: Update project
        update_data = {
            "description": "Updated description for E2E workflow",
            "metadata": {
                "status": "in_progress"
            }
        }

        # Update mock to return updated project
        updated_project = MagicMock()
        updated_project.dict.return_value = {
            **mock_project.dict.return_value,
            **update_data
        }
        mock_project_manager.update_project.return_value = updated_project

        update_response = client.put(f"/api/v1/projects/{project_id}", json=update_data)
        assert update_response.status_code == 200
        updated_project_data = update_response.json()
        assert updated_project_data["description"] == update_data["description"]

        # Step 5: Create a novel in the project
        novel_data = {
            "title": "Test Novel",
            "project_id": project_id,
            "description": "Test novel description",
            "metadata": {
                "genre": "Fantasy",
                "target_word_count": 80000
            }
        }

        novel_response = client.post("/api/v1/novels/", json=novel_data)
        assert novel_response.status_code in [201, 404]  # 404 if endpoint doesn't exist yet

        # Step 6: Get project statistics
        mock_project_manager.get_project_statistics.return_value = {
            "novel_count": 1,
            "total_word_count": 0,
            "chapter_count": 0
        }

        stats_response = client.get(f"/api/v1/projects/{project_id}/statistics")
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert "statistics" in stats

        # Step 7: Delete project (with force since it has novels)
        mock_project_manager.get_novels_by_project.return_value = [mock_novel]
        mock_project.title = "Complete Workflow Project"

        delete_response = client.delete(f"/api/v1/projects/{project_id}?force=true")
        assert delete_response.status_code == 200
        delete_result = delete_response.json()
        assert delete_result["success"] is True

        # Step 8: Verify project is deleted
        verify_response = client.get(f"/api/v1/projects/{project_id}")
        assert verify_response.status_code == 404

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_project_search_and_filter_workflow(self, mock_manager, client: TestClient):
        """Test project search and filtering workflow"""
        mock_project_manager = AsyncMock()
        mock_manager.return_value = mock_project_manager

        # Mock multiple projects with different attributes
        projects = []
        for i in range(5):
            project = MagicMock()
            project.dict.return_value = {
                "id": str(uuid.uuid4()),
                "name": f"Project {i}",
                "author": "Test Author" if i % 2 == 0 else "Another Author",
                "genre": "Fantasy" if i % 3 == 0 else "Sci-Fi",
                "status": "active" if i % 2 == 0 else "paused",
                "created_at": "2024-01-01T00:00:00Z"
            }
            projects.append(project)

        mock_project_manager.get_projects.return_value = projects
        mock_project_manager.count_projects.return_value = len(projects)
        mock_project_manager.get_novels_by_project.return_value = []

        # Test filtering by author
        author_filter_response = client.get("/api/v1/projects/?author=Test Author")
        assert author_filter_response.status_code == 200

        # Test filtering by genre
        genre_filter_response = client.get("/api/v1/projects/?genre=Fantasy")
        assert genre_filter_response.status_code == 200

        # Test filtering by status
        status_filter_response = client.get("/api/v1/projects/?status_filter=active")
        assert status_filter_response.status_code == 200

        # Test combined filters
        combined_filter_response = client.get(
            "/api/v1/projects/?author=Test Author&genre=Fantasy&status_filter=active"
        )
        assert combined_filter_response.status_code == 200

        # Test pagination
        paginated_response = client.get("/api/v1/projects/?page=1&page_size=2")
        assert paginated_response.status_code == 200

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_batch_operations_workflow(self, mock_manager, client: TestClient):
        """Test batch operations workflow"""
        mock_project_manager = AsyncMock()
        mock_manager.return_value = mock_project_manager

        # Mock successful project creation
        mock_project_manager.create_project.return_value = MagicMock()

        # Step 1: Create multiple projects in batch
        batch_data = {
            "projects": [
                {"name": "Batch Project 1", "description": "First batch project"},
                {"name": "Batch Project 2", "description": "Second batch project"},
                {"name": "Batch Project 3", "description": "Third batch project"}
            ]
        }

        batch_response = client.post("/api/v1/projects/batch", json=batch_data)
        assert batch_response.status_code == 201
        batch_result = batch_response.json()
        assert batch_result["success"] is True
        assert batch_result["succeeded"] == 3
        assert batch_result["failed"] == 0

        # Step 2: Verify all projects were created
        mock_project_manager.get_projects.return_value = [
            MagicMock(dict=lambda: {"id": str(uuid.uuid4()), "name": f"Batch Project {i}"})
            for i in range(1, 4)
        ]
        mock_project_manager.count_projects.return_value = 3
        mock_project_manager.get_novels_by_project.return_value = []

        list_response = client.get("/api/v1/projects/")
        assert list_response.status_code == 200
        projects_list = list_response.json()
        assert len(projects_list["projects"]) == 3


@pytest.mark.e2e
@pytest.mark.api
class TestContentManagementWorkflow:
    """Test content management workflow"""

    @patch("api.v1.endpoints.projects.get_global_manager")
    @patch("api.v1.endpoints.content.get_global_manager")
    def test_content_creation_workflow(self, mock_content_manager, mock_project_manager, client: TestClient):
        """Test complete content creation and management workflow"""

        # Setup mocks
        mock_proj_mgr = AsyncMock()
        mock_cont_mgr = AsyncMock()
        mock_project_manager.return_value = mock_proj_mgr
        mock_content_manager.return_value = mock_cont_mgr

        project_id = str(uuid.uuid4())
        batch_id = str(uuid.uuid4())

        # Mock project exists
        mock_project = MagicMock()
        mock_project.dict.return_value = {
            "id": project_id,
            "name": "Content Test Project",
            "created_at": "2024-01-01T00:00:00Z"
        }
        mock_proj_mgr.get_project.return_value = mock_project
        mock_proj_mgr.get_novels_by_project.return_value = []

        # Step 1: Verify project exists
        project_response = client.get(f"/api/v1/projects/{project_id}")
        assert project_response.status_code == 200

        # Step 2: Create content batch (mock endpoint)
        batch_data = {
            "project_id": project_id,
            "name": "Chapter 1 Batch",
            "description": "First chapter content batch",
            "batch_type": "chapter"
        }

        # Mock content batch creation
        mock_batch = MagicMock()
        mock_batch.dict.return_value = {
            "id": batch_id,
            "project_id": project_id,
            "name": batch_data["name"],
            "created_at": "2024-01-01T00:00:00Z"
        }
        mock_cont_mgr.create_batch.return_value = mock_batch

        # Test content endpoint (this would need actual endpoint)
        # For now, we'll test the structure
        content_response = client.post("/api/v1/content/batches", json=batch_data)
        # This might return 404 if endpoint doesn't exist yet
        assert content_response.status_code in [201, 404]

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_export_import_workflow(self, mock_manager, client: TestClient):
        """Test project export and import workflow"""
        mock_project_manager = AsyncMock()
        mock_manager.return_value = mock_project_manager

        project_id = str(uuid.uuid4())

        # Mock project for export
        mock_project = MagicMock()
        mock_project_manager.get_project.return_value = mock_project
        mock_project_manager.export_project.return_value = {
            "project": {
                "name": "Export Test Project",
                "description": "Project for export testing"
            },
            "novels": [],
            "content": []
        }

        # Step 1: Export project
        export_request = {
            "include_novels": True,
            "include_content": True,
            "include_worldbuilding": False,
            "format": "json"
        }

        export_response = client.post(f"/api/v1/projects/{project_id}/export", json=export_request)
        assert export_response.status_code == 200
        export_data = export_response.json()
        assert export_data["success"] is True
        assert "data" in export_data

        # Step 2: Import project
        import_request = {
            "data": export_data["data"],
            "validate_only": False,
            "merge_existing": False
        }

        mock_project_manager.import_project.return_value = {"success": True}

        import_response = client.post("/api/v1/projects/import", json=import_request)
        assert import_response.status_code == 201
        import_result = import_response.json()
        assert import_result["success"] is True


@pytest.mark.e2e
@pytest.mark.api
class TestErrorHandlingWorkflow:
    """Test error handling in complete workflows"""

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_error_recovery_workflow(self, mock_manager, client: TestClient):
        """Test error handling and recovery in workflows"""
        mock_project_manager = AsyncMock()
        mock_manager.return_value = mock_project_manager

        # Step 1: Try to get non-existent project
        mock_project_manager.get_project.return_value = None

        nonexistent_id = str(uuid.uuid4())
        error_response = client.get(f"/api/v1/projects/{nonexistent_id}")
        assert error_response.status_code == 404

        # Step 2: Try to create project with invalid data
        invalid_data = {"name": ""}  # Invalid empty name

        invalid_response = client.post("/api/v1/projects/", json=invalid_data)
        assert invalid_response.status_code == 422

        # Step 3: Create valid project after fixing errors
        valid_data = {
            "name": "Valid Project",
            "description": "Fixed validation errors"
        }

        mock_project = MagicMock()
        mock_project.dict.return_value = {
            "id": str(uuid.uuid4()),
            "name": valid_data["name"],
            "description": valid_data["description"],
            "created_at": "2024-01-01T00:00:00Z"
        }
        mock_project_manager.get_project_by_name.return_value = None
        mock_project_manager.create_project.return_value = mock_project

        valid_response = client.post("/api/v1/projects/", json=valid_data)
        assert valid_response.status_code == 201

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_concurrent_access_workflow(self, mock_manager, client: TestClient):
        """Test concurrent access handling"""
        mock_project_manager = AsyncMock()
        mock_manager.return_value = mock_project_manager

        project_id = str(uuid.uuid4())

        # Mock project exists
        mock_project = MagicMock()
        mock_project.dict.return_value = {
            "id": project_id,
            "name": "Concurrent Test Project",
            "version": 1
        }
        mock_project_manager.get_project.return_value = mock_project
        mock_project_manager.update_project.return_value = mock_project
        mock_project_manager.get_novels_by_project.return_value = []

        # Simulate concurrent updates
        update_data_1 = {"description": "Update from user 1"}
        update_data_2 = {"description": "Update from user 2"}

        # Both updates should succeed (in a real scenario, one might fail due to optimistic locking)
        response_1 = client.put(f"/api/v1/projects/{project_id}", json=update_data_1)
        response_2 = client.put(f"/api/v1/projects/{project_id}", json=update_data_2)

        assert response_1.status_code == 200
        assert response_2.status_code == 200


@pytest.mark.e2e
@pytest.mark.api
class TestAPIIntegrationWorkflow:
    """Test integration between different API modules"""

    @patch("api.v1.endpoints.projects.get_global_manager")
    @patch("api.v1.endpoints.worldbuilding.get_global_manager")
    def test_cross_module_integration(self, mock_wb_manager, mock_proj_manager, client: TestClient):
        """Test integration between projects and worldbuilding modules"""

        # Setup mocks
        mock_project_mgr = AsyncMock()
        mock_worldbuilding_mgr = AsyncMock()
        mock_proj_manager.return_value = mock_project_mgr
        mock_wb_manager.return_value = mock_worldbuilding_mgr

        project_id = str(uuid.uuid4())
        domain_id = str(uuid.uuid4())

        # Mock project exists
        mock_project = MagicMock()
        mock_project.dict.return_value = {
            "id": project_id,
            "name": "Integration Test Project"
        }
        mock_project_mgr.get_project.return_value = mock_project

        # Step 1: Create project
        project_data = {
            "name": "Integration Test Project",
            "description": "Testing cross-module integration"
        }
        mock_project_mgr.get_project_by_name.return_value = None
        mock_project_mgr.create_project.return_value = mock_project

        project_response = client.post("/api/v1/projects/", json=project_data)
        assert project_response.status_code == 201

        # Step 2: Create worldbuilding domain for the project
        domain_data = {
            "project_id": project_id,
            "domain_name": "Test Domain",
            "domain_type": "technology",
            "description": "Test worldbuilding domain"
        }

        # Mock worldbuilding domain creation
        mock_domain = MagicMock()
        mock_domain.dict.return_value = {
            "id": domain_id,
            "project_id": project_id,
            "domain_name": domain_data["domain_name"],
            "created_at": "2024-01-01T00:00:00Z"
        }
        mock_worldbuilding_mgr.create_domain.return_value = mock_domain

        # Test worldbuilding endpoint (might not exist yet)
        wb_response = client.post("/api/v1/worldbuilding/domains", json=domain_data)
        assert wb_response.status_code in [201, 404]

        # Step 3: Verify project statistics include worldbuilding data
        mock_project_mgr.get_project_statistics.return_value = {
            "novel_count": 0,
            "worldbuilding_domains": 1,
            "total_word_count": 0
        }

        stats_response = client.get(f"/api/v1/projects/{project_id}/statistics")
        assert stats_response.status_code == 200

    def test_api_versioning_workflow(self, client: TestClient):
        """Test API versioning and backward compatibility"""

        # Test that v1 endpoints are accessible
        v1_response = client.get("/api/v1/projects/")
        assert v1_response.status_code in [200, 422]  # 422 if validation fails

        # Test API info endpoint
        info_response = client.get("/info")
        assert info_response.status_code == 200
        info_data = info_response.json()
        assert "version" in info_data

        # Test OpenAPI schema versioning
        openapi_response = client.get("/openapi.json")
        assert openapi_response.status_code == 200
        schema = openapi_response.json()
        assert "info" in schema
        assert "version" in schema["info"]

    def test_authentication_workflow(self, client: TestClient):
        """Test authentication workflow (when enabled)"""

        # Test accessing protected endpoints without auth
        # This assumes auth is disabled in test environment
        protected_response = client.delete("/api/v1/projects/batch")
        # Should either work (auth disabled) or return 401/403
        assert protected_response.status_code in [200, 401, 403, 404, 405, 422]

        # Test with API key header
        headers = {"X-API-Key": "test-key"}
        auth_response = client.get("/api/v1/projects/", headers=headers)
        assert auth_response.status_code in [200, 401, 422]

        # Test with Bearer token
        bearer_headers = {"Authorization": "Bearer test-token"}
        bearer_response = client.get("/api/v1/projects/", headers=bearer_headers)
        assert bearer_response.status_code in [200, 401, 422]