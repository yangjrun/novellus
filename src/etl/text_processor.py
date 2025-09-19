"""
Text Processor for Chinese Novel Content

Specialized text preprocessing and cleaning for Chinese novel content including:
- Chinese text segmentation and tokenization
- Traditional/Simplified Chinese conversion
- Text normalization and cleaning
- Content structure extraction
- Language-specific preprocessing
"""

import re
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import jieba
import jieba.posseg as pseg
from opencc import OpenCC
import unicodedata

logger = logging.getLogger(__name__)


class TextType(Enum):
    """Types of text content for different processing strategies."""
    NARRATIVE = "narrative"      # 叙述文本
    DIALOGUE = "dialogue"        # 对话文本
    DESCRIPTION = "description"  # 描述文本
    SYSTEM_TEXT = "system"       # 系统设定文本


@dataclass
class TextProcessingConfig:
    """Configuration for text processing operations."""
    # Chinese processing
    enable_segmentation: bool = True
    enable_pos_tagging: bool = True
    custom_dict_path: Optional[str] = None

    # Character conversion
    traditional_to_simplified: bool = False
    simplified_to_traditional: bool = False

    # Cleaning options
    remove_extra_whitespace: bool = True
    normalize_punctuation: bool = True
    remove_special_chars: bool = False
    preserve_line_breaks: bool = True

    # Content extraction
    extract_dialogue: bool = True
    extract_names: bool = True
    extract_locations: bool = True
    extract_time_expressions: bool = True

    # Validation
    min_content_length: int = 10
    max_content_length: int = 50000


@dataclass
class ProcessedText:
    """Result of text processing operations."""
    original_text: str
    cleaned_text: str
    segments: List[str]
    pos_tags: List[Tuple[str, str]]
    extracted_elements: Dict[str, List[str]]
    metadata: Dict[str, Any]
    text_type: TextType
    processing_time: float


