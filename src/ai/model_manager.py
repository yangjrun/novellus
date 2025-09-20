"""
AI Model Manager - Core management system for multiple LLM providers
"""

import asyncio
import hashlib
import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from enum import Enum
import logging
from dataclasses import dataclass, field
from collections import defaultdict
import random

import httpx
import openai
from anthropic import AsyncAnthropic
import numpy as np
from sqlalchemy import select, update, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from cryptography.fernet import Fernet
import redis.asyncio as redis

from src.config import config

logger = logging.getLogger(__name__)

class ModelProvider(str, Enum):
    """Supported model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    AZURE = "azure"
    GOOGLE = "google"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"

class ModelStatus(str, Enum):
    """Model availability status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"
    ERROR = "error"

class RequestStatus(str, Enum):
    """Request processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CACHED = "cached"

@dataclass
class ModelConfig:
    """Configuration for an AI model"""
    id: str
    provider: ModelProvider
    model_name: str
    display_name: str
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    input_token_cost: float = 0.0
    output_token_cost: float = 0.0
    supports_streaming: bool = True
    supports_function_calling: bool = False
    context_window: int = 4096
    requests_per_minute: int = 60
    priority: int = 100
    status: ModelStatus = ModelStatus.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ModelMetrics:
    """Performance metrics for a model"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    avg_latency_ms: float = 0.0
    error_rate: float = 0.0
    cache_hit_rate: float = 0.0
    health_score: float = 100.0
    last_updated: datetime = field(default_factory=datetime.utcnow)

