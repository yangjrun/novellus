"""
Incremental Processor for Novel Content Management

Advanced incremental processing system including:
- Change data capture (CDC) from multiple sources
- Intelligent delta detection and processing
- Data versioning and lineage tracking
- Conflict resolution and consistency guarantees
- Efficient merging and upsert operations
- Cross-database synchronization
"""

import asyncio
import logging
import hashlib
import json
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid
from collections import defaultdict

from database.connections.postgresql import postgres_db
from database.connections.mongodb import mongodb
from .pipeline_manager import ContentType
from .entity_extractor import ExtractedEntity

logger = logging.getLogger(__name__)


class ChangeType(Enum):
    """Types of data changes."""
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    MERGE = "merge"


class ConflictResolutionStrategy(Enum):
    """Strategies for resolving data conflicts."""
    LATEST_WINS = "latest_wins"
    HIGHEST_CONFIDENCE = "highest_confidence"
    MANUAL_REVIEW = "manual_review"
    MERGE_FIELDS = "merge_fields"
    PRESERVE_ORIGINAL = "preserve_original"


@dataclass
class DataVersion:
    """Represents a version of data."""
    version_id: str
    content_hash: str
    timestamp: datetime
    author: str
    changes: Dict[str, Any]
    parent_version: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChangeRecord:
    """Records a change in the system."""
    change_id: str
    change_type: ChangeType
    table_name: str
    record_id: str
    old_data: Optional[Dict[str, Any]]
    new_data: Optional[Dict[str, Any]]
    timestamp: datetime
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConflictRecord:
    """Records a data conflict."""
    conflict_id: str
    table_name: str
    record_id: str
    field_name: str
    local_value: Any
    remote_value: Any
    local_timestamp: datetime
    remote_timestamp: datetime
    resolution_strategy: ConflictResolutionStrategy
    resolved: bool = False
    resolved_value: Any = None
    resolved_at: Optional[datetime] = None


