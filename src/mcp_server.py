#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
from .config import config
from database.data_access import (
    init_database,
    close_database,
    get_global_manager,
    get_novel_manager,
    get_database_health,
    DatabaseError,
)
from database.models import *
from database.batch_manager import get_batch_manager
from database.database_init import initialize_database, reset_database
from database.conflict_data_importer import ConflictDataImporter, ImportConfig

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
                "世界观配置管理",
            ],
        }
        return json.dumps(server_info, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"MCP测试错误: {str(e)}"


# =============================================================================
# 数据库管理工具
# =============================================================================


@mcp.tool()
async def initialize_database_tool() -> str:
    """初始化数据库结构和基础数据"""
    try:
        result = await initialize_database()

        if result["overall_success"]:
            return json.dumps({
                "success": True,
                "message": "数据库初始化成功",
                "details": {
                    "postgresql": result["postgresql"]["message"],
                    "mongodb": result["mongodb"]["message"]
                }
            }, indent=2, ensure_ascii=False)
        else:
            return json.dumps({
                "success": False,
                "message": "数据库初始化失败",
                "details": {
                    "postgresql": result["postgresql"]["message"],
                    "mongodb": result["mongodb"]["message"]
                }
            }, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"数据库初始化错误: {str(e)}"
        }, indent=2, ensure_ascii=False)