class ChineseTextNormalizer:
    """Specialized Chinese text normalization."""

    def __init__(self):
        # Initialize OpenCC converters
        self.s2t_converter = OpenCC('s2t')  # Simplified to Traditional
        self.t2s_converter = OpenCC('t2s')  # Traditional to Simplified

        # Punctuation normalization mappings
        self.punctuation_map = {
            # Full-width to half-width
            '，': ',', '。': '.', '！': '!', '？': '?',
            '；': ';', '：': ':', '（': '(', '）': ')',
            '【': '[', '】': ']', '《': '<', '》': '>',
            '"': '"', '"': '"', ''': "'", ''': "'",

            # Special Chinese punctuation
            '…': '...', '——': '--', '－': '-',
        }

        # Dialogue markers patterns
        self.dialogue_patterns = [
            r'"[^"]*"',                    # "dialogue"
            r'"[^"]*"',                    # "dialogue"
            r'「[^」]*」',                  # 「dialogue」
            r'『[^』]*』',                  # 『dialogue』
        ]

        # Name patterns (common Chinese surname + given name patterns)
        self.name_patterns = [
            r'[王李张刘陈杨黄赵周吴徐孙朱马胡郭林何高梁郑罗宋谢唐韩曹许邓萧冯曾程蔡彭潘袁于董余苏叶吕魏蒋田杜丁沈姜范江傅钟卢汪戴崔任陆廖姚方金邱夏谭韦贾邹石熊孟秦阎薛侯雷白龙段郝孔邵史毛常万顾赖武康贺严尹钱施牛洪龚][一-龯]{1,3}',
        ]

        # Location patterns
        self.location_patterns = [
            r'[东西南北中][一-龯]*[域界州城郡国]',     # 方位+地名
            r'[一-龯]*[山峰谷川江河湖海岛洲]',         # 地理特征
            r'[一-龯]*[城镇村寨堡关隘]',               # 建筑聚集地
            r'[一-龯]*[宫殿府邸院楼阁塔]',             # 建筑物
        ]

        # Time expression patterns
        self.time_patterns = [
            r'[一二三四五六七八九十百千万亿]*[年月日时辰]',
            r'[春夏秋冬][天日季]',
            r'[早中晚夜深][上午时分]',
            r'[今昨明][天日夜]',
        ]

    def normalize_text(self, text: str, config: TextProcessingConfig) -> str:
        """Normalize Chinese text according to configuration."""
        if not text:
            return ""

        normalized = text

        # Character conversion
        if config.traditional_to_simplified:
            normalized = self.t2s_converter.convert(normalized)
        elif config.simplified_to_traditional:
            normalized = self.s2t_converter.convert(normalized)

        # Unicode normalization
        normalized = unicodedata.normalize('NFKC', normalized)

        # Punctuation normalization
        if config.normalize_punctuation:
            for old_punct, new_punct in self.punctuation_map.items():
                normalized = normalized.replace(old_punct, new_punct)

        # Whitespace normalization
        if config.remove_extra_whitespace:
            # Remove extra spaces but preserve line breaks if configured
            if config.preserve_line_breaks:
                normalized = re.sub(r' +', ' ', normalized)
                normalized = re.sub(r'\n +', '\n', normalized)
                normalized = re.sub(r' +\n', '\n', normalized)
            else:
                normalized = re.sub(r'\s+', ' ', normalized)

        # Special character removal
        if config.remove_special_chars:
            # Keep Chinese characters, basic punctuation, and numbers
            normalized = re.sub(r'[^\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\w\s.,!?;:()\[\]"\'<>-]', '', normalized)

        return normalized.strip()

    def extract_dialogues(self, text: str) -> List[str]:
        """Extract dialogue content from text."""
        dialogues = []
        for pattern in self.dialogue_patterns:
            matches = re.findall(pattern, text)
            dialogues.extend(matches)
        return dialogues

    def extract_names(self, text: str) -> List[str]:
        """Extract potential character names."""
        names = []
        for pattern in self.name_patterns:
            matches = re.findall(pattern, text)
            names.extend(matches)
        return list(set(names))  # Remove duplicates

    def extract_locations(self, text: str) -> List[str]:
        """Extract location references."""
        locations = []
        for pattern in self.location_patterns:
            matches = re.findall(pattern, text)
            locations.extend(matches)
        return list(set(locations))

    def extract_time_expressions(self, text: str) -> List[str]:
        """Extract time-related expressions."""
        times = []
        for pattern in self.time_patterns:
            matches = re.findall(pattern, text)
            times.extend(matches)
        return list(set(times))


