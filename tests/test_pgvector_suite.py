#!/usr/bin/env python3
"""
Comprehensive pgvector Extension Test Suite
验证pgvector扩展和向量数据库功能的完整测试套件
"""

import asyncio
import json
import logging
import os
import random
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import asyncpg
import numpy as np
import pytest
import psutil
from dataclasses import dataclass
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TestConfig:
    """测试配置"""
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "postgres"
    db_user: str = "postgres"
    db_password: str = "postgres"
    vector_dimensions: int = 1536
    test_batch_size: int = 100
    performance_test_size: int = 1000
    similarity_threshold: float = 0.8
    max_concurrent_connections: int = 10

@dataclass
class TestMetrics:
    """测试指标"""
    test_name: str
    start_time: float
    end_time: float
    duration_ms: float
    success: bool
    rows_processed: int = 0
    vectors_processed: int = 0
    memory_usage_mb: float = 0
    cpu_usage_percent: float = 0
    error_message: str = ""
    additional_metrics: Dict[str, Any] = None

    def __post_init__(self):
        if self.additional_metrics is None:
            self.additional_metrics = {}

class PgvectorTestSuite:
    """pgvector扩展测试套件主类"""

    def __init__(self, config: TestConfig = None):
        self.config = config or TestConfig()
        self.pool = None
        self.test_results: List[TestMetrics] = []
        self.test_data_ids: List[str] = []

    async def initialize(self):
        """初始化测试环境"""
        logger.info("Initializing pgvector test suite...")

        # 创建连接池
        self.pool = await asyncpg.create_pool(
            host=self.config.db_host,
            port=self.config.db_port,
            database=self.config.db_name,
            user=self.config.db_user,
            password=self.config.db_password,
            min_size=2,
            max_size=self.config.max_concurrent_connections
        )

        # 验证扩展安装
        await self._verify_extension_installation()

        # 创建测试表
        await self._create_test_tables()

        logger.info("pgvector test suite initialized successfully")

    async def cleanup(self):
        """清理测试环境"""
        logger.info("Cleaning up test environment...")

        if self.pool:
            await self._cleanup_test_data()
            await self.pool.close()

    @asynccontextmanager
    async def get_connection(self):
        """获取数据库连接的上下文管理器"""
        async with self.pool.acquire() as conn:
            yield conn

    async def _measure_performance(self, test_func, test_name: str, *args, **kwargs) -> TestMetrics:
        """性能测量装饰器"""
        # 记录开始时的系统资源
        process = psutil.Process()
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        start_cpu = process.cpu_percent()
        start_time = time.time()

        try:
            result = await test_func(*args, **kwargs)
            success = True
            error_message = ""
        except Exception as e:
            result = None
            success = False
            error_message = str(e)
            logger.error(f"Test {test_name} failed: {e}")

        # 记录结束时的系统资源
        end_time = time.time()
        end_memory = process.memory_info().rss / 1024 / 1024  # MB
        end_cpu = process.cpu_percent()

        metrics = TestMetrics(
            test_name=test_name,
            start_time=start_time,
            end_time=end_time,
            duration_ms=(end_time - start_time) * 1000,
            success=success,
            memory_usage_mb=end_memory - start_memory,
            cpu_usage_percent=max(start_cpu, end_cpu),
            error_message=error_message,
            additional_metrics=result if isinstance(result, dict) else {}
        )

        self.test_results.append(metrics)
        return metrics

    async def _verify_extension_installation(self):
        """验证pgvector扩展安装和配置"""
        logger.info("Verifying pgvector extension installation...")

        async with self.get_connection() as conn:
            # 检查扩展是否安装
            extension_query = """
                SELECT name, installed_version, default_version
                FROM pg_available_extensions
                WHERE name = 'vector'
            """
            extension_info = await conn.fetch(extension_query)

            if not extension_info:
                raise Exception("pgvector extension is not available")

            # 检查扩展是否启用
            enabled_query = """
                SELECT extname, extversion
                FROM pg_extension
                WHERE extname = 'vector'
            """
            enabled_info = await conn.fetch(enabled_query)

            if not enabled_info:
                # 尝试启用扩展
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
                logger.info("pgvector extension enabled")
            else:
                logger.info(f"pgvector extension already enabled, version: {enabled_info[0]['extversion']}")

            # 验证向量操作符
            operators_query = """
                SELECT oprname, oprleft::regtype, oprright::regtype, oprresult::regtype
                FROM pg_operator
                WHERE oprnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
                AND oprname IN ('<->', '<#>', '<=>')
            """
            operators = await conn.fetch(operators_query)

            if len(operators) < 3:
                raise Exception("pgvector operators not properly installed")

            logger.info(f"pgvector extension verified: {len(operators)} operators available")

    async def _create_test_tables(self):
        """创建测试表结构"""
        logger.info("Creating test tables...")

        async with self.get_connection() as conn:
            # 创建向量测试表
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS test_vectors (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    content_type VARCHAR(50) NOT NULL,
                    content_text TEXT,
                    embedding vector({self.config.vector_dimensions}),
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 创建索引测试表
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS test_vector_index (
                    id SERIAL PRIMARY KEY,
                    category VARCHAR(100),
                    embedding vector({self.config.vector_dimensions}),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 创建性能测试表
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS test_performance_vectors (
                    id BIGSERIAL PRIMARY KEY,
                    batch_id INTEGER,
                    embedding vector({self.config.vector_dimensions}),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            logger.info("Test tables created successfully")

    async def _cleanup_test_data(self):
        """清理测试数据"""
        logger.info("Cleaning up test data...")

        async with self.get_connection() as conn:
            await conn.execute("DELETE FROM test_vectors")
            await conn.execute("DELETE FROM test_vector_index")
            await conn.execute("DELETE FROM test_performance_vectors")

            # 删除测试表
            await conn.execute("DROP TABLE IF EXISTS test_vectors CASCADE")
            await conn.execute("DROP TABLE IF EXISTS test_vector_index CASCADE")
            await conn.execute("DROP TABLE IF EXISTS test_performance_vectors CASCADE")

    def _generate_random_vector(self, dimensions: int = None) -> List[float]:
        """生成随机向量"""
        dims = dimensions or self.config.vector_dimensions
        return [random.random() for _ in range(dims)]

    def _generate_similar_vector(self, base_vector: List[float], similarity: float = 0.9) -> List[float]:
        """生成与基础向量相似的向量"""
        noise_strength = 1 - similarity
        return [
            base_val + random.uniform(-noise_strength, noise_strength) * 0.1
            for base_val in base_vector
        ]

    async def test_basic_vector_operations(self) -> Dict[str, Any]:
        """测试基础向量操作"""
        async def _test():
            test_vectors = []
            async with self.get_connection() as conn:
                # 插入测试向量
                base_vector = self._generate_random_vector()
                similar_vector = self._generate_similar_vector(base_vector, 0.95)
                different_vector = self._generate_random_vector()

                vectors_data = [
                    ('base', 'Base vector for similarity testing', base_vector, {'test': 'base'}),
                    ('similar', 'Similar vector for testing', similar_vector, {'test': 'similar'}),
                    ('different', 'Different vector for testing', different_vector, {'test': 'different'})
                ]

                for content_type, content_text, embedding, metadata in vectors_data:
                    vector_id = await conn.fetchval("""
                        INSERT INTO test_vectors (content_type, content_text, embedding, metadata)
                        VALUES ($1, $2, $3, $4)
                        RETURNING id
                    """, content_type, content_text, embedding, json.dumps(metadata))
                    test_vectors.append(vector_id)
                    self.test_data_ids.append(str(vector_id))

                # 测试向量检索
                retrieved = await conn.fetch("""
                    SELECT id, content_type, embedding
                    FROM test_vectors
                    WHERE content_type = 'base'
                """)

                if not retrieved:
                    raise Exception("Failed to retrieve inserted vector")

                # 测试向量运算
                distances = await conn.fetch("""
                    SELECT
                        content_type,
                        embedding <-> $1 as l2_distance,
                        embedding <#> $1 as negative_inner_product,
                        1 - (embedding <=> $1) as cosine_similarity
                    FROM test_vectors
                    ORDER BY embedding <-> $1
                """, base_vector)

                # 验证相似度排序
                if len(distances) < 3:
                    raise Exception("Insufficient test vectors for similarity testing")

                # base向量应该最相似（距离最小）
                if distances[0]['content_type'] != 'base':
                    raise Exception("Base vector should be most similar to itself")

                return {
                    'vectors_inserted': len(test_vectors),
                    'similarity_results': [
                        {
                            'type': row['content_type'],
                            'l2_distance': float(row['l2_distance']),
                            'cosine_similarity': float(row['cosine_similarity'])
                        }
                        for row in distances
                    ],
                    'test_passed': True
                }

        return await self._measure_performance(_test, "basic_vector_operations")

    async def test_vector_indexing(self) -> Dict[str, Any]:
        """测试向量索引性能"""
        async def _test():
            async with self.get_connection() as conn:
                # 插入大量向量数据用于索引测试
                batch_size = 100
                total_vectors = 1000

                for batch in range(0, total_vectors, batch_size):
                    vectors_batch = []
                    for i in range(batch_size):
                        if batch + i >= total_vectors:
                            break
                        vectors_batch.append((
                            f'category_{(batch + i) % 10}',
                            self._generate_random_vector()
                        ))

                    await conn.executemany("""
                        INSERT INTO test_vector_index (category, embedding)
                        VALUES ($1, $2)
                    """, vectors_batch)

                # 测试无索引时的查询性能
                query_vector = self._generate_random_vector()

                start_time = time.time()
                no_index_results = await conn.fetch("""
                    SELECT id, category, embedding <-> $1 as distance
                    FROM test_vector_index
                    ORDER BY embedding <-> $1
                    LIMIT 10
                """, query_vector)
                no_index_time = (time.time() - start_time) * 1000

                # 创建HNSW索引
                await conn.execute("""
                    CREATE INDEX CONCURRENTLY test_vector_hnsw_idx
                    ON test_vector_index
                    USING hnsw (embedding vector_l2_ops)
                """)

                # 测试有索引时的查询性能
                start_time = time.time()
                with_index_results = await conn.fetch("""
                    SELECT id, category, embedding <-> $1 as distance
                    FROM test_vector_index
                    ORDER BY embedding <-> $1
                    LIMIT 10
                """, query_vector)
                with_index_time = (time.time() - start_time) * 1000

                # 创建IVFFlat索引进行比较
                await conn.execute("DROP INDEX test_vector_hnsw_idx")
                await conn.execute("""
                    CREATE INDEX test_vector_ivfflat_idx
                    ON test_vector_index
                    USING ivfflat (embedding vector_l2_ops)
                    WITH (lists = 100)
                """)

                start_time = time.time()
                ivfflat_results = await conn.fetch("""
                    SELECT id, category, embedding <-> $1 as distance
                    FROM test_vector_index
                    ORDER BY embedding <-> $1
                    LIMIT 10
                """, query_vector)
                ivfflat_time = (time.time() - start_time) * 1000

                return {
                    'vectors_indexed': total_vectors,
                    'no_index_time_ms': no_index_time,
                    'hnsw_index_time_ms': with_index_time,
                    'ivfflat_index_time_ms': ivfflat_time,
                    'performance_improvement': {
                        'hnsw_speedup': no_index_time / with_index_time if with_index_time > 0 else 0,
                        'ivfflat_speedup': no_index_time / ivfflat_time if ivfflat_time > 0 else 0
                    },
                    'results_consistent': len(no_index_results) == len(with_index_results) == len(ivfflat_results)
                }

        return await self._measure_performance(_test, "vector_indexing")

    async def test_similarity_search_accuracy(self) -> Dict[str, Any]:
        """测试相似度搜索准确性"""
        async def _test():
            async with self.get_connection() as conn:
                # 创建已知相似度的向量集合
                base_vectors = []
                similar_groups = []

                # 生成5个基础向量组，每组有1个基础向量和4个相似向量
                for group_id in range(5):
                    base_vector = self._generate_random_vector()
                    base_vectors.append(base_vector)

                    group_vectors = [base_vector]

                    # 生成不同相似度的向量
                    similarities = [0.95, 0.90, 0.85, 0.80]
                    for sim in similarities:
                        similar_vector = self._generate_similar_vector(base_vector, sim)
                        group_vectors.append(similar_vector)

                    similar_groups.append(group_vectors)

                # 插入所有向量
                all_vectors = []
                for group_id, group_vectors in enumerate(similar_groups):
                    for vector_id, vector in enumerate(group_vectors):
                        all_vectors.append((f'group_{group_id}', f'vector_{vector_id}', vector))

                await conn.executemany("""
                    INSERT INTO test_vectors (content_type, content_text, embedding)
                    VALUES ($1, $2, $3)
                """, all_vectors)

                # 测试每个基础向量的搜索准确性
                accuracy_results = []

                for group_id, base_vector in enumerate(base_vectors):
                    # 搜索最相似的向量
                    search_results = await conn.fetch("""
                        SELECT
                            content_type,
                            content_text,
                            1 - (embedding <=> $1) as cosine_similarity,
                            embedding <-> $1 as l2_distance
                        FROM test_vectors
                        WHERE content_type = $2
                        ORDER BY embedding <=> $1
                        LIMIT 5
                    """, base_vector, f'group_{group_id}')

                    # 验证结果排序是否正确（相似度递减）
                    similarities = [float(r['cosine_similarity']) for r in search_results]
                    is_sorted = all(similarities[i] >= similarities[i+1] for i in range(len(similarities)-1))

                    # 计算平均相似度
                    avg_similarity = sum(similarities) / len(similarities)

                    accuracy_results.append({
                        'group_id': group_id,
                        'results_count': len(search_results),
                        'properly_sorted': is_sorted,
                        'avg_similarity': avg_similarity,
                        'top_similarity': similarities[0] if similarities else 0,
                        'similarities': similarities
                    })

                # 计算总体准确性指标
                total_groups = len(accuracy_results)
                properly_sorted_count = sum(1 for r in accuracy_results if r['properly_sorted'])
                overall_accuracy = properly_sorted_count / total_groups if total_groups > 0 else 0

                return {
                    'test_groups': total_groups,
                    'vectors_per_group': 5,
                    'total_vectors': len(all_vectors),
                    'properly_sorted_groups': properly_sorted_count,
                    'overall_accuracy': overall_accuracy,
                    'group_results': accuracy_results,
                    'avg_top_similarity': sum(r['top_similarity'] for r in accuracy_results) / total_groups
                }

        return await self._measure_performance(_test, "similarity_search_accuracy")

    async def test_concurrent_operations(self) -> Dict[str, Any]:
        """测试并发操作性能"""
        async def _test():
            concurrent_tasks = []
            results = {}

            async def insert_vectors_task(task_id: int, count: int):
                async with self.get_connection() as conn:
                    start_time = time.time()
                    for i in range(count):
                        vector = self._generate_random_vector()
                        await conn.execute("""
                            INSERT INTO test_vectors (content_type, content_text, embedding)
                            VALUES ($1, $2, $3)
                        """, f'concurrent_{task_id}', f'Task {task_id} Vector {i}', vector)

                    duration = (time.time() - start_time) * 1000
                    return {
                        'task_id': task_id,
                        'vectors_inserted': count,
                        'duration_ms': duration,
                        'vectors_per_second': count / (duration / 1000) if duration > 0 else 0
                    }

            async def search_vectors_task(task_id: int, queries: int):
                async with self.get_connection() as conn:
                    start_time = time.time()
                    total_results = 0

                    for i in range(queries):
                        query_vector = self._generate_random_vector()
                        results = await conn.fetch("""
                            SELECT id, content_type
                            FROM test_vectors
                            ORDER BY embedding <-> $1
                            LIMIT 5
                        """, query_vector)
                        total_results += len(results)

                    duration = (time.time() - start_time) * 1000
                    return {
                        'task_id': task_id,
                        'queries_executed': queries,
                        'total_results': total_results,
                        'duration_ms': duration,
                        'queries_per_second': queries / (duration / 1000) if duration > 0 else 0
                    }

            # 启动并发插入任务
            for i in range(5):
                task = insert_vectors_task(i, 20)
                concurrent_tasks.append(task)

            # 启动并发搜索任务
            for i in range(3):
                task = search_vectors_task(i + 5, 10)
                concurrent_tasks.append(task)

            # 执行所有并发任务
            start_time = time.time()
            task_results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
            total_duration = (time.time() - start_time) * 1000

            # 分析结果
            insert_results = []
            search_results = []
            errors = []

            for result in task_results:
                if isinstance(result, Exception):
                    errors.append(str(result))
                elif 'vectors_inserted' in result:
                    insert_results.append(result)
                elif 'queries_executed' in result:
                    search_results.append(result)

            return {
                'total_duration_ms': total_duration,
                'concurrent_tasks': len(concurrent_tasks),
                'successful_tasks': len(insert_results) + len(search_results),
                'failed_tasks': len(errors),
                'insert_tasks': len(insert_results),
                'search_tasks': len(search_results),
                'avg_insert_speed': sum(r['vectors_per_second'] for r in insert_results) / len(insert_results) if insert_results else 0,
                'avg_search_speed': sum(r['queries_per_second'] for r in search_results) / len(search_results) if search_results else 0,
                'errors': errors,
                'task_details': {
                    'inserts': insert_results,
                    'searches': search_results
                }
            }

        return await self._measure_performance(_test, "concurrent_operations")

    async def test_large_dataset_performance(self) -> Dict[str, Any]:
        """测试大数据集性能"""
        async def _test():
            async with self.get_connection() as conn:
                # 批量插入大量数据
                total_vectors = self.config.performance_test_size
                batch_size = 100

                insert_start = time.time()

                for batch_id in range(0, total_vectors, batch_size):
                    vectors_batch = []
                    batch_end = min(batch_id + batch_size, total_vectors)

                    for i in range(batch_id, batch_end):
                        vector = self._generate_random_vector()
                        vectors_batch.append((batch_id // batch_size, vector))

                    await conn.executemany("""
                        INSERT INTO test_performance_vectors (batch_id, embedding)
                        VALUES ($1, $2)
                    """, vectors_batch)

                insert_duration = (time.time() - insert_start) * 1000

                # 测试搜索性能
                search_queries = 100
                query_vectors = [self._generate_random_vector() for _ in range(search_queries)]

                search_start = time.time()

                for query_vector in query_vectors:
                    await conn.fetch("""
                        SELECT id, batch_id
                        FROM test_performance_vectors
                        ORDER BY embedding <-> $1
                        LIMIT 10
                    """, query_vector)

                search_duration = (time.time() - search_start) * 1000

                # 获取数据库统计信息
                stats = await conn.fetchrow("""
                    SELECT
                        COUNT(*) as total_vectors,
                        pg_size_pretty(pg_total_relation_size('test_performance_vectors')) as table_size
                    FROM test_performance_vectors
                """)

                return {
                    'vectors_inserted': total_vectors,
                    'insert_duration_ms': insert_duration,
                    'insert_speed_vectors_per_sec': total_vectors / (insert_duration / 1000),
                    'search_queries': search_queries,
                    'search_duration_ms': search_duration,
                    'search_speed_queries_per_sec': search_queries / (search_duration / 1000),
                    'avg_query_time_ms': search_duration / search_queries,
                    'table_size': stats['table_size'],
                    'performance_ratio': search_duration / insert_duration
                }

        return await self._measure_performance(_test, "large_dataset_performance")

    async def test_vector_data_integrity(self) -> Dict[str, Any]:
        """测试向量数据完整性"""
        async def _test():
            async with self.get_connection() as conn:
                test_vectors = []
                integrity_results = []

                # 生成不同类型的测试向量
                test_cases = [
                    ('normal', self._generate_random_vector()),
                    ('zeros', [0.0] * self.config.vector_dimensions),
                    ('ones', [1.0] * self.config.vector_dimensions),
                    ('negative', [-1.0] * self.config.vector_dimensions),
                    ('mixed', [random.choice([-1, 0, 1]) for _ in range(self.config.vector_dimensions)])
                ]

                # 插入测试向量
                for case_name, vector in test_cases:
                    vector_id = await conn.fetchval("""
                        INSERT INTO test_vectors (content_type, content_text, embedding)
                        VALUES ($1, $2, $3)
                        RETURNING id
                    """, case_name, f'Test case: {case_name}', vector)

                    test_vectors.append((vector_id, case_name, vector))

                # 验证数据完整性
                for vector_id, case_name, original_vector in test_vectors:
                    # 检索向量
                    retrieved = await conn.fetchrow("""
                        SELECT content_type, embedding
                        FROM test_vectors
                        WHERE id = $1
                    """, vector_id)

                    if not retrieved:
                        integrity_results.append({
                            'case': case_name,
                            'status': 'FAILED',
                            'error': 'Vector not found'
                        })
                        continue

                    retrieved_vector = retrieved['embedding']

                    # 比较向量值
                    if len(retrieved_vector) != len(original_vector):
                        integrity_results.append({
                            'case': case_name,
                            'status': 'FAILED',
                            'error': f'Dimension mismatch: {len(retrieved_vector)} vs {len(original_vector)}'
                        })
                        continue

                    # 检查数值精度
                    max_diff = max(abs(a - b) for a, b in zip(original_vector, retrieved_vector))

                    if max_diff > 1e-6:  # 允许微小的浮点误差
                        integrity_results.append({
                            'case': case_name,
                            'status': 'FAILED',
                            'error': f'Values differ by {max_diff}'
                        })
                        continue

                    integrity_results.append({
                        'case': case_name,
                        'status': 'PASSED',
                        'max_difference': max_diff
                    })

                # 测试边界条件
                boundary_tests = []

                # 测试空向量处理
                try:
                    await conn.execute("""
                        INSERT INTO test_vectors (content_type, content_text, embedding)
                        VALUES ($1, $2, $3)
                    """, 'empty_test', 'Empty vector test', [])
                    boundary_tests.append({'test': 'empty_vector', 'result': 'UNEXPECTED_SUCCESS'})
                except Exception as e:
                    boundary_tests.append({'test': 'empty_vector', 'result': 'EXPECTED_FAILURE', 'error': str(e)})

                # 测试维度不匹配
                try:
                    wrong_dimension_vector = [1.0] * (self.config.vector_dimensions + 1)
                    await conn.execute("""
                        INSERT INTO test_vectors (content_type, content_text, embedding)
                        VALUES ($1, $2, $3)
                    """, 'wrong_dim_test', 'Wrong dimension test', wrong_dimension_vector)
                    boundary_tests.append({'test': 'wrong_dimension', 'result': 'UNEXPECTED_SUCCESS'})
                except Exception as e:
                    boundary_tests.append({'test': 'wrong_dimension', 'result': 'EXPECTED_FAILURE', 'error': str(e)})

                passed_tests = sum(1 for r in integrity_results if r['status'] == 'PASSED')
                total_tests = len(integrity_results)

                return {
                    'total_integrity_tests': total_tests,
                    'passed_tests': passed_tests,
                    'failed_tests': total_tests - passed_tests,
                    'success_rate': passed_tests / total_tests if total_tests > 0 else 0,
                    'test_details': integrity_results,
                    'boundary_tests': boundary_tests,
                    'all_tests_passed': passed_tests == total_tests
                }

        return await self._measure_performance(_test, "vector_data_integrity")

    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        logger.info("Starting comprehensive pgvector test suite...")

        test_suite_start = time.time()

        # 运行所有测试
        tests = [
            self.test_basic_vector_operations,
            self.test_vector_indexing,
            self.test_similarity_search_accuracy,
            self.test_concurrent_operations,
            self.test_large_dataset_performance,
            self.test_vector_data_integrity
        ]

        all_results = {}
        for test_func in tests:
            try:
                result = await test_func()
                all_results[result.test_name] = {
                    'success': result.success,
                    'duration_ms': result.duration_ms,
                    'metrics': result.additional_metrics,
                    'error': result.error_message
                }
                logger.info(f"Test {result.test_name}: {'PASSED' if result.success else 'FAILED'} ({result.duration_ms:.2f}ms)")
            except Exception as e:
                logger.error(f"Test {test_func.__name__} failed with exception: {e}")
                all_results[test_func.__name__] = {
                    'success': False,
                    'duration_ms': 0,
                    'metrics': {},
                    'error': str(e)
                }

        test_suite_duration = (time.time() - test_suite_start) * 1000

        # 计算总体统计
        total_tests = len(all_results)
        passed_tests = sum(1 for r in all_results.values() if r['success'])

        summary = {
            'test_suite': 'pgvector_comprehensive',
            'total_duration_ms': test_suite_duration,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': passed_tests / total_tests if total_tests > 0 else 0,
            'timestamp': datetime.now().isoformat(),
            'test_results': all_results,
            'test_configuration': {
                'db_host': self.config.db_host,
                'db_port': self.config.db_port,
                'vector_dimensions': self.config.vector_dimensions,
                'performance_test_size': self.config.performance_test_size
            }
        }

        logger.info(f"pgvector test suite completed: {passed_tests}/{total_tests} tests passed")
        return summary

async def main():
    """主测试入口"""
    config = TestConfig()
    test_suite = PgvectorTestSuite(config)

    try:
        await test_suite.initialize()
        results = await test_suite.run_all_tests()

        # 保存测试结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"/h/novellus/test_results/pgvector_test_results_{timestamp}.json"

        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\nTest results saved to: {results_file}")
        print(f"Overall success rate: {results['success_rate']:.2%}")

        return results['success_rate'] == 1.0

    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        return False
    finally:
        await test_suite.cleanup()

if __name__ == "__main__":
    asyncio.run(main())