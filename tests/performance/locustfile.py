"""
Locust load testing configuration
Defines user behavior and load testing scenarios for the FastAPI application
"""

import json
import random
from locust import HttpUser, task, between
from uuid import uuid4


class APIUser(HttpUser):
    """Base API user for load testing"""

    wait_time = between(1, 3)  # Wait 1-3 seconds between requests

    def on_start(self):
        """Called when a user starts"""
        self.project_ids = []
        self.novel_ids = []

        # Health check to ensure API is ready
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")

    @task(10)
    def health_check(self):
        """Health check endpoint - high frequency"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")

    @task(5)
    def get_api_info(self):
        """Get API information"""
        with self.client.get("/info", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"API info failed: {response.status_code}")

    @task(8)
    def list_projects(self):
        """List projects with various parameters"""
        params = {
            "page": random.randint(1, 3),
            "page_size": random.choice([10, 20, 50])
        }

        # Randomly add filters
        if random.random() < 0.3:
            params["genre"] = random.choice(["fantasy", "sci-fi", "mystery"])
        if random.random() < 0.2:
            params["status_filter"] = random.choice(["active", "paused", "completed"])

        with self.client.get("/api/v1/projects/", params=params, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
                # Store project IDs for later use
                data = response.json()
                if data.get("projects"):
                    for project in data["projects"][:3]:  # Store up to 3 project IDs
                        if project["id"] not in self.project_ids:
                            self.project_ids.append(project["id"])
            else:
                response.failure(f"List projects failed: {response.status_code}")

    @task(3)
    def create_project(self):
        """Create a new project"""
        project_data = {
            "name": f"Load Test Project {uuid4().hex[:8]}",
            "description": f"Project created during load test at {random.randint(1000, 9999)}",
            "author": random.choice(["Test Author", "Load Tester", "Performance User"]),
            "genre": random.choice(["fantasy", "sci-fi", "mystery", "romance", "thriller"]),
            "metadata": {
                "target_audience": random.choice(["adult", "young_adult", "children"]),
                "estimated_length": random.randint(50000, 150000),
                "test_project": True
            }
        }

        with self.client.post(
            "/api/v1/projects/",
            json=project_data,
            catch_response=True
        ) as response:
            if response.status_code == 201:
                response.success()
                project_id = response.json().get("id")
                if project_id:
                    self.project_ids.append(project_id)
            elif response.status_code == 409:  # Conflict - duplicate name
                response.success()  # This is expected sometimes
            else:
                response.failure(f"Create project failed: {response.status_code}")

    @task(6)
    def get_project_details(self):
        """Get details of a specific project"""
        if not self.project_ids:
            return

        project_id = random.choice(self.project_ids)
        params = {
            "include_novels": random.choice([True, False]),
            "include_stats": random.choice([True, False])
        }

        with self.client.get(
            f"/api/v1/projects/{project_id}",
            params=params,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                # Project might have been deleted
                self.project_ids.remove(project_id)
                response.success()
            else:
                response.failure(f"Get project details failed: {response.status_code}")

    @task(2)
    def update_project(self):
        """Update an existing project"""
        if not self.project_ids:
            return

        project_id = random.choice(self.project_ids)
        update_data = {
            "description": f"Updated during load test at {random.randint(1000, 9999)}",
            "metadata": {
                "last_updated": "load_test",
                "update_count": random.randint(1, 10)
            }
        }

        with self.client.put(
            f"/api/v1/projects/{project_id}",
            json=update_data,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                # Project might have been deleted
                self.project_ids.remove(project_id)
                response.success()
            else:
                response.failure(f"Update project failed: {response.status_code}")

    @task(4)
    def get_project_statistics(self):
        """Get project statistics"""
        if not self.project_ids:
            return

        project_id = random.choice(self.project_ids)

        with self.client.get(
            f"/api/v1/projects/{project_id}/statistics",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                self.project_ids.remove(project_id)
                response.success()
            else:
                response.failure(f"Get project statistics failed: {response.status_code}")

    @task(1)
    def batch_create_projects(self):
        """Create multiple projects in batch"""
        batch_size = random.randint(2, 5)
        projects = []

        for i in range(batch_size):
            projects.append({
                "name": f"Batch Project {uuid4().hex[:8]}",
                "description": f"Batch created project {i+1}",
                "author": "Batch Creator",
                "genre": random.choice(["fantasy", "sci-fi", "mystery"])
            })

        batch_data = {"projects": projects}

        with self.client.post(
            "/api/v1/projects/batch",
            json=batch_data,
            catch_response=True
        ) as response:
            if response.status_code == 201:
                response.success()
            else:
                response.failure(f"Batch create failed: {response.status_code}")

    @task(1)
    def export_project(self):
        """Export a project"""
        if not self.project_ids:
            return

        project_id = random.choice(self.project_ids)
        export_data = {
            "include_novels": random.choice([True, False]),
            "include_content": random.choice([True, False]),
            "include_worldbuilding": random.choice([True, False]),
            "format": random.choice(["json", "yaml"])
        }

        with self.client.post(
            f"/api/v1/projects/{project_id}/export",
            json=export_data,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                self.project_ids.remove(project_id)
                response.success()
            else:
                response.failure(f"Export project failed: {response.status_code}")


class HeavyAPIUser(APIUser):
    """Heavy API user that performs more intensive operations"""

    wait_time = between(2, 5)
    weight = 2  # This user type will be chosen less frequently

    @task(3)
    def stress_list_projects(self):
        """Stress test project listing with large page sizes"""
        params = {
            "page": 1,
            "page_size": 100,  # Large page size
            "sort_by": "created_at",
            "sort_order": "desc"
        }

        with self.client.get("/api/v1/projects/", params=params, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Heavy list projects failed: {response.status_code}")

    @task(2)
    def create_large_project(self):
        """Create project with large metadata"""
        large_metadata = {
            "description": "x" * 1000,  # 1KB description
            "notes": "x" * 500,
            "tags": [f"tag_{i}" for i in range(20)],
            "large_field": "x" * 2000,  # 2KB field
            "test_project": True
        }

        project_data = {
            "name": f"Large Load Test Project {uuid4().hex[:8]}",
            "description": "Large project for stress testing",
            "author": "Heavy Load Tester",
            "genre": "epic_fantasy",
            "metadata": large_metadata
        }

        with self.client.post(
            "/api/v1/projects/",
            json=project_data,
            catch_response=True
        ) as response:
            if response.status_code == 201:
                response.success()
                project_id = response.json().get("id")
                if project_id:
                    self.project_ids.append(project_id)
            elif response.status_code == 409:
                response.success()
            else:
                response.failure(f"Create large project failed: {response.status_code}")


class ReadOnlyUser(HttpUser):
    """Read-only user that only performs GET operations"""

    wait_time = between(0.5, 2)
    weight = 3  # This user type will be chosen more frequently

    def on_start(self):
        """Initialize read-only user"""
        # Health check
        self.client.get("/health")

    @task(15)
    def health_check(self):
        """Frequent health checks"""
        self.client.get("/health")

    @task(10)
    def list_projects(self):
        """List projects with random pagination"""
        params = {
            "page": random.randint(1, 5),
            "page_size": random.choice([10, 20])
        }
        self.client.get("/api/v1/projects/", params=params)

    @task(5)
    def get_api_info(self):
        """Get API information"""
        self.client.get("/info")

    @task(3)
    def get_openapi_schema(self):
        """Get OpenAPI schema"""
        self.client.get("/openapi.json")

    @task(2)
    def access_documentation(self):
        """Access API documentation"""
        self.client.get("/docs")


class BurstUser(HttpUser):
    """User that creates burst traffic"""

    wait_time = between(10, 20)  # Long wait between bursts

    @task
    def burst_requests(self):
        """Create a burst of requests"""
        # Create a burst of 10-20 requests quickly
        burst_size = random.randint(10, 20)

        for _ in range(burst_size):
            endpoint = random.choice([
                "/health",
                "/info",
                "/api/v1/projects/"
            ])
            self.client.get(endpoint)


# Custom load testing shapes
class StepLoadShape:
    """Custom load shape that increases users in steps"""

    def tick(self):
        run_time = self.get_run_time()

        if run_time < 60:
            return (10, 1)  # 10 users, 1 spawn rate
        elif run_time < 120:
            return (20, 2)  # 20 users, 2 spawn rate
        elif run_time < 180:
            return (30, 3)  # 30 users, 3 spawn rate
        elif run_time < 240:
            return (40, 4)  # 40 users, 4 spawn rate
        else:
            return None  # Stop the test


class SpikeLoadShape:
    """Custom load shape that creates traffic spikes"""

    def tick(self):
        run_time = self.get_run_time()

        # Create spikes every 60 seconds
        if run_time % 60 < 10:
            return (50, 5)  # Spike: 50 users
        else:
            return (10, 1)  # Normal: 10 users


# Environment-specific configurations
def get_load_test_config():
    """Get load test configuration based on environment"""
    import os

    env = os.getenv("LOAD_TEST_ENV", "development")

    configs = {
        "development": {
            "users": 10,
            "spawn_rate": 2,
            "duration": "5m"
        },
        "staging": {
            "users": 50,
            "spawn_rate": 5,
            "duration": "10m"
        },
        "production": {
            "users": 100,
            "spawn_rate": 10,
            "duration": "30m"
        }
    }

    return configs.get(env, configs["development"])


# Usage examples:
"""
# Run basic load test
locust -f locustfile.py --host=http://localhost:8000

# Run with specific user count and spawn rate
locust -f locustfile.py --host=http://localhost:8000 -u 20 -r 2 -t 5m

# Run headless (no web UI)
locust -f locustfile.py --host=http://localhost:8000 -u 20 -r 2 -t 5m --headless

# Run with custom user classes
locust -f locustfile.py --host=http://localhost:8000 APIUser ReadOnlyUser

# Run with HTML report
locust -f locustfile.py --host=http://localhost:8000 -u 20 -r 2 -t 5m --headless --html report.html
"""