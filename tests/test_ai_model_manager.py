#!/usr/bin/env python3
"""
AI Model Manager Test Framework
AI模型管理系统的综合测试框架，验证多模型支持、负载均衡、缓存机制等功能
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
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import dataclass, field
import traceback

import pytest
import psutil
import aiohttp
import redis.asyncio as redis
from contextlib import asynccontextmanager

# 导入被测试的模块
import sys
sys.path.append('/h/novellus/src')

from ai.model_manager import AIModelManager, ModelConfig, ModelProvider, ModelStatus, RequestStatus
from ai.cache_manager import CacheManager
from ai.metrics_collector import MetricsCollector
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AITestConfig:
    """AI测试配置"""
    test_db_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"
    test_redis_url: str = "redis://localhost:6379/1"
    mock_api_responses: bool = True
    test_timeout: int = 30
    concurrent_requests: int = 10
    load_test_requests: int = 100
    cache_test_size: int = 50
    model_health_check_interval: int = 5

@dataclass
class ModelTestMetrics:
    """模型测试指标"""
    model_id: str
    test_name: str
    start_time: float
    end_time: float
    duration_ms: float
    success: bool
    requests_sent: int = 0
    responses_received: int = 0
    cached_responses: int = 0
    errors: List[str] = field(default_factory=list)
    latency_p50: float = 0
    latency_p95: float = 0
    latency_p99: float = 0
    throughput_rps: float = 0
    memory_usage_mb: float = 0
    additional_data: Dict[str, Any] = field(default_factory=dict)

class MockAPIClient:
    """模拟API客户端"""

    def __init__(self, provider: ModelProvider, latency_ms: int = 100, error_rate: float = 0.0):
        self.provider = provider
        self.latency_ms = latency_ms
        self.error_rate = error_rate
        self.request_count = 0

    async def simulate_request(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """模拟API请求"""
        self.request_count += 1

        # 模拟延迟
        await asyncio.sleep(self.latency_ms / 1000)

        # 模拟错误
        if random.random() < self.error_rate:
            raise Exception(f"Simulated {self.provider} API error")

        # 模拟响应
        response_text = f"Mock response from {self.provider} for: {prompt[:50]}..."
        tokens_used = len(prompt.split()) + len(response_text.split())

        return {
            "content": response_text,
            "model": f"mock-{self.provider}",
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(response_text.split()),
                "total_tokens": tokens_used
            },
            "finish_reason": "stop"
        }

class AIModelManagerTestSuite:
    """AI模型管理器测试套件"""

    def __init__(self, config: AITestConfig = None):
        self.config = config or AITestConfig()
        self.model_manager = None
        self.test_results: List[ModelTestMetrics] = []
        self.mock_clients: Dict[str, MockAPIClient] = {}
        self.test_models: List[ModelConfig] = []

    async def initialize(self):
        """初始化测试环境"""
        logger.info("Initializing AI Model Manager test suite...")

        # 创建测试模型配置
        self._create_test_models()

        # 初始化模型管理器
        self.model_manager = AIModelManager(
            db_url=self.config.test_db_url,
            redis_url=self.config.test_redis_url
        )

        if self.config.mock_api_responses:
            await self._setup_mock_clients()

        await self.model_manager.initialize()

        # 注册测试模型
        for model_config in self.test_models:
            self.model_manager.models[model_config.id] = model_config

        logger.info(f"AI Model Manager test suite initialized with {len(self.test_models)} test models")

    def _create_test_models(self):
        """创建测试模型配置"""
        self.test_models = [
            ModelConfig(
                id="test_openai_gpt4",
                provider=ModelProvider.OPENAI,
                model_name="gpt-4",
                display_name="Test OpenAI GPT-4",
                max_tokens=4096,
                temperature=0.7,
                input_token_cost=0.03,
                output_token_cost=0.06,
                requests_per_minute=60,
                priority=100,
                status=ModelStatus.ACTIVE
            ),
            ModelConfig(
                id="test_anthropic_claude",
                provider=ModelProvider.ANTHROPIC,
                model_name="claude-3-sonnet-20240229",
                display_name="Test Anthropic Claude",
                max_tokens=4096,
                temperature=0.7,
                input_token_cost=0.015,
                output_token_cost=0.075,
                requests_per_minute=50,
                priority=90,
                status=ModelStatus.ACTIVE
            ),
            ModelConfig(
                id="test_openai_gpt35",
                provider=ModelProvider.OPENAI,
                model_name="gpt-3.5-turbo",
                display_name="Test OpenAI GPT-3.5",
                max_tokens=4096,
                temperature=0.7,
                input_token_cost=0.001,
                output_token_cost=0.002,
                requests_per_minute=100,
                priority=80,
                status=ModelStatus.ACTIVE
            ),
            ModelConfig(
                id="test_ollama_llama",
                provider=ModelProvider.OLLAMA,
                model_name="llama2:7b",
                display_name="Test Ollama Llama2",
                api_endpoint="http://localhost:11434",
                max_tokens=2048,
                temperature=0.7,
                input_token_cost=0.0,
                output_token_cost=0.0,
                requests_per_minute=30,
                priority=70,
                status=ModelStatus.ACTIVE
            ),
            ModelConfig(
                id="test_slow_model",
                provider=ModelProvider.OPENAI,
                model_name="slow-model",
                display_name="Test Slow Model",
                max_tokens=2048,
                temperature=0.7,
                input_token_cost=0.01,
                output_token_cost=0.02,
                requests_per_minute=10,
                priority=60,
                status=ModelStatus.ACTIVE
            )
        ]

    async def _setup_mock_clients(self):
        """设置模拟客户端"""
        for model_config in self.test_models:
            # 为不同模型设置不同的性能特征
            if "slow" in model_config.id:
                latency_ms = 2000
                error_rate = 0.1
            elif model_config.provider == ModelProvider.OLLAMA:
                latency_ms = 500
                error_rate = 0.05
            else:
                latency_ms = 200
                error_rate = 0.02

            mock_client = MockAPIClient(
                provider=model_config.provider,
                latency_ms=latency_ms,
                error_rate=error_rate
            )

            self.mock_clients[model_config.id] = mock_client

            # 替换模型管理器中的客户端
            self.model_manager.clients[model_config.id] = mock_client

    async def _measure_test_performance(self, test_func, test_name: str, model_id: str = None, *args, **kwargs) -> ModelTestMetrics:
        """测试性能测量装饰器"""
        process = psutil.Process()
        start_memory = process.memory_info().rss / 1024 / 1024
        start_time = time.time()

        try:
            result = await test_func(*args, **kwargs)
            success = True
            errors = []
        except Exception as e:
            result = None
            success = False
            errors = [str(e)]
            logger.error(f"Test {test_name} failed: {e}")
            logger.error(traceback.format_exc())

        end_time = time.time()
        end_memory = process.memory_info().rss / 1024 / 1024

        metrics = ModelTestMetrics(
            model_id=model_id or "all_models",
            test_name=test_name,
            start_time=start_time,
            end_time=end_time,
            duration_ms=(end_time - start_time) * 1000,
            success=success,
            memory_usage_mb=end_memory - start_memory,
            errors=errors,
            additional_data=result if isinstance(result, dict) else {}
        )

        self.test_results.append(metrics)
        return metrics

    async def test_model_initialization(self) -> Dict[str, Any]:
        """测试模型初始化"""
        async def _test():
            initialized_models = []
            failed_models = []

            for model_config in self.test_models:
                try:
                    # 验证模型是否正确加载
                    loaded_model = self.model_manager.models.get(model_config.id)
                    if not loaded_model:
                        failed_models.append({
                            'model_id': model_config.id,
                            'error': 'Model not found in manager'
                        })
                        continue

                    # 验证客户端是否初始化
                    client = self.model_manager.clients.get(model_config.id)
                    if not client:
                        failed_models.append({
                            'model_id': model_config.id,
                            'error': 'Client not initialized'
                        })
                        continue

                    initialized_models.append({
                        'model_id': model_config.id,
                        'provider': model_config.provider.value,
                        'status': model_config.status.value,
                        'client_type': type(client).__name__
                    })

                except Exception as e:
                    failed_models.append({
                        'model_id': model_config.id,
                        'error': str(e)
                    })

            return {
                'total_models': len(self.test_models),
                'initialized_models': len(initialized_models),
                'failed_models': len(failed_models),
                'success_rate': len(initialized_models) / len(self.test_models) if self.test_models else 0,
                'model_details': initialized_models,
                'failures': failed_models
            }

        return await self._measure_test_performance(_test, "model_initialization")

    async def test_basic_completion(self) -> Dict[str, Any]:
        """测试基础完成功能"""
        async def _test():
            test_prompts = [
                "What is the capital of France?",
                "Explain quantum computing in simple terms.",
                "Write a short poem about technology.",
                "Calculate 2 + 2 and explain the process.",
                "Describe the benefits of renewable energy."
            ]

            completion_results = []

            for model_config in self.test_models:
                if not self.config.mock_api_responses:
                    continue  # 跳过实际API调用，除非配置允许

                model_results = []

                for i, prompt in enumerate(test_prompts):
                    try:
                        start_time = time.time()

                        if self.config.mock_api_responses:
                            # 使用模拟客户端
                            mock_client = self.mock_clients[model_config.id]
                            response = await mock_client.simulate_request(prompt)
                        else:
                            # 使用实际模型管理器
                            response = await self.model_manager.complete(
                                prompt=prompt,
                                model_id=model_config.id,
                                use_cache=False
                            )

                        latency = (time.time() - start_time) * 1000

                        model_results.append({
                            'prompt_index': i,
                            'success': True,
                            'latency_ms': latency,
                            'tokens_used': response.get('usage', {}).get('total_tokens', 0),
                            'response_length': len(response.get('content', ''))
                        })

                    except Exception as e:
                        model_results.append({
                            'prompt_index': i,
                            'success': False,
                            'error': str(e),
                            'latency_ms': 0
                        })

                # 计算模型统计
                successful_requests = [r for r in model_results if r['success']]
                avg_latency = sum(r['latency_ms'] for r in successful_requests) / len(successful_requests) if successful_requests else 0
                success_rate = len(successful_requests) / len(model_results) if model_results else 0

                completion_results.append({
                    'model_id': model_config.id,
                    'provider': model_config.provider.value,
                    'total_requests': len(model_results),
                    'successful_requests': len(successful_requests),
                    'success_rate': success_rate,
                    'avg_latency_ms': avg_latency,
                    'request_details': model_results
                })

            overall_success_rate = sum(r['success_rate'] for r in completion_results) / len(completion_results) if completion_results else 0

            return {
                'test_prompts_count': len(test_prompts),
                'tested_models': len(completion_results),
                'overall_success_rate': overall_success_rate,
                'model_results': completion_results
            }

        return await self._measure_test_performance(_test, "basic_completion")

    async def test_load_balancing(self) -> Dict[str, Any]:
        """测试负载均衡功能"""
        async def _test():
            if not hasattr(self.model_manager, 'load_balancer') or not self.model_manager.load_balancer:
                return {'error': 'Load balancer not available'}

            # 模拟不同类型的请求
            request_scenarios = [
                {'type': 'short_prompt', 'prompt': 'Hello', 'expected_priority': 'low_cost'},
                {'type': 'medium_prompt', 'prompt': 'Explain machine learning' * 10, 'expected_priority': 'balanced'},
                {'type': 'long_prompt', 'prompt': 'Write a detailed analysis' * 50, 'expected_priority': 'high_performance'},
                {'type': 'function_call', 'prompt': 'Call function', 'requires_functions': True}
            ]

            balancing_results = []

            for scenario in request_scenarios:
                model_selections = []

                # 多次请求相同场景，观察负载均衡行为
                for _ in range(20):
                    try:
                        selected_model = await self.model_manager.load_balancer.select_model(
                            request_type="completion",
                            prompt_length=len(scenario['prompt']),
                            requires_functions=scenario.get('requires_functions', False)
                        )

                        if selected_model:
                            model_selections.append(selected_model)

                    except Exception as e:
                        logger.warning(f"Load balancer selection failed: {e}")

                # 分析模型选择分布
                model_distribution = {}
                for model_id in model_selections:
                    model_distribution[model_id] = model_distribution.get(model_id, 0) + 1

                # 计算分布均匀度（使用基尼系数的简化版本）
                if model_selections:
                    total_selections = len(model_selections)
                    proportions = [count / total_selections for count in model_distribution.values()]
                    balance_score = 1 - sum(p * p for p in proportions)  # 1 - Herfindahl index
                else:
                    balance_score = 0

                balancing_results.append({
                    'scenario': scenario['type'],
                    'total_selections': len(model_selections),
                    'unique_models_selected': len(model_distribution),
                    'model_distribution': model_distribution,
                    'balance_score': balance_score,
                    'most_selected_model': max(model_distribution.items(), key=lambda x: x[1])[0] if model_distribution else None
                })

            # 计算整体负载均衡性能
            overall_balance_score = sum(r['balance_score'] for r in balancing_results) / len(balancing_results) if balancing_results else 0

            return {
                'tested_scenarios': len(request_scenarios),
                'overall_balance_score': overall_balance_score,
                'scenario_results': balancing_results,
                'load_balancing_effective': overall_balance_score > 0.3  # 阈值可调整
            }

        return await self._measure_test_performance(_test, "load_balancing")

    async def test_caching_mechanism(self) -> Dict[str, Any]:
        """测试缓存机制"""
        async def _test():
            cache_test_prompts = [
                "What is artificial intelligence?",
                "Explain the concept of machine learning.",
                "What are the benefits of cloud computing?",
                "Describe neural networks.",
                "What is deep learning?"
            ]

            cache_results = []

            for prompt in cache_test_prompts:
                # 第一次请求（应该不在缓存中）
                start_time = time.time()
                if self.config.mock_api_responses:
                    mock_client = self.mock_clients[self.test_models[0].id]
                    first_response = await mock_client.simulate_request(prompt)
                else:
                    first_response = await self.model_manager.complete(
                        prompt=prompt,
                        use_cache=True
                    )
                first_request_time = (time.time() - start_time) * 1000

                # 第二次相同请求（应该命中缓存）
                start_time = time.time()
                if self.config.mock_api_responses:
                    second_response = await mock_client.simulate_request(prompt)
                else:
                    second_response = await self.model_manager.complete(
                        prompt=prompt,
                        use_cache=True
                    )
                second_request_time = (time.time() - start_time) * 1000

                # 分析缓存性能
                cache_hit = second_request_time < first_request_time * 0.5  # 假设缓存命中应该至少快50%
                speedup = first_request_time / second_request_time if second_request_time > 0 else 0

                cache_results.append({
                    'prompt': prompt[:50] + "...",
                    'first_request_time_ms': first_request_time,
                    'second_request_time_ms': second_request_time,
                    'speedup_factor': speedup,
                    'cache_hit_detected': cache_hit,
                    'responses_identical': first_response.get('content') == second_response.get('content')
                })

            # 计算缓存性能统计
            cache_hits = sum(1 for r in cache_results if r['cache_hit_detected'])
            avg_speedup = sum(r['speedup_factor'] for r in cache_results) / len(cache_results) if cache_results else 0
            cache_hit_rate = cache_hits / len(cache_results) if cache_results else 0

            return {
                'tested_prompts': len(cache_test_prompts),
                'cache_hits': cache_hits,
                'cache_hit_rate': cache_hit_rate,
                'avg_speedup_factor': avg_speedup,
                'cache_results': cache_results,
                'caching_effective': cache_hit_rate > 0.7 and avg_speedup > 2.0
            }

        return await self._measure_test_performance(_test, "caching_mechanism")

    async def test_concurrent_requests(self) -> Dict[str, Any]:
        """测试并发请求处理"""
        async def _test():
            concurrent_requests = self.config.concurrent_requests
            test_prompt = "Handle this concurrent request and respond appropriately."

            async def single_request(request_id: int):
                start_time = time.time()
                try:
                    if self.config.mock_api_responses:
                        # 随机选择一个模型进行测试
                        model_id = random.choice([m.id for m in self.test_models])
                        mock_client = self.mock_clients[model_id]
                        response = await mock_client.simulate_request(test_prompt)
                        used_model = model_id
                    else:
                        response = await self.model_manager.complete(
                            prompt=test_prompt,
                            use_cache=False
                        )
                        used_model = response.get('model', 'unknown')

                    duration = (time.time() - start_time) * 1000

                    return {
                        'request_id': request_id,
                        'success': True,
                        'duration_ms': duration,
                        'model_used': used_model,
                        'response_length': len(response.get('content', ''))
                    }

                except Exception as e:
                    duration = (time.time() - start_time) * 1000
                    return {
                        'request_id': request_id,
                        'success': False,
                        'duration_ms': duration,
                        'error': str(e)
                    }

            # 执行并发请求
            start_time = time.time()
            tasks = [single_request(i) for i in range(concurrent_requests)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_duration = (time.time() - start_time) * 1000

            # 分析结果
            successful_results = [r for r in results if isinstance(r, dict) and r.get('success', False)]
            failed_results = [r for r in results if not isinstance(r, dict) or not r.get('success', False)]

            if successful_results:
                latencies = [r['duration_ms'] for r in successful_results]
                latencies.sort()

                p50_latency = latencies[len(latencies) // 2]
                p95_latency = latencies[int(len(latencies) * 0.95)]
                p99_latency = latencies[int(len(latencies) * 0.99)]
                throughput = len(successful_results) / (total_duration / 1000)

                # 分析模型使用分布
                model_usage = {}
                for result in successful_results:
                    model = result.get('model_used', 'unknown')
                    model_usage[model] = model_usage.get(model, 0) + 1

            else:
                p50_latency = p95_latency = p99_latency = throughput = 0
                model_usage = {}

            return {
                'concurrent_requests': concurrent_requests,
                'total_duration_ms': total_duration,
                'successful_requests': len(successful_results),
                'failed_requests': len(failed_results),
                'success_rate': len(successful_results) / concurrent_requests,
                'throughput_rps': throughput,
                'latency_percentiles': {
                    'p50': p50_latency,
                    'p95': p95_latency,
                    'p99': p99_latency
                },
                'model_usage_distribution': model_usage,
                'request_details': results[:10]  # 只保留前10个结果的详细信息
            }

        return await self._measure_test_performance(_test, "concurrent_requests")

    async def test_error_handling_and_fallback(self) -> Dict[str, Any]:
        """测试错误处理和故障转移"""
        async def _test():
            # 临时将一个模型设置为ERROR状态
            original_status = self.test_models[0].status
            self.test_models[0].status = ModelStatus.ERROR

            # 增加一个模型的错误率来测试故障转移
            original_error_rate = None
            if self.config.mock_api_responses:
                target_model = self.test_models[1]
                original_error_rate = self.mock_clients[target_model.id].error_rate
                self.mock_clients[target_model.id].error_rate = 0.8  # 80%错误率

            test_scenarios = [
                {
                    'name': 'model_unavailable',
                    'prompt': 'Test with unavailable model',
                    'model_id': self.test_models[0].id,  # ERROR状态的模型
                    'expected_behavior': 'fallback_to_other_model'
                },
                {
                    'name': 'high_error_rate',
                    'prompt': 'Test with high error rate model',
                    'model_id': self.test_models[1].id if len(self.test_models) > 1 else None,
                    'expected_behavior': 'retry_or_fallback'
                },
                {
                    'name': 'rate_limit_exceeded',
                    'prompt': 'Test rate limiting',
                    'model_id': None,  # 让负载均衡器选择
                    'expected_behavior': 'switch_to_available_model'
                }
            ]

            error_handling_results = []

            for scenario in test_scenarios:
                scenario_results = []

                # 对每个场景执行多次测试
                for attempt in range(5):
                    try:
                        start_time = time.time()

                        if self.config.mock_api_responses and scenario['model_id']:
                            mock_client = self.mock_clients[scenario['model_id']]
                            response = await mock_client.simulate_request(scenario['prompt'])
                            fallback_occurred = False
                        else:
                            response = await self.model_manager.complete(
                                prompt=scenario['prompt'],
                                model_id=scenario['model_id'],
                                use_cache=False
                            )
                            # 检查是否发生了故障转移
                            fallback_occurred = response.get('model') != scenario['model_id']

                        duration = (time.time() - start_time) * 1000

                        scenario_results.append({
                            'attempt': attempt,
                            'success': True,
                            'duration_ms': duration,
                            'fallback_occurred': fallback_occurred,
                            'final_model': response.get('model', 'unknown')
                        })

                    except Exception as e:
                        duration = (time.time() - start_time) * 1000
                        scenario_results.append({
                            'attempt': attempt,
                            'success': False,
                            'duration_ms': duration,
                            'error': str(e)
                        })

                # 分析场景结果
                successful_attempts = [r for r in scenario_results if r['success']]
                fallback_attempts = [r for r in successful_attempts if r.get('fallback_occurred', False)]

                error_handling_results.append({
                    'scenario': scenario['name'],
                    'total_attempts': len(scenario_results),
                    'successful_attempts': len(successful_attempts),
                    'fallback_occurred': len(fallback_attempts),
                    'success_rate': len(successful_attempts) / len(scenario_results),
                    'fallback_rate': len(fallback_attempts) / len(successful_attempts) if successful_attempts else 0,
                    'avg_response_time_ms': sum(r['duration_ms'] for r in successful_attempts) / len(successful_attempts) if successful_attempts else 0
                })

            # 恢复原始状态
            self.test_models[0].status = original_status
            if original_error_rate is not None and self.config.mock_api_responses:
                self.mock_clients[self.test_models[1].id].error_rate = original_error_rate

            return {
                'tested_scenarios': len(test_scenarios),
                'scenario_results': error_handling_results,
                'overall_resilience_score': sum(r['success_rate'] for r in error_handling_results) / len(error_handling_results) if error_handling_results else 0
            }

        return await self._measure_test_performance(_test, "error_handling_and_fallback")

    async def test_rate_limiting(self) -> Dict[str, Any]:
        """测试速率限制功能"""
        async def _test():
            # 选择一个有较低速率限制的模型进行测试
            test_model = min(self.test_models, key=lambda m: m.requests_per_minute)
            original_limit = test_model.requests_per_minute

            # 设置一个很低的速率限制进行测试
            test_model.requests_per_minute = 5
            test_prompt = "Test rate limiting functionality"

            rate_limit_results = []
            start_time = time.time()

            # 快速发送多个请求以触发速率限制
            for i in range(10):
                try:
                    request_start = time.time()

                    if self.config.mock_api_responses:
                        # 模拟速率限制检查
                        if await self.model_manager._check_rate_limit(test_model.id):
                            mock_client = self.mock_clients[test_model.id]
                            response = await mock_client.simulate_request(test_prompt)
                            status = "success"
                        else:
                            response = None
                            status = "rate_limited"
                    else:
                        response = await self.model_manager.complete(
                            prompt=test_prompt,
                            model_id=test_model.id,
                            use_cache=False
                        )
                        status = "success"

                    request_duration = (time.time() - request_start) * 1000

                    rate_limit_results.append({
                        'request_index': i,
                        'status': status,
                        'duration_ms': request_duration,
                        'response_received': response is not None
                    })

                except Exception as e:
                    request_duration = (time.time() - request_start) * 1000
                    rate_limit_results.append({
                        'request_index': i,
                        'status': "error",
                        'duration_ms': request_duration,
                        'error': str(e)
                    })

                # 避免过快发送请求
                await asyncio.sleep(0.1)

            total_test_duration = (time.time() - start_time) * 1000

            # 分析速率限制行为
            successful_requests = [r for r in rate_limit_results if r['status'] == 'success']
            rate_limited_requests = [r for r in rate_limit_results if r['status'] == 'rate_limited']
            error_requests = [r for r in rate_limit_results if r['status'] == 'error']

            # 恢复原始速率限制
            test_model.requests_per_minute = original_limit

            return {
                'test_model': test_model.id,
                'configured_rate_limit': 5,
                'total_requests': len(rate_limit_results),
                'successful_requests': len(successful_requests),
                'rate_limited_requests': len(rate_limited_requests),
                'error_requests': len(error_requests),
                'total_test_duration_ms': total_test_duration,
                'rate_limiting_working': len(rate_limited_requests) > 0 or len(successful_requests) <= 5,
                'request_details': rate_limit_results
            }

        return await self._measure_test_performance(_test, "rate_limiting")

    async def test_model_health_monitoring(self) -> Dict[str, Any]:
        """测试模型健康监控"""
        async def _test():
            if not hasattr(self.model_manager, 'model_metrics'):
                return {'error': 'Model metrics not available'}

            # 模拟一些请求以生成指标数据
            test_requests = 20
            test_prompt = "Health monitoring test request"

            for i in range(test_requests):
                try:
                    if self.config.mock_api_responses:
                        # 随机选择模型并发送请求
                        model_id = random.choice([m.id for m in self.test_models])
                        mock_client = self.mock_clients[model_id]
                        await mock_client.simulate_request(test_prompt)

                        # 更新模型指标（模拟）
                        metrics = self.model_manager.model_metrics[model_id]
                        metrics.total_requests += 1
                        metrics.successful_requests += 1
                    else:
                        await self.model_manager.complete(
                            prompt=test_prompt,
                            use_cache=False
                        )

                except Exception as e:
                    logger.warning(f"Health monitoring test request failed: {e}")

            # 等待健康监控更新
            await asyncio.sleep(1)

            # 收集健康指标
            health_results = []

            for model_config in self.test_models:
                metrics = self.model_manager.model_metrics.get(model_config.id)
                if metrics:
                    error_rate = (metrics.failed_requests / metrics.total_requests * 100) if metrics.total_requests > 0 else 0

                    health_results.append({
                        'model_id': model_config.id,
                        'status': model_config.status.value,
                        'total_requests': metrics.total_requests,
                        'successful_requests': metrics.successful_requests,
                        'failed_requests': metrics.failed_requests,
                        'error_rate_percent': error_rate,
                        'avg_latency_ms': metrics.avg_latency_ms,
                        'health_score': metrics.health_score,
                        'total_cost': metrics.total_cost
                    })

            # 分析健康状态
            healthy_models = [h for h in health_results if h['health_score'] > 70]
            unhealthy_models = [h for h in health_results if h['health_score'] <= 70]

            return {
                'monitored_models': len(health_results),
                'healthy_models': len(healthy_models),
                'unhealthy_models': len(unhealthy_models),
                'avg_health_score': sum(h['health_score'] for h in health_results) / len(health_results) if health_results else 0,
                'avg_error_rate': sum(h['error_rate_percent'] for h in health_results) / len(health_results) if health_results else 0,
                'total_cost': sum(h['total_cost'] for h in health_results),
                'model_health_details': health_results
            }

        return await self._measure_test_performance(_test, "model_health_monitoring")

    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有AI模型管理器测试"""
        logger.info("Starting comprehensive AI Model Manager test suite...")

        test_suite_start = time.time()

        # 定义测试列表
        tests = [
            self.test_model_initialization,
            self.test_basic_completion,
            self.test_load_balancing,
            self.test_caching_mechanism,
            self.test_concurrent_requests,
            self.test_error_handling_and_fallback,
            self.test_rate_limiting,
            self.test_model_health_monitoring
        ]

        all_results = {}

        for test_func in tests:
            try:
                logger.info(f"Running test: {test_func.__name__}")
                result = await test_func()

                all_results[result.test_name] = {
                    'success': result.success,
                    'duration_ms': result.duration_ms,
                    'metrics': result.additional_data,
                    'error': result.error_message if hasattr(result, 'error_message') else None
                }

                status = 'PASSED' if result.success else 'FAILED'
                logger.info(f"Test {result.test_name}: {status} ({result.duration_ms:.2f}ms)")

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
            'test_suite': 'ai_model_manager_comprehensive',
            'total_duration_ms': test_suite_duration,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': passed_tests / total_tests if total_tests > 0 else 0,
            'timestamp': datetime.now().isoformat(),
            'test_configuration': {
                'mock_api_responses': self.config.mock_api_responses,
                'concurrent_requests': self.config.concurrent_requests,
                'load_test_requests': self.config.load_test_requests,
                'test_models_count': len(self.test_models)
            },
            'test_results': all_results
        }

        logger.info(f"AI Model Manager test suite completed: {passed_tests}/{total_tests} tests passed")
        return summary

    async def cleanup(self):
        """清理测试环境"""
        logger.info("Cleaning up AI Model Manager test environment...")

        if self.model_manager:
            await self.model_manager.shutdown()

        # 清理模拟客户端
        self.mock_clients.clear()

async def main():
    """主测试入口"""
    config = AITestConfig()
    test_suite = AIModelManagerTestSuite(config)

    try:
        await test_suite.initialize()
        results = await test_suite.run_all_tests()

        # 保存测试结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"/h/novellus/test_results/ai_model_manager_test_results_{timestamp}.json"

        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\nAI Model Manager test results saved to: {results_file}")
        print(f"Overall success rate: {results['success_rate']:.2%}")

        return results['success_rate'] == 1.0

    except Exception as e:
        logger.error(f"AI Model Manager test suite failed: {e}")
        return False
    finally:
        await test_suite.cleanup()

if __name__ == "__main__":
    asyncio.run(main())