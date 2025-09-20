"""
Test runner utility for orchestrating test execution
Manages test discovery, execution, and reporting
"""

import os
import sys
import time
import asyncio
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
import pytest
import json


@dataclass
class TestConfiguration:
    """Test execution configuration"""
    test_types: List[str]  # unit, integration, e2e, performance
    test_paths: List[str]
    markers: List[str]  # pytest markers to include/exclude
    parallel: bool
    workers: int
    coverage: bool
    html_report: bool
    junit_xml: bool
    timeout: int  # seconds
    environment: str  # development, staging, production
    database_reset: bool
    performance_baseline: bool


class TestRunner:
    """Orchestrates test execution and reporting"""

    def __init__(self, config: TestConfiguration):
        self.config = config
        self.project_root = Path(__file__).parent.parent.parent
        self.test_root = self.project_root / "tests"
        self.reports_dir = self.project_root / "reports"
        self.reports_dir.mkdir(exist_ok=True)

    def discover_tests(self) -> Dict[str, List[str]]:
        """Discover tests by category"""
        test_files = {}

        for test_type in self.config.test_types:
            test_dir = self.test_root / test_type
            if test_dir.exists():
                files = list(test_dir.glob("test_*.py"))
                test_files[test_type] = [str(f) for f in files]
            else:
                test_files[test_type] = []

        return test_files

    def prepare_environment(self):
        """Prepare test environment"""
        print("🔧 Preparing test environment...")

        # Set environment variables
        os.environ.update({
            "ENVIRONMENT": "testing",
            "DEBUG": "True",
            "AUTH_ENABLED": "False",
            "CACHE_ENABLED": "False",
            "MONITORING_ENABLED": "False"
        })

        # Database setup
        if self.config.database_reset:
            self._reset_test_databases()

        # Install dependencies if needed
        self._ensure_dependencies()

        print("✅ Environment prepared")

    def _reset_test_databases(self):
        """Reset test databases"""
        print("🗄️ Resetting test databases...")

        # PostgreSQL test database reset
        try:
            subprocess.run([
                "psql", "-h", "localhost", "-U", "postgres",
                "-c", "DROP DATABASE IF EXISTS test_novellus;"
            ], check=True, capture_output=True)

            subprocess.run([
                "psql", "-h", "localhost", "-U", "postgres",
                "-c", "CREATE DATABASE test_novellus;"
            ], check=True, capture_output=True)

            print("✅ PostgreSQL test database reset")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ PostgreSQL reset failed: {e}")

        # MongoDB test database reset
        try:
            subprocess.run([
                "mongosh", "--eval", "use test_novellus; db.dropDatabase();"
            ], check=True, capture_output=True)

            print("✅ MongoDB test database reset")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ MongoDB reset failed: {e}")

    def _ensure_dependencies(self):
        """Ensure all test dependencies are installed"""
        requirements_file = self.project_root / "pyproject.toml"
        if requirements_file.exists():
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-e", ".[test,dev]"
                ], check=True, capture_output=True)
                print("✅ Dependencies verified")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Dependency installation failed: {e}")

    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests"""
        print("🧪 Running unit tests...")

        pytest_args = [
            "-v",
            "--tb=short",
            "-m", "unit",
            str(self.test_root / "unit")
        ]

        if self.config.coverage:
            pytest_args.extend(["--cov=src", "--cov-report=xml", "--cov-report=html"])

        if self.config.parallel and self.config.workers > 1:
            pytest_args.extend(["-n", str(self.config.workers)])

        if self.config.junit_xml:
            pytest_args.extend(["--junitxml", str(self.reports_dir / "unit_tests.xml")])

        return self._run_pytest(pytest_args, "unit")

    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests"""
        print("🔗 Running integration tests...")

        pytest_args = [
            "-v",
            "--tb=short",
            "-m", "integration",
            str(self.test_root / "integration")
        ]

        if self.config.junit_xml:
            pytest_args.extend(["--junitxml", str(self.reports_dir / "integration_tests.xml")])

        # Integration tests typically don't run in parallel due to shared resources
        return self._run_pytest(pytest_args, "integration")

    def run_e2e_tests(self) -> Dict[str, Any]:
        """Run end-to-end tests"""
        print("🎭 Running end-to-end tests...")

        pytest_args = [
            "-v",
            "--tb=short",
            "-m", "e2e",
            str(self.test_root / "e2e")
        ]

        if self.config.junit_xml:
            pytest_args.extend(["--junitxml", str(self.reports_dir / "e2e_tests.xml")])

        return self._run_pytest(pytest_args, "e2e")

    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests"""
        print("🚀 Running performance tests...")

        pytest_args = [
            "-v",
            "--tb=short",
            "-m", "performance",
            str(self.test_root / "performance"),
            "--benchmark-json", str(self.reports_dir / "benchmark.json")
        ]

        if self.config.junit_xml:
            pytest_args.extend(["--junitxml", str(self.reports_dir / "performance_tests.xml")])

        return self._run_pytest(pytest_args, "performance")

    def run_load_tests(self) -> Dict[str, Any]:
        """Run load tests with Locust"""
        print("📈 Running load tests...")

        locust_file = self.test_root / "performance" / "locustfile.py"
        if not locust_file.exists():
            return {"status": "skipped", "reason": "No locustfile.py found"}

        # Start API server for load testing
        server_process = self._start_api_server()
        time.sleep(5)  # Wait for server to start

        try:
            # Run Locust tests
            cmd = [
                "locust",
                "-f", str(locust_file),
                "--host", "http://localhost:8000",
                "--users", "10",
                "--spawn-rate", "2",
                "--run-time", "2m",
                "--headless",
                "--html", str(self.reports_dir / "load_test_report.html"),
                "--csv", str(self.reports_dir / "load_test")
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            return {
                "status": "completed",
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "reports": [
                    str(self.reports_dir / "load_test_report.html"),
                    str(self.reports_dir / "load_test_stats.csv"),
                    str(self.reports_dir / "load_test_failures.csv")
                ]
            }

        except subprocess.TimeoutExpired:
            return {"status": "timeout", "reason": "Load test timed out"}

        finally:
            # Stop API server
            if server_process:
                server_process.terminate()
                server_process.wait()

    def _start_api_server(self) -> Optional[subprocess.Popen]:
        """Start API server for testing"""
        try:
            api_main = self.project_root / "src" / "api" / "main.py"
            if api_main.exists():
                return subprocess.Popen([
                    sys.executable, str(api_main)
                ], cwd=str(self.project_root))
        except Exception as e:
            print(f"⚠️ Failed to start API server: {e}")
        return None

    def _run_pytest(self, args: List[str], test_type: str) -> Dict[str, Any]:
        """Run pytest with given arguments"""
        start_time = time.time()

        try:
            # Run pytest programmatically
            exit_code = pytest.main(args)
            duration = time.time() - start_time

            return {
                "status": "completed",
                "test_type": test_type,
                "exit_code": exit_code,
                "duration": duration,
                "success": exit_code == 0
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                "status": "error",
                "test_type": test_type,
                "error": str(e),
                "duration": duration,
                "success": False
            }

    def run_security_tests(self) -> Dict[str, Any]:
        """Run security tests"""
        print("🔒 Running security tests...")

        security_results = {}

        # Static security analysis with bandit
        try:
            cmd = ["bandit", "-r", "src/", "-f", "json", "-o", str(self.reports_dir / "bandit.json")]
            result = subprocess.run(cmd, capture_output=True, text=True)
            security_results["bandit"] = {
                "exit_code": result.returncode,
                "report_file": str(self.reports_dir / "bandit.json")
            }
        except FileNotFoundError:
            security_results["bandit"] = {"status": "skipped", "reason": "bandit not installed"}

        # Dependency vulnerability check with safety
        try:
            cmd = ["safety", "check", "--json", "--output", str(self.reports_dir / "safety.json")]
            result = subprocess.run(cmd, capture_output=True, text=True)
            security_results["safety"] = {
                "exit_code": result.returncode,
                "report_file": str(self.reports_dir / "safety.json")
            }
        except FileNotFoundError:
            security_results["safety"] = {"status": "skipped", "reason": "safety not installed"}

        return security_results

    def generate_comprehensive_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive test report"""
        from .test_reporter import TestReporter, TestSuiteResult, TestResult, TestCategory, TestStatus

        reporter = TestReporter(str(self.reports_dir))

        # Convert results to TestReporter format
        for test_type, result in results.items():
            if result.get("status") == "completed" and result.get("success"):
                # Create mock test suite result
                suite = TestSuiteResult(
                    name=f"{test_type}_tests",
                    total_tests=result.get("test_count", 0),
                    passed=result.get("passed", 0),
                    failed=result.get("failed", 0),
                    skipped=result.get("skipped", 0),
                    errors=result.get("errors", 0),
                    total_duration=result.get("duration", 0),
                    start_time=datetime.now(timezone.utc),
                    end_time=datetime.now(timezone.utc),
                    tests=[]
                )
                reporter.add_test_suite_result(suite)

        # Generate and save reports
        report_paths = reporter.save_reports()
        return report_paths["latest_html"]

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all configured test types"""
        print("🚀 Starting comprehensive test suite...")
        print(f"Configuration: {self.config}")

        self.prepare_environment()

        results = {}
        overall_start_time = time.time()

        # Run different test types based on configuration
        if "unit" in self.config.test_types:
            results["unit"] = self.run_unit_tests()

        if "integration" in self.config.test_types:
            results["integration"] = self.run_integration_tests()

        if "e2e" in self.config.test_types:
            results["e2e"] = self.run_e2e_tests()

        if "performance" in self.config.test_types:
            results["performance"] = self.run_performance_tests()
            results["load_tests"] = self.run_load_tests()

        # Always run security tests
        results["security"] = self.run_security_tests()

        overall_duration = time.time() - overall_start_time

        # Generate comprehensive report
        report_path = self.generate_comprehensive_report(results)

        # Summary
        total_success = all(r.get("success", True) for r in results.values() if "success" in r)

        summary = {
            "overall_success": total_success,
            "total_duration": overall_duration,
            "results": results,
            "report_path": report_path,
            "reports_directory": str(self.reports_dir)
        }

        print(f"\n{'✅' if total_success else '❌'} Test suite completed in {overall_duration:.2f}s")
        print(f"📊 Report available at: {report_path}")

        return summary


def create_test_config_from_args(args) -> TestConfiguration:
    """Create test configuration from command line arguments"""
    return TestConfiguration(
        test_types=args.test_types,
        test_paths=args.test_paths or [],
        markers=args.markers or [],
        parallel=args.parallel,
        workers=args.workers,
        coverage=args.coverage,
        html_report=args.html_report,
        junit_xml=args.junit_xml,
        timeout=args.timeout,
        environment=args.environment,
        database_reset=args.database_reset,
        performance_baseline=args.performance_baseline
    )


def main():
    """Main CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Novellus API Test Runner")

    parser.add_argument(
        "--test-types",
        nargs="+",
        choices=["unit", "integration", "e2e", "performance", "all"],
        default=["unit"],
        help="Types of tests to run"
    )

    parser.add_argument(
        "--test-paths",
        nargs="+",
        help="Specific test paths to run"
    )

    parser.add_argument(
        "--markers",
        nargs="+",
        help="Pytest markers to include"
    )

    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel"
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of parallel workers"
    )

    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )

    parser.add_argument(
        "--html-report",
        action="store_true",
        default=True,
        help="Generate HTML report"
    )

    parser.add_argument(
        "--junit-xml",
        action="store_true",
        help="Generate JUnit XML reports"
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Test timeout in seconds"
    )

    parser.add_argument(
        "--environment",
        choices=["development", "staging", "production"],
        default="development",
        help="Test environment"
    )

    parser.add_argument(
        "--database-reset",
        action="store_true",
        help="Reset test databases before running"
    )

    parser.add_argument(
        "--performance-baseline",
        action="store_true",
        help="Establish performance baseline"
    )

    args = parser.parse_args()

    # Handle "all" test types
    if "all" in args.test_types:
        args.test_types = ["unit", "integration", "e2e", "performance"]

    # Create configuration
    config = create_test_config_from_args(args)

    # Run tests
    runner = TestRunner(config)
    results = runner.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if results["overall_success"] else 1)


if __name__ == "__main__":
    main()