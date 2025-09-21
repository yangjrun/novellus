#!/usr/bin/env python3
"""
Simplified AI System Integration Test for Novellus Project
Tests core AI infrastructure without requiring external API keys
"""

import asyncio
import json
import time
import traceback
from datetime import datetime
import numpy as np
import logging
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test configuration
POSTGRES_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"


class AIIntegrationVerifier:
    """Verify AI system integration status"""

    def __init__(self):
        self.engine = None
        self.async_session = None
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "issues": [],
            "recommendations": []
        }

    async def setup(self):
        """Initialize database connection"""
        try:
            self.engine = create_async_engine(POSTGRES_URL, echo=False, pool_pre_ping=True)
            self.async_session = async_sessionmaker(self.engine, expire_on_commit=False)

            # Test connection
            async with self.async_session() as session:
                result = await session.execute(text("SELECT version()"))
                version = result.scalar()
                logger.info(f"✓ Connected to PostgreSQL: {version}")
                return True

        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            self.results["issues"].append(f"Database connection failed: {str(e)}")
            return False

    async def teardown(self):
        """Cleanup resources"""
        if self.engine:
            await self.engine.dispose()

    async def verify_pgvector(self):
        """Verify pgvector extension status"""
        logger.info("\n1. VERIFYING PGVECTOR EXTENSION")
        logger.info("-" * 40)

        try:
            async with self.async_session() as session:
                # Check if pgvector is installed
                result = await session.execute(text("""
                    SELECT extname, extversion
                    FROM pg_extension
                    WHERE extname = 'vector'
                """))
                pgvector_info = result.first()

                if pgvector_info:
                    logger.info(f"✓ pgvector {pgvector_info.extversion} is installed")
                    self.results["components"]["pgvector"] = {
                        "status": "installed",
                        "version": pgvector_info.extversion
                    }
                else:
                    logger.warning("✗ pgvector extension not found")
                    logger.info("  Installing pgvector...")

                    await session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                    await session.commit()

                    # Verify installation
                    result = await session.execute(text("""
                        SELECT extversion FROM pg_extension WHERE extname = 'vector'
                    """))
                    version = result.scalar()

                    if version:
                        logger.info(f"✓ pgvector {version} installed successfully")
                        self.results["components"]["pgvector"] = {
                            "status": "installed",
                            "version": version
                        }
                    else:
                        raise Exception("Failed to install pgvector")

                # Test vector operations
                logger.info("  Testing vector operations...")

                # Create test table
                await session.execute(text("""
                    CREATE TABLE IF NOT EXISTS vector_test_verify (
                        id SERIAL PRIMARY KEY,
                        embedding vector(3)
                    )
                """))
                await session.commit()

                # Insert test vector
                test_vector = "[0.1, 0.2, 0.3]"
                await session.execute(text(f"""
                    INSERT INTO vector_test_verify (embedding)
                    VALUES ('{test_vector}'::vector)
                    ON CONFLICT DO NOTHING
                """))
                await session.commit()

                # Test similarity search
                result = await session.execute(text("""
                    SELECT embedding <-> '[0.11, 0.21, 0.31]'::vector as distance
                    FROM vector_test_verify
                    LIMIT 1
                """))
                distance = result.scalar()

                if distance is not None:
                    logger.info(f"✓ Vector similarity search working (distance: {distance:.4f})")
                    self.results["components"]["pgvector"]["operations"] = "working"
                else:
                    raise Exception("Vector operations failed")

                # Cleanup
                await session.execute(text("DROP TABLE IF EXISTS vector_test_verify"))
                await session.commit()

                return True

        except Exception as e:
            logger.error(f"✗ pgvector verification failed: {e}")
            self.results["issues"].append(f"pgvector: {str(e)}")
            self.results["recommendations"].append(
                "Ensure pgvector extension is properly installed: CREATE EXTENSION vector;"
            )
            return False

    async def verify_ai_tables(self):
        """Verify AI-related database tables"""
        logger.info("\n2. VERIFYING AI DATABASE SCHEMA")
        logger.info("-" * 40)

        required_tables = {
            "ai_models": [
                "id", "provider", "model_name", "display_name",
                "max_tokens", "temperature", "status"
            ],
            "ai_requests": [
                "id", "model_id", "request_type", "prompt",
                "status", "created_at"
            ],
            "ai_response_cache": [
                "id", "cache_key", "response", "created_at"
            ],
            "model_performance_metrics": [
                "id", "model_id", "total_requests", "avg_latency_ms"
            ]
        }

        tables_status = {}

        try:
            async with self.async_session() as session:
                for table_name, required_columns in required_tables.items():
                    # Check if table exists
                    result = await session.execute(text(f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables
                            WHERE table_schema = 'public'
                            AND table_name = '{table_name}'
                        )
                    """))

                    exists = result.scalar()

                    if exists:
                        # Check columns
                        result = await session.execute(text(f"""
                            SELECT column_name
                            FROM information_schema.columns
                            WHERE table_schema = 'public'
                            AND table_name = '{table_name}'
                        """))

                        columns = [row[0] for row in result]
                        missing_columns = [col for col in required_columns if col not in columns]

                        if missing_columns:
                            logger.warning(f"⚠ Table '{table_name}' missing columns: {missing_columns}")
                            tables_status[table_name] = "incomplete"
                        else:
                            logger.info(f"✓ Table '{table_name}' structure verified")
                            tables_status[table_name] = "ready"
                    else:
                        logger.warning(f"✗ Table '{table_name}' not found")
                        tables_status[table_name] = "missing"

                        # Create the table
                        logger.info(f"  Creating table '{table_name}'...")
                        await self._create_ai_table(session, table_name)
                        tables_status[table_name] = "created"

                self.results["components"]["ai_tables"] = tables_status
                return all(status in ["ready", "created"] for status in tables_status.values())

        except Exception as e:
            logger.error(f"✗ AI tables verification failed: {e}")
            self.results["issues"].append(f"AI tables: {str(e)}")
            return False

    async def _create_ai_table(self, session, table_name):
        """Create missing AI tables"""
        table_definitions = {
            "ai_models": """
                CREATE TABLE ai_models (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    provider VARCHAR(50) NOT NULL,
                    model_name VARCHAR(255) NOT NULL,
                    display_name VARCHAR(255) NOT NULL,
                    api_endpoint TEXT,
                    api_key_encrypted TEXT,
                    max_tokens INTEGER DEFAULT 4096,
                    temperature FLOAT DEFAULT 0.7,
                    input_token_cost DECIMAL(10, 6) DEFAULT 0,
                    output_token_cost DECIMAL(10, 6) DEFAULT 0,
                    supports_streaming BOOLEAN DEFAULT TRUE,
                    supports_function_calling BOOLEAN DEFAULT FALSE,
                    context_window INTEGER DEFAULT 4096,
                    requests_per_minute INTEGER DEFAULT 60,
                    priority INTEGER DEFAULT 100,
                    status VARCHAR(20) DEFAULT 'active',
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "ai_requests": """
                CREATE TABLE ai_requests (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    model_id VARCHAR(255),
                    request_type VARCHAR(50),
                    prompt TEXT,
                    messages JSONB,
                    response JSONB,
                    status VARCHAR(20),
                    latency_ms INTEGER,
                    prompt_tokens INTEGER,
                    completion_tokens INTEGER,
                    estimated_cost DECIMAL(10, 6),
                    cache_hit BOOLEAN DEFAULT FALSE,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "ai_response_cache": """
                CREATE TABLE ai_response_cache (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    cache_key VARCHAR(255) UNIQUE NOT NULL,
                    request_hash VARCHAR(255),
                    response TEXT NOT NULL,
                    hit_count INTEGER DEFAULT 0,
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "model_performance_metrics": """
                CREATE TABLE model_performance_metrics (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    model_id VARCHAR(255),
                    metric_date DATE,
                    metric_hour INTEGER,
                    total_requests INTEGER DEFAULT 0,
                    successful_requests INTEGER DEFAULT 0,
                    failed_requests INTEGER DEFAULT 0,
                    total_prompt_tokens INTEGER DEFAULT 0,
                    total_completion_tokens INTEGER DEFAULT 0,
                    avg_latency_ms FLOAT,
                    total_cost DECIMAL(10, 6),
                    error_rate FLOAT,
                    cache_hit_rate FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(model_id, metric_date, metric_hour)
                )
            """
        }

        if table_name in table_definitions:
            await session.execute(text(table_definitions[table_name]))
            await session.commit()
            logger.info(f"  ✓ Table '{table_name}' created successfully")

    async def verify_cache_system(self):
        """Verify caching infrastructure"""
        logger.info("\n3. VERIFYING CACHE SYSTEM")
        logger.info("-" * 40)

        cache_status = {}

        try:
            # Check Redis availability
            try:
                import redis.asyncio as redis
                redis_client = await redis.from_url("redis://localhost:6379", decode_responses=True)
                await redis_client.ping()
                logger.info("✓ Redis cache available and responding")
                cache_status["redis"] = "available"
                await redis_client.close()
            except:
                logger.warning("⚠ Redis not available (will use database cache)")
                cache_status["redis"] = "unavailable"
                self.results["recommendations"].append(
                    "Consider installing Redis for improved cache performance: docker run -p 6379:6379 redis"
                )

            # Check database cache table
            async with self.async_session() as session:
                result = await session.execute(text("""
                    SELECT COUNT(*) FROM ai_response_cache
                    WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
                """))
                recent_cache_entries = result.scalar() or 0

                logger.info(f"  Database cache entries (last 24h): {recent_cache_entries}")
                cache_status["database_cache"] = "working"
                cache_status["recent_entries"] = recent_cache_entries

            # Check semantic cache capability
            async with self.async_session() as session:
                # Create semantic cache table if not exists
                await session.execute(text("""
                    CREATE TABLE IF NOT EXISTS semantic_cache (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        content TEXT NOT NULL,
                        embedding vector(1536),
                        response TEXT,
                        similarity_threshold FLOAT DEFAULT 0.85,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                await session.commit()

                logger.info("✓ Semantic cache table ready")
                cache_status["semantic_cache"] = "ready"

            self.results["components"]["cache_system"] = cache_status
            return True

        except Exception as e:
            logger.error(f"✗ Cache system verification failed: {e}")
            self.results["issues"].append(f"Cache system: {str(e)}")
            return False

    async def verify_model_configuration(self):
        """Verify AI model configurations"""
        logger.info("\n4. VERIFYING MODEL CONFIGURATION")
        logger.info("-" * 40)

        try:
            async with self.async_session() as session:
                # Check configured models
                result = await session.execute(text("""
                    SELECT provider, model_name, status, COUNT(*) as count
                    FROM ai_models
                    GROUP BY provider, model_name, status
                """))

                models = result.all()

                if models:
                    logger.info("  Configured models:")
                    for model in models:
                        status_icon = "✓" if model.status == "active" else "✗"
                        logger.info(f"  {status_icon} {model.provider}/{model.model_name}: {model.status}")

                    self.results["components"]["models"] = [
                        {"provider": m.provider, "model": m.model_name, "status": m.status}
                        for m in models
                    ]
                else:
                    logger.warning("⚠ No AI models configured")
                    logger.info("  Adding default test models...")

                    # Add default models for testing
                    test_models = [
                        ("openai", "gpt-4o-mini", "GPT-4 Optimized Mini"),
                        ("anthropic", "claude-3-haiku", "Claude 3 Haiku"),
                        ("ollama", "llama3.2", "Llama 3.2 (Local)")
                    ]

                    for provider, model_name, display_name in test_models:
                        await session.execute(text("""
                            INSERT INTO ai_models (provider, model_name, display_name)
                            VALUES (:provider, :model, :display)
                            ON CONFLICT DO NOTHING
                        """), {
                            "provider": provider,
                            "model": model_name,
                            "display": display_name
                        })
                    await session.commit()

                    logger.info("  ✓ Default test models added")
                    self.results["components"]["models"] = "configured"

                return True

        except Exception as e:
            logger.error(f"✗ Model configuration verification failed: {e}")
            self.results["issues"].append(f"Model configuration: {str(e)}")
            return False

    async def verify_performance_metrics(self):
        """Verify performance tracking system"""
        logger.info("\n5. VERIFYING PERFORMANCE METRICS")
        logger.info("-" * 40)

        try:
            async with self.async_session() as session:
                # Check recent metrics
                result = await session.execute(text("""
                    SELECT
                        COUNT(DISTINCT model_id) as models_tracked,
                        SUM(total_requests) as total_requests,
                        AVG(avg_latency_ms) as avg_latency,
                        AVG(cache_hit_rate) as avg_cache_hit_rate
                    FROM model_performance_metrics
                    WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '7 days'
                """))

                metrics = result.first()

                if metrics and metrics.total_requests:
                    logger.info(f"  Models tracked: {metrics.models_tracked}")
                    logger.info(f"  Total requests (7d): {metrics.total_requests}")
                    logger.info(f"  Average latency: {metrics.avg_latency:.2f}ms")
                    logger.info(f"  Cache hit rate: {metrics.avg_cache_hit_rate:.1f}%")

                    self.results["components"]["metrics"] = {
                        "status": "active",
                        "models_tracked": metrics.models_tracked,
                        "total_requests": metrics.total_requests
                    }
                else:
                    logger.info("  No performance metrics recorded yet")
                    self.results["components"]["metrics"] = {
                        "status": "no_data"
                    }

                # Check if metrics tables have proper indexes
                result = await session.execute(text("""
                    SELECT indexname
                    FROM pg_indexes
                    WHERE tablename = 'model_performance_metrics'
                """))

                indexes = [row[0] for row in result]
                if indexes:
                    logger.info(f"  ✓ Performance indexes configured: {len(indexes)}")
                else:
                    logger.warning("  ⚠ No indexes on metrics table")
                    self.results["recommendations"].append(
                        "Create indexes on model_performance_metrics for better query performance"
                    )

                return True

        except Exception as e:
            logger.error(f"✗ Performance metrics verification failed: {e}")
            self.results["issues"].append(f"Performance metrics: {str(e)}")
            return False

    async def run_integration_test(self):
        """Run a simple integration test"""
        logger.info("\n6. RUNNING INTEGRATION TEST")
        logger.info("-" * 40)

        try:
            async with self.async_session() as session:
                # Simulate an AI request
                test_request = {
                    "model_id": "test-model",
                    "type": "completion",
                    "prompt": "Test prompt for integration",
                    "status": "completed",
                    "latency": 150,
                    "p_tokens": 10,
                    "c_tokens": 20,
                    "cost": 0.00001
                }

                # Insert test request
                await session.execute(text("""
                    INSERT INTO ai_requests (
                        model_id, request_type, prompt, status,
                        latency_ms, prompt_tokens, completion_tokens, estimated_cost
                    ) VALUES (
                        :model_id, :type, :prompt, :status,
                        :latency, :p_tokens, :c_tokens, :cost
                    )
                """), test_request)
                await session.commit()

                # Test cache insertion
                cache_key = f"test_cache_{time.time()}"
                await session.execute(text("""
                    INSERT INTO ai_response_cache (cache_key, response)
                    VALUES (:key, :response)
                """), {
                    "key": cache_key,
                    "response": json.dumps({"test": "response"})
                })
                await session.commit()

                # Verify retrieval
                result = await session.execute(text("""
                    SELECT response FROM ai_response_cache
                    WHERE cache_key = :key
                """), {"key": cache_key})

                cached = result.scalar()
                if cached:
                    logger.info("✓ End-to-end data flow test passed")
                    self.results["components"]["integration_test"] = "passed"
                    return True
                else:
                    raise Exception("Cache retrieval failed")

        except Exception as e:
            logger.error(f"✗ Integration test failed: {e}")
            self.results["issues"].append(f"Integration test: {str(e)}")
            return False

    async def generate_report(self):
        """Generate final integration status report"""
        logger.info("\n" + "="*60)
        logger.info("AI SYSTEM INTEGRATION STATUS REPORT")
        logger.info("="*60)

        # Component status
        logger.info("\n📊 COMPONENT STATUS:")
        for component, status in self.results["components"].items():
            if isinstance(status, dict) and "status" in status:
                icon = "✓" if status["status"] in ["ready", "active", "working"] else "⚠"
                logger.info(f"  {icon} {component}: {status['status']}")
            else:
                logger.info(f"  • {component}: {status}")

        # Issues found
        if self.results["issues"]:
            logger.info("\n⚠️  ISSUES FOUND:")
            for issue in self.results["issues"]:
                logger.info(f"  - {issue}")

        # Recommendations
        if self.results["recommendations"]:
            logger.info("\n💡 RECOMMENDATIONS:")
            for rec in self.results["recommendations"]:
                logger.info(f"  - {rec}")

        # Overall status
        total_components = len(self.results["components"])
        working_components = sum(
            1 for c in self.results["components"].values()
            if (isinstance(c, dict) and c.get("status") in ["ready", "active", "working", "installed"])
            or (isinstance(c, str) and c in ["ready", "working", "configured", "passed"])
        )

        integration_score = (working_components / total_components * 100) if total_components > 0 else 0

        logger.info(f"\n📈 INTEGRATION SCORE: {integration_score:.1f}%")
        logger.info(f"   Components Working: {working_components}/{total_components}")

        if integration_score >= 80:
            logger.info("\n✅ AI System Integration: OPERATIONAL")
            logger.info("   The AI infrastructure is properly configured and ready for use.")
        elif integration_score >= 50:
            logger.info("\n⚠️  AI System Integration: PARTIALLY OPERATIONAL")
            logger.info("   Some components need attention but basic functionality is available.")
        else:
            logger.info("\n❌ AI System Integration: NEEDS CONFIGURATION")
            logger.info("   Several critical components require setup.")

        # Save detailed report
        report_file = "ai_integration_status.json"
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        logger.info(f"\n📄 Detailed report saved to: {report_file}")

        return self.results

    async def run_all_verifications(self):
        """Execute all verification checks"""
        if not await self.setup():
            logger.error("Failed to connect to database. Cannot proceed.")
            return self.results

        # Run all verifications
        checks = [
            self.verify_pgvector,
            self.verify_ai_tables,
            self.verify_cache_system,
            self.verify_model_configuration,
            self.verify_performance_metrics,
            self.run_integration_test
        ]

        for check in checks:
            try:
                await check()
            except Exception as e:
                logger.error(f"Check failed: {e}")
                traceback.print_exc()

        await self.teardown()
        return await self.generate_report()


async def main():
    """Main entry point"""
    logger.info("Starting AI System Integration Verification...")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info(f"Python: {sys.version}")

    verifier = AIIntegrationVerifier()
    results = await verifier.run_all_verifications()

    # Exit code based on results
    if results.get("issues"):
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())