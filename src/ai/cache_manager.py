"""
Advanced Cache Manager with Semantic Caching Support
"""

import asyncio
import hashlib
import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

import redis.asyncio as redis
from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
import openai

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Represents a cache entry"""
    key: str
    value: Any
    embedding: Optional[np.ndarray] = None
    ttl: int = 3600
    created_at: float = None
    access_count: int = 0
    last_accessed: float = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()
        if self.last_accessed is None:
            self.last_accessed = time.time()
        if self.metadata is None:
            self.metadata = {}


class CacheManager:
    """
    Advanced cache manager with multiple caching strategies
    """

    def __init__(
        self,
        redis_client: redis.Redis = None,
        db_session: AsyncSession = None,
        embedding_model: str = "text-embedding-3-small",
        similarity_threshold: float = 0.85,
        max_memory_cache: int = 1000
    ):
        """
        Initialize Cache Manager

        Args:
            redis_client: Redis client for fast caching
            db_session: Database session for persistent caching
            embedding_model: Model for generating embeddings
            similarity_threshold: Threshold for semantic similarity
            max_memory_cache: Maximum items in memory cache
        """
        self.redis_client = redis_client
        self.db_session = db_session
        self.embedding_model = embedding_model
        self.similarity_threshold = similarity_threshold
        self.max_memory_cache = max_memory_cache

        # In-memory cache for ultra-fast access
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.memory_cache_order: List[str] = []

        # Semantic cache
        self.semantic_cache: List[CacheEntry] = []
        self.embeddings_matrix: Optional[np.ndarray] = None

        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "semantic_hits": 0,
            "evictions": 0
        }

        # Background tasks
        self.background_tasks = []

    async def initialize(self):
        """Initialize cache manager and load existing cache"""
        # Load semantic cache from database
        if self.db_session:
            await self._load_semantic_cache()

        # Start background tasks
        self.background_tasks.append(
            asyncio.create_task(self._cleanup_expired())
        )
        self.background_tasks.append(
            asyncio.create_task(self._sync_cache())
        )

        logger.info("Cache Manager initialized")

    async def get(
        self,
        key: str,
        use_semantic: bool = False,
        semantic_query: str = None
    ) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key
            use_semantic: Whether to use semantic search if exact key not found
            semantic_query: Query for semantic search

        Returns:
            Cached value or None
        """
        # Check memory cache first
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if self._is_valid(entry):
                self._update_access(entry)
                self.stats["hits"] += 1
                return entry.value
            else:
                del self.memory_cache[key]

        # Check Redis cache
        if self.redis_client:
            try:
                value = await self.redis_client.get(f"cache:{key}")
                if value:
                    self.stats["hits"] += 1
                    # Add to memory cache
                    await self._add_to_memory_cache(key, json.loads(value))
                    return json.loads(value)
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")

        # Check database cache
        if self.db_session:
            try:
                query = select("ai_response_cache").where(
                    and_(
                        "cache_key == key",
                        or_("expires_at IS NULL", "expires_at > CURRENT_TIMESTAMP")
                    )
                )
                result = await self.db_session.execute(query)
                row = result.first()

                if row:
                    self.stats["hits"] += 1
                    value = json.loads(row.response)
                    # Update hit count
                    await self._update_db_hit_count(row.id)
                    # Add to faster caches
                    await self._add_to_memory_cache(key, value)
                    if self.redis_client:
                        await self._add_to_redis(key, value)
                    return value
            except Exception as e:
                logger.warning(f"Database cache get failed: {e}")

        # Try semantic search if enabled
        if use_semantic and semantic_query and self.semantic_cache:
            result = await self._semantic_search(semantic_query)
            if result:
                self.stats["semantic_hits"] += 1
                return result

        self.stats["misses"] += 1
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600,
        generate_embedding: bool = False,
        embedding_text: str = None
    ):
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            generate_embedding: Whether to generate embedding for semantic search
            embedding_text: Text to generate embedding from
        """
        entry = CacheEntry(
            key=key,
            value=value,
            ttl=ttl
        )

        # Generate embedding if requested
        if generate_embedding and embedding_text:
            entry.embedding = await self._generate_embedding(embedding_text)

        # Add to all cache levels
        await self._add_to_memory_cache(key, value, ttl)

        if self.redis_client:
            await self._add_to_redis(key, value, ttl)

        if self.db_session:
            await self._add_to_database(key, value, ttl, entry.embedding)

        # Add to semantic cache if embedding exists
        if entry.embedding is not None:
            await self._add_to_semantic_cache(entry)

    async def invalidate(self, key: str = None, pattern: str = None):
        """
        Invalidate cache entries

        Args:
            key: Specific key to invalidate
            pattern: Pattern to match keys for invalidation
        """
        if key:
            # Remove from memory cache
            if key in self.memory_cache:
                del self.memory_cache[key]
                self.memory_cache_order.remove(key)

            # Remove from Redis
            if self.redis_client:
                try:
                    await self.redis_client.delete(f"cache:{key}")
                except Exception as e:
                    logger.warning(f"Redis delete failed: {e}")

            # Remove from database
            if self.db_session:
                try:
                    await self.db_session.execute(
                        delete("ai_response_cache").where("cache_key == key")
                    )
                    await self.db_session.commit()
                except Exception as e:
                    logger.warning(f"Database delete failed: {e}")

        elif pattern:
            # Pattern-based invalidation
            keys_to_remove = [
                k for k in self.memory_cache.keys()
                if self._match_pattern(k, pattern)
            ]

            for k in keys_to_remove:
                await self.invalidate(key=k)

    async def _semantic_search(self, query: str, top_k: int = 1) -> Optional[Any]:
        """
        Perform semantic search in cache

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            Best matching cached value or None
        """
        if not self.semantic_cache or self.embeddings_matrix is None:
            return None

        # Generate embedding for query
        query_embedding = await self._generate_embedding(query)
        if query_embedding is None:
            return None

        # Calculate similarities
        similarities = cosine_similarity(
            query_embedding.reshape(1, -1),
            self.embeddings_matrix
        )[0]

        # Find best matches
        best_indices = np.argsort(similarities)[-top_k:][::-1]

        for idx in best_indices:
            if similarities[idx] >= self.similarity_threshold:
                entry = self.semantic_cache[idx]
                if self._is_valid(entry):
                    self._update_access(entry)
                    return entry.value

        return None

    async def _generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """Generate embedding for text"""
        try:
            client = openai.AsyncOpenAI()
            response = await client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return np.array(response.data[0].embedding)
        except Exception as e:
            logger.warning(f"Failed to generate embedding: {e}")
            return None

    async def _add_to_memory_cache(self, key: str, value: Any, ttl: int = 3600):
        """Add entry to memory cache with LRU eviction"""
        # Check if we need to evict
        if len(self.memory_cache) >= self.max_memory_cache:
            # Evict least recently used
            lru_key = self.memory_cache_order[0]
            del self.memory_cache[lru_key]
            self.memory_cache_order.remove(lru_key)
            self.stats["evictions"] += 1

        # Add new entry
        entry = CacheEntry(key=key, value=value, ttl=ttl)
        self.memory_cache[key] = entry

        # Update order for LRU
        if key in self.memory_cache_order:
            self.memory_cache_order.remove(key)
        self.memory_cache_order.append(key)

    async def _add_to_redis(self, key: str, value: Any, ttl: int = 3600):
        """Add entry to Redis cache"""
        if not self.redis_client:
            return

        try:
            await self.redis_client.setex(
                f"cache:{key}",
                ttl,
                json.dumps(value)
            )
        except Exception as e:
            logger.warning(f"Redis set failed: {e}")

    async def _add_to_database(
        self,
        key: str,
        value: Any,
        ttl: int,
        embedding: np.ndarray = None
    ):
        """Add entry to database cache"""
        if not self.db_session:
            return

        try:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl) if ttl > 0 else None

            await self.db_session.execute(
                """
                INSERT INTO ai_response_cache (
                    cache_key, request_hash, response, embedding, expires_at
                ) VALUES (
                    :key, :hash, :response, :embedding, :expires
                )
                ON CONFLICT (cache_key) DO UPDATE
                SET response = :response,
                    embedding = :embedding,
                    expires_at = :expires,
                    updated_at = CURRENT_TIMESTAMP
                """,
                {
                    "key": key,
                    "hash": hashlib.sha256(key.encode()).hexdigest(),
                    "response": json.dumps(value),
                    "embedding": embedding.tolist() if embedding is not None else None,
                    "expires": expires_at
                }
            )
            await self.db_session.commit()
        except Exception as e:
            logger.warning(f"Database cache set failed: {e}")

    async def _add_to_semantic_cache(self, entry: CacheEntry):
        """Add entry to semantic cache"""
        self.semantic_cache.append(entry)

        # Update embeddings matrix
        if self.embeddings_matrix is None:
            self.embeddings_matrix = entry.embedding.reshape(1, -1)
        else:
            self.embeddings_matrix = np.vstack([
                self.embeddings_matrix,
                entry.embedding.reshape(1, -1)
            ])

        # Limit semantic cache size
        if len(self.semantic_cache) > 1000:
            # Remove oldest entries
            self.semantic_cache = self.semantic_cache[-1000:]
            self.embeddings_matrix = self.embeddings_matrix[-1000:]

    async def _load_semantic_cache(self):
        """Load semantic cache from database"""
        if not self.db_session:
            return

        try:
            query = select("ai_response_cache").where(
                and_(
                    "embedding IS NOT NULL",
                    or_("expires_at IS NULL", "expires_at > CURRENT_TIMESTAMP")
                )
            ).order_by("hit_count DESC").limit(1000)

            result = await self.db_session.execute(query)

            embeddings = []
            for row in result:
                entry = CacheEntry(
                    key=row.cache_key,
                    value=json.loads(row.response),
                    embedding=np.array(row.embedding),
                    metadata=row.metadata
                )
                self.semantic_cache.append(entry)
                embeddings.append(row.embedding)

            if embeddings:
                self.embeddings_matrix = np.array(embeddings)

            logger.info(f"Loaded {len(self.semantic_cache)} entries into semantic cache")
        except Exception as e:
            logger.warning(f"Failed to load semantic cache: {e}")

    async def _update_db_hit_count(self, cache_id: str):
        """Update hit count in database"""
        if not self.db_session:
            return

        try:
            await self.db_session.execute(
                update("ai_response_cache")
                .where("id == cache_id")
                .values(
                    hit_count="hit_count + 1",
                    last_accessed_at=datetime.utcnow()
                )
            )
            await self.db_session.commit()
        except Exception as e:
            logger.warning(f"Failed to update hit count: {e}")

    def _is_valid(self, entry: CacheEntry) -> bool:
        """Check if cache entry is still valid"""
        if entry.ttl <= 0:
            return True  # No expiration

        age = time.time() - entry.created_at
        return age < entry.ttl

    def _update_access(self, entry: CacheEntry):
        """Update access statistics for entry"""
        entry.access_count += 1
        entry.last_accessed = time.time()

        # Update LRU order
        if entry.key in self.memory_cache_order:
            self.memory_cache_order.remove(entry.key)
            self.memory_cache_order.append(entry.key)

    def _match_pattern(self, key: str, pattern: str) -> bool:
        """Check if key matches pattern (simple wildcard support)"""
        import fnmatch
        return fnmatch.fnmatch(key, pattern)

    async def _cleanup_expired(self):
        """Background task to clean up expired entries"""
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes

                # Clean memory cache
                expired_keys = [
                    k for k, v in self.memory_cache.items()
                    if not self._is_valid(v)
                ]
                for key in expired_keys:
                    del self.memory_cache[key]
                    if key in self.memory_cache_order:
                        self.memory_cache_order.remove(key)

                # Clean database cache
                if self.db_session:
                    await self.db_session.execute(
                        delete("ai_response_cache").where(
                            and_(
                                "expires_at IS NOT NULL",
                                "expires_at < CURRENT_TIMESTAMP"
                            )
                        )
                    )
                    await self.db_session.commit()

                logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

            except Exception as e:
                logger.error(f"Cache cleanup failed: {e}")

    async def _sync_cache(self):
        """Sync cache between different levels"""
        while True:
            try:
                await asyncio.sleep(60)  # Every minute

                # Sync hot entries from database to Redis
                if self.db_session and self.redis_client:
                    query = select("ai_response_cache").where(
                        "hit_count > 10"
                    ).order_by("hit_count DESC").limit(100)

                    result = await self.db_session.execute(query)

                    for row in result:
                        if row.cache_key not in self.memory_cache:
                            ttl_seconds = 3600
                            if row.expires_at:
                                ttl_seconds = max(
                                    1,
                                    int((row.expires_at - datetime.utcnow()).total_seconds())
                                )

                            await self._add_to_redis(
                                row.cache_key,
                                json.loads(row.response),
                                ttl_seconds
                            )

            except Exception as e:
                logger.error(f"Cache sync failed: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0

        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "semantic_hits": self.stats["semantic_hits"],
            "evictions": self.stats["evictions"],
            "hit_rate": round(hit_rate, 2),
            "memory_cache_size": len(self.memory_cache),
            "semantic_cache_size": len(self.semantic_cache)
        }

    async def shutdown(self):
        """Shutdown cache manager"""
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()

        logger.info("Cache Manager shut down")