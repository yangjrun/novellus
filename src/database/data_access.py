"""
数据访问层 - 统一的数据库操作接口
支持PostgreSQL和MongoDB的混合架构操作
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from datetime import datetime

from .connection_manager import (
    DatabaseManager,
    get_database_manager,
    close_database_manager,
    DatabaseError
)
from .models import *
from .repositories.postgresql_repository import PostgreSQLRepository
from .repositories.mongodb_repository import MongoDBRepository

logger = logging.getLogger(__name__)


class NovelDataManager:
    """小说数据管理器 - 针对特定小说的数据操作"""

    def __init__(self, novel_id: Union[str, UUID], db_manager: DatabaseManager):
        self.novel_id = str(novel_id)
        self.db_manager = db_manager
        self.pg_repo = PostgreSQLRepository(db_manager.postgres)
        self.mongo_repo = MongoDBRepository(db_manager.mongodb)

    # =============================================================================
    # 批次管理操作
    # =============================================================================

    async def create_content_batch(self, batch_data: ContentBatchCreate) -> ContentBatch:
        """创建内容批次"""
        try:
            # 验证小说ID
            novel = await self.pg_repo.get_novel_by_id(UUID(batch_data.novel_id))
            if not novel:
                raise DatabaseError(f"小说不存在: {batch_data.novel_id}")

            # 检查批次编号是否已存在
            existing_batch = await self.pg_repo.get_content_batch_by_number(
                UUID(batch_data.novel_id), batch_data.batch_number
            )
            if existing_batch:
                raise DatabaseError(f"批次编号 {batch_data.batch_number} 已存在")

            # 创建批次
            batch = await self.pg_repo.create_content_batch(batch_data)
            logger.info(f"创建内容批次: {batch.batch_name} (ID: {batch.id})")
            return batch

        except Exception as e:
            logger.error(f"创建内容批次失败: {e}")
            raise DatabaseError(f"创建内容批次失败: {e}")

    async def get_content_batches(
        self,
        batch_type: Optional[BatchType] = None,
        status: Optional[BatchStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ContentBatch]:
        """获取内容批次列表"""
        try:
            return await self.pg_repo.get_content_batches_by_novel(
                UUID(self.novel_id), batch_type, status, skip, limit
            )
        except Exception as e:
            logger.error(f"获取内容批次失败: {e}")
            raise DatabaseError(f"获取内容批次失败: {e}")

    async def update_content_batch(
        self,
        batch_id: Union[str, UUID],
        update_data: ContentBatchUpdate
    ) -> Optional[ContentBatch]:
        """更新内容批次"""
        try:
            batch = await self.pg_repo.update_content_batch(UUID(batch_id), update_data)
            if batch:
                logger.info(f"更新内容批次: {batch.batch_name} (ID: {batch.id})")
            return batch
        except Exception as e:
            logger.error(f"更新内容批次失败: {e}")
            raise DatabaseError(f"更新内容批次失败: {e}")

    async def delete_content_batch(self, batch_id: Union[str, UUID]) -> bool:
        """删除内容批次"""
        try:
            # 检查批次是否有关联的内容段落
            segments = await self.pg_repo.get_content_segments_by_batch(UUID(batch_id))
            if segments:
                raise DatabaseError("无法删除包含内容段落的批次，请先删除相关段落")

            success = await self.pg_repo.delete_content_batch(UUID(batch_id))
            if success:
                logger.info(f"删除内容批次: {batch_id}")
            return success
        except Exception as e:
            logger.error(f"删除内容批次失败: {e}")
            raise DatabaseError(f"删除内容批次失败: {e}")

    # =============================================================================
    # 内容段落操作
    # =============================================================================

    async def create_content_segment(self, segment_data: ContentSegmentCreate) -> ContentSegment:
        """创建内容段落"""
        try:
            # 验证批次ID
            batch = await self.pg_repo.get_content_batch_by_id(segment_data.batch_id)
            if not batch:
                raise DatabaseError(f"批次不存在: {segment_data.batch_id}")

            # 检查序列顺序是否已存在
            existing_segment = await self.pg_repo.get_content_segment_by_sequence(
                segment_data.batch_id, segment_data.sequence_order
            )
            if existing_segment:
                raise DatabaseError(f"序列顺序 {segment_data.sequence_order} 已存在")

            # 创建段落
            segment = await self.pg_repo.create_content_segment(segment_data)
            logger.info(f"创建内容段落: {segment.title or '无标题'} (ID: {segment.id})")
            return segment

        except Exception as e:
            logger.error(f"创建内容段落失败: {e}")
            raise DatabaseError(f"创建内容段落失败: {e}")

    async def get_content_segments(
        self,
        batch_id: Union[str, UUID],
        segment_type: Optional[SegmentType] = None,
        status: Optional[SegmentStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ContentSegment]:
        """获取内容段落列表"""
        try:
            return await self.pg_repo.get_content_segments_by_batch(
                UUID(batch_id), segment_type, status, skip, limit
            )
        except Exception as e:
            logger.error(f"获取内容段落失败: {e}")
            raise DatabaseError(f"获取内容段落失败: {e}")

    async def update_content_segment(
        self,
        segment_id: Union[str, UUID],
        update_data: ContentSegmentUpdate
    ) -> Optional[ContentSegment]:
        """更新内容段落"""
        try:
            segment = await self.pg_repo.update_content_segment(UUID(segment_id), update_data)
            if segment:
                logger.info(f"更新内容段落: {segment.title or '无标题'} (ID: {segment.id})")
            return segment
        except Exception as e:
            logger.error(f"更新内容段落失败: {e}")
            raise DatabaseError(f"更新内容段落失败: {e}")

    async def delete_content_segment(self, segment_id: Union[str, UUID]) -> bool:
        """删除内容段落"""
        try:
            success = await self.pg_repo.delete_content_segment(UUID(segment_id))
            if success:
                logger.info(f"删除内容段落: {segment_id}")
            return success
        except Exception as e:
            logger.error(f"删除内容段落失败: {e}")
            raise DatabaseError(f"删除内容段落失败: {e}")

    # =============================================================================
    # 世界观数据操作
    # =============================================================================

    async def create_domain(self, domain_data: DomainCreate) -> Domain:
        """创建域"""
        try:
            domain = await self.pg_repo.create_domain(domain_data)
            logger.info(f"创建域: {domain.name} (ID: {domain.id})")
            return domain
        except Exception as e:
            logger.error(f"创建域失败: {e}")
            raise DatabaseError(f"创建域失败: {e}")

    async def get_domains(self) -> List[Domain]:
        """获取域列表"""
        try:
            return await self.pg_repo.get_domains_by_novel(UUID(self.novel_id))
        except Exception as e:
            logger.error(f"获取域列表失败: {e}")
            raise DatabaseError(f"获取域列表失败: {e}")

    async def create_law_chain(self, law_chain_data: LawChainCreate) -> LawChain:
        """创建法则链"""
        try:
            law_chain = await self.pg_repo.create_law_chain(law_chain_data)
            logger.info(f"创建法则链: {law_chain.name} (ID: {law_chain.id})")
            return law_chain
        except Exception as e:
            logger.error(f"创建法则链失败: {e}")
            raise DatabaseError(f"创建法则链失败: {e}")

    async def get_law_chains(self) -> List[LawChain]:
        """获取法则链列表"""
        try:
            return await self.pg_repo.get_law_chains_by_novel(UUID(self.novel_id))
        except Exception as e:
            logger.error(f"获取法则链列表失败: {e}")
            raise DatabaseError(f"获取法则链列表失败: {e}")

    # =============================================================================
    # MongoDB数据操作
    # =============================================================================

    async def create_character(self, character_data: CharacterCreate) -> Character:
        """创建角色"""
        try:
            character = await self.mongo_repo.create_character(character_data)
            logger.info(f"创建角色: {character.name} (ID: {character.id})")
            return character
        except Exception as e:
            logger.error(f"创建角色失败: {e}")
            raise DatabaseError(f"创建角色失败: {e}")

    async def get_characters(
        self,
        character_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Character]:
        """获取角色列表"""
        try:
            return await self.mongo_repo.get_characters_by_novel(
                self.novel_id, character_type, status, skip, limit
            )
        except Exception as e:
            logger.error(f"获取角色列表失败: {e}")
            raise DatabaseError(f"获取角色列表失败: {e}")

    async def create_location(self, location_data: LocationCreate) -> Location:
        """创建地点"""
        try:
            location = await self.mongo_repo.create_location(location_data)
            logger.info(f"创建地点: {location.name} (ID: {location.id})")
            return location
        except Exception as e:
            logger.error(f"创建地点失败: {e}")
            raise DatabaseError(f"创建地点失败: {e}")

    async def get_locations(
        self,
        location_type: Optional[str] = None,
        domain_affiliation: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Location]:
        """获取地点列表"""
        try:
            return await self.mongo_repo.get_locations_by_novel(
                self.novel_id, location_type, domain_affiliation, skip, limit
            )
        except Exception as e:
            logger.error(f"获取地点列表失败: {e}")
            raise DatabaseError(f"获取地点列表失败: {e}")

    # =============================================================================
    # 搜索和统计操作
    # =============================================================================

    async def search_content(
        self,
        query: str,
        content_types: Optional[List[str]] = None
    ) -> Dict[str, List[Any]]:
        """全文搜索内容"""
        try:
            results = {
                "segments": [],
                "characters": [],
                "locations": [],
                "knowledge": []
            }

            # 搜索PostgreSQL中的内容段落
            if not content_types or "segments" in content_types:
                results["segments"] = await self.pg_repo.search_content_segments(
                    UUID(self.novel_id), query
                )

            # 搜索MongoDB中的各类内容
            if not content_types or "characters" in content_types:
                results["characters"] = await self.mongo_repo.search_characters(
                    self.novel_id, query
                )

            if not content_types or "locations" in content_types:
                results["locations"] = await self.mongo_repo.search_locations(
                    self.novel_id, query
                )

            if not content_types or "knowledge" in content_types:
                results["knowledge"] = await self.mongo_repo.search_knowledge_base(
                    self.novel_id, query
                )

            return results

        except Exception as e:
            logger.error(f"搜索内容失败: {e}")
            raise DatabaseError(f"搜索内容失败: {e}")

    async def get_novel_statistics(self) -> Dict[str, Any]:
        """获取小说统计信息"""
        try:
            novel = await self.pg_repo.get_novel_by_id(UUID(self.novel_id))
            if not novel:
                raise DatabaseError(f"小说不存在: {self.novel_id}")

            # PostgreSQL统计
            batch_stats = await self.pg_repo.get_batch_statistics(UUID(self.novel_id))

            # MongoDB统计
            character_count = await self.mongo_repo.count_characters(self.novel_id)
            location_count = await self.mongo_repo.count_locations(self.novel_id)

            return {
                "novel_info": {
                    "id": str(novel.id),
                    "name": novel.name,
                    "title": novel.title,
                    "status": novel.status,
                    "total_word_count": novel.word_count,
                    "chapter_count": novel.chapter_count
                },
                "content_statistics": {
                    "total_batches": batch_stats.get("total_batches", 0),
                    "completed_batches": batch_stats.get("completed_batches", 0),
                    "total_segments": batch_stats.get("total_segments", 0),
                    "total_words": batch_stats.get("total_words", 0)
                },
                "world_statistics": {
                    "character_count": character_count,
                    "location_count": location_count
                },
                "last_updated": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"获取小说统计失败: {e}")
            raise DatabaseError(f"获取小说统计失败: {e}")


class GlobalDataManager:
    """全局数据管理器 - 跨项目的数据操作"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.pg_repo = PostgreSQLRepository(db_manager.postgres)
        self.mongo_repo = MongoDBRepository(db_manager.mongodb)

    # =============================================================================
    # 项目管理操作
    # =============================================================================

    async def create_project(self, project_data: ProjectCreate) -> Project:
        """创建项目"""
        try:
            # 检查项目名称是否已存在
            existing_project = await self.pg_repo.get_project_by_name(project_data.name)
            if existing_project:
                raise DatabaseError(f"项目名称 '{project_data.name}' 已存在")

            project = await self.pg_repo.create_project(project_data)
            logger.info(f"创建项目: {project.name} (ID: {project.id})")
            return project

        except Exception as e:
            logger.error(f"创建项目失败: {e}")
            raise DatabaseError(f"创建项目失败: {e}")

    async def get_projects(
        self,
        status: Optional[ProjectStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Project]:
        """获取项目列表"""
        try:
            return await self.pg_repo.get_projects(status, skip, limit)
        except Exception as e:
            logger.error(f"获取项目列表失败: {e}")
            raise DatabaseError(f"获取项目列表失败: {e}")

    async def create_novel(self, novel_data: NovelCreate) -> Novel:
        """创建小说"""
        try:
            # 验证项目ID
            project = await self.pg_repo.get_project_by_id(novel_data.project_id)
            if not project:
                raise DatabaseError(f"项目不存在: {novel_data.project_id}")

            # 检查小说名称在项目内是否已存在
            existing_novel = await self.pg_repo.get_novel_by_name(
                novel_data.project_id, novel_data.name
            )
            if existing_novel:
                raise DatabaseError(f"小说名称 '{novel_data.name}' 在项目内已存在")

            novel = await self.pg_repo.create_novel(novel_data)
            logger.info(f"创建小说: {novel.name} (ID: {novel.id})")
            return novel

        except Exception as e:
            logger.error(f"创建小说失败: {e}")
            raise DatabaseError(f"创建小说失败: {e}")

    async def get_novels_by_project(
        self,
        project_id: Union[str, UUID],
        status: Optional[NovelStatus] = None
    ) -> List[Novel]:
        """获取项目下的小说列表"""
        try:
            return await self.pg_repo.get_novels_by_project(project_id, status)
        except Exception as e:
            logger.error(f"获取小说列表失败: {e}")
            raise DatabaseError(f"获取小说列表失败: {e}")

    def get_novel_manager(self, novel_id: Union[str, UUID]) -> NovelDataManager:
        """获取小说数据管理器"""
        return NovelDataManager(novel_id, self.db_manager)


# 全局数据库管理器实例
_global_manager: Optional[GlobalDataManager] = None
_database_manager: Optional[DatabaseManager] = None


async def init_database() -> None:
    """初始化数据库连接"""
    global _database_manager, _global_manager

    try:
        if _database_manager is None:
            _database_manager = await get_database_manager()
            _global_manager = GlobalDataManager(_database_manager)
            logger.info("数据库初始化完成")
        else:
            logger.info("数据库已经初始化")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise DatabaseError(f"数据库初始化失败: {e}")


async def close_database() -> None:
    """关闭数据库连接"""
    global _database_manager, _global_manager

    try:
        if _database_manager:
            await close_database_manager()
            _database_manager = None
            _global_manager = None
            logger.info("数据库连接已关闭")
    except Exception as e:
        logger.error(f"关闭数据库失败: {e}")


def get_global_manager() -> GlobalDataManager:
    """获取全局数据管理器"""
    if _global_manager is None:
        raise DatabaseError("数据库未初始化，请先调用 init_database()")
    return _global_manager


def get_novel_manager(novel_id: Union[str, UUID]) -> NovelDataManager:
    """获取小说数据管理器"""
    global_manager = get_global_manager()
    return global_manager.get_novel_manager(novel_id)


async def get_database_health() -> Dict[str, Any]:
    """获取数据库健康状态"""
    if _database_manager:
        return await _database_manager.health_check()
    else:
        return {
            "postgresql": {"connected": False, "error": "数据库未初始化"},
            "mongodb": {"connected": False, "error": "数据库未初始化"}
        }