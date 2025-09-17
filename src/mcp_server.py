#!/usr/bin/env python3
"""
网络小说世界观管理 MCP 服务器
支持多小说的通用数据管理系统
"""

import signal
import sys
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
import json
import logging
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from config import config
from database.data_access import (
    init_database, close_database, get_global_manager, get_novel_manager,
    DatabaseError
)
from database.models import *

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the MCP server instance
mcp = FastMCP(config.server_name)


# =============================================================================
# 基础测试工具
# =============================================================================

@mcp.tool()
def test_mcp_connection() -> str:
    """测试MCP服务器通信和基本功能"""
    try:
        server_info = {
            "server_name": config.server_name,
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "message": "网络小说世界观管理系统运行正常",
            "features": [
                "多小说数据管理",
                "实体关系管理",
                "故事内容管理",
                "世界观配置管理"
            ]
        }
        return json.dumps(server_info, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"MCP测试错误: {str(e)}"


# =============================================================================
# 小说项目管理工具
# =============================================================================

@mcp.tool()
async def create_novel(title: str, code: str, author: str = "", genre: str = "",
                      world_type: str = "", template_code: str = "") -> str:
    """创建新的小说项目"""
    try:
        global_manager = get_global_manager()

        novel = Novel(
            title=title,
            code=code,
            author=author,
            genre=genre,
            world_type=world_type,
            settings={}
        )

        novel_id = await global_manager.create_novel(novel, template_code if template_code else None)

        result = {
            "success": True,
            "novel_id": novel_id,
            "message": f"小说项目 '{title}' 创建成功",
            "code": code
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "创建小说项目失败"
        }
        return json.dumps(error_result, indent=2, ensure_ascii=False)


@mcp.tool()
async def list_novels(status: str = "") -> str:
    """获取小说列表"""
    try:
        global_manager = get_global_manager()
        novels = await global_manager.get_novel_list(status if status else None)

        result = {
            "success": True,
            "count": len(novels),
            "novels": [
                {
                    "id": novel.id,
                    "title": novel.title,
                    "code": novel.code,
                    "author": novel.author,
                    "genre": novel.genre,
                    "world_type": novel.world_type,
                    "status": novel.status,
                    "entity_count": novel.entity_count,
                    "created_at": novel.created_at.isoformat() if novel.created_at else None
                }
                for novel in novels
            ]
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "获取小说列表失败"
        }
        return json.dumps(error_result, indent=2, ensure_ascii=False)


@mcp.tool()
async def get_novel_summary(novel_id: int) -> str:
    """获取小说摘要信息"""
    try:
        novel_manager = get_novel_manager(novel_id)
        summary = await novel_manager.get_novel_summary()

        result = {
            "success": True,
            "novel": {
                "id": summary.novel.id,
                "title": summary.novel.title,
                "code": summary.novel.code,
                "author": summary.novel.author,
                "genre": summary.novel.genre,
                "world_type": summary.novel.world_type,
                "status": summary.novel.status,
                "settings": summary.novel.settings
            },
            "entity_types": [
                {
                    "id": et.id,
                    "name": et.name,
                    "display_name": et.display_name,
                    "count": summary.entity_counts.get(et.name, 0)
                }
                for et in summary.entity_types
            ],
            "recent_events": [
                {
                    "id": event.id,
                    "name": event.name,
                    "event_type": event.event_type,
                    "impact_level": event.impact_level,
                    "created_at": event.created_at.isoformat() if event.created_at else None
                }
                for event in summary.recent_events
            ]
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": f"获取小说 {novel_id} 摘要失败"
        }
        return json.dumps(error_result, indent=2, ensure_ascii=False)


# =============================================================================
# 实体管理工具
# =============================================================================

@mcp.tool()
async def create_entity(novel_id: int, entity_type_name: str, name: str,
                       code: str = "", attributes: str = "{}",
                       tags: str = "[]", priority: int = 0, profile: str = "{}") -> str:
    """创建实体（角色、地点、势力等）"""
    try:
        novel_manager = get_novel_manager(novel_id)

        # 解析JSON参数
        try:
            attributes_dict = json.loads(attributes) if attributes else {}
            tags_list = json.loads(tags) if tags else []
            profile_dict = json.loads(profile) if profile else {}
        except json.JSONDecodeError as e:
            return json.dumps({
                "success": False,
                "error": f"JSON参数解析错误: {str(e)}",
                "message": "请确保attributes、tags和profile参数是有效的JSON格式"
            }, indent=2, ensure_ascii=False)

        request = CreateEntityRequest(
            novel_id=novel_id,
            entity_type_name=entity_type_name,
            name=name,
            code=code if code else None,
            attributes=attributes_dict,
            tags=tags_list,
            priority=priority,
            profile=profile_dict if profile_dict else None
        )

        entity_id = await novel_manager.create_entity(request)

        result = {
            "success": True,
            "entity_id": entity_id,
            "message": f"实体 '{name}' 创建成功",
            "entity_type": entity_type_name
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": f"创建实体失败"
        }
        return json.dumps(error_result, indent=2, ensure_ascii=False)


@mcp.tool()
async def get_entity(novel_id: int, entity_id: int, include_profile: bool = True) -> str:
    """获取实体详细信息"""
    try:
        novel_manager = get_novel_manager(novel_id)
        entity = await novel_manager.get_entity(entity_id, include_profile)

        if not entity:
            return json.dumps({
                "success": False,
                "error": "实体不存在",
                "message": f"实体 {entity_id} 在小说 {novel_id} 中不存在"
            }, indent=2, ensure_ascii=False)

        result = {
            "success": True,
            "entity": {
                "id": entity.id,
                "name": entity.name,
                "code": entity.code,
                "entity_type": entity.entity_type_name,
                "status": entity.status,
                "attributes": entity.attributes,
                "tags": entity.tags,
                "priority": entity.priority,
                "version": entity.version,
                "created_at": entity.created_at.isoformat() if entity.created_at else None,
                "updated_at": entity.updated_at.isoformat() if entity.updated_at else None
            }
        }

        if include_profile and entity.profile:
            result["entity"]["profile"] = entity.profile

        if entity.categories:
            result["entity"]["categories"] = [
                {
                    "id": cat.id,
                    "name": cat.name,
                    "type": cat.type,
                    "level": cat.level
                }
                for cat in entity.categories
            ]

        if entity.relationships:
            result["entity"]["relationships"] = [
                {
                    "id": rel.id,
                    "type": rel.relationship_type,
                    "source_id": rel.source_entity_id,
                    "target_id": rel.target_entity_id,
                    "strength": rel.strength,
                    "status": rel.status
                }
                for rel in entity.relationships
            ]

        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": f"获取实体 {entity_id} 失败"
        }
        return json.dumps(error_result, indent=2, ensure_ascii=False)


