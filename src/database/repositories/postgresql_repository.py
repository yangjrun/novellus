"""
PostgreSQL数据仓库 - 处理关系型数据库操作
"""

import logging
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from datetime import datetime
import json

from ..connection_manager import PostgreSQLManager, DatabaseError
from ..models import *

logger = logging.getLogger(__name__)

def _deserialize_json_fields(row_dict: dict, *fields) -> dict:
    """反序列化JSON字段"""
    for field in fields:
        if field in row_dict and isinstance(row_dict[field], str):
            try:
                row_dict[field] = json.loads(row_dict[field])
            except (json.JSONDecodeError, TypeError):
                row_dict[field] = {}
    return row_dict


class PostgreSQLRepository:
    """PostgreSQL数据仓库"""

    def __init__(self, postgres_manager: PostgreSQLManager):
        self.postgres = postgres_manager

    # =============================================================================
    # 项目管理操作
    # =============================================================================

    async def create_project(self, project_data: ProjectCreate) -> Project:
        """创建项目"""
        async with self.postgres.get_transaction() as conn:
            query = """
                INSERT INTO projects (name, title, description, author, genre, metadata)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id, name, title, description, author, genre, status, metadata, created_at, updated_at
            """
            row = await conn.fetchrow(
                query,
                project_data.name,
                project_data.title,
                project_data.description,
                project_data.author,
                project_data.genre,
                json.dumps(project_data.metadata)
            )
            return Project(**_deserialize_json_fields(dict(row), "metadata"))

    async def get_project_by_id(self, project_id: UUID) -> Optional[Project]:
        """根据ID获取项目"""
        async with self.postgres.get_connection() as conn:
            query = "SELECT * FROM projects WHERE id = $1"
            row = await conn.fetchrow(query, project_id)
            return Project(**_deserialize_json_fields(dict(row), "metadata")) if row else None

    async def get_project_by_name(self, name: str) -> Optional[Project]:
        """根据名称获取项目"""
        async with self.postgres.get_connection() as conn:
            query = "SELECT * FROM projects WHERE name = $1"
            row = await conn.fetchrow(query, name)
            return Project(**_deserialize_json_fields(dict(row), "metadata")) if row else None

    async def get_projects(
        self,
        status: Optional[ProjectStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Project]:
        """获取项目列表"""
        async with self.postgres.get_connection() as conn:
            if status:
                query = """
                    SELECT * FROM projects
                    WHERE status = $1
                    ORDER BY updated_at DESC
                    OFFSET $2 LIMIT $3
                """
                rows = await conn.fetch(query, status.value, skip, limit)
            else:
                query = """
                    SELECT * FROM projects
                    ORDER BY updated_at DESC
                    OFFSET $1 LIMIT $2
                """
                rows = await conn.fetch(query, skip, limit)

            return [Project(**_deserialize_json_fields(dict(row), "metadata")) for row in rows]

    async def update_project(self, project_id: UUID, update_data: ProjectUpdate) -> Optional[Project]:
        """更新项目"""
        updates = []
        params = []
        param_count = 1

        # 构建动态更新查询
        if update_data.title is not None:
            updates.append(f"title = ${param_count}")
            params.append(update_data.title)
            param_count += 1

        if update_data.description is not None:
            updates.append(f"description = ${param_count}")
            params.append(update_data.description)
            param_count += 1

        if update_data.author is not None:
            updates.append(f"author = ${param_count}")
            params.append(update_data.author)
            param_count += 1

        if update_data.genre is not None:
            updates.append(f"genre = ${param_count}")
            params.append(update_data.genre)
            param_count += 1

        if update_data.status is not None:
            updates.append(f"status = ${param_count}")
            params.append(update_data.status.value)
            param_count += 1

        if update_data.metadata is not None:
            updates.append(f"metadata = ${param_count}")
            params.append(json.dumps(update_data.metadata))
            param_count += 1

        if not updates:
            return await self.get_project_by_id(project_id)

        params.append(project_id)
        query = f"""
            UPDATE projects
            SET {', '.join(updates)}
            WHERE id = ${param_count}
            RETURNING *
        """

        async with self.postgres.get_transaction() as conn:
            row = await conn.fetchrow(query, *params)
            return Project(**_deserialize_json_fields(dict(row), "metadata")) if row else None

    # =============================================================================
    # 小说管理操作
    # =============================================================================

    async def create_novel(self, novel_data: NovelCreate) -> Novel:
        """创建小说"""
        async with self.postgres.get_transaction() as conn:
            query = """
                INSERT INTO novels (project_id, name, title, description, volume_number, metadata)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
            """
            row = await conn.fetchrow(
                query,
                novel_data.project_id,
                novel_data.name,
                novel_data.title,
                novel_data.description,
                novel_data.volume_number,
                json.dumps(novel_data.metadata)
            )
            return Novel(**_deserialize_json_fields(dict(row), "metadata"))

    async def get_novel_by_id(self, novel_id: UUID) -> Optional[Novel]:
        """根据ID获取小说"""
        async with self.postgres.get_connection() as conn:
            query = "SELECT * FROM novels WHERE id = $1"
            row = await conn.fetchrow(query, novel_id)
            return Novel(**_deserialize_json_fields(dict(row), "metadata")) if row else None

    async def get_novel_by_name(self, project_id: UUID, name: str) -> Optional[Novel]:
        """根据项目ID和名称获取小说"""
        async with self.postgres.get_connection() as conn:
            query = "SELECT * FROM novels WHERE project_id = $1 AND name = $2"
            row = await conn.fetchrow(query, project_id, name)
            return Novel(**_deserialize_json_fields(dict(row), "metadata")) if row else None

    async def get_novels_by_project(
        self,
        project_id: UUID,
        status: Optional[NovelStatus] = None
    ) -> List[Novel]:
        """获取项目下的小说列表"""
        async with self.postgres.get_connection() as conn:
            if status:
                query = """
                    SELECT * FROM novels
                    WHERE project_id = $1 AND status = $2
                    ORDER BY volume_number, created_at
                """
                rows = await conn.fetch(query, project_id, status.value)
            else:
                query = """
                    SELECT * FROM novels
                    WHERE project_id = $1
                    ORDER BY volume_number, created_at
                """
                rows = await conn.fetch(query, project_id)

            return [Novel(**_deserialize_json_fields(dict(row), "metadata")) for row in rows]

    # =============================================================================
    # 内容批次操作
    # =============================================================================

    async def create_content_batch(self, batch_data: ContentBatchCreate) -> ContentBatch:
        """创建内容批次"""
        async with self.postgres.get_transaction() as conn:
            query = """
                INSERT INTO content_batches (
                    novel_id, batch_name, batch_number, batch_type,
                    description, priority, due_date, metadata
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING *
            """
            row = await conn.fetchrow(
                query,
                batch_data.novel_id,
                batch_data.batch_name,
                batch_data.batch_number,
                batch_data.batch_type.value,
                batch_data.description,
                batch_data.priority,
                batch_data.due_date,
                json.dumps(batch_data.metadata)
            )
            return ContentBatch(**_deserialize_json_fields(dict(row), "metadata"))

    async def get_content_batch_by_id(self, batch_id: UUID) -> Optional[ContentBatch]:
        """根据ID获取内容批次"""
        async with self.postgres.get_connection() as conn:
            query = "SELECT * FROM content_batches WHERE id = $1"
            row = await conn.fetchrow(query, batch_id)
            return ContentBatch(**_deserialize_json_fields(dict(row), "metadata")) if row else None

    async def get_content_batch_by_number(self, novel_id: UUID, batch_number: int) -> Optional[ContentBatch]:
        """根据小说ID和批次编号获取内容批次"""
        async with self.postgres.get_connection() as conn:
            query = "SELECT * FROM content_batches WHERE novel_id = $1 AND batch_number = $2"
            row = await conn.fetchrow(query, novel_id, batch_number)
            return ContentBatch(**_deserialize_json_fields(dict(row), "metadata")) if row else None

    async def get_content_batches_by_novel(
        self,
        novel_id: UUID,
        batch_type: Optional[BatchType] = None,
        status: Optional[BatchStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ContentBatch]:
        """获取小说的内容批次列表"""
        async with self.postgres.get_connection() as conn:
            conditions = ["novel_id = $1"]
            params = [novel_id]
            param_count = 2

            if batch_type:
                conditions.append(f"batch_type = ${param_count}")
                params.append(batch_type.value)
                param_count += 1

            if status:
                conditions.append(f"status = ${param_count}")
                params.append(status.value)
                param_count += 1

            where_clause = " AND ".join(conditions)
            query = f"""
                SELECT * FROM content_batches
                WHERE {where_clause}
                ORDER BY batch_number
                OFFSET ${param_count} LIMIT ${param_count + 1}
            """
            params.extend([skip, limit])

            rows = await conn.fetch(query, *params)
            return [ContentBatch(**_deserialize_json_fields(dict(row), "metadata")) for row in rows]

    async def update_content_batch(
        self,
        batch_id: UUID,
        update_data: ContentBatchUpdate
    ) -> Optional[ContentBatch]:
        """更新内容批次"""
        updates = []
        params = []
        param_count = 1

        # 构建动态更新查询
        for field, value in update_data.dict(exclude_unset=True).items():
            if value is not None:
                if field in ['status', 'batch_type'] and hasattr(value, 'value'):
                    value = value.value
                updates.append(f"{field} = ${param_count}")
                params.append(value)
                param_count += 1

        if not updates:
            return await self.get_content_batch_by_id(batch_id)

        params.append(batch_id)
        query = f"""
            UPDATE content_batches
            SET {', '.join(updates)}
            WHERE id = ${param_count}
            RETURNING *
        """

        async with self.postgres.get_transaction() as conn:
            row = await conn.fetchrow(query, *params)
            return ContentBatch(**_deserialize_json_fields(dict(row), "metadata")) if row else None

    async def delete_content_batch(self, batch_id: UUID) -> bool:
        """删除内容批次"""
        async with self.postgres.get_transaction() as conn:
            query = "DELETE FROM content_batches WHERE id = $1"
            result = await conn.execute(query, batch_id)
            return result == "DELETE 1"

    # =============================================================================
    # 内容段落操作
    # =============================================================================

    async def create_content_segment(self, segment_data: ContentSegmentCreate) -> ContentSegment:
        """创建内容段落"""
        async with self.postgres.get_transaction() as conn:
            query = """
                INSERT INTO content_segments (
                    batch_id, segment_type, title, content, sequence_order,
                    tags, emotions, characters, locations, metadata
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                RETURNING *
            """
            row = await conn.fetchrow(
                query,
                segment_data.batch_id,
                segment_data.segment_type.value,
                segment_data.title,
                segment_data.content,
                segment_data.sequence_order,
                segment_data.tags,
                segment_data.emotions,
                [str(char_id) for char_id in segment_data.characters],
                [str(loc_id) for loc_id in segment_data.locations],
                json.dumps(segment_data.metadata)
            )
            return ContentSegment(**_deserialize_json_fields(dict(row), "metadata"))

    async def get_content_segment_by_id(self, segment_id: UUID) -> Optional[ContentSegment]:
        """根据ID获取内容段落"""
        async with self.postgres.get_connection() as conn:
            query = "SELECT * FROM content_segments WHERE id = $1"
            row = await conn.fetchrow(query, segment_id)
            return ContentSegment(**_deserialize_json_fields(dict(row), "metadata")) if row else None

    async def get_content_segment_by_sequence(
        self,
        batch_id: UUID,
        sequence_order: int
    ) -> Optional[ContentSegment]:
        """根据批次ID和序列顺序获取内容段落"""
        async with self.postgres.get_connection() as conn:
            query = "SELECT * FROM content_segments WHERE batch_id = $1 AND sequence_order = $2"
            row = await conn.fetchrow(query, batch_id, sequence_order)
            return ContentSegment(**_deserialize_json_fields(dict(row), "metadata")) if row else None

    async def get_content_segments_by_batch(
        self,
        batch_id: UUID,
        segment_type: Optional[SegmentType] = None,
        status: Optional[SegmentStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ContentSegment]:
        """获取批次的内容段落列表"""
        async with self.postgres.get_connection() as conn:
            conditions = ["batch_id = $1"]
            params = [batch_id]
            param_count = 2

            if segment_type:
                conditions.append(f"segment_type = ${param_count}")
                params.append(segment_type.value)
                param_count += 1

            if status:
                conditions.append(f"status = ${param_count}")
                params.append(status.value)
                param_count += 1

            where_clause = " AND ".join(conditions)
            query = f"""
                SELECT * FROM content_segments
                WHERE {where_clause}
                ORDER BY sequence_order
                OFFSET ${param_count} LIMIT ${param_count + 1}
            """
            params.extend([skip, limit])

            rows = await conn.fetch(query, *params)
            return [ContentSegment(**_deserialize_json_fields(dict(row), "metadata")) for row in rows]

    async def update_content_segment(
        self,
        segment_id: UUID,
        update_data: ContentSegmentUpdate
    ) -> Optional[ContentSegment]:
        """更新内容段落"""
        updates = []
        params = []
        param_count = 1

        # 构建动态更新查询
        for field, value in update_data.dict(exclude_unset=True).items():
            if value is not None:
                if field in ['segment_type', 'status'] and hasattr(value, 'value'):
                    value = value.value
                elif field in ['characters', 'locations']:
                    value = [str(item_id) for item_id in value]
                updates.append(f"{field} = ${param_count}")
                params.append(value)
                param_count += 1

        if not updates:
            return await self.get_content_segment_by_id(segment_id)

        params.append(segment_id)
        query = f"""
            UPDATE content_segments
            SET {', '.join(updates)}
            WHERE id = ${param_count}
            RETURNING *
        """

        async with self.postgres.get_transaction() as conn:
            row = await conn.fetchrow(query, *params)
            return ContentSegment(**_deserialize_json_fields(dict(row), "metadata")) if row else None

    async def delete_content_segment(self, segment_id: UUID) -> bool:
        """删除内容段落"""
        async with self.postgres.get_transaction() as conn:
            query = "DELETE FROM content_segments WHERE id = $1"
            result = await conn.execute(query, segment_id)
            return result == "DELETE 1"

    # =============================================================================
    # 世界观数据操作
    # =============================================================================

    async def create_domain(self, domain_data: DomainCreate) -> Domain:
        """创建域"""
        async with self.postgres.get_transaction() as conn:
            query = """
                INSERT INTO domains (
                    novel_id, name, domain_type, description, characteristics,
                    rules, power_level, location_info, climate_info, resources, dangers
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                RETURNING *
            """
            row = await conn.fetchrow(
                query,
                domain_data.novel_id,
                domain_data.name,
                domain_data.domain_type.value,
                domain_data.description,
                domain_data.characteristics,
                domain_data.rules,
                domain_data.power_level,
                domain_data.location_info,
                domain_data.climate_info,
                domain_data.resources,
                domain_data.dangers
            )
            return Domain(**dict(row))

    async def get_domains_by_novel(self, novel_id: UUID) -> List[Domain]:
        """获取小说的域列表"""
        async with self.postgres.get_connection() as conn:
            query = "SELECT * FROM domains WHERE novel_id = $1 ORDER BY power_level"
            rows = await conn.fetch(query, novel_id)
            return [Domain(**dict(row)) for row in rows]

    async def create_law_chain(self, law_chain_data: LawChainCreate) -> LawChain:
        """创建法则链"""
        async with self.postgres.get_transaction() as conn:
            query = """
                INSERT INTO law_chains (
                    novel_id, name, chain_type, description, origin_story,
                    power_level, activation_conditions, effects, limitations,
                    corruption_risk, rarity
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                RETURNING *
            """
            row = await conn.fetchrow(
                query,
                law_chain_data.novel_id,
                law_chain_data.name,
                law_chain_data.chain_type,
                law_chain_data.description,
                law_chain_data.origin_story,
                law_chain_data.power_level,
                law_chain_data.activation_conditions,
                law_chain_data.effects,
                law_chain_data.limitations,
                law_chain_data.corruption_risk,
                law_chain_data.rarity.value
            )
            return LawChain(**dict(row))

    async def get_law_chains_by_novel(self, novel_id: UUID) -> List[LawChain]:
        """获取小说的法则链列表"""
        async with self.postgres.get_connection() as conn:
            query = "SELECT * FROM law_chains WHERE novel_id = $1 ORDER BY power_level DESC"
            rows = await conn.fetch(query, novel_id)
            return [LawChain(**dict(row)) for row in rows]

    # =============================================================================
    # 搜索和统计操作
    # =============================================================================

    async def search_content_segments(self, novel_id: UUID, query: str) -> List[ContentSegment]:
        """搜索内容段落"""
        async with self.postgres.get_connection() as conn:
            search_query = """
                SELECT cs.* FROM content_segments cs
                JOIN content_batches cb ON cs.batch_id = cb.id
                WHERE cb.novel_id = $1
                AND (
                    to_tsvector('simple', cs.content) @@ plainto_tsquery('simple', $2)
                    OR to_tsvector('simple', COALESCE(cs.title, '')) @@ plainto_tsquery('simple', $2)
                )
                ORDER BY cs.sequence_order
                LIMIT 50
            """
            rows = await conn.fetch(search_query, novel_id, query)
            return [ContentSegment(**_deserialize_json_fields(dict(row), "metadata")) for row in rows]

    async def get_batch_statistics(self, novel_id: UUID) -> Dict[str, Any]:
        """获取批次统计信息"""
        async with self.postgres.get_connection() as conn:
            stats_query = """
                SELECT
                    COUNT(*) as total_batches,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_batches,
                    COALESCE(SUM(word_count), 0) as total_words,
                    (
                        SELECT COUNT(*)
                        FROM content_segments cs
                        JOIN content_batches cb ON cs.batch_id = cb.id
                        WHERE cb.novel_id = $1
                    ) as total_segments
                FROM content_batches
                WHERE novel_id = $1
            """
            row = await conn.fetchrow(stats_query, novel_id)
            return dict(row) if row else {}