"""
数据库迁移和初始化模块
包含数据库初始化、角色版本生命周期管理等功能
"""

from .init_mongodb import *
from .init_character_system import (
    init_character_system,
    init_character_system_sync,
    CharacterSystemInitializer,
    SyncCharacterSystemInitializer
)
from .character_lifecycle_manager import (
    CharacterLifecycleManager,
    create_character_version,
    get_character_timeline,
    CharacterEssence,
    CharacterManifestation,
    ChangeType,
    RelationshipTransition
)

# 保持向后兼容（已弃用的迁移功能）
try:
    from .character_data_migration import (
        CharacterDataMigrator,
        migrate_character_to_domain,
        sync_all_character_data
    )
    _MIGRATION_LEGACY_AVAILABLE = True
except ImportError:
    _MIGRATION_LEGACY_AVAILABLE = False

__all__ = [
    # 原有功能
    "init_mongodb", "MongoDBInitializer",

    # 角色系统初始化功能
    'init_character_system',
    'init_character_system_sync',
    'CharacterSystemInitializer',
    'SyncCharacterSystemInitializer',

    # 新的智能角色版本生命周期管理
    'CharacterLifecycleManager',
    'create_character_version',
    'get_character_timeline',
    'CharacterEssence',
    'CharacterManifestation',
    'ChangeType',
    'RelationshipTransition',
]

# 向后兼容的遗留功能（如果可用）
if _MIGRATION_LEGACY_AVAILABLE:
    __all__.extend([
        'CharacterDataMigrator',
        'migrate_character_to_domain',
        'sync_all_character_data'
    ])

# 测试功能
from .test_character_system import (
    CharacterSystemIntegrationTest,
    run_integration_tests
)

__all__.extend([
    'CharacterSystemIntegrationTest',
    'run_integration_tests'
])