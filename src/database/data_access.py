"""
数据访问层 API
提供多小说兼容的数据操作接口
"""

import asyncio
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import json
import logging
from contextlib import asynccontextmanager

import asyncpg
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import MongoClient
from pymongo.database import Database as SyncDatabase

from .models import *
from config import config


logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """数据库操作异常"""
    pass


class NovelDataManager:
    """小说数据管理器 - 提供数据隔离和安全访问"""

    def __init__(self, novel_id: int, pg_pool: asyncpg.Pool, mongo_db: AsyncIOMotorDatabase):
        self.novel_id = novel_id
        self.pg_pool = pg_pool
        self.mongo_db = mongo_db
        self._novel_cache = None

    async def _get_novel_info(self) -> Novel:
        """获取小说基础信息"""
        if self._novel_cache is None:
            async with self.pg_pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM novels WHERE id = $1 AND status != 'archived'",
                    self.novel_id
                )
                if not row:
                    raise DatabaseError(f"小说 {self.novel_id} 不存在或已归档")
                self._novel_cache = Novel(**dict(row))
        return self._novel_cache

    async def _validate_access(self, operation: str = "read"):
        """验证访问权限"""
        novel = await self._get_novel_info()
        if novel.status == 'archived':
            raise DatabaseError("无法访问已归档的小说")

    # =========================================================================
    # 小说管理 API
    # =========================================================================

    async def get_novel_summary(self) -> NovelSummary:
        """获取小说摘要信息"""
        await self._validate_access()

        async with self.pg_pool.acquire() as conn:
            # 获取小说基础信息
            novel_row = await conn.fetchrow(
                "SELECT * FROM novels WHERE id = $1", self.novel_id
            )
            novel = Novel(**dict(novel_row))

            # 获取实体类型
            entity_types_rows = await conn.fetch(
                "SELECT * FROM entity_types WHERE novel_id = $1 AND is_active = true",
                self.novel_id
            )
            entity_types = [EntityType(**dict(row)) for row in entity_types_rows]

            # 获取实体统计
            entity_counts = {}
            for et in entity_types:
                count = await conn.fetchval(
                    "SELECT COUNT(*) FROM entities WHERE novel_id = $1 AND entity_type_id = $2 AND status = 'active'",
                    self.novel_id, et.id
                )
                entity_counts[et.name] = count

            # 获取最近事件
            recent_events_rows = await conn.fetch(
                "SELECT * FROM events WHERE novel_id = $1 ORDER BY created_at DESC LIMIT 5",
                self.novel_id
            )
            recent_events = [Event(**dict(row)) for row in recent_events_rows]

        return NovelSummary(
            novel=novel,
            entity_types=entity_types,
            entity_counts=entity_counts,
            recent_events=recent_events
        )

    async def update_novel_settings(self, settings: Dict[str, Any]) -> bool:
        """更新小说配置"""
        await self._validate_access("write")

        async with self.pg_pool.acquire() as conn:
            await conn.execute(
                "UPDATE novels SET settings = $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2",
                json.dumps(settings), self.novel_id
            )

        # 清除缓存
        self._novel_cache = None
        return True

    # =========================================================================
    # 实体管理 API
    # =========================================================================

    async def create_entity(self, request: CreateEntityRequest) -> int:
        """创建实体"""
        await self._validate_access("write")

        if request.novel_id != self.novel_id:
            raise DatabaseError("请求的小说ID与当前管理器不匹配")

        async with self.pg_pool.acquire() as conn:
            async with conn.transaction():
                # 获取实体类型
                entity_type_row = await conn.fetchrow(
                    "SELECT * FROM entity_types WHERE novel_id = $1 AND name = $2 AND is_active = true",
                    self.novel_id, request.entity_type_name
                )
                if not entity_type_row:
                    raise DatabaseError(f"实体类型 '{request.entity_type_name}' 不存在")

                entity_type = EntityType(**dict(entity_type_row))

                # 验证属性
                validated_attributes = await self._validate_entity_attributes(
                    request.attributes, entity_type
                )

                # 创建实体
                entity_id = await conn.fetchval(
                    """INSERT INTO entities
                       (novel_id, entity_type_id, name, code, attributes, tags, priority)
                       VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id""",
                    self.novel_id, entity_type.id, request.name, request.code,
                    json.dumps(validated_attributes), request.tags, request.priority
                )

                # 创建 MongoDB 档案
                if request.profile:
                    await self._create_entity_profile(entity_id, request.entity_type_name, request.profile)

        logger.info(f"创建实体成功: novel_id={self.novel_id}, entity_id={entity_id}, name={request.name}")
        return entity_id

    async def get_entity(self, entity_id: int, include_profile: bool = True) -> Optional[EntityWithProfile]:
        """获取实体详情"""
        await self._validate_access()

        async with self.pg_pool.acquire() as conn:
            # 获取实体基础信息
            entity_row = await conn.fetchrow(
                """SELECT e.*, et.name as entity_type_name
                   FROM entities e
                   JOIN entity_types et ON e.entity_type_id = et.id
                   WHERE e.novel_id = $1 AND e.id = $2 AND e.status != 'deleted'""",
                self.novel_id, entity_id
            )

            if not entity_row:
                return None

            entity_dict = dict(entity_row)
            entity_type_name = entity_dict.pop('entity_type_name')
            entity = EntityWithProfile(**entity_dict)
            entity.entity_type_name = entity_type_name

            # 获取分类信息
            categories_rows = await conn.fetch(
                """SELECT c.* FROM categories c
                   JOIN entity_categories ec ON c.id = ec.category_id
                   WHERE ec.novel_id = $1 AND ec.entity_id = $2
                   AND (ec.valid_to IS NULL OR ec.valid_to > CURRENT_TIMESTAMP)""",
                self.novel_id, entity_id
            )
            entity.categories = [Category(**dict(row)) for row in categories_rows]

            # 获取关系信息
            relationships_rows = await conn.fetch(
                """SELECT * FROM entity_relationships
                   WHERE novel_id = $1 AND (source_entity_id = $2 OR target_entity_id = $2)
                   AND status = 'active'
                   AND (valid_to IS NULL OR valid_to > CURRENT_TIMESTAMP)""",
                self.novel_id, entity_id
            )
            entity.relationships = [EntityRelationship(**dict(row)) for row in relationships_rows]

        # 获取 MongoDB 档案
        if include_profile:
            profile_doc = await self.mongo_db.entity_profiles.find_one({
                "novel_id": self.novel_id,
                "entity_id": entity_id
            })
            if profile_doc:
                entity.profile = profile_doc.get('profile', {})

        return entity

    async def update_entity(self, entity_id: int, request: UpdateEntityRequest) -> bool:
        """更新实体"""
        await self._validate_access("write")

        async with self.pg_pool.acquire() as conn:
            async with conn.transaction():
                # 检查实体是否存在
                existing = await conn.fetchrow(
                    "SELECT * FROM entities WHERE novel_id = $1 AND id = $2",
                    self.novel_id, entity_id
                )
                if not existing:
                    raise DatabaseError(f"实体 {entity_id} 不存在")

                # 构建更新字段
                update_fields = []
                update_values = []
                value_index = 1

                if request.name is not None:
                    update_fields.append(f"name = ${value_index}")
                    update_values.append(request.name)
                    value_index += 1

                if request.code is not None:
                    update_fields.append(f"code = ${value_index}")
                    update_values.append(request.code)
                    value_index += 1

                if request.status is not None:
                    update_fields.append(f"status = ${value_index}")
                    update_values.append(request.status.value)
                    value_index += 1

                if request.attributes is not None:
                    update_fields.append(f"attributes = ${value_index}")
                    update_values.append(json.dumps(request.attributes))
                    value_index += 1

                if request.tags is not None:
                    update_fields.append(f"tags = ${value_index}")
                    update_values.append(request.tags)
                    value_index += 1

                if request.priority is not None:
                    update_fields.append(f"priority = ${value_index}")
                    update_values.append(request.priority)
                    value_index += 1

                if update_fields:
                    update_fields.append("updated_at = CURRENT_TIMESTAMP")
                    update_fields.append(f"version = version + 1")

                    update_values.extend([self.novel_id, entity_id])

                    query = f"""UPDATE entities SET {', '.join(update_fields)}
                               WHERE novel_id = ${value_index} AND id = ${value_index + 1}"""
                    await conn.execute(query, *update_values)

                # 更新 MongoDB 档案
                if request.profile is not None:
                    await self.mongo_db.entity_profiles.update_one(
                        {"novel_id": self.novel_id, "entity_id": entity_id},
                        {"$set": {"profile": request.profile, "metadata.last_updated": datetime.utcnow()}},
                        upsert=True
                    )

        logger.info(f"更新实体成功: novel_id={self.novel_id}, entity_id={entity_id}")
        return True

    async def delete_entity(self, entity_id: int, soft_delete: bool = True) -> bool:
        """删除实体"""
        await self._validate_access("write")

        async with self.pg_pool.acquire() as conn:
            async with conn.transaction():
                if soft_delete:
                    # 软删除：标记为已删除
                    await conn.execute(
                        """UPDATE entities SET status = 'deleted', updated_at = CURRENT_TIMESTAMP
                           WHERE novel_id = $1 AND id = $2""",
                        self.novel_id, entity_id
                    )
                else:
                    # 硬删除：完全删除记录
                    await conn.execute(
                        "DELETE FROM entities WHERE novel_id = $1 AND id = $2",
                        self.novel_id, entity_id
                    )

                # 删除相关关系
                await conn.execute(
                    """UPDATE entity_relationships SET status = 'ended', valid_to = CURRENT_TIMESTAMP
                       WHERE novel_id = $1 AND (source_entity_id = $2 OR target_entity_id = $2)""",
                    self.novel_id, entity_id
                )

        # 标记 MongoDB 档案为已删除
        await self.mongo_db.entity_profiles.update_one(
            {"novel_id": self.novel_id, "entity_id": entity_id},
            {"$set": {"metadata.deleted": True, "metadata.deleted_at": datetime.utcnow()}}
        )

        logger.info(f"删除实体成功: novel_id={self.novel_id}, entity_id={entity_id}, soft_delete={soft_delete}")
        return True

    async def search_entities(self, query: QueryRequest) -> PaginatedResponse:
        """搜索实体"""
        await self._validate_access()

        if query.novel_id != self.novel_id:
            raise DatabaseError("查询的小说ID与当前管理器不匹配")

        async with self.pg_pool.acquire() as conn:
            # 构建查询条件
            where_conditions = ["e.novel_id = $1", "e.status != 'deleted'"]
            query_params = [self.novel_id]
            param_index = 2

            # 添加过滤条件
            if query.filters:
                if 'entity_type' in query.filters:
                    where_conditions.append(f"et.name = ${param_index}")
                    query_params.append(query.filters['entity_type'])
                    param_index += 1

                if 'name_like' in query.filters:
                    where_conditions.append(f"e.name ILIKE ${param_index}")
                    query_params.append(f"%{query.filters['name_like']}%")
                    param_index += 1

                if 'tags' in query.filters:
                    where_conditions.append(f"e.tags && ${param_index}")
                    query_params.append(query.filters['tags'])
                    param_index += 1

                if 'priority_min' in query.filters:
                    where_conditions.append(f"e.priority >= ${param_index}")
                    query_params.append(query.filters['priority_min'])
                    param_index += 1

            where_clause = " AND ".join(where_conditions)

            # 构建排序
            order_clause = "e.created_at DESC"
            if query.sort:
                if query.sort in ['name', 'created_at', 'updated_at', 'priority']:
                    order_clause = f"e.{query.sort} DESC"

            # 查询总数
            count_query = f"""
                SELECT COUNT(*)
                FROM entities e
                JOIN entity_types et ON e.entity_type_id = et.id
                WHERE {where_clause}
            """
            total = await conn.fetchval(count_query, *query_params)

            # 查询数据
            data_query = f"""
                SELECT e.*, et.name as entity_type_name
                FROM entities e
                JOIN entity_types et ON e.entity_type_id = et.id
                WHERE {where_clause}
                ORDER BY {order_clause}
                LIMIT ${param_index} OFFSET ${param_index + 1}
            """
            query_params.extend([query.limit, query.offset])

            rows = await conn.fetch(data_query, *query_params)

            # 转换为模型
            entities = []
            for row in rows:
                entity_dict = dict(row)
                entity_type_name = entity_dict.pop('entity_type_name')
                entity = EntityWithProfile(**entity_dict)
                entity.entity_type_name = entity_type_name
                entities.append(entity)

        # 计算分页信息
        page = (query.offset // query.limit) + 1
        total_pages = (total + query.limit - 1) // query.limit

        return PaginatedResponse(
            items=entities,
            total=total,
            page=page,
            page_size=query.limit,
            has_next=page < total_pages,
            has_prev=page > 1
        )

    # =========================================================================
    # 关系管理 API
    # =========================================================================

    async def create_relationship(self, source_id: int, target_id: int,
                                relationship_type: str, **kwargs) -> int:
        """创建实体关系"""
        await self._validate_access("write")

        async with self.pg_pool.acquire() as conn:
            # 验证实体存在
            source_exists = await conn.fetchval(
                "SELECT 1 FROM entities WHERE novel_id = $1 AND id = $2 AND status != 'deleted'",
                self.novel_id, source_id
            )
            target_exists = await conn.fetchval(
                "SELECT 1 FROM entities WHERE novel_id = $1 AND id = $2 AND status != 'deleted'",
                self.novel_id, target_id
            )

            if not source_exists or not target_exists:
                raise DatabaseError("源实体或目标实体不存在")

            # 创建关系
            relationship_id = await conn.fetchval(
                """INSERT INTO entity_relationships
                   (novel_id, source_entity_id, target_entity_id, relationship_type, attributes, strength)
                   VALUES ($1, $2, $3, $4, $5, $6) RETURNING id""",
                self.novel_id, source_id, target_id, relationship_type,
                json.dumps(kwargs.get('attributes', {})), kwargs.get('strength', 1)
            )

        logger.info(f"创建关系成功: {source_id} -> {target_id} ({relationship_type})")
        return relationship_id

    async def get_entity_relationships(self, entity_id: int) -> List[EntityRelationship]:
        """获取实体的所有关系"""
        await self._validate_access()

        async with self.pg_pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT * FROM entity_relationships
                   WHERE novel_id = $1 AND (source_entity_id = $2 OR target_entity_id = $2)
                   AND status = 'active'
                   AND (valid_to IS NULL OR valid_to > CURRENT_TIMESTAMP)
                   ORDER BY created_at DESC""",
                self.novel_id, entity_id
            )

        return [EntityRelationship(**dict(row)) for row in rows]

    # =========================================================================
    # 事件管理 API
    # =========================================================================

    async def create_event(self, event: Event, participants: List[int] = None) -> int:
        """创建事件"""
        await self._validate_access("write")

        async with self.pg_pool.acquire() as conn:
            async with conn.transaction():
                # 创建事件
                event_id = await conn.fetchval(
                    """INSERT INTO events
                       (novel_id, name, event_type, occurred_at, in_world_time, sequence_order,
                        location_entity_id, impact_level, scope, attributes, description, status)
                       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12) RETURNING id""",
                    self.novel_id, event.name, event.event_type, event.occurred_at,
                    event.in_world_time, event.sequence_order, event.location_entity_id,
                    event.impact_level, event.scope, json.dumps(event.attributes),
                    event.description, event.status.value
                )

                # 添加参与者
                if participants:
                    for entity_id in participants:
                        await conn.execute(
                            """INSERT INTO event_participants (novel_id, event_id, entity_id)
                               VALUES ($1, $2, $3)""",
                            self.novel_id, event_id, entity_id
                        )

        logger.info(f"创建事件成功: novel_id={self.novel_id}, event_id={event_id}, name={event.name}")
        return event_id

    async def get_story_timeline(self, limit: int = 100) -> List[Event]:
        """获取故事时间线"""
        await self._validate_access()

        async with self.pg_pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT * FROM events
                   WHERE novel_id = $1 AND status != 'cancelled'
                   ORDER BY sequence_order ASC, occurred_at ASC
                   LIMIT $2""",
                self.novel_id, limit
            )

        return [Event(**dict(row)) for row in rows]

    # =========================================================================
    # 辅助方法
    # =========================================================================

    async def _validate_entity_attributes(self, attributes: Dict[str, Any],
                                         entity_type: EntityType) -> Dict[str, Any]:
        """验证实体属性"""
        schema = entity_type.schema_definition
        validation_rules = entity_type.validation_rules

        # 这里可以添加复杂的验证逻辑
        # 简单验证示例
        validated = attributes.copy()

        # 检查必需字段
        required_fields = schema.get('required_fields', [])
        for field in required_fields:
            if field not in attributes:
                raise DatabaseError(f"缺少必需字段: {field}")

        return validated

    async def _create_entity_profile(self, entity_id: int, entity_type: str, profile: Dict[str, Any]):
        """创建实体档案"""
        novel = await self._get_novel_info()

        profile_doc = {
            "novel_id": self.novel_id,
            "novel_code": novel.code,
            "entity_id": entity_id,
            "entity_type": entity_type,
            "profile": profile,
            "metadata": {
                "created_at": datetime.utcnow(),
                "version": "1.0",
                "tags": []
            }
        }

        await self.mongo_db.entity_profiles.insert_one(profile_doc)