@mcp.tool()
async def search_entities(novel_id: int, filters: str = "{}", sort: str = "",
                         limit: int = 20, offset: int = 0) -> str:
    """搜索实体"""
    try:
        novel_manager = get_novel_manager(novel_id)

        # 解析过滤条件
        try:
            filters_dict = json.loads(filters) if filters else {}
        except json.JSONDecodeError as e:
            return json.dumps({
                "success": False,
                "error": f"过滤条件JSON解析错误: {str(e)}",
                "message": "请确保filters参数是有效的JSON格式"
            }, indent=2, ensure_ascii=False)

        query = QueryRequest(
            novel_id=novel_id,
            filters=filters_dict,
            sort=sort if sort else None,
            limit=min(limit, 100),  # 限制最大返回数量
            offset=offset
        )

        response = await novel_manager.search_entities(query)

        result = {
            "success": True,
            "pagination": {
                "total": response.total,
                "page": response.page,
                "page_size": response.page_size,
                "has_next": response.has_next,
                "has_prev": response.has_prev
            },
            "entities": [
                {
                    "id": entity.id,
                    "name": entity.name,
                    "code": entity.code,
                    "entity_type": entity.entity_type_name,
                    "status": entity.status,
                    "tags": entity.tags,
                    "priority": entity.priority,
                    "created_at": entity.created_at.isoformat() if entity.created_at else None
                }
                for entity in response.items
            ]
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": f"搜索实体失败"
        }
        return json.dumps(error_result, indent=2, ensure_ascii=False)


@mcp.tool()
async def update_entity(novel_id: int, entity_id: int, name: str = "",
                       code: str = "", status: str = "", attributes: str = "",
                       tags: str = "", priority: int = -1, profile: str = "") -> str:
    """更新实体信息"""
    try:
        novel_manager = get_novel_manager(novel_id)

        # 构建更新请求
        update_data = {}

        if name:
            update_data["name"] = name
        if code:
            update_data["code"] = code
        if status:
            try:
                update_data["status"] = EntityStatus(status)
            except ValueError:
                return json.dumps({
                    "success": False,
                    "error": f"无效的状态值: {status}",
                    "message": "状态必须是: active, inactive, deleted"
                }, indent=2, ensure_ascii=False)

        if attributes:
            try:
                update_data["attributes"] = json.loads(attributes)
            except json.JSONDecodeError as e:
                return json.dumps({
                    "success": False,
                    "error": f"属性JSON解析错误: {str(e)}"
                }, indent=2, ensure_ascii=False)

        if tags:
            try:
                update_data["tags"] = json.loads(tags)
            except json.JSONDecodeError as e:
                return json.dumps({
                    "success": False,
                    "error": f"标签JSON解析错误: {str(e)}"
                }, indent=2, ensure_ascii=False)

        if priority >= 0:
            update_data["priority"] = priority

        if profile:
            try:
                update_data["profile"] = json.loads(profile)
            except json.JSONDecodeError as e:
                return json.dumps({
                    "success": False,
                    "error": f"档案JSON解析错误: {str(e)}"
                }, indent=2, ensure_ascii=False)

        request = UpdateEntityRequest(**update_data)
        success = await novel_manager.update_entity(entity_id, request)

        result = {
            "success": success,
            "message": f"实体 {entity_id} 更新成功"
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": f"更新实体 {entity_id} 失败"
        }
        return json.dumps(error_result, indent=2, ensure_ascii=False)


