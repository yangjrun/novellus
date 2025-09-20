"""
AI System Integration Module - Connects all AI components together
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import redis.asyncio as redis

from src.config import config
from src.ai.model_manager import AIModelManager
from src.ai.cache_manager import CacheManager
from src.ai.metrics_collector import MetricsCollector, RequestMetrics

logger = logging.getLogger(__name__)


class AISystemIntegration:
    """
    Main integration class that connects all AI components
    """

    def __init__(self, config_override: Dict[str, Any] = None):
        """
        Initialize AI System Integration

        Args:
            config_override: Optional configuration overrides
        """
        self.config = config_override or {}

        # Components
        self.model_manager: Optional[AIModelManager] = None
        self.cache_manager: Optional[CacheManager] = None
        self.metrics_collector: Optional[MetricsCollector] = None

        # Database
        self.engine = None
        self.async_session = None

        # Redis
        self.redis_client = None

        # Status
        self.initialized = False

    async def initialize(self):
        """Initialize all AI components"""
        if self.initialized:
            return

        try:
            # Initialize database
            db_url = self.config.get("db_url", config.postgres_async_url)
            self.engine = create_async_engine(db_url, echo=False, pool_pre_ping=True)
            self.async_session = async_sessionmaker(self.engine, expire_on_commit=False)

            # Initialize Redis
            redis_url = self.config.get("redis_url", "redis://localhost:6379")
            try:
                self.redis_client = await redis.from_url(redis_url, decode_responses=True)
                await self.redis_client.ping()
                logger.info("Redis connected successfully")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}")
                self.redis_client = None

            # Initialize Model Manager
            self.model_manager = AIModelManager(
                db_url=db_url,
                redis_url=redis_url,
                encryption_key=self.config.get("encryption_key")
            )
            await self.model_manager.initialize()

            # Initialize Cache Manager
            async with self.async_session() as session:
                self.cache_manager = CacheManager(
                    redis_client=self.redis_client,
                    db_session=session,
                    embedding_model=self.config.get("embedding_model", "text-embedding-3-small"),
                    similarity_threshold=self.config.get("similarity_threshold", 0.85)
                )
                await self.cache_manager.initialize()

            # Initialize Metrics Collector
            async with self.async_session() as session:
                self.metrics_collector = MetricsCollector(
                    db_session=session,
                    window_size=self.config.get("metrics_window", 3600)
                )
                await self.metrics_collector.initialize()

            self.initialized = True
            logger.info("AI System Integration initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize AI System: {e}")
            await self.shutdown()
            raise

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
        use_semantic_cache: bool = False,
        track_metrics: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a completion request with full integration

        Args:
            prompt: Text prompt
            messages: Chat messages
            model_id: Specific model to use
            max_tokens: Max tokens to generate
            temperature: Sampling temperature
            stream: Enable streaming
            functions: Function definitions
            use_cache: Enable caching
            use_semantic_cache: Enable semantic caching
            track_metrics: Track request metrics
            **kwargs: Additional parameters

        Returns:
            Completion response
        """
        if not self.initialized:
            await self.initialize()

        # Generate cache key
        cache_key = None
        if use_cache:
            import hashlib
            import json
            cache_data = {
                "prompt": prompt,
                "messages": messages,
                "model_id": model_id,
                **kwargs
            }
            cache_str = json.dumps(cache_data, sort_keys=True)
            cache_key = hashlib.sha256(cache_str.encode()).hexdigest()

            # Check cache
            cached_response = await self.cache_manager.get(
                cache_key,
                use_semantic=use_semantic_cache,
                semantic_query=prompt or (messages[-1]["content"] if messages else None)
            )

            if cached_response:
                logger.info(f"Cache hit for key: {cache_key[:8]}...")

                # Track metrics for cached response
                if track_metrics:
                    await self.metrics_collector.record_request(
                        RequestMetrics(
                            model_id=model_id or "cache",
                            provider="cache",
                            request_type="completion",
                            status="cached",
                            latency_ms=0,
                            cache_hit=True
                        )
                    )

                return cached_response

        # Execute request through model manager
        import time
        start_time = time.time()

        try:
            response = await self.model_manager.complete(
                prompt=prompt,
                messages=messages,
                model_id=model_id,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=stream,
                functions=functions,
                use_cache=False,  # We handle caching here
                **kwargs
            )

            latency_ms = (time.time() - start_time) * 1000

            # Cache successful response
            if use_cache and cache_key and not stream:
                await self.cache_manager.set(
                    cache_key,
                    response,
                    ttl=self.config.get("cache_ttl", 3600),
                    generate_embedding=use_semantic_cache,
                    embedding_text=prompt or (messages[-1]["content"] if messages else None)
                )

            # Track metrics
            if track_metrics:
                usage = response.get("usage", {})
                await self.metrics_collector.record_request(
                    RequestMetrics(
                        model_id=response.get("model", model_id or "unknown"),
                        provider=self._get_provider_from_model(response.get("model")),
                        request_type="completion",
                        status="completed",
                        latency_ms=latency_ms,
                        prompt_tokens=usage.get("prompt_tokens", 0),
                        completion_tokens=usage.get("completion_tokens", 0),
                        cost=response.get("cost", 0.0),
                        cache_hit=False
                    )
                )

            return response

        except Exception as e:
            logger.error(f"Completion request failed: {e}")

            # Track failure metrics
            if track_metrics:
                await self.metrics_collector.record_request(
                    RequestMetrics(
                        model_id=model_id or "unknown",
                        provider=self._get_provider_from_model(model_id),
                        request_type="completion",
                        status="failed",
                        latency_ms=(time.time() - start_time) * 1000,
                        error=str(e)
                    )
                )

            raise

    async def embed(
        self,
        text: str,
        model: str = "text-embedding-3-small",
        use_cache: bool = True
    ) -> List[float]:
        """
        Generate embeddings for text

        Args:
            text: Text to embed
            model: Embedding model to use
            use_cache: Whether to use caching

        Returns:
            Embedding vector
        """
        if not self.initialized:
            await self.initialize()

        # Check cache
        if use_cache:
            cache_key = f"embed:{model}:{hashlib.md5(text.encode()).hexdigest()}"
            cached = await self.cache_manager.get(cache_key)
            if cached:
                return cached

        # Generate embedding
        import openai
        client = openai.AsyncOpenAI()
        response = await client.embeddings.create(
            model=model,
            input=text
        )

        embedding = response.data[0].embedding

        # Cache result
        if use_cache:
            await self.cache_manager.set(cache_key, embedding, ttl=86400)  # 24 hours

        return embedding

    async def get_metrics(
        self,
        model_id: str = None,
        time_range: str = "1h"
    ) -> Dict[str, Any]:
        """
        Get performance metrics

        Args:
            model_id: Specific model or None for all
            time_range: Time range for metrics

        Returns:
            Metrics dictionary
        """
        if not self.initialized:
            await self.initialize()

        if model_id:
            return await self.metrics_collector.get_model_metrics(model_id, time_range)
        else:
            # Get metrics for all models
            all_metrics = {}
            for model_id in self.model_manager.models.keys():
                all_metrics[model_id] = await self.metrics_collector.get_model_metrics(
                    model_id, time_range
                )
            return all_metrics

    async def get_model_health(self, model_id: str = None) -> Dict[str, float]:
        """
        Get health scores for models

        Args:
            model_id: Specific model or None for all

        Returns:
            Health scores dictionary
        """
        if not self.initialized:
            await self.initialize()

        health_scores = {}

        if model_id:
            health_scores[model_id] = await self.metrics_collector.calculate_health_score(model_id)
        else:
            for model_id in self.model_manager.models.keys():
                health_scores[model_id] = await self.metrics_collector.calculate_health_score(model_id)

        return health_scores

    async def invalidate_cache(self, pattern: str = None):
        """
        Invalidate cache entries

        Args:
            pattern: Pattern to match for invalidation
        """
        if not self.initialized:
            await self.initialize()

        await self.cache_manager.invalidate(pattern=pattern)

    def _get_provider_from_model(self, model_name: str) -> str:
        """Extract provider from model name"""
        if not model_name:
            return "unknown"

        if "gpt" in model_name.lower():
            return "openai"
        elif "claude" in model_name.lower():
            return "anthropic"
        elif "llama" in model_name.lower():
            return "ollama"
        else:
            return "unknown"

    async def shutdown(self):
        """Shutdown all components"""
        if self.model_manager:
            await self.model_manager.shutdown()

        if self.cache_manager:
            await self.cache_manager.shutdown()

        if self.metrics_collector:
            await self.metrics_collector.shutdown()

        if self.redis_client:
            await self.redis_client.close()

        if self.engine:
            await self.engine.dispose()

        self.initialized = False
        logger.info("AI System Integration shut down")


# Singleton instance
ai_system = AISystemIntegration()


# Context manager for AI operations
@asynccontextmanager
async def ai_context():
    """Context manager for AI operations"""
    if not ai_system.initialized:
        await ai_system.initialize()

    try:
        yield ai_system
    finally:
        pass  # Keep connection alive for reuse


# Convenience functions
async def ai_complete(prompt: str = None, messages: List[Dict] = None, **kwargs):
    """Convenience function for completions"""
    async with ai_context() as ai:
        return await ai.complete(prompt=prompt, messages=messages, **kwargs)


async def ai_embed(text: str, **kwargs):
    """Convenience function for embeddings"""
    async with ai_context() as ai:
        return await ai.embed(text=text, **kwargs)


async def ai_metrics(model_id: str = None, time_range: str = "1h"):
    """Convenience function for getting metrics"""
    async with ai_context() as ai:
        return await ai.get_metrics(model_id=model_id, time_range=time_range)


async def ai_health(model_id: str = None):
    """Convenience function for health check"""
    async with ai_context() as ai:
        return await ai.get_model_health(model_id=model_id)