class TextProcessor:
    """
    Main text processor for Chinese novel content.

    Provides comprehensive text processing capabilities including:
    - Text cleaning and normalization
    - Chinese text segmentation
    - Part-of-speech tagging
    - Content element extraction
    - Text type detection and processing
    """

    def __init__(self,
                 enable_chinese_segmentation: bool = True,
                 traditional_to_simplified: bool = False,
                 custom_dict_path: Optional[str] = None):

        self.config = TextProcessingConfig(
            enable_segmentation=enable_chinese_segmentation,
            traditional_to_simplified=traditional_to_simplified,
            custom_dict_path=custom_dict_path
        )

        self.normalizer = ChineseTextNormalizer()

        # Initialize jieba with custom dictionary if provided
        if custom_dict_path:
            jieba.load_userdict(custom_dict_path)

        # Load novel-specific terms
        self._load_novel_terms()

        logger.info("TextProcessor initialized")

    def _load_novel_terms(self):
        """Load novel-specific terms and names into jieba dictionary."""
        # Add novel-specific terms that should be recognized as single units
        novel_terms = [
            # 九域相关
            "裂世九域", "法则链纪元", "天权域", "地煞域", "人皇域",
            "修罗域", "魔渊域", "仙境域", "神界域", "混沌域", "虚无域",

            # 修炼体系
            "法则链", "灵力", "灵脉", "丹田", "经脉", "神魂", "元神",
            "筑基期", "结丹期", "元婴期", "化神期", "合体期", "大乘期",

            # 常见小说词汇
            "修炼者", "修仙者", "武者", "剑修", "丹师", "阵法师",
            "灵石", "灵药", "功法", "神通", "法宝", "灵器", "法器",
        ]

        for term in novel_terms:
            jieba.add_word(term, freq=1000)  # High frequency for better recognition

    async def clean_text(self, text: str, text_type: TextType = TextType.NARRATIVE) -> str:
        """
        Clean and normalize input text.

        Args:
            text: Raw input text
            text_type: Type of text content for specialized processing

        Returns:
            Cleaned and normalized text
        """
        if not text or not text.strip():
            return ""

        # Apply normalization
        cleaned = self.normalizer.normalize_text(text, self.config)

        # Text type specific processing
        if text_type == TextType.DIALOGUE:
            # For dialogue, preserve quotation marks and speaker indicators
            cleaned = self._process_dialogue_text(cleaned)
        elif text_type == TextType.DESCRIPTION:
            # For descriptions, focus on clarity and structure
            cleaned = self._process_description_text(cleaned)
        elif text_type == TextType.SYSTEM_TEXT:
            # For system text, maintain technical terms and structure
            cleaned = self._process_system_text(cleaned)

        return cleaned

    def _process_dialogue_text(self, text: str) -> str:
        """Specialized processing for dialogue text."""
        # Ensure proper dialogue formatting
        text = re.sub(r'(["""])([^""]*?)(["""])', r'"\2"', text)

        # Clean up speaker tags
        text = re.sub(r'(\w+)[说道：]', r'\1说：', text)

        return text

    def _process_description_text(self, text: str) -> str:
        """Specialized processing for description text."""
        # Enhance readability for descriptive text
        text = re.sub(r'([，。])([一-龯])', r'\1 \2', text)

        return text

    def _process_system_text(self, text: str) -> str:
        """Specialized processing for system/worldview text."""
        # Preserve technical formatting and structure
        return text

    async def segment_text(self, text: str, enable_pos_tagging: bool = True) -> Tuple[List[str], List[Tuple[str, str]]]:
        """
        Segment Chinese text and optionally perform POS tagging.

        Args:
            text: Text to segment
            enable_pos_tagging: Whether to perform part-of-speech tagging

        Returns:
            Tuple of (segments, pos_tags)
        """
        if not self.config.enable_segmentation:
            return [text], []

        segments = []
        pos_tags = []

        if enable_pos_tagging and self.config.enable_pos_tagging:
            # Segment with POS tagging
            words = pseg.cut(text)
            for word, flag in words:
                if word.strip():  # Skip empty segments
                    segments.append(word)
                    pos_tags.append((word, flag))
        else:
            # Simple segmentation
            words = jieba.cut(text)
            segments = [word for word in words if word.strip()]

        return segments, pos_tags

    async def extract_content_elements(self, text: str) -> Dict[str, List[str]]:
        """
        Extract various content elements from text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary of extracted elements by type
        """
        elements = {
            'dialogues': [],
            'names': [],
            'locations': [],
            'time_expressions': [],
            'cultivation_terms': [],
            'action_words': []
        }

        if self.config.extract_dialogue:
            elements['dialogues'] = self.normalizer.extract_dialogues(text)

        if self.config.extract_names:
            elements['names'] = self.normalizer.extract_names(text)

        if self.config.extract_locations:
            elements['locations'] = self.normalizer.extract_locations(text)

        if self.config.extract_time_expressions:
            elements['time_expressions'] = self.normalizer.extract_time_expressions(text)

        # Extract cultivation-related terms
        elements['cultivation_terms'] = self._extract_cultivation_terms(text)

        # Extract action words using POS tagging
        elements['action_words'] = await self._extract_action_words(text)

        return elements

    def _extract_cultivation_terms(self, text: str) -> List[str]:
        """Extract cultivation and fantasy-related terms."""
        cultivation_patterns = [
            r'[一-龯]*[法诀术技能力]',
            r'[一-龯]*[丹药石器宝物]',
            r'[一-龯]*[期阶段层级]境',
            r'[一-龯]*[元神魂识念]',
        ]

        terms = []
        for pattern in cultivation_patterns:
            matches = re.findall(pattern, text)
            terms.extend(matches)

        return list(set(terms))

    async def _extract_action_words(self, text: str) -> List[str]:
        """Extract action words using POS tagging."""
        _, pos_tags = await self.segment_text(text, enable_pos_tagging=True)

        action_words = []
        for word, flag in pos_tags:
            # Extract verbs (v, vd, vn, etc.)
            if flag.startswith('v') and len(word) > 1:
                action_words.append(word)

        return list(set(action_words))

    async def process_text(self,
                          text: str,
                          text_type: TextType = TextType.NARRATIVE,
                          config: Optional[TextProcessingConfig] = None) -> ProcessedText:
        """
        Complete text processing pipeline.

        Args:
            text: Raw input text
            text_type: Type of text content
            config: Optional configuration override

        Returns:
            ProcessedText object with all processing results
        """
        import time
        start_time = time.time()

        # Use provided config or default
        processing_config = config or self.config

        # Validate input
        if not text or len(text) < processing_config.min_content_length:
            raise ValueError(f"Text too short (minimum {processing_config.min_content_length} characters)")

        if len(text) > processing_config.max_content_length:
            logger.warning(f"Text truncated from {len(text)} to {processing_config.max_content_length} characters")
            text = text[:processing_config.max_content_length]

        # Step 1: Clean and normalize
        cleaned_text = await self.clean_text(text, text_type)

        # Step 2: Segment text
        segments, pos_tags = await self.segment_text(cleaned_text, processing_config.enable_pos_tagging)

        # Step 3: Extract content elements
        extracted_elements = await self.extract_content_elements(cleaned_text)

        # Step 4: Generate metadata
        metadata = {
            'original_length': len(text),
            'cleaned_length': len(cleaned_text),
            'segment_count': len(segments),
            'unique_words': len(set(segments)),
            'text_type': text_type.value,
            'processing_config': {
                'segmentation_enabled': processing_config.enable_segmentation,
                'pos_tagging_enabled': processing_config.enable_pos_tagging,
                'traditional_conversion': processing_config.traditional_to_simplified,
            }
        }

        processing_time = time.time() - start_time

        return ProcessedText(
            original_text=text,
            cleaned_text=cleaned_text,
            segments=segments,
            pos_tags=pos_tags,
            extracted_elements=extracted_elements,
            metadata=metadata,
            text_type=text_type,
            processing_time=processing_time
        )

    def update_config(self, **kwargs):
        """Update processing configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        logger.info("Text processor configuration updated")

    def add_custom_terms(self, terms: List[str], freq: int = 1000):
        """Add custom terms to the segmentation dictionary."""
        for term in terms:
            jieba.add_word(term, freq=freq)
        logger.info(f"Added {len(terms)} custom terms to dictionary")

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics and configuration."""
        return {
            'configuration': {
                'segmentation_enabled': self.config.enable_segmentation,
                'pos_tagging_enabled': self.config.enable_pos_tagging,
                'traditional_conversion': self.config.traditional_to_simplified,
                'dialogue_extraction': self.config.extract_dialogue,
                'name_extraction': self.config.extract_names,
                'location_extraction': self.config.extract_locations,
                'min_content_length': self.config.min_content_length,
                'max_content_length': self.config.max_content_length,
            },
            'jieba_status': {
                'dictionary_loaded': True,
                'custom_terms_added': True,
            }
        }