class AIModelManager:
    """
    Central manager for AI models with load balancing, caching, and monitoring
    """

    def __init__(self, db_url: str = None, redis_url: str = None, encryption_key: str = None):
        """
        Initialize the AI Model Manager

        Args:
            db_url: Database connection URL
            redis_url: Redis connection URL for caching
            encryption_key: Key for encrypting API keys
        """
        self.db_url = db_url or config.postgres_async_url
        self.redis_url = redis_url or "redis://localhost:6379"
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)

        # Model registry
        self.models: Dict[str, ModelConfig] = {}
        self.model_metrics: Dict[str, ModelMetrics] = defaultdict(ModelMetrics)

        # Client instances
        self.clients: Dict[str, Any] = {}

        # Database
        self.engine = None
        self.async_session = None

        # Redis cache
        self.redis_client = None

        # Rate limiting
        self.rate_limits: Dict[str, List[float]] = defaultdict(list)

        # Load balancer
        self.load_balancer = None

        # Background tasks
        self.background_tasks = []

    async def initialize(self):
        """Initialize database and cache connections"""
        # Initialize database
        self.engine = create_async_engine(self.db_url, echo=False, pool_pre_ping=True)
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False)

        # Initialize Redis
        try:
            self.redis_client = await redis.from_url(self.redis_url, decode_responses=True)
            await self.redis_client.ping()
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed, falling back to in-memory cache: {e}")
            self.redis_client = None

        # Load models from database
        await self.load_models_from_db()

        # Initialize load balancer
        self.load_balancer = ModelLoadBalancer(self)

        # Start background tasks
        self.background_tasks.append(asyncio.create_task(self._metrics_collector()))
        self.background_tasks.append(asyncio.create_task(self._health_monitor()))

        logger.info(f"AI Model Manager initialized with {len(self.models)} models")

    async def load_models_from_db(self):
        """Load model configurations from database"""
        async with self.async_session() as session:
            query = select("ai_models").where("status != 'deprecated'")
            result = await session.execute(query)

            for row in result:
                model_config = ModelConfig(
                    id=str(row.id),
                    provider=ModelProvider(row.provider),
                    model_name=row.model_name,
                    display_name=row.display_name,
                    api_endpoint=row.api_endpoint,
                    api_key=self._decrypt_api_key(row.api_key_encrypted) if row.api_key_encrypted else None,
                    max_tokens=row.max_tokens,
                    temperature=row.temperature,
                    input_token_cost=float(row.input_token_cost or 0),
                    output_token_cost=float(row.output_token_cost or 0),
                    supports_streaming=row.supports_streaming,
                    supports_function_calling=row.supports_function_calling,
                    context_window=row.context_window,
                    requests_per_minute=row.requests_per_minute,
                    priority=row.priority,
                    status=ModelStatus(row.status),
                    metadata=row.metadata or {}
                )

                self.models[model_config.id] = model_config
                await self._initialize_client(model_config)

    async def _initialize_client(self, model_config: ModelConfig):
        """Initialize API client for a model"""
        try:
            if model_config.provider == ModelProvider.OPENAI:
                self.clients[model_config.id] = openai.AsyncOpenAI(
                    api_key=model_config.api_key or config.openai_api_key
                )
            elif model_config.provider == ModelProvider.ANTHROPIC:
                self.clients[model_config.id] = AsyncAnthropic(
                    api_key=model_config.api_key or config.claude_api_key
                )
            elif model_config.provider == ModelProvider.OLLAMA:
                self.clients[model_config.id] = httpx.AsyncClient(
                    base_url=model_config.api_endpoint or "http://localhost:11434"
                )
            # Add more providers as needed

            logger.info(f"Initialized client for {model_config.display_name}")
        except Exception as e:
            logger.error(f"Failed to initialize client for {model_config.display_name}: {e}")
            model_config.status = ModelStatus.ERROR

    async def complete(
        self,
        prompt: str = None,
        messages: List[Dict[str, str]] = None,
        model_id: str = None,
        max_tokens: int = None,
        temperature: float = None,
        stream: bool = False,
        functions: List[Dict] = None,
        use_cache: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a completion request with automatic model selection and caching

        Args:
            prompt: Text prompt for completion
            messages: Chat messages for conversation
            model_id: Specific model ID to use (optional)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stream: Enable streaming response
            functions: Function definitions for function calling
            use_cache: Whether to use cached responses
            **kwargs: Additional model-specific parameters

        Returns:
            Response dictionary with completion and metadata
        """
        start_time = time.time()

        # Select model if not specified
        if not model_id:
            model_id = await self.load_balancer.select_model(
                request_type="completion",
                prompt_length=len(prompt or str(messages)),
                requires_functions=bool(functions)
            )

        if not model_id:
            raise ValueError("No available models for request")

        model_config = self.models.get(model_id)
        if not model_config:
            raise ValueError(f"Model {model_id} not found")

        # Check cache
        cache_key = None
        if use_cache:
            cache_key = self._generate_cache_key(prompt, messages, model_id, kwargs)
            cached_response = await self._get_cached_response(cache_key)
            if cached_response:
                await self._track_request(
                    model_id, "completion", prompt, messages,
                    cached_response, RequestStatus.CACHED,
                    latency_ms=int((time.time() - start_time) * 1000),
                    cache_hit=True
                )
                return cached_response

        # Check rate limits
        if not await self._check_rate_limit(model_id):
            # Try another model
            model_id = await self.load_balancer.select_model(
                request_type="completion",
                prompt_length=len(prompt or str(messages)),
                requires_functions=bool(functions),
                exclude_models=[model_id]
            )
            if not model_id:
                raise ValueError("All models are rate limited")
            model_config = self.models[model_id]

        # Execute request
        try:
            response = await self._execute_completion(
                model_config,
                prompt=prompt,
                messages=messages,
                max_tokens=max_tokens or model_config.max_tokens,
                temperature=temperature or model_config.temperature,
                stream=stream,
                functions=functions,
                **kwargs
            )

            # Calculate costs
            usage = response.get("usage", {})
            cost = self._calculate_cost(
                model_config,
                usage.get("prompt_tokens", 0),
                usage.get("completion_tokens", 0)
            )
            response["cost"] = cost

            # Cache response
            if use_cache and cache_key:
                await self._cache_response(cache_key, response)

            # Track request
            await self._track_request(
                model_id, "completion", prompt, messages,
                response, RequestStatus.COMPLETED,
                latency_ms=int((time.time() - start_time) * 1000),
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                cost=cost
            )

            return response

        except Exception as e:
            logger.error(f"Completion request failed for {model_config.display_name}: {e}")

            # Track failure
            await self._track_request(
                model_id, "completion", prompt, messages,
                None, RequestStatus.FAILED,
                latency_ms=int((time.time() - start_time) * 1000),
                error_message=str(e)
            )

            # Try fallback model
            if model_id:
                fallback_model_id = await self.load_balancer.select_model(
                    request_type="completion",
                    prompt_length=len(prompt or str(messages)),
                    requires_functions=bool(functions),
                    exclude_models=[model_id]
                )
                if fallback_model_id:
                    return await self.complete(
                        prompt=prompt,
                        messages=messages,
                        model_id=fallback_model_id,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        stream=stream,
                        functions=functions,
                        use_cache=use_cache,
                        **kwargs
                    )

            raise

    async def _execute_completion(
        self,
        model_config: ModelConfig,
        prompt: str = None,
        messages: List[Dict[str, str]] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        stream: bool = False,
        functions: List[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute completion request for specific provider"""
        client = self.clients.get(model_config.id)
        if not client:
            raise ValueError(f"No client initialized for model {model_config.id}")

        if model_config.provider == ModelProvider.OPENAI:
            return await self._openai_completion(
                client, model_config, prompt, messages,
                max_tokens, temperature, stream, functions, **kwargs
            )
        elif model_config.provider == ModelProvider.ANTHROPIC:
            return await self._anthropic_completion(
                client, model_config, prompt, messages,
                max_tokens, temperature, stream, **kwargs
            )
        elif model_config.provider == ModelProvider.OLLAMA:
            return await self._ollama_completion(
                client, model_config, prompt, messages,
                max_tokens, temperature, stream, **kwargs
            )
        else:
            raise NotImplementedError(f"Provider {model_config.provider} not implemented")

    async def _openai_completion(
        self, client, model_config, prompt, messages,
        max_tokens, temperature, stream, functions, **kwargs
    ):
        """Execute OpenAI completion"""
        params = {
            "model": model_config.model_name,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream,
            **kwargs
        }

        if messages:
            params["messages"] = messages
        else:
            params["messages"] = [{"role": "user", "content": prompt}]

        if functions and model_config.supports_function_calling:
            params["functions"] = functions

        response = await client.chat.completions.create(**params)

        if stream:
            return {"stream": response, "model": model_config.model_name}

        return {
            "content": response.choices[0].message.content,
            "model": model_config.model_name,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            "finish_reason": response.choices[0].finish_reason
        }

    async def _anthropic_completion(
        self, client, model_config, prompt, messages,
        max_tokens, temperature, stream, **kwargs
    ):
        """Execute Anthropic completion"""
        if messages:
            # Convert to Anthropic format
            anthropic_messages = []
            for msg in messages:
                anthropic_messages.append({
                    "role": "user" if msg["role"] == "user" else "assistant",
                    "content": msg["content"]
                })
        else:
            anthropic_messages = [{"role": "user", "content": prompt}]

        response = await client.messages.create(
            model=model_config.model_name,
            messages=anthropic_messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=stream,
            **kwargs
        )

        if stream:
            return {"stream": response, "model": model_config.model_name}

        return {
            "content": response.content[0].text,
            "model": model_config.model_name,
            "usage": {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            },
            "stop_reason": response.stop_reason
        }

    async def _ollama_completion(
        self, client, model_config, prompt, messages,
        max_tokens, temperature, stream, **kwargs
    ):
        """Execute Ollama completion"""
        data = {
            "model": model_config.model_name,
            "prompt": prompt or messages[-1]["content"] if messages else "",
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            },
            "stream": stream
        }

        if messages:
            data["messages"] = messages

        response = await client.post("/api/generate", json=data)
        result = response.json()

        return {
            "content": result.get("response", ""),
            "model": model_config.model_name,
            "usage": {
                "prompt_tokens": result.get("prompt_eval_count", 0),
                "completion_tokens": result.get("eval_count", 0),
                "total_tokens": result.get("prompt_eval_count", 0) + result.get("eval_count", 0)
            }
        }

    def _generate_cache_key(self, prompt, messages, model_id, kwargs):
        """Generate cache key for request"""
        cache_data = {
            "prompt": prompt,
            "messages": messages,
            "model_id": model_id,
            **kwargs
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_str.encode()).hexdigest()

    async def _get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """Get cached response"""
        if self.redis_client:
            try:
                cached = await self.redis_client.get(f"ai_cache:{cache_key}")
                if cached:
                    return json.loads(cached)
            except Exception as e:
                logger.warning(f"Cache retrieval failed: {e}")

        # Fallback to database cache
        async with self.async_session() as session:
            query = select("ai_response_cache").where(
                and_(
                    "cache_key == cache_key",
                    or_("expires_at IS NULL", "expires_at > CURRENT_TIMESTAMP")
                )
            )
            result = await session.execute(query)
            row = result.first()

            if row:
                # Update hit count
                await session.execute(
                    update("ai_response_cache")
                    .where("id == row.id")
                    .values(
                        hit_count=row.hit_count + 1,
                        last_accessed_at=datetime.utcnow()
                    )
                )
                await session.commit()

                return json.loads(row.response)

        return None

    async def _cache_response(self, cache_key: str, response: Dict, ttl: int = 3600):
        """Cache response"""
        response_str = json.dumps(response)

        # Cache in Redis
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    f"ai_cache:{cache_key}",
                    ttl,
                    response_str
                )
            except Exception as e:
                logger.warning(f"Redis caching failed: {e}")

        # Cache in database
        async with self.async_session() as session:
            await session.execute(
                """
                INSERT INTO ai_response_cache (cache_key, request_hash, response, expires_at)
                VALUES (:key, :hash, :response, :expires)
                ON CONFLICT (cache_key) DO UPDATE
                SET response = :response, expires_at = :expires, updated_at = CURRENT_TIMESTAMP
                """,
                {
                    "key": cache_key,
                    "hash": cache_key,
                    "response": response_str,
                    "expires": datetime.utcnow() + timedelta(seconds=ttl)
                }
            )
            await session.commit()

    async def _check_rate_limit(self, model_id: str) -> bool:
        """Check if model is within rate limits"""
        model_config = self.models.get(model_id)
        if not model_config:
            return False

        now = time.time()
        window = 60  # 1 minute window

        # Clean old timestamps
        self.rate_limits[model_id] = [
            t for t in self.rate_limits[model_id]
            if now - t < window
        ]

        # Check limit
        if len(self.rate_limits[model_id]) >= model_config.requests_per_minute:
            return False

        # Add current timestamp
        self.rate_limits[model_id].append(now)
        return True

    def _calculate_cost(
        self,
        model_config: ModelConfig,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """Calculate cost for token usage"""
        input_cost = (prompt_tokens / 1000) * model_config.input_token_cost
        output_cost = (completion_tokens / 1000) * model_config.output_token_cost
        return round(input_cost + output_cost, 6)

    async def _track_request(
        self,
        model_id: str,
        request_type: str,
        prompt: str,
        messages: List[Dict],
        response: Dict,
        status: RequestStatus,
        latency_ms: int = 0,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        cost: float = 0.0,
        cache_hit: bool = False,
        error_message: str = None
    ):
        """Track request in database"""
        async with self.async_session() as session:
            await session.execute(
                """
                INSERT INTO ai_requests (
                    model_id, request_type, prompt, messages, response,
                    status, latency_ms, prompt_tokens, completion_tokens,
                    estimated_cost, cache_hit, error_message, created_at
                ) VALUES (
                    :model_id, :type, :prompt, :messages, :response,
                    :status, :latency, :p_tokens, :c_tokens,
                    :cost, :cache, :error, CURRENT_TIMESTAMP
                )
                """,
                {
                    "model_id": model_id,
                    "type": request_type,
                    "prompt": prompt,
                    "messages": json.dumps(messages) if messages else None,
                    "response": json.dumps(response) if response else None,
                    "status": status.value,
                    "latency": latency_ms,
                    "p_tokens": prompt_tokens,
                    "c_tokens": completion_tokens,
                    "cost": cost,
                    "cache": cache_hit,
                    "error": error_message
                }
            )
            await session.commit()

        # Update metrics
        metrics = self.model_metrics[model_id]
        metrics.total_requests += 1
        if status == RequestStatus.COMPLETED:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1
        metrics.total_tokens += prompt_tokens + completion_tokens
        metrics.total_cost += cost

        # Update average latency
        if latency_ms > 0:
            alpha = 0.1  # Exponential moving average factor
            metrics.avg_latency_ms = (1 - alpha) * metrics.avg_latency_ms + alpha * latency_ms

    async def _metrics_collector(self):
        """Background task to collect and store metrics"""
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes

                for model_id, metrics in self.model_metrics.items():
                    if metrics.total_requests == 0:
                        continue

                    # Calculate rates
                    error_rate = (metrics.failed_requests / metrics.total_requests) * 100

                    # Store in database
                    async with self.async_session() as session:
                        await session.execute(
                            """
                            INSERT INTO model_performance_metrics (
                                model_id, metric_date, metric_hour,
                                total_requests, successful_requests, failed_requests,
                                total_prompt_tokens, total_completion_tokens,
                                avg_latency_ms, total_cost, error_rate
                            ) VALUES (
                                :model_id, CURRENT_DATE, EXTRACT(HOUR FROM CURRENT_TIME),
                                :total, :success, :failed,
                                :p_tokens, :c_tokens,
                                :latency, :cost, :error_rate
                            )
                            ON CONFLICT (model_id, metric_date, metric_hour) DO UPDATE
                            SET total_requests = model_performance_metrics.total_requests + :total,
                                successful_requests = model_performance_metrics.successful_requests + :success,
                                failed_requests = model_performance_metrics.failed_requests + :failed,
                                updated_at = CURRENT_TIMESTAMP
                            """,
                            {
                                "model_id": model_id,
                                "total": metrics.total_requests,
                                "success": metrics.successful_requests,
                                "failed": metrics.failed_requests,
                                "p_tokens": 0,  # Would need to track separately
                                "c_tokens": 0,
                                "latency": metrics.avg_latency_ms,
                                "cost": metrics.total_cost,
                                "error_rate": error_rate
                            }
                        )
                        await session.commit()

                    # Reset counters
                    metrics.total_requests = 0
                    metrics.successful_requests = 0
                    metrics.failed_requests = 0
                    metrics.total_cost = 0.0

            except Exception as e:
                logger.error(f"Metrics collection failed: {e}")

    async def _health_monitor(self):
        """Monitor model health and update status"""
        while True:
            try:
                await asyncio.sleep(60)  # Every minute

                for model_id, model_config in self.models.items():
                    if model_config.status != ModelStatus.ACTIVE:
                        continue

                    metrics = self.model_metrics[model_id]

                    # Calculate health score
                    health_score = 100.0

                    # Penalize for errors
                    if metrics.total_requests > 0:
                        error_rate = (metrics.failed_requests / metrics.total_requests) * 100
                        health_score -= min(error_rate * 2, 50)

                    # Penalize for high latency
                    if metrics.avg_latency_ms > 5000:
                        health_score -= 20
                    elif metrics.avg_latency_ms > 2000:
                        health_score -= 10

                    metrics.health_score = max(health_score, 0)

                    # Update model status if health is poor
                    if metrics.health_score < 30:
                        model_config.status = ModelStatus.ERROR
                        logger.warning(f"Model {model_config.display_name} marked as ERROR due to poor health")

            except Exception as e:
                logger.error(f"Health monitoring failed: {e}")

    def _encrypt_api_key(self, api_key: str) -> str:
        """Encrypt API key for storage"""
        return self.cipher.encrypt(api_key.encode()).decode()

    def _decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt API key from storage"""
        return self.cipher.decrypt(encrypted_key.encode()).decode()

    async def shutdown(self):
        """Shutdown manager and cleanup resources"""
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()

        # Close connections
        if self.redis_client:
            await self.redis_client.close()

        if self.engine:
            await self.engine.dispose()

        # Close HTTP clients
        for client in self.clients.values():
            if isinstance(client, httpx.AsyncClient):
                await client.aclose()

        logger.info("AI Model Manager shut down")


class ModelLoadBalancer:
    """
    Intelligent load balancer for model selection
    """

    def __init__(self, manager: AIModelManager):
        self.manager = manager
        self.selection_history = defaultdict(list)

    async def select_model(
        self,
        request_type: str = "completion",
        prompt_length: int = 0,
        requires_functions: bool = False,
        exclude_models: List[str] = None,
        strategy: str = "weighted"
    ) -> Optional[str]:
        """
        Select the best model for a request

        Args:
            request_type: Type of request
            prompt_length: Length of prompt for context window check
            requires_functions: Whether function calling is required
            exclude_models: Models to exclude from selection
            strategy: Selection strategy (weighted, round_robin, least_latency, cost_optimized)

        Returns:
            Selected model ID or None if no suitable model
        """
        exclude_models = exclude_models or []

        # Filter eligible models
        eligible_models = []
        for model_id, model_config in self.manager.models.items():
            if model_id in exclude_models:
                continue

            if model_config.status != ModelStatus.ACTIVE:
                continue

            if requires_functions and not model_config.supports_function_calling:
                continue

            if prompt_length > model_config.context_window * 0.8:  # Leave room for response
                continue

            metrics = self.manager.model_metrics[model_id]
            if metrics.health_score < 50:
                continue

            eligible_models.append((model_id, model_config, metrics))

        if not eligible_models:
            return None

        # Apply selection strategy
        if strategy == "weighted":
            return self._weighted_selection(eligible_models)
        elif strategy == "round_robin":
            return self._round_robin_selection(eligible_models)
        elif strategy == "least_latency":
            return self._least_latency_selection(eligible_models)
        elif strategy == "cost_optimized":
            return self._cost_optimized_selection(eligible_models)
        else:
            return self._weighted_selection(eligible_models)

    def _weighted_selection(self, eligible_models: List[Tuple]) -> str:
        """Select model based on weighted score"""
        scores = []

        for model_id, model_config, metrics in eligible_models:
            score = model_config.priority

            # Boost score for good health
            score += metrics.health_score / 10

            # Boost score for low latency
            if metrics.avg_latency_ms > 0:
                score += 100 / (1 + metrics.avg_latency_ms / 1000)

            # Boost score for low cost
            if model_config.input_token_cost > 0:
                score += 10 / (1 + model_config.input_token_cost)

            scores.append((model_id, score))

        # Weighted random selection
        total_score = sum(s for _, s in scores)
        if total_score == 0:
            return eligible_models[0][0]

        rand = random.random() * total_score
        cumulative = 0

        for model_id, score in scores:
            cumulative += score
            if rand <= cumulative:
                return model_id

        return scores[-1][0]

    def _round_robin_selection(self, eligible_models: List[Tuple]) -> str:
        """Select model using round-robin"""
        model_ids = [m[0] for m in eligible_models]

        # Get last selected for this type
        history = self.selection_history["round_robin"]
        if not history:
            selected = model_ids[0]
        else:
            last_idx = model_ids.index(history[-1]) if history[-1] in model_ids else -1
            selected = model_ids[(last_idx + 1) % len(model_ids)]

        self.selection_history["round_robin"].append(selected)
        if len(self.selection_history["round_robin"]) > 100:
            self.selection_history["round_robin"] = self.selection_history["round_robin"][-50:]

        return selected

    def _least_latency_selection(self, eligible_models: List[Tuple]) -> str:
        """Select model with lowest latency"""
        best_model = min(
            eligible_models,
            key=lambda x: x[2].avg_latency_ms if x[2].avg_latency_ms > 0 else float('inf')
        )
        return best_model[0]

    def _cost_optimized_selection(self, eligible_models: List[Tuple]) -> str:
        """Select most cost-effective model"""
        best_model = min(
            eligible_models,
            key=lambda x: x[1].input_token_cost + x[1].output_token_cost
        )
        return best_model[0]