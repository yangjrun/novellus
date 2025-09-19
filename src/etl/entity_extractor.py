"""
Entity Extractor for Novel Content

Advanced entity recognition and concept extraction specifically designed for
Chinese fantasy novels, including:
- Character name and relationship extraction
- Location and worldbuilding element identification
- Cultivation system terms and power scaling
- Plot elements and narrative structures
- Cross-reference and relationship mapping
"""

import asyncio
import logging
import re
from typing import Dict, List, Any, Set, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict, Counter
import spacy
from spacy.matcher import Matcher, PhraseMatcher
from spacy.tokens import Doc, Span
import networkx as nx

from .types import ContentType

logger = logging.getLogger(__name__)


class EntityType(Enum):
    """Types of entities that can be extracted."""
    CHARACTER = "character"                 # 人物
    LOCATION = "location"                  # 地点
    CULTIVATION_LEVEL = "cultivation_level" # 修炼境界
    TECHNIQUE = "technique"                # 功法/技能
    ARTIFACT = "artifact"                  # 法宝/器具
    ORGANIZATION = "organization"          # 组织/势力
    EVENT = "event"                       # 事件
    CONCEPT = "concept"                   # 概念
    TIME = "time"                         # 时间
    POWER = "power"                       # 力量/能力


@dataclass
class EntityMention:
    """A mention of an entity in text."""
    text: str                      # Original text mention
    normalized_form: str           # Normalized entity name
    entity_type: EntityType        # Type of entity
    start_pos: int                # Start position in text
    end_pos: int                  # End position in text
    confidence: float             # Confidence score (0-1)
    context: str                  # Surrounding context
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractedEntity:
    """A complete extracted entity with all mentions and metadata."""
    entity_id: str                     # Unique identifier
    canonical_name: str                # Primary name
    entity_type: EntityType            # Type of entity
    mentions: List[EntityMention]      # All mentions in text
    aliases: Set[str]                  # Alternative names
    attributes: Dict[str, Any]         # Entity attributes
    relationships: Dict[str, List[str]] # Relationships to other entities
    first_mention_pos: int             # Position of first mention
    mention_count: int                 # Total mentions
    confidence: float                  # Overall confidence


class EntityRecognitionPattern:
    """Pattern for entity recognition."""

    def __init__(self, pattern_type: str, pattern: str, entity_type: EntityType,
                 flags: int = 0, confidence: float = 0.8):
        self.pattern_type = pattern_type  # 'regex' or 'phrase'
        self.pattern = pattern
        self.entity_type = entity_type
        self.flags = flags
        self.confidence = confidence

        if pattern_type == 'regex':
            self.compiled_pattern = re.compile(pattern, flags)
        else:
            self.compiled_pattern = None


