"""
Test reporting and analysis utilities
Generates comprehensive test reports and performance analysis
"""

import json
import os
import time
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class TestStatus(Enum):
    """Test execution status"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class TestCategory(Enum):
    """Test category classification"""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PERFORMANCE = "performance"
    SECURITY = "security"
    API = "api"


@dataclass
class TestResult:
    """Individual test result data"""
    name: str
    category: TestCategory
    status: TestStatus
    duration: float
    file_path: str
    line_number: int
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    setup_time: Optional[float] = None
    teardown_time: Optional[float] = None
    memory_usage: Optional[int] = None
    parameters: Optional[Dict[str, Any]] = None


@dataclass
class TestSuiteResult:
    """Test suite execution results"""
    name: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    total_duration: float
    start_time: datetime
    end_time: datetime
    tests: List[TestResult]
    coverage_percentage: Optional[float] = None
    environment: Optional[Dict[str, str]] = None


@dataclass
class PerformanceMetrics:
    """Performance test metrics"""
    endpoint: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    min_response_time: float
    max_response_time: float
    p50_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None


class TestReporter:
    """Comprehensive test reporting and analysis"""

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results: List[TestSuiteResult] = []
        self.performance_metrics: List[PerformanceMetrics] = []

    def add_test_suite_result(self, result: TestSuiteResult):
        """Add test suite result to the report"""
        self.results.append(result)

    def add_performance_metrics(self, metrics: PerformanceMetrics):
        """Add performance metrics to the report"""
        self.performance_metrics.append(metrics)

    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate comprehensive test summary report"""
        if not self.results:
            return {"error": "No test results available"}

        total_tests = sum(suite.total_tests for suite in self.results)
        total_passed = sum(suite.passed for suite in self.results)
        total_failed = sum(suite.failed for suite in self.results)
        total_skipped = sum(suite.skipped for suite in self.results)
        total_errors = sum(suite.errors for suite in self.results)
        total_duration = sum(suite.total_duration for suite in self.results)

        # Calculate success rate
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

        # Category breakdown
        category_stats = {}
        for suite in self.results:
            for test in suite.tests:
                category = test.category.value
                if category not in category_stats:
                    category_stats[category] = {
                        "total": 0, "passed": 0, "failed": 0, "skipped": 0, "errors": 0
                    }
                category_stats[category]["total"] += 1
                category_stats[category][test.status.value] += 1

        # Performance summary
        performance_summary = {}
        if self.performance_metrics:
            all_response_times = []
            total_requests = 0
            successful_requests = 0

            for metric in self.performance_metrics:
                all_response_times.extend([metric.average_response_time])
                total_requests += metric.total_requests
                successful_requests += metric.successful_requests

            performance_summary = {
                "total_performance_tests": len(self.performance_metrics),
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "overall_success_rate": (successful_requests / total_requests * 100) if total_requests > 0 else 0,
                "average_response_time": statistics.mean(all_response_times) if all_response_times else 0
            }

        # Test execution timeline
        if self.results:
            start_time = min(suite.start_time for suite in self.results)
            end_time = max(suite.end_time for suite in self.results)
            execution_time = (end_time - start_time).total_seconds()
        else:
            execution_time = 0

        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_test_suites": len(self.results),
                "total_tests": total_tests,
                "passed": total_passed,
                "failed": total_failed,
                "skipped": total_skipped,
                "errors": total_errors,
                "success_rate_percent": round(success_rate, 2),
                "total_duration_seconds": round(total_duration, 2),
                "execution_time_seconds": round(execution_time, 2)
            },
            "category_breakdown": category_stats,
            "performance_summary": performance_summary,
            "test_suites": [
                {
                    "name": suite.name,
                    "total": suite.total_tests,
                    "passed": suite.passed,
                    "failed": suite.failed,
                    "skipped": suite.skipped,
                    "duration": round(suite.total_duration, 2),
                    "success_rate": round((suite.passed / suite.total_tests * 100) if suite.total_tests > 0 else 0, 2)
                }
                for suite in self.results
            ]
        }

        return report

    def generate_detailed_report(self) -> Dict[str, Any]:
        """Generate detailed test report with individual test results"""
        summary = self.generate_summary_report()

        # Add detailed test results
        detailed_suites = []
        for suite in self.results:
            detailed_tests = []
            for test in suite.tests:
                test_detail = {
                    "name": test.name,
                    "category": test.category.value,
                    "status": test.status.value,
                    "duration": round(test.duration, 3),
                    "file_path": test.file_path,
                    "line_number": test.line_number
                }

                if test.error_message:
                    test_detail["error_message"] = test.error_message
                if test.error_traceback:
                    test_detail["error_traceback"] = test.error_traceback
                if test.memory_usage:
                    test_detail["memory_usage_bytes"] = test.memory_usage
                if test.parameters:
                    test_detail["parameters"] = test.parameters

                detailed_tests.append(test_detail)

            suite_detail = {
                "name": suite.name,
                "summary": {
                    "total": suite.total_tests,
                    "passed": suite.passed,
                    "failed": suite.failed,
                    "skipped": suite.skipped,
                    "errors": suite.errors,
                    "duration": round(suite.total_duration, 2)
                },
                "start_time": suite.start_time.isoformat(),
                "end_time": suite.end_time.isoformat(),
                "tests": detailed_tests
            }

            if suite.coverage_percentage is not None:
                suite_detail["coverage_percentage"] = round(suite.coverage_percentage, 2)
            if suite.environment:
                suite_detail["environment"] = suite.environment

            detailed_suites.append(suite_detail)

        # Add performance details
        detailed_performance = []
        for metric in self.performance_metrics:
            perf_detail = asdict(metric)
            # Round floating point values
            for key, value in perf_detail.items():
                if isinstance(value, float):
                    perf_detail[key] = round(value, 3)
            detailed_performance.append(perf_detail)

        return {
            **summary,
            "detailed_results": {
                "test_suites": detailed_suites,
                "performance_metrics": detailed_performance
            }
        }

    def generate_html_report(self) -> str:
        """Generate HTML test report"""
        detailed_report = self.generate_detailed_report()

        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Novellus API Test Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric {{ background: #ecf0f1; padding: 15px; border-radius: 5px; text-align: center; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #2c3e50; }}
        .metric-label {{ color: #7f8c8d; text-transform: uppercase; font-size: 0.8em; }}
        .passed {{ background: #d5f4e6; color: #27ae60; }}
        .failed {{ background: #fadbd8; color: #e74c3c; }}
        .skipped {{ background: #fef9e7; color: #f39c12; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #34495e; color: white; }}
        .status-passed {{ background: #d5f4e6; color: #27ae60; padding: 4px 8px; border-radius: 3px; }}
        .status-failed {{ background: #fadbd8; color: #e74c3c; padding: 4px 8px; border-radius: 3px; }}
        .status-skipped {{ background: #fef9e7; color: #f39c12; padding: 4px 8px; border-radius: 3px; }}
        .error-details {{ background: #fdf2f2; padding: 10px; border-left: 3px solid #e74c3c; margin: 5px 0; font-family: monospace; font-size: 0.9em; }}
        .chart {{ margin: 20px 0; }}
        .performance-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }}
        .performance-card {{ background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #3498db; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 Novellus API Test Report</h1>
        <p><strong>Generated:</strong> {generated_at}</p>

        <div class="summary">
            <div class="metric">
                <div class="metric-value">{total_tests}</div>
                <div class="metric-label">Total Tests</div>
            </div>
            <div class="metric passed">
                <div class="metric-value">{passed}</div>
                <div class="metric-label">Passed</div>
            </div>
            <div class="metric failed">
                <div class="metric-value">{failed}</div>
                <div class="metric-label">Failed</div>
            </div>
            <div class="metric skipped">
                <div class="metric-value">{skipped}</div>
                <div class="metric-label">Skipped</div>
            </div>
            <div class="metric">
                <div class="metric-value">{success_rate}%</div>
                <div class="metric-label">Success Rate</div>
            </div>
            <div class="metric">
                <div class="metric-value">{duration}s</div>
                <div class="metric-label">Duration</div>
            </div>
        </div>

        <h2>📊 Test Category Breakdown</h2>
        <table>
            <thead>
                <tr><th>Category</th><th>Total</th><th>Passed</th><th>Failed</th><th>Skipped</th><th>Success Rate</th></tr>
            </thead>
            <tbody>
                {category_rows}
            </tbody>
        </table>

        <h2>🚀 Performance Metrics</h2>
        <div class="performance-grid">
            {performance_cards}
        </div>

        <h2>📋 Test Suite Results</h2>
        {suite_tables}
    </div>
</body>
</html>
        """

        # Format the data
        summary = detailed_report["summary"]

        # Generate category rows
        category_rows = ""
        for category, stats in detailed_report.get("category_breakdown", {}).items():
            success_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            category_rows += f"""
            <tr>
                <td>{category.title()}</td>
                <td>{stats["total"]}</td>
                <td>{stats["passed"]}</td>
                <td>{stats["failed"]}</td>
                <td>{stats["skipped"]}</td>
                <td>{success_rate:.1f}%</td>
            </tr>
            """

        # Generate performance cards
        performance_cards = ""
        for metric in detailed_report.get("detailed_results", {}).get("performance_metrics", []):
            performance_cards += f"""
            <div class="performance-card">
                <h4>{metric["endpoint"]}</h4>
                <p><strong>Requests:</strong> {metric["total_requests"]} ({metric["successful_requests"]} successful)</p>
                <p><strong>Avg Response:</strong> {metric["average_response_time"]}ms</p>
                <p><strong>P95:</strong> {metric["p95_response_time"]}ms</p>
                <p><strong>RPS:</strong> {metric["requests_per_second"]}</p>
            </div>
            """

        # Generate suite tables
        suite_tables = ""
        for suite in detailed_report.get("detailed_results", {}).get("test_suites", []):
            suite_tables += f"""
            <h3>{suite["name"]}</h3>
            <table>
                <thead>
                    <tr><th>Test Name</th><th>Status</th><th>Duration</th><th>Category</th></tr>
                </thead>
                <tbody>
            """

            for test in suite["tests"]:
                status_class = f"status-{test['status']}"
                suite_tables += f"""
                <tr>
                    <td>{test["name"]}</td>
                    <td><span class="{status_class}">{test["status"].upper()}</span></td>
                    <td>{test["duration"]}s</td>
                    <td>{test["category"]}</td>
                </tr>
                """

                if test.get("error_message"):
                    suite_tables += f"""
                    <tr>
                        <td colspan="4">
                            <div class="error-details">{test["error_message"]}</div>
                        </td>
                    </tr>
                    """

            suite_tables += "</tbody></table>"

        return html_template.format(
            generated_at=detailed_report["generated_at"],
            total_tests=summary["total_tests"],
            passed=summary["passed"],
            failed=summary["failed"],
            skipped=summary["skipped"],
            success_rate=summary["success_rate_percent"],
            duration=summary["total_duration_seconds"],
            category_rows=category_rows,
            performance_cards=performance_cards,
            suite_tables=suite_tables
        )

    def save_reports(self):
        """Save all report formats to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # JSON summary report
        summary_report = self.generate_summary_report()
        summary_path = self.output_dir / f"test_summary_{timestamp}.json"
        with open(summary_path, 'w') as f:
            json.dump(summary_report, f, indent=2, default=str)

        # JSON detailed report
        detailed_report = self.generate_detailed_report()
        detailed_path = self.output_dir / f"test_detailed_{timestamp}.json"
        with open(detailed_path, 'w') as f:
            json.dump(detailed_report, f, indent=2, default=str)

        # HTML report
        html_report = self.generate_html_report()
        html_path = self.output_dir / f"test_report_{timestamp}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_report)

        # Create latest symlinks
        latest_summary = self.output_dir / "latest_summary.json"
        latest_detailed = self.output_dir / "latest_detailed.json"
        latest_html = self.output_dir / "latest_report.html"

        # Copy to latest files
        import shutil
        shutil.copy2(summary_path, latest_summary)
        shutil.copy2(detailed_path, latest_detailed)
        shutil.copy2(html_path, latest_html)

        return {
            "summary_report": str(summary_path),
            "detailed_report": str(detailed_path),
            "html_report": str(html_path),
            "latest_summary": str(latest_summary),
            "latest_detailed": str(latest_detailed),
            "latest_html": str(latest_html)
        }

    def analyze_trends(self, previous_reports_dir: str = None) -> Dict[str, Any]:
        """Analyze test trends comparing with previous reports"""
        if not previous_reports_dir:
            return {"error": "No previous reports directory specified"}

        # This would implement trend analysis comparing current results
        # with historical data from previous test runs
        return {
            "trends": {
                "success_rate_trend": "stable",
                "performance_trend": "improving",
                "test_count_trend": "increasing"
            }
        }


class PerformanceAnalyzer:
    """Analyze performance test results"""

    @staticmethod
    def analyze_response_times(response_times: List[float]) -> Dict[str, float]:
        """Analyze response time distribution"""
        if not response_times:
            return {}

        sorted_times = sorted(response_times)
        count = len(sorted_times)

        return {
            "min": min(sorted_times),
            "max": max(sorted_times),
            "mean": statistics.mean(sorted_times),
            "median": statistics.median(sorted_times),
            "p95": sorted_times[int(0.95 * count)],
            "p99": sorted_times[int(0.99 * count)],
            "std_dev": statistics.stdev(sorted_times) if count > 1 else 0
        }

    @staticmethod
    def analyze_throughput(total_requests: int, duration: float) -> Dict[str, float]:
        """Analyze throughput metrics"""
        return {
            "requests_per_second": total_requests / duration if duration > 0 else 0,
            "average_request_duration": duration / total_requests if total_requests > 0 else 0
        }

    @staticmethod
    def detect_performance_issues(metrics: PerformanceMetrics) -> List[str]:
        """Detect potential performance issues"""
        issues = []

        if metrics.average_response_time > 1000:  # 1 second
            issues.append("High average response time detected")

        if metrics.p95_response_time > 2000:  # 2 seconds
            issues.append("High P95 response time detected")

        if metrics.failed_requests / metrics.total_requests > 0.01:  # 1% failure rate
            issues.append("High failure rate detected")

        if metrics.requests_per_second < 10:
            issues.append("Low throughput detected")

        return issues


# CLI utility for generating reports
def main():
    """Main CLI function for test reporting"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate test reports for Novellus API")
    parser.add_argument("--input", required=True, help="Input test results directory")
    parser.add_argument("--output", default="reports", help="Output directory for reports")
    parser.add_argument("--format", choices=["json", "html", "all"], default="all", help="Report format")

    args = parser.parse_args()

    reporter = TestReporter(args.output)

    # This would load test results from the input directory
    # For now, it's a placeholder
    print(f"Generating reports from {args.input} to {args.output}")
    print(f"Format: {args.format}")

    # Generate reports
    paths = reporter.save_reports()
    print("Reports generated:")
    for name, path in paths.items():
        print(f"  {name}: {path}")


if __name__ == "__main__":
    main()