@mcp.tool()
async def get_database_status() -> str:
    """获取数据库连接状态和健康信息"""
    try:
        health_info = await get_database_health()

        return json.dumps({
            "database_health": health_info,
            "timestamp": datetime.now().isoformat()
        }, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "error": f"获取数据库状态失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }, indent=2, ensure_ascii=False)


# =============================================================================
# 项目和小说管理工具
# =============================================================================


@mcp.tool()
async def create_project(
    name: str,
    title: str,
    description: str = "",
    author: str = "",
    genre: str = ""
) -> str:
    """创建新的小说项目"""
    try:
        global_manager = get_global_manager()

        project_data = ProjectCreate(
            name=name,
            title=title,
            description=description or None,
            author=author or None,
            genre=genre or None
        )

        project = await global_manager.create_project(project_data)

        return json.dumps({
            "success": True,
            "message": f"项目 '{title}' 创建成功",
            "project": {
                "id": str(project.id),
                "name": project.name,
                "title": project.title,
                "description": project.description,
                "author": project.author,
                "genre": project.genre,
                "status": project.status,
                "created_at": project.created_at.isoformat()
            }
        }, indent=2, ensure_ascii=False)

    except DatabaseError as e:
        return json.dumps({
            "success": False,
            "message": f"创建项目失败: {str(e)}"
        }, indent=2, ensure_ascii=False)


@mcp.tool()
async def create_novel(
    project_id: str,
    name: str,
    title: str,
    description: str = "",
    volume_number: int = 1
) -> str:
    """在项目中创建新的小说"""
    try:
        global_manager = get_global_manager()

        novel_data = NovelCreate(
            project_id=UUID(project_id),
            name=name,
            title=title,
            description=description or None,
            volume_number=volume_number
        )

        novel = await global_manager.create_novel(novel_data)

        return json.dumps({
            "success": True,
            "message": f"小说 '{title}' 创建成功",
            "novel": {
                "id": str(novel.id),
                "project_id": str(novel.project_id),
                "name": novel.name,
                "title": novel.title,
                "description": novel.description,
                "volume_number": novel.volume_number,
                "status": novel.status,
                "created_at": novel.created_at.isoformat()
            }
        }, indent=2, ensure_ascii=False)

    except DatabaseError as e:
        return json.dumps({
            "success": False,
            "message": f"创建小说失败: {str(e)}"
        }, indent=2, ensure_ascii=False)


@mcp.tool()
async def list_projects() -> str:
    """获取所有项目列表"""
    try:
        global_manager = get_global_manager()
        projects = await global_manager.get_projects()

        projects_data = []
        for project in projects:
            # 获取项目下的小说
            novels = await global_manager.get_novels_by_project(project.id)

            projects_data.append({
                "id": str(project.id),
                "name": project.name,
                "title": project.title,
                "description": project.description,
                "author": project.author,
                "genre": project.genre,
                "status": project.status,
                "novel_count": len(novels),
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat()
            })

        return json.dumps({
            "success": True,
            "total_projects": len(projects_data),
            "projects": projects_data
        }, indent=2, ensure_ascii=False)

    except DatabaseError as e:
        return json.dumps({
            "success": False,
            "message": f"获取项目列表失败: {str(e)}"
        }, indent=2, ensure_ascii=False)


# =============================================================================
# 批次管理工具
# =============================================================================


@mcp.tool()
async def create_content_batch(
    novel_id: str,
    batch_name: str,
    batch_type: str,
    description: str = "",
    priority: int = 3,
    due_date: str = ""
) -> str:
    """创建内容批次"""
    try:
        novel_manager = get_novel_manager(novel_id)

        # 解析截止日期
        due_date_obj = None
        if due_date:
            try:
                due_date_obj = datetime.fromisoformat(due_date)
            except ValueError:
                return json.dumps({
                    "success": False,
                    "message": "截止日期格式错误，请使用 ISO 格式 (YYYY-MM-DDTHH:MM:SS)"
                }, indent=2, ensure_ascii=False)

        # 获取下一个批次编号
        existing_batches = await novel_manager.get_content_batches()
        next_batch_number = max([b.batch_number for b in existing_batches], default=0) + 1

        batch_data = ContentBatchCreate(
            novel_id=UUID(novel_id),
            batch_name=batch_name,
            batch_number=next_batch_number,
            batch_type=BatchType(batch_type),
            description=description or None,
            priority=priority,
            due_date=due_date_obj
        )

        batch = await novel_manager.create_content_batch(batch_data)

        return json.dumps({
            "success": True,
            "message": f"内容批次 '{batch_name}' 创建成功",
            "batch": {
                "id": str(batch.id),
                "novel_id": str(batch.novel_id),
                "batch_name": batch.batch_name,
                "batch_number": batch.batch_number,
                "batch_type": batch.batch_type,
                "description": batch.description,
                "priority": batch.priority,
                "status": batch.status,
                "due_date": batch.due_date.isoformat() if batch.due_date else None,
                "created_at": batch.created_at.isoformat()
            }
        }, indent=2, ensure_ascii=False)

    except DatabaseError as e:
        return json.dumps({
            "success": False,
            "message": f"创建内容批次失败: {str(e)}"
        }, indent=2, ensure_ascii=False)


@mcp.tool()
async def get_batch_dashboard(novel_id: str) -> str:
    """获取批次管理仪表板"""
    try:
        batch_manager = await get_batch_manager(novel_id)
        dashboard_data = await batch_manager.get_batch_dashboard()

        return json.dumps({
            "success": True,
            "dashboard": dashboard_data
        }, indent=2, ensure_ascii=False)

    except DatabaseError as e:
        return json.dumps({
            "success": False,
            "message": f"获取批次仪表板失败: {str(e)}"
        }, indent=2, ensure_ascii=False)


@mcp.tool()
async def create_batch_series(
    novel_id: str,
    series_name: str,
    batch_type: str,
    batch_count: int,
    description: str = "",
    interval_days: int = 7
) -> str:
    """创建批次系列"""
    try:
        batch_manager = await get_batch_manager(novel_id)

        batches = await batch_manager.create_batch_series(
            series_name=series_name,
            batch_type=BatchType(batch_type),
            batch_count=batch_count,
            description=description or None,
            interval_days=interval_days
        )

        batches_info = [
            {
                "id": str(batch.id),
                "batch_name": batch.batch_name,
                "batch_number": batch.batch_number,
                "due_date": batch.due_date.isoformat() if batch.due_date else None
            }
            for batch in batches
        ]

        return json.dumps({
            "success": True,
            "message": f"批次系列 '{series_name}' 创建成功，包含 {batch_count} 个批次",
            "series_name": series_name,
            "batch_count": batch_count,
            "batches": batches_info
        }, indent=2, ensure_ascii=False)

    except DatabaseError as e:
        return json.dumps({
            "success": False,
            "message": f"创建批次系列失败: {str(e)}"
        }, indent=2, ensure_ascii=False)


# =============================================================================
# 内容段落管理工具
# =============================================================================


@mcp.tool()
async def create_content_segment(
    batch_id: str,
    title: str,
    content: str,
    segment_type: str = "narrative",
    tags: str = ""
) -> str:
    """创建内容段落"""
    try:
        # 通过批次ID获取小说ID
        global_manager = get_global_manager()

        # 这里需要先获取批次信息来确定小说ID
        # 为了简化，我们假设已经知道novel_id，实际使用中可以通过批次查询

        # 解析标签
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []

        # 获取批次中现有段落的数量来确定序列号
        novel_manager = get_novel_manager("dummy")  # 这里需要实际的小说ID
        existing_segments = await novel_manager.get_content_segments(batch_id)
        next_sequence = len(existing_segments) + 1

        segment_data = ContentSegmentCreate(
            batch_id=UUID(batch_id),
            segment_type=SegmentType(segment_type),
            title=title,
            content=content,
            sequence_order=next_sequence,
            tags=tag_list
        )

        segment = await novel_manager.create_content_segment(segment_data)

        return json.dumps({
            "success": True,
            "message": f"内容段落 '{title}' 创建成功",
            "segment": {
                "id": str(segment.id),
                "batch_id": str(segment.batch_id),
                "title": segment.title,
                "segment_type": segment.segment_type,
                "word_count": segment.word_count,
                "sequence_order": segment.sequence_order,
                "tags": segment.tags,
                "status": segment.status,
                "created_at": segment.created_at.isoformat()
            }
        }, indent=2, ensure_ascii=False)

    except DatabaseError as e:
        return json.dumps({
            "success": False,
            "message": f"创建内容段落失败: {str(e)}"
        }, indent=2, ensure_ascii=False)


# =============================================================================
# 世界观管理工具
# =============================================================================


@mcp.tool()
async def create_domain(
    novel_id: str,
    name: str,
    domain_type: str,
    description: str = "",
    power_level: int = 5
) -> str:
    """创建九域中的一个域"""
    try:
        novel_manager = get_novel_manager(novel_id)

        domain_data = DomainCreate(
            novel_id=UUID(novel_id),
            name=name,
            domain_type=DomainType(domain_type),
            description=description or None,
            power_level=power_level
        )

        domain = await novel_manager.create_domain(domain_data)

        return json.dumps({
            "success": True,
            "message": f"域 '{name}' 创建成功",
            "domain": {
                "id": str(domain.id),
                "novel_id": str(domain.novel_id),
                "name": domain.name,
                "domain_type": domain.domain_type,
                "description": domain.description,
                "power_level": domain.power_level,
                "created_at": domain.created_at.isoformat()
            }
        }, indent=2, ensure_ascii=False)

    except DatabaseError as e:
        return json.dumps({
            "success": False,
            "message": f"创建域失败: {str(e)}"
        }, indent=2, ensure_ascii=False)


@mcp.tool()
async def create_law_chain(
    novel_id: str,
    name: str,
    chain_type: str,
    description: str = "",
    power_level: int = 5,
    rarity: str = "common"
) -> str:
    """创建法则链"""
    try:
        novel_manager = get_novel_manager(novel_id)

        law_chain_data = LawChainCreate(
            novel_id=UUID(novel_id),
            name=name,
            chain_type=chain_type,
            description=description or None,
            power_level=power_level,
            rarity=ItemRarity(rarity)
        )

        law_chain = await novel_manager.create_law_chain(law_chain_data)

        return json.dumps({
            "success": True,
            "message": f"法则链 '{name}' 创建成功",
            "law_chain": {
                "id": str(law_chain.id),
                "novel_id": str(law_chain.novel_id),
                "name": law_chain.name,
                "chain_type": law_chain.chain_type,
                "description": law_chain.description,
                "power_level": law_chain.power_level,
                "rarity": law_chain.rarity,
                "created_at": law_chain.created_at.isoformat()
            }
        }, indent=2, ensure_ascii=False)

    except DatabaseError as e:
        return json.dumps({
            "success": False,
            "message": f"创建法则链失败: {str(e)}"
        }, indent=2, ensure_ascii=False)


@mcp.tool()
async def create_character(
    novel_id: str,
    name: str,
    character_type: str,
    description: str = "",
    tags: str = ""
) -> str:
    """创建角色"""
    try:
        novel_manager = get_novel_manager(novel_id)

        # 解析标签
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []

        character_data = CharacterCreate(
            novel_id=novel_id,
            name=name,
            character_type=character_type,
            basic_info={"description": description} if description else None,
            tags=tag_list
        )

        character = await novel_manager.create_character(character_data)

        return json.dumps({
            "success": True,
            "message": f"角色 '{name}' 创建成功",
            "character": {
                "id": character.id,
                "novel_id": character.novel_id,
                "name": character.name,
                "character_type": character.character_type,
                "status": character.status,
                "tags": character.tags,
                "created_at": character.created_at.isoformat()
            }
        }, indent=2, ensure_ascii=False)

    except DatabaseError as e:
        return json.dumps({
            "success": False,
            "message": f"创建角色失败: {str(e)}"
        }, indent=2, ensure_ascii=False)


# =============================================================================
# 文化框架管理工具
# =============================================================================


@mcp.tool()
async def create_cultural_framework(
    novel_id: str,
    domain_type: str,
    dimension: str,
    title: str,
    detailed_content: str,
    summary: str = "",
    key_elements: str = "",
    tags: str = "",
    priority: int = 5
) -> str:
    """创建文化框架"""
    try:
        # 导入文化框架相关模块
        from database.repositories.cultural_framework_repository import CulturalFrameworkRepository
        from database.connection_manager import DatabaseConnectionManager
        from database.models.cultural_framework_models import (
            CulturalFrameworkCreate, DomainType, CulturalDimension
        )

        # 初始化仓库
        connection_manager = DatabaseConnectionManager()
        await connection_manager.initialize()
        repository = CulturalFrameworkRepository(connection_manager)
        await repository.initialize()

        # 解析参数
        key_elements_list = [elem.strip() for elem in key_elements.split(",") if elem.strip()] if key_elements else []
        tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []

        # 创建文化框架
        framework_data = CulturalFrameworkCreate(
            novel_id=UUID(novel_id),
            domain_type=DomainType(domain_type),
            dimension=CulturalDimension(dimension),
            title=title,
            summary=summary or None,
            key_elements=key_elements_list,
            detailed_content=detailed_content,
            tags=tags_list,
            priority=priority
        )

        framework_id = await repository.create_cultural_framework(framework_data)

        return json.dumps({
            "success": True,
            "message": f"文化框架 '{title}' 创建成功",
            "framework": {
                "id": str(framework_id),
                "novel_id": novel_id,
                "domain_type": domain_type,
                "dimension": dimension,
                "title": title,
                "priority": priority
            }
        }, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"创建文化框架失败: {str(e)}"
        }, indent=2, ensure_ascii=False)


