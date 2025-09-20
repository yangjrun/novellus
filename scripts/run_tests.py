#!/usr/bin/env python3
"""
Novellus API Test Execution Script
Convenient script for running different types of tests locally
"""

import os
import sys
import time
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from tests.utils.test_runner import TestRunner, TestConfiguration


def setup_local_environment():
    """Setup local testing environment"""
    print("🔧 Setting up local test environment...")

    # Set environment variables
    os.environ.update({
        "ENVIRONMENT": "testing",
        "DEBUG": "True",
        "AUTH_ENABLED": "False",
        "CACHE_ENABLED": "False",
        "MONITORING_ENABLED": "False",
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "",
        "POSTGRES_DB": "test_novellus",
        "MONGODB_HOST": "localhost",
        "MONGODB_PORT": "27017",
        "MONGODB_DB": "test_novellus"
    })

    print("✅ Environment configured")


def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking dependencies...")

    required_commands = [
        ("python", "Python interpreter"),
        ("pip", "Python package manager"),
    ]

    optional_commands = [
        ("docker", "Docker (for containerized testing)"),
        ("docker-compose", "Docker Compose (for service orchestration)"),
        ("psql", "PostgreSQL client (for database testing)"),
        ("mongosh", "MongoDB shell (for database testing)"),
        ("locust", "Locust (for load testing)")
    ]

    missing_required = []
    missing_optional = []

    for cmd, description in required_commands:
        if subprocess.run(["which", cmd], capture_output=True).returncode != 0:
            missing_required.append(f"{cmd} - {description}")

    for cmd, description in optional_commands:
        if subprocess.run(["which", cmd], capture_output=True).returncode != 0:
            missing_optional.append(f"{cmd} - {description}")

    if missing_required:
        print("❌ Missing required dependencies:")
        for dep in missing_required:
            print(f"   - {dep}")
        return False

    if missing_optional:
        print("⚠️ Missing optional dependencies:")
        for dep in missing_optional:
            print(f"   - {dep}")

    print("✅ Dependencies checked")
    return True


def start_services():
    """Start required services for testing"""
    print("🚀 Starting services...")

    services_started = []

    # Check if services are already running
    if check_service("postgresql", "localhost", 5432):
        print("✅ PostgreSQL already running")
    else:
        print("⚠️ PostgreSQL not detected - please start manually or use Docker")

    if check_service("mongodb", "localhost", 27017):
        print("✅ MongoDB already running")
    else:
        print("⚠️ MongoDB not detected - please start manually or use Docker")

    return services_started


