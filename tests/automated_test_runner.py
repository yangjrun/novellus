#!/usr/bin/env python3
"""
Automated Test Runner and Report Generator
自动化测试执行器和报告生成器，统一管理和执行所有测试套件
"""

import asyncio
import json
import logging
import os
import sys
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import argparse

import jinja2
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path

# 添加项目根目录到路径
sys.path.append('/h/novellus')
sys.path.append('/h/novellus/tests')

# 导入测试套件
from test_pgvector_suite import PgvectorTestSuite, TestConfig as PgVectorConfig
from test_ai_model_manager import AIModelManagerTestSuite, AITestConfig
from test_integration_suite import IntegrationTestSuite, IntegrationTestConfig
from performance_benchmark_suite import PerformanceBenchmarkSuite, BenchmarkConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/h/novellus/test_results/test_runner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TestSuiteType(str, Enum):
    """测试套件类型"""
    PGVECTOR = "pgvector"
    AI_MODEL = "ai_model"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    ALL = "all"

@dataclass
class TestRunConfig:
    """测试运行配置"""
    # 测试选择
    test_suites: List[TestSuiteType] = field(default_factory=lambda: [TestSuiteType.ALL])
    skip_long_running_tests: bool = False
    parallel_execution: bool = True
    fail_fast: bool = False

    # 环境配置
    environment: str = "test"
    cleanup_after_tests: bool = True
    generate_detailed_report: bool = True
    generate_charts: bool = True

    # 报告配置
    output_directory: str = "/h/novellus/test_results"
    report_format: List[str] = field(default_factory=lambda: ["json", "html", "markdown"])
    include_raw_data: bool = False

    # 通知配置
    enable_notifications: bool = False
    notification_webhook: Optional[str] = None

    # 数据库配置
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "postgres"
    db_user: str = "postgres"
    db_password: str = "postgres"
    redis_url: str = "redis://localhost:6379"

@dataclass
class TestSuiteResult:
    """测试套件结果"""
    suite_name: str
    suite_type: TestSuiteType
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    success: bool
    tests_run: int
    tests_passed: int
    tests_failed: int
    success_rate: float
    error_message: str = ""
    detailed_results: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TestRunSummary:
    """测试运行总结"""
    run_id: str
    start_time: datetime
    end_time: datetime
    total_duration_seconds: float
    environment: str
    configuration: TestRunConfig
    suite_results: List[TestSuiteResult]
    overall_success: bool
    overall_success_rate: float
    total_tests: int
    total_passed: int
    total_failed: int
    critical_issues: List[str] = field(default_factory=list)
    performance_summary: Dict[str, Any] = field(default_factory=dict)