@mcp.tool()
async def create_cultural_entity(
    novel_id: str,
    name: str,
    entity_type: str,
    description: str,
    domain_type: str = "",
    dimensions: str = "",
    functions: str = "",
    significance: str = "",
    tags: str = ""
) -> str:
    """创建文化实体"""
    try:
        from database.repositories.cultural_framework_repository import CulturalFrameworkRepository
        from database.connection_manager import DatabaseConnectionManager
        from database.models.cultural_framework_models import (
            CulturalEntityCreate, EntityType, DomainType, CulturalDimension
        )

        # 初始化仓库
        connection_manager = DatabaseConnectionManager()
        await connection_manager.initialize()
        repository = CulturalFrameworkRepository(connection_manager)
        await repository.initialize()

        # 解析参数
        dimensions_list = []
        if dimensions:
            for dim in dimensions.split(","):
                try:
                    dimensions_list.append(CulturalDimension(dim.strip()))
                except ValueError:
                    pass  # 忽略无效的维度

        functions_list = [func.strip() for func in functions.split(",") if func.strip()] if functions else []
        tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []

        # 创建文化实体
        entity_data = CulturalEntityCreate(
            novel_id=UUID(novel_id),
            name=name,
            entity_type=EntityType(entity_type),
            domain_type=DomainType(domain_type) if domain_type else None,
            dimensions=dimensions_list,
            description=description,
            functions=functions_list,
            significance=significance or None,
            tags=tags_list
        )

        entity_id = await repository.create_cultural_entity(entity_data)

        return json.dumps({
            "success": True,
            "message": f"文化实体 '{name}' 创建成功",
            "entity": {
                "id": str(entity_id),
                "novel_id": novel_id,
                "name": name,
                "entity_type": entity_type,
                "domain_type": domain_type,
                "dimensions": dimensions_list
            }
        }, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"创建文化实体失败: {str(e)}"
        }, indent=2, ensure_ascii=False)


