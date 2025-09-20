"""
上下文窗口管理器
管理Claude的上下文窗口，优化token使用
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
try:
    import tiktoken
except ImportError:
    tiktoken = None
import heapq
import logging

logger = logging.getLogger(__name__)


@dataclass
class ContextItem:
    """上下文项"""
    content: str
    priority: int  # 优先级（越高越重要）
    tokens: int
    category: str  # worldbuilding/character/plot/dialogue等
    metadata: Dict[str, Any]

    def __lt__(self, other):
        """用于优先队列比较"""
        return self.priority > other.priority  # 优先级高的排前面


class ContextWindowManager:
    """上下文窗口管理器"""

    # Claude 3的上下文限制
    MAX_TOKENS = 200000  # Claude 3 Opus的上下文窗口
    RESERVED_TOKENS = 20000  # 为响应预留的token数

    # 不同类别的默认优先级
    CATEGORY_PRIORITIES = {
        "system_prompt": 100,
        "current_scene": 90,
        "main_characters": 85,
        "active_conflicts": 80,
        "worldbuilding": 75,
        "previous_context": 70,
        "story_hooks": 65,
        "law_chains": 60,
        "side_characters": 50,
        "background_info": 40,
        "optional_details": 30
    }

    def __init__(self, model: str = "cl100k_base"):
        """
        初始化上下文管理器

        Args:
            model: tokenizer模型名称
        """
        try:
            self.encoder = tiktoken.get_encoding(model)
        except:
            # 如果无法获取指定编码，使用默认的cl100k_base
            self.encoder = tiktoken.get_encoding("cl100k_base")

        self.context_items: List[ContextItem] = []
        self.current_tokens = 0
        self.categories_count = {}

    def count_tokens(self, text: str) -> int:
        """
        计算文本的token数量

        Args:
            text: 要计算的文本

        Returns:
            token数量
        """
        try:
            return len(self.encoder.encode(text))
        except:
            # 粗略估算：中文约1.5字符/token，英文约4字符/token
            chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
            english_chars = len(text) - chinese_chars
            return int(chinese_chars / 1.5 + english_chars / 4)

    def add_context(
        self,
        content: str,
        priority: Optional[int] = None,
        category: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        添加上下文内容

        Args:
            content: 内容文本
            priority: 优先级（如果不指定，使用类别默认优先级）
            category: 内容类别
            metadata: 元数据

        Returns:
            是否成功添加
        """
        if not content:
            return False

        # 计算token数
        tokens = self.count_tokens(content)

        # 检查是否超出限制
        if tokens > self.MAX_TOKENS - self.RESERVED_TOKENS:
            logger.warning(f"Content too large: {tokens} tokens")
            # 尝试压缩内容
            content = self._compress_content(content, category)
            tokens = self.count_tokens(content)

        # 确定优先级
        if priority is None:
            priority = self.CATEGORY_PRIORITIES.get(category, 50)

        # 创建上下文项
        item = ContextItem(
            content=content,
            priority=priority,
            tokens=tokens,
            category=category,
            metadata=metadata or {}
        )

        # 检查空间并添加
        if self.current_tokens + tokens > self.MAX_TOKENS - self.RESERVED_TOKENS:
            self._prune_context(tokens)

        self.context_items.append(item)
        self.current_tokens += tokens

        # 更新类别计数
        self.categories_count[category] = self.categories_count.get(category, 0) + 1

        logger.debug(f"Added {category} context: {tokens} tokens, priority {priority}")
        return True

    def _prune_context(self, required_tokens: int):
        """
        修剪上下文以腾出空间

        Args:
            required_tokens: 需要的token空间
        """
        target_tokens = (self.MAX_TOKENS - self.RESERVED_TOKENS) * 0.8  # 保留80%空间
        need_to_free = self.current_tokens + required_tokens - target_tokens

        if need_to_free <= 0:
            return

        # 按优先级排序（低优先级在前）
        self.context_items.sort(key=lambda x: x.priority)

        freed_tokens = 0
        items_to_remove = []

        for item in self.context_items:
            # 不删除高优先级内容
            if item.priority >= 80:
                break

            items_to_remove.append(item)
            freed_tokens += item.tokens

            if freed_tokens >= need_to_free:
                break

        # 删除选中的项
        for item in items_to_remove:
            self.context_items.remove(item)
            self.current_tokens -= item.tokens
            self.categories_count[item.category] -= 1

        logger.info(f"Pruned {len(items_to_remove)} items, freed {freed_tokens} tokens")

    def _compress_content(self, content: str, category: str) -> str:
        """
        压缩内容以减少token使用

        Args:
            content: 原始内容
            category: 内容类别

        Returns:
            压缩后的内容
        """
        # 根据类别采用不同的压缩策略
        if category == "previous_context":
            # 前情提要：保留关键事件
            lines = content.split('\n')
            important_lines = [line for line in lines if any(
                keyword in line for keyword in ['关键', '重要', '主要', '决定', '改变']
            )]
            if important_lines:
                return '\n'.join(important_lines[:10])  # 最多10行

        elif category == "worldbuilding":
            # 世界观：保留核心设定
            if len(content) > 2000:
                return content[:2000] + "\n[部分内容已省略...]"

        elif category == "dialogue":
            # 对话：保留最近的对话
            lines = content.split('\n')
            if len(lines) > 20:
                return '\n'.join(lines[-20:])  # 保留最后20行

        # 默认压缩：截断
        max_length = 3000
        if len(content) > max_length:
            return content[:max_length] + "\n[内容已截断...]"

        return content

    def get_optimized_context(self) -> str:
        """
        获取优化后的完整上下文

        Returns:
            优化后的上下文文本
        """
        # 按优先级排序
        sorted_items = sorted(self.context_items, key=lambda x: x.priority, reverse=True)

        # 组织上下文
        context_parts = []
        current_category = None

        for item in sorted_items:
            # 添加类别标题
            if item.category != current_category:
                if item.category != "general":
                    context_parts.append(f"\n## {self._get_category_title(item.category)}\n")
                current_category = item.category

            context_parts.append(item.content)

        return "\n".join(context_parts)

    def _get_category_title(self, category: str) -> str:
        """获取类别标题"""
        titles = {
            "system_prompt": "系统设定",
            "current_scene": "当前场景",
            "main_characters": "主要角色",
            "active_conflicts": "活跃冲突",
            "worldbuilding": "世界观背景",
            "previous_context": "前情提要",
            "story_hooks": "剧情钩子",
            "law_chains": "法则链系统",
            "side_characters": "次要角色",
            "background_info": "背景信息",
            "optional_details": "补充细节"
        }
        return titles.get(category, category)

    def get_context_summary(self) -> Dict[str, Any]:
        """
        获取上下文摘要信息

        Returns:
            上下文统计信息
        """
        summary = {
            "total_tokens": self.current_tokens,
            "max_tokens": self.MAX_TOKENS,
            "reserved_tokens": self.RESERVED_TOKENS,
            "usage_percentage": (self.current_tokens / (self.MAX_TOKENS - self.RESERVED_TOKENS)) * 100,
            "items_count": len(self.context_items),
            "categories": self.categories_count,
            "priority_distribution": self._get_priority_distribution()
        }

        return summary

    def _get_priority_distribution(self) -> Dict[str, int]:
        """获取优先级分布"""
        distribution = {
            "critical (>90)": 0,
            "high (70-90)": 0,
            "medium (50-70)": 0,
            "low (30-50)": 0,
            "optional (<30)": 0
        }

        for item in self.context_items:
            if item.priority > 90:
                distribution["critical (>90)"] += 1
            elif item.priority > 70:
                distribution["high (70-90)"] += 1
            elif item.priority > 50:
                distribution["medium (50-70)"] += 1
            elif item.priority > 30:
                distribution["low (30-50)"] += 1
            else:
                distribution["optional (<30)"] += 1

        return distribution

    def clear(self):
        """清空上下文"""
        self.context_items.clear()
        self.current_tokens = 0
        self.categories_count.clear()
        logger.info("Context cleared")

    def remove_category(self, category: str):
        """
        删除特定类别的所有内容

        Args:
            category: 要删除的类别
        """
        items_to_remove = [item for item in self.context_items if item.category == category]

        for item in items_to_remove:
            self.context_items.remove(item)
            self.current_tokens -= item.tokens

        if category in self.categories_count:
            del self.categories_count[category]

        logger.info(f"Removed {len(items_to_remove)} items from category {category}")

    def get_total_tokens(self) -> int:
        """获取当前总token数"""
        return self.current_tokens

    def has_space(self, tokens: int) -> bool:
        """
        检查是否有足够空间

        Args:
            tokens: 需要的token数

        Returns:
            是否有足够空间
        """
        return self.current_tokens + tokens <= self.MAX_TOKENS - self.RESERVED_TOKENS

    def estimate_remaining_space(self) -> int:
        """估算剩余空间（token数）"""
        return self.MAX_TOKENS - self.RESERVED_TOKENS - self.current_tokens

    def optimize_for_chapter(self, chapter_number: int):
        """
        针对特定章节优化上下文

        Args:
            chapter_number: 章节号
        """
        # 根据章节调整优先级
        if chapter_number <= 3:
            # 前期章节：重视世界观介绍
            self._adjust_category_priority("worldbuilding", 10)
            self._adjust_category_priority("background_info", 5)

        elif chapter_number <= 10:
            # 中前期：平衡发展
            self._adjust_category_priority("main_characters", 5)
            self._adjust_category_priority("active_conflicts", 5)

        else:
            # 中后期：重视剧情和角色
            self._adjust_category_priority("previous_context", 10)
            self._adjust_category_priority("story_hooks", 5)
            self._adjust_category_priority("worldbuilding", -10)

    def _adjust_category_priority(self, category: str, adjustment: int):
        """
        调整特定类别的优先级

        Args:
            category: 类别
            adjustment: 调整值（正值提高，负值降低）
        """
        for item in self.context_items:
            if item.category == category:
                item.priority += adjustment

        logger.debug(f"Adjusted {category} priority by {adjustment}")

    def export_context(self) -> List[Dict[str, Any]]:
        """
        导出上下文数据

        Returns:
            上下文数据列表
        """
        export_data = []

        for item in self.context_items:
            export_data.append({
                "content": item.content,
                "priority": item.priority,
                "tokens": item.tokens,
                "category": item.category,
                "metadata": item.metadata
            })

        return export_data

    def import_context(self, data: List[Dict[str, Any]]):
        """
        导入上下文数据

        Args:
            data: 上下文数据列表
        """
        self.clear()

        for item_data in data:
            self.add_context(
                content=item_data["content"],
                priority=item_data.get("priority"),
                category=item_data.get("category", "general"),
                metadata=item_data.get("metadata")
            )