class EntityExtractor:
    """
    Advanced entity extraction system for Chinese fantasy novels.

    Features:
    - Multi-pattern entity recognition
    - Context-aware disambiguation
    - Relationship extraction
    - Cross-reference resolution
    - Novel-specific entity types
    - Confidence scoring
    """

    def __init__(self):
        # Initialize spaCy model for Chinese (if available)
        try:
            self.nlp = spacy.load("zh_core_web_sm")
        except OSError:
            logger.warning("Chinese spaCy model not found, using basic processing")
            self.nlp = None

        # Entity recognition patterns
        self.patterns = self._initialize_patterns()

        # Phrase matchers for known entities
        self.phrase_matchers = {}
        if self.nlp:
            self._initialize_phrase_matchers()

        # Entity relationship graph
        self.entity_graph = nx.DiGraph()

        # Entity knowledge base
        self.entity_kb = {
            'characters': {},
            'locations': {},
            'cultivation_levels': {},
            'techniques': {},
            'artifacts': {},
            'organizations': {}
        }

        # Coreference resolution cache
        self.coreference_cache = {}

        logger.info("EntityExtractor initialized")

    def _initialize_patterns(self) -> List[EntityRecognitionPattern]:
        """Initialize regex patterns for entity recognition."""
        patterns = []

        # Character name patterns (Chinese names)
        patterns.extend([
            EntityRecognitionPattern(
                'regex',
                r'[王李张刘陈杨黄赵周吴徐孙朱马胡郭林何高梁郑罗宋谢唐韩曹许邓萧冯曾程蔡彭潘袁于董余苏叶吕魏蒋田杜丁沈姜范江傅钟卢汪戴崔任陆廖姚方金邱夏谭韦贾邹石熊孟秦阎薛侯雷白龙段郝孔邵史毛常万顾赖武康贺严尹钱施牛洪龚汤安易常温康庄严牧][一-龯]{1,3}(?:公子|大人|前辈|道友|师兄|师姐|师父|长老)?',
                EntityType.CHARACTER,
                confidence=0.85
            ),
            EntityRecognitionPattern(
                'regex',
                r'[一-龯]{2,4}(?:公子|大人|前辈|道友|师兄|师姐|师父|长老|掌门|宗主|族长|域主)',
                EntityType.CHARACTER,
                confidence=0.75
            ),
        ])

        # Location patterns
        patterns.extend([
            EntityRecognitionPattern(
                'regex',
                r'[东西南北中][一-龯]*(?:域|界|州|城|郡|国)',
                EntityType.LOCATION,
                confidence=0.9
            ),
            EntityRecognitionPattern(
                'regex',
                r'[一-龯]{2,6}(?:山|峰|谷|川|江|河|湖|海|岛|洲|城|镇|村|寨|堡|关|隘|宫|殿|府|邸|院|楼|阁|塔)',
                EntityType.LOCATION,
                confidence=0.8
            ),
        ])

        # Cultivation level patterns
        patterns.extend([
            EntityRecognitionPattern(
                'regex',
                r'[一-龯]*(?:筑基|结丹|元婴|化神|合体|大乘|渡劫|散仙|地仙|天仙|金仙|太乙|大罗)(?:期|境|级|层)?',
                EntityType.CULTIVATION_LEVEL,
                confidence=0.95
            ),
            EntityRecognitionPattern(
                'regex',
                r'(?:初中后期|前中后期|巅峰|圆满)(?:筑基|结丹|元婴|化神|合体|大乘)',
                EntityType.CULTIVATION_LEVEL,
                confidence=0.9
            ),
        ])

        # Technique patterns
        patterns.extend([
            EntityRecognitionPattern(
                'regex',
                r'[一-龯]{2,8}(?:剑法|刀法|拳法|掌法|指法|腿法|身法|轻功)',
                EntityType.TECHNIQUE,
                confidence=0.85
            ),
            EntityRecognitionPattern(
                'regex',
                r'[一-龯]{2,8}(?:诀|功|法|术|技|能)',
                EntityType.TECHNIQUE,
                confidence=0.7
            ),
        ])

        # Artifact patterns
        patterns.extend([
            EntityRecognitionPattern(
                'regex',
                r'[一-龯]{2,8}(?:剑|刀|枪|戟|斧|锤|鞭|棍|环|珠|镜|鼎|塔|印|符|玉|石)',
                EntityType.ARTIFACT,
                confidence=0.8
            ),
            EntityRecognitionPattern(
                'regex',
                r'[一-龯]*(?:法宝|灵器|法器|神器|仙器|至宝)',
                EntityType.ARTIFACT,
                confidence=0.85
            ),
        ])

        # Organization patterns
        patterns.extend([
            EntityRecognitionPattern(
                'regex',
                r'[一-龯]{2,6}(?:宗|派|门|教|会|盟|帮|堂|府|家族)',
                EntityType.ORGANIZATION,
                confidence=0.8
            ),
        ])

        return patterns

    def _initialize_phrase_matchers(self):
        """Initialize phrase matchers for known entities."""
        if not self.nlp:
            return

        # Known characters from the novel universe
        character_phrases = [
            "裂世九域", "天权域主", "地煞域主", "人皇域主",
            "修罗域主", "魔渊域主", "仙境域主", "神界域主",
            "混沌域主", "虚无域主"
        ]

        # Known locations
        location_phrases = [
            "天权域", "地煞域", "人皇域", "修罗域", "魔渊域",
            "仙境域", "神界域", "混沌域", "虚无域"
        ]

        # Create phrase matchers
        self.phrase_matchers['characters'] = PhraseMatcher(self.nlp.vocab)
        self.phrase_matchers['locations'] = PhraseMatcher(self.nlp.vocab)

        # Add phrases
        char_patterns = [self.nlp(phrase) for phrase in character_phrases]
        loc_patterns = [self.nlp(phrase) for phrase in location_phrases]

        self.phrase_matchers['characters'].add("CHARACTERS", char_patterns)
        self.phrase_matchers['locations'].add("LOCATIONS", loc_patterns)

    async def extract_entities(self,
                              text: str,
                              content_type: ContentType,
                              context: Optional[Dict[str, Any]] = None) -> List[ExtractedEntity]:
        """
        Extract entities from text with content-type specific processing.

        Args:
            text: Input text to analyze
            content_type: Type of content being processed
            context: Additional context information

        Returns:
            List of extracted entities
        """
        if not text:
            return []

        logger.debug(f"Extracting entities from {len(text)} characters of {content_type.value} content")

        # Step 1: Apply pattern-based extraction
        pattern_entities = await self._extract_with_patterns(text)

        # Step 2: Apply NLP-based extraction (if available)
        nlp_entities = await self._extract_with_nlp(text) if self.nlp else []

        # Step 3: Apply phrase matching
        phrase_entities = await self._extract_with_phrases(text) if self.nlp else []

        # Step 4: Combine and deduplicate entities
        all_mentions = pattern_entities + nlp_entities + phrase_entities
        entities = await self._consolidate_entities(all_mentions, text)

        # Step 5: Content-type specific post-processing
        entities = await self._post_process_by_content_type(entities, content_type, context)

        # Step 6: Extract relationships
        entities = await self._extract_relationships(entities, text)

        # Step 7: Update entity knowledge base
        await self._update_knowledge_base(entities)

        logger.debug(f"Extracted {len(entities)} entities")
        return entities

    async def _extract_with_patterns(self, text: str) -> List[EntityMention]:
        """Extract entities using regex patterns."""
        mentions = []

        for pattern in self.patterns:
            if pattern.pattern_type == 'regex':
                matches = pattern.compiled_pattern.finditer(text)
                for match in matches:
                    mention = EntityMention(
                        text=match.group(),
                        normalized_form=self._normalize_entity_name(match.group()),
                        entity_type=pattern.entity_type,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=pattern.confidence,
                        context=self._extract_context(text, match.start(), match.end())
                    )
                    mentions.append(mention)

        return mentions

    async def _extract_with_nlp(self, text: str) -> List[EntityMention]:
        """Extract entities using spaCy NLP model."""
        mentions = []

        doc = self.nlp(text)
        for ent in doc.ents:
            # Map spaCy entity types to our entity types
            entity_type = self._map_spacy_entity_type(ent.label_)
            if entity_type:
                mention = EntityMention(
                    text=ent.text,
                    normalized_form=self._normalize_entity_name(ent.text),
                    entity_type=entity_type,
                    start_pos=ent.start_char,
                    end_pos=ent.end_char,
                    confidence=0.7,  # Default confidence for NLP entities
                    context=self._extract_context(text, ent.start_char, ent.end_char)
                )
                mentions.append(mention)

        return mentions

    async def _extract_with_phrases(self, text: str) -> List[EntityMention]:
        """Extract entities using phrase matchers."""
        mentions = []

        doc = self.nlp(text)
        for matcher_name, matcher in self.phrase_matchers.items():
            matches = matcher(doc)
            for match_id, start, end in matches:
                span = doc[start:end]
                entity_type = self._get_entity_type_for_matcher(matcher_name)

                mention = EntityMention(
                    text=span.text,
                    normalized_form=self._normalize_entity_name(span.text),
                    entity_type=entity_type,
                    start_pos=span.start_char,
                    end_pos=span.end_char,
                    confidence=0.9,  # High confidence for known phrases
                    context=self._extract_context(text, span.start_char, span.end_char)
                )
                mentions.append(mention)

        return mentions

    async def _consolidate_entities(self, mentions: List[EntityMention], text: str) -> List[ExtractedEntity]:
        """Consolidate overlapping mentions into entities."""
        # Group mentions by normalized name and type
        entity_groups = defaultdict(list)
        for mention in mentions:
            key = (mention.normalized_form, mention.entity_type)
            entity_groups[key].append(mention)

        entities = []
        for (normalized_name, entity_type), mention_list in entity_groups.items():
            # Sort mentions by position
            mention_list.sort(key=lambda m: m.start_pos)

            # Remove overlapping mentions (keep highest confidence)
            filtered_mentions = self._remove_overlapping_mentions(mention_list)

            # Create entity
            entity_id = f"{entity_type.value}_{len(entities)}"
            canonical_name = self._determine_canonical_name(filtered_mentions)
            aliases = set(m.text for m in filtered_mentions if m.text != canonical_name)

            # Calculate overall confidence
            if filtered_mentions:
                overall_confidence = sum(m.confidence for m in filtered_mentions) / len(filtered_mentions)
            else:
                overall_confidence = 0.0

            entity = ExtractedEntity(
                entity_id=entity_id,
                canonical_name=canonical_name,
                entity_type=entity_type,
                mentions=filtered_mentions,
                aliases=aliases,
                attributes={},
                relationships={},
                first_mention_pos=filtered_mentions[0].start_pos if filtered_mentions else 0,
                mention_count=len(filtered_mentions),
                confidence=overall_confidence
            )

            entities.append(entity)

        return entities

    async def _post_process_by_content_type(self,
                                          entities: List[ExtractedEntity],
                                          content_type: ContentType,
                                          context: Optional[Dict[str, Any]]) -> List[ExtractedEntity]:
        """Apply content-type specific post-processing."""
        if content_type == ContentType.CHARACTER:
            # For character content, prioritize character entities
            entities = [e for e in entities if e.entity_type == EntityType.CHARACTER] + \
                      [e for e in entities if e.entity_type != EntityType.CHARACTER]

        elif content_type == ContentType.WORLDVIEW:
            # For worldview content, prioritize locations and concepts
            priority_types = {EntityType.LOCATION, EntityType.CONCEPT, EntityType.ORGANIZATION}
            entities = [e for e in entities if e.entity_type in priority_types] + \
                      [e for e in entities if e.entity_type not in priority_types]

        elif content_type == ContentType.PLOT:
            # For plot content, balance all entity types
            pass

        elif content_type == ContentType.SCENE:
            # For scene content, prioritize locations and characters
            priority_types = {EntityType.LOCATION, EntityType.CHARACTER}
            entities = [e for e in entities if e.entity_type in priority_types] + \
                      [e for e in entities if e.entity_type not in priority_types]

        elif content_type == ContentType.DIALOGUE:
            # For dialogue content, prioritize characters and techniques
            priority_types = {EntityType.CHARACTER, EntityType.TECHNIQUE}
            entities = [e for e in entities if e.entity_type in priority_types] + \
                      [e for e in entities if e.entity_type not in priority_types]

        return entities

    async def _extract_relationships(self, entities: List[ExtractedEntity], text: str) -> List[ExtractedEntity]:
        """Extract relationships between entities."""
        # Relationship patterns
        relationship_patterns = [
            (r'([^，。]+)的(?:师父|徒弟|弟子)', 'mentor_student'),
            (r'([^，。]+)和([^，。]+)(?:是|乃)(?:师兄弟|好友|敌人)', 'peer_relationship'),
            (r'([^，。]+)(?:来自|属于)([^，。]+)', 'belongs_to'),
            (r'([^，。]+)(?:位于|在)([^，。]+)', 'located_in'),
        ]

        entity_name_to_id = {e.canonical_name: e.entity_id for e in entities}

        for entity in entities:
            for pattern, rel_type in relationship_patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    entity1, entity2 = match.groups()
                    entity1_clean = self._normalize_entity_name(entity1)
                    entity2_clean = self._normalize_entity_name(entity2)

                    # Check if both entities are in our extracted set
                    if entity1_clean in entity_name_to_id and entity2_clean in entity_name_to_id:
                        if rel_type not in entity.relationships:
                            entity.relationships[rel_type] = []
                        entity.relationships[rel_type].append(entity_name_to_id[entity2_clean])

        return entities

    async def _update_knowledge_base(self, entities: List[ExtractedEntity]):
        """Update the entity knowledge base with extracted entities."""
        for entity in entities:
            kb_key = entity.entity_type.value + 's'  # e.g., 'character' -> 'characters'
            if kb_key in self.entity_kb:
                self.entity_kb[kb_key][entity.entity_id] = {
                    'canonical_name': entity.canonical_name,
                    'aliases': list(entity.aliases),
                    'mention_count': entity.mention_count,
                    'confidence': entity.confidence,
                    'attributes': entity.attributes,
                    'relationships': entity.relationships
                }

    def _normalize_entity_name(self, name: str) -> str:
        """Normalize entity name for comparison."""
        # Remove common suffixes and prefixes
        name = re.sub(r'(?:前辈|大人|公子|师兄|师姐|道友)$', '', name)
        name = re.sub(r'^(?:老|小)', '', name)
        return name.strip()

    def _extract_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Extract context around an entity mention."""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end]

    def _map_spacy_entity_type(self, spacy_label: str) -> Optional[EntityType]:
        """Map spaCy entity labels to our entity types."""
        mapping = {
            'PERSON': EntityType.CHARACTER,
            'GPE': EntityType.LOCATION,
            'LOC': EntityType.LOCATION,
            'ORG': EntityType.ORGANIZATION,
            'TIME': EntityType.TIME,
            'EVENT': EntityType.EVENT,
        }
        return mapping.get(spacy_label)

    def _get_entity_type_for_matcher(self, matcher_name: str) -> EntityType:
        """Get entity type for phrase matcher."""
        mapping = {
            'characters': EntityType.CHARACTER,
            'locations': EntityType.LOCATION,
        }
        return mapping.get(matcher_name, EntityType.CONCEPT)

    def _remove_overlapping_mentions(self, mentions: List[EntityMention]) -> List[EntityMention]:
        """Remove overlapping mentions, keeping the one with highest confidence."""
        if not mentions:
            return []

        # Sort by start position
        sorted_mentions = sorted(mentions, key=lambda m: m.start_pos)
        filtered = [sorted_mentions[0]]

        for mention in sorted_mentions[1:]:
            last_added = filtered[-1]
            # Check for overlap
            if mention.start_pos < last_added.end_pos:
                # Overlapping - keep the one with higher confidence
                if mention.confidence > last_added.confidence:
                    filtered[-1] = mention
            else:
                # No overlap - add to filtered list
                filtered.append(mention)

        return filtered

    def _determine_canonical_name(self, mentions: List[EntityMention]) -> str:
        """Determine the canonical name from mentions."""
        if not mentions:
            return ""

        # Count frequency of each mention text
        name_counts = Counter(m.text for m in mentions)

        # Return the most frequent name
        return name_counts.most_common(1)[0][0]

    def get_entity_statistics(self) -> Dict[str, Any]:
        """Get statistics about extracted entities."""
        stats = {
            'total_entities': 0,
            'by_type': {},
            'knowledge_base_size': {},
        }

        for kb_key, entities in self.entity_kb.items():
            stats['knowledge_base_size'][kb_key] = len(entities)
            stats['total_entities'] += len(entities)

        return stats

    def search_entities(self,
                       query: str,
                       entity_type: Optional[EntityType] = None,
                       min_confidence: float = 0.0) -> List[Dict[str, Any]]:
        """Search for entities in the knowledge base."""
        results = []

        for kb_key, entities in self.entity_kb.items():
            for entity_id, entity_data in entities.items():
                # Filter by type if specified
                if entity_type and not kb_key.startswith(entity_type.value):
                    continue

                # Filter by confidence
                if entity_data['confidence'] < min_confidence:
                    continue

                # Search in canonical name and aliases
                if (query.lower() in entity_data['canonical_name'].lower() or
                    any(query.lower() in alias.lower() for alias in entity_data['aliases'])):
                    results.append({
                        'entity_id': entity_id,
                        'canonical_name': entity_data['canonical_name'],
                        'entity_type': kb_key[:-1],  # Remove 's' suffix
                        'confidence': entity_data['confidence'],
                        'mention_count': entity_data['mention_count'],
                        'aliases': entity_data['aliases']
                    })

        return sorted(results, key=lambda x: x['confidence'], reverse=True)