@mcp.tool()
async def create_cultural_relation(
    novel_id: str,
    source_entity_name: str,
    target_entity_name: str,
    relation_type: str,
    description: str = "",
    strength: float = 1.0,
    context: str = ""
) -> str:
    """创建文化实体关系"""
    try:
        from database.repositories.cultural_framework_repository import CulturalFrameworkRepository
        from database.connection_manager import DatabaseConnectionManager
        from database.models.cultural_framework_models import (
            CulturalRelationCreate, RelationType
        )

        # 初始化仓库
        connection_manager = DatabaseConnectionManager()
        await connection_manager.initialize()
        repository = CulturalFrameworkRepository(connection_manager)
        await repository.initialize()

        # 查找实体ID（这里简化处理，实际应该通过名称搜索）
        # 暂时返回错误提示，因为需要实现实体搜索功能
        return json.dumps({
            "success": False,
            "message": "创建文化关系功能正在开发中，需要先实现实体搜索功能"
        }, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"创建文化关系失败: {str(e)}"
        }, indent=2, ensure_ascii=False)


@mcp.tool()
async def import_cultural_analysis(
    novel_id: str,
    analysis_file_path: str,
    task_name: str = "文化框架分析导入"
) -> str:
    """导入文化框架分析结果"""
    try:
        from database.repositories.cultural_framework_repository import CulturalFrameworkRepository
        from database.connection_manager import DatabaseConnectionManager
        from database.cultural_batch_manager import CulturalDataBatchManager
        import json

        # 初始化仓库和批量管理器
        connection_manager = DatabaseConnectionManager()
        await connection_manager.initialize()
        repository = CulturalFrameworkRepository(connection_manager)
        await repository.initialize()
        batch_manager = CulturalDataBatchManager(repository)

        # 读取分析文件
        with open(analysis_file_path, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)

        # 导入数据
        task_id = await batch_manager.import_cultural_framework_analysis(
            novel_id=UUID(novel_id),
            analysis_data=analysis_data,
            task_name=task_name
        )

        # 获取处理统计
        stats = batch_manager.get_processing_statistics()

        return json.dumps({
            "success": True,
            "message": f"文化框架分析导入任务启动成功",
            "task_id": task_id,
            "processing_stats": stats
        }, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"导入文化框架分析失败: {str(e)}"
        }, indent=2, ensure_ascii=False)


