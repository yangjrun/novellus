"""
Data Validator for Novel Content Processing

Comprehensive data validation and quality assurance system including:
- Content quality metrics and scoring
- Data integrity checks
- Cross-reference validation
- Schema validation for structured data
- Business rule validation for novel content
- Anomaly detection and alerting
"""

import asyncio
import logging
import re
from typing import Dict, List, Any, Optional, Union, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime
import hashlib
import statistics
from collections import Counter, defaultdict

from .pipeline_manager import ContentType
from .entity_extractor import EntityType, ExtractedEntity

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationCategory(Enum):
    """Categories of validation checks."""
    CONTENT_QUALITY = "content_quality"
    DATA_INTEGRITY = "data_integrity"
    SCHEMA_VALIDATION = "schema_validation"
    BUSINESS_RULES = "business_rules"
    ENTITY_CONSISTENCY = "entity_consistency"
    CROSS_REFERENCE = "cross_reference"


@dataclass
class ValidationIssue:
    """A validation issue found during data quality checks."""
    issue_id: str
    category: ValidationCategory
    severity: ValidationSeverity
    message: str
    field_name: Optional[str] = None
    field_value: Optional[Any] = None
    rule_name: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    suggested_fix: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ValidationResult:
    """Result of data validation."""
    is_valid: bool
    overall_score: float  # 0-100
    issues: List[ValidationIssue]
    metrics: Dict[str, Any]
    validation_time: float
    record_id: Optional[str] = None

    def get_issues_by_severity(self, severity: ValidationSeverity) -> List[ValidationIssue]:
        """Get issues filtered by severity."""
        return [issue for issue in self.issues if issue.severity == severity]

    def get_issues_by_category(self, category: ValidationCategory) -> List[ValidationIssue]:
        """Get issues filtered by category."""
        return [issue for issue in self.issues if issue.category == category]


class ContentQualityMetrics:
    """Calculate content quality metrics for text."""

    @staticmethod
    def calculate_readability_score(text: str) -> float:
        """Calculate readability score for Chinese text."""
        if not text:
            return 0.0

        # Basic metrics
        char_count = len(text)
        sentence_count = len(re.findall(r'[。！？]', text))
        if sentence_count == 0:
            return 0.0

        avg_sentence_length = char_count / sentence_count

        # Chinese readability scoring (simplified)
        # Optimal sentence length for Chinese is around 15-25 characters
        if 15 <= avg_sentence_length <= 25:
            length_score = 100
        elif 10 <= avg_sentence_length <= 30:
            length_score = 80
        else:
            length_score = max(0, 60 - abs(avg_sentence_length - 20) * 2)

        return min(100, length_score)

    @staticmethod
    def calculate_complexity_score(text: str, entities: List[ExtractedEntity]) -> float:
        """Calculate content complexity based on entities and structure."""
        if not text:
            return 0.0

        # Entity density
        entity_count = len(entities)
        char_count = len(text)
        entity_density = (entity_count / char_count * 1000) if char_count > 0 else 0

        # Entity type diversity
        entity_types = set(e.entity_type for e in entities)
        type_diversity = len(entity_types)

        # Complexity scoring
        complexity_score = min(100, (entity_density * 20) + (type_diversity * 10))

        return complexity_score

    @staticmethod
    def calculate_coherence_score(text: str) -> float:
        """Calculate text coherence based on structure and flow."""
        if not text:
            return 0.0

        # Paragraph structure
        paragraphs = text.split('\n\n')
        paragraph_count = len([p for p in paragraphs if p.strip()])

        # Sentence structure
        sentences = re.split(r'[。！？]', text)
        sentence_count = len([s for s in sentences if s.strip()])

        if sentence_count == 0:
            return 0.0

        # Optimal ratios
        sentences_per_paragraph = sentence_count / paragraph_count if paragraph_count > 0 else sentence_count

        # Coherence scoring (based on structure balance)
        if 3 <= sentences_per_paragraph <= 8:
            structure_score = 100
        elif 2 <= sentences_per_paragraph <= 10:
            structure_score = 80
        else:
            structure_score = 60

        return structure_score


