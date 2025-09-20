# 🔧 测试系统故障排除指南

## 概述

本指南提供了针对H:\novellus项目测试验证系统的全面故障排除方案，覆盖pgvector扩展、AI模型管理系统、集成测试和性能基准测试的常见问题及解决方案。

## 📋 目录

1. [环境检查和预备步骤](#环境检查和预备步骤)
2. [pgvector扩展故障排除](#pgvector扩展故障排除)
3. [AI模型管理系统故障排除](#ai模型管理系统故障排除)
4. [集成测试故障排除](#集成测试故障排除)
5. [性能基准测试故障排除](#性能基准测试故障排除)
6. [自动化测试执行器故障排除](#自动化测试执行器故障排除)
7. [数据库连接问题](#数据库连接问题)
8. [Redis缓存问题](#redis缓存问题)
9. [系统资源问题](#系统资源问题)
10. [日志分析和诊断](#日志分析和诊断)

---

## 🔍 环境检查和预备步骤

### 快速环境验证脚本

```bash
#!/bin/bash
# 环境验证脚本

echo "🔍 Novellus测试环境验证"
echo "========================"

# 1. 检查Python环境
echo "检查Python环境..."
python3 --version
pip3 list | grep -E "(asyncpg|redis|psutil|numpy)"

# 2. 检查数据库连接
echo "检查PostgreSQL连接..."
psql -h localhost -p 5432 -U postgres -d postgres -c "SELECT version();"

# 3. 检查pgvector扩展
echo "检查pgvector扩展..."
psql -h localhost -p 5432 -U postgres -d postgres -c "SELECT name, installed_version FROM pg_available_extensions WHERE name = 'vector';"

# 4. 检查Redis连接
echo "检查Redis连接..."
redis-cli ping

# 5. 检查项目结构
echo "检查项目结构..."
ls -la /h/novellus/src/
ls -la /h/novellus/tests/

echo "✅ 环境验证完成"
```

### 基础依赖检查

```python
#!/usr/bin/env python3
"""
依赖检查脚本
"""
import sys
import importlib

required_packages = [
    'asyncio',
    'asyncpg',
    'redis',
    'psutil',
    'numpy',
    'matplotlib',
    'seaborn',
    'jinja2',
    'pandas'
]

def check_dependencies():
    missing_packages = []

    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 未安装")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install " + " ".join(missing_packages))
        return False

    print("\n✅ 所有依赖包已安装")
    return True

if __name__ == "__main__":
    check_dependencies()
```

---

## 🔧 pgvector扩展故障排除

### 常见问题及解决方案

#### 1. pgvector扩展未安装

**症状:**
```
ERROR: extension "vector" is not available
```

**诊断:**
```sql
-- 检查可用扩展
SELECT name, installed_version, default_version
FROM pg_available_extensions
WHERE name = 'vector';

-- 检查已安装扩展
SELECT extname, extversion
FROM pg_extension
WHERE extname = 'vector';
```

**解决方案:**
```sql
-- 安装pgvector扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 验证安装
SELECT vector_version();
```

**Docker环境解决方案:**
```bash
# 使用官方pgvector镜像
docker run -d \
  --name postgres-pgvector \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  pgvector/pgvector:pg15
```

#### 2. 向量维度不匹配

**症状:**
```
ERROR: expected 1536 dimensions, not 512
```

**诊断脚本:**
```python
async def diagnose_vector_dimensions(db_pool):
    async with db_pool.acquire() as conn:
        # 检查表结构
        result = await conn.fetch("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'content_embeddings'
            AND column_name = 'embedding'
        """)

        # 检查实际数据
        sample = await conn.fetch("""
            SELECT array_length(embedding::float[], 1) as dimensions
            FROM content_embeddings
            LIMIT 5
        """)

        return {
            'table_definition': result,
            'actual_dimensions': [row['dimensions'] for row in sample]
        }
```

**解决方案:**
```sql
-- 修改表结构
ALTER TABLE content_embeddings
ALTER COLUMN embedding TYPE vector(1536);

-- 或重建表
DROP TABLE IF EXISTS content_embeddings CASCADE;
CREATE TABLE content_embeddings (
    content_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    embedding vector(1536),
    -- 其他字段...
);
```

#### 3. 向量索引性能问题

**症状:**
- 查询速度慢
- 索引创建失败

**诊断:**
```sql
-- 检查索引状态
SELECT schemaname, tablename, indexname, indexdef
FROM pg_indexes
WHERE tablename LIKE '%vector%';

-- 检查表大小
SELECT pg_size_pretty(pg_total_relation_size('content_embeddings'));

-- 检查查询计划
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM content_embeddings
ORDER BY embedding <-> '[0,1,0,...]'::vector
LIMIT 10;
```

**解决方案:**
```sql
-- 优化HNSW索引
DROP INDEX IF EXISTS idx_embedding_hnsw;
CREATE INDEX CONCURRENTLY idx_embedding_hnsw
ON content_embeddings
USING hnsw (embedding vector_l2_ops)
WITH (m = 16, ef_construction = 64);

-- 或优化IVFFlat索引
DROP INDEX IF EXISTS idx_embedding_ivfflat;
CREATE INDEX CONCURRENTLY idx_embedding_ivfflat
ON content_embeddings
USING ivfflat (embedding vector_l2_ops)
WITH (lists = 100);

-- 调整查询参数
SET ivfflat.probes = 10;
SET hnsw.ef_search = 40;
```

### pgvector测试验证脚本

```python
#!/usr/bin/env python3
"""
pgvector功能验证脚本
"""
import asyncio
import asyncpg
import random

async def verify_pgvector_functionality():
    """验证pgvector基础功能"""

    # 连接数据库
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        database="postgres",
        user="postgres",
        password="postgres"
    )

    try:
        print("🔍 验证pgvector功能...")

        # 1. 检查扩展
        version = await conn.fetchval("SELECT vector_version()")
        print(f"✅ pgvector版本: {version}")

        # 2. 测试向量操作
        test_vector = [random.random() for _ in range(1536)]

        # 创建测试表
        await conn.execute("""
            CREATE TEMP TABLE test_vectors (
                id SERIAL PRIMARY KEY,
                embedding vector(1536)
            )
        """)

        # 插入测试数据
        await conn.execute(
            "INSERT INTO test_vectors (embedding) VALUES ($1)",
            test_vector
        )

        # 测试相似度查询
        result = await conn.fetchval("""
            SELECT embedding <-> $1 as distance
            FROM test_vectors
            ORDER BY embedding <-> $1
            LIMIT 1
        """, test_vector)

        print(f"✅ 向量距离计算: {result}")

        # 3. 测试不同距离函数
        l2_dist = await conn.fetchval(
            "SELECT $1 <-> $2", test_vector, test_vector
        )
        cosine_dist = await conn.fetchval(
            "SELECT $1 <=> $2", test_vector, test_vector
        )
        inner_product = await conn.fetchval(
            "SELECT $1 <#> $2", test_vector, test_vector
        )

        print(f"✅ L2距离: {l2_dist}")
        print(f"✅ 余弦距离: {cosine_dist}")
        print(f"✅ 内积: {inner_product}")

        return True

    except Exception as e:
        print(f"❌ pgvector验证失败: {e}")
        return False

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(verify_pgvector_functionality())
```

---

## 🤖 AI模型管理系统故障排除

### 常见问题及解决方案

#### 1. 模型API连接失败

**症状:**
```
ConnectionError: Failed to connect to OpenAI API
AuthenticationError: Invalid API key
```

**诊断脚本:**
```python
async def diagnose_ai_model_connections():
    """诊断AI模型连接问题"""

    diagnostics = {
        'api_keys_configured': False,
        'network_connectivity': False,
        'model_availability': {},
        'rate_limits': {}
    }

    # 检查API密钥配置
    import os
    api_keys = {
        'openai': os.getenv('OPENAI_API_KEY'),
        'anthropic': os.getenv('CLAUDE_API_KEY')
    }

    diagnostics['api_keys_configured'] = any(api_keys.values())

    # 测试网络连接
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.openai.com/v1/models') as resp:
                diagnostics['network_connectivity'] = resp.status == 401  # 401表示认证问题，但网络通
    except:
        diagnostics['network_connectivity'] = False

    return diagnostics
```

**解决方案:**
```bash
# 设置环境变量
export OPENAI_API_KEY="your-openai-api-key"
export CLAUDE_API_KEY="your-claude-api-key"

# 或在.env文件中配置
echo "OPENAI_API_KEY=your-key" >> .env
echo "CLAUDE_API_KEY=your-key" >> .env
```

#### 2. 模型负载均衡问题

**症状:**
- 请求总是路由到同一个模型
- 某些模型从未被选择

**诊断:**
```python
async def diagnose_load_balancing(model_manager):
    """诊断负载均衡问题"""

    # 模拟多个请求
    model_selections = []
    for _ in range(50):
        selected = await model_manager.load_balancer.select_model(
            request_type="completion",
            prompt_length=100
        )
        model_selections.append(selected)

    # 分析分布
    from collections import Counter
    distribution = Counter(model_selections)

    return {
        'total_requests': len(model_selections),
        'model_distribution': dict(distribution),
        'unique_models_used': len(distribution),
        'balance_score': 1 - max(distribution.values()) / len(model_selections)
    }
```

**解决方案:**
```python
# 调整模型优先级
model_config.priority = 100  # 更高优先级

# 检查模型状态
for model_id, model in model_manager.models.items():
    if model.status != ModelStatus.ACTIVE:
        print(f"模型 {model_id} 状态: {model.status}")

# 重置速率限制
model_manager.rate_limits.clear()
```

#### 3. 缓存命中率低

**症状:**
- 缓存命中率低于预期
- 响应时间没有明显改善

**诊断:**
```python
async def diagnose_cache_performance(cache_manager):
    """诊断缓存性能问题"""

    # 检查缓存配置
    cache_stats = await cache_manager.get_cache_statistics()

    # 测试缓存功能
    test_key = "test_cache_key"
    test_value = {"test": "data"}

    # 写入测试
    await cache_manager.set_cache(test_key, test_value, ttl=60)

    # 读取测试
    cached_value = await cache_manager.get_cache(test_key)

    return {
        'cache_stats': cache_stats,
        'write_test_success': True,
        'read_test_success': cached_value == test_value,
        'cache_backend': type(cache_manager.redis_client).__name__
    }
```

**解决方案:**
```python
# 调整缓存TTL
await cache_manager.set_cache(key, value, ttl=3600)  # 1小时

# 优化缓存键生成
def generate_cache_key(prompt, model_id, **kwargs):
    import hashlib
    cache_data = f"{prompt}_{model_id}_{sorted(kwargs.items())}"
    return hashlib.md5(cache_data.encode()).hexdigest()

# 预热缓存
common_prompts = ["常见问题1", "常见问题2", ...]
for prompt in common_prompts:
    response = await model_manager.complete(prompt, use_cache=True)
```

### AI模型系统监控脚本

```python
#!/usr/bin/env python3
"""
AI模型系统监控脚本
"""
import asyncio
import time
from datetime import datetime, timedelta

async def monitor_ai_model_system(model_manager, duration_minutes=5):
    """监控AI模型系统健康状况"""

    print(f"🔍 开始监控AI模型系统 ({duration_minutes}分钟)")

    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)

    metrics = {
        'requests_sent': 0,
        'requests_successful': 0,
        'cache_hits': 0,
        'model_usage': {},
        'error_count': 0,
        'avg_latency': 0,
        'latencies': []
    }

    while time.time() < end_time:
        try:
            # 发送测试请求
            request_start = time.time()

            response = await model_manager.complete(
                prompt=f"测试请求 {datetime.now().isoformat()}",
                use_cache=True
            )

            request_latency = (time.time() - request_start) * 1000

            # 更新指标
            metrics['requests_sent'] += 1
            metrics['latencies'].append(request_latency)

            if response and 'content' in response:
                metrics['requests_successful'] += 1

                # 记录模型使用
                model = response.get('model', 'unknown')
                metrics['model_usage'][model] = metrics['model_usage'].get(model, 0) + 1

                # 检查是否缓存命中
                if response.get('cache_hit'):
                    metrics['cache_hits'] += 1

        except Exception as e:
            metrics['error_count'] += 1
            print(f"❌ 请求失败: {e}")

        # 等待间隔
        await asyncio.sleep(10)

    # 计算最终指标
    if metrics['latencies']:
        metrics['avg_latency'] = sum(metrics['latencies']) / len(metrics['latencies'])

    # 输出监控结果
    print("\n📊 监控结果:")
    print(f"总请求数: {metrics['requests_sent']}")
    print(f"成功率: {metrics['requests_successful'] / metrics['requests_sent']:.2%}")
    print(f"缓存命中率: {metrics['cache_hits'] / metrics['requests_sent']:.2%}")
    print(f"平均延迟: {metrics['avg_latency']:.2f}ms")
    print(f"错误计数: {metrics['error_count']}")
    print(f"模型使用分布: {metrics['model_usage']}")

    return metrics
```

---

## 🔗 集成测试故障排除

### 常见问题及解决方案

#### 1. 组件间通信失败

**症状:**
- 集成测试超时
- 数据在组件间传递时丢失

**诊断脚本:**
```python
async def diagnose_component_integration():
    """诊断组件集成问题"""

    diagnostics = {
        'database_connectivity': False,
        'redis_connectivity': False,
        'ai_model_availability': False,
        'vector_search_functional': False,
        'cache_integration': False
    }

    try:
        # 测试数据库连接
        import asyncpg
        conn = await asyncpg.connect("postgresql://...")
        await conn.fetchval("SELECT 1")
        diagnostics['database_connectivity'] = True
        await conn.close()
    except:
        pass

    try:
        # 测试Redis连接
        import redis.asyncio as redis
        r = await redis.from_url("redis://localhost:6379")
        await r.ping()
        diagnostics['redis_connectivity'] = True
        await r.close()
    except:
        pass

    # 继续其他组件测试...

    return diagnostics
```

#### 2. 数据一致性问题

**症状:**
- 不同组件返回不一致的数据
- 缓存数据与数据库数据不匹配

**验证脚本:**
```python
async def verify_data_consistency(integration_system):
    """验证数据一致性"""

    test_content = "测试数据一致性的内容"
    content_id = None

    try:
        # 1. 通过集成系统存储内容
        store_result = await integration_system.store_content_with_embedding(
            content=test_content,
            content_type="consistency_test"
        )
        content_id = store_result['content_id']

        # 2. 直接从数据库查询
        async with integration_system.db_pool.acquire() as conn:
            db_result = await conn.fetchrow(
                "SELECT * FROM content_embeddings WHERE content_id = $1",
                content_id
            )

        # 3. 通过搜索查找
        search_result = await integration_system.semantic_search(
            query_text=test_content,
            content_type="consistency_test"
        )

        # 4. 检查缓存
        cache_result = await integration_system.cache_manager.get_cache(
            f"content_{content_id}"
        )

        # 验证一致性
        checks = {
            'database_has_content': db_result is not None,
            'search_finds_content': any(
                r.get('content_id') == content_id
                for r in search_result.get('results', [])
            ),
            'content_text_matches': db_result and db_result['content_text'] == test_content,
            'cache_consistency': cache_result is not None
        }

        return checks

    finally:
        # 清理测试数据
        if content_id:
            async with integration_system.db_pool.acquire() as conn:
                await conn.execute(
                    "DELETE FROM content_embeddings WHERE content_id = $1",
                    content_id
                )
```

#### 3. 性能瓶颈识别

**性能诊断脚本:**
```python
import time
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def performance_monitor(operation_name):
    """性能监控上下文管理器"""
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss

    print(f"⏱️ 开始 {operation_name}")

    try:
        yield
    finally:
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss

        duration = (end_time - start_time) * 1000
        memory_delta = (end_memory - start_memory) / 1024 / 1024

        print(f"✅ {operation_name} 完成: {duration:.2f}ms, 内存变化: {memory_delta:.2f}MB")

async def profile_integration_performance(integration_system):
    """性能分析集成系统"""

    test_data = "这是用于性能测试的内容" * 100

    # 测试向量生成性能
    async with performance_monitor("向量生成"):
        embedding_result = await integration_system.generate_embedding(test_data)

    # 测试存储性能
    async with performance_monitor("数据存储"):
        store_result = await integration_system.store_content_with_embedding(
            content=test_data,
            content_type="performance_test"
        )

    # 测试搜索性能
    async with performance_monitor("语义搜索"):
        search_result = await integration_system.semantic_search(
            query_text=test_data[:100],
            content_type="performance_test"
        )

    # 测试缓存性能
    async with performance_monitor("缓存操作"):
        await integration_system.cache_manager.set_cache("perf_test", test_data)
        cached = await integration_system.cache_manager.get_cache("perf_test")

    return {
        'embedding_latency': embedding_result.get('latency_ms', 0),
        'storage_success': store_result.get('success', False),
        'search_results_count': len(search_result.get('results', [])),
        'cache_hit': cached == test_data
    }
```

---

## 📊 性能基准测试故障排除

### 常见问题及解决方案

#### 1. 基准测试数据生成缓慢

**症状:**
- 测试数据插入速度慢
- 内存使用过高

**优化方案:**
```python
async def optimized_batch_insert(db_pool, vectors, batch_size=1000):
    """优化的批量插入"""

    async with db_pool.acquire() as conn:
        # 使用事务和批量插入
        async with conn.transaction():
            # 准备语句
            stmt = await conn.prepare("""
                INSERT INTO benchmark_vectors (content_text, embedding, metadata)
                VALUES ($1, $2, $3)
            """)

            # 批量执行
            batch = []
            for i, (content, embedding, metadata) in enumerate(vectors):
                batch.append((content, embedding, json.dumps(metadata)))

                if len(batch) >= batch_size:
                    await stmt.executemany(batch)
                    batch = []

                    # 周期性提交以释放内存
                    if (i + 1) % (batch_size * 10) == 0:
                        print(f"已插入 {i + 1} 条记录")

            # 插入剩余数据
            if batch:
                await stmt.executemany(batch)
```

#### 2. 性能测试结果不稳定

**症状:**
- 相同测试多次运行结果差异很大
- 性能指标出现异常值

**稳定性改进:**
```python
import statistics
import time

async def stable_performance_test(test_func, iterations=5, warmup=2):
    """稳定的性能测试"""

    print(f"🔥 预热测试 ({warmup}次)")
    for i in range(warmup):
        await test_func()

    print(f"📊 正式测试 ({iterations}次)")
    latencies = []

    for i in range(iterations):
        start_time = time.time()
        await test_func()
        latency = (time.time() - start_time) * 1000
        latencies.append(latency)
        print(f"  第{i+1}次: {latency:.2f}ms")

    # 计算统计指标
    results = {
        'iterations': iterations,
        'min_latency': min(latencies),
        'max_latency': max(latencies),
        'avg_latency': statistics.mean(latencies),
        'median_latency': statistics.median(latencies),
        'std_deviation': statistics.stdev(latencies) if len(latencies) > 1 else 0,
        'coefficient_of_variation': statistics.stdev(latencies) / statistics.mean(latencies) if len(latencies) > 1 and statistics.mean(latencies) > 0 else 0
    }

    # 检查稳定性
    cv_threshold = 0.2  # 变异系数阈值
    results['is_stable'] = results['coefficient_of_variation'] < cv_threshold

    return results
```

#### 3. 系统资源监控异常

**资源监控改进:**
```python
import psutil
import asyncio
from collections import deque

class SystemResourceMonitor:
    """系统资源监控器"""

    def __init__(self, max_history=100):
        self.max_history = max_history
        self.cpu_history = deque(maxlen=max_history)
        self.memory_history = deque(maxlen=max_history)
        self.disk_io_history = deque(maxlen=max_history)
        self.network_io_history = deque(maxlen=max_history)
        self.monitoring = False

    async def start_monitoring(self, interval=1):
        """开始监控"""
        self.monitoring = True

        while self.monitoring:
            try:
                # CPU使用率
                cpu_percent = psutil.cpu_percent(interval=None)
                self.cpu_history.append(cpu_percent)

                # 内存使用
                memory = psutil.virtual_memory()
                self.memory_history.append(memory.percent)

                # 磁盘IO
                disk_io = psutil.disk_io_counters()
                if disk_io:
                    self.disk_io_history.append({
                        'read_bytes': disk_io.read_bytes,
                        'write_bytes': disk_io.write_bytes
                    })

                # 网络IO
                network_io = psutil.net_io_counters()
                if network_io:
                    self.network_io_history.append({
                        'bytes_sent': network_io.bytes_sent,
                        'bytes_recv': network_io.bytes_recv
                    })

                await asyncio.sleep(interval)

            except Exception as e:
                print(f"监控错误: {e}")
                await asyncio.sleep(interval)

    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False

    def get_resource_summary(self):
        """获取资源使用摘要"""
        if not self.cpu_history:
            return None

        return {
            'cpu': {
                'avg': statistics.mean(self.cpu_history),
                'max': max(self.cpu_history),
                'current': self.cpu_history[-1] if self.cpu_history else 0
            },
            'memory': {
                'avg': statistics.mean(self.memory_history),
                'max': max(self.memory_history),
                'current': self.memory_history[-1] if self.memory_history else 0
            },
            'monitoring_duration': len(self.cpu_history),
            'resource_alerts': self._check_resource_alerts()
        }

    def _check_resource_alerts(self):
        """检查资源警报"""
        alerts = []

        if self.cpu_history:
            avg_cpu = statistics.mean(self.cpu_history)
            if avg_cpu > 90:
                alerts.append("CPU使用率过高")

        if self.memory_history:
            avg_memory = statistics.mean(self.memory_history)
            if avg_memory > 90:
                alerts.append("内存使用率过高")

        return alerts
```

---

## 🤖 自动化测试执行器故障排除

### 常见问题及解决方案

#### 1. 测试执行器无法启动

**症状:**
```
ModuleNotFoundError: No module named 'test_pgvector_suite'
ImportError: cannot import name 'AIModelManager'
```

**诊断脚本:**
```python
#!/usr/bin/env python3
"""
测试执行器诊断脚本
"""
import sys
import os
from pathlib import Path

def diagnose_test_runner():
    """诊断测试执行器问题"""

    print("🔍 诊断测试执行器环境")

    # 检查Python路径
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")

    # 检查当前工作目录
    print(f"当前目录: {os.getcwd()}")

    # 检查项目路径
    project_root = Path("/h/novellus")
    if not project_root.exists():
        print(f"❌ 项目根目录不存在: {project_root}")
        return False

    # 检查测试文件
    test_files = [
        "tests/test_pgvector_suite.py",
        "tests/test_ai_model_manager.py",
        "tests/test_integration_suite.py",
        "tests/performance_benchmark_suite.py"
    ]

    for test_file in test_files:
        file_path = project_root / test_file
        if file_path.exists():
            print(f"✅ {test_file}")
        else:
            print(f"❌ {test_file}")

    # 检查源码目录
    src_path = project_root / "src"
    if src_path.exists():
        print(f"✅ src目录存在")

        # 检查关键模块
        key_modules = [
            "src/ai/model_manager.py",
            "src/ai/cache_manager.py",
            "src/config.py"
        ]

        for module in key_modules:
            module_path = project_root / module
            if module_path.exists():
                print(f"✅ {module}")
            else:
                print(f"❌ {module}")
    else:
        print(f"❌ src目录不存在")

    # 检查Python路径配置
    print(f"\nPython搜索路径:")
    for path in sys.path:
        print(f"  {path}")

    return True

if __name__ == "__main__":
    diagnose_test_runner()
```

**解决方案:**
```bash
# 设置Python路径
export PYTHONPATH="/h/novellus:/h/novellus/src:/h/novellus/tests:$PYTHONPATH"

# 或在脚本中添加
import sys
sys.path.append('/h/novellus')
sys.path.append('/h/novellus/src')
sys.path.append('/h/novellus/tests')
```

#### 2. 并行测试冲突

**症状:**
- 并行测试时数据库连接池耗尽
- 测试结果不一致

**解决方案:**
```python
# 优化连接池配置
async def create_optimized_pool():
    """创建优化的连接池"""

    # 根据并行测试数量调整连接池大小
    import os
    concurrent_tests = int(os.getenv('CONCURRENT_TESTS', '4'))

    pool = await asyncpg.create_pool(
        host="localhost",
        port=5432,
        database="postgres",
        user="postgres",
        password="postgres",
        min_size=concurrent_tests,
        max_size=concurrent_tests * 5,
        command_timeout=60,
        server_settings={
            'jit': 'off',  # 禁用JIT以提高稳定性
            'application_name': 'novellus_tests'
        }
    )

    return pool

# 测试数据隔离
class TestDataIsolation:
    """测试数据隔离管理器"""

    def __init__(self):
        self.test_schemas = set()

    async def create_test_schema(self, pool, test_name):
        """为测试创建独立的模式"""
        schema_name = f"test_{test_name}_{int(time.time())}"

        async with pool.acquire() as conn:
            await conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
            await conn.execute(f"SET search_path = {schema_name}, public")

            # 复制必要的表结构
            tables_to_copy = [
                'content_embeddings',
                'ai_models',
                'ai_requests'
            ]

            for table in tables_to_copy:
                await conn.execute(f"""
                    CREATE TABLE {schema_name}.{table}
                    (LIKE public.{table} INCLUDING ALL)
                """)

        self.test_schemas.add(schema_name)
        return schema_name

    async def cleanup_test_schemas(self, pool):
        """清理测试模式"""
        async with pool.acquire() as conn:
            for schema in self.test_schemas:
                await conn.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")

        self.test_schemas.clear()
```

#### 3. 报告生成失败

**症状:**
- HTML报告模板错误
- 图表生成失败

**解决方案:**
```python
# 修复报告生成问题
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端

async def safe_report_generation(test_summary, output_dir):
    """安全的报告生成"""

    try:
        # JSON报告（最基础）
        json_file = output_dir / "test_report.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(test_summary.__dict__, f, indent=2, default=str)
        print(f"✅ JSON报告生成成功: {json_file}")

    except Exception as e:
        print(f"❌ JSON报告生成失败: {e}")

    try:
        # 简化HTML报告
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Test Report</title></head>
        <body>
            <h1>测试报告</h1>
            <p>运行ID: {test_summary.run_id}</p>
            <p>总体状态: {'PASSED' if test_summary.overall_success else 'FAILED'}</p>
            <p>成功率: {test_summary.overall_success_rate:.2%}</p>
            <p>总测试数: {test_summary.total_tests}</p>
            <p>通过: {test_summary.total_passed}</p>
            <p>失败: {test_summary.total_failed}</p>
        </body>
        </html>
        """

        html_file = output_dir / "test_report.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ HTML报告生成成功: {html_file}")

    except Exception as e:
        print(f"❌ HTML报告生成失败: {e}")
```

---

## 🗄️ 数据库连接问题

### PostgreSQL连接故障排除

#### 连接诊断脚本
```python
#!/usr/bin/env python3
"""
PostgreSQL连接诊断脚本
"""
import asyncio
import asyncpg
import psutil
import time

async def diagnose_postgresql_connection():
    """诊断PostgreSQL连接问题"""

    connection_configs = [
        {
            'name': '本地默认配置',
            'config': {
                'host': 'localhost',
                'port': 5432,
                'database': 'postgres',
                'user': 'postgres',
                'password': 'postgres'
            }
        },
        {
            'name': 'Docker配置',
            'config': {
                'host': '127.0.0.1',
                'port': 5432,
                'database': 'postgres',
                'user': 'postgres',
                'password': 'postgres'
            }
        }
    ]

    for config_info in connection_configs:
        print(f"\n🔍 测试 {config_info['name']}")

        try:
            # 测试连接
            conn = await asyncpg.connect(**config_info['config'])

            # 基础查询测试
            version = await conn.fetchval("SELECT version()")
            print(f"✅ 连接成功")
            print(f"   PostgreSQL版本: {version.split(',')[0]}")

            # 测试pgvector
            try:
                vector_version = await conn.fetchval("SELECT vector_version()")
                print(f"✅ pgvector可用: {vector_version}")
            except:
                print(f"❌ pgvector不可用")

            # 测试性能
            start_time = time.time()
            await conn.fetchval("SELECT pg_sleep(0.001)")
            latency = (time.time() - start_time) * 1000
            print(f"✅ 连接延迟: {latency:.2f}ms")

            # 检查连接池
            pool_info = await conn.fetch("""
                SELECT
                    state,
                    COUNT(*) as count
                FROM pg_stat_activity
                WHERE datname = current_database()
                GROUP BY state
            """)
            print(f"✅ 活动连接: {dict(pool_info)}")

            await conn.close()

        except Exception as e:
            print(f"❌ 连接失败: {e}")

            # 提供诊断建议
            if "Connection refused" in str(e):
                print("   建议: 检查PostgreSQL是否运行，端口是否正确")
            elif "authentication failed" in str(e):
                print("   建议: 检查用户名和密码，查看pg_hba.conf配置")
            elif "database does not exist" in str(e):
                print("   建议: 创建数据库或使用正确的数据库名")

# 连接池诊断
async def diagnose_connection_pool():
    """诊断连接池问题"""

    print("🔍 诊断连接池配置")

    try:
        # 创建连接池
        pool = await asyncpg.create_pool(
            host="localhost",
            port=5432,
            database="postgres",
            user="postgres",
            password="postgres",
            min_size=2,
            max_size=10,
            command_timeout=10
        )

        print(f"✅ 连接池创建成功")
        print(f"   最小连接数: {pool._minsize}")
        print(f"   最大连接数: {pool._maxsize}")

        # 测试并发连接
        async def test_connection(conn_id):
            try:
                async with pool.acquire() as conn:
                    result = await conn.fetchval("SELECT $1", conn_id)
                    await asyncio.sleep(0.1)  # 模拟工作负载
                    return f"连接{conn_id}: 成功"
            except Exception as e:
                return f"连接{conn_id}: 失败 - {e}"

        # 并发测试
        tasks = [test_connection(i) for i in range(15)]
        results = await asyncio.gather(*tasks)

        successful = sum(1 for r in results if "成功" in r)
        print(f"✅ 并发连接测试: {successful}/{len(tasks)} 成功")

        for result in results:
            if "失败" in result:
                print(f"   {result}")

        await pool.close()

    except Exception as e:
        print(f"❌ 连接池测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(diagnose_postgresql_connection())
    asyncio.run(diagnose_connection_pool())
```

---

## 🗂️ Redis缓存问题

### Redis连接和性能诊断

```python
#!/usr/bin/env python3
"""
Redis诊断脚本
"""
import asyncio
import redis.asyncio as redis
import time
import json

async def diagnose_redis_connection():
    """诊断Redis连接问题"""

    redis_configs = [
        {
            'name': '本地默认',
            'url': 'redis://localhost:6379'
        },
        {
            'name': '本地数据库1',
            'url': 'redis://localhost:6379/1'
        },
        {
            'name': 'Docker Redis',
            'url': 'redis://127.0.0.1:6379'
        }
    ]

    for config in redis_configs:
        print(f"\n🔍 测试 {config['name']}: {config['url']}")

        try:
            # 创建Redis客户端
            client = await redis.from_url(config['url'], decode_responses=True)

            # 基础连接测试
            pong = await client.ping()
            print(f"✅ 连接成功: {pong}")

            # 获取Redis信息
            info = await client.info()
            print(f"✅ Redis版本: {info['redis_version']}")
            print(f"   使用内存: {info['used_memory_human']}")
            print(f"   连接数: {info['connected_clients']}")
            print(f"   运行时间: {info['uptime_in_seconds']}秒")

            # 性能测试
            test_key = "test_performance"
            test_value = {"data": "test" * 100}

            # 写入性能
            start_time = time.time()
            await client.set(test_key, json.dumps(test_value), ex=60)
            write_latency = (time.time() - start_time) * 1000
            print(f"✅ 写入延迟: {write_latency:.2f}ms")

            # 读取性能
            start_time = time.time()
            cached_value = await client.get(test_key)
            read_latency = (time.time() - start_time) * 1000
            print(f"✅ 读取延迟: {read_latency:.2f}ms")

            # 验证数据一致性
            if cached_value == json.dumps(test_value):
                print(f"✅ 数据一致性: 正确")
            else:
                print(f"❌ 数据一致性: 错误")

            # 清理测试数据
            await client.delete(test_key)

            await client.close()

        except Exception as e:
            print(f"❌ 连接失败: {e}")

            if "Connection refused" in str(e):
                print("   建议: 检查Redis是否运行")
            elif "timeout" in str(e):
                print("   建议: 检查网络连接或增加超时时间")

async def diagnose_redis_memory_usage():
    """诊断Redis内存使用"""

    try:
        client = await redis.from_url("redis://localhost:6379", decode_responses=True)

        print("\n🔍 Redis内存使用分析")

        # 获取内存信息
        info = await client.info('memory')

        print(f"已用内存: {info['used_memory_human']}")
        print(f"内存峰值: {info['used_memory_peak_human']}")
        print(f"内存碎片率: {info['mem_fragmentation_ratio']:.2f}")

        # 分析键空间
        keyspace_info = await client.info('keyspace')
        for db, stats in keyspace_info.items():
            if db.startswith('db'):
                print(f"{db}: {stats}")

        # 检查大键
        print("\n🔍 检查大键:")
        cursor = 0
        large_keys = []

        while True:
            cursor, keys = await client.scan(cursor=cursor, count=100)

            for key in keys:
                try:
                    size = await client.memory_usage(key)
                    if size and size > 1024 * 1024:  # 大于1MB的键
                        large_keys.append((key, size))
                except:
                    pass

            if cursor == 0:
                break

        if large_keys:
            print("发现大键:")
            for key, size in sorted(large_keys, key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {key}: {size / 1024 / 1024:.2f}MB")
        else:
            print("未发现异常大键")

        await client.close()

    except Exception as e:
        print(f"❌ Redis内存分析失败: {e}")

if __name__ == "__main__":
    asyncio.run(diagnose_redis_connection())
    asyncio.run(diagnose_redis_memory_usage())
```

---

## 💻 系统资源问题

### 系统资源监控和优化

```python
#!/usr/bin/env python3
"""
系统资源监控脚本
"""
import psutil
import time
import platform
from datetime import datetime

def diagnose_system_resources():
    """诊断系统资源状况"""

    print("🔍 系统资源诊断")
    print("=" * 50)

    # 系统基本信息
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"架构: {platform.machine()}")
    print(f"Python版本: {platform.python_version()}")
    print(f"当前时间: {datetime.now()}")

    print("\n💾 内存状态:")
    memory = psutil.virtual_memory()
    print(f"总内存: {memory.total / 1024**3:.2f} GB")
    print(f"可用内存: {memory.available / 1024**3:.2f} GB")
    print(f"已用内存: {memory.used / 1024**3:.2f} GB ({memory.percent:.1f}%)")

    if memory.percent > 90:
        print("⚠️  内存使用率过高!")
    elif memory.percent > 80:
        print("⚠️  内存使用率较高")
    else:
        print("✅ 内存使用率正常")

    print("\n🔥 CPU状态:")
    cpu_count = psutil.cpu_count()
    cpu_count_logical = psutil.cpu_count(logical=True)
    print(f"物理核心数: {cpu_count}")
    print(f"逻辑核心数: {cpu_count_logical}")

    # CPU使用率（多次采样取平均）
    cpu_samples = []
    for i in range(5):
        cpu_percent = psutil.cpu_percent(interval=0.2)
        cpu_samples.append(cpu_percent)

    avg_cpu = sum(cpu_samples) / len(cpu_samples)
    print(f"平均CPU使用率: {avg_cpu:.1f}%")

    if avg_cpu > 90:
        print("⚠️  CPU使用率过高!")
    elif avg_cpu > 70:
        print("⚠️  CPU使用率较高")
    else:
        print("✅ CPU使用率正常")

    # 每核心使用率
    per_cpu = psutil.cpu_percent(percpu=True, interval=1)
    print("各核心使用率:", [f"{cpu:.1f}%" for cpu in per_cpu])

    print("\n💿 磁盘状态:")
    disk_usage = psutil.disk_usage('/')
    print(f"总空间: {disk_usage.total / 1024**3:.2f} GB")
    print(f"已用空间: {disk_usage.used / 1024**3:.2f} GB ({disk_usage.used/disk_usage.total*100:.1f}%)")
    print(f"可用空间: {disk_usage.free / 1024**3:.2f} GB")

    if disk_usage.used / disk_usage.total > 0.9:
        print("⚠️  磁盘空间不足!")
    elif disk_usage.used / disk_usage.total > 0.8:
        print("⚠️  磁盘空间较少")
    else:
        print("✅ 磁盘空间充足")

    # 磁盘IO
    disk_io = psutil.disk_io_counters()
    if disk_io:
        print(f"磁盘读取: {disk_io.read_bytes / 1024**2:.2f} MB")
        print(f"磁盘写入: {disk_io.write_bytes / 1024**2:.2f} MB")

    print("\n🌐 网络状态:")
    network_io = psutil.net_io_counters()
    if network_io:
        print(f"网络发送: {network_io.bytes_sent / 1024**2:.2f} MB")
        print(f"网络接收: {network_io.bytes_recv / 1024**2:.2f} MB")

    # 网络连接
    connections = psutil.net_connections()
    tcp_connections = len([c for c in connections if c.type == 1])  # TCP
    print(f"TCP连接数: {tcp_connections}")

    print("\n🔧 进程状态:")
    # 当前进程信息
    current_process = psutil.Process()
    print(f"当前进程PID: {current_process.pid}")
    print(f"进程内存: {current_process.memory_info().rss / 1024**2:.2f} MB")
    print(f"进程CPU: {current_process.cpu_percent():.1f}%")

    # 查找PostgreSQL和Redis进程
    postgres_processes = []
    redis_processes = []

    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        try:
            if 'postgres' in proc.info['name'].lower():
                postgres_processes.append(proc.info)
            elif 'redis' in proc.info['name'].lower():
                redis_processes.append(proc.info)
        except:
            continue

    if postgres_processes:
        print(f"\n📊 PostgreSQL进程 ({len(postgres_processes)}个):")
        for proc in postgres_processes[:5]:  # 只显示前5个
            memory_mb = proc['memory_info'].rss / 1024**2 if proc['memory_info'] else 0
            print(f"  PID {proc['pid']}: CPU {proc['cpu_percent']:.1f}%, 内存 {memory_mb:.2f}MB")
    else:
        print("\n❌ 未找到PostgreSQL进程")

    if redis_processes:
        print(f"\n🗂️  Redis进程 ({len(redis_processes)}个):")
        for proc in redis_processes:
            memory_mb = proc['memory_info'].rss / 1024**2 if proc['memory_info'] else 0
            print(f"  PID {proc['pid']}: CPU {proc['cpu_percent']:.1f}%, 内存 {memory_mb:.2f}MB")
    else:
        print("\n❌ 未找到Redis进程")

def get_optimization_recommendations():
    """获取系统优化建议"""

    recommendations = []

    # 内存建议
    memory = psutil.virtual_memory()
    if memory.percent > 90:
        recommendations.append("🔴 紧急: 内存使用率过高，考虑增加内存或优化应用程序")
    elif memory.percent > 80:
        recommendations.append("🟡 建议: 监控内存使用，考虑优化缓存策略")

    # CPU建议
    cpu_percent = psutil.cpu_percent(interval=1)
    if cpu_percent > 90:
        recommendations.append("🔴 紧急: CPU使用率过高，检查是否有死循环或优化算法")
    elif cpu_percent > 70:
        recommendations.append("🟡 建议: CPU使用率较高，考虑优化并发策略")

    # 磁盘建议
    disk_usage = psutil.disk_usage('/')
    if disk_usage.used / disk_usage.total > 0.9:
        recommendations.append("🔴 紧急: 磁盘空间不足，清理临时文件或扩容")
    elif disk_usage.used / disk_usage.total > 0.8:
        recommendations.append("🟡 建议: 磁盘空间较少，定期清理日志文件")

    # 进程建议
    process_count = len(psutil.pids())
    if process_count > 1000:
        recommendations.append("🟡 建议: 进程数较多，检查是否有僵尸进程")

    # 网络建议
    connections = psutil.net_connections()
    tcp_count = len([c for c in connections if c.type == 1])
    if tcp_count > 1000:
        recommendations.append("🟡 建议: TCP连接数较多，检查连接池配置")

    if not recommendations:
        recommendations.append("✅ 系统资源状况良好")

    return recommendations

if __name__ == "__main__":
    diagnose_system_resources()

    print("\n💡 优化建议:")
    print("=" * 50)
    for recommendation in get_optimization_recommendations():
        print(f"  {recommendation}")
```

---

## 📋 日志分析和诊断

### 自动化日志分析工具

```python
#!/usr/bin/env python3
"""
日志分析和诊断工具
"""
import re
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
import gzip

class LogAnalyzer:
    """日志分析器"""

    def __init__(self, log_directory="/h/novellus/test_results"):
        self.log_directory = Path(log_directory)
        self.error_patterns = {
            'connection_error': [
                r'Connection refused',
                r'Connection timeout',
                r'Connection reset by peer'
            ],
            'database_error': [
                r'relation .* does not exist',
                r'column .* does not exist',
                r'database .* does not exist'
            ],
            'authentication_error': [
                r'authentication failed',
                r'permission denied',
                r'invalid api key'
            ],
            'memory_error': [
                r'out of memory',
                r'memory allocation failed',
                r'cannot allocate memory'
            ],
            'timeout_error': [
                r'timeout',
                r'operation timed out',
                r'deadline exceeded'
            ]
        }

    def analyze_test_logs(self, hours_back=24):
        """分析测试日志"""

        cutoff_time = datetime.now() - timedelta(hours=hours_back)

        analysis_results = {
            'log_files_analyzed': 0,
            'total_log_lines': 0,
            'error_summary': defaultdict(int),
            'error_details': defaultdict(list),
            'performance_issues': [],
            'test_failures': [],
            'recommendations': []
        }

        # 查找日志文件
        log_files = []
        log_files.extend(self.log_directory.glob("*.log"))
        log_files.extend(self.log_directory.glob("**/*.log"))
        log_files.extend(self.log_directory.glob("*.log.gz"))

        for log_file in log_files:
            if log_file.stat().st_mtime < cutoff_time.timestamp():
                continue

            try:
                analysis_results['log_files_analyzed'] += 1
                self._analyze_single_log_file(log_file, analysis_results)
            except Exception as e:
                print(f"分析日志文件失败 {log_file}: {e}")

        # 生成建议
        analysis_results['recommendations'] = self._generate_recommendations(analysis_results)

        return analysis_results

    def _analyze_single_log_file(self, log_file, results):
        """分析单个日志文件"""

        # 读取日志文件
        content = self._read_log_file(log_file)
        lines = content.split('\n')
        results['total_log_lines'] += len(lines)

        for line_num, line in enumerate(lines, 1):
            if not line.strip():
                continue

            # 检查错误模式
            for error_type, patterns in self.error_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        results['error_summary'][error_type] += 1
                        results['error_details'][error_type].append({
                            'file': str(log_file),
                            'line': line_num,
                            'content': line.strip(),
                            'timestamp': self._extract_timestamp(line)
                        })
                        break

            # 检查性能问题
            if self._is_performance_issue(line):
                results['performance_issues'].append({
                    'file': str(log_file),
                    'line': line_num,
                    'content': line.strip(),
                    'timestamp': self._extract_timestamp(line)
                })

            # 检查测试失败
            if self._is_test_failure(line):
                results['test_failures'].append({
                    'file': str(log_file),
                    'line': line_num,
                    'content': line.strip(),
                    'timestamp': self._extract_timestamp(line)
                })

    def _read_log_file(self, log_file):
        """读取日志文件（支持压缩文件）"""

        if log_file.suffix == '.gz':
            with gzip.open(log_file, 'rt', encoding='utf-8') as f:
                return f.read()
        else:
            with open(log_file, 'r', encoding='utf-8') as f:
                return f.read()

    def _extract_timestamp(self, line):
        """提取时间戳"""

        # 尝试多种时间戳格式
        timestamp_patterns = [
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
            r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]'
        ]

        for pattern in timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(0).strip('[]')

        return None

    def _is_performance_issue(self, line):
        """检查是否是性能问题"""

        performance_indicators = [
            r'slow query',
            r'took \d+ms',
            r'timeout',
            r'high cpu',
            r'memory usage',
            r'latency'
        ]

        return any(re.search(pattern, line, re.IGNORECASE) for pattern in performance_indicators)

    def _is_test_failure(self, line):
        """检查是否是测试失败"""

        failure_indicators = [
            r'test.*failed',
            r'assertion.*failed',
            r'error.*in.*test',
            r'failed.*\d+.*test'
        ]

        return any(re.search(pattern, line, re.IGNORECASE) for pattern in failure_indicators)

    def _generate_recommendations(self, results):
        """生成诊断建议"""

        recommendations = []

        # 基于错误类型的建议
        if results['error_summary']['connection_error'] > 5:
            recommendations.append("🔴 频繁的连接错误，检查网络配置和服务状态")

        if results['error_summary']['database_error'] > 3:
            recommendations.append("🔴 数据库错误，检查数据库模式和表结构")

        if results['error_summary']['authentication_error'] > 0:
            recommendations.append("🔴 认证错误，检查API密钥和数据库凭证")

        if results['error_summary']['memory_error'] > 0:
            recommendations.append("🔴 内存不足，考虑增加内存或优化内存使用")

        if results['error_summary']['timeout_error'] > 10:
            recommendations.append("🟡 频繁超时，检查网络延迟和服务性能")

        # 基于性能问题的建议
        if len(results['performance_issues']) > 20:
            recommendations.append("🟡 性能问题较多，考虑优化算法和配置")

        # 基于测试失败的建议
        if len(results['test_failures']) > 5:
            recommendations.append("🟡 测试失败较多，检查测试环境和依赖")

        if not recommendations:
            recommendations.append("✅ 未发现严重问题")

        return recommendations

    def generate_log_report(self, analysis_results):
        """生成日志分析报告"""

        report = f"""
# 📋 日志分析报告

**分析时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**分析文件数:** {analysis_results['log_files_analyzed']}
**总日志行数:** {analysis_results['total_log_lines']}

## 🚨 错误摘要

"""

        for error_type, count in analysis_results['error_summary'].items():
            if count > 0:
                report += f"- **{error_type}:** {count} 次\n"

        if analysis_results['performance_issues']:
            report += f"\n## ⚡ 性能问题\n\n发现 {len(analysis_results['performance_issues'])} 个性能相关问题\n"

        if analysis_results['test_failures']:
            report += f"\n## ❌ 测试失败\n\n发现 {len(analysis_results['test_failures'])} 个测试失败\n"

        report += "\n## 💡 建议\n\n"
        for recommendation in analysis_results['recommendations']:
            report += f"- {recommendation}\n"

        report += "\n## 🔍 详细错误信息\n\n"
        for error_type, details in analysis_results['error_details'].items():
            if details:
                report += f"### {error_type}\n\n"
                for detail in details[:5]:  # 只显示前5个
                    report += f"- **文件:** {detail['file']}\n"
                    report += f"  **行号:** {detail['line']}\n"
                    report += f"  **内容:** {detail['content'][:100]}...\n\n"

        return report

def main():
    """主函数"""

    analyzer = LogAnalyzer()

    print("🔍 开始分析日志...")
    results = analyzer.analyze_test_logs(hours_back=24)

    print("\n📊 分析结果:")
    print(f"分析了 {results['log_files_analyzed']} 个日志文件")
    print(f"总共 {results['total_log_lines']} 行日志")

    if results['error_summary']:
        print("\n🚨 错误统计:")
        for error_type, count in results['error_summary'].items():
            print(f"  {error_type}: {count}")

    print(f"\n⚡ 性能问题: {len(results['performance_issues'])}")
    print(f"❌ 测试失败: {len(results['test_failures'])}")

    print("\n💡 建议:")
    for recommendation in results['recommendations']:
        print(f"  {recommendation}")

    # 生成报告文件
    report = analyzer.generate_log_report(results)
    report_file = Path("/h/novellus/test_results/log_analysis_report.md")

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n📄 详细报告已保存到: {report_file}")

if __name__ == "__main__":
    main()
```

---

## 🎯 快速诊断检查清单

### 测试启动前检查

```bash
#!/bin/bash
# 快速诊断脚本

echo "🎯 Novellus测试系统快速诊断"
echo "================================"

# 1. 环境检查
echo "1️⃣ 检查Python环境..."
python3 --version || echo "❌ Python3 未安装"
pip3 show asyncpg > /dev/null 2>&1 && echo "✅ asyncpg" || echo "❌ asyncpg"
pip3 show redis > /dev/null 2>&1 && echo "✅ redis" || echo "❌ redis"

# 2. 数据库检查
echo "2️⃣ 检查数据库连接..."
pg_isready -h localhost -p 5432 && echo "✅ PostgreSQL" || echo "❌ PostgreSQL"
redis-cli ping > /dev/null 2>&1 && echo "✅ Redis" || echo "❌ Redis"

# 3. 文件检查
echo "3️⃣ 检查关键文件..."
[ -f "/h/novellus/tests/test_pgvector_suite.py" ] && echo "✅ pgvector测试" || echo "❌ pgvector测试"
[ -f "/h/novellus/tests/test_ai_model_manager.py" ] && echo "✅ AI模型测试" || echo "❌ AI模型测试"
[ -f "/h/novellus/tests/automated_test_runner.py" ] && echo "✅ 自动化执行器" || echo "❌ 自动化执行器"

# 4. 权限检查
echo "4️⃣ 检查目录权限..."
[ -w "/h/novellus/test_results" ] && echo "✅ 结果目录可写" || echo "❌ 结果目录不可写"

# 5. 资源检查
echo "5️⃣ 检查系统资源..."
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.1f"), $3/$2 * 100.0}')
echo "内存使用率: ${MEMORY_USAGE}%"
[ $(echo "$MEMORY_USAGE < 90" | bc -l) -eq 1 ] && echo "✅ 内存充足" || echo "⚠️ 内存使用率高"

DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
echo "磁盘使用率: ${DISK_USAGE}%"
[ $DISK_USAGE -lt 90 ] && echo "✅ 磁盘空间充足" || echo "⚠️ 磁盘空间不足"

echo "================================"
echo "✅ 诊断完成"
```

---

## 📞 获取支持

如果按照本故障排除指南仍无法解决问题，请：

1. **收集诊断信息:**
   ```bash
   # 运行完整诊断
   python3 /h/novellus/tests/diagnose_environment.py > diagnosis.log 2>&1

   # 收集日志
   tar -czf novellus_logs.tar.gz /h/novellus/test_results/*.log
   ```

2. **记录问题详情:**
   - 具体错误信息
   - 重现步骤
   - 环境配置
   - 相关日志

3. **创建问题报告:**
   包含上述诊断信息和问题描述

---

## 📚 相关文档

- [测试架构文档](testing_architecture.md)
- [性能优化指南](performance_optimization.md)
- [部署指南](deployment_guide.md)
- [API文档](api_documentation.md)

---

*最后更新: 2024年9月20日*