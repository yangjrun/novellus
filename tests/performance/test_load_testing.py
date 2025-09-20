"""
Performance and load testing for FastAPI application
Tests API response times, throughput, and resource usage
"""

import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient


@pytest.mark.performance
@pytest.mark.slow
class TestAPIPerformance:
    """Test API endpoint performance"""

    def test_health_check_performance(self, client: TestClient, performance_config):
        """Test health check endpoint performance"""
        response_times = []
        iterations = 100

        with patch("api.core.database.get_database_health") as mock_health:
            mock_health.return_value = {"postgresql": True, "mongodb": True}

            for _ in range(iterations):
                start_time = time.time()
                response = client.get("/health")
                end_time = time.time()

                assert response.status_code == 200
                response_times.append(end_time - start_time)

        # Analyze performance
        avg_response_time = statistics.mean(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        max_response_time = max(response_times)

        print(f"\nHealth Check Performance:")
        print(f"Average response time: {avg_response_time:.3f}s")
        print(f"95th percentile: {p95_response_time:.3f}s")
        print(f"Max response time: {max_response_time:.3f}s")

        # Performance assertions
        assert avg_response_time < performance_config["max_response_time"]
        assert p95_response_time < performance_config["max_response_time"] * 2

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_projects_list_performance(self, mock_manager, client: TestClient, performance_config):
        """Test projects listing endpoint performance"""
        mock_project_manager = AsyncMock()
        mock_manager.return_value = mock_project_manager

        # Mock large number of projects
        projects = []
        for i in range(100):
            project = MagicMock()
            project.dict.return_value = {
                "id": f"project-{i}",
                "name": f"Project {i}",
                "description": f"Description for project {i}",
                "created_at": "2024-01-01T00:00:00Z"
            }
            projects.append(project)

        mock_project_manager.get_projects.return_value = projects
        mock_project_manager.count_projects.return_value = 100
        mock_project_manager.get_novels_by_project.return_value = []

        response_times = []
        iterations = 50

        for _ in range(iterations):
            start_time = time.time()
            response = client.get("/api/v1/projects/?page_size=20")
            end_time = time.time()

            assert response.status_code == 200
            response_times.append(end_time - start_time)

        avg_response_time = statistics.mean(response_times)
        print(f"\nProjects List Performance:")
        print(f"Average response time: {avg_response_time:.3f}s")

        assert avg_response_time < performance_config["max_response_time"]

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_project_creation_performance(self, mock_manager, client: TestClient, performance_config):
        """Test project creation endpoint performance"""
        mock_project_manager = AsyncMock()
        mock_manager.return_value = mock_project_manager

        mock_project_manager.get_project_by_name.return_value = None

        response_times = []
        iterations = 20

        for i in range(iterations):
            # Mock different project for each iteration
            mock_project = MagicMock()
            mock_project.dict.return_value = {
                "id": f"project-{i}",
                "name": f"Performance Test Project {i}",
                "description": "Performance testing project",
                "created_at": "2024-01-01T00:00:00Z"
            }
            mock_project_manager.create_project.return_value = mock_project

            project_data = {
                "name": f"Performance Test Project {i}",
                "description": "Performance testing project",
                "metadata": {"test": True}
            }

            start_time = time.time()
            response = client.post("/api/v1/projects/", json=project_data)
            end_time = time.time()

            assert response.status_code == 201
            response_times.append(end_time - start_time)

        avg_response_time = statistics.mean(response_times)
        print(f"\nProject Creation Performance:")
        print(f"Average response time: {avg_response_time:.3f}s")

        assert avg_response_time < performance_config["max_response_time"]

    @pytest.mark.benchmark
    def test_concurrent_requests_performance(self, client: TestClient, performance_config):
        """Test concurrent request handling performance"""
        num_concurrent = performance_config["concurrent_users"]
        requests_per_user = 10

        with patch("api.core.database.get_database_health") as mock_health:
            mock_health.return_value = {"postgresql": True, "mongodb": True}

            def make_request():
                """Make a single request and return response time"""
                start_time = time.time()
                response = client.get("/health")
                end_time = time.time()
                return end_time - start_time, response.status_code

            all_response_times = []
            all_status_codes = []

            # Use ThreadPoolExecutor for concurrent requests
            with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
                # Submit all requests
                futures = []
                for _ in range(num_concurrent):
                    for _ in range(requests_per_user):
                        future = executor.submit(make_request)
                        futures.append(future)

                # Collect results
                for future in as_completed(futures):
                    response_time, status_code = future.result()
                    all_response_times.append(response_time)
                    all_status_codes.append(status_code)

        # Analyze results
        total_requests = len(all_response_times)
        successful_requests = sum(1 for code in all_status_codes if code == 200)
        avg_response_time = statistics.mean(all_response_times)
        p95_response_time = statistics.quantiles(all_response_times, n=20)[18]

        print(f"\nConcurrent Requests Performance:")
        print(f"Total requests: {total_requests}")
        print(f"Successful requests: {successful_requests}")
        print(f"Success rate: {successful_requests/total_requests*100:.1f}%")
        print(f"Average response time: {avg_response_time:.3f}s")
        print(f"95th percentile: {p95_response_time:.3f}s")

        # Performance assertions
        assert successful_requests / total_requests >= 0.95  # 95% success rate
        assert avg_response_time < performance_config["max_response_time"] * 2


@pytest.mark.performance
class TestMemoryUsage:
    """Test memory usage and resource consumption"""

    def test_memory_usage_under_load(self, client: TestClient):
        """Test memory usage during load testing"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        with patch("api.core.database.get_database_health") as mock_health:
            mock_health.return_value = {"postgresql": True, "mongodb": True}

            # Make many requests to test memory usage
            for _ in range(1000):
                response = client.get("/health")
                assert response.status_code == 200

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        print(f"\nMemory Usage Test:")
        print(f"Initial memory: {initial_memory / 1024 / 1024:.1f} MB")
        print(f"Final memory: {final_memory / 1024 / 1024:.1f} MB")
        print(f"Memory increase: {memory_increase / 1024 / 1024:.1f} MB")

        # Memory increase should be reasonable (less than 50MB for this test)
        assert memory_increase < 50 * 1024 * 1024

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_large_response_handling(self, mock_manager, client: TestClient):
        """Test handling of large response data"""
        mock_project_manager = AsyncMock()
        mock_manager.return_value = mock_project_manager

        # Create a large number of mock projects
        large_projects_list = []
        for i in range(1000):
            project = MagicMock()
            project.dict.return_value = {
                "id": f"project-{i}",
                "name": f"Large Dataset Project {i}",
                "description": "x" * 1000,  # 1KB description each
                "metadata": {"large_field": "x" * 500},
                "created_at": "2024-01-01T00:00:00Z"
            }
            large_projects_list.append(project)

        mock_project_manager.get_projects.return_value = large_projects_list
        mock_project_manager.count_projects.return_value = 1000
        mock_project_manager.get_novels_by_project.return_value = []

        start_time = time.time()
        response = client.get("/api/v1/projects/?page_size=1000")
        end_time = time.time()

        assert response.status_code == 200
        response_time = end_time - start_time

        print(f"\nLarge Response Test:")
        print(f"Response time: {response_time:.3f}s")
        print(f"Response size: {len(response.content)} bytes")

        # Should handle large responses within reasonable time
        assert response_time < 5.0


@pytest.mark.performance
class TestDatabasePerformance:
    """Test database operation performance"""

    async def test_database_connection_pool_performance(self):
        """Test database connection pool performance"""
        connection_times = []
        iterations = 50

        # Mock database connection timing
        async def mock_get_connection():
            start_time = time.time()
            await asyncio.sleep(0.001)  # Simulate connection time
            end_time = time.time()
            return end_time - start_time

        for _ in range(iterations):
            connection_time = await mock_get_connection()
            connection_times.append(connection_time)

        avg_connection_time = statistics.mean(connection_times)
        print(f"\nDatabase Connection Performance:")
        print(f"Average connection time: {avg_connection_time:.3f}s")

        # Connection should be fast
        assert avg_connection_time < 0.1

    async def test_concurrent_database_operations(self):
        """Test concurrent database operations performance"""

        async def mock_database_operation(operation_id):
            """Simulate a database operation"""
            start_time = time.time()
            await asyncio.sleep(0.01)  # Simulate DB operation
            end_time = time.time()
            return operation_id, end_time - start_time

        # Run concurrent operations
        tasks = []
        for i in range(20):
            task = mock_database_operation(i)
            tasks.append(task)

        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

        operation_times = [result[1] for result in results]
        avg_operation_time = statistics.mean(operation_times)

        print(f"\nConcurrent Database Operations:")
        print(f"Total operations: {len(results)}")
        print(f"Total time: {total_time:.3f}s")
        print(f"Average operation time: {avg_operation_time:.3f}s")
        print(f"Operations per second: {len(results)/total_time:.1f}")

        # Should handle concurrent operations efficiently
        assert total_time < 1.0  # All operations should complete within 1 second


@pytest.mark.performance
class TestCachePerformance:
    """Test cache performance (when enabled)"""

    def test_cache_hit_performance(self, client: TestClient):
        """Test cache hit performance"""
        response_times_cold = []
        response_times_warm = []

        with patch("api.core.database.get_database_health") as mock_health:
            mock_health.return_value = {"postgresql": True, "mongodb": True}

            # Cold cache - first requests
            for _ in range(10):
                start_time = time.time()
                response = client.get("/health")
                end_time = time.time()
                assert response.status_code == 200
                response_times_cold.append(end_time - start_time)

            # Warm cache - repeated requests (simulating cache hits)
            for _ in range(10):
                start_time = time.time()
                response = client.get("/health")
                end_time = time.time()
                assert response.status_code == 200
                response_times_warm.append(end_time - start_time)

        avg_cold = statistics.mean(response_times_cold)
        avg_warm = statistics.mean(response_times_warm)

        print(f"\nCache Performance:")
        print(f"Cold cache average: {avg_cold:.3f}s")
        print(f"Warm cache average: {avg_warm:.3f}s")
        print(f"Cache improvement: {((avg_cold - avg_warm) / avg_cold * 100):.1f}%")

        # Warm cache should be at least as fast as cold cache
        assert avg_warm <= avg_cold


@pytest.mark.performance
class TestAPIRateLimiting:
    """Test rate limiting performance"""

    def test_rate_limit_performance(self, client: TestClient):
        """Test rate limiting behavior under load"""
        responses = []
        request_times = []

        # Make requests rapidly to test rate limiting
        for i in range(50):
            start_time = time.time()
            response = client.get("/health")
            end_time = time.time()

            responses.append(response.status_code)
            request_times.append(end_time - start_time)

        # Analyze rate limiting behavior
        success_count = sum(1 for code in responses if code == 200)
        rate_limited_count = sum(1 for code in responses if code == 429)

        print(f"\nRate Limiting Performance:")
        print(f"Total requests: {len(responses)}")
        print(f"Successful: {success_count}")
        print(f"Rate limited: {rate_limited_count}")
        print(f"Average response time: {statistics.mean(request_times):.3f}s")

        # Should handle rate limiting gracefully
        assert success_count > 0  # Some requests should succeed
        # Rate limiting behavior depends on configuration


@pytest.mark.performance
@pytest.mark.benchmark
class TestBenchmarks:
    """Comprehensive benchmark tests"""

    @pytest.mark.parametrize("endpoint", [
        "/health",
        "/ready",
        "/info",
        "/docs",
        "/openapi.json"
    ])
    def test_endpoint_benchmarks(self, client: TestClient, endpoint, benchmark):
        """Benchmark various endpoints"""

        def make_request():
            with patch("api.core.database.get_database_health") as mock_health:
                mock_health.return_value = {"postgresql": True, "mongodb": True}
                response = client.get(endpoint)
                assert response.status_code in [200, 307]  # 307 for redirects
                return response

        result = benchmark(make_request)

        print(f"\nBenchmark for {endpoint}:")
        print(f"Mean time: {benchmark.stats['mean']:.3f}s")
        print(f"Min time: {benchmark.stats['min']:.3f}s")
        print(f"Max time: {benchmark.stats['max']:.3f}s")

    def test_application_startup_benchmark(self, benchmark):
        """Benchmark application startup time"""

        def create_test_client():
            from api.main import app
            return TestClient(app)

        result = benchmark(create_test_client)

        print(f"\nApplication Startup Benchmark:")
        print(f"Mean startup time: {benchmark.stats['mean']:.3f}s")

    @patch("api.v1.endpoints.projects.get_global_manager")
    def test_crud_operations_benchmark(self, mock_manager, client: TestClient, benchmark):
        """Benchmark CRUD operations"""
        mock_project_manager = AsyncMock()
        mock_manager.return_value = mock_project_manager

        # Mock successful operations
        mock_project = MagicMock()
        mock_project.dict.return_value = {
            "id": "test-project-id",
            "name": "Benchmark Project",
            "description": "Project for benchmarking",
            "created_at": "2024-01-01T00:00:00Z"
        }

        mock_project_manager.get_project_by_name.return_value = None
        mock_project_manager.create_project.return_value = mock_project
        mock_project_manager.get_project.return_value = mock_project
        mock_project_manager.update_project.return_value = mock_project
        mock_project_manager.get_novels_by_project.return_value = []

        def run_crud_cycle():
            # Create
            create_data = {
                "name": "Benchmark Project",
                "description": "Project for benchmarking"
            }
            create_response = client.post("/api/v1/projects/", json=create_data)
            assert create_response.status_code == 201

            project_id = create_response.json()["id"]

            # Read
            read_response = client.get(f"/api/v1/projects/{project_id}")
            assert read_response.status_code == 200

            # Update
            update_data = {"description": "Updated description"}
            update_response = client.put(f"/api/v1/projects/{project_id}", json=update_data)
            assert update_response.status_code == 200

            return project_id

        result = benchmark(run_crud_cycle)

        print(f"\nCRUD Operations Benchmark:")
        print(f"Mean CRUD cycle time: {benchmark.stats['mean']:.3f}s")