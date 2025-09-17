"""
地理数据访问服务
提供地理实体的CRUD操作和查询接口
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from .connections.postgresql import get_postgresql_connection
from .models.geographic_models import (
    GeographicEntity, Region, City, Town, Village, Landmark, Building,
    NaturalFeature, Infrastructure, GeographicRelationship,
    GeographicQuery, GeographicSummary, GeographicHierarchy,
    CreateGeographicEntityRequest, UpdateGeographicEntityRequest,
    CreateGeographicRelationshipRequest, GeographicDataImport
)
from .models.plot_mapping_models import (
    PlotFunctionType, PlotNodeType, GeographicPlotMapping, PlotHookDetail,
    PlotFunctionUsage, GeographicPlotView, PlotFunctionStats,
    PlotFunctionQuery, CreatePlotMappingRequest, UpdatePlotMappingRequest,
    RecordPlotUsageRequest, BatchPlotMappingImport, PlotFunctionQueryResponse
)
from .models.models import StandardResponse, PaginatedResponse


class GeographicService:
    """地理数据服务"""

    def __init__(self):
        self.entity_type_mapping = {
            'region': Region,
            'city': City,
            'town': Town,
            'village': Village,
            'landmark': Landmark,
            'building': Building,
            'natural_feature': NaturalFeature,
            'infrastructure': Infrastructure
        }

    async def create_geographic_entity(self, request: CreateGeographicEntityRequest) -> StandardResponse:
        """创建地理实体"""
        try:
            async with get_postgresql_connection() as conn:
                # 获取实体类型ID
                entity_type_id = await self._get_entity_type_id(conn, request.entity_type, request.novel_id)
                if not entity_type_id:
                    return StandardResponse(
                        success=False,
                        message=f"未找到实体类型: {request.entity_type}",
                        error="ENTITY_TYPE_NOT_FOUND"
                    )

                # 生成代码标识
                code = f"{request.domain_code}_{request.name.replace(' ', '_').lower()}" if request.domain_code else None

                # 构建属性
                attributes = request.attributes.copy()
                attributes.update({
                    'domain_code': request.domain_code,
                    'region_name': request.region_name
                })

                # 创建实体
                query = """
                INSERT INTO entities (novel_id, entity_type_id, name, code, attributes, tags, priority, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING id
                """

                now = datetime.utcnow()
                row = await conn.fetchrow(
                    query, request.novel_id, entity_type_id, request.name, code,
                    attributes, request.tags, request.geographic_importance, now, now
                )

                entity_id = row['id']

                # 创建父子关系（如果指定了父级实体）
                if request.parent_entity_id:
                    await self._create_parent_child_relationship(
                        conn, request.novel_id, request.parent_entity_id, entity_id
                    )

                return StandardResponse(
                    success=True,
                    message="地理实体创建成功",
                    data={"entity_id": entity_id}
                )

        except Exception as e:
            return StandardResponse(
                success=False,
                message="创建地理实体失败",
                error=str(e)
            )

    async def get_geographic_entity(self, novel_id: int, entity_id: int) -> StandardResponse:
        """获取地理实体详情"""
        try:
            async with get_postgresql_connection() as conn:
                query = """
                SELECT e.*, et.name as entity_type_name
                FROM entities e
                JOIN entity_types et ON e.entity_type_id = et.id
                WHERE e.novel_id = $1 AND e.id = $2
                """

                row = await conn.fetchrow(query, novel_id, entity_id)
                if not row:
                    return StandardResponse(
                        success=False,
                        message="地理实体不存在",
                        error="ENTITY_NOT_FOUND"
                    )

                # 转换为对应的地理实体模型
                entity_type = row['entity_type_name']
                model_class = self.entity_type_mapping.get(entity_type, GeographicEntity)

                entity_data = dict(row)
                entity = model_class(**entity_data)

                return StandardResponse(
                    success=True,
                    message="获取地理实体成功",
                    data=entity.dict()
                )

        except Exception as e:
            return StandardResponse(
                success=False,
                message="获取地理实体失败",
                error=str(e)
            )

    async def update_geographic_entity(self, novel_id: int, entity_id: int,
                                     request: UpdateGeographicEntityRequest) -> StandardResponse:
        """更新地理实体"""
        try:
            async with get_postgresql_connection() as conn:
                # 构建更新字段
                update_fields = []
                params = [novel_id, entity_id]
                param_idx = 3

                if request.name is not None:
                    update_fields.append(f"name = ${param_idx}")
                    params.append(request.name)
                    param_idx += 1

                if request.attributes is not None:
                    update_fields.append(f"attributes = ${param_idx}")
                    params.append(request.attributes)
                    param_idx += 1

                if request.tags is not None:
                    update_fields.append(f"tags = ${param_idx}")
                    params.append(request.tags)
                    param_idx += 1

                if request.geographic_importance is not None:
                    update_fields.append(f"priority = ${param_idx}")
                    params.append(request.geographic_importance)
                    param_idx += 1

                if not update_fields:
                    return StandardResponse(
                        success=False,
                        message="没有提供更新字段",
                        error="NO_UPDATE_FIELDS"
                    )

                update_fields.append(f"updated_at = ${param_idx}")
                params.append(datetime.utcnow())

                query = f"""
                UPDATE entities
                SET {', '.join(update_fields)}
                WHERE novel_id = $1 AND id = $2
                RETURNING id
                """

                row = await conn.fetchrow(query, *params)
                if not row:
                    return StandardResponse(
                        success=False,
                        message="地理实体不存在",
                        error="ENTITY_NOT_FOUND"
                    )

                return StandardResponse(
                    success=True,
                    message="地理实体更新成功"
                )

        except Exception as e:
            return StandardResponse(
                success=False,
                message="更新地理实体失败",
                error=str(e)
            )

    async def delete_geographic_entity(self, novel_id: int, entity_id: int) -> StandardResponse:
        """删除地理实体"""
        try:
            async with get_postgresql_connection() as conn:
                query = """
                UPDATE entities
                SET status = 'deleted', updated_at = $3
                WHERE novel_id = $1 AND id = $2
                RETURNING id
                """

                row = await conn.fetchrow(query, novel_id, entity_id, datetime.utcnow())
                if not row:
                    return StandardResponse(
                        success=False,
                        message="地理实体不存在",
                        error="ENTITY_NOT_FOUND"
                    )

                return StandardResponse(
                    success=True,
                    message="地理实体删除成功"
                )

        except Exception as e:
            return StandardResponse(
                success=False,
                message="删除地理实体失败",
                error=str(e)
            )

    async def query_geographic_entities(self, query: GeographicQuery) -> PaginatedResponse:
        """查询地理实体"""
        try:
            async with get_postgresql_connection() as conn:
                # 构建WHERE条件
                where_conditions = ["e.novel_id = $1", "e.status = 'active'"]
                params = [query.novel_id]
                param_idx = 2

                if query.domain_codes:
                    where_conditions.append(f"e.attributes->>'domain_code' = ANY(${param_idx})")
                    params.append(query.domain_codes)
                    param_idx += 1

                if query.entity_types:
                    where_conditions.append(f"et.name = ANY(${param_idx})")
                    params.append(query.entity_types)
                    param_idx += 1

                if query.region_names:
                    where_conditions.append(f"e.attributes->>'region_name' = ANY(${param_idx})")
                    params.append(query.region_names)
                    param_idx += 1

                if query.min_importance:
                    where_conditions.append(f"e.priority >= ${param_idx}")
                    params.append(query.min_importance)
                    param_idx += 1

                # 总数查询
                count_query = f"""
                SELECT COUNT(*)
                FROM entities e
                JOIN entity_types et ON e.entity_type_id = et.id
                WHERE {' AND '.join(where_conditions)}
                """

                total = await conn.fetchval(count_query, *params)

                # 数据查询
                data_query = f"""
                SELECT e.*, et.name as entity_type_name
                FROM entities e
                JOIN entity_types et ON e.entity_type_id = et.id
                WHERE {' AND '.join(where_conditions)}
                ORDER BY e.priority DESC, e.name
                LIMIT ${param_idx} OFFSET ${param_idx + 1}
                """

                params.extend([query.limit, query.offset])
                rows = await conn.fetch(data_query, *params)

                # 转换为地理实体模型
                entities = []
                for row in rows:
                    entity_type = row['entity_type_name']
                    model_class = self.entity_type_mapping.get(entity_type, GeographicEntity)
                    entity_data = dict(row)
                    entity = model_class(**entity_data)
                    entities.append(entity.dict())

                # 计算分页信息
                page = (query.offset // query.limit) + 1
                has_next = query.offset + query.limit < total
                has_prev = query.offset > 0

                return PaginatedResponse(
                    items=entities,
                    total=total,
                    page=page,
                    page_size=query.limit,
                    has_next=has_next,
                    has_prev=has_prev
                )

        except Exception as e:
            return PaginatedResponse(
                items=[],
                total=0,
                page=1,
                page_size=query.limit,
                has_next=False,
                has_prev=False
            )

    async def get_geographic_hierarchy(self, novel_id: int, domain_code: str) -> StandardResponse:
        """获取地理层级结构"""
        try:
            async with get_postgresql_connection() as conn:
                # 获取域下的所有地理实体
                query = """
                SELECT e.*, et.name as entity_type_name
                FROM entities e
                JOIN entity_types et ON e.entity_type_id = et.id
                WHERE e.novel_id = $1
                  AND e.attributes->>'domain_code' = $2
                  AND e.status = 'active'
                ORDER BY
                  CASE et.name
                    WHEN 'region' THEN 1
                    WHEN 'city' THEN 2
                    WHEN 'town' THEN 3
                    WHEN 'village' THEN 4
                    ELSE 5
                  END,
                  e.priority DESC,
                  e.name
                """

                rows = await conn.fetch(query, novel_id, domain_code)

                # 按类型分组
                entities_by_type = {}
                for row in rows:
                    entity_type = row['entity_type_name']
                    if entity_type not in entities_by_type:
                        entities_by_type[entity_type] = []

                    model_class = self.entity_type_mapping.get(entity_type, GeographicEntity)
                    entity_data = dict(row)
                    entity = model_class(**entity_data)
                    entities_by_type[entity_type].append(entity)

                # 构建层级结构
                hierarchy = GeographicHierarchy(
                    domain=domain_code,
                    entities=[]
                )

                # 添加各类型实体
                for entity_type, entities in entities_by_type.items():
                    hierarchy.entities.extend([entity.dict() for entity in entities])

                return StandardResponse(
                    success=True,
                    message="获取地理层级成功",
                    data=hierarchy.dict()
                )

        except Exception as e:
            return StandardResponse(
                success=False,
                message="获取地理层级失败",
                error=str(e)
            )

    async def get_geographic_summary(self, novel_id: int, domain_code: Optional[str] = None) -> StandardResponse:
        """获取地理数据概要"""
        try:
            async with get_postgresql_connection() as conn:
                # 构建WHERE条件
                where_condition = "e.novel_id = $1 AND e.status = 'active'"
                params = [novel_id]

                if domain_code:
                    where_condition += " AND e.attributes->>'domain_code' = $2"
                    params.append(domain_code)

                # 统计查询
                query = f"""
                SELECT
                  et.name as entity_type,
                  COUNT(*) as count
                FROM entities e
                JOIN entity_types et ON e.entity_type_id = et.id
                WHERE {where_condition}
                  AND et.name IN ('region', 'city', 'town', 'village', 'landmark', 'building', 'natural_feature', 'infrastructure')
                GROUP BY et.name
                """

                rows = await conn.fetch(query, *params)

                # 构建统计信息
                stats = {
                    'total_regions': 0,
                    'total_cities': 0,
                    'total_towns': 0,
                    'total_villages': 0,
                    'total_landmarks': 0,
                    'total_buildings': 0,
                    'total_natural_features': 0,
                    'total_infrastructure': 0
                }

                for row in rows:
                    entity_type = row['entity_type']
                    count = row['count']
                    stats[f'total_{entity_type}s'] = count

                summary = GeographicSummary(
                    novel_id=novel_id,
                    domain_code=domain_code or 'all',
                    **stats
                )

                return StandardResponse(
                    success=True,
                    message="获取地理概要成功",
                    data=summary.dict()
                )

        except Exception as e:
            return StandardResponse(
                success=False,
                message="获取地理概要失败",
                error=str(e)
            )

    async def create_geographic_relationship(self, request: CreateGeographicRelationshipRequest) -> StandardResponse:
        """创建地理关系"""
        try:
            async with get_postgresql_connection() as conn:
                # 检查实体是否存在
                entity_check_query = """
                SELECT COUNT(*) FROM entities
                WHERE novel_id = $1 AND id = ANY($2) AND status = 'active'
                """

                entity_count = await conn.fetchval(
                    entity_check_query,
                    request.novel_id,
                    [request.source_entity_id, request.target_entity_id]
                )

                if entity_count != 2:
                    return StandardResponse(
                        success=False,
                        message="源实体或目标实体不存在",
                        error="ENTITY_NOT_FOUND"
                    )

                # 创建关系
                query = """
                INSERT INTO entity_relationships (
                    novel_id, source_entity_id, target_entity_id, relationship_type,
                    attributes, strength, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
                """

                attributes = {
                    'distance': request.distance,
                    'travel_time': request.travel_time,
                    'difficulty': request.difficulty,
                    'importance': request.importance
                }

                row = await conn.fetchrow(
                    query, request.novel_id, request.source_entity_id, request.target_entity_id,
                    request.relationship_type.value, attributes, request.strength, datetime.utcnow()
                )

                return StandardResponse(
                    success=True,
                    message="地理关系创建成功",
                    data={"relationship_id": row['id']}
                )

        except Exception as e:
            return StandardResponse(
                success=False,
                message="创建地理关系失败",
                error=str(e)
            )

    async def import_geographic_data(self, data: GeographicDataImport) -> StandardResponse:
        """批量导入地理数据"""
        try:
            from .migrations.init_geographic_data import GeographicDataInitializer

            # 准备数据格式
            domain_data = {
                'regions': data.regions,
                'cities': data.cities,
                'towns': data.towns,
                'villages': data.villages,
                'landmarks': data.landmarks,
                'buildings': data.buildings,
                'natural_features': data.natural_features,
                'infrastructure': data.infrastructure
            }

            # 初始化数据
            initializer = GeographicDataInitializer(data.novel_id)

            async with get_postgresql_connection() as conn:
                await initializer._initialize_domain_data(conn, data.domain_code, domain_data)

            return StandardResponse(
                success=True,
                message=f"域 {data.domain_code} 的地理数据导入成功"
            )

        except Exception as e:
            return StandardResponse(
                success=False,
                message="导入地理数据失败",
                error=str(e)
            )

    # =============================================================================
    # 剧情功能映射相关方法
    # =============================================================================

    async def query_plot_functions(self, query: PlotFunctionQuery) -> PlotFunctionQueryResponse:
        """查询剧情功能"""
        try:
            async with get_postgresql_connection() as conn:
                # 构建WHERE条件
                where_conditions = ["gpcv.novel_id = $1"]
                params = [query.novel_id]
                param_idx = 2

                # 功能代码筛选
                if query.function_codes:
                    where_conditions.append(f"gpcv.function_codes && ${param_idx}")
                    params.append(query.function_codes)
                    param_idx += 1

                # 节点代码筛选
                if query.node_codes:
                    where_conditions.append(f"gpcv.node_codes && ${param_idx}")
                    params.append(query.node_codes)
                    param_idx += 1

                # 域代码筛选
                if query.domain_codes:
                    where_conditions.append(f"gpcv.domain_code = ANY(${param_idx})")
                    params.append(query.domain_codes)
                    param_idx += 1

                # 实体类型筛选
                if query.entity_types:
                    where_conditions.append(f"gpcv.entity_type = ANY(${param_idx})")
                    params.append(query.entity_types)
                    param_idx += 1

                # 区域筛选
                if query.region_names:
                    where_conditions.append(f"gpcv.region_name = ANY(${param_idx})")
                    params.append(query.region_names)
                    param_idx += 1

                # 戏剧性水平筛选
                if query.min_drama_level is not None:
                    where_conditions.append(f"gpcv.hook_drama_level >= ${param_idx}")
                    params.append(query.min_drama_level)
                    param_idx += 1

                if query.max_drama_level is not None:
                    where_conditions.append(f"gpcv.hook_drama_level <= ${param_idx}")
                    params.append(query.max_drama_level)
                    param_idx += 1

                # 难度等级筛选
                if query.min_difficulty is not None:
                    where_conditions.append(f"gpcv.difficulty_level >= ${param_idx}")
                    params.append(query.min_difficulty)
                    param_idx += 1

                if query.max_difficulty is not None:
                    where_conditions.append(f"gpcv.difficulty_level <= ${param_idx}")
                    params.append(query.max_difficulty)
                    param_idx += 1

                # 紧急程度筛选
                if query.urgency_levels:
                    where_conditions.append(f"gpcv.hook_urgency = ANY(${param_idx})")
                    params.append(query.urgency_levels)
                    param_idx += 1

                # 使用状态筛选
                if query.max_usage_count is not None:
                    where_conditions.append(f"gpcv.usage_count <= ${param_idx}")
                    params.append(query.max_usage_count)
                    param_idx += 1

                if query.unused_only:
                    where_conditions.append("gpcv.usage_count = 0")

                # 功能分类筛选
                if query.categories:
                    category_codes = []
                    for category in query.categories:
                        func_query = "SELECT code FROM plot_function_types WHERE category = $1"
                        rows = await conn.fetch(func_query, category.value)
                        category_codes.extend([row['code'] for row in rows])

                    if category_codes:
                        where_conditions.append(f"gpcv.function_codes && ${param_idx}")
                        params.append(category_codes)
                        param_idx += 1

                # 确保有剧情映射数据
                where_conditions.append("gpcv.function_codes IS NOT NULL")
                where_conditions.append("array_length(gpcv.function_codes, 1) > 0")

                # 总数查询
                count_query = f"""
                SELECT COUNT(*)
                FROM geographic_plot_complete_view gpcv
                WHERE {' AND '.join(where_conditions)}
                """

                total = await conn.fetchval(count_query, *params)

                # 排序字段映射
                sort_field_mapping = {
                    'hook_drama_level': 'gpcv.hook_drama_level',
                    'difficulty_level': 'gpcv.difficulty_level',
                    'hook_urgency': 'gpcv.hook_urgency',
                    'usage_count': 'gpcv.usage_count',
                    'entity_name': 'gpcv.entity_name',
                    'created_at': 'gpcv.created_at'
                }

                sort_field = sort_field_mapping.get(query.sort_by, 'gpcv.hook_drama_level')
                sort_order = 'DESC' if query.sort_desc else 'ASC'

                # 数据查询
                data_query = f"""
                SELECT gpcv.*
                FROM geographic_plot_complete_view gpcv
                WHERE {' AND '.join(where_conditions)}
                ORDER BY {sort_field} {sort_order}, gpcv.entity_name
                LIMIT ${param_idx} OFFSET ${param_idx + 1}
                """

                params.extend([query.limit, query.offset])
                rows = await conn.fetch(data_query, *params)

                # 转换为模型
                items = []
                function_dist = {}
                node_dist = {}
                total_drama = 0
                total_difficulty = 0
                valid_count = 0

                for row in rows:
                    item_data = dict(row)

                    # 处理空值
                    for field in ['function_codes', 'node_codes', 'function_names', 'node_names']:
                        if item_data.get(field) is None:
                            item_data[field] = []

                    item = GeographicPlotView(**item_data)
                    items.append(item)

                    # 统计功能分布
                    for func_code in item.function_codes:
                        function_dist[func_code] = function_dist.get(func_code, 0) + 1

                    # 统计节点分布
                    for node_code in item.node_codes:
                        node_dist[node_code] = node_dist.get(node_code, 0) + 1

                    # 累计统计
                    total_drama += item.hook_drama_level
                    total_difficulty += item.difficulty_level
                    valid_count += 1

                # 计算分页信息
                page = (query.offset // query.limit) + 1
                has_next = query.offset + query.limit < total
                has_prev = query.offset > 0

                # 计算平均值
                avg_drama = total_drama / valid_count if valid_count > 0 else 0.0
                avg_difficulty = total_difficulty / valid_count if valid_count > 0 else 0.0

                return PlotFunctionQueryResponse(
                    items=items,
                    total=total,
                    page=page,
                    page_size=query.limit,
                    has_next=has_next,
                    has_prev=has_prev,
                    function_distribution=function_dist,
                    node_distribution=node_dist,
                    avg_drama_level=round(avg_drama, 2),
                    avg_difficulty_level=round(avg_difficulty, 2)
                )

        except Exception as e:
            return PlotFunctionQueryResponse(
                items=[],
                total=0,
                page=1,
                page_size=query.limit,
                has_next=False,
                has_prev=False,
                function_distribution={},
                node_distribution={},
                avg_drama_level=0.0,
                avg_difficulty_level=0.0
            )

    async def create_plot_mapping(self, request: CreatePlotMappingRequest) -> StandardResponse:
        """创建剧情映射"""
        try:
            async with get_postgresql_connection() as conn:
                # 检查实体是否存在
                entity_check = await conn.fetchrow(
                    "SELECT id FROM entities WHERE novel_id = $1 AND id = $2 AND status = 'active'",
                    request.novel_id, request.entity_id
                )
                if not entity_check:
                    return StandardResponse(
                        success=False,
                        message="地理实体不存在",
                        error="ENTITY_NOT_FOUND"
                    )

                # 检查是否已存在映射
                existing = await conn.fetchrow(
                    "SELECT id FROM geographic_plot_mappings WHERE novel_id = $1 AND entity_id = $2",
                    request.novel_id, request.entity_id
                )
                if existing:
                    return StandardResponse(
                        success=False,
                        message="该实体已存在剧情映射",
                        error="MAPPING_EXISTS"
                    )

                # 创建主映射记录
                mapping_query = """
                INSERT INTO geographic_plot_mappings (
                    novel_id, entity_id, function_codes, node_codes,
                    hook_title, hook_description, hook_urgency, hook_drama_level,
                    difficulty_level, conflict_types, emotional_tags, required_conditions,
                    created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                RETURNING id
                """

                now = datetime.utcnow()
                mapping_row = await conn.fetchrow(
                    mapping_query,
                    request.novel_id, request.entity_id, request.function_codes, request.node_codes,
                    request.hook_title, request.hook_description, request.hook_urgency,
                    request.hook_drama_level, request.difficulty_level, request.conflict_types,
                    request.emotional_tags, request.required_conditions, now, now
                )

                mapping_id = mapping_row['id']

                # 如果有详细设定，创建详情记录
                if request.background_context or request.escalation_paths or request.resolution_options:
                    detail_query = """
                    INSERT INTO plot_hook_details (
                        mapping_id, novel_id, background_context, escalation_paths,
                        resolution_options, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """

                    await conn.execute(
                        detail_query,
                        mapping_id, request.novel_id, request.background_context,
                        request.escalation_paths, request.resolution_options, now, now
                    )

                return StandardResponse(
                    success=True,
                    message="剧情映射创建成功",
                    data={"mapping_id": mapping_id}
                )

        except Exception as e:
            return StandardResponse(
                success=False,
                message="创建剧情映射失败",
                error=str(e)
            )

    async def update_plot_mapping(self, novel_id: int, entity_id: int,
                                request: UpdatePlotMappingRequest) -> StandardResponse:
        """更新剧情映射"""
        try:
            async with get_postgresql_connection() as conn:
                # 构建更新字段
                update_fields = []
                params = [novel_id, entity_id]
                param_idx = 3

                if request.function_codes is not None:
                    update_fields.append(f"function_codes = ${param_idx}")
                    params.append(request.function_codes)
                    param_idx += 1

                if request.node_codes is not None:
                    update_fields.append(f"node_codes = ${param_idx}")
                    params.append(request.node_codes)
                    param_idx += 1

                if request.hook_title is not None:
                    update_fields.append(f"hook_title = ${param_idx}")
                    params.append(request.hook_title)
                    param_idx += 1

                if request.hook_description is not None:
                    update_fields.append(f"hook_description = ${param_idx}")
                    params.append(request.hook_description)
                    param_idx += 1

                if request.hook_urgency is not None:
                    update_fields.append(f"hook_urgency = ${param_idx}")
                    params.append(request.hook_urgency)
                    param_idx += 1

                if request.hook_drama_level is not None:
                    update_fields.append(f"hook_drama_level = ${param_idx}")
                    params.append(request.hook_drama_level)
                    param_idx += 1

                if request.difficulty_level is not None:
                    update_fields.append(f"difficulty_level = ${param_idx}")
                    params.append(request.difficulty_level)
                    param_idx += 1

                if request.conflict_types is not None:
                    update_fields.append(f"conflict_types = ${param_idx}")
                    params.append(request.conflict_types)
                    param_idx += 1

                if request.emotional_tags is not None:
                    update_fields.append(f"emotional_tags = ${param_idx}")
                    params.append(request.emotional_tags)
                    param_idx += 1

                if request.is_active is not None:
                    update_fields.append(f"is_active = ${param_idx}")
                    params.append(request.is_active)
                    param_idx += 1

                if not update_fields:
                    return StandardResponse(
                        success=False,
                        message="没有提供更新字段",
                        error="NO_UPDATE_FIELDS"
                    )

                update_fields.append(f"updated_at = ${param_idx}")
                params.append(datetime.utcnow())

                query = f"""
                UPDATE geographic_plot_mappings
                SET {', '.join(update_fields)}
                WHERE novel_id = $1 AND entity_id = $2
                RETURNING id
                """

                row = await conn.fetchrow(query, *params)
                if not row:
                    return StandardResponse(
                        success=False,
                        message="剧情映射不存在",
                        error="MAPPING_NOT_FOUND"
                    )

                return StandardResponse(
                    success=True,
                    message="剧情映射更新成功"
                )

        except Exception as e:
            return StandardResponse(
                success=False,
                message="更新剧情映射失败",
                error=str(e)
            )

    async def record_plot_usage(self, request: RecordPlotUsageRequest) -> StandardResponse:
        """记录剧情使用"""
        try:
            async with get_postgresql_connection() as conn:
                # 检查映射是否存在
                mapping_check = await conn.fetchrow(
                    "SELECT id FROM geographic_plot_mappings WHERE novel_id = $1 AND id = $2",
                    request.novel_id, request.mapping_id
                )
                if not mapping_check:
                    return StandardResponse(
                        success=False,
                        message="剧情映射不存在",
                        error="MAPPING_NOT_FOUND"
                    )

                # 记录使用情况
                usage_query = """
                INSERT INTO plot_function_usage (
                    novel_id, mapping_id, used_in_chapter, function_codes_used,
                    node_codes_used, player_choices, outcome_achieved, impact_level,
                    session_id, notes, used_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                RETURNING id
                """

                usage_row = await conn.fetchrow(
                    usage_query,
                    request.novel_id, request.mapping_id, request.used_in_chapter,
                    request.function_codes_used, request.node_codes_used,
                    request.player_choices, request.outcome_achieved, request.impact_level,
                    request.session_id, request.notes, datetime.utcnow()
                )

                return StandardResponse(
                    success=True,
                    message="使用记录创建成功",
                    data={"usage_id": usage_row['id']}
                )

        except Exception as e:
            return StandardResponse(
                success=False,
                message="记录使用失败",
                error=str(e)
            )

    async def get_plot_function_stats(self, novel_id: int) -> StandardResponse:
        """获取剧情功能统计"""
        try:
            async with get_postgresql_connection() as conn:
                query = """
                SELECT * FROM plot_function_stats_view
                WHERE novel_id = $1
                ORDER BY total_usage_count DESC, avg_drama_level DESC
                """

                rows = await conn.fetch(query, novel_id)
                stats = [PlotFunctionStats(**dict(row)) for row in rows]

                return StandardResponse(
                    success=True,
                    message="获取统计信息成功",
                    data=[stat.dict() for stat in stats]
                )

        except Exception as e:
            return StandardResponse(
                success=False,
                message="获取统计信息失败",
                error=str(e)
            )

    async def batch_import_plot_mappings(self, data: BatchPlotMappingImport) -> StandardResponse:
        """批量导入剧情映射"""
        try:
            async with get_postgresql_connection() as conn:
                created_count = 0
                updated_count = 0
                error_count = 0
                errors = []

                for mapping_data in data.mappings:
                    try:
                        # 查找实体ID
                        entity_query = """
                        SELECT e.id FROM entities e
                        JOIN entity_types et ON e.entity_type_id = et.id
                        WHERE e.novel_id = $1 AND e.name = $2 AND et.name = $3
                          AND e.attributes->>'domain_code' = $4 AND e.status = 'active'
                        """

                        entity_row = await conn.fetchrow(
                            entity_query, data.novel_id, mapping_data.entity_name,
                            mapping_data.entity_type, mapping_data.domain_code
                        )

                        if not entity_row:
                            errors.append(f"实体不存在: {mapping_data.entity_name}")
                            error_count += 1
                            continue

                        entity_id = entity_row['id']

                        # 检查是否已存在映射
                        existing = await conn.fetchrow(
                            "SELECT id FROM geographic_plot_mappings WHERE novel_id = $1 AND entity_id = $2",
                            data.novel_id, entity_id
                        )

                        now = datetime.utcnow()

                        if existing and data.overwrite_existing:
                            # 更新现有映射
                            update_query = """
                            UPDATE geographic_plot_mappings SET
                                function_codes = $3, node_codes = $4, hook_title = $5,
                                hook_description = $6, hook_urgency = $7, hook_drama_level = $8,
                                difficulty_level = $9, updated_at = $10
                            WHERE novel_id = $1 AND entity_id = $2
                            """

                            await conn.execute(
                                update_query, data.novel_id, entity_id,
                                mapping_data.function_codes, mapping_data.node_codes,
                                mapping_data.hook_title, mapping_data.hook_description,
                                mapping_data.hook_urgency, mapping_data.hook_drama_level,
                                mapping_data.difficulty_level, now
                            )
                            updated_count += 1

                        elif not existing:
                            # 创建新映射
                            insert_query = """
                            INSERT INTO geographic_plot_mappings (
                                novel_id, entity_id, function_codes, node_codes,
                                hook_title, hook_description, hook_urgency, hook_drama_level,
                                difficulty_level, created_at, updated_at
                            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                            """

                            await conn.execute(
                                insert_query, data.novel_id, entity_id,
                                mapping_data.function_codes, mapping_data.node_codes,
                                mapping_data.hook_title, mapping_data.hook_description,
                                mapping_data.hook_urgency, mapping_data.hook_drama_level,
                                mapping_data.difficulty_level, now, now
                            )
                            created_count += 1

                        else:
                            errors.append(f"映射已存在且未设置覆盖: {mapping_data.entity_name}")
                            error_count += 1

                    except Exception as e:
                        errors.append(f"处理 {mapping_data.entity_name} 时出错: {str(e)}")
                        error_count += 1

                return StandardResponse(
                    success=True,
                    message=f"批量导入完成: 创建{created_count}个, 更新{updated_count}个, 错误{error_count}个",
                    data={
                        "created_count": created_count,
                        "updated_count": updated_count,
                        "error_count": error_count,
                        "errors": errors
                    }
                )

        except Exception as e:
            return StandardResponse(
                success=False,
                message="批量导入失败",
                error=str(e)
            )

    # 私有辅助方法

    async def _get_entity_type_id(self, conn, entity_type: str, novel_id: int) -> Optional[int]:
        """获取实体类型ID"""
        query = "SELECT id FROM entity_types WHERE novel_id = $1 AND name = $2"
        row = await conn.fetchrow(query, novel_id, entity_type)
        return row['id'] if row else None

    async def _create_parent_child_relationship(self, conn, novel_id: int, parent_id: int, child_id: int):
        """创建父子关系"""
        query = """
        INSERT INTO entity_relationships (novel_id, source_entity_id, target_entity_id, relationship_type, strength, created_at)
        VALUES ($1, $2, $3, 'contains', 8, $4)
        """
        await conn.execute(query, novel_id, parent_id, child_id, datetime.utcnow())


# 创建服务实例
geographic_service = GeographicService()