# =============================================================================
# 关系管理工具
# =============================================================================

@mcp.tool()
async def create_relationship(novel_id: int, source_entity_id: int, target_entity_id: int,
                             relationship_type: str, strength: int = 1, attributes: str = "{}") -> str:
    """创建实体间关系"""
    try:
        novel_manager = get_novel_manager(novel_id)

        # 解析属性
        try:
            attributes_dict = json.loads(attributes) if attributes else {}
        except json.JSONDecodeError as e:
            return json.dumps({
                "success": False,
                "error": f"属性JSON解析错误: {str(e)}"
            }, indent=2, ensure_ascii=False)

        relationship_id = await novel_manager.create_relationship(
            source_entity_id, target_entity_id, relationship_type,
            strength=strength, attributes=attributes_dict
        )

        result = {
            "success": True,
            "relationship_id": relationship_id,
            "message": f"关系创建成功: {source_entity_id} -> {target_entity_id} ({relationship_type})"
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "创建关系失败"
        }
        return json.dumps(error_result, indent=2, ensure_ascii=False)


@mcp.tool()
async def get_entity_relationships(novel_id: int, entity_id: int) -> str:
    """获取实体的所有关系"""
    try:
        novel_manager = get_novel_manager(novel_id)
        relationships = await novel_manager.get_entity_relationships(entity_id)

        result = {
            "success": True,
            "entity_id": entity_id,
            "relationships": [
                {
                    "id": rel.id,
                    "type": rel.relationship_type,
                    "source_id": rel.source_entity_id,
                    "target_id": rel.target_entity_id,
                    "strength": rel.strength,
                    "status": rel.status,
                    "attributes": rel.attributes,
                    "created_at": rel.created_at.isoformat() if rel.created_at else None
                }
                for rel in relationships
            ]
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": f"获取实体 {entity_id} 关系失败"
        }
        return json.dumps(error_result, indent=2, ensure_ascii=False)


# =============================================================================
# 事件管理工具
# =============================================================================

@mcp.tool()
async def create_event(novel_id: int, name: str, event_type: str = "",
                      description: str = "", impact_level: int = 1,
                      scope: str = "local", participants: str = "[]") -> str:
    """创建剧情事件"""
    try:
        novel_manager = get_novel_manager(novel_id)

        # 解析参与者列表
        try:
            participants_list = json.loads(participants) if participants else []
        except json.JSONDecodeError as e:
            return json.dumps({
                "success": False,
                "error": f"参与者列表JSON解析错误: {str(e)}"
            }, indent=2, ensure_ascii=False)

        event = Event(
            novel_id=novel_id,
            name=name,
            event_type=event_type if event_type else None,
            description=description if description else None,
            impact_level=impact_level,
            scope=scope,
            attributes={}
        )

        event_id = await novel_manager.create_event(event, participants_list)

        result = {
            "success": True,
            "event_id": event_id,
            "message": f"事件 '{name}' 创建成功"
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "创建事件失败"
        }
        return json.dumps(error_result, indent=2, ensure_ascii=False)


@mcp.tool()
async def get_story_timeline(novel_id: int, limit: int = 20) -> str:
    """获取故事时间线"""
    try:
        novel_manager = get_novel_manager(novel_id)
        events = await novel_manager.get_story_timeline(min(limit, 100))

        result = {
            "success": True,
            "novel_id": novel_id,
            "events": [
                {
                    "id": event.id,
                    "name": event.name,
                    "event_type": event.event_type,
                    "sequence_order": event.sequence_order,
                    "impact_level": event.impact_level,
                    "scope": event.scope,
                    "description": event.description,
                    "status": event.status,
                    "occurred_at": event.occurred_at.isoformat() if event.occurred_at else None,
                    "created_at": event.created_at.isoformat() if event.created_at else None
                }
                for event in events
            ]
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": f"获取故事时间线失败"
        }
        return json.dumps(error_result, indent=2, ensure_ascii=False)




def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    asyncio.create_task(close_database())
    sys.exit(0)


def main():
    """Main entry point for the MCP server."""
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Initialize database connection
    try:
        asyncio.run(init_database())
        print("Database connection initialized")
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")
        print("Database functionality may not work properly")

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