@mcp.tool()
async def get_cultural_entities_by_type(
    novel_id: str,
    entity_type: str,
    domain_type: str = ""
) -> str:
    """按类型获取文化实体"""
    try:
        from database.repositories.cultural_framework_repository import CulturalFrameworkRepository
        from database.connection_manager import DatabaseConnectionManager
        from database.models.cultural_framework_models import EntityType, DomainType

        # 初始化仓库
        connection_manager = DatabaseConnectionManager()
        await connection_manager.initialize()
        repository = CulturalFrameworkRepository(connection_manager)
        await repository.initialize()

        # 获取实体
        entities = await repository.get_entities_by_type(
            novel_id=UUID(novel_id),
            entity_type=EntityType(entity_type),
            domain_type=DomainType(domain_type) if domain_type else None
        )

        entities_data = [
            {
                "id": str(entity.id),
                "name": entity.name,
                "entity_type": entity.entity_type.value,
                "domain_type": entity.domain_type.value if entity.domain_type else None,
                "description": entity.description[:200] + "..." if len(entity.description) > 200 else entity.description,
                "functions": entity.functions,
                "tags": entity.tags
            }
            for entity in entities
        ]

        return json.dumps({
            "success": True,
            "message": f"找到 {len(entities)} 个 {entity_type} 类型的文化实体",
            "entities": entities_data
        }, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"获取文化实体失败: {str(e)}"
        }, indent=2, ensure_ascii=False)


@mcp.tool()
async def get_cross_domain_relations(novel_id: str) -> str:
    """获取跨域关系分析"""
    try:
        from database.repositories.cultural_framework_repository import CulturalFrameworkRepository
        from database.connection_manager import DatabaseConnectionManager

        # 初始化仓库
        connection_manager = DatabaseConnectionManager()
        await connection_manager.initialize()
        repository = CulturalFrameworkRepository(connection_manager)
        await repository.initialize()

        # 获取跨域关系
        relations = await repository.get_cross_domain_relations(UUID(novel_id))

        return json.dumps({
            "success": True,
            "message": f"找到 {len(relations)} 个跨域关系",
            "cross_domain_relations": relations
        }, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"获取跨域关系失败: {str(e)}"
        }, indent=2, ensure_ascii=False)


@mcp.tool()
async def search_cultural_entities(
    novel_id: str,
    search_query: str,
    entity_types: str = "",
    domains: str = ""
) -> str:
    """全文搜索文化实体"""
    try:
        from database.repositories.cultural_framework_repository import CulturalFrameworkRepository
        from database.connection_manager import DatabaseConnectionManager
        from database.models.cultural_framework_models import EntityType, DomainType

        # 初始化仓库
        connection_manager = DatabaseConnectionManager()
        await connection_manager.initialize()
        repository = CulturalFrameworkRepository(connection_manager)
        await repository.initialize()

        # 解析搜索参数
        entity_types_list = []
        if entity_types:
            for et in entity_types.split(","):
                try:
                    entity_types_list.append(EntityType(et.strip()))
                except ValueError:
                    pass

        domains_list = []
        if domains:
            for domain in domains.split(","):
                try:
                    domains_list.append(DomainType(domain.strip()))
                except ValueError:
                    pass

        # 执行搜索
        results = await repository.search_entities(
            novel_id=UUID(novel_id),
            search_query=search_query,
            entity_types=entity_types_list if entity_types_list else None,
            domains=domains_list if domains_list else None
        )

        return json.dumps({
            "success": True,
            "message": f"找到 {len(results)} 个匹配的文化实体",
            "search_results": results
        }, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"搜索文化实体失败: {str(e)}"
        }, indent=2, ensure_ascii=False)


@mcp.tool()
async def get_cultural_statistics(novel_id: str) -> str:
    """获取文化框架统计信息"""
    try:
        from database.repositories.cultural_framework_repository import CulturalFrameworkRepository
        from database.connection_manager import DatabaseConnectionManager

        # 初始化仓库
        connection_manager = DatabaseConnectionManager()
        await connection_manager.initialize()
        repository = CulturalFrameworkRepository(connection_manager)
        await repository.initialize()

        # 获取统计信息
        stats = await repository.get_novel_statistics(UUID(novel_id))

        return json.dumps({
            "success": True,
            "cultural_statistics": stats
        }, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"获取文化统计信息失败: {str(e)}"
        }, indent=2, ensure_ascii=False)


