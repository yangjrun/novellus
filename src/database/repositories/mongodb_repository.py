"""
MongoDB数据仓库 - 处理文档型数据库操作
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import TEXT, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError

from ..connection_manager import MongoDBManager, DatabaseError
from ..models.character_models import Character, Location
from ..models.content_models import (
    Item, Event, KnowledgeBase,
    CharacterCreate, LocationCreate, ItemCreate, EventCreate, KnowledgeBaseCreate
)

logger = logging.getLogger(__name__)


class MongoDBRepository:
    """MongoDB数据仓库"""

    def __init__(self, mongodb_manager: MongoDBManager):
        self.mongodb = mongodb_manager

    @property
    def db(self) -> AsyncIOMotorDatabase:
        """获取数据库实例"""
        return self.mongodb.database

    # =============================================================================
    # 角色操作
    # =============================================================================

    async def create_character(self, character_data: CharacterCreate) -> Character:
        """创建角色"""
        try:
            # 检查角色名称是否已存在
            existing = await self.db.characters.find_one({
                "novel_id": character_data.novel_id,
                "name": character_data.name
            })
            if existing:
                raise DatabaseError(f"角色名称 '{character_data.name}' 已存在")

            # 构建角色文档
            character_doc = {
                "novel_id": character_data.novel_id,
                "name": character_data.name,
                "character_type": character_data.character_type,
                "basic_info": character_data.basic_info or {},
                "cultivation_info": character_data.cultivation_info or {},
                "personality": character_data.personality or {},
                "appearance": character_data.appearance or {},
                "background": character_data.background or {},
                "relationships": [],
                "story_role": character_data.story_role or {},
                "dialogue_style": character_data.dialogue_style or {},
                "status": "active",
                "tags": character_data.tags,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }

            # 插入文档
            result = await self.db.characters.insert_one(character_doc)
            character_doc["id"] = str(result.inserted_id)
            character_doc.pop("_id", None)

            return Character(**character_doc)

        except DuplicateKeyError:
            raise DatabaseError(f"角色名称 '{character_data.name}' 已存在")
        except Exception as e:
            logger.error(f"创建角色失败: {e}")
            raise DatabaseError(f"创建角色失败: {e}")

    async def get_character_by_id(self, character_id: str) -> Optional[Character]:
        """根据ID获取角色"""
        try:
            doc = await self.db.characters.find_one({"_id": character_id})
            if doc:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
                return Character(**doc)
            return None
        except Exception as e:
            logger.error(f"获取角色失败: {e}")
            raise DatabaseError(f"获取角色失败: {e}")

    async def get_characters_by_novel(
        self,
        novel_id: str,
        character_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Character]:
        """获取小说的角色列表"""
        try:
            filter_query = {"novel_id": novel_id}

            if character_type:
                filter_query["character_type"] = character_type

            if status:
                filter_query["status"] = status

            cursor = self.db.characters.find(filter_query).skip(skip).limit(limit).sort("name", ASCENDING)
            characters = []

            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
                characters.append(Character(**doc))

            return characters

        except Exception as e:
            logger.error(f"获取角色列表失败: {e}")
            raise DatabaseError(f"获取角色列表失败: {e}")

    async def update_character(self, character_id: str, update_data: Dict[str, Any]) -> Optional[Character]:
        """更新角色"""
        try:
            update_data["updated_at"] = datetime.now()

            result = await self.db.characters.find_one_and_update(
                {"_id": character_id},
                {"$set": update_data},
                return_document=True
            )

            if result:
                result["id"] = str(result["_id"])
                result.pop("_id", None)
                return Character(**result)
            return None

        except Exception as e:
            logger.error(f"更新角色失败: {e}")
            raise DatabaseError(f"更新角色失败: {e}")

    async def delete_character(self, character_id: str) -> bool:
        """删除角色"""
        try:
            result = await self.db.characters.delete_one({"_id": character_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"删除角色失败: {e}")
            raise DatabaseError(f"删除角色失败: {e}")

    async def search_characters(self, novel_id: str, query: str) -> List[Character]:
        """搜索角色"""
        try:
            search_query = {
                "novel_id": novel_id,
                "$text": {"$search": query}
            }

            cursor = self.db.characters.find(search_query).limit(20)
            characters = []

            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
                characters.append(Character(**doc))

            return characters

        except Exception as e:
            logger.error(f"搜索角色失败: {e}")
            raise DatabaseError(f"搜索角色失败: {e}")

    async def count_characters(self, novel_id: str) -> int:
        """统计角色数量"""
        try:
            return await self.db.characters.count_documents({"novel_id": novel_id})
        except Exception as e:
            logger.error(f"统计角色数量失败: {e}")
            return 0

    # =============================================================================
    # 地点操作
    # =============================================================================

    async def create_location(self, location_data: LocationCreate) -> Location:
        """创建地点"""
        try:
            # 检查地点名称是否已存在
            existing = await self.db.locations.find_one({
                "novel_id": location_data.novel_id,
                "name": location_data.name
            })
            if existing:
                raise DatabaseError(f"地点名称 '{location_data.name}' 已存在")

            # 构建地点文档
            location_doc = {
                "novel_id": location_data.novel_id,
                "name": location_data.name,
                "location_type": location_data.location_type,
                "domain_affiliation": location_data.domain_affiliation,
                "geographical_info": location_data.geographical_info or {},
                "political_info": location_data.political_info or {},
                "cultivation_aspects": location_data.cultivation_aspects or {},
                "physical_description": location_data.physical_description or {},
                "history": location_data.history or {},
                "connected_locations": [],
                "story_significance": location_data.story_significance or {},
                "status": "active",
                "tags": location_data.tags,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }

            # 插入文档
            result = await self.db.locations.insert_one(location_doc)
            location_doc["id"] = str(result.inserted_id)
            location_doc.pop("_id", None)

            return Location(**location_doc)

        except DuplicateKeyError:
            raise DatabaseError(f"地点名称 '{location_data.name}' 已存在")
        except Exception as e:
            logger.error(f"创建地点失败: {e}")
            raise DatabaseError(f"创建地点失败: {e}")

    async def get_locations_by_novel(
        self,
        novel_id: str,
        location_type: Optional[str] = None,
        domain_affiliation: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Location]:
        """获取小说的地点列表"""
        try:
            filter_query = {"novel_id": novel_id}

            if location_type:
                filter_query["location_type"] = location_type

            if domain_affiliation:
                filter_query["domain_affiliation"] = domain_affiliation

            cursor = self.db.locations.find(filter_query).skip(skip).limit(limit).sort("name", ASCENDING)
            locations = []

            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
                locations.append(Location(**doc))

            return locations

        except Exception as e:
            logger.error(f"获取地点列表失败: {e}")
            raise DatabaseError(f"获取地点列表失败: {e}")

    async def search_locations(self, novel_id: str, query: str) -> List[Location]:
        """搜索地点"""
        try:
            search_query = {
                "novel_id": novel_id,
                "$text": {"$search": query}
            }

            cursor = self.db.locations.find(search_query).limit(20)
            locations = []

            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
                locations.append(Location(**doc))

            return locations

        except Exception as e:
            logger.error(f"搜索地点失败: {e}")
            raise DatabaseError(f"搜索地点失败: {e}")

    async def count_locations(self, novel_id: str) -> int:
        """统计地点数量"""
        try:
            return await self.db.locations.count_documents({"novel_id": novel_id})
        except Exception as e:
            logger.error(f"统计地点数量失败: {e}")
            return 0

    # =============================================================================
    # 物品操作
    # =============================================================================

    async def create_item(self, item_data: ItemCreate) -> Item:
        """创建物品"""
        try:
            # 构建物品文档
            item_doc = {
                "novel_id": item_data.novel_id,
                "name": item_data.name,
                "item_type": item_data.item_type,
                "rarity": item_data.rarity,
                "basic_info": item_data.basic_info or {},
                "physical_properties": item_data.physical_properties or {},
                "abilities": item_data.abilities or {},
                "law_chain_connections": [],
                "requirements": item_data.requirements or {},
                "history": item_data.history or {},
                "current_status": item_data.current_status or {},
                "story_role": item_data.story_role or {},
                "tags": item_data.tags,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }

            # 插入文档
            result = await self.db.items.insert_one(item_doc)
            item_doc["id"] = str(result.inserted_id)
            item_doc.pop("_id", None)

            return Item(**item_doc)

        except Exception as e:
            logger.error(f"创建物品失败: {e}")
            raise DatabaseError(f"创建物品失败: {e}")

    async def get_items_by_novel(
        self,
        novel_id: str,
        item_type: Optional[str] = None,
        rarity: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Item]:
        """获取小说的物品列表"""
        try:
            filter_query = {"novel_id": novel_id}

            if item_type:
                filter_query["item_type"] = item_type

            if rarity:
                filter_query["rarity"] = rarity

            cursor = self.db.items.find(filter_query).skip(skip).limit(limit).sort("name", ASCENDING)
            items = []

            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
                items.append(Item(**doc))

            return items

        except Exception as e:
            logger.error(f"获取物品列表失败: {e}")
            raise DatabaseError(f"获取物品列表失败: {e}")

    # =============================================================================
    # 事件操作
    # =============================================================================

    async def create_event(self, event_data: EventCreate) -> Event:
        """创建事件"""
        try:
            # 构建事件文档
            event_doc = {
                "novel_id": event_data.novel_id,
                "name": event_data.name,
                "event_type": event_data.event_type,
                "timeline_info": event_data.timeline_info or {},
                "participants": event_data.participants,
                "location_info": event_data.location_info or {},
                "description": event_data.description or {},
                "consequences": event_data.consequences or {},
                "plot_connections": event_data.plot_connections or {},
                "themes": event_data.themes,
                "status": "planned",
                "tags": event_data.tags,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }

            # 插入文档
            result = await self.db.events.insert_one(event_doc)
            event_doc["id"] = str(result.inserted_id)
            event_doc.pop("_id", None)

            return Event(**event_doc)

        except Exception as e:
            logger.error(f"创建事件失败: {e}")
            raise DatabaseError(f"创建事件失败: {e}")

    async def get_events_by_novel(
        self,
        novel_id: str,
        event_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Event]:
        """获取小说的事件列表"""
        try:
            filter_query = {"novel_id": novel_id}

            if event_type:
                filter_query["event_type"] = event_type

            if status:
                filter_query["status"] = status

            cursor = self.db.events.find(filter_query).skip(skip).limit(limit).sort("timeline_info.chronological_order", ASCENDING)
            events = []

            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
                events.append(Event(**doc))

            return events

        except Exception as e:
            logger.error(f"获取事件列表失败: {e}")
            raise DatabaseError(f"获取事件列表失败: {e}")

    # =============================================================================
    # 知识库操作
    # =============================================================================

    async def create_knowledge_base(self, kb_data: KnowledgeBaseCreate) -> KnowledgeBase:
        """创建知识库条目"""
        try:
            # 检查标题是否已存在
            existing = await self.db.knowledge_base.find_one({
                "novel_id": kb_data.novel_id,
                "title": kb_data.title
            })
            if existing:
                raise DatabaseError(f"知识库标题 '{kb_data.title}' 已存在")

            # 构建知识库文档
            kb_doc = {
                "novel_id": kb_data.novel_id,
                "title": kb_data.title,
                "category": kb_data.category,
                "content": kb_data.content or {},
                "related_entities": kb_data.related_entities,
                "sources": kb_data.sources,
                "reliability": kb_data.reliability,
                "tags": kb_data.tags,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }

            # 插入文档
            result = await self.db.knowledge_base.insert_one(kb_doc)
            kb_doc["id"] = str(result.inserted_id)
            kb_doc.pop("_id", None)

            return KnowledgeBase(**kb_doc)

        except DuplicateKeyError:
            raise DatabaseError(f"知识库标题 '{kb_data.title}' 已存在")
        except Exception as e:
            logger.error(f"创建知识库条目失败: {e}")
            raise DatabaseError(f"创建知识库条目失败: {e}")

    async def get_knowledge_base_by_novel(
        self,
        novel_id: str,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[KnowledgeBase]:
        """获取小说的知识库列表"""
        try:
            filter_query = {"novel_id": novel_id}

            if category:
                filter_query["category"] = category

            cursor = self.db.knowledge_base.find(filter_query).skip(skip).limit(limit).sort("title", ASCENDING)
            knowledge_items = []

            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
                knowledge_items.append(KnowledgeBase(**doc))

            return knowledge_items

        except Exception as e:
            logger.error(f"获取知识库列表失败: {e}")
            raise DatabaseError(f"获取知识库列表失败: {e}")

    async def search_knowledge_base(self, novel_id: str, query: str) -> List[KnowledgeBase]:
        """搜索知识库"""
        try:
            search_query = {
                "novel_id": novel_id,
                "$text": {"$search": query}
            }

            cursor = self.db.knowledge_base.find(search_query).limit(20)
            knowledge_items = []

            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
                knowledge_items.append(KnowledgeBase(**doc))

            return knowledge_items

        except Exception as e:
            logger.error(f"搜索知识库失败: {e}")
            raise DatabaseError(f"搜索知识库失败: {e}")

    # =============================================================================
    # 数据库维护操作
    # =============================================================================

    async def ensure_indexes(self) -> None:
        """确保索引存在"""
        try:
            # 角色集合索引
            await self.db.characters.create_index([("novel_id", ASCENDING), ("name", ASCENDING)], unique=True)
            await self.db.characters.create_index([("novel_id", ASCENDING), ("character_type", ASCENDING)])
            await self.db.characters.create_index([("name", TEXT), ("basic_info.full_name", TEXT)])

            # 地点集合索引
            await self.db.locations.create_index([("novel_id", ASCENDING), ("name", ASCENDING)], unique=True)
            await self.db.locations.create_index([("novel_id", ASCENDING), ("location_type", ASCENDING)])
            await self.db.locations.create_index([("name", TEXT), ("physical_description.atmosphere", TEXT)])

            # 物品集合索引
            await self.db.items.create_index([("novel_id", ASCENDING), ("name", ASCENDING)], unique=True)
            await self.db.items.create_index([("novel_id", ASCENDING), ("item_type", ASCENDING)])
            await self.db.items.create_index([("name", TEXT), ("physical_properties.appearance", TEXT)])

            # 事件集合索引
            await self.db.events.create_index([("novel_id", ASCENDING), ("name", ASCENDING)])
            await self.db.events.create_index([("novel_id", ASCENDING), ("event_type", ASCENDING)])
            await self.db.events.create_index([("name", TEXT), ("description.summary", TEXT)])

            # 知识库集合索引
            await self.db.knowledge_base.create_index([("novel_id", ASCENDING), ("title", ASCENDING)], unique=True)
            await self.db.knowledge_base.create_index([("novel_id", ASCENDING), ("category", ASCENDING)])
            await self.db.knowledge_base.create_index([("title", TEXT), ("content.summary", TEXT)])

            logger.info("MongoDB索引创建完成")

        except Exception as e:
            logger.error(f"创建MongoDB索引失败: {e}")
            raise DatabaseError(f"创建MongoDB索引失败: {e}")