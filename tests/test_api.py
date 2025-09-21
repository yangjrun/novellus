#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Test Script
Basic tests to verify the FastAPI implementation
"""

import asyncio
import httpx
import json
from typing import Dict, Any

# API Base URL
BASE_URL = "http://localhost:8000"
API_V1_URL = f"{BASE_URL}/api/v1"


class APITester:
    """Simple API testing utility"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def test_endpoint(self, name: str, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Test a single endpoint"""
        try:
            response = await self.client.request(method, url, **kwargs)
            success = response.status_code < 400

            result = {
                "name": name,
                "method": method,
                "url": url,
                "status_code": response.status_code,
                "success": success,
                "response": response.json() if response.content else None
            }

            self.test_results.append(result)

            status_emoji = "✅" if success else "❌"
            print(f"{status_emoji} {name}: {response.status_code}")

            return result

        except Exception as e:
            result = {
                "name": name,
                "method": method,
                "url": url,
                "success": False,
                "error": str(e)
            }

            self.test_results.append(result)
            print(f"❌ {name}: {e}")

            return result

    async def run_tests(self):
        """Run all API tests"""
        print("=" * 60)
        print("🧪 Running API Tests")
        print("=" * 60)

        # Test root endpoints
        print("\n📌 Testing Root Endpoints:")
        await self.test_endpoint("Root", "GET", BASE_URL)
        await self.test_endpoint("Health Check", "GET", f"{BASE_URL}/health")
        await self.test_endpoint("Ready Check", "GET", f"{BASE_URL}/ready")
        await self.test_endpoint("API Info", "GET", f"{BASE_URL}/info")

        # Test admin endpoints
        print("\n📌 Testing Admin Endpoints:")
        await self.test_endpoint("Admin Health", "GET", f"{API_V1_URL}/admin/health")
        await self.test_endpoint("Database Status", "GET", f"{API_V1_URL}/admin/database/status")
        await self.test_endpoint("System Metrics", "GET", f"{API_V1_URL}/admin/metrics")

        # Test project endpoints
        print("\n📌 Testing Project Endpoints:")
        await self.test_endpoint("List Projects", "GET", f"{API_V1_URL}/projects")

        # Create a test project
        test_project = {
            "name": "test_project_api",
            "title": "Test Project from API",
            "description": "Created by API test script",
            "author": "API Tester",
            "genre": "Fantasy"
        }

        create_result = await self.test_endpoint(
            "Create Project",
            "POST",
            f"{API_V1_URL}/projects",
            json=test_project
        )

        if create_result.get("success") and create_result.get("response", {}).get("data"):
            project_id = create_result["response"]["data"].get("id")
            if project_id:
                # Test getting specific project
                await self.test_endpoint(
                    "Get Project",
                    "GET",
                    f"{API_V1_URL}/projects/{project_id}"
                )

        # Test novel endpoints
        print("\n📌 Testing Novel Endpoints:")
        await self.test_endpoint("List Novels", "GET", f"{API_V1_URL}/novels")

        # Test content endpoints
        print("\n📌 Testing Content Endpoints:")
        await self.test_endpoint(
            "List Batches",
            "GET",
            f"{API_V1_URL}/content/batches",
            params={"novel_id": "e1fd1aa4-bde2-4c76-8cee-334e54fa47d1"}  # Default novel ID
        )

        # Test search endpoints
        print("\n📌 Testing Search Endpoints:")
        await self.test_endpoint(
            "Search Content",
            "GET",
            f"{API_V1_URL}/search/content",
            params={
                "novel_id": "e1fd1aa4-bde2-4c76-8cee-334e54fa47d1",
                "query": "test"
            }
        )

        # Test conflict analysis endpoints
        print("\n📌 Testing Conflict Analysis Endpoints:")
        await self.test_endpoint(
            "Query Conflict Matrix",
            "GET",
            f"{API_V1_URL}/conflicts/matrix",
            params={"novel_id": "e1fd1aa4-bde2-4c76-8cee-334e54fa47d1"}
        )

        await self.test_endpoint(
            "Get Conflict Statistics",
            "GET",
            f"{API_V1_URL}/conflicts/statistics",
            params={"novel_id": "e1fd1aa4-bde2-4c76-8cee-334e54fa47d1"}
        )

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 Test Summary")
        print("=" * 60)

        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.get("success"))
        failed = total - passed

        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "N/A")

        if failed > 0:
            print("\n⚠️ Failed Tests:")
            for result in self.test_results:
                if not result.get("success"):
                    error_msg = result.get("error", f"HTTP {result.get('status_code', 'Unknown')}")
                    print(f"  - {result['name']}: {error_msg}")


async def main():
    """Main test runner"""
    print("🔧 Testing Novellus API")
    print(f"📍 Target: {BASE_URL}")
    print()

    tester = APITester()

    try:
        # Wait a moment for the server to be ready
        await asyncio.sleep(1)

        # Run tests
        await tester.run_tests()

    except httpx.ConnectError:
        print("❌ Error: Could not connect to API server")
        print(f"   Make sure the server is running at {BASE_URL}")
        print("   Run: python run_api.py")

    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())