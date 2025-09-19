"""
ETL Pipeline Manager for Novel Text Processing

Manages the entire ETL pipeline including:
- Batch processing for historical data
- Stream processing for real-time updates
- Data quality monitoring
- Pipeline orchestration and scheduling
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

from ..database.connections.postgresql import postgres_db
from ..database.connections.mongodb import mongodb
from .types import ContentType, PipelineConfig, ProcessingMetrics, PipelineStatus
from .text_processor import TextProcessor
from .entity_extractor import EntityExtractor
from .data_validator import DataValidator
from .stream_processor import StreamProcessor

logger = logging.getLogger(__name__)


class PipelineManager:
    """
    Main ETL pipeline manager for novel text processing.

    Features:
    - Multi-content type processing (worldview, characters, plot, etc.)
    - Batch and stream processing modes
    - Incremental updates with checkpointing
    - Data quality validation
    - Entity extraction and relationship mapping
    - Dual database output (PostgreSQL + MongoDB)
    """

    def __init__(self, config: PipelineConfig = None):
        self.config = config or PipelineConfig()
        self.status = PipelineStatus.PENDING
        self.metrics = ProcessingMetrics()

        # Initialize processors
        self.text_processor = TextProcessor(
            enable_chinese_segmentation=self.config.chinese_segmentation,
            traditional_to_simplified=self.config.traditional_to_simplified
        )
        self.entity_extractor = EntityExtractor()
        self.data_validator = DataValidator()
        self.stream_processor = StreamProcessor()

        # Checkpoint management
        self.checkpoint_file = Path("pipeline_checkpoint.json")
        self.last_checkpoint = self._load_checkpoint()

        # Pipeline callbacks
        self.on_batch_complete: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        self.on_pipeline_complete: Optional[Callable] = None

    def _load_checkpoint(self) -> Dict[str, Any]:
        """Load pipeline checkpoint."""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load checkpoint: {e}")
        return {}

    def _save_checkpoint(self, checkpoint_data: Dict[str, Any]):
        """Save pipeline checkpoint."""
        try:
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
            logger.debug("Checkpoint saved successfully")
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")

    async def process_batch(self,
                          content_type: ContentType,
                          data_source: str,
                          resume_from_checkpoint: bool = True) -> ProcessingMetrics:
        """
        Process a batch of content.

        Args:
            content_type: Type of content being processed
            data_source: Source identifier (file path, database query, etc.)
            resume_from_checkpoint: Whether to resume from last checkpoint

        Returns:
            ProcessingMetrics: Processing statistics
        """
        self.status = PipelineStatus.RUNNING
        self.metrics = ProcessingMetrics()

        try:
            logger.info(f"Starting batch processing for {content_type.value}")

            # Determine starting position
            start_position = 0
            if resume_from_checkpoint and content_type.value in self.last_checkpoint:
                start_position = self.last_checkpoint[content_type.value].get('last_processed', 0)
                logger.info(f"Resuming from checkpoint at position {start_position}")

            # Extract data from source
            raw_data = await self._extract_data(data_source, start_position)

            # Process in batches
            total_batches = len(raw_data) // self.config.batch_size + 1

            for batch_idx in range(0, len(raw_data), self.config.batch_size):
                if self.status == PipelineStatus.PAUSED:
                    logger.info("Pipeline paused, saving checkpoint")
                    await self._save_batch_checkpoint(content_type, batch_idx)
                    break

                batch_data = raw_data[batch_idx:batch_idx + self.config.batch_size]

                try:
                    await self._process_batch_data(batch_data, content_type)
                    self.metrics.processed_records += len(batch_data)

                    # Save checkpoint periodically
                    if (batch_idx + len(batch_data)) % self.config.checkpoint_interval == 0:
                        await self._save_batch_checkpoint(content_type, batch_idx + len(batch_data))

                    # Call batch complete callback
                    if self.on_batch_complete:
                        await self.on_batch_complete(batch_idx // self.config.batch_size + 1, total_batches)

                except Exception as e:
                    logger.error(f"Batch processing failed at position {batch_idx}: {e}")
                    self.metrics.failed_records += len(batch_data)

                    if self.on_error:
                        await self.on_error(e, batch_data)

            self.metrics.end_time = datetime.now()
            self.metrics.calculate_rate()
            self.status = PipelineStatus.COMPLETED

            logger.info(f"Batch processing completed. Processed: {self.metrics.processed_records}, "
                       f"Failed: {self.metrics.failed_records}, "
                       f"Rate: {self.metrics.processing_rate:.2f} records/sec")

            if self.on_pipeline_complete:
                await self.on_pipeline_complete(self.metrics)

            return self.metrics

        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            self.status = PipelineStatus.FAILED
            self.metrics.end_time = datetime.now()
            raise

    async def _extract_data(self, data_source: str, start_position: int = 0) -> List[Dict[str, Any]]:
        """Extract data from source."""
        # This would be implemented based on the specific data source
        # For now, return mock data structure
        return [
            {
                "id": i,
                "content": f"Sample content {i}",
                "metadata": {"source": data_source, "position": i}
            }
            for i in range(start_position, start_position + 1000)
        ]

    async def _process_batch_data(self, batch_data: List[Dict[str, Any]], content_type: ContentType):
        """Process a batch of data through the pipeline."""
        processed_data = []

        for record in batch_data:
            try:
                # 1. Text preprocessing and cleaning
                cleaned_text = await self.text_processor.clean_text(record.get('content', ''))

                # 2. Entity extraction (if enabled)
                entities = []
                if self.config.enable_entity_extraction:
                    entities = await self.entity_extractor.extract_entities(
                        cleaned_text, content_type
                    )
                    self.metrics.extracted_entities += len(entities)

                # 3. Data validation (if enabled)
                if self.config.enable_validation:
                    validation_result = await self.data_validator.validate_record(
                        record, content_type
                    )
                    if not validation_result.is_valid:
                        self.metrics.validation_errors += 1
                        logger.warning(f"Validation failed for record {record.get('id')}: "
                                     f"{validation_result.errors}")
                        continue

                # 4. Prepare processed record
                processed_record = {
                    'original_id': record.get('id'),
                    'content_type': content_type.value,
                    'original_content': record.get('content'),
                    'cleaned_content': cleaned_text,
                    'entities': entities,
                    'metadata': record.get('metadata', {}),
                    'processed_at': datetime.now().isoformat(),
                    'pipeline_version': '1.0'
                }

                processed_data.append(processed_record)

            except Exception as e:
                logger.error(f"Failed to process record {record.get('id')}: {e}")
                continue

        # 5. Load to databases
        await self._load_processed_data(processed_data, content_type)

    async def _load_processed_data(self, processed_data: List[Dict[str, Any]], content_type: ContentType):
        """Load processed data to target databases."""
        if not processed_data:
            return

        try:
            # Load to PostgreSQL (structured data)
            if self.config.output_postgres:
                await self._load_to_postgres(processed_data, content_type)

            # Load to MongoDB (document storage)
            if self.config.output_mongodb:
                await self._load_to_mongodb(processed_data, content_type)

        except Exception as e:
            logger.error(f"Failed to load processed data: {e}")
            raise

    async def _load_to_postgres(self, processed_data: List[Dict[str, Any]], content_type: ContentType):
        """Load processed data to PostgreSQL."""
        table_name = f"processed_{content_type.value}"

        # Prepare INSERT statement (simplified)
        insert_query = f"""
        INSERT INTO {table_name}
        (original_id, content_type, original_content, cleaned_content,
         entities_count, metadata, processed_at, pipeline_version)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ON CONFLICT (original_id, content_type)
        DO UPDATE SET
            cleaned_content = EXCLUDED.cleaned_content,
            entities_count = EXCLUDED.entities_count,
            processed_at = EXCLUDED.processed_at
        """

        async with postgres_db.get_connection() as conn:
            for record in processed_data:
                await conn.execute(
                    insert_query,
                    record['original_id'],
                    record['content_type'],
                    record['original_content'],
                    record['cleaned_content'],
                    len(record['entities']),
                    json.dumps(record['metadata']),
                    record['processed_at'],
                    record['pipeline_version']
                )

    async def _load_to_mongodb(self, processed_data: List[Dict[str, Any]], content_type: ContentType):
        """Load processed data to MongoDB."""
        collection_name = f"processed_{content_type.value}"

        # Use upsert for incremental updates
        for record in processed_data:
            await mongodb.update_one(
                collection_name,
                {"original_id": record['original_id'], "content_type": record['content_type']},
                record
            )

    async def _save_batch_checkpoint(self, content_type: ContentType, position: int):
        """Save batch processing checkpoint."""
        checkpoint_data = self.last_checkpoint.copy()
        checkpoint_data[content_type.value] = {
            'last_processed': position,
            'timestamp': datetime.now().isoformat()
        }
        self._save_checkpoint(checkpoint_data)

    async def start_streaming(self, content_type: ContentType, source_config: Dict[str, Any]):
        """Start real-time streaming processing."""
        if not self.config.enable_streaming:
            raise ValueError("Streaming is disabled in configuration")

        logger.info(f"Starting streaming pipeline for {content_type.value}")
        await self.stream_processor.start_stream(content_type, source_config, self._process_stream_data)

    async def _process_stream_data(self, data: Dict[str, Any], content_type: ContentType):
        """Process streaming data."""
        try:
            await self._process_batch_data([data], content_type)
        except Exception as e:
            logger.error(f"Streaming data processing failed: {e}")
            if self.on_error:
                await self.on_error(e, [data])

    def pause_pipeline(self):
        """Pause the pipeline execution."""
        self.status = PipelineStatus.PAUSED
        logger.info("Pipeline execution paused")

    def resume_pipeline(self):
        """Resume the pipeline execution."""
        if self.status == PipelineStatus.PAUSED:
            self.status = PipelineStatus.RUNNING
            logger.info("Pipeline execution resumed")

    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status and metrics."""
        return {
            'status': self.status.value,
            'metrics': {
                'start_time': self.metrics.start_time.isoformat(),
                'end_time': self.metrics.end_time.isoformat() if self.metrics.end_time else None,
                'processed_records': self.metrics.processed_records,
                'failed_records': self.metrics.failed_records,
                'extracted_entities': self.metrics.extracted_entities,
                'validation_errors': self.metrics.validation_errors,
                'processing_rate': self.metrics.processing_rate
            },
            'config': {
                'batch_size': self.config.batch_size,
                'max_workers': self.config.max_workers,
                'enable_streaming': self.config.enable_streaming,
                'enable_validation': self.config.enable_validation,
                'enable_entity_extraction': self.config.enable_entity_extraction
            }
        }