# =============================================================================
# 搜索和统计工具
# =============================================================================


@mcp.tool()
async def search_novel_content(
    novel_id: str,
    query: str,
    content_types: str = ""
) -> str:
    """搜索小说内容"""
    try:
        novel_manager = get_novel_manager(novel_id)

        # 解析内容类型
        content_type_list = None
        if content_types:
            content_type_list = [ct.strip() for ct in content_types.split(",") if ct.strip()]

        search_results = await novel_manager.search_content(query, content_type_list)

        return json.dumps({
            "success": True,
            "query": query,
            "results": {
                "segments_count": len(search_results.get("segments", [])),
                "characters_count": len(search_results.get("characters", [])),
                "locations_count": len(search_results.get("locations", [])),
                "knowledge_count": len(search_results.get("knowledge", [])),
                "segments": [
                    {
                        "id": str(s.id),
                        "title": s.title,
                        "content_preview": s.content[:200] + "..." if len(s.content) > 200 else s.content,
                        "word_count": s.word_count,
                        "tags": s.tags
                    }
                    for s in search_results.get("segments", [])
                ],
                "characters": [
                    {
                        "id": c.id,
                        "name": c.name,
                        "character_type": c.character_type,
                        "tags": c.tags
                    }
                    for c in search_results.get("characters", [])
                ]
            }
        }, indent=2, ensure_ascii=False)

    except DatabaseError as e:
        return json.dumps({
            "success": False,
            "message": f"搜索内容失败: {str(e)}"
        }, indent=2, ensure_ascii=False)


@mcp.tool()
async def get_novel_statistics(novel_id: str) -> str:
    """获取小说统计信息"""
    try:
        novel_manager = get_novel_manager(novel_id)
        stats = await novel_manager.get_novel_statistics()

        return json.dumps({
            "success": True,
            "statistics": stats
        }, indent=2, ensure_ascii=False)

    except DatabaseError as e:
        return json.dumps({
            "success": False,
            "message": f"获取统计信息失败: {str(e)}"
        }, indent=2, ensure_ascii=False)


# =============================================================================
# 调试和维护工具
# =============================================================================


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    asyncio.create_task(close_database())
    sys.exit(0)


# =============================================================================
# 冲突分析系统API
# =============================================================================

