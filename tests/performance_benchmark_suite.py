#!/usr/bin/env python3
"""
Performance Benchmark and Monitoring Suite
性能基准测试和监控系统，用于测试pgvector、AI模型管理系统的性能指标
"""

import asyncio
import json
import logging
import os
import random
import statistics
import time
import uuid
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
import traceback

import asyncpg
import numpy as np
import psutil
import matplotlib.pyplot as plt
import seaborn as sns
from contextlib import asynccontextmanager

# 导入被测试的模块
import sys
sys.path.append('/h/novellus/src')

from ai.model_manager import AIModelManager, ModelConfig, ModelProvider, ModelStatus
from ai.cache_manager import CacheManager
from ai.metrics_collector import MetricsCollector
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BenchmarkConfig:
    """基准测试配置"""
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "postgres"
    db_user: str = "postgres"
    db_password: str = "postgres"
    redis_url: str = "redis://localhost:6379"

    # 测试规模配置
    vector_dimensions: int = 1536
    small_dataset_size: int = 1000
    medium_dataset_size: int = 10000
    large_dataset_size: int = 100000

    # 性能测试配置
    concurrent_users: List[int] = field(default_factory=lambda: [1, 5, 10, 20, 50])
    query_batches: List[int] = field(default_factory=lambda: [10, 50, 100, 500])
    cache_sizes: List[int] = field(default_factory=lambda: [100, 500, 1000, 5000])

    # 基准阈值
    vector_search_threshold_ms: int = 100
    ai_completion_threshold_ms: int = 2000
    cache_hit_threshold_ms: int = 50
    throughput_threshold_qps: float = 10.0

    # 监控配置
    monitoring_duration_seconds: int = 300
    metrics_collection_interval_seconds: int = 5

    # 输出配置
    generate_plots: bool = True
    save_raw_data: bool = True

@dataclass
class PerformanceMetric:
    """性能指标"""
    metric_name: str
    timestamp: datetime
    value: float
    unit: str
    component: str
    test_scenario: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BenchmarkResult:
    """基准测试结果"""
    test_name: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    success: bool
    metrics: List[PerformanceMetric]
    summary_stats: Dict[str, Any]
    error_message: str = ""

