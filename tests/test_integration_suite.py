#!/usr/bin/env python3
"""
Comprehensive Integration Test Suite
验证pgvector扩展、AI模型管理系统、语义缓存和数据库的集成协同工作
"""

import asyncio
import json
import logging
import os
import random
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
import traceback

import asyncpg
import numpy as np
import pytest
import psutil
from contextlib import asynccontextmanager

# 导入被测试的模块
import sys
sys.path.append('/h/novellus/src')

from ai.model_manager import AIModelManager, ModelConfig, ModelProvider, ModelStatus
from ai.cache_manager import CacheManager
from ai.integration import AIIntegration
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class IntegrationTestConfig:
    """集成测试配置"""
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "postgres"
    db_user: str = "postgres"
    db_password: str = "postgres"
    redis_url: str = "redis://localhost:6379"
    vector_dimensions: int = 1536
    test_scenarios: int = 10
    concurrent_users: int = 5
    semantic_cache_test_size: int = 20
    performance_threshold_ms: int = 2000
    similarity_threshold: float = 0.8

@dataclass
class IntegrationTestResult:
    """集成测试结果"""
    test_name: str
    component: str
    start_time: float
    end_time: float
    duration_ms: float
    success: bool
    data_consistency: bool = True
    performance_acceptable: bool = True
    error_message: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)