class GlobalDataManager:
    """全局数据管理器 - 提供跨小说的数据操作"""

    def __init__(self, pg_pool: asyncpg.Pool, mongo_db: AsyncIOMotorDatabase):
        self.pg_pool = pg_pool
        self.mongo_db = mongo_db

    async def create_novel(self, novel: Novel, template_code: str = None) -> int:
        """创建新小说"""
        async with self.pg_pool.acquire() as conn:
            async with conn.transaction():
                # 创建小说记录
                novel_id = await conn.fetchval(
                    """INSERT INTO novels (title, code, author, genre, world_type, settings)
                       VALUES ($1, $2, $3, $4, $5, $6) RETURNING id""",
                    novel.title, novel.code, novel.author, novel.genre,
                    novel.world_type, json.dumps(novel.settings)
                )

                # 应用模板
                if template_code:
                    await self._apply_template(conn, novel_id, template_code)

        logger.info(f"创建小说成功: novel_id={novel_id}, title={novel.title}")
        return novel_id

    async def get_novel_list(self, status: str = None) -> List[Novel]:
        """获取小说列表"""
        async with self.pg_pool.acquire() as conn:
            query = "SELECT * FROM novels"
            params = []

            if status:
                query += " WHERE status = $1"
                params.append(status)

            query += " ORDER BY created_at DESC"

            rows = await conn.fetch(query, *params)

        return [Novel(**dict(row)) for row in rows]

    async def get_novel_manager(self, novel_id: int) -> NovelDataManager:
        """获取小说数据管理器"""
        return NovelDataManager(novel_id, self.pg_pool, self.mongo_db)

    async def _apply_template(self, conn, novel_id: int, template_code: str):
        """应用小说模板"""
        # 从 MongoDB 获取模板
        template = await self.mongo_db.novel_templates.find_one({
            "template_code": template_code
        })

        if not template:
            raise DatabaseError(f"模板 {template_code} 不存在")

        # 创建默认实体类型
        entity_templates = template.get('entity_templates', {})
        for entity_type_name, config in entity_templates.items():
            await conn.execute(
                """INSERT INTO entity_types (novel_id, name, display_name, schema_definition)
                   VALUES ($1, $2, $3, $4)""",
                novel_id, entity_type_name,
                config.get('display_name', entity_type_name.title()),
                json.dumps(config)
            )

        logger.info(f"应用模板成功: novel_id={novel_id}, template={template_code}")


