"""
Metrics Collector for AI Model Performance Monitoring
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from collections import deque, defaultdict
import logging
from dataclasses import dataclass, field
import statistics

import numpy as np
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import prometheus_client as prom

logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNTER = prom.Counter(
    'ai_model_requests_total',
    'Total number of AI model requests',
    ['model_id', 'provider', 'status']
)

REQUEST_DURATION = prom.Histogram(
    'ai_model_request_duration_seconds',
    'AI model request duration',
    ['model_id', 'provider'],
    buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60]
)

TOKEN_COUNTER = prom.Counter(
    'ai_model_tokens_total',
    'Total tokens processed',
    ['model_id', 'provider', 'token_type']
)

COST_COUNTER = prom.Counter(
    'ai_model_cost_total',
    'Total cost of AI model usage',
    ['model_id', 'provider']
)

CACHE_HIT_RATE = prom.Gauge(
    'ai_cache_hit_rate',
    'Cache hit rate percentage'
)

MODEL_HEALTH_SCORE = prom.Gauge(
    'ai_model_health_score',
    'Model health score (0-100)',
    ['model_id', 'provider']
)

@dataclass
class RequestMetrics:
    """Metrics for a single request"""
    model_id: str
    provider: str
    request_type: str
    status: str
    latency_ms: float
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost: float = 0.0
    cache_hit: bool = False
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

@dataclass
class ModelPerformance:
    """Aggregated performance metrics for a model"""
    model_id: str
    provider: str
    window_start: datetime
    window_end: datetime
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    cached_requests: int = 0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_cost: float = 0.0
    latencies: List[float] = field(default_factory=list)
    error_types: Dict[str, int] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0
        return (self.successful_requests / self.total_requests) * 100

    @property
    def error_rate(self) -> float:
        if self.total_requests == 0:
            return 0
        return (self.failed_requests / self.total_requests) * 100

    @property
    def cache_hit_rate(self) -> float:
        if self.total_requests == 0:
            return 0
        return (self.cached_requests / self.total_requests) * 100

    @property
    def avg_latency(self) -> float:
        if not self.latencies:
            return 0
        return statistics.mean(self.latencies)

    @property
    def p50_latency(self) -> float:
        if not self.latencies:
            return 0
        return np.percentile(self.latencies, 50)

    @property
    def p95_latency(self) -> float:
        if not self.latencies:
            return 0
        return np.percentile(self.latencies, 95)

    @property
    def p99_latency(self) -> float:
        if not self.latencies:
            return 0
        return np.percentile(self.latencies, 99)


class MetricsCollector:
    """
    Collects and analyzes metrics for AI model performance
    """

    def __init__(self, db_session: AsyncSession = None, window_size: int = 3600):
        """
        Initialize metrics collector

        Args:
            db_session: Database session for persistence
            window_size: Time window in seconds for metrics aggregation
        """
        self.db_session = db_session
        self.window_size = window_size

        # In-memory metrics storage
        self.request_buffer: deque = deque(maxlen=10000)
        self.model_metrics: Dict[str, ModelPerformance] = {}
        self.hourly_metrics: Dict[str, List[ModelPerformance]] = defaultdict(list)

        # Real-time statistics
        self.realtime_stats: Dict[str, Dict] = defaultdict(lambda: {
            "requests_per_minute": deque(maxlen=60),
            "avg_latency_per_minute": deque(maxlen=60),
            "errors_per_minute": deque(maxlen=60)
        })

        # Anomaly detection
        self.baseline_metrics: Dict[str, Dict] = {}
        self.anomalies: List[Dict] = []

        # Background tasks
        self.background_tasks = []

    async def initialize(self):
        """Initialize metrics collector"""
        # Load historical baselines
        await self._load_baselines()

        # Start background tasks
        self.background_tasks.append(
            asyncio.create_task(self._aggregate_metrics())
        )
        self.background_tasks.append(
            asyncio.create_task(self._persist_metrics())
        )
        self.background_tasks.append(
            asyncio.create_task(self._anomaly_detector())
        )
        self.background_tasks.append(
            asyncio.create_task(self._realtime_aggregator())
        )

        logger.info("Metrics Collector initialized")

    async def record_request(self, metrics: RequestMetrics):
        """
        Record metrics for a request

        Args:
            metrics: Request metrics to record
        """
        # Add to buffer
        self.request_buffer.append(metrics)

        # Update Prometheus metrics
        REQUEST_COUNTER.labels(
            model_id=metrics.model_id,
            provider=metrics.provider,
            status=metrics.status
        ).inc()

        REQUEST_DURATION.labels(
            model_id=metrics.model_id,
            provider=metrics.provider
        ).observe(metrics.latency_ms / 1000)

        if metrics.prompt_tokens > 0:
            TOKEN_COUNTER.labels(
                model_id=metrics.model_id,
                provider=metrics.provider,
                token_type="prompt"
            ).inc(metrics.prompt_tokens)

        if metrics.completion_tokens > 0:
            TOKEN_COUNTER.labels(
                model_id=metrics.model_id,
                provider=metrics.provider,
                token_type="completion"
            ).inc(metrics.completion_tokens)

        if metrics.cost > 0:
            COST_COUNTER.labels(
                model_id=metrics.model_id,
                provider=metrics.provider
            ).inc(metrics.cost)

        # Update current window metrics
        await self._update_current_metrics(metrics)

    async def _update_current_metrics(self, metrics: RequestMetrics):
        """Update current time window metrics"""
        current_time = datetime.utcnow()
        window_key = f"{metrics.model_id}:{current_time.hour}"

        if window_key not in self.model_metrics:
            self.model_metrics[window_key] = ModelPerformance(
                model_id=metrics.model_id,
                provider=metrics.provider,
                window_start=current_time.replace(minute=0, second=0, microsecond=0),
                window_end=current_time.replace(minute=59, second=59, microsecond=999999)
            )

        perf = self.model_metrics[window_key]
        perf.total_requests += 1

        if metrics.status == "completed":
            perf.successful_requests += 1
        else:
            perf.failed_requests += 1
            if metrics.error:
                perf.error_types[metrics.error] = perf.error_types.get(metrics.error, 0) + 1

        if metrics.cache_hit:
            perf.cached_requests += 1

        perf.total_prompt_tokens += metrics.prompt_tokens
        perf.total_completion_tokens += metrics.completion_tokens
        perf.total_cost += metrics.cost
        perf.latencies.append(metrics.latency_ms)

    async def get_model_metrics(
        self,
        model_id: str,
        time_range: str = "1h"
    ) -> Dict[str, Any]:
        """
        Get metrics for a specific model

        Args:
            model_id: Model identifier
            time_range: Time range (1h, 6h, 24h, 7d, 30d)

        Returns:
            Dictionary of metrics
        """
        # Parse time range
        range_map = {
            "1h": timedelta(hours=1),
            "6h": timedelta(hours=6),
            "24h": timedelta(hours=24),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30)
        }
        delta = range_map.get(time_range, timedelta(hours=1))
        start_time = datetime.utcnow() - delta

        # Collect metrics from buffer
        relevant_metrics = [
            m for m in self.request_buffer
            if m.model_id == model_id and m.timestamp > start_time.timestamp()
        ]

        if not relevant_metrics:
            return {
                "model_id": model_id,
                "time_range": time_range,
                "no_data": True
            }

        # Calculate statistics
        total_requests = len(relevant_metrics)
        successful = sum(1 for m in relevant_metrics if m.status == "completed")
        failed = sum(1 for m in relevant_metrics if m.status == "failed")
        cached = sum(1 for m in relevant_metrics if m.cache_hit)

        latencies = [m.latency_ms for m in relevant_metrics]
        costs = [m.cost for m in relevant_metrics]
        prompt_tokens = sum(m.prompt_tokens for m in relevant_metrics)
        completion_tokens = sum(m.completion_tokens for m in relevant_metrics)

        return {
            "model_id": model_id,
            "time_range": time_range,
            "total_requests": total_requests,
            "successful_requests": successful,
            "failed_requests": failed,
            "cached_requests": cached,
            "success_rate": (successful / total_requests * 100) if total_requests > 0 else 0,
            "error_rate": (failed / total_requests * 100) if total_requests > 0 else 0,
            "cache_hit_rate": (cached / total_requests * 100) if total_requests > 0 else 0,
            "latency": {
                "avg": statistics.mean(latencies) if latencies else 0,
                "min": min(latencies) if latencies else 0,
                "max": max(latencies) if latencies else 0,
                "p50": np.percentile(latencies, 50) if latencies else 0,
                "p95": np.percentile(latencies, 95) if latencies else 0,
                "p99": np.percentile(latencies, 99) if latencies else 0
            },
            "tokens": {
                "prompt": prompt_tokens,
                "completion": completion_tokens,
                "total": prompt_tokens + completion_tokens
            },
            "cost": {
                "total": sum(costs),
                "average": statistics.mean(costs) if costs else 0
            }
        }

    async def get_comparative_metrics(
        self,
        model_ids: List[str],
        time_range: str = "24h"
    ) -> Dict[str, Any]:
        """
        Get comparative metrics for multiple models

        Args:
            model_ids: List of model identifiers
            time_range: Time range for comparison

        Returns:
            Comparative metrics dictionary
        """
        metrics = {}
        for model_id in model_ids:
            metrics[model_id] = await self.get_model_metrics(model_id, time_range)

        # Calculate relative performance
        if metrics:
            # Find best performers
            best_latency = min(
                (m["latency"]["avg"] for m in metrics.values() if not m.get("no_data")),
                default=0
            )
            best_success_rate = max(
                (m["success_rate"] for m in metrics.values() if not m.get("no_data")),
                default=0
            )
            lowest_cost = min(
                (m["cost"]["average"] for m in metrics.values() if not m.get("no_data")),
                default=0
            )

            for model_id, m in metrics.items():
                if not m.get("no_data"):
                    m["relative_performance"] = {
                        "latency_ratio": m["latency"]["avg"] / best_latency if best_latency > 0 else 1,
                        "success_rate_ratio": m["success_rate"] / best_success_rate if best_success_rate > 0 else 0,
                        "cost_ratio": m["cost"]["average"] / lowest_cost if lowest_cost > 0 else 1
                    }

        return {
            "models": metrics,
            "time_range": time_range,
            "comparison": {
                "best_latency_model": min(
                    metrics.keys(),
                    key=lambda k: metrics[k]["latency"]["avg"] if not metrics[k].get("no_data") else float('inf')
                ),
                "best_success_rate_model": max(
                    metrics.keys(),
                    key=lambda k: metrics[k]["success_rate"] if not metrics[k].get("no_data") else 0
                ),
                "most_cost_effective_model": min(
                    metrics.keys(),
                    key=lambda k: metrics[k]["cost"]["average"] if not metrics[k].get("no_data") else float('inf')
                )
            }
        }

    async def calculate_health_score(self, model_id: str) -> float:
        """
        Calculate health score for a model (0-100)

        Args:
            model_id: Model identifier

        Returns:
            Health score
        """
        metrics = await self.get_model_metrics(model_id, "1h")

        if metrics.get("no_data"):
            return 100.0  # Assume healthy if no recent data

        score = 100.0

        # Penalize for errors (up to -40 points)
        error_rate = metrics["error_rate"]
        score -= min(error_rate * 0.8, 40)

        # Penalize for high latency (up to -30 points)
        avg_latency = metrics["latency"]["avg"]
        if avg_latency > 5000:
            score -= 30
        elif avg_latency > 2000:
            score -= 20
        elif avg_latency > 1000:
            score -= 10

        # Penalize for no cache hits (up to -10 points)
        cache_hit_rate = metrics["cache_hit_rate"]
        if cache_hit_rate < 10:
            score -= 10
        elif cache_hit_rate < 30:
            score -= 5

        # Check for anomalies (up to -20 points)
        recent_anomalies = [
            a for a in self.anomalies
            if a["model_id"] == model_id and
            datetime.fromisoformat(a["timestamp"]) > datetime.utcnow() - timedelta(hours=1)
        ]
        score -= min(len(recent_anomalies) * 5, 20)

        # Update Prometheus metric
        MODEL_HEALTH_SCORE.labels(
            model_id=model_id,
            provider=metrics.get("provider", "unknown")
        ).set(max(score, 0))

        return max(score, 0)

    async def detect_anomalies(self, model_id: str) -> List[Dict[str, Any]]:
        """
        Detect anomalies in model performance

        Args:
            model_id: Model identifier

        Returns:
            List of detected anomalies
        """
        if model_id not in self.baseline_metrics:
            return []

        current = await self.get_model_metrics(model_id, "1h")
        baseline = self.baseline_metrics[model_id]

        anomalies = []

        # Check latency anomaly (2x baseline)
        if current["latency"]["avg"] > baseline["latency_avg"] * 2:
            anomalies.append({
                "type": "high_latency",
                "severity": "warning",
                "current": current["latency"]["avg"],
                "baseline": baseline["latency_avg"],
                "deviation": current["latency"]["avg"] / baseline["latency_avg"]
            })

        # Check error rate anomaly (5% above baseline)
        if current["error_rate"] > baseline["error_rate"] + 5:
            anomalies.append({
                "type": "high_error_rate",
                "severity": "critical" if current["error_rate"] > 10 else "warning",
                "current": current["error_rate"],
                "baseline": baseline["error_rate"],
                "deviation": current["error_rate"] - baseline["error_rate"]
            })

        # Check request volume anomaly (3x baseline)
        if current["total_requests"] > baseline["avg_requests_per_hour"] * 3:
            anomalies.append({
                "type": "traffic_spike",
                "severity": "info",
                "current": current["total_requests"],
                "baseline": baseline["avg_requests_per_hour"],
                "deviation": current["total_requests"] / baseline["avg_requests_per_hour"]
            })

        return anomalies

    async def _aggregate_metrics(self):
        """Background task to aggregate metrics"""
        while True:
            try:
                await asyncio.sleep(60)  # Every minute

                current_time = datetime.utcnow()
                hour_ago = current_time - timedelta(hours=1)

                # Clean old metrics from buffer
                cutoff_timestamp = hour_ago.timestamp()
                while self.request_buffer and self.request_buffer[0].timestamp < cutoff_timestamp:
                    self.request_buffer.popleft()

                # Update cache hit rate gauge
                if self.request_buffer:
                    recent_requests = list(self.request_buffer)[-100:]  # Last 100 requests
                    cache_hits = sum(1 for r in recent_requests if r.cache_hit)
                    CACHE_HIT_RATE.set(cache_hits)

            except Exception as e:
                logger.error(f"Metrics aggregation failed: {e}")

    async def _persist_metrics(self):
        """Background task to persist metrics to database"""
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes

                if not self.db_session:
                    continue

                for key, perf in list(self.model_metrics.items()):
                    # Only persist completed windows
                    if perf.window_end < datetime.utcnow():
                        await self._save_to_database(perf)
                        del self.model_metrics[key]

            except Exception as e:
                logger.error(f"Metrics persistence failed: {e}")

    async def _save_to_database(self, perf: ModelPerformance):
        """Save performance metrics to database"""
        if not self.db_session:
            return

        try:
            await self.db_session.execute(
                """
                INSERT INTO model_performance_metrics (
                    model_id, metric_date, metric_hour,
                    total_requests, successful_requests, failed_requests,
                    cached_requests, total_prompt_tokens, total_completion_tokens,
                    avg_latency_ms, p50_latency_ms, p95_latency_ms, p99_latency_ms,
                    total_cost, error_rate, cache_hit_rate
                ) VALUES (
                    :model_id, :date, :hour,
                    :total, :success, :failed,
                    :cached, :prompt_tokens, :completion_tokens,
                    :avg_latency, :p50, :p95, :p99,
                    :cost, :error_rate, :cache_rate
                )
                ON CONFLICT (model_id, metric_date, metric_hour) DO UPDATE
                SET total_requests = model_performance_metrics.total_requests + :total,
                    successful_requests = model_performance_metrics.successful_requests + :success,
                    failed_requests = model_performance_metrics.failed_requests + :failed,
                    updated_at = CURRENT_TIMESTAMP
                """,
                {
                    "model_id": perf.model_id,
                    "date": perf.window_start.date(),
                    "hour": perf.window_start.hour,
                    "total": perf.total_requests,
                    "success": perf.successful_requests,
                    "failed": perf.failed_requests,
                    "cached": perf.cached_requests,
                    "prompt_tokens": perf.total_prompt_tokens,
                    "completion_tokens": perf.total_completion_tokens,
                    "avg_latency": perf.avg_latency,
                    "p50": perf.p50_latency,
                    "p95": perf.p95_latency,
                    "p99": perf.p99_latency,
                    "cost": perf.total_cost,
                    "error_rate": perf.error_rate,
                    "cache_rate": perf.cache_hit_rate
                }
            )
            await self.db_session.commit()

            # Add to hourly metrics history
            self.hourly_metrics[perf.model_id].append(perf)
            if len(self.hourly_metrics[perf.model_id]) > 168:  # Keep 7 days
                self.hourly_metrics[perf.model_id] = self.hourly_metrics[perf.model_id][-168:]

        except Exception as e:
            logger.error(f"Failed to save metrics to database: {e}")

    async def _load_baselines(self):
        """Load baseline metrics from historical data"""
        if not self.db_session:
            return

        try:
            # Get last 7 days of data for baselines
            week_ago = datetime.utcnow() - timedelta(days=7)

            query = """
                SELECT model_id,
                       AVG(avg_latency_ms) as latency_avg,
                       AVG(error_rate) as error_rate,
                       AVG(total_requests) as avg_requests_per_hour
                FROM model_performance_metrics
                WHERE metric_date >= :start_date
                GROUP BY model_id
            """

            result = await self.db_session.execute(query, {"start_date": week_ago})

            for row in result:
                self.baseline_metrics[row.model_id] = {
                    "latency_avg": float(row.latency_avg or 0),
                    "error_rate": float(row.error_rate or 0),
                    "avg_requests_per_hour": float(row.avg_requests_per_hour or 0)
                }

            logger.info(f"Loaded baselines for {len(self.baseline_metrics)} models")

        except Exception as e:
            logger.error(f"Failed to load baselines: {e}")

    async def _anomaly_detector(self):
        """Background task for anomaly detection"""
        while True:
            try:
                await asyncio.sleep(60)  # Every minute

                for model_id in self.baseline_metrics.keys():
                    anomalies = await self.detect_anomalies(model_id)

                    for anomaly in anomalies:
                        anomaly_record = {
                            "model_id": model_id,
                            "timestamp": datetime.utcnow().isoformat(),
                            **anomaly
                        }
                        self.anomalies.append(anomaly_record)

                        # Log critical anomalies
                        if anomaly["severity"] == "critical":
                            logger.error(f"Critical anomaly detected for {model_id}: {anomaly}")

                # Keep only recent anomalies (last 24 hours)
                cutoff = datetime.utcnow() - timedelta(hours=24)
                self.anomalies = [
                    a for a in self.anomalies
                    if datetime.fromisoformat(a["timestamp"]) > cutoff
                ]

            except Exception as e:
                logger.error(f"Anomaly detection failed: {e}")

    async def _realtime_aggregator(self):
        """Aggregate real-time statistics"""
        while True:
            try:
                await asyncio.sleep(1)  # Every second

                current_minute = int(time.time() / 60)

                for model_id in self.realtime_stats.keys():
                    stats = self.realtime_stats[model_id]

                    # Count requests in current minute
                    minute_requests = [
                        m for m in self.request_buffer
                        if m.model_id == model_id and
                        int(m.timestamp / 60) == current_minute
                    ]

                    if minute_requests:
                        stats["requests_per_minute"].append(len(minute_requests))

                        latencies = [m.latency_ms for m in minute_requests]
                        stats["avg_latency_per_minute"].append(
                            statistics.mean(latencies) if latencies else 0
                        )

                        errors = sum(1 for m in minute_requests if m.status == "failed")
                        stats["errors_per_minute"].append(errors)

            except Exception as e:
                logger.error(f"Real-time aggregation failed: {e}")

    async def shutdown(self):
        """Shutdown metrics collector"""
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()

        # Final metrics persistence
        for perf in self.model_metrics.values():
            await self._save_to_database(perf)

        logger.info("Metrics Collector shut down")