class IntegrationTestSuite:
    """集成测试套件主类"""

    def __init__(self, config: IntegrationTestConfig = None):
        self.config = config or IntegrationTestConfig()
        self.db_pool = None
        self.ai_manager = None
        self.cache_manager = None
        self.ai_integration = None
        self.test_results: List[IntegrationTestResult] = []
        self.test_data_cleanup: List[str] = []

    async def initialize(self):
        """初始化集成测试环境"""
        logger.info("Initializing integration test suite...")

        # 创建数据库连接池
        self.db_pool = await asyncpg.create_pool(
            host=self.config.db_host,
            port=self.config.db_port,
            database=self.config.db_name,
            user=self.config.db_user,
            password=self.config.db_password,
            min_size=5,
            max_size=20
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

        # 初始化AI集成组件
        self.ai_integration = AIIntegration(
            model_manager=self.ai_manager,
            cache_manager=self.cache_manager,
            db_pool=self.db_pool
        )

        # 启动所有组件
        await self.ai_manager.initialize()
        await self.cache_manager.initialize()
        await self.ai_integration.initialize()

        # 验证环境
        await self._verify_test_environment()

        logger.info("Integration test suite initialized successfully")

    async def _verify_test_environment(self):
        """验证测试环境"""
        # 验证数据库连接
        async with self.db_pool.acquire() as conn:
            # 检查pgvector扩展
            result = await conn.fetchval("SELECT COUNT(*) FROM pg_extension WHERE extname = 'vector'")
            if result == 0:
                raise Exception("pgvector extension not installed")

            # 检查必要的表
            required_tables = [
                'ai_models', 'ai_requests', 'ai_response_cache',
                'content_embeddings', 'law_chain_embeddings',
                'character_semantic_profiles', 'semantic_cache'
            ]

            for table in required_tables:
                exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM pg_tables
                        WHERE tablename = $1
                    )
                """, table)
                if not exists:
                    logger.warning(f"Table {table} does not exist, some tests may fail")

        # 验证Redis连接
        try:
            await self.cache_manager.redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")

        logger.info("Test environment verification completed")

    async def _measure_integration_test(self, test_func, test_name: str, component: str, *args, **kwargs) -> IntegrationTestResult:
        """集成测试性能测量装饰器"""
        start_time = time.time()

        try:
            result = await test_func(*args, **kwargs)
            success = True
            error_message = ""
            data_consistency = result.get('data_consistency', True) if isinstance(result, dict) else True
            performance_acceptable = result.get('performance_acceptable', True) if isinstance(result, dict) else True
            metrics = result if isinstance(result, dict) else {}
        except Exception as e:
            success = False
            error_message = str(e)
            data_consistency = False
            performance_acceptable = False
            metrics = {}
            logger.error(f"Integration test {test_name} failed: {e}")
            logger.error(traceback.format_exc())

        end_time = time.time()

        test_result = IntegrationTestResult(
            test_name=test_name,
            component=component,
            start_time=start_time,
            end_time=end_time,
            duration_ms=(end_time - start_time) * 1000,
            success=success,
            data_consistency=data_consistency,
            performance_acceptable=performance_acceptable,
            error_message=error_message,
            metrics=metrics
        )

        self.test_results.append(test_result)
        return test_result

    async def test_vector_ai_integration(self) -> Dict[str, Any]:
        """测试向量数据库与AI模型的集成"""
        async def _test():
            test_documents = [
                {
                    'content': '法则链是小说中角色获得超自然能力的方式，每条法则链都有独特的能力和限制',
                    'type': 'law_chain_concept',
                    'metadata': {'category': 'fantasy', 'power_level': 'high'}
                },
                {
                    'content': '角色通过冥想和修炼来强化与法则链的连接，提升法则链的掌控程度',
                    'type': 'training_method',
                    'metadata': {'category': 'cultivation', 'difficulty': 'medium'}
                },
                {
                    'content': '命运法则链可以预见未来的可能性，但使用时会消耗巨大的精神力',
                    'type': 'specific_chain',
                    'metadata': {'chain_type': 'destiny', 'cost': 'high'}
                }
            ]

            integration_results = []

            for doc in test_documents:
                try:
                    # 1. 使用AI生成向量
                    vector_response = await self.ai_integration.generate_embedding(
                        text=doc['content'],
                        embedding_type='content'
                    )

                    if not vector_response.get('success'):
                        integration_results.append({
                            'document': doc['content'][:50] + '...',
                            'step': 'embedding_generation',
                            'success': False,
                            'error': vector_response.get('error', 'Unknown error')
                        })
                        continue

                    embedding = vector_response['embedding']

                    # 2. 存储到向量数据库
                    async with self.db_pool.acquire() as conn:
                        doc_id = await conn.fetchval("""
                            INSERT INTO content_embeddings (
                                content_id, content_type, content_hash, content_text,
                                embedding, metadata
                            ) VALUES (
                                gen_random_uuid(), $1, $2, $3, $4, $5
                            ) RETURNING content_id
                        """, doc['type'],
                            str(hash(doc['content'])),
                            doc['content'],
                            embedding,
                            json.dumps(doc['metadata'])
                        )

                        self.test_data_cleanup.append(str(doc_id))

                    # 3. 执行相似度搜索
                    search_results = await self.ai_integration.semantic_search(
                        query_text=doc['content'],
                        content_type=doc['type'],
                        top_k=5,
                        similarity_threshold=0.7
                    )

                    # 4. 验证AI理解和响应
                    analysis_prompt = f"分析这段内容的含义和重要性：{doc['content']}"
                    ai_response = await self.ai_integration.analyze_content(
                        content=doc['content'],
                        analysis_type='semantic_understanding',
                        context=doc['metadata']
                    )

                    integration_results.append({
                        'document': doc['content'][:50] + '...',
                        'embedding_generated': len(embedding) == self.config.vector_dimensions,
                        'stored_successfully': doc_id is not None,
                        'search_results_count': len(search_results.get('results', [])),
                        'ai_analysis_success': ai_response.get('success', False),
                        'ai_analysis_quality': len(ai_response.get('analysis', '')) > 50,
                        'integration_latency_ms': sum([
                            vector_response.get('latency_ms', 0),
                            search_results.get('latency_ms', 0),
                            ai_response.get('latency_ms', 0)
                        ])
                    })

                except Exception as e:
                    integration_results.append({
                        'document': doc['content'][:50] + '...',
                        'success': False,
                        'error': str(e)
                    })

            # 分析整体集成性能
            successful_integrations = [r for r in integration_results if r.get('embedding_generated', False) and r.get('stored_successfully', False)]
            avg_latency = sum(r.get('integration_latency_ms', 0) for r in successful_integrations) / len(successful_integrations) if successful_integrations else 0

            return {
                'total_documents': len(test_documents),
                'successful_integrations': len(successful_integrations),
                'integration_success_rate': len(successful_integrations) / len(test_documents),
                'avg_integration_latency_ms': avg_latency,
                'performance_acceptable': avg_latency < self.config.performance_threshold_ms,
                'data_consistency': all(r.get('stored_successfully', False) for r in successful_integrations),
                'detailed_results': integration_results
            }

        return await self._measure_integration_test(_test, "vector_ai_integration", "ai_vector_db")

    async def test_semantic_cache_integration(self) -> Dict[str, Any]:
        """测试语义缓存与AI模型集成"""
        async def _test():
            cache_test_queries = [
                "什么是法则链？",
                "法则链的作用是什么？",
                "法则链有什么用？",  # 语义相似
                "如何获得法则链？",
                "怎样获取法则链？",  # 语义相似
                "法则链的副作用有哪些？",
                "命运法则链的能力",
                "destiny chain abilities",  # 不同语言，相似语义
                "时间法则链的限制",
                "角色如何修炼法则链？"
            ]

            cache_results = []
            semantic_hits = 0
            total_queries = len(cache_test_queries)

            for i, query in enumerate(cache_test_queries):
                try:
                    # 1. 第一次查询（构建缓存）
                    start_time = time.time()
                    first_response = await self.ai_integration.query_with_semantic_cache(
                        query=query,
                        use_ai_fallback=True,
                        cache_ttl=3600
                    )
                    first_query_time = (time.time() - start_time) * 1000

                    if not first_response.get('success'):
                        cache_results.append({
                            'query': query,
                            'first_query_success': False,
                            'error': first_response.get('error')
                        })
                        continue

                    # 2. 相同查询（应该命中缓存）
                    start_time = time.time()
                    cached_response = await self.ai_integration.query_with_semantic_cache(
                        query=query,
                        use_ai_fallback=True
                    )
                    cached_query_time = (time.time() - start_time) * 1000

                    # 3. 检查语义相似查询的缓存命中
                    similar_queries = [q for q in cache_test_queries if q != query and self._are_semantically_similar(query, q)]
                    semantic_cache_hits = 0

                    for similar_query in similar_queries:
                        start_time = time.time()
                        similar_response = await self.ai_integration.query_with_semantic_cache(
                            query=similar_query,
                            similarity_threshold=0.85
                        )
                        similar_query_time = (time.time() - start_time) * 1000

                        if similar_response.get('cache_hit') and similar_query_time < first_query_time * 0.5:
                            semantic_cache_hits += 1
                            semantic_hits += 1

                    cache_speedup = first_query_time / cached_query_time if cached_query_time > 0 else 0

                    cache_results.append({
                        'query': query,
                        'first_query_time_ms': first_query_time,
                        'cached_query_time_ms': cached_query_time,
                        'cache_speedup': cache_speedup,
                        'cache_hit_detected': cached_response.get('cache_hit', False),
                        'semantic_cache_hits': semantic_cache_hits,
                        'response_consistency': first_response.get('content') == cached_response.get('content')
                    })

                except Exception as e:
                    cache_results.append({
                        'query': query,
                        'success': False,
                        'error': str(e)
                    })

            # 分析缓存性能
            successful_tests = [r for r in cache_results if r.get('cache_hit_detected', False)]
            avg_speedup = sum(r.get('cache_speedup', 0) for r in successful_tests) / len(successful_tests) if successful_tests else 0
            cache_hit_rate = len(successful_tests) / total_queries
            semantic_cache_rate = semantic_hits / total_queries

            return {
                'total_queries': total_queries,
                'cache_hits': len(successful_tests),
                'semantic_cache_hits': semantic_hits,
                'cache_hit_rate': cache_hit_rate,
                'semantic_cache_rate': semantic_cache_rate,
                'avg_speedup_factor': avg_speedup,
                'performance_acceptable': avg_speedup > 2.0,
                'data_consistency': all(r.get('response_consistency', False) for r in successful_tests),
                'detailed_results': cache_results[:5]  # 只保留前5个详细结果
            }

        return await self._measure_integration_test(_test, "semantic_cache_integration", "cache_ai")

    def _are_semantically_similar(self, query1: str, query2: str) -> bool:
        """简单的语义相似性检查（在实际环境中会使用向量相似度）"""
        # 简化的相似性检查
        words1 = set(query1.lower().split())
        words2 = set(query2.lower().split())

        if len(words1) == 0 or len(words2) == 0:
            return False

        overlap = len(words1.intersection(words2))
        union = len(words1.union(words2))

        jaccard_similarity = overlap / union if union > 0 else 0
        return jaccard_similarity > 0.3

    async def test_concurrent_system_load(self) -> Dict[str, Any]:
        """测试并发系统负载下的集成性能"""
        async def _test():
            concurrent_users = self.config.concurrent_users
            operations_per_user = 10

            async def user_simulation(user_id: int):
                """模拟单个用户的操作序列"""
                user_operations = []
                user_start_time = time.time()

                for op_id in range(operations_per_user):
                    try:
                        operation_start = time.time()

                        # 随机选择操作类型
                        operation_type = random.choice([
                            'vector_search',
                            'ai_completion',
                            'semantic_cache',
                            'content_analysis'
                        ])

                        if operation_type == 'vector_search':
                            # 向量搜索操作
                            query = f"用户{user_id}的搜索查询{op_id}"
                            result = await self.ai_integration.semantic_search(
                                query_text=query,
                                content_type='law_chain',
                                top_k=5
                            )

                        elif operation_type == 'ai_completion':
                            # AI完成操作
                            prompt = f"请解释法则链系统的第{op_id}个概念"
                            result = await self.ai_manager.complete(
                                prompt=prompt,
                                use_cache=True
                            )

                        elif operation_type == 'semantic_cache':
                            # 语义缓存操作
                            query = f"法则链的应用场景{op_id}"
                            result = await self.ai_integration.query_with_semantic_cache(
                                query=query,
                                use_ai_fallback=True
                            )

                        elif operation_type == 'content_analysis':
                            # 内容分析操作
                            content = f"这是用户{user_id}提交的第{op_id}段内容，需要进行语义分析"
                            result = await self.ai_integration.analyze_content(
                                content=content,
                                analysis_type='comprehensive'
                            )

                        operation_time = (time.time() - operation_start) * 1000

                        user_operations.append({
                            'operation_id': op_id,
                            'operation_type': operation_type,
                            'success': result.get('success', True) if isinstance(result, dict) else True,
                            'latency_ms': operation_time,
                            'response_size': len(str(result)) if result else 0
                        })

                    except Exception as e:
                        operation_time = (time.time() - operation_start) * 1000
                        user_operations.append({
                            'operation_id': op_id,
                            'operation_type': operation_type,
                            'success': False,
                            'latency_ms': operation_time,
                            'error': str(e)
                        })

                total_user_time = (time.time() - user_start_time) * 1000

                return {
                    'user_id': user_id,
                    'total_operations': len(user_operations),
                    'successful_operations': sum(1 for op in user_operations if op['success']),
                    'total_time_ms': total_user_time,
                    'avg_operation_time_ms': total_user_time / len(user_operations) if user_operations else 0,
                    'operations': user_operations
                }

            # 启动并发用户模拟
            concurrent_start = time.time()
            user_tasks = [user_simulation(i) for i in range(concurrent_users)]
            user_results = await asyncio.gather(*user_tasks, return_exceptions=True)
            total_concurrent_time = (time.time() - concurrent_start) * 1000

            # 分析并发测试结果
            successful_users = [r for r in user_results if isinstance(r, dict)]
            failed_users = [r for r in user_results if isinstance(r, Exception)]

            if successful_users:
                total_operations = sum(r['total_operations'] for r in successful_users)
                successful_operations = sum(r['successful_operations'] for r in successful_users)
                avg_user_time = sum(r['total_time_ms'] for r in successful_users) / len(successful_users)

                # 计算延迟百分位数
                all_latencies = []
                for user in successful_users:
                    all_latencies.extend([op['latency_ms'] for op in user['operations'] if op['success']])

                all_latencies.sort()
                if all_latencies:
                    p50 = all_latencies[len(all_latencies) // 2]
                    p95 = all_latencies[int(len(all_latencies) * 0.95)]
                    p99 = all_latencies[int(len(all_latencies) * 0.99)]
                else:
                    p50 = p95 = p99 = 0

                throughput = successful_operations / (total_concurrent_time / 1000) if total_concurrent_time > 0 else 0

            else:
                total_operations = successful_operations = avg_user_time = 0
                p50 = p95 = p99 = throughput = 0

            return {
                'concurrent_users': concurrent_users,
                'operations_per_user': operations_per_user,
                'total_operations': total_operations,
                'successful_operations': successful_operations,
                'failed_users': len(failed_users),
                'success_rate': successful_operations / total_operations if total_operations > 0 else 0,
                'total_test_time_ms': total_concurrent_time,
                'avg_user_time_ms': avg_user_time,
                'throughput_ops_per_sec': throughput,
                'latency_percentiles': {
                    'p50': p50,
                    'p95': p95,
                    'p99': p99
                },
                'performance_acceptable': p95 < self.config.performance_threshold_ms and throughput > 1.0,
                'data_consistency': len(failed_users) == 0,
                'user_results_sample': successful_users[:3] if successful_users else []
            }

        return await self._measure_integration_test(_test, "concurrent_system_load", "system_wide")

    async def test_data_consistency_across_components(self) -> Dict[str, Any]:
        """测试跨组件的数据一致性"""
        async def _test():
            test_content = {
                'text': '这是一个测试法则链的综合内容，包含了复杂的语义信息和元数据',
                'metadata': {
                    'category': 'test',
                    'importance': 'high',
                    'timestamp': datetime.now().isoformat()
                }
            }

            consistency_checks = []

            try:
                # 1. 通过AI集成组件存储内容
                storage_result = await self.ai_integration.store_content_with_embedding(
                    content=test_content['text'],
                    content_type='consistency_test',
                    metadata=test_content['metadata']
                )

                if not storage_result.get('success'):
                    return {
                        'data_consistency': False,
                        'error': 'Failed to store content',
                        'details': storage_result
                    }

                content_id = storage_result['content_id']
                self.test_data_cleanup.append(content_id)

                # 2. 直接从数据库检索内容
                async with self.db_pool.acquire() as conn:
                    db_result = await conn.fetchrow("""
                        SELECT content_text, embedding, metadata
                        FROM content_embeddings
                        WHERE content_id = $1
                    """, content_id)

                consistency_checks.append({
                    'check': 'database_content_match',
                    'passed': db_result and db_result['content_text'] == test_content['text'],
                    'details': 'Content text matches between AI integration and database'
                })

                # 3. 通过向量搜索找到内容
                search_result = await self.ai_integration.semantic_search(
                    query_text=test_content['text'],
                    content_type='consistency_test',
                    top_k=1
                )

                search_found = False
                if search_result.get('success') and search_result.get('results'):
                    for result in search_result['results']:
                        if result.get('content_id') == content_id:
                            search_found = True
                            break

                consistency_checks.append({
                    'check': 'semantic_search_consistency',
                    'passed': search_found,
                    'details': f'Content found via semantic search: {search_found}'
                })

                # 4. 测试缓存一致性
                cache_key = f"test_consistency_{content_id}"
                await self.cache_manager.set_cache(
                    key=cache_key,
                    value=test_content,
                    ttl=300
                )

                cached_content = await self.cache_manager.get_cache(cache_key)

                consistency_checks.append({
                    'check': 'cache_consistency',
                    'passed': cached_content and cached_content.get('text') == test_content['text'],
                    'details': 'Cached content matches original'
                })

                # 5. 测试AI模型响应一致性
                analysis_prompt = f"分析这段内容：{test_content['text']}"

                first_analysis = await self.ai_manager.complete(
                    prompt=analysis_prompt,
                    use_cache=True
                )

                second_analysis = await self.ai_manager.complete(
                    prompt=analysis_prompt,
                    use_cache=True
                )

                ai_consistency = (
                    first_analysis.get('content') == second_analysis.get('content') or
                    abs(len(first_analysis.get('content', '')) - len(second_analysis.get('content', ''))) < 10
                )

                consistency_checks.append({
                    'check': 'ai_response_consistency',
                    'passed': ai_consistency,
                    'details': 'AI responses are consistent for identical prompts'
                })

                # 6. 验证元数据完整性
                if db_result and db_result['metadata']:
                    stored_metadata = json.loads(db_result['metadata']) if isinstance(db_result['metadata'], str) else db_result['metadata']
                    metadata_match = stored_metadata.get('category') == test_content['metadata']['category']
                else:
                    metadata_match = False

                consistency_checks.append({
                    'check': 'metadata_integrity',
                    'passed': metadata_match,
                    'details': 'Metadata preserved correctly'
                })

                # 计算总体一致性得分
                passed_checks = sum(1 for check in consistency_checks if check['passed'])
                consistency_score = passed_checks / len(consistency_checks) if consistency_checks else 0

                return {
                    'total_checks': len(consistency_checks),
                    'passed_checks': passed_checks,
                    'consistency_score': consistency_score,
                    'data_consistency': consistency_score >= 0.8,
                    'consistency_details': consistency_checks,
                    'content_id': content_id
                }

            except Exception as e:
                return {
                    'data_consistency': False,
                    'error': str(e),
                    'consistency_checks': consistency_checks
                }

        return await self._measure_integration_test(_test, "data_consistency_across_components", "data_integrity")

    async def test_error_recovery_and_resilience(self) -> Dict[str, Any]:
        """测试错误恢复和系统弹性"""
        async def _test():
            resilience_tests = []

            # 1. 测试数据库连接中断恢复
            try:
                # 模拟数据库操作失败
                original_pool = self.ai_integration.db_pool
                self.ai_integration.db_pool = None

                # 尝试执行需要数据库的操作
                try:
                    await self.ai_integration.semantic_search(
                        query_text="测试数据库连接中断",
                        content_type="resilience_test"
                    )
                    db_recovery_test = False
                except Exception:
                    db_recovery_test = True  # 预期的失败

                # 恢复连接
                self.ai_integration.db_pool = original_pool

                # 验证恢复后的操作
                recovery_result = await self.ai_integration.semantic_search(
                    query_text="测试数据库连接恢复",
                    content_type="resilience_test"
                )

                resilience_tests.append({
                    'test': 'database_connection_recovery',
                    'failure_handled': db_recovery_test,
                    'recovery_successful': recovery_result.get('success', False),
                    'passed': db_recovery_test and recovery_result.get('success', False)
                })

            except Exception as e:
                resilience_tests.append({
                    'test': 'database_connection_recovery',
                    'passed': False,
                    'error': str(e)
                })

            # 2. 测试AI模型失败转移
            try:
                # 临时禁用所有模型
                original_models = dict(self.ai_manager.models)
                for model_id in self.ai_manager.models:
                    self.ai_manager.models[model_id].status = ModelStatus.ERROR

                # 尝试AI请求
                try:
                    await self.ai_manager.complete(
                        prompt="测试模型失败转移",
                        use_cache=False
                    )
                    model_fallback_test = False
                except Exception:
                    model_fallback_test = True  # 预期的失败

                # 恢复一个模型
                first_model = next(iter(original_models.values()))
                first_model.status = ModelStatus.ACTIVE
                self.ai_manager.models[first_model.id] = first_model

                # 验证恢复后的操作
                recovery_result = await self.ai_manager.complete(
                    prompt="测试模型恢复",
                    use_cache=False
                )

                resilience_tests.append({
                    'test': 'ai_model_failover',
                    'failure_handled': model_fallback_test,
                    'recovery_successful': recovery_result.get('content') is not None,
                    'passed': model_fallback_test or recovery_result.get('content') is not None
                })

                # 恢复所有模型
                self.ai_manager.models.update(original_models)

            except Exception as e:
                resilience_tests.append({
                    'test': 'ai_model_failover',
                    'passed': False,
                    'error': str(e)
                })

            # 3. 测试缓存失败降级
            try:
                # 模拟缓存不可用
                original_redis = self.cache_manager.redis_client
                self.cache_manager.redis_client = None

                # 执行需要缓存的操作
                cache_fallback_result = await self.ai_integration.query_with_semantic_cache(
                    query="测试缓存失败降级",
                    use_ai_fallback=True
                )

                # 恢复缓存
                self.cache_manager.redis_client = original_redis

                resilience_tests.append({
                    'test': 'cache_failure_degradation',
                    'fallback_successful': cache_fallback_result.get('success', False),
                    'ai_fallback_used': not cache_fallback_result.get('cache_hit', True),
                    'passed': cache_fallback_result.get('success', False)
                })

            except Exception as e:
                resilience_tests.append({
                    'test': 'cache_failure_degradation',
                    'passed': False,
                    'error': str(e)
                })

            # 4. 测试高负载下的性能降级
            try:
                high_load_start = time.time()
                high_load_tasks = []

                # 创建高负载
                for i in range(20):
                    task = self.ai_integration.semantic_search(
                        query_text=f"高负载测试查询{i}",
                        content_type="load_test"
                    )
                    high_load_tasks.append(task)

                # 执行所有任务
                high_load_results = await asyncio.gather(*high_load_tasks, return_exceptions=True)
                high_load_time = (time.time() - high_load_start) * 1000

                successful_results = [r for r in high_load_results if isinstance(r, dict) and r.get('success')]
                success_rate = len(successful_results) / len(high_load_tasks)

                resilience_tests.append({
                    'test': 'high_load_performance',
                    'total_tasks': len(high_load_tasks),
                    'successful_tasks': len(successful_results),
                    'success_rate': success_rate,
                    'total_time_ms': high_load_time,
                    'passed': success_rate > 0.8 and high_load_time < self.config.performance_threshold_ms * 2
                })

            except Exception as e:
                resilience_tests.append({
                    'test': 'high_load_performance',
                    'passed': False,
                    'error': str(e)
                })

            # 计算总体弹性得分
            passed_tests = sum(1 for test in resilience_tests if test.get('passed', False))
            resilience_score = passed_tests / len(resilience_tests) if resilience_tests else 0

            return {
                'total_resilience_tests': len(resilience_tests),
                'passed_tests': passed_tests,
                'resilience_score': resilience_score,
                'performance_acceptable': resilience_score >= 0.75,
                'data_consistency': all(test.get('passed', False) for test in resilience_tests),
                'test_details': resilience_tests
            }

        return await self._measure_integration_test(_test, "error_recovery_and_resilience", "system_resilience")

    async def run_all_integration_tests(self) -> Dict[str, Any]:
        """运行所有集成测试"""
        logger.info("Starting comprehensive integration test suite...")

        test_suite_start = time.time()

        # 定义集成测试列表
        integration_tests = [
            self.test_vector_ai_integration,
            self.test_semantic_cache_integration,
            self.test_concurrent_system_load,
            self.test_data_consistency_across_components,
            self.test_error_recovery_and_resilience
        ]

        all_results = {}

        for test_func in integration_tests:
            try:
                logger.info(f"Running integration test: {test_func.__name__}")
                result = await test_func()

                all_results[result.test_name] = {
                    'success': result.success,
                    'duration_ms': result.duration_ms,
                    'data_consistency': result.data_consistency,
                    'performance_acceptable': result.performance_acceptable,
                    'component': result.component,
                    'metrics': result.metrics,
                    'error': result.error_message
                }

                status = 'PASSED' if result.success else 'FAILED'
                logger.info(f"Integration test {result.test_name}: {status} ({result.duration_ms:.2f}ms)")

            except Exception as e:
                logger.error(f"Integration test {test_func.__name__} failed with exception: {e}")
                all_results[test_func.__name__] = {
                    'success': False,
                    'duration_ms': 0,
                    'data_consistency': False,
                    'performance_acceptable': False,
                    'component': 'unknown',
                    'metrics': {},
                    'error': str(e)
                }

        test_suite_duration = (time.time() - test_suite_start) * 1000

        # 计算总体统计
        total_tests = len(all_results)
        passed_tests = sum(1 for r in all_results.values() if r['success'])
        data_consistent_tests = sum(1 for r in all_results.values() if r['data_consistency'])
        performance_acceptable_tests = sum(1 for r in all_results.values() if r['performance_acceptable'])

        summary = {
            'test_suite': 'comprehensive_integration',
            'total_duration_ms': test_suite_duration,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': passed_tests / total_tests if total_tests > 0 else 0,
            'data_consistency_rate': data_consistent_tests / total_tests if total_tests > 0 else 0,
            'performance_acceptable_rate': performance_acceptable_tests / total_tests if total_tests > 0 else 0,
            'timestamp': datetime.now().isoformat(),
            'test_configuration': {
                'db_host': self.config.db_host,
                'vector_dimensions': self.config.vector_dimensions,
                'concurrent_users': self.config.concurrent_users,
                'performance_threshold_ms': self.config.performance_threshold_ms
            },
            'test_results': all_results,
            'overall_health': {
                'functional': passed_tests / total_tests if total_tests > 0 else 0,
                'data_integrity': data_consistent_tests / total_tests if total_tests > 0 else 0,
                'performance': performance_acceptable_tests / total_tests if total_tests > 0 else 0
            }
        }

        logger.info(f"Integration test suite completed: {passed_tests}/{total_tests} tests passed")
        return summary

    async def cleanup(self):
        """清理集成测试环境"""
        logger.info("Cleaning up integration test environment...")

        # 清理测试数据
        if self.db_pool:
            async with self.db_pool.acquire() as conn:
                for content_id in self.test_data_cleanup:
                    try:
                        await conn.execute("""
                            DELETE FROM content_embeddings WHERE content_id = $1
                        """, content_id)
                    except Exception as e:
                        logger.warning(f"Failed to cleanup test data {content_id}: {e}")

        # 关闭组件
        if self.ai_integration:
            await self.ai_integration.shutdown()
        if self.ai_manager:
            await self.ai_manager.shutdown()
        if self.cache_manager:
            await self.cache_manager.shutdown()
        if self.db_pool:
            await self.db_pool.close()

async def main():
    """主测试入口"""
    config = IntegrationTestConfig()
    test_suite = IntegrationTestSuite(config)

    try:
        await test_suite.initialize()
        results = await test_suite.run_all_integration_tests()

        # 保存测试结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"/h/novellus/test_results/integration_test_results_{timestamp}.json"

        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\nIntegration test results saved to: {results_file}")
        print(f"Overall success rate: {results['success_rate']:.2%}")
        print(f"Data consistency rate: {results['data_consistency_rate']:.2%}")
        print(f"Performance acceptable rate: {results['performance_acceptable_rate']:.2%}")

        return results['success_rate'] >= 0.8

    except Exception as e:
        logger.error(f"Integration test suite failed: {e}")
        return False
    finally:
        await test_suite.cleanup()

if __name__ == "__main__":
    asyncio.run(main())