def check_service(service_name: str, host: str, port: int) -> bool:
    """Check if a service is running"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result == 0
    except Exception:
        return False


def run_quick_tests():
    """Run quick test suite for rapid feedback"""
    print("⚡ Running quick test suite...")

    config = TestConfiguration(
        test_types=["unit"],
        test_paths=[],
        markers=["not slow"],
        parallel=True,
        workers=4,
        coverage=False,
        html_report=False,
        junit_xml=False,
        timeout=60,
        environment="development",
        database_reset=False,
        performance_baseline=False
    )

    runner = TestRunner(config)
    results = runner.run_unit_tests()

    print(f"✅ Quick tests completed: {'PASSED' if results.get('success') else 'FAILED'}")
    return results.get('success', False)


def run_comprehensive_tests():
    """Run comprehensive test suite"""
    print("🔬 Running comprehensive test suite...")

    config = TestConfiguration(
        test_types=["unit", "integration", "e2e"],
        test_paths=[],
        markers=[],
        parallel=True,
        workers=4,
        coverage=True,
        html_report=True,
        junit_xml=True,
        timeout=300,
        environment="development",
        database_reset=True,
        performance_baseline=False
    )

    runner = TestRunner(config)
    results = runner.run_all_tests()

    print(f"✅ Comprehensive tests completed: {'PASSED' if results.get('overall_success') else 'FAILED'}")
    return results.get('overall_success', False)


def run_performance_tests():
    """Run performance and load tests"""
    print("🚀 Running performance tests...")

    # Check if API server is running
    if not check_service("api", "localhost", 8000):
        print("Starting API server for performance testing...")
        api_process = start_api_server()
        if not api_process:
            print("❌ Failed to start API server")
            return False
        time.sleep(5)  # Wait for server to start
    else:
        api_process = None

    try:
        config = TestConfiguration(
            test_types=["performance"],
            test_paths=[],
            markers=[],
            parallel=False,
            workers=1,
            coverage=False,
            html_report=True,
            junit_xml=True,
            timeout=600,
            environment="development",
            database_reset=False,
            performance_baseline=True
        )

        runner = TestRunner(config)
        results = runner.run_performance_tests()

        # Also run load tests
        load_results = runner.run_load_tests()

        success = results.get('success', False) and load_results.get('status') == 'completed'
        print(f"✅ Performance tests completed: {'PASSED' if success else 'FAILED'}")
        return success

    finally:
        if api_process:
            print("Stopping API server...")
            api_process.terminate()
            api_process.wait()


def start_api_server():
    """Start the API server for testing"""
    try:
        api_main = project_root / "src" / "api" / "main.py"
        if api_main.exists():
            return subprocess.Popen([
                sys.executable, str(api_main)
            ], cwd=str(project_root))
    except Exception as e:
        print(f"Failed to start API server: {e}")
    return None


def run_security_tests():
    """Run security tests and scans"""
    print("🔒 Running security tests...")

    commands = [
        {
            "name": "Bandit Security Scan",
            "cmd": ["bandit", "-r", "src/", "-f", "txt"],
            "required": False
        },
        {
            "name": "Safety Vulnerability Check",
            "cmd": ["safety", "check"],
            "required": False
        },
        {
            "name": "Pip Audit",
            "cmd": ["pip-audit"],
            "required": False
        }
    ]

    all_passed = True

    for test in commands:
        print(f"Running {test['name']}...")
        try:
            result = subprocess.run(test['cmd'], capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print(f"✅ {test['name']} passed")
            else:
                print(f"⚠️ {test['name']} found issues:")
                print(result.stdout)
                if test['required']:
                    all_passed = False
        except FileNotFoundError:
            print(f"⚠️ {test['name']} tool not installed - skipping")
        except subprocess.TimeoutExpired:
            print(f"⚠️ {test['name']} timed out")
            if test['required']:
                all_passed = False

    return all_passed


def run_docker_tests():
    """Run tests in Docker environment"""
    print("🐳 Running tests in Docker...")

    # Check if Docker is available
    if subprocess.run(["which", "docker"], capture_output=True).returncode != 0:
        print("❌ Docker not available")
        return False

    # Build test image
    print("Building test Docker image...")
    build_cmd = [
        "docker", "build",
        "-f", "Dockerfile.test",
        "-t", "novellus-test",
        "."
    ]

    try:
        subprocess.run(build_cmd, check=True, cwd=project_root)
        print("✅ Test image built successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to build test image")
        return False

    # Run tests in container
    print("Running tests in container...")
    run_cmd = [
        "docker", "run",
        "--rm",
        "-v", f"{project_root}/reports:/app/reports",
        "novellus-test"
    ]

    try:
        result = subprocess.run(run_cmd, check=True, cwd=project_root)
        print("✅ Docker tests completed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Docker tests failed")
        return False


def cleanup_test_environment():
    """Clean up test environment"""
    print("🧹 Cleaning up test environment...")

    # Clean up test databases
    cleanup_commands = [
        ["docker", "stop", "test-postgres", "test-mongodb"],
        ["docker", "rm", "test-postgres", "test-mongodb"]
    ]

    for cmd in cleanup_commands:
        try:
            subprocess.run(cmd, capture_output=True, check=False)
        except Exception:
            pass

    print("✅ Cleanup completed")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Novellus API Test Runner")

    parser.add_argument(
        "command",
        choices=["quick", "full", "performance", "security", "docker", "all"],
        help="Type of tests to run"
    )

    parser.add_argument(
        "--setup",
        action="store_true",
        help="Setup test environment before running"
    )

    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Cleanup test environment after running"
    )

    parser.add_argument(
        "--no-deps-check",
        action="store_true",
        help="Skip dependency checking"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    print("🧪 Novellus API Test Runner")
    print("=" * 50)

    # Check dependencies unless skipped
    if not args.no_deps_check:
        if not check_dependencies():
            print("❌ Dependency check failed")
            return 1

    # Setup environment if requested
    if args.setup:
        setup_local_environment()
        start_services()

    success = True

    try:
        # Run specified tests
        if args.command == "quick":
            success = run_quick_tests()

        elif args.command == "full":
            success = run_comprehensive_tests()

        elif args.command == "performance":
            success = run_performance_tests()

        elif args.command == "security":
            success = run_security_tests()

        elif args.command == "docker":
            success = run_docker_tests()

        elif args.command == "all":
            print("Running all test types...")
            results = []
            results.append(run_quick_tests())
            results.append(run_comprehensive_tests())
            results.append(run_performance_tests())
            results.append(run_security_tests())
            success = all(results)

    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        success = False

    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        success = False

    finally:
        # Cleanup if requested
        if args.cleanup:
            cleanup_test_environment()

    # Summary
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests completed successfully!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())