# =============================================================================
# 数据库连接管理
# =============================================================================

class DatabaseManager:
    """数据库连接管理器"""

    def __init__(self):
        self.pg_pool: Optional[asyncpg.Pool] = None
        self.mongo_db: Optional[AsyncIOMotorDatabase] = None
        self._initialized = False

    async def initialize(self):
        """初始化数据库连接"""
        if self._initialized:
            return

        # 初始化 PostgreSQL 连接池
        self.pg_pool = await asyncpg.create_pool(
            host=config.postgres_host,
            port=config.postgres_port,
            database=config.postgres_db,
            user=config.postgres_user,
            password=config.postgres_password,
            min_size=5,
            max_size=20,
            command_timeout=30
        )

        # 初始化 MongoDB 连接
        from motor.motor_asyncio import AsyncIOMotorClient
        mongo_client = AsyncIOMotorClient(config.mongodb_url)
        self.mongo_db = mongo_client[config.mongodb_db]

        # 测试连接
        await self.pg_pool.fetchval("SELECT 1")
        await mongo_client.admin.command('ping')

        self._initialized = True
        logger.info("数据库连接初始化成功")

    async def close(self):
        """关闭数据库连接"""
        if self.pg_pool:
            await self.pg_pool.close()
        # MongoDB 客户端会自动管理连接

        self._initialized = False
        logger.info("数据库连接已关闭")

    def get_global_manager(self) -> GlobalDataManager:
        """获取全局数据管理器"""
        if not self._initialized:
            raise DatabaseError("数据库未初始化")
        return GlobalDataManager(self.pg_pool, self.mongo_db)

    def get_novel_manager(self, novel_id: int) -> NovelDataManager:
        """获取小说数据管理器"""
        if not self._initialized:
            raise DatabaseError("数据库未初始化")
        return NovelDataManager(novel_id, self.pg_pool, self.mongo_db)


# 全局数据库管理器实例
db_manager = DatabaseManager()


# =============================================================================
# 便捷函数
# =============================================================================

async def init_database():
    """初始化数据库"""
    await db_manager.initialize()


async def close_database():
    """关闭数据库"""
    await db_manager.close()


def get_global_manager() -> GlobalDataManager:
    """获取全局数据管理器"""
    return db_manager.get_global_manager()


def get_novel_manager(novel_id: int) -> NovelDataManager:
    """获取小说数据管理器"""
    return db_manager.get_novel_manager(novel_id)