"""
Common types and enums for the ETL pipeline.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


class ContentType(Enum):
    """Types of content for specialized processing."""
    NARRATIVE = "narrative"      # 叙述文本
    DIALOGUE = "dialogue"        # 对话文本
    DESCRIPTION = "description"  # 描述文本
    CULTURAL = "cultural"        # 文化设定
    WORLDBUILDING = "worldbuilding"  # 世界观构建
    CHARACTER = "character"      # 角色相关
    PLOT = "plot"               # 情节相关
    TECHNICAL = "technical"      # 技术设定
    SYSTEM = "system"           # 体系设定


class ProcessingStage(Enum):
    """Processing stages in the ETL pipeline."""
    EXTRACTION = "extraction"
    TRANSFORMATION = "transformation"
    LOADING = "loading"
    VALIDATION = "validation"
    CLEANING = "cleaning"
    ANALYSIS = "analysis"


class PipelineStatus(Enum):
    """Pipeline execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class PipelineConfig:
    """Configuration for ETL pipeline."""
    batch_size: int = 100
    max_workers: int = 4
    retry_attempts: int = 3
    retry_delay: int = 5  # seconds
    enable_streaming: bool = True
    enable_validation: bool = True
    enable_entity_extraction: bool = True
    output_postgres: bool = True
    output_mongodb: bool = True
    checkpoint_interval: int = 1000  # records

    # Chinese text processing specific settings
    chinese_segmentation: bool = True
    traditional_to_simplified: bool = False
    remove_punctuation: bool = False
    normalize_whitespace: bool = True


@dataclass
class ProcessingMetrics:
    """Metrics for pipeline execution."""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    processed_records: int = 0
    failed_records: int = 0
    extracted_entities: int = 0
    validation_errors: int = 0
    processing_rate: float = 0.0  # records per second

    def calculate_rate(self):
        """Calculate processing rate."""
        if self.end_time and self.start_time:
            duration = (self.end_time - self.start_time).total_seconds()
            if duration > 0:
                self.processing_rate = self.processed_records / duration