class DataValidator:
    """
    Comprehensive data validation system for novel content.

    Features:
    - Multi-level validation (syntax, semantics, business rules)
    - Content quality scoring
    - Entity consistency checking
    - Cross-reference validation
    - Anomaly detection
    - Configurable validation rules
    """

    def __init__(self):
        self.validation_rules = self._initialize_validation_rules()
        self.business_rules = self._initialize_business_rules()
        self.quality_metrics = ContentQualityMetrics()

        # Validation history for anomaly detection
        self.validation_history = []

        # Entity consistency cache
        self.entity_consistency_cache = {}

        # Schema definitions
        self.schemas = self._initialize_schemas()

        logger.info("DataValidator initialized")

    def _initialize_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize basic validation rules."""
        rules = {
            'content_length': {
                'min_length': 10,
                'max_length': 50000,
                'warning_threshold': 1000,
                'optimal_range': (500, 5000)
            },
            'character_encoding': {
                'allowed_encodings': ['utf-8'],
                'check_special_chars': True
            },
            'text_format': {
                'max_consecutive_spaces': 3,
                'max_consecutive_newlines': 3,
                'check_punctuation_balance': True
            },
            'entity_consistency': {
                'max_name_variants': 5,
                'min_confidence_threshold': 0.6,
                'check_contradictions': True
            }
        }
        return rules

    def _initialize_business_rules(self) -> Dict[str, Callable]:
        """Initialize business-specific validation rules."""
        return {
            'cultivation_system_consistency': self._validate_cultivation_consistency,
            'character_relationship_logic': self._validate_character_relationships,
            'location_hierarchy_consistency': self._validate_location_hierarchy,
            'timeline_consistency': self._validate_timeline_consistency,
            'power_scaling_logic': self._validate_power_scaling,
        }

    def _initialize_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Initialize data schemas for different content types."""
        return {
            'processed_content': {
                'required_fields': ['original_id', 'content_type', 'cleaned_content', 'processed_at'],
                'field_types': {
                    'original_id': (str, int),
                    'content_type': str,
                    'original_content': str,
                    'cleaned_content': str,
                    'entities': list,
                    'metadata': dict,
                    'processed_at': str,
                    'pipeline_version': str
                }
            },
            'entity_data': {
                'required_fields': ['entity_id', 'canonical_name', 'entity_type'],
                'field_types': {
                    'entity_id': str,
                    'canonical_name': str,
                    'entity_type': str,
                    'mentions': list,
                    'aliases': (list, set),
                    'confidence': (int, float),
                    'relationships': dict
                }
            }
        }

    async def validate_record(self,
                            record: Dict[str, Any],
                            content_type: ContentType,
                            entities: Optional[List[ExtractedEntity]] = None,
                            context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate a single record comprehensively.

        Args:
            record: Record to validate
            content_type: Type of content being validated
            entities: Extracted entities (optional)
            context: Additional validation context

        Returns:
            ValidationResult with validation status and issues
        """
        start_time = datetime.now()
        issues = []
        metrics = {}

        record_id = str(record.get('id', record.get('original_id', 'unknown')))

        try:
            # 1. Schema validation
            schema_issues = await self._validate_schema(record, 'processed_content')
            issues.extend(schema_issues)

            # 2. Content quality validation
            content = record.get('cleaned_content') or record.get('original_content', '')
            quality_issues, quality_metrics = await self._validate_content_quality(
                content, content_type, entities
            )
            issues.extend(quality_issues)
            metrics.update(quality_metrics)

            # 3. Data integrity validation
            integrity_issues = await self._validate_data_integrity(record)
            issues.extend(integrity_issues)

            # 4. Entity consistency validation
            if entities:
                entity_issues = await self._validate_entity_consistency(entities, content)
                issues.extend(entity_issues)

            # 5. Business rules validation
            business_issues = await self._validate_business_rules(record, content_type, entities)
            issues.extend(business_issues)

            # 6. Cross-reference validation
            if context:
                xref_issues = await self._validate_cross_references(record, context)
                issues.extend(xref_issues)

            # 7. Calculate overall score
            overall_score = self._calculate_overall_score(issues, metrics)

            # 8. Determine if record is valid
            critical_errors = [i for i in issues if i.severity == ValidationSeverity.CRITICAL]
            errors = [i for i in issues if i.severity == ValidationSeverity.ERROR]
            is_valid = len(critical_errors) == 0 and len(errors) == 0

            validation_time = (datetime.now() - start_time).total_seconds()

            result = ValidationResult(
                is_valid=is_valid,
                overall_score=overall_score,
                issues=issues,
                metrics=metrics,
                validation_time=validation_time,
                record_id=record_id
            )

            # Store in history for anomaly detection
            self.validation_history.append({
                'timestamp': datetime.now(),
                'record_id': record_id,
                'content_type': content_type.value,
                'score': overall_score,
                'issue_count': len(issues),
                'is_valid': is_valid
            })

            # Keep only recent history
            if len(self.validation_history) > 1000:
                self.validation_history = self.validation_history[-1000:]

            return result

        except Exception as e:
            logger.error(f"Validation failed for record {record_id}: {e}")
            return ValidationResult(
                is_valid=False,
                overall_score=0.0,
                issues=[ValidationIssue(
                    issue_id=f"validation_error_{record_id}",
                    category=ValidationCategory.DATA_INTEGRITY,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Validation process failed: {str(e)}",
                    rule_name="validation_process_integrity"
                )],
                metrics={},
                validation_time=(datetime.now() - start_time).total_seconds(),
                record_id=record_id
            )

    async def _validate_schema(self, record: Dict[str, Any], schema_name: str) -> List[ValidationIssue]:
        """Validate record against schema."""
        issues = []

        if schema_name not in self.schemas:
            return issues

        schema = self.schemas[schema_name]

        # Check required fields
        for field in schema['required_fields']:
            if field not in record:
                issues.append(ValidationIssue(
                    issue_id=f"missing_field_{field}",
                    category=ValidationCategory.SCHEMA_VALIDATION,
                    severity=ValidationSeverity.ERROR,
                    message=f"Required field '{field}' is missing",
                    field_name=field,
                    rule_name="required_fields"
                ))

        # Check field types
        for field, expected_types in schema['field_types'].items():
            if field in record:
                value = record[field]
                if not isinstance(expected_types, tuple):
                    expected_types = (expected_types,)

                if value is not None and not isinstance(value, expected_types):
                    issues.append(ValidationIssue(
                        issue_id=f"invalid_type_{field}",
                        category=ValidationCategory.SCHEMA_VALIDATION,
                        severity=ValidationSeverity.ERROR,
                        message=f"Field '{field}' has invalid type. Expected {expected_types}, got {type(value)}",
                        field_name=field,
                        field_value=value,
                        rule_name="field_types"
                    ))

        return issues

    async def _validate_content_quality(self,
                                       content: str,
                                       content_type: ContentType,
                                       entities: Optional[List[ExtractedEntity]]) -> Tuple[List[ValidationIssue], Dict[str, Any]]:
        """Validate content quality metrics."""
        issues = []
        metrics = {}

        if not content:
            issues.append(ValidationIssue(
                issue_id="empty_content",
                category=ValidationCategory.CONTENT_QUALITY,
                severity=ValidationSeverity.ERROR,
                message="Content is empty",
                field_name="content",
                rule_name="content_presence"
            ))
            return issues, metrics

        # Length validation
        content_length = len(content)
        rules = self.validation_rules['content_length']

        if content_length < rules['min_length']:
            issues.append(ValidationIssue(
                issue_id="content_too_short",
                category=ValidationCategory.CONTENT_QUALITY,
                severity=ValidationSeverity.ERROR,
                message=f"Content too short: {content_length} chars (minimum: {rules['min_length']})",
                field_name="content",
                field_value=content_length,
                rule_name="min_length"
            ))

        if content_length > rules['max_length']:
            issues.append(ValidationIssue(
                issue_id="content_too_long",
                category=ValidationCategory.CONTENT_QUALITY,
                severity=ValidationSeverity.WARNING,
                message=f"Content very long: {content_length} chars (maximum: {rules['max_length']})",
                field_name="content",
                field_value=content_length,
                rule_name="max_length"
            ))

        # Quality metrics calculation
        readability_score = self.quality_metrics.calculate_readability_score(content)
        coherence_score = self.quality_metrics.calculate_coherence_score(content)

        if entities:
            complexity_score = self.quality_metrics.calculate_complexity_score(content, entities)
        else:
            complexity_score = 0.0

        metrics.update({
            'content_length': content_length,
            'readability_score': readability_score,
            'coherence_score': coherence_score,
            'complexity_score': complexity_score
        })

        # Quality thresholds
        if readability_score < 50:
            issues.append(ValidationIssue(
                issue_id="low_readability",
                category=ValidationCategory.CONTENT_QUALITY,
                severity=ValidationSeverity.WARNING,
                message=f"Low readability score: {readability_score:.1f}",
                field_name="content",
                field_value=readability_score,
                rule_name="readability_threshold",
                suggested_fix="Consider breaking long sentences or improving sentence structure"
            ))

        if coherence_score < 60:
            issues.append(ValidationIssue(
                issue_id="low_coherence",
                category=ValidationCategory.CONTENT_QUALITY,
                severity=ValidationSeverity.WARNING,
                message=f"Low coherence score: {coherence_score:.1f}",
                field_name="content",
                field_value=coherence_score,
                rule_name="coherence_threshold",
                suggested_fix="Consider improving paragraph and sentence structure"
            ))

        return issues, metrics

    async def _validate_data_integrity(self, record: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate data integrity."""
        issues = []

        # Check for null/empty required fields
        content = record.get('cleaned_content') or record.get('original_content', '')
        if not content.strip():
            issues.append(ValidationIssue(
                issue_id="empty_cleaned_content",
                category=ValidationCategory.DATA_INTEGRITY,
                severity=ValidationSeverity.ERROR,
                message="Cleaned content is empty after processing",
                field_name="cleaned_content",
                rule_name="content_integrity"
            ))

        # Check timestamp validity
        processed_at = record.get('processed_at')
        if processed_at:
            try:
                datetime.fromisoformat(processed_at.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                issues.append(ValidationIssue(
                    issue_id="invalid_timestamp",
                    category=ValidationCategory.DATA_INTEGRITY,
                    severity=ValidationSeverity.WARNING,
                    message=f"Invalid timestamp format: {processed_at}",
                    field_name="processed_at",
                    field_value=processed_at,
                    rule_name="timestamp_format"
                ))

        # Check metadata integrity
        metadata = record.get('metadata', {})
        if not isinstance(metadata, dict):
            issues.append(ValidationIssue(
                issue_id="invalid_metadata",
                category=ValidationCategory.DATA_INTEGRITY,
                severity=ValidationSeverity.WARNING,
                message="Metadata is not a valid dictionary",
                field_name="metadata",
                field_value=type(metadata).__name__,
                rule_name="metadata_format"
            ))

        return issues

    async def _validate_entity_consistency(self,
                                         entities: List[ExtractedEntity],
                                         content: str) -> List[ValidationIssue]:
        """Validate entity consistency."""
        issues = []

        if not entities:
            return issues

        # Check for duplicate entities
        entity_names = [e.canonical_name for e in entities]
        name_counts = Counter(entity_names)
        for name, count in name_counts.items():
            if count > 1:
                issues.append(ValidationIssue(
                    issue_id=f"duplicate_entity_{name}",
                    category=ValidationCategory.ENTITY_CONSISTENCY,
                    severity=ValidationSeverity.WARNING,
                    message=f"Entity '{name}' appears {count} times with same canonical name",
                    field_name="entities",
                    field_value=name,
                    rule_name="entity_uniqueness"
                ))

        # Check entity confidence scores
        rules = self.validation_rules['entity_consistency']
        for entity in entities:
            if entity.confidence < rules['min_confidence_threshold']:
                issues.append(ValidationIssue(
                    issue_id=f"low_confidence_entity_{entity.entity_id}",
                    category=ValidationCategory.ENTITY_CONSISTENCY,
                    severity=ValidationSeverity.WARNING,
                    message=f"Entity '{entity.canonical_name}' has low confidence: {entity.confidence:.2f}",
                    field_name="entities",
                    field_value=entity.confidence,
                    rule_name="entity_confidence_threshold"
                ))

        # Check for entity mention consistency in text
        for entity in entities:
            for mention in entity.mentions:
                mention_text = content[mention.start_pos:mention.end_pos]
                if mention_text != mention.text:
                    issues.append(ValidationIssue(
                        issue_id=f"mention_mismatch_{entity.entity_id}",
                        category=ValidationCategory.ENTITY_CONSISTENCY,
                        severity=ValidationSeverity.ERROR,
                        message=f"Entity mention position mismatch for '{entity.canonical_name}'",
                        field_name="entities",
                        field_value=mention.text,
                        rule_name="mention_position_consistency"
                    ))

        return issues

    async def _validate_business_rules(self,
                                     record: Dict[str, Any],
                                     content_type: ContentType,
                                     entities: Optional[List[ExtractedEntity]]) -> List[ValidationIssue]:
        """Validate business-specific rules."""
        issues = []

        for rule_name, rule_func in self.business_rules.items():
            try:
                rule_issues = await rule_func(record, content_type, entities)
                issues.extend(rule_issues)
            except Exception as e:
                logger.warning(f"Business rule '{rule_name}' failed: {e}")
                issues.append(ValidationIssue(
                    issue_id=f"business_rule_error_{rule_name}",
                    category=ValidationCategory.BUSINESS_RULES,
                    severity=ValidationSeverity.WARNING,
                    message=f"Business rule validation failed: {str(e)}",
                    rule_name=rule_name
                ))

        return issues

    async def _validate_cross_references(self,
                                       record: Dict[str, Any],
                                       context: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate cross-references with other data."""
        issues = []

        # Check for referenced entities that should exist
        content = record.get('cleaned_content', '')

        # This would be implemented based on specific cross-reference requirements
        # For now, we'll implement a basic check

        return issues

    # Business rule implementations
    async def _validate_cultivation_consistency(self,
                                              record: Dict[str, Any],
                                              content_type: ContentType,
                                              entities: Optional[List[ExtractedEntity]]) -> List[ValidationIssue]:
        """Validate cultivation system consistency."""
        issues = []

        if not entities:
            return issues

        cultivation_entities = [e for e in entities if e.entity_type == EntityType.CULTIVATION_LEVEL]

        # Check for impossible cultivation progressions
        cultivation_order = [
            '筑基', '结丹', '元婴', '化神', '合体', '大乘', '渡劫', '散仙', '地仙', '天仙', '金仙', '太乙', '大罗'
        ]

        for entity in cultivation_entities:
            for mention in entity.mentions:
                # Check if cultivation level is in known order
                level_found = False
                for level in cultivation_order:
                    if level in mention.text:
                        level_found = True
                        break

                if not level_found and len(mention.text) < 10:  # Short mentions are more likely to be levels
                    issues.append(ValidationIssue(
                        issue_id=f"unknown_cultivation_level_{entity.entity_id}",
                        category=ValidationCategory.BUSINESS_RULES,
                        severity=ValidationSeverity.INFO,
                        message=f"Unknown cultivation level detected: '{mention.text}'",
                        field_name="entities",
                        field_value=mention.text,
                        rule_name="cultivation_system_consistency"
                    ))

        return issues

    async def _validate_character_relationships(self,
                                              record: Dict[str, Any],
                                              content_type: ContentType,
                                              entities: Optional[List[ExtractedEntity]]) -> List[ValidationIssue]:
        """Validate character relationship logic."""
        issues = []
        # Implementation would check for logical relationship consistency
        return issues

    async def _validate_location_hierarchy(self,
                                         record: Dict[str, Any],
                                         content_type: ContentType,
                                         entities: Optional[List[ExtractedEntity]]) -> List[ValidationIssue]:
        """Validate location hierarchy consistency."""
        issues = []
        # Implementation would check for geographical consistency
        return issues

    async def _validate_timeline_consistency(self,
                                           record: Dict[str, Any],
                                           content_type: ContentType,
                                           entities: Optional[List[ExtractedEntity]]) -> List[ValidationIssue]:
        """Validate timeline consistency."""
        issues = []
        # Implementation would check for temporal consistency
        return issues

    async def _validate_power_scaling(self,
                                    record: Dict[str, Any],
                                    content_type: ContentType,
                                    entities: Optional[List[ExtractedEntity]]) -> List[ValidationIssue]:
        """Validate power scaling logic."""
        issues = []
        # Implementation would check for consistent power scaling
        return issues

    def _calculate_overall_score(self, issues: List[ValidationIssue], metrics: Dict[str, Any]) -> float:
        """Calculate overall validation score."""
        if not issues and not metrics:
            return 50.0  # Neutral score for empty validation

        # Base score
        base_score = 100.0

        # Deduct points for issues
        for issue in issues:
            if issue.severity == ValidationSeverity.CRITICAL:
                base_score -= 25
            elif issue.severity == ValidationSeverity.ERROR:
                base_score -= 15
            elif issue.severity == ValidationSeverity.WARNING:
                base_score -= 5
            elif issue.severity == ValidationSeverity.INFO:
                base_score -= 1

        # Add points for quality metrics
        quality_boost = 0
        if 'readability_score' in metrics:
            quality_boost += metrics['readability_score'] * 0.1

        if 'coherence_score' in metrics:
            quality_boost += metrics['coherence_score'] * 0.1

        if 'complexity_score' in metrics:
            quality_boost += min(metrics['complexity_score'] * 0.05, 5)  # Cap complexity bonus

        final_score = base_score + quality_boost
        return max(0.0, min(100.0, final_score))

    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation statistics from history."""
        if not self.validation_history:
            return {}

        scores = [entry['score'] for entry in self.validation_history]
        issue_counts = [entry['issue_count'] for entry in self.validation_history]
        valid_ratio = sum(1 for entry in self.validation_history if entry['is_valid']) / len(self.validation_history)

        return {
            'total_validations': len(self.validation_history),
            'average_score': statistics.mean(scores),
            'score_std_dev': statistics.stdev(scores) if len(scores) > 1 else 0,
            'average_issues': statistics.mean(issue_counts),
            'valid_record_ratio': valid_ratio,
            'recent_validations': self.validation_history[-10:] if len(self.validation_history) >= 10 else self.validation_history
        }

    def detect_anomalies(self, lookback_days: int = 7) -> List[Dict[str, Any]]:
        """Detect anomalous validation patterns."""
        if len(self.validation_history) < 10:
            return []

        # Get recent data
        cutoff_time = datetime.now() - timedelta(days=lookback_days)
        recent_data = [entry for entry in self.validation_history if entry['timestamp'] >= cutoff_time]

        if len(recent_data) < 5:
            return []

        # Calculate baselines
        all_scores = [entry['score'] for entry in self.validation_history[:-len(recent_data)]]
        if not all_scores:
            return []

        baseline_mean = statistics.mean(all_scores)
        baseline_std = statistics.stdev(all_scores) if len(all_scores) > 1 else 0

        anomalies = []

        # Detect score anomalies
        for entry in recent_data:
            if baseline_std > 0:
                z_score = abs(entry['score'] - baseline_mean) / baseline_std
                if z_score > 2.5:  # 2.5 standard deviations
                    anomalies.append({
                        'type': 'score_anomaly',
                        'record_id': entry['record_id'],
                        'timestamp': entry['timestamp'],
                        'score': entry['score'],
                        'baseline_mean': baseline_mean,
                        'z_score': z_score,
                        'severity': 'high' if z_score > 3 else 'medium'
                    })

        return anomalies