@mcp.tool()
async def import_conflict_analysis_data(
    project_id: str = "29c170c5-4a3e-4829-a242-74c1acb96453",
    novel_id: str = "e1fd1aa4-bde2-4c76-8cee-334e54fa47d1",
    clear_existing: bool = False,
    validate_integrity: bool = True
) -> str:
    """
    导入跨域冲突分析数据到数据库

    Args:
        project_id: 项目ID（默认为"裂世九域·法则链纪元"）
        novel_id: 小说ID（默认为"裂世九域·主线"）
        clear_existing: 是否清除现有冲突数据
        validate_integrity: 是否验证数据完整性

    Returns:
        导入结果的JSON字符串
    """
    try:
        config = ImportConfig(
            project_id=project_id,
            novel_id=novel_id,
            clear_existing_data=clear_existing,
            validate_data_integrity=validate_integrity
        )

        importer = ConflictDataImporter(config)
        result = await importer.run_import()

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"冲突数据导入失败: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "message": "冲突分析数据导入失败"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
async def query_conflict_matrix(
    novel_id: str = "e1fd1aa4-bde2-4c76-8cee-334e54fa47d1",
    domain_a: Optional[str] = None,
    domain_b: Optional[str] = None,
    min_intensity: float = 0.0,
    max_intensity: float = 5.0
) -> str:
    """
    查询跨域冲突矩阵数据

    Args:
        novel_id: 小说ID
        domain_a: 域A名称（可选）
        domain_b: 域B名称（可选）
        min_intensity: 最小冲突强度
        max_intensity: 最大冲突强度

    Returns:
        冲突矩阵数据的JSON字符串
    """
    try:
        manager = await get_novel_manager(novel_id)

        # 构建查询条件
        conditions = ["novel_id = $1", "intensity BETWEEN $2 AND $3"]
        params = [novel_id, min_intensity, max_intensity]

        if domain_a:
            conditions.append("(domain_a = $4 OR domain_b = $4)")
            params.append(domain_a)

        if domain_b and domain_a != domain_b:
            param_idx = len(params) + 1
            conditions.append(f"(domain_a = ${param_idx} OR domain_b = ${param_idx})")
            params.append(domain_b)

        query = f"""
            SELECT id, matrix_name, domain_a, domain_b, intensity, conflict_type,
                   risk_level, status, priority, core_resources, trigger_laws,
                   typical_scenarios, key_roles, created_at, updated_at
            FROM cross_domain_conflict_matrix
            WHERE {' AND '.join(conditions)}
            ORDER BY intensity DESC, priority DESC
        """

        results = await manager.fetch_query(query, *params)

        # 转换结果为字典格式
        conflicts = []
        for row in results:
            conflict = dict(row)
            # 转换UUID和时间戳为字符串
            conflict['id'] = str(conflict['id'])
            conflict['created_at'] = conflict['created_at'].isoformat()
            conflict['updated_at'] = conflict['updated_at'].isoformat()
            conflicts.append(conflict)

        return json.dumps({
            "success": True,
            "count": len(conflicts),
            "conflicts": conflicts
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"冲突矩阵查询失败: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "message": "冲突矩阵查询失败"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
async def query_conflict_entities(
    novel_id: str = "e1fd1aa4-bde2-4c76-8cee-334e54fa47d1",
    entity_type: Optional[str] = None,
    domain: Optional[str] = None,
    min_strategic_value: float = 0.0,
    limit: int = 100
) -> str:
    """
    查询冲突实体数据

    Args:
        novel_id: 小说ID
        entity_type: 实体类型（可选）
        domain: 相关域（可选）
        min_strategic_value: 最小战略价值
        limit: 返回结果限制

    Returns:
        冲突实体数据的JSON字符串
    """
    try:
        manager = await get_novel_manager(novel_id)

        # 构建查询条件
        conditions = ["novel_id = $1", "strategic_value >= $2"]
        params = [novel_id, min_strategic_value]

        if entity_type:
            conditions.append("entity_type = $3")
            params.append(entity_type)

        if domain:
            param_idx = len(params) + 1
            conditions.append(f"(primary_domain = ${param_idx} OR ${param_idx} = ANY(involved_domains))")
            params.append(domain)

        query = f"""
            SELECT id, name, entity_type, entity_subtype, primary_domain,
                   involved_domains, description, strategic_value, economic_value,
                   symbolic_value, scarcity_level, conflict_roles, dispute_intensity,
                   confidence_score, validation_status, tags, created_at
            FROM conflict_entities
            WHERE {' AND '.join(conditions)}
            ORDER BY strategic_value DESC, dispute_intensity DESC
            LIMIT ${len(params) + 1}
        """

        params.append(limit)
        results = await manager.fetch_query(query, *params)

        # 转换结果为字典格式
        entities = []
        for row in results:
            entity = dict(row)
            entity['id'] = str(entity['id'])
            entity['created_at'] = entity['created_at'].isoformat()
            entities.append(entity)

        return json.dumps({
            "success": True,
            "count": len(entities),
            "entities": entities
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"冲突实体查询失败: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "message": "冲突实体查询失败"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
async def query_story_hooks(
    novel_id: str = "e1fd1aa4-bde2-4c76-8cee-334e54fa47d1",
    hook_type: Optional[str] = None,
    min_score: float = 5.0,
    is_ai_generated: Optional[bool] = None,
    domains: Optional[List[str]] = None,
    limit: int = 50
) -> str:
    """
    查询剧情钩子数据

    Args:
        novel_id: 小说ID
        hook_type: 钩子类型（可选）
        min_score: 最小综合评分
        is_ai_generated: 是否AI生成（可选）
        domains: 相关域列表（可选）
        limit: 返回结果限制

    Returns:
        剧情钩子数据的JSON字符串
    """
    try:
        manager = await get_novel_manager(novel_id)

        # 构建查询条件
        conditions = ["novel_id = $1", "overall_score >= $2"]
        params = [novel_id, min_score]

        if hook_type:
            conditions.append("hook_type = $3")
            params.append(hook_type)

        if is_ai_generated is not None:
            param_idx = len(params) + 1
            conditions.append(f"is_ai_generated = ${param_idx}")
            params.append(is_ai_generated)

        if domains:
            param_idx = len(params) + 1
            conditions.append(f"domains_involved && ${param_idx}")
            params.append(domains)

        query = f"""
            SELECT id, title, description, hook_type, hook_subtype,
                   domains_involved, main_characters, moral_themes,
                   inciting_incident, originality, complexity, emotional_impact,
                   plot_integration, overall_score, priority_level,
                   is_ai_generated, generation_method, human_validation_status,
                   usage_count, tags, created_at
            FROM conflict_story_hooks
            WHERE {' AND '.join(conditions)}
            ORDER BY overall_score DESC, priority_level DESC
            LIMIT ${len(params) + 1}
        """

        params.append(limit)
        results = await manager.fetch_query(query, *params)

        # 转换结果为字典格式
        hooks = []
        for row in results:
            hook = dict(row)
            hook['id'] = str(hook['id'])
            hook['created_at'] = hook['created_at'].isoformat()
            hooks.append(hook)

        return json.dumps({
            "success": True,
            "count": len(hooks),
            "story_hooks": hooks
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"剧情钩子查询失败: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "message": "剧情钩子查询失败"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
async def query_network_analysis(
    novel_id: str = "e1fd1aa4-bde2-4c76-8cee-334e54fa47d1",
    analysis_type: Optional[str] = None,
    min_confidence: float = 0.5
) -> str:
    """
    查询网络分析结果

    Args:
        novel_id: 小说ID
        analysis_type: 分析类型（可选）
        min_confidence: 最小置信度

    Returns:
        网络分析结果的JSON字符串
    """
    try:
        manager = await get_novel_manager(novel_id)

        # 构建查询条件
        conditions = ["novel_id = $1", "analysis_confidence >= $2"]
        params = [novel_id, min_confidence]

        if analysis_type:
            conditions.append("analysis_type = $3")
            params.append(analysis_type)

        query = f"""
            SELECT id, analysis_type, network_type, node_count, edge_count,
                   network_density, average_clustering_coefficient,
                   average_path_length, diameter, modularity,
                   community_count, analysis_confidence, results,
                   analysis_date, created_at
            FROM network_analysis_results
            WHERE {' AND '.join(conditions)}
            ORDER BY analysis_date DESC, analysis_confidence DESC
        """

        results = await manager.fetch_query(query, *params)

        # 转换结果为字典格式
        analyses = []
        for row in results:
            analysis = dict(row)
            analysis['id'] = str(analysis['id'])
            analysis['analysis_date'] = analysis['analysis_date'].isoformat()
            analysis['created_at'] = analysis['created_at'].isoformat()
            # 解析JSONB字段
            if analysis['results']:
                analysis['results'] = json.loads(analysis['results'])
            analyses.append(analysis)

        return json.dumps({
            "success": True,
            "count": len(analyses),
            "network_analyses": analyses
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"网络分析查询失败: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "message": "网络分析查询失败"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
async def get_conflict_statistics(
    novel_id: str = "e1fd1aa4-bde2-4c76-8cee-334e54fa47d1"
) -> str:
    """
    获取冲突分析系统的统计信息

    Args:
        novel_id: 小说ID

    Returns:
        冲突分析统计信息的JSON字符串
    """
    try:
        manager = await get_novel_manager(novel_id)

        # 查询各类数据的统计信息
        stats_queries = {
            "conflict_matrices": "SELECT COUNT(*) as count, AVG(intensity) as avg_intensity FROM cross_domain_conflict_matrix WHERE novel_id = $1",
            "conflict_entities": "SELECT COUNT(*) as count, entity_type, AVG(strategic_value) as avg_value FROM conflict_entities WHERE novel_id = $1 GROUP BY entity_type",
            "conflict_relations": "SELECT COUNT(*) as count, relation_type FROM conflict_relations WHERE novel_id = $1 GROUP BY relation_type",
            "story_hooks": "SELECT COUNT(*) as count, hook_type, AVG(overall_score) as avg_score, COUNT(CASE WHEN is_ai_generated THEN 1 END) as ai_generated_count FROM conflict_story_hooks WHERE novel_id = $1 GROUP BY hook_type",
            "network_analyses": "SELECT COUNT(*) as count, analysis_type FROM network_analysis_results WHERE novel_id = $1 GROUP BY analysis_type"
        }

        statistics = {}

        for stat_name, query in stats_queries.items():
            results = await manager.fetch_query(query, novel_id)

            if stat_name in ["conflict_entities", "conflict_relations", "story_hooks", "network_analyses"]:
                # 分组统计结果
                statistics[stat_name] = [dict(row) for row in results]
            else:
                # 单个统计结果
                if results:
                    statistics[stat_name] = dict(results[0])
                else:
                    statistics[stat_name] = {"count": 0}

        # 查询域参与度统计
        domain_stats_query = """
            WITH domain_conflicts AS (
                SELECT domain_a as domain, intensity FROM cross_domain_conflict_matrix WHERE novel_id = $1
                UNION ALL
                SELECT domain_b as domain, intensity FROM cross_domain_conflict_matrix WHERE novel_id = $1
            )
            SELECT domain, COUNT(*) as conflict_count, AVG(intensity) as avg_intensity
            FROM domain_conflicts
            GROUP BY domain
            ORDER BY avg_intensity DESC
        """

        domain_results = await manager.fetch_query(domain_stats_query, novel_id)
        statistics["domain_participation"] = [dict(row) for row in domain_results]

        return json.dumps({
            "success": True,
            "novel_id": novel_id,
            "generated_at": datetime.now().isoformat(),
            "statistics": statistics
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"冲突统计查询失败: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "message": "冲突分析统计查询失败"
        }, ensure_ascii=False, indent=2)

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