class SystemMonitor:
    """系统监控器"""

    def __init__(self, collection_interval: int = 5):
        self.collection_interval = collection_interval
        self.monitoring = False
        self.metrics_history: List[Dict[str, Any]] = []

    async def start_monitoring(self):
        """开始系统监控"""
        self.monitoring = True
        self.metrics_history = []

        while self.monitoring:
            try:
                # 收集系统指标
                process = psutil.Process()

                # CPU和内存
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_info = psutil.virtual_memory()
                process_memory = process.memory_info()

                # 磁盘IO
                disk_io = psutil.disk_io_counters()

                # 网络IO
                network_io = psutil.net_io_counters()

                metrics = {
                    'timestamp': datetime.now().isoformat(),
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory_info.percent,
                    'memory_available_gb': memory_info.available / (1024**3),
                    'process_memory_mb': process_memory.rss / (1024**2),
                    'disk_read_mb': disk_io.read_bytes / (1024**2) if disk_io else 0,
                    'disk_write_mb': disk_io.write_bytes / (1024**2) if disk_io else 0,
                    'network_sent_mb': network_io.bytes_sent / (1024**2) if network_io else 0,
                    'network_recv_mb': network_io.bytes_recv / (1024**2) if network_io else 0
                }

                self.metrics_history.append(metrics)

                await asyncio.sleep(self.collection_interval)

            except Exception as e:
                logger.error(f"System monitoring error: {e}")
                await asyncio.sleep(self.collection_interval)

    def stop_monitoring(self):
        """停止系统监控"""
        self.monitoring = False

    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取监控指标摘要"""
        if not self.metrics_history:
            return {}

        # 计算统计指标
        cpu_values = [m['cpu_percent'] for m in self.metrics_history]
        memory_values = [m['memory_percent'] for m in self.metrics_history]
        process_memory_values = [m['process_memory_mb'] for m in self.metrics_history]

        return {
            'monitoring_duration_seconds': len(self.metrics_history) * self.collection_interval,
            'cpu_stats': {
                'min': min(cpu_values),
                'max': max(cpu_values),
                'avg': statistics.mean(cpu_values),
                'median': statistics.median(cpu_values)
            },
            'memory_stats': {
                'min': min(memory_values),
                'max': max(memory_values),
                'avg': statistics.mean(memory_values),
                'median': statistics.median(memory_values)
            },
            'process_memory_stats': {
                'min': min(process_memory_values),
                'max': max(process_memory_values),
                'avg': statistics.mean(process_memory_values),
                'median': statistics.median(process_memory_values)
            },
            'raw_metrics': self.metrics_history
        }

class PerformanceBenchmarkSuite:
    """性能基准测试套件"""

    def __init__(self, config: BenchmarkConfig = None):
        self.config = config or BenchmarkConfig()
        self.db_pool = None
        self.ai_manager = None
        self.cache_manager = None
        self.metrics_collector = None
        self.system_monitor = SystemMonitor(self.config.metrics_collection_interval_seconds)

        # 结果存储
        self.benchmark_results: List[BenchmarkResult] = []
        self.performance_metrics: List[PerformanceMetric] = []

        # 测试数据
        self.test_data_ids: List[str] = []

    async def initialize(self):
        """初始化基准测试环境"""
        logger.info("Initializing performance benchmark suite...")

        # 创建数据库连接池
        self.db_pool = await asyncpg.create_pool(
            host=self.config.db_host,
            port=self.config.db_port,
            database=self.config.db_name,
            user=self.config.db_user,
            password=self.config.db_password,
            min_size=10,
            max_size=50
        )

        # 初始化AI模型管理器
        self.ai_manager = AIModelManager(
            db_url=f"postgresql+asyncpg://{self.config.db_user}:{self.config.db_password}@{self.config.db_host}:{self.config.db_port}/{self.config.db_name}",
            redis_url=self.config.redis_url
        )

        # 初始化缓存管理器
        self.cache_manager = CacheManager(
            redis_url=self.config.redis_url,
            db_pool=self.db_pool
        )

        # 初始化指标收集器
        self.metrics_collector = MetricsCollector(
            db_pool=self.db_pool,
            collection_interval=self.config.metrics_collection_interval_seconds
        )

        # 启动组件
        await self.ai_manager.initialize()
        await self.cache_manager.initialize()
        await self.metrics_collector.initialize()

        # 验证环境
        await self._verify_benchmark_environment()

        logger.info("Performance benchmark suite initialized successfully")

    async def _verify_benchmark_environment(self):
        """验证基准测试环境"""
        # 验证pgvector扩展
        async with self.db_pool.acquire() as conn:
            vector_ext = await conn.fetchval("SELECT COUNT(*) FROM pg_extension WHERE extname = 'vector'")
            if vector_ext == 0:
                raise Exception("pgvector extension not available for benchmarking")

            # 创建基准测试表
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS benchmark_vectors (
                    id BIGSERIAL PRIMARY KEY,
                    dataset_size INTEGER,
                    batch_id INTEGER,
                    content_text TEXT,
                    embedding vector({self.config.vector_dimensions}),
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 创建性能指标表
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_benchmarks (
                    id SERIAL PRIMARY KEY,
                    test_name VARCHAR(255),
                    component VARCHAR(100),
                    test_scenario VARCHAR(255),
                    metric_name VARCHAR(100),
                    metric_value NUMERIC,
                    metric_unit VARCHAR(50),
                    metadata JSONB,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def _generate_test_vectors(self, count: int, batch_id: int = 0) -> List[Tuple[str, List[float], Dict[str, Any]]]:
        """生成测试向量数据"""
        vectors = []

        for i in range(count):
            # 生成随机向量
            embedding = [random.random() for _ in range(self.config.vector_dimensions)]

            # 生成测试内容
            content = f"Benchmark test content {batch_id}_{i}: " + " ".join([
                f"word{j}" for j in range(random.randint(10, 50))
            ])

            # 生成元数据
            metadata = {
                'batch_id': batch_id,
                'content_length': len(content),
                'vector_norm': sum(x*x for x in embedding) ** 0.5,
                'generated_at': datetime.now().isoformat()
            }

            vectors.append((content, embedding, metadata))

        return vectors

    async def _insert_benchmark_vectors(self, dataset_size: int, batch_size: int = 1000) -> int:
        """插入基准测试向量数据"""
        logger.info(f"Inserting {dataset_size} benchmark vectors...")

        total_inserted = 0
        batch_id = 0

        for i in range(0, dataset_size, batch_size):
            current_batch_size = min(batch_size, dataset_size - i)
            vectors = self._generate_test_vectors(current_batch_size, batch_id)

            async with self.db_pool.acquire() as conn:
                insert_data = [
                    (dataset_size, batch_id, content, embedding, json.dumps(metadata))
                    for content, embedding, metadata in vectors
                ]

                await conn.executemany("""
                    INSERT INTO benchmark_vectors (dataset_size, batch_id, content_text, embedding, metadata)
                    VALUES ($1, $2, $3, $4, $5)
                """, insert_data)

            total_inserted += current_batch_size
            batch_id += 1

            if batch_id % 10 == 0:
                logger.info(f"Inserted {total_inserted}/{dataset_size} vectors...")

        logger.info(f"Completed inserting {total_inserted} benchmark vectors")
        return total_inserted

    async def benchmark_vector_search_performance(self) -> BenchmarkResult:
        """基准测试向量搜索性能"""
        test_name = "vector_search_performance"
        start_time = datetime.now()
        metrics = []

        try:
            # 准备测试数据
            test_dataset_sizes = [
                self.config.small_dataset_size,
                self.config.medium_dataset_size,
                self.config.large_dataset_size
            ]

            for dataset_size in test_dataset_sizes:
                logger.info(f"Benchmarking vector search with {dataset_size} vectors...")

                # 插入测试数据
                await self._insert_benchmark_vectors(dataset_size)

                # 创建索引并测试不同索引类型
                index_types = [
                    ('no_index', None),
                    ('hnsw', 'CREATE INDEX CONCURRENTLY idx_benchmark_hnsw ON benchmark_vectors USING hnsw (embedding vector_l2_ops)'),
                    ('ivfflat', 'CREATE INDEX CONCURRENTLY idx_benchmark_ivfflat ON benchmark_vectors USING ivfflat (embedding vector_l2_ops) WITH (lists = 100)')
                ]

                for index_name, index_sql in index_types:
                    # 创建索引
                    if index_sql:
                        async with self.db_pool.acquire() as conn:
                            await conn.execute("DROP INDEX IF EXISTS idx_benchmark_hnsw")
                            await conn.execute("DROP INDEX IF EXISTS idx_benchmark_ivfflat")
                            await conn.execute(index_sql)

                    # 测试不同的查询批次大小
                    for batch_size in self.config.query_batches:
                        # 生成查询向量
                        query_vectors = [
                            [random.random() for _ in range(self.config.vector_dimensions)]
                            for _ in range(batch_size)
                        ]

                        # 执行查询性能测试
                        latencies = []
                        throughput_start = time.time()

                        for query_vector in query_vectors:
                            query_start = time.time()

                            async with self.db_pool.acquire() as conn:
                                results = await conn.fetch("""
                                    SELECT id, content_text, embedding <-> $1 as distance
                                    FROM benchmark_vectors
                                    WHERE dataset_size = $2
                                    ORDER BY embedding <-> $1
                                    LIMIT 10
                                """, query_vector, dataset_size)

                            query_latency = (time.time() - query_start) * 1000
                            latencies.append(query_latency)

                        throughput_duration = time.time() - throughput_start
                        throughput = batch_size / throughput_duration

                        # 计算统计指标
                        latencies.sort()

                        metrics.extend([
                            PerformanceMetric(
                                metric_name="vector_search_latency_p50",
                                timestamp=datetime.now(),
                                value=latencies[len(latencies) // 2],
                                unit="ms",
                                component="pgvector",
                                test_scenario=f"{dataset_size}_{index_name}_{batch_size}",
                                metadata={
                                    'dataset_size': dataset_size,
                                    'index_type': index_name,
                                    'batch_size': batch_size
                                }
                            ),
                            PerformanceMetric(
                                metric_name="vector_search_latency_p95",
                                timestamp=datetime.now(),
                                value=latencies[int(len(latencies) * 0.95)],
                                unit="ms",
                                component="pgvector",
                                test_scenario=f"{dataset_size}_{index_name}_{batch_size}"
                            ),
                            PerformanceMetric(
                                metric_name="vector_search_throughput",
                                timestamp=datetime.now(),
                                value=throughput,
                                unit="qps",
                                component="pgvector",
                                test_scenario=f"{dataset_size}_{index_name}_{batch_size}"
                            )
                        ])

                        logger.info(f"Dataset: {dataset_size}, Index: {index_name}, Batch: {batch_size}, "
                                   f"P50: {latencies[len(latencies) // 2]:.2f}ms, "
                                   f"Throughput: {throughput:.2f} qps")

                # 清理测试数据
                async with self.db_pool.acquire() as conn:
                    await conn.execute("DELETE FROM benchmark_vectors WHERE dataset_size = $1", dataset_size)
                    await conn.execute("DROP INDEX IF EXISTS idx_benchmark_hnsw")
                    await conn.execute("DROP INDEX IF EXISTS idx_benchmark_ivfflat")

            # 计算摘要统计
            search_latencies = [m.value for m in metrics if 'latency' in m.metric_name]
            search_throughputs = [m.value for m in metrics if 'throughput' in m.metric_name]

            summary_stats = {
                'total_tests': len(metrics),
                'avg_latency_ms': statistics.mean(search_latencies) if search_latencies else 0,
                'max_latency_ms': max(search_latencies) if search_latencies else 0,
                'avg_throughput_qps': statistics.mean(search_throughputs) if search_throughputs else 0,
                'max_throughput_qps': max(search_throughputs) if search_throughputs else 0,
                'performance_acceptable': all(l < self.config.vector_search_threshold_ms for l in search_latencies) if search_latencies else False
            }

            return BenchmarkResult(
                test_name=test_name,
                start_time=start_time,
                end_time=datetime.now(),
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                success=True,
                metrics=metrics,
                summary_stats=summary_stats
            )

        except Exception as e:
            logger.error(f"Vector search benchmark failed: {e}")
            return BenchmarkResult(
                test_name=test_name,
                start_time=start_time,
                end_time=datetime.now(),
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                success=False,
                metrics=metrics,
                summary_stats={},
                error_message=str(e)
            )

    async def benchmark_ai_model_performance(self) -> BenchmarkResult:
        """基准测试AI模型性能"""
        test_name = "ai_model_performance"
        start_time = datetime.now()
        metrics = []

        try:
            # 测试提示词集合
            test_prompts = [
                ("short", "Hello, how are you?"),
                ("medium", "Explain the concept of artificial intelligence and its applications in modern technology."),
                ("long", "Write a comprehensive analysis of the impact of machine learning on various industries, including healthcare, finance, education, and transportation. Discuss both benefits and challenges." * 3),
                ("code", "Write a Python function to calculate the factorial of a number using recursion."),
                ("creative", "Write a short story about a robot learning to understand human emotions.")
            ]

            # 测试不同并发级别
            for concurrent_users in self.config.concurrent_users:
                logger.info(f"Testing AI model performance with {concurrent_users} concurrent users...")

                for prompt_type, prompt in test_prompts:
                    async def single_completion(user_id: int):
                        completion_start = time.time()

                        try:
                            # 模拟AI完成请求
                            result = {
                                'content': f"Mock AI response for user {user_id}: {prompt[:50]}...",
                                'model': 'mock-gpt-4',
                                'usage': {
                                    'prompt_tokens': len(prompt.split()),
                                    'completion_tokens': 100,
                                    'total_tokens': len(prompt.split()) + 100
                                }
                            }

                            completion_time = (time.time() - completion_start) * 1000

                            return {
                                'user_id': user_id,
                                'success': True,
                                'latency_ms': completion_time,
                                'tokens': result['usage']['total_tokens'],
                                'cost': result['usage']['total_tokens'] * 0.00001  # 模拟成本
                            }

                        except Exception as e:
                            completion_time = (time.time() - completion_start) * 1000
                            return {
                                'user_id': user_id,
                                'success': False,
                                'latency_ms': completion_time,
                                'error': str(e)
                            }

                    # 执行并发测试
                    batch_start = time.time()
                    tasks = [single_completion(i) for i in range(concurrent_users)]
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    batch_duration = time.time() - batch_start

                    # 分析结果
                    successful_results = [r for r in results if isinstance(r, dict) and r.get('success')]
                    failed_results = [r for r in results if not isinstance(r, dict) or not r.get('success')]

                    if successful_results:
                        latencies = [r['latency_ms'] for r in successful_results]
                        latencies.sort()

                        total_tokens = sum(r.get('tokens', 0) for r in successful_results)
                        total_cost = sum(r.get('cost', 0) for r in successful_results)
                        throughput = len(successful_results) / batch_duration

                        metrics.extend([
                            PerformanceMetric(
                                metric_name="ai_completion_latency_p50",
                                timestamp=datetime.now(),
                                value=latencies[len(latencies) // 2],
                                unit="ms",
                                component="ai_model",
                                test_scenario=f"{prompt_type}_{concurrent_users}",
                                metadata={
                                    'prompt_type': prompt_type,
                                    'concurrent_users': concurrent_users,
                                    'prompt_length': len(prompt)
                                }
                            ),
                            PerformanceMetric(
                                metric_name="ai_completion_latency_p95",
                                timestamp=datetime.now(),
                                value=latencies[int(len(latencies) * 0.95)],
                                unit="ms",
                                component="ai_model",
                                test_scenario=f"{prompt_type}_{concurrent_users}"
                            ),
                            PerformanceMetric(
                                metric_name="ai_completion_throughput",
                                timestamp=datetime.now(),
                                value=throughput,
                                unit="rps",
                                component="ai_model",
                                test_scenario=f"{prompt_type}_{concurrent_users}"
                            ),
                            PerformanceMetric(
                                metric_name="ai_completion_cost",
                                timestamp=datetime.now(),
                                value=total_cost,
                                unit="usd",
                                component="ai_model",
                                test_scenario=f"{prompt_type}_{concurrent_users}"
                            )
                        ])

                        logger.info(f"Prompt: {prompt_type}, Users: {concurrent_users}, "
                                   f"P50: {latencies[len(latencies) // 2]:.2f}ms, "
                                   f"Success Rate: {len(successful_results)}/{concurrent_users}")

            # 计算摘要统计
            completion_latencies = [m.value for m in metrics if 'latency' in m.metric_name]
            completion_throughputs = [m.value for m in metrics if 'throughput' in m.metric_name]
            total_costs = [m.value for m in metrics if 'cost' in m.metric_name]

            summary_stats = {
                'total_tests': len(metrics),
                'avg_latency_ms': statistics.mean(completion_latencies) if completion_latencies else 0,
                'max_latency_ms': max(completion_latencies) if completion_latencies else 0,
                'avg_throughput_rps': statistics.mean(completion_throughputs) if completion_throughputs else 0,
                'total_cost_usd': sum(total_costs),
                'performance_acceptable': all(l < self.config.ai_completion_threshold_ms for l in completion_latencies) if completion_latencies else False
            }

            return BenchmarkResult(
                test_name=test_name,
                start_time=start_time,
                end_time=datetime.now(),
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                success=True,
                metrics=metrics,
                summary_stats=summary_stats
            )

        except Exception as e:
            logger.error(f"AI model benchmark failed: {e}")
            return BenchmarkResult(
                test_name=test_name,
                start_time=start_time,
                end_time=datetime.now(),
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                success=False,
                metrics=metrics,
                summary_stats={},
                error_message=str(e)
            )

    async def benchmark_cache_performance(self) -> BenchmarkResult:
        """基准测试缓存性能"""
        test_name = "cache_performance"
        start_time = datetime.now()
        metrics = []

        try:
            # 测试不同缓存大小
            for cache_size in self.config.cache_sizes:
                logger.info(f"Testing cache performance with {cache_size} items...")

                # 预填充缓存
                cache_data = {}
                for i in range(cache_size):
                    key = f"benchmark_key_{i}"
                    value = {
                        'data': f"Benchmark cache value {i}",
                        'metadata': {'size': len(f"Benchmark cache value {i}"), 'index': i},
                        'created_at': datetime.now().isoformat()
                    }
                    cache_data[key] = value

                # 写入性能测试
                write_start = time.time()
                write_latencies = []

                for key, value in cache_data.items():
                    write_op_start = time.time()

                    # 模拟缓存写入
                    await asyncio.sleep(0.001)  # 模拟写入延迟

                    write_latency = (time.time() - write_op_start) * 1000
                    write_latencies.append(write_latency)

                total_write_time = time.time() - write_start
                write_throughput = cache_size / total_write_time

                # 读取性能测试
                read_start = time.time()
                read_latencies = []
                cache_hits = 0

                # 测试缓存命中
                for key in list(cache_data.keys())[:cache_size // 2]:
                    read_op_start = time.time()

                    # 模拟缓存读取
                    if key in cache_data:
                        cache_hits += 1
                        await asyncio.sleep(0.0005)  # 模拟缓存命中延迟
                    else:
                        await asyncio.sleep(0.01)  # 模拟缓存未命中延迟

                    read_latency = (time.time() - read_op_start) * 1000
                    read_latencies.append(read_latency)

                # 测试缓存未命中
                for i in range(cache_size // 2):
                    key = f"nonexistent_key_{i}"
                    read_op_start = time.time()

                    # 模拟缓存未命中
                    await asyncio.sleep(0.01)

                    read_latency = (time.time() - read_op_start) * 1000
                    read_latencies.append(read_latency)

                total_read_time = time.time() - read_start
                read_throughput = len(read_latencies) / total_read_time
                cache_hit_rate = cache_hits / (cache_size // 2)

                # 计算统计指标
                write_latencies.sort()
                read_latencies.sort()

                metrics.extend([
                    PerformanceMetric(
                        metric_name="cache_write_latency_p50",
                        timestamp=datetime.now(),
                        value=write_latencies[len(write_latencies) // 2],
                        unit="ms",
                        component="cache",
                        test_scenario=f"size_{cache_size}",
                        metadata={'cache_size': cache_size}
                    ),
                    PerformanceMetric(
                        metric_name="cache_read_latency_p50",
                        timestamp=datetime.now(),
                        value=read_latencies[len(read_latencies) // 2],
                        unit="ms",
                        component="cache",
                        test_scenario=f"size_{cache_size}"
                    ),
                    PerformanceMetric(
                        metric_name="cache_write_throughput",
                        timestamp=datetime.now(),
                        value=write_throughput,
                        unit="ops/s",
                        component="cache",
                        test_scenario=f"size_{cache_size}"
                    ),
                    PerformanceMetric(
                        metric_name="cache_read_throughput",
                        timestamp=datetime.now(),
                        value=read_throughput,
                        unit="ops/s",
                        component="cache",
                        test_scenario=f"size_{cache_size}"
                    ),
                    PerformanceMetric(
                        metric_name="cache_hit_rate",
                        timestamp=datetime.now(),
                        value=cache_hit_rate * 100,
                        unit="percent",
                        component="cache",
                        test_scenario=f"size_{cache_size}"
                    )
                ])

                logger.info(f"Cache size: {cache_size}, "
                           f"Write P50: {write_latencies[len(write_latencies) // 2]:.2f}ms, "
                           f"Read P50: {read_latencies[len(read_latencies) // 2]:.2f}ms, "
                           f"Hit Rate: {cache_hit_rate:.2%}")

            # 计算摘要统计
            write_latencies = [m.value for m in metrics if 'write_latency' in m.metric_name]
            read_latencies = [m.value for m in metrics if 'read_latency' in m.metric_name]
            hit_rates = [m.value for m in metrics if 'hit_rate' in m.metric_name]

            summary_stats = {
                'total_tests': len(metrics),
                'avg_write_latency_ms': statistics.mean(write_latencies) if write_latencies else 0,
                'avg_read_latency_ms': statistics.mean(read_latencies) if read_latencies else 0,
                'avg_hit_rate_percent': statistics.mean(hit_rates) if hit_rates else 0,
                'performance_acceptable': all(l < self.config.cache_hit_threshold_ms for l in read_latencies) if read_latencies else False
            }

            return BenchmarkResult(
                test_name=test_name,
                start_time=start_time,
                end_time=datetime.now(),
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                success=True,
                metrics=metrics,
                summary_stats=summary_stats
            )

        except Exception as e:
            logger.error(f"Cache benchmark failed: {e}")
            return BenchmarkResult(
                test_name=test_name,
                start_time=start_time,
                end_time=datetime.now(),
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                success=False,
                metrics=metrics,
                summary_stats={},
                error_message=str(e)
            )

    async def benchmark_system_load_limits(self) -> BenchmarkResult:
        """基准测试系统负载极限"""
        test_name = "system_load_limits"
        start_time = datetime.now()
        metrics = []

        try:
            # 启动系统监控
            monitor_task = asyncio.create_task(self.system_monitor.start_monitoring())

            # 逐步增加负载直到系统达到极限
            load_levels = [10, 25, 50, 100, 200, 500, 1000]

            for load_level in load_levels:
                logger.info(f"Testing system load limit at {load_level} concurrent operations...")

                async def load_operation(op_id: int):
                    operation_start = time.time()

                    try:
                        # 模拟复合操作：向量搜索 + AI完成 + 缓存操作

                        # 1. 向量搜索
                        query_vector = [random.random() for _ in range(self.config.vector_dimensions)]
                        await asyncio.sleep(0.01)  # 模拟向量搜索延迟

                        # 2. AI完成
                        await asyncio.sleep(0.1)  # 模拟AI完成延迟

                        # 3. 缓存操作
                        await asyncio.sleep(0.001)  # 模拟缓存操作延迟

                        operation_time = (time.time() - operation_start) * 1000

                        return {
                            'op_id': op_id,
                            'success': True,
                            'latency_ms': operation_time
                        }

                    except Exception as e:
                        operation_time = (time.time() - operation_start) * 1000
                        return {
                            'op_id': op_id,
                            'success': False,
                            'latency_ms': operation_time,
                            'error': str(e)
                        }

                # 执行负载测试
                load_start = time.time()
                tasks = [load_operation(i) for i in range(load_level)]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                load_duration = time.time() - load_start

                # 分析负载测试结果
                successful_ops = [r for r in results if isinstance(r, dict) and r.get('success')]
                failed_ops = [r for r in results if not isinstance(r, dict) or not r.get('success')]

                if successful_ops:
                    latencies = [r['latency_ms'] for r in successful_ops]
                    latencies.sort()

                    success_rate = len(successful_ops) / load_level
                    throughput = len(successful_ops) / load_duration

                    metrics.extend([
                        PerformanceMetric(
                            metric_name="load_test_success_rate",
                            timestamp=datetime.now(),
                            value=success_rate * 100,
                            unit="percent",
                            component="system",
                            test_scenario=f"load_{load_level}",
                            metadata={'concurrent_operations': load_level}
                        ),
                        PerformanceMetric(
                            metric_name="load_test_latency_p95",
                            timestamp=datetime.now(),
                            value=latencies[int(len(latencies) * 0.95)],
                            unit="ms",
                            component="system",
                            test_scenario=f"load_{load_level}"
                        ),
                        PerformanceMetric(
                            metric_name="load_test_throughput",
                            timestamp=datetime.now(),
                            value=throughput,
                            unit="ops/s",
                            component="system",
                            test_scenario=f"load_{load_level}"
                        )
                    ])

                    logger.info(f"Load: {load_level}, Success Rate: {success_rate:.2%}, "
                               f"P95 Latency: {latencies[int(len(latencies) * 0.95)]:.2f}ms, "
                               f"Throughput: {throughput:.2f} ops/s")

                    # 检查系统是否达到极限
                    if success_rate < 0.95 or latencies[int(len(latencies) * 0.95)] > 5000:
                        logger.info(f"System load limit reached at {load_level} concurrent operations")
                        break

                # 短暂休息以让系统恢复
                await asyncio.sleep(2)

            # 停止系统监控
            self.system_monitor.stop_monitoring()
            monitor_task.cancel()

            # 获取系统监控摘要
            system_metrics = self.system_monitor.get_metrics_summary()

            # 计算摘要统计
            success_rates = [m.value for m in metrics if 'success_rate' in m.metric_name]
            throughputs = [m.value for m in metrics if 'throughput' in m.metric_name]

            summary_stats = {
                'max_concurrent_operations': max(load_levels[:len(success_rates)]) if success_rates else 0,
                'max_throughput_ops_per_sec': max(throughputs) if throughputs else 0,
                'avg_success_rate_percent': statistics.mean(success_rates) if success_rates else 0,
                'system_metrics': system_metrics,
                'performance_acceptable': min(success_rates) > 90 if success_rates else False
            }

            return BenchmarkResult(
                test_name=test_name,
                start_time=start_time,
                end_time=datetime.now(),
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                success=True,
                metrics=metrics,
                summary_stats=summary_stats
            )

        except Exception as e:
            logger.error(f"System load benchmark failed: {e}")
            self.system_monitor.stop_monitoring()

            return BenchmarkResult(
                test_name=test_name,
                start_time=start_time,
                end_time=datetime.now(),
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                success=False,
                metrics=metrics,
                summary_stats={},
                error_message=str(e)
            )

    def generate_performance_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        logger.info("Generating comprehensive performance report...")

        # 收集所有指标
        all_metrics = []
        for result in self.benchmark_results:
            all_metrics.extend(result.metrics)

        # 按组件分组指标
        metrics_by_component = defaultdict(list)
        for metric in all_metrics:
            metrics_by_component[metric.component].append(metric)

        # 生成组件级摘要
        component_summaries = {}
        for component, component_metrics in metrics_by_component.items():
            latency_metrics = [m for m in component_metrics if 'latency' in m.metric_name]
            throughput_metrics = [m for m in component_metrics if 'throughput' in m.metric_name]

            if latency_metrics:
                latencies = [m.value for m in latency_metrics]
                avg_latency = statistics.mean(latencies)
                p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0
            else:
                avg_latency = p95_latency = 0

            if throughput_metrics:
                throughputs = [m.value for m in throughput_metrics]
                avg_throughput = statistics.mean(throughputs)
                max_throughput = max(throughputs)
            else:
                avg_throughput = max_throughput = 0

            component_summaries[component] = {
                'total_metrics': len(component_metrics),
                'avg_latency_ms': avg_latency,
                'p95_latency_ms': p95_latency,
                'avg_throughput': avg_throughput,
                'max_throughput': max_throughput,
                'performance_grade': self._calculate_performance_grade(component, avg_latency, avg_throughput)
            }

        # 计算总体性能评分
        successful_tests = [r for r in self.benchmark_results if r.success]
        overall_success_rate = len(successful_tests) / len(self.benchmark_results) if self.benchmark_results else 0

        overall_grade = statistics.mean([
            summary['performance_grade'] for summary in component_summaries.values()
        ]) if component_summaries else 0

        # 性能建议
        recommendations = self._generate_performance_recommendations(component_summaries)

        report = {
            'report_generated_at': datetime.now().isoformat(),
            'test_configuration': {
                'vector_dimensions': self.config.vector_dimensions,
                'dataset_sizes': [self.config.small_dataset_size, self.config.medium_dataset_size, self.config.large_dataset_size],
                'concurrent_users': self.config.concurrent_users,
                'performance_thresholds': {
                    'vector_search_ms': self.config.vector_search_threshold_ms,
                    'ai_completion_ms': self.config.ai_completion_threshold_ms,
                    'cache_hit_ms': self.config.cache_hit_threshold_ms
                }
            },
            'overall_summary': {
                'total_benchmarks': len(self.benchmark_results),
                'successful_benchmarks': len(successful_tests),
                'success_rate': overall_success_rate,
                'overall_performance_grade': overall_grade,
                'total_metrics_collected': len(all_metrics)
            },
            'component_performance': component_summaries,
            'benchmark_results': [
                {
                    'test_name': r.test_name,
                    'duration_seconds': r.duration_seconds,
                    'success': r.success,
                    'summary_stats': r.summary_stats,
                    'error_message': r.error_message
                }
                for r in self.benchmark_results
            ],
            'performance_recommendations': recommendations,
            'detailed_metrics': [
                {
                    'metric_name': m.metric_name,
                    'value': m.value,
                    'unit': m.unit,
                    'component': m.component,
                    'test_scenario': m.test_scenario,
                    'timestamp': m.timestamp.isoformat()
                }
                for m in all_metrics[:100]  # 限制详细指标数量
            ]
        }

        return report

    def _calculate_performance_grade(self, component: str, avg_latency: float, avg_throughput: float) -> float:
        """计算性能评分 (0-100)"""
        if component == "pgvector":
            latency_score = max(0, 100 - (avg_latency / self.config.vector_search_threshold_ms) * 50)
            throughput_score = min(100, (avg_throughput / self.config.throughput_threshold_qps) * 50)
        elif component == "ai_model":
            latency_score = max(0, 100 - (avg_latency / self.config.ai_completion_threshold_ms) * 50)
            throughput_score = min(100, avg_throughput * 10)  # 调整AI模型吞吐量评分
        elif component == "cache":
            latency_score = max(0, 100 - (avg_latency / self.config.cache_hit_threshold_ms) * 50)
            throughput_score = min(100, avg_throughput / 100)
        else:
            latency_score = throughput_score = 50  # 默认中等评分

        return (latency_score + throughput_score) / 2

    def _generate_performance_recommendations(self, component_summaries: Dict[str, Any]) -> List[str]:
        """生成性能优化建议"""
        recommendations = []

        for component, summary in component_summaries.items():
            grade = summary['performance_grade']
            avg_latency = summary['avg_latency_ms']

            if component == "pgvector":
                if grade < 70:
                    recommendations.append(f"🔍 pgvector性能可以优化: 考虑调整索引参数或使用更高效的索引类型")
                if avg_latency > self.config.vector_search_threshold_ms:
                    recommendations.append(f"⚡ 向量搜索延迟较高 ({avg_latency:.2f}ms): 建议优化查询或增加硬件资源")

            elif component == "ai_model":
                if grade < 70:
                    recommendations.append(f"🤖 AI模型性能需要优化: 考虑负载均衡或模型缓存策略")
                if avg_latency > self.config.ai_completion_threshold_ms:
                    recommendations.append(f"🕒 AI完成延迟较高 ({avg_latency:.2f}ms): 建议使用更快的模型或优化提示词")

            elif component == "cache":
                if grade < 70:
                    recommendations.append(f"💾 缓存性能可以改善: 检查Redis配置或网络延迟")
                if avg_latency > self.config.cache_hit_threshold_ms:
                    recommendations.append(f"🚀 缓存访问延迟较高 ({avg_latency:.2f}ms): 考虑缓存预热或增加缓存容量")

        # 通用建议
        if not recommendations:
            recommendations.append("✅ 系统性能表现良好，继续监控关键指标")

        return recommendations

    async def run_all_benchmarks(self) -> Dict[str, Any]:
        """运行所有性能基准测试"""
        logger.info("Starting comprehensive performance benchmark suite...")

        suite_start_time = time.time()

        # 定义基准测试列表
        benchmarks = [
            self.benchmark_vector_search_performance,
            self.benchmark_ai_model_performance,
            self.benchmark_cache_performance,
            self.benchmark_system_load_limits
        ]

        # 逐个执行基准测试
        for benchmark_func in benchmarks:
            try:
                logger.info(f"Running benchmark: {benchmark_func.__name__}")
                result = await benchmark_func()
                self.benchmark_results.append(result)

                status = 'PASSED' if result.success else 'FAILED'
                logger.info(f"Benchmark {result.test_name}: {status} ({result.duration_seconds:.2f}s)")

            except Exception as e:
                logger.error(f"Benchmark {benchmark_func.__name__} failed with exception: {e}")

                # 创建失败结果记录
                failed_result = BenchmarkResult(
                    test_name=benchmark_func.__name__,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    duration_seconds=0,
                    success=False,
                    metrics=[],
                    summary_stats={},
                    error_message=str(e)
                )
                self.benchmark_results.append(failed_result)

        suite_duration = time.time() - suite_start_time

        # 生成综合性能报告
        performance_report = self.generate_performance_report()
        performance_report['benchmark_suite_duration_seconds'] = suite_duration

        logger.info(f"Performance benchmark suite completed in {suite_duration:.2f} seconds")

        return performance_report

    async def cleanup(self):
        """清理基准测试环境"""
        logger.info("Cleaning up performance benchmark environment...")

        # 清理测试数据
        if self.db_pool:
            async with self.db_pool.acquire() as conn:
                await conn.execute("DELETE FROM benchmark_vectors")
                await conn.execute("DROP INDEX IF EXISTS idx_benchmark_hnsw")
                await conn.execute("DROP INDEX IF EXISTS idx_benchmark_ivfflat")

        # 关闭组件
        if self.ai_manager:
            await self.ai_manager.shutdown()
        if self.cache_manager:
            await self.cache_manager.shutdown()
        if self.metrics_collector:
            await self.metrics_collector.shutdown()
        if self.db_pool:
            await self.db_pool.close()

async def main():
    """主基准测试入口"""
    config = BenchmarkConfig()
    benchmark_suite = PerformanceBenchmarkSuite(config)

    try:
        await benchmark_suite.initialize()
        performance_report = await benchmark_suite.run_all_benchmarks()

        # 保存性能报告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"/h/novellus/test_results/performance_benchmark_report_{timestamp}.json"

        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(performance_report, f, indent=2, ensure_ascii=False)

        print(f"\nPerformance benchmark report saved to: {report_file}")
        print(f"Overall performance grade: {performance_report['overall_summary']['overall_performance_grade']:.1f}/100")
        print(f"Success rate: {performance_report['overall_summary']['success_rate']:.2%}")

        # 显示主要性能指标
        print("\n=== Performance Summary ===")
        for component, summary in performance_report['component_performance'].items():
            print(f"{component.upper()}: Grade {summary['performance_grade']:.1f}/100, "
                  f"Avg Latency: {summary['avg_latency_ms']:.2f}ms, "
                  f"Max Throughput: {summary['max_throughput']:.2f}")

        # 显示优化建议
        print("\n=== Recommendations ===")
        for recommendation in performance_report['performance_recommendations']:
            print(f"  {recommendation}")

        return performance_report['overall_summary']['success_rate'] >= 0.8

    except Exception as e:
        logger.error(f"Performance benchmark suite failed: {e}")
        return False
    finally:
        await benchmark_suite.cleanup()

if __name__ == "__main__":
    asyncio.run(main())