class DataConsistencyManager:
    """Manages data consistency across different storage systems."""

    def __init__(self):
        self.consistency_rules = self._initialize_consistency_rules()
        self.cross_references = defaultdict(set)

    def _initialize_consistency_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize data consistency rules."""
        return {
            'character_references': {
                'postgres_table': 'processed_character',
                'mongodb_collection': 'processed_character',
                'key_fields': ['canonical_name', 'entity_type'],
                'sync_fields': ['aliases', 'relationships', 'confidence']
            },
            'location_references': {
                'postgres_table': 'processed_scene',
                'mongodb_collection': 'processed_scene',
                'key_fields': ['canonical_name', 'entity_type'],
                'sync_fields': ['aliases', 'relationships', 'confidence']
            },
            'entity_relationships': {
                'check_bidirectional': True,
                'validate_references': True,
                'orphan_cleanup': True
            }
        }

    async def validate_consistency(self, table_name: str, record_id: str) -> List[str]:
        """Validate data consistency for a specific record."""
        issues = []

        if table_name in self.consistency_rules:
            rule = self.consistency_rules[table_name]

            # Check PostgreSQL vs MongoDB consistency
            if 'mongodb_collection' in rule:
                issues.extend(await self._check_cross_db_consistency(
                    rule['postgres_table'], rule['mongodb_collection'], record_id, rule
                ))

        # Check entity relationships
        if 'entity_relationships' in self.consistency_rules:
            issues.extend(await self._check_relationship_consistency(table_name, record_id))

        return issues

    async def _check_cross_db_consistency(self,
                                        postgres_table: str,
                                        mongo_collection: str,
                                        record_id: str,
                                        rule: Dict[str, Any]) -> List[str]:
        """Check consistency between PostgreSQL and MongoDB."""
        issues = []

        try:
            # Get PostgreSQL record
            pg_query = f"SELECT * FROM {postgres_table} WHERE original_id = $1"
            pg_records = await postgres_db.execute_query(pg_query, (record_id,))
            pg_record = pg_records[0] if pg_records else None

            # Get MongoDB record
            mongo_record = await mongodb.find_one(mongo_collection, {"original_id": record_id})

            if pg_record and mongo_record:
                # Check key fields consistency
                for field in rule['key_fields']:
                    pg_value = pg_record.get(field)
                    mongo_value = mongo_record.get(field)

                    if pg_value != mongo_value:
                        issues.append(f"Inconsistent {field}: PostgreSQL='{pg_value}', MongoDB='{mongo_value}'")

            elif pg_record and not mongo_record:
                issues.append(f"Record exists in PostgreSQL but not in MongoDB")
            elif mongo_record and not pg_record:
                issues.append(f"Record exists in MongoDB but not in PostgreSQL")

        except Exception as e:
            issues.append(f"Error checking cross-database consistency: {str(e)}")

        return issues

    async def _check_relationship_consistency(self, table_name: str, record_id: str) -> List[str]:
        """Check entity relationship consistency."""
        issues = []

        # This would implement relationship validation logic
        # For example, checking if referenced entities exist

        return issues


class IncrementalProcessor:
    """
    Advanced incremental processing system for novel content.

    Features:
    - Change data capture from multiple sources
    - Intelligent delta detection using content hashing
    - Data versioning with lineage tracking
    - Conflict detection and resolution
    - Cross-database synchronization
    - Consistency validation and repair
    """

    def __init__(self):
        self.change_log: List[ChangeRecord] = []
        self.version_store: Dict[str, List[DataVersion]] = defaultdict(list)
        self.conflict_store: List[ConflictRecord] = []
        self.consistency_manager = DataConsistencyManager()

        # Caches for performance
        self.content_hash_cache: Dict[str, str] = {}
        self.last_sync_timestamps: Dict[str, datetime] = {}

        # Configuration
        self.max_version_history = 100
        self.conflict_resolution_strategy = ConflictResolutionStrategy.LATEST_WINS

        logger.info("IncrementalProcessor initialized")

    async def process_incremental_update(self,
                                       content_type: ContentType,
                                       record_id: str,
                                       new_data: Dict[str, Any],
                                       source: str = "manual") -> Dict[str, Any]:
        """
        Process an incremental update to existing data.

        Args:
            content_type: Type of content being updated
            record_id: Unique identifier for the record
            new_data: New data to be applied
            source: Source of the update

        Returns:
            Dictionary with update results and metadata
        """
        start_time = datetime.now()

        try:
            # 1. Retrieve existing data
            existing_data = await self._get_existing_data(content_type, record_id)

            # 2. Calculate content hash for change detection
            new_content_hash = self._calculate_content_hash(new_data)
            existing_hash = existing_data.get('content_hash') if existing_data else None

            # 3. Check if data actually changed
            if existing_hash == new_content_hash:
                logger.debug(f"No changes detected for {record_id}")
                return {
                    'status': 'no_change',
                    'record_id': record_id,
                    'processing_time': (datetime.now() - start_time).total_seconds()
                }

            # 4. Detect conflicts
            conflicts = await self._detect_conflicts(content_type, record_id, new_data, existing_data)

            # 5. Resolve conflicts if any
            if conflicts:
                resolved_data = await self._resolve_conflicts(conflicts, new_data, existing_data)
            else:
                resolved_data = new_data

            # 6. Create version record
            version = await self._create_version(record_id, resolved_data, existing_data, source)

            # 7. Determine change type
            change_type = ChangeType.UPDATE if existing_data else ChangeType.INSERT

            # 8. Apply changes to databases
            apply_results = await self._apply_changes(
                content_type, record_id, resolved_data, existing_data, change_type
            )

            # 9. Update version store and change log
            await self._record_change(change_type, content_type, record_id, existing_data, resolved_data, source)
            await self._store_version(record_id, version)

            # 10. Validate consistency
            consistency_issues = await self.consistency_manager.validate_consistency(
                self._get_table_name(content_type), record_id
            )

            # 11. Update caches
            self.content_hash_cache[record_id] = new_content_hash
            self.last_sync_timestamps[record_id] = datetime.now()

            processing_time = (datetime.now() - start_time).total_seconds()

            result = {
                'status': 'success',
                'change_type': change_type.value,
                'record_id': record_id,
                'version_id': version.version_id,
                'conflicts_detected': len(conflicts),
                'conflicts_resolved': len([c for c in conflicts if c.resolved]),
                'consistency_issues': consistency_issues,
                'apply_results': apply_results,
                'processing_time': processing_time
            }

            logger.info(f"Incremental update completed for {record_id}: {change_type.value}")
            return result

        except Exception as e:
            logger.error(f"Incremental update failed for {record_id}: {e}")
            return {
                'status': 'error',
                'record_id': record_id,
                'error': str(e),
                'processing_time': (datetime.now() - start_time).total_seconds()
            }

    async def _get_existing_data(self, content_type: ContentType, record_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve existing data for a record."""
        table_name = self._get_table_name(content_type)

        # Try PostgreSQL first
        try:
            query = f"SELECT * FROM {table_name} WHERE original_id = $1"
            records = await postgres_db.execute_query(query, (record_id,))
            if records:
                return records[0]
        except Exception as e:
            logger.warning(f"Failed to retrieve from PostgreSQL: {e}")

        # Try MongoDB as fallback
        try:
            collection_name = self._get_collection_name(content_type)
            record = await mongodb.find_one(collection_name, {"original_id": record_id})
            if record:
                return record
        except Exception as e:
            logger.warning(f"Failed to retrieve from MongoDB: {e}")

        return None

    def _calculate_content_hash(self, data: Dict[str, Any]) -> str:
        """Calculate a hash of the content for change detection."""
        # Remove metadata fields that shouldn't affect the hash
        hashable_data = {k: v for k, v in data.items()
                        if k not in ['processed_at', 'pipeline_version', 'content_hash', 'version_id']}

        # Create stable hash
        content_str = json.dumps(hashable_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content_str.encode('utf-8')).hexdigest()

    async def _detect_conflicts(self,
                               content_type: ContentType,
                               record_id: str,
                               new_data: Dict[str, Any],
                               existing_data: Optional[Dict[str, Any]]) -> List[ConflictRecord]:
        """Detect conflicts between new and existing data."""
        conflicts = []

        if not existing_data:
            return conflicts

        # Check timestamp-based conflicts
        new_timestamp = new_data.get('processed_at')
        existing_timestamp = existing_data.get('processed_at')

        if new_timestamp and existing_timestamp:
            try:
                new_dt = datetime.fromisoformat(new_timestamp.replace('Z', '+00:00'))
                existing_dt = datetime.fromisoformat(existing_timestamp.replace('Z', '+00:00'))

                # Check if we're trying to apply an older update
                if new_dt < existing_dt:
                    conflicts.append(ConflictRecord(
                        conflict_id=str(uuid.uuid4()),
                        table_name=self._get_table_name(content_type),
                        record_id=record_id,
                        field_name='processed_at',
                        local_value=existing_timestamp,
                        remote_value=new_timestamp,
                        local_timestamp=existing_dt,
                        remote_timestamp=new_dt,
                        resolution_strategy=self.conflict_resolution_strategy
                    ))
            except ValueError:
                pass  # Invalid timestamp format, skip conflict detection

        # Check field-level conflicts for important fields
        conflict_fields = ['cleaned_content', 'entities', 'confidence']

        for field in conflict_fields:
            if field in new_data and field in existing_data:
                if new_data[field] != existing_data[field]:
                    conflicts.append(ConflictRecord(
                        conflict_id=str(uuid.uuid4()),
                        table_name=self._get_table_name(content_type),
                        record_id=record_id,
                        field_name=field,
                        local_value=existing_data[field],
                        remote_value=new_data[field],
                        local_timestamp=existing_dt if 'existing_dt' in locals() else datetime.now(),
                        remote_timestamp=new_dt if 'new_dt' in locals() else datetime.now(),
                        resolution_strategy=self.conflict_resolution_strategy
                    ))

        return conflicts

    async def _resolve_conflicts(self,
                               conflicts: List[ConflictRecord],
                               new_data: Dict[str, Any],
                               existing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve detected conflicts based on resolution strategy."""
        resolved_data = new_data.copy()

        for conflict in conflicts:
            if conflict.resolution_strategy == ConflictResolutionStrategy.LATEST_WINS:
                # Use the value from the more recent timestamp
                if conflict.remote_timestamp > conflict.local_timestamp:
                    resolved_value = conflict.remote_value
                else:
                    resolved_value = conflict.local_value

            elif conflict.resolution_strategy == ConflictResolutionStrategy.HIGHEST_CONFIDENCE:
                # For entity data, use highest confidence
                if conflict.field_name == 'entities':
                    resolved_value = self._merge_entities_by_confidence(
                        conflict.local_value, conflict.remote_value
                    )
                else:
                    resolved_value = conflict.remote_value

            elif conflict.resolution_strategy == ConflictResolutionStrategy.MERGE_FIELDS:
                # Intelligent field merging
                resolved_value = self._merge_field_values(
                    conflict.field_name, conflict.local_value, conflict.remote_value
                )

            elif conflict.resolution_strategy == ConflictResolutionStrategy.PRESERVE_ORIGINAL:
                resolved_value = conflict.local_value

            else:  # MANUAL_REVIEW
                # Store for manual review, use remote value for now
                resolved_value = conflict.remote_value
                conflict.resolved = False
                self.conflict_store.append(conflict)
                continue

            # Apply resolution
            resolved_data[conflict.field_name] = resolved_value
            conflict.resolved_value = resolved_value
            conflict.resolved = True
            conflict.resolved_at = datetime.now()

        return resolved_data

    def _merge_entities_by_confidence(self, local_entities: List[Dict], remote_entities: List[Dict]) -> List[Dict]:
        """Merge entity lists based on confidence scores."""
        entity_map = {}

        # Process local entities
        for entity in local_entities:
            key = (entity.get('canonical_name'), entity.get('entity_type'))
            entity_map[key] = entity

        # Merge remote entities
        for entity in remote_entities:
            key = (entity.get('canonical_name'), entity.get('entity_type'))
            if key in entity_map:
                # Keep the one with higher confidence
                if entity.get('confidence', 0) > entity_map[key].get('confidence', 0):
                    entity_map[key] = entity
            else:
                entity_map[key] = entity

        return list(entity_map.values())

    def _merge_field_values(self, field_name: str, local_value: Any, remote_value: Any) -> Any:
        """Merge field values intelligently based on field type."""
        if field_name == 'aliases' and isinstance(local_value, list) and isinstance(remote_value, list):
            # Merge alias lists
            return list(set(local_value + remote_value))

        elif field_name == 'relationships' and isinstance(local_value, dict) and isinstance(remote_value, dict):
            # Merge relationship dictionaries
            merged = local_value.copy()
            for key, value in remote_value.items():
                if key in merged:
                    if isinstance(value, list) and isinstance(merged[key], list):
                        merged[key] = list(set(merged[key] + value))
                    else:
                        merged[key] = value
                else:
                    merged[key] = value
            return merged

        # Default: use remote value
        return remote_value

    async def _create_version(self,
                            record_id: str,
                            new_data: Dict[str, Any],
                            existing_data: Optional[Dict[str, Any]],
                            source: str) -> DataVersion:
        """Create a new version record."""
        # Calculate changes
        changes = {}
        if existing_data:
            for key, new_value in new_data.items():
                old_value = existing_data.get(key)
                if old_value != new_value:
                    changes[key] = {'old': old_value, 'new': new_value}

        # Find parent version
        parent_version = None
        if record_id in self.version_store and self.version_store[record_id]:
            parent_version = self.version_store[record_id][-1].version_id

        version = DataVersion(
            version_id=str(uuid.uuid4()),
            content_hash=self._calculate_content_hash(new_data),
            timestamp=datetime.now(),
            author=source,
            changes=changes,
            parent_version=parent_version,
            metadata={
                'record_id': record_id,
                'change_count': len(changes)
            }
        )

        return version

    async def _apply_changes(self,
                           content_type: ContentType,
                           record_id: str,
                           new_data: Dict[str, Any],
                           existing_data: Optional[Dict[str, Any]],
                           change_type: ChangeType) -> Dict[str, Any]:
        """Apply changes to both PostgreSQL and MongoDB."""
        results = {}

        # Apply to PostgreSQL
        try:
            if change_type == ChangeType.INSERT:
                result = await self._insert_to_postgres(content_type, record_id, new_data)
            else:
                result = await self._update_postgres(content_type, record_id, new_data)
            results['postgresql'] = {'status': 'success', 'result': result}
        except Exception as e:
            results['postgresql'] = {'status': 'error', 'error': str(e)}

        # Apply to MongoDB
        try:
            if change_type == ChangeType.INSERT:
                result = await self._insert_to_mongodb(content_type, record_id, new_data)
            else:
                result = await self._update_mongodb(content_type, record_id, new_data)
            results['mongodb'] = {'status': 'success', 'result': result}
        except Exception as e:
            results['mongodb'] = {'status': 'error', 'error': str(e)}

        return results

    async def _insert_to_postgres(self, content_type: ContentType, record_id: str, data: Dict[str, Any]) -> str:
        """Insert new record to PostgreSQL."""
        table_name = self._get_table_name(content_type)

        # Build insert query dynamically
        fields = list(data.keys())
        placeholders = [f"${i+1}" for i in range(len(fields))]
        values = list(data.values())

        query = f"""
        INSERT INTO {table_name} ({', '.join(fields)})
        VALUES ({', '.join(placeholders)})
        RETURNING original_id
        """

        result = await postgres_db.execute_command(query, tuple(values))
        return result

    async def _update_postgres(self, content_type: ContentType, record_id: str, data: Dict[str, Any]) -> str:
        """Update existing record in PostgreSQL."""
        table_name = self._get_table_name(content_type)

        # Build update query
        set_clauses = []
        values = []
        for i, (key, value) in enumerate(data.items()):
            if key != 'original_id':  # Don't update the ID
                set_clauses.append(f"{key} = ${i+1}")
                values.append(value)

        values.append(record_id)  # For WHERE clause

        query = f"""
        UPDATE {table_name}
        SET {', '.join(set_clauses)}
        WHERE original_id = ${len(values)}
        """

        result = await postgres_db.execute_command(query, tuple(values))
        return result

    async def _insert_to_mongodb(self, content_type: ContentType, record_id: str, data: Dict[str, Any]) -> str:
        """Insert new document to MongoDB."""
        collection_name = self._get_collection_name(content_type)
        return await mongodb.insert_one(collection_name, data)

    async def _update_mongodb(self, content_type: ContentType, record_id: str, data: Dict[str, Any]) -> int:
        """Update existing document in MongoDB."""
        collection_name = self._get_collection_name(content_type)
        filter_dict = {"original_id": record_id}
        return await mongodb.update_one(collection_name, filter_dict, data)

    async def _record_change(self,
                           change_type: ChangeType,
                           content_type: ContentType,
                           record_id: str,
                           old_data: Optional[Dict[str, Any]],
                           new_data: Dict[str, Any],
                           source: str):
        """Record the change in the change log."""
        change_record = ChangeRecord(
            change_id=str(uuid.uuid4()),
            change_type=change_type,
            table_name=self._get_table_name(content_type),
            record_id=record_id,
            old_data=old_data,
            new_data=new_data,
            timestamp=datetime.now(),
            source=source,
            metadata={'content_type': content_type.value}
        )

        self.change_log.append(change_record)

        # Keep only recent changes
        if len(self.change_log) > 10000:
            self.change_log = self.change_log[-5000:]

    async def _store_version(self, record_id: str, version: DataVersion):
        """Store version in version store."""
        self.version_store[record_id].append(version)

        # Limit version history
        if len(self.version_store[record_id]) > self.max_version_history:
            self.version_store[record_id] = self.version_store[record_id][-self.max_version_history:]

    def _get_table_name(self, content_type: ContentType) -> str:
        """Get PostgreSQL table name for content type."""
        return f"processed_{content_type.value}"

    def _get_collection_name(self, content_type: ContentType) -> str:
        """Get MongoDB collection name for content type."""
        return f"processed_{content_type.value}"

    async def get_change_history(self,
                               record_id: Optional[str] = None,
                               since: Optional[datetime] = None,
                               limit: int = 100) -> List[Dict[str, Any]]:
        """Get change history with optional filtering."""
        changes = self.change_log

        # Filter by record ID
        if record_id:
            changes = [c for c in changes if c.record_id == record_id]

        # Filter by time
        if since:
            changes = [c for c in changes if c.timestamp >= since]

        # Sort by timestamp (newest first) and limit
        changes.sort(key=lambda c: c.timestamp, reverse=True)
        changes = changes[:limit]

        # Convert to serializable format
        return [
            {
                'change_id': c.change_id,
                'change_type': c.change_type.value,
                'table_name': c.table_name,
                'record_id': c.record_id,
                'timestamp': c.timestamp.isoformat(),
                'source': c.source,
                'metadata': c.metadata
            }
            for c in changes
        ]

    async def get_version_history(self, record_id: str) -> List[Dict[str, Any]]:
        """Get version history for a specific record."""
        if record_id not in self.version_store:
            return []

        versions = self.version_store[record_id]
        return [
            {
                'version_id': v.version_id,
                'content_hash': v.content_hash,
                'timestamp': v.timestamp.isoformat(),
                'author': v.author,
                'parent_version': v.parent_version,
                'change_count': len(v.changes),
                'metadata': v.metadata
            }
            for v in versions
        ]

    async def get_unresolved_conflicts(self) -> List[Dict[str, Any]]:
        """Get list of unresolved conflicts."""
        unresolved = [c for c in self.conflict_store if not c.resolved]

        return [
            {
                'conflict_id': c.conflict_id,
                'table_name': c.table_name,
                'record_id': c.record_id,
                'field_name': c.field_name,
                'local_value': c.local_value,
                'remote_value': c.remote_value,
                'local_timestamp': c.local_timestamp.isoformat(),
                'remote_timestamp': c.remote_timestamp.isoformat(),
                'resolution_strategy': c.resolution_strategy.value
            }
            for c in unresolved
        ]

    async def resolve_conflict_manually(self,
                                      conflict_id: str,
                                      resolved_value: Any) -> bool:
        """Manually resolve a conflict."""
        for conflict in self.conflict_store:
            if conflict.conflict_id == conflict_id and not conflict.resolved:
                conflict.resolved_value = resolved_value
                conflict.resolved = True
                conflict.resolved_at = datetime.now()

                # Apply the resolution
                try:
                    # This would update the actual data with resolved value
                    logger.info(f"Manually resolved conflict {conflict_id}")
                    return True
                except Exception as e:
                    logger.error(f"Failed to apply manual conflict resolution: {e}")
                    conflict.resolved = False
                    conflict.resolved_at = None
                    return False

        return False

    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get incremental processing statistics."""
        now = datetime.now()
        last_hour = now - timedelta(hours=1)
        last_day = now - timedelta(days=1)

        recent_changes = [c for c in self.change_log if c.timestamp >= last_hour]
        daily_changes = [c for c in self.change_log if c.timestamp >= last_day]

        return {
            'total_changes': len(self.change_log),
            'recent_changes_1h': len(recent_changes),
            'daily_changes': len(daily_changes),
            'change_types': {
                change_type.value: len([c for c in daily_changes if c.change_type == change_type])
                for change_type in ChangeType
            },
            'total_versions': sum(len(versions) for versions in self.version_store.values()),
            'total_conflicts': len(self.conflict_store),
            'unresolved_conflicts': len([c for c in self.conflict_store if not c.resolved]),
            'cache_size': len(self.content_hash_cache),
            'last_sync_timestamps': len(self.last_sync_timestamps)
        }