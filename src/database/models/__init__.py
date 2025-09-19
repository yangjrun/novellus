"""
裂世九域·法则链纪元 数据模型
定义所有数据结构和验证规则
"""

from .core_models import *
from .worldbuilding_models import *
from .content_models import *
from .character_models import *

__all__ = [
    # 核心模型
    'Project',
    'Novel',
    'ContentBatch',
    'ContentSegment',

    # Create/Update模型
    'ProjectCreate',
    'ProjectUpdate',
    'NovelCreate',
    'NovelUpdate',
    'ContentBatchCreate',
    'ContentBatchUpdate',
    'ContentSegmentCreate',
    'ContentSegmentUpdate',
    'DomainCreate',
    'DomainUpdate',
    'CultivationSystemCreate',
    'CultivationStageCreate',
    'PowerOrganizationCreate',
    'LawChainCreate',
    'ChainMarkCreate',
    'CharacterCreate',
    'LocationCreate',
    'ItemCreate',
    'EventCreate',
    'KnowledgeBaseCreate',

    # 世界观模型
    'Domain',
    'CultivationSystem',
    'CultivationStage',
    'PowerOrganization',
    'LawChain',
    'ChainMark',

    # 内容模型
    'Character',
    'Location',
    'Item',
    'Event',
    'KnowledgeBase',

    # 枚举类型
    'ProjectStatus',
    'NovelStatus',
    'BatchType',
    'BatchStatus',
    'SegmentType',
    'SegmentStatus',
    'DomainType',
    'CultivationStageType',
    'OrganizationType',
    'CharacterType',
    'LocationType',
    'ItemType',
    'ItemRarity',
    'EventType',
    'EventStatus',
    'KnowledgeCategory',
]