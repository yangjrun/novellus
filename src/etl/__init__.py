"""
ETL (Extract, Transform, Load) pipeline for novel text processing.

This package provides:
- Text extraction from various sources
- Content preprocessing and cleaning
- Entity recognition and concept extraction
- Data validation and quality checks
- Incremental processing capabilities
- Real-time and batch processing support
"""

from .pipeline_manager import PipelineManager
from .text_processor import TextProcessor
from .entity_extractor import EntityExtractor
from .data_validator import DataValidator
from .stream_processor import StreamProcessor

__all__ = [
    'PipelineManager',
    'TextProcessor',
    'EntityExtractor',
    'DataValidator',
    'StreamProcessor'
]