class AutomatedTestRunner:
    """自动化测试运行器"""

    def __init__(self, config: TestRunConfig = None):
        self.config = config or TestRunConfig()
        self.run_id = f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.output_dir = Path(self.config.output_directory) / self.run_id

        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 配置文件路径
        self.config_file = self.output_dir / "test_config.json"
        self.log_file = self.output_dir / "test_execution.log"

        # 测试结果
        self.suite_results: List[TestSuiteResult] = []
        self.test_summary: Optional[TestRunSummary] = None

        # 设置日志
        self._setup_logging()

    def _setup_logging(self):
        """设置日志"""
        # 添加文件处理器
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # 添加到根日志器
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)

    async def run_all_tests(self) -> TestRunSummary:
        """运行所有选定的测试套件"""
        logger.info(f"Starting automated test run {self.run_id}")
        run_start_time = datetime.now()

        # 保存配置
        self._save_test_config()

        # 确定要运行的测试套件
        test_suites_to_run = self._determine_test_suites()

        logger.info(f"Will run {len(test_suites_to_run)} test suites: {[s.value for s in test_suites_to_run]}")

        # 运行测试套件
        if self.config.parallel_execution and len(test_suites_to_run) > 1:
            await self._run_tests_parallel(test_suites_to_run)
        else:
            await self._run_tests_sequential(test_suites_to_run)

        run_end_time = datetime.now()

        # 生成测试总结
        self.test_summary = self._generate_test_summary(run_start_time, run_end_time)

        # 生成报告
        await self._generate_reports()

        # 清理资源
        if self.config.cleanup_after_tests:
            await self._cleanup_test_resources()

        # 发送通知
        if self.config.enable_notifications:
            await self._send_notifications()

        logger.info(f"Test run {self.run_id} completed. Overall success rate: {self.test_summary.overall_success_rate:.2%}")

        return self.test_summary

    def _determine_test_suites(self) -> List[TestSuiteType]:
        """确定要运行的测试套件"""
        if TestSuiteType.ALL in self.config.test_suites:
            return [TestSuiteType.PGVECTOR, TestSuiteType.AI_MODEL, TestSuiteType.INTEGRATION, TestSuiteType.PERFORMANCE]
        else:
            return [suite for suite in self.config.test_suites if suite != TestSuiteType.ALL]

    async def _run_tests_sequential(self, test_suites: List[TestSuiteType]):
        """顺序运行测试套件"""
        for suite_type in test_suites:
            try:
                logger.info(f"Running test suite: {suite_type.value}")
                result = await self._run_single_test_suite(suite_type)
                self.suite_results.append(result)

                if self.config.fail_fast and not result.success:
                    logger.error(f"Test suite {suite_type.value} failed, stopping execution (fail_fast=True)")
                    break

            except Exception as e:
                logger.error(f"Failed to run test suite {suite_type.value}: {e}")
                logger.error(traceback.format_exc())

                # 创建失败结果
                failed_result = TestSuiteResult(
                    suite_name=suite_type.value,
                    suite_type=suite_type,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    duration_seconds=0,
                    success=False,
                    tests_run=0,
                    tests_passed=0,
                    tests_failed=1,
                    success_rate=0.0,
                    error_message=str(e)
                )
                self.suite_results.append(failed_result)

                if self.config.fail_fast:
                    break

    async def _run_tests_parallel(self, test_suites: List[TestSuiteType]):
        """并行运行测试套件"""
        logger.info("Running test suites in parallel...")

        async def run_suite_with_error_handling(suite_type: TestSuiteType):
            try:
                return await self._run_single_test_suite(suite_type)
            except Exception as e:
                logger.error(f"Test suite {suite_type.value} failed: {e}")
                return TestSuiteResult(
                    suite_name=suite_type.value,
                    suite_type=suite_type,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    duration_seconds=0,
                    success=False,
                    tests_run=0,
                    tests_passed=0,
                    tests_failed=1,
                    success_rate=0.0,
                    error_message=str(e)
                )

        # 创建并行任务
        tasks = [run_suite_with_error_handling(suite_type) for suite_type in test_suites]

        # 执行并收集结果
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, TestSuiteResult):
                self.suite_results.append(result)
            else:
                logger.error(f"Unexpected result type: {type(result)}")

    async def _run_single_test_suite(self, suite_type: TestSuiteType) -> TestSuiteResult:
        """运行单个测试套件"""
        start_time = datetime.now()

        try:
            if suite_type == TestSuiteType.PGVECTOR:
                return await self._run_pgvector_tests()
            elif suite_type == TestSuiteType.AI_MODEL:
                return await self._run_ai_model_tests()
            elif suite_type == TestSuiteType.INTEGRATION:
                return await self._run_integration_tests()
            elif suite_type == TestSuiteType.PERFORMANCE:
                return await self._run_performance_tests()
            else:
                raise ValueError(f"Unknown test suite type: {suite_type}")

        except Exception as e:
            end_time = datetime.now()
            logger.error(f"Test suite {suite_type.value} execution failed: {e}")

            return TestSuiteResult(
                suite_name=suite_type.value,
                suite_type=suite_type,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=(end_time - start_time).total_seconds(),
                success=False,
                tests_run=0,
                tests_passed=0,
                tests_failed=1,
                success_rate=0.0,
                error_message=str(e)
            )

    async def _run_pgvector_tests(self) -> TestSuiteResult:
        """运行pgvector测试套件"""
        start_time = datetime.now()

        config = PgVectorConfig(
            db_host=self.config.db_host,
            db_port=self.config.db_port,
            db_name=self.config.db_name,
            db_user=self.config.db_user,
            db_password=self.config.db_password
        )

        test_suite = PgvectorTestSuite(config)

        try:
            await test_suite.initialize()
            results = await test_suite.run_all_tests()

            # 解析结果
            total_tests = results['total_tests']
            passed_tests = results['passed_tests']
            success_rate = results['success_rate']

            end_time = datetime.now()

            return TestSuiteResult(
                suite_name="pgvector_comprehensive",
                suite_type=TestSuiteType.PGVECTOR,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=(end_time - start_time).total_seconds(),
                success=success_rate == 1.0,
                tests_run=total_tests,
                tests_passed=passed_tests,
                tests_failed=total_tests - passed_tests,
                success_rate=success_rate,
                detailed_results=results
            )

        finally:
            await test_suite.cleanup()

    async def _run_ai_model_tests(self) -> TestSuiteResult:
        """运行AI模型测试套件"""
        start_time = datetime.now()

        config = AITestConfig(
            test_db_url=f"postgresql+asyncpg://{self.config.db_user}:{self.config.db_password}@{self.config.db_host}:{self.config.db_port}/{self.config.db_name}",
            test_redis_url=self.config.redis_url,
            mock_api_responses=True  # 在自动化测试中使用模拟
        )

        test_suite = AIModelManagerTestSuite(config)

        try:
            await test_suite.initialize()
            results = await test_suite.run_all_tests()

            # 解析结果
            total_tests = results['total_tests']
            passed_tests = results['passed_tests']
            success_rate = results['success_rate']

            end_time = datetime.now()

            return TestSuiteResult(
                suite_name="ai_model_manager_comprehensive",
                suite_type=TestSuiteType.AI_MODEL,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=(end_time - start_time).total_seconds(),
                success=success_rate >= 0.8,  # AI测试允许一定容错
                tests_run=total_tests,
                tests_passed=passed_tests,
                tests_failed=total_tests - passed_tests,
                success_rate=success_rate,
                detailed_results=results
            )

        finally:
            await test_suite.cleanup()

    async def _run_integration_tests(self) -> TestSuiteResult:
        """运行集成测试套件"""
        start_time = datetime.now()

        config = IntegrationTestConfig(
            db_host=self.config.db_host,
            db_port=self.config.db_port,
            db_name=self.config.db_name,
            db_user=self.config.db_user,
            db_password=self.config.db_password,
            redis_url=self.config.redis_url
        )

        test_suite = IntegrationTestSuite(config)

        try:
            await test_suite.initialize()
            results = await test_suite.run_all_tests()

            # 解析结果
            total_tests = results['total_tests']
            passed_tests = results['passed_tests']
            success_rate = results['success_rate']

            end_time = datetime.now()

            return TestSuiteResult(
                suite_name="comprehensive_integration",
                suite_type=TestSuiteType.INTEGRATION,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=(end_time - start_time).total_seconds(),
                success=success_rate >= 0.8,  # 集成测试允许一定容错
                tests_run=total_tests,
                tests_passed=passed_tests,
                tests_failed=total_tests - passed_tests,
                success_rate=success_rate,
                detailed_results=results
            )

        finally:
            await test_suite.cleanup()

    async def _run_performance_tests(self) -> TestSuiteResult:
        """运行性能测试套件"""
        start_time = datetime.now()

        # 如果跳过长时间运行的测试，减少性能测试规模
        config = BenchmarkConfig(
            db_host=self.config.db_host,
            db_port=self.config.db_port,
            db_name=self.config.db_name,
            db_user=self.config.db_user,
            db_password=self.config.db_password,
            redis_url=self.config.redis_url
        )

        if self.config.skip_long_running_tests:
            config.small_dataset_size = 100
            config.medium_dataset_size = 1000
            config.large_dataset_size = 5000
            config.concurrent_users = [1, 5, 10]

        test_suite = PerformanceBenchmarkSuite(config)

        try:
            await test_suite.initialize()
            results = await test_suite.run_all_benchmarks()

            # 解析结果
            overall_summary = results['overall_summary']
            total_tests = overall_summary['total_benchmarks']
            passed_tests = overall_summary['successful_benchmarks']
            success_rate = overall_summary['success_rate']

            end_time = datetime.now()

            return TestSuiteResult(
                suite_name="performance_comprehensive",
                suite_type=TestSuiteType.PERFORMANCE,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=(end_time - start_time).total_seconds(),
                success=success_rate >= 0.75,  # 性能测试允许更多容错
                tests_run=total_tests,
                tests_passed=passed_tests,
                tests_failed=total_tests - passed_tests,
                success_rate=success_rate,
                detailed_results=results,
                performance_metrics=overall_summary
            )

        finally:
            await test_suite.cleanup()

    def _generate_test_summary(self, start_time: datetime, end_time: datetime) -> TestRunSummary:
        """生成测试运行总结"""
        total_tests = sum(result.tests_run for result in self.suite_results)
        total_passed = sum(result.tests_passed for result in self.suite_results)
        total_failed = sum(result.tests_failed for result in self.suite_results)

        overall_success_rate = total_passed / total_tests if total_tests > 0 else 0
        overall_success = all(result.success for result in self.suite_results)

        # 识别关键问题
        critical_issues = []
        for result in self.suite_results:
            if not result.success:
                critical_issues.append(f"{result.suite_name}: {result.error_message}")
            elif result.success_rate < 0.8:
                critical_issues.append(f"{result.suite_name}: Low success rate ({result.success_rate:.2%})")

        # 性能摘要
        performance_summary = {}
        perf_result = next((r for r in self.suite_results if r.suite_type == TestSuiteType.PERFORMANCE), None)
        if perf_result and perf_result.performance_metrics:
            performance_summary = {
                'overall_grade': perf_result.performance_metrics.get('overall_performance_grade', 0),
                'component_grades': {},
                'recommendations': []
            }

        return TestRunSummary(
            run_id=self.run_id,
            start_time=start_time,
            end_time=end_time,
            total_duration_seconds=(end_time - start_time).total_seconds(),
            environment=self.config.environment,
            configuration=self.config,
            suite_results=self.suite_results,
            overall_success=overall_success,
            overall_success_rate=overall_success_rate,
            total_tests=total_tests,
            total_passed=total_passed,
            total_failed=total_failed,
            critical_issues=critical_issues,
            performance_summary=performance_summary
        )

    async def _generate_reports(self):
        """生成测试报告"""
        logger.info("Generating test reports...")

        # JSON报告
        if "json" in self.config.report_format:
            await self._generate_json_report()

        # HTML报告
        if "html" in self.config.report_format:
            await self._generate_html_report()

        # Markdown报告
        if "markdown" in self.config.report_format:
            await self._generate_markdown_report()

        # 图表报告
        if self.config.generate_charts:
            await self._generate_charts()

    async def _generate_json_report(self):
        """生成JSON格式报告"""
        json_file = self.output_dir / "test_report.json"

        report_data = {
            'test_run_summary': {
                'run_id': self.test_summary.run_id,
                'start_time': self.test_summary.start_time.isoformat(),
                'end_time': self.test_summary.end_time.isoformat(),
                'duration_seconds': self.test_summary.total_duration_seconds,
                'environment': self.test_summary.environment,
                'overall_success': self.test_summary.overall_success,
                'overall_success_rate': self.test_summary.overall_success_rate,
                'total_tests': self.test_summary.total_tests,
                'total_passed': self.test_summary.total_passed,
                'total_failed': self.test_summary.total_failed,
                'critical_issues': self.test_summary.critical_issues
            },
            'suite_results': [
                {
                    'suite_name': result.suite_name,
                    'suite_type': result.suite_type.value,
                    'start_time': result.start_time.isoformat(),
                    'end_time': result.end_time.isoformat(),
                    'duration_seconds': result.duration_seconds,
                    'success': result.success,
                    'tests_run': result.tests_run,
                    'tests_passed': result.tests_passed,
                    'tests_failed': result.tests_failed,
                    'success_rate': result.success_rate,
                    'error_message': result.error_message,
                    'detailed_results': result.detailed_results if self.config.include_raw_data else {}
                }
                for result in self.suite_results
            ],
            'configuration': {
                'test_suites': [suite.value for suite in self.config.test_suites],
                'parallel_execution': self.config.parallel_execution,
                'skip_long_running_tests': self.config.skip_long_running_tests,
                'environment': self.config.environment
            }
        }

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        logger.info(f"JSON report saved to: {json_file}")

    async def _generate_html_report(self):
        """生成HTML格式报告"""
        html_file = self.output_dir / "test_report.html"

        # HTML模板
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Novellus Test Report - {{ summary.run_id }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; margin: -20px -20px 20px; border-radius: 8px 8px 0 0; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
        .metric-card { background: #f8f9fa; padding: 15px; border-radius: 6px; text-align: center; border: 1px solid #e9ecef; }
        .metric-value { font-size: 2em; font-weight: bold; margin-bottom: 5px; }
        .metric-label { color: #6c757d; font-size: 0.9em; }
        .success { color: #28a745; }
        .warning { color: #ffc107; }
        .danger { color: #dc3545; }
        .suite-results { margin: 20px 0; }
        .suite-card { background: white; border: 1px solid #ddd; border-radius: 6px; margin: 10px 0; overflow: hidden; }
        .suite-header { padding: 15px; background: #f8f9fa; border-bottom: 1px solid #ddd; display: flex; justify-content: space-between; align-items: center; }
        .suite-content { padding: 15px; }
        .status-badge { padding: 5px 10px; border-radius: 15px; color: white; font-size: 0.8em; font-weight: bold; }
        .status-success { background-color: #28a745; }
        .status-failure { background-color: #dc3545; }
        .progress-bar { width: 100%; height: 20px; background-color: #e9ecef; border-radius: 10px; overflow: hidden; margin: 10px 0; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #28a745, #20c997); transition: width 0.3s ease; }
        .issues-section { margin: 20px 0; padding: 15px; background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 6px; }
        .timestamp { color: #6c757d; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Novellus Test Report</h1>
            <h2>{{ summary.run_id }}</h2>
            <p class="timestamp">Generated on {{ summary.end_time.strftime('%Y-%m-%d %H:%M:%S') }}</p>
        </div>

        <div class="summary">
            <div class="metric-card">
                <div class="metric-value {% if summary.overall_success %}success{% else %}danger{% endif %}">
                    {% if summary.overall_success %}✅{% else %}❌{% endif %}
                </div>
                <div class="metric-label">Overall Status</div>
            </div>
            <div class="metric-card">
                <div class="metric-value {{ 'success' if summary.overall_success_rate >= 0.9 else 'warning' if summary.overall_success_rate >= 0.7 else 'danger' }}">
                    {{ "%.1f"|format(summary.overall_success_rate * 100) }}%
                </div>
                <div class="metric-label">Success Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ summary.total_tests }}</div>
                <div class="metric-label">Total Tests</div>
            </div>
            <div class="metric-card">
                <div class="metric-value success">{{ summary.total_passed }}</div>
                <div class="metric-label">Passed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value danger">{{ summary.total_failed }}</div>
                <div class="metric-label">Failed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ "%.1f"|format(summary.total_duration_seconds) }}s</div>
                <div class="metric-label">Duration</div>
            </div>
        </div>

        {% if summary.critical_issues %}
        <div class="issues-section">
            <h3>🚨 Critical Issues</h3>
            <ul>
                {% for issue in summary.critical_issues %}
                <li>{{ issue }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}

        <div class="suite-results">
            <h3>📊 Test Suite Results</h3>
            {% for result in suite_results %}
            <div class="suite-card">
                <div class="suite-header">
                    <div>
                        <h4>{{ result.suite_name }}</h4>
                        <small>{{ result.suite_type.value }} | {{ "%.1f"|format(result.duration_seconds) }}s</small>
                    </div>
                    <span class="status-badge {% if result.success %}status-success{% else %}status-failure{% endif %}">
                        {% if result.success %}PASSED{% else %}FAILED{% endif %}
                    </span>
                </div>
                <div class="suite-content">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {{ result.success_rate * 100 }}%"></div>
                    </div>
                    <p>
                        <strong>{{ result.tests_passed }}/{{ result.tests_run }}</strong> tests passed
                        ({{ "%.1f"|format(result.success_rate * 100) }}%)
                    </p>
                    {% if result.error_message %}
                    <p><strong>Error:</strong> {{ result.error_message }}</p>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
        """

        # 渲染模板
        template = jinja2.Template(html_template)
        html_content = template.render(
            summary=self.test_summary,
            suite_results=self.suite_results
        )

        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"HTML report saved to: {html_file}")

    async def _generate_markdown_report(self):
        """生成Markdown格式报告"""
        md_file = self.output_dir / "test_report.md"

        # 生成Markdown内容
        md_content = f"""# 🧪 Novellus Test Report

**Run ID:** {self.test_summary.run_id}
**Environment:** {self.test_summary.environment}
**Generated:** {self.test_summary.end_time.strftime('%Y-%m-%d %H:%M:%S')}
**Duration:** {self.test_summary.total_duration_seconds:.1f} seconds

## 📊 Summary

| Metric | Value |
|--------|-------|
| Overall Status | {'✅ PASSED' if self.test_summary.overall_success else '❌ FAILED'} |
| Success Rate | {self.test_summary.overall_success_rate:.1%} |
| Total Tests | {self.test_summary.total_tests} |
| Passed Tests | {self.test_summary.total_passed} |
| Failed Tests | {self.test_summary.total_failed} |

"""

        # 添加关键问题
        if self.test_summary.critical_issues:
            md_content += "## 🚨 Critical Issues\n\n"
            for issue in self.test_summary.critical_issues:
                md_content += f"- {issue}\n"
            md_content += "\n"

        # 添加测试套件结果
        md_content += "## 📋 Test Suite Results\n\n"

        for result in self.suite_results:
            status = "✅ PASSED" if result.success else "❌ FAILED"
            md_content += f"### {result.suite_name}\n\n"
            md_content += f"- **Status:** {status}\n"
            md_content += f"- **Type:** {result.suite_type.value}\n"
            md_content += f"- **Duration:** {result.duration_seconds:.1f} seconds\n"
            md_content += f"- **Tests:** {result.tests_passed}/{result.tests_run} passed ({result.success_rate:.1%})\n"

            if result.error_message:
                md_content += f"- **Error:** {result.error_message}\n"

            md_content += "\n"

        # 添加配置信息
        md_content += "## ⚙️ Configuration\n\n"
        md_content += f"- **Test Suites:** {', '.join([suite.value for suite in self.config.test_suites])}\n"
        md_content += f"- **Parallel Execution:** {'Yes' if self.config.parallel_execution else 'No'}\n"
        md_content += f"- **Skip Long Tests:** {'Yes' if self.config.skip_long_running_tests else 'No'}\n"
        md_content += f"- **Environment:** {self.config.environment}\n"

        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)

        logger.info(f"Markdown report saved to: {md_file}")

    async def _generate_charts(self):
        """生成图表"""
        if not self.config.generate_charts:
            return

        try:
            # 设置matplotlib样式
            plt.style.use('seaborn-v0_8')
            sns.set_palette("husl")

            # 创建图表目录
            charts_dir = self.output_dir / "charts"
            charts_dir.mkdir(exist_ok=True)

            # 1. 测试套件成功率图表
            await self._generate_success_rate_chart(charts_dir)

            # 2. 测试持续时间图表
            await self._generate_duration_chart(charts_dir)

            # 3. 测试结果分布图表
            await self._generate_distribution_chart(charts_dir)

            logger.info(f"Charts saved to: {charts_dir}")

        except Exception as e:
            logger.warning(f"Failed to generate charts: {e}")

    async def _generate_success_rate_chart(self, charts_dir: Path):
        """生成成功率图表"""
        # 准备数据
        suite_names = [result.suite_name for result in self.suite_results]
        success_rates = [result.success_rate * 100 for result in self.suite_results]

        # 创建图表
        plt.figure(figsize=(10, 6))
        bars = plt.bar(suite_names, success_rates)

        # 设置颜色
        for bar, rate in zip(bars, success_rates):
            if rate >= 90:
                bar.set_color('#28a745')  # 绿色
            elif rate >= 70:
                bar.set_color('#ffc107')  # 黄色
            else:
                bar.set_color('#dc3545')  # 红色

        plt.title('Test Suite Success Rates', fontsize=16, fontweight='bold')
        plt.xlabel('Test Suite')
        plt.ylabel('Success Rate (%)')
        plt.xticks(rotation=45, ha='right')
        plt.ylim(0, 100)

        # 添加数值标签
        for bar, rate in zip(bars, success_rates):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{rate:.1f}%', ha='center', va='bottom')

        plt.tight_layout()
        plt.savefig(charts_dir / 'success_rates.png', dpi=300, bbox_inches='tight')
        plt.close()

    async def _generate_duration_chart(self, charts_dir: Path):
        """生成持续时间图表"""
        # 准备数据
        suite_names = [result.suite_name for result in self.suite_results]
        durations = [result.duration_seconds for result in self.suite_results]

        # 创建图表
        plt.figure(figsize=(10, 6))
        bars = plt.bar(suite_names, durations, color='skyblue')

        plt.title('Test Suite Execution Duration', fontsize=16, fontweight='bold')
        plt.xlabel('Test Suite')
        plt.ylabel('Duration (seconds)')
        plt.xticks(rotation=45, ha='right')

        # 添加数值标签
        for bar, duration in zip(bars, durations):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(durations)*0.01,
                    f'{duration:.1f}s', ha='center', va='bottom')

        plt.tight_layout()
        plt.savefig(charts_dir / 'durations.png', dpi=300, bbox_inches='tight')
        plt.close()

    async def _generate_distribution_chart(self, charts_dir: Path):
        """生成测试结果分布图表"""
        # 准备数据
        total_passed = sum(result.tests_passed for result in self.suite_results)
        total_failed = sum(result.tests_failed for result in self.suite_results)

        # 创建饼图
        plt.figure(figsize=(8, 8))
        labels = ['Passed', 'Failed']
        sizes = [total_passed, total_failed]
        colors = ['#28a745', '#dc3545']

        # 只显示非零的部分
        non_zero_labels = []
        non_zero_sizes = []
        non_zero_colors = []

        for label, size, color in zip(labels, sizes, colors):
            if size > 0:
                non_zero_labels.append(f'{label}\n({size} tests)')
                non_zero_sizes.append(size)
                non_zero_colors.append(color)

        if non_zero_sizes:
            plt.pie(non_zero_sizes, labels=non_zero_labels, colors=non_zero_colors,
                   autopct='%1.1f%%', startangle=90)
            plt.title('Overall Test Results Distribution', fontsize=16, fontweight='bold')
        else:
            plt.text(0.5, 0.5, 'No Test Data Available', ha='center', va='center',
                    transform=plt.gca().transAxes, fontsize=16)

        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(charts_dir / 'distribution.png', dpi=300, bbox_inches='tight')
        plt.close()

    def _save_test_config(self):
        """保存测试配置"""
        config_data = {
            'run_id': self.run_id,
            'test_suites': [suite.value for suite in self.config.test_suites],
            'skip_long_running_tests': self.config.skip_long_running_tests,
            'parallel_execution': self.config.parallel_execution,
            'fail_fast': self.config.fail_fast,
            'environment': self.config.environment,
            'cleanup_after_tests': self.config.cleanup_after_tests,
            'generate_detailed_report': self.config.generate_detailed_report,
            'generate_charts': self.config.generate_charts,
            'output_directory': str(self.output_dir),
            'report_format': self.config.report_format,
            'database_config': {
                'host': self.config.db_host,
                'port': self.config.db_port,
                'database': self.config.db_name
            }
        }

        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

    async def _cleanup_test_resources(self):
        """清理测试资源"""
        logger.info("Cleaning up test resources...")
        # 这里可以添加清理逻辑，比如删除临时数据等

    async def _send_notifications(self):
        """发送测试结果通知"""
        if not self.config.notification_webhook:
            return

        try:
            # 构建通知消息
            message = {
                'text': f"Test Run {self.run_id} Completed",
                'attachments': [
                    {
                        'color': 'good' if self.test_summary.overall_success else 'danger',
                        'fields': [
                            {
                                'title': 'Overall Status',
                                'value': 'PASSED' if self.test_summary.overall_success else 'FAILED',
                                'short': True
                            },
                            {
                                'title': 'Success Rate',
                                'value': f"{self.test_summary.overall_success_rate:.1%}",
                                'short': True
                            },
                            {
                                'title': 'Total Tests',
                                'value': str(self.test_summary.total_tests),
                                'short': True
                            },
                            {
                                'title': 'Duration',
                                'value': f"{self.test_summary.total_duration_seconds:.1f}s",
                                'short': True
                            }
                        ]
                    }
                ]
            }

            # 发送通知 (这里可以实现实际的Webhook调用)
            logger.info(f"Notification would be sent to: {self.config.notification_webhook}")

        except Exception as e:
            logger.warning(f"Failed to send notification: {e}")

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='Novellus Automated Test Runner')

    parser.add_argument('--suites', nargs='+', choices=['pgvector', 'ai_model', 'integration', 'performance', 'all'],
                       default=['all'], help='Test suites to run')
    parser.add_argument('--environment', default='test', help='Test environment')
    parser.add_argument('--parallel', action='store_true', help='Run test suites in parallel')
    parser.add_argument('--fail-fast', action='store_true', help='Stop on first failure')
    parser.add_argument('--skip-long', action='store_true', help='Skip long-running tests')
    parser.add_argument('--no-cleanup', action='store_true', help='Skip cleanup after tests')
    parser.add_argument('--no-charts', action='store_true', help='Skip chart generation')
    parser.add_argument('--output-dir', default='/h/novellus/test_results', help='Output directory')
    parser.add_argument('--formats', nargs='+', choices=['json', 'html', 'markdown'],
                       default=['json', 'html'], help='Report formats')

    # 数据库配置
    parser.add_argument('--db-host', default='localhost', help='Database host')
    parser.add_argument('--db-port', type=int, default=5432, help='Database port')
    parser.add_argument('--db-name', default='postgres', help='Database name')
    parser.add_argument('--db-user', default='postgres', help='Database user')
    parser.add_argument('--db-password', default='postgres', help='Database password')
    parser.add_argument('--redis-url', default='redis://localhost:6379', help='Redis URL')

    return parser.parse_args()

async def main():
    """主函数"""
    args = parse_arguments()

    # 构建配置
    config = TestRunConfig(
        test_suites=[TestSuiteType(suite) for suite in args.suites],
        skip_long_running_tests=args.skip_long,
        parallel_execution=args.parallel,
        fail_fast=args.fail_fast,
        environment=args.environment,
        cleanup_after_tests=not args.no_cleanup,
        generate_charts=not args.no_charts,
        output_directory=args.output_dir,
        report_format=args.formats,
        db_host=args.db_host,
        db_port=args.db_port,
        db_name=args.db_name,
        db_user=args.db_user,
        db_password=args.db_password,
        redis_url=args.redis_url
    )

    # 创建并运行测试
    test_runner = AutomatedTestRunner(config)

    try:
        test_summary = await test_runner.run_all_tests()

        # 输出结果摘要
        print(f"\n{'='*60}")
        print(f"🧪 Test Run {test_summary.run_id} Completed")
        print(f"{'='*60}")
        print(f"Overall Status: {'✅ PASSED' if test_summary.overall_success else '❌ FAILED'}")
        print(f"Success Rate:   {test_summary.overall_success_rate:.1%}")
        print(f"Total Tests:    {test_summary.total_tests}")
        print(f"Passed:         {test_summary.total_passed}")
        print(f"Failed:         {test_summary.total_failed}")
        print(f"Duration:       {test_summary.total_duration_seconds:.1f} seconds")
        print(f"Reports:        {test_runner.output_dir}")

        if test_summary.critical_issues:
            print(f"\n🚨 Critical Issues:")
            for issue in test_summary.critical_issues:
                print(f"  - {issue}")

        return 0 if test_summary.overall_success else 1

    except Exception as e:
        logger.error(f"Test runner failed: {e}")
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))