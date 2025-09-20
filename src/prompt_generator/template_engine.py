"""
Prompt模板引擎
提供灵活的prompt模板系统
"""

from typing import Dict, Any, Optional, List, Tuple
import json
import re
from pathlib import Path


class PromptTemplateEngine:
    """Prompt模板引擎"""

    def __init__(self):
        """初始化模板引擎"""
        self.templates = self._load_default_templates()
        self.custom_templates = {}
        self.variables = {}

    def _load_default_templates(self) -> Dict[str, str]:
        """加载默认模板"""
        return {
            # =========================================================================
            # 系统提示词模板
            # =========================================================================
            "system_prompt": """你是一位精通东方玄幻小说创作的专业作家，正在创作《{novel_title}》。

## 作品信息
- **作品名称**：{novel_title}
- **作品简介**：{novel_description}
- **作者**：{author}
- **类型**：{genre}

## 世界观设定

### 九域体系
{domains}

### 核心概念
{core_concepts}

### 法则链系统
{law_chains}

## 创作规范
{creation_rules}

请基于以上设定，创作符合世界观的精彩内容。注意保持风格一致性，角色行为合理性，以及情节的逻辑性。""",

            # =========================================================================
            # 场景模板
            # =========================================================================

            "scene_narrative": """请为第{chapter_number}章创作一个{scene_type}。

## 前情提要
{previous_context}

## 本章主要角色
{characters}

## 当前冲突状态
{conflicts}

## 可用剧情钩子
{story_hooks}

## 场景要求
{scene_requirements}

请创作约{word_count}字的内容，确保：
1. 自然承接前文
2. 推进主线剧情
3. 展现角色性格
4. 适当运用法则链元素
5. 为后续发展留下伏笔""",

            "scene_battle": """请为第{chapter_number}章创作一个精彩的{scene_type}。

## 战斗背景
{previous_context}

## 参战双方
{characters}

## 冲突焦点
{conflicts}

## 战斗要素
{story_hooks}

## 战斗场景要求
{scene_requirements}

请创作约{word_count}字的战斗场景，必须包含：
1. 详细的战斗动作描写
2. 法则链的创造性运用
3. 战斗策略和心理博弈
4. 环境互动和地利运用
5. 战斗的转折点和高潮
6. 明确的战斗结果和影响""",

            "scene_dialogue": """请为第{chapter_number}章创作一个{scene_type}。

## 对话背景
{previous_context}

## 对话参与者
{characters}

## 对话目的
{conflicts}

## 信息要点
{story_hooks}

## 对话场景要求
{scene_requirements}

请创作约{word_count}字的对话场景，要求：
1. 对话自然流畅，符合角色身份
2. 通过对话推进情节或揭示信息
3. 展现角色性格和关系变化
4. 适当的动作和表情描写
5. 对话节奏张弛有度""",

            "scene_exposition": """请为第{chapter_number}章创作一个{scene_type}。

## 说明背景
{previous_context}

## 相关角色
{characters}

## 核心信息
{conflicts}

## 世界观要素
{story_hooks}

## 说明场景要求
{scene_requirements}

请创作约{word_count}字的说明内容，包括：
1. 清晰介绍世界观设定或背景信息
2. 自然融入叙事，避免生硬说教
3. 通过角色视角展现
4. 配合适当的场景描写
5. 为后续剧情做铺垫""",

            "scene_development": """请为第{chapter_number}章创作一个{scene_type}。

## 发展背景
{previous_context}

## 成长角色
{characters}

## 成长契机
{conflicts}

## 成长要素
{story_hooks}

## 发展场景要求
{scene_requirements}

请创作约{word_count}字的角色发展场景，展现：
1. 角色的内心挣扎和领悟
2. 能力或认知的具体提升
3. 成长的代价和困难
4. 外在表现的变化
5. 对未来的影响和意义""",

            # =========================================================================
            # 特殊场景模板
            # =========================================================================

            "scene_flashback": """请创作一个回忆场景，展现过去的重要事件。

## 回忆触发点
{trigger}

## 回忆主角
{characters}

## 回忆内容
{memory_content}

要求：
1. 自然的回忆过渡
2. 与现在的关联
3. 情感渲染到位
4. 补充重要背景信息""",

            "scene_dream": """请创作一个梦境场景，展现角色的潜意识。

## 做梦者
{dreamer}

## 梦境主题
{dream_theme}

## 象征意义
{symbolism}

要求：
1. 梦境的超现实感
2. 隐喻和象征运用
3. 与角色心理状态呼应
4. 可能的预言性质""",

            # =========================================================================
            # 章节结构模板
            # =========================================================================

            "chapter_opening": """## 第{chapter_number}章 {chapter_title}

{opening_scene}

本章需要完成：
- {objective_1}
- {objective_2}
- {objective_3}""",

            "chapter_closing": """{closing_scene}

## 本章总结
- 完成事件：{completed_events}
- 角色变化：{character_changes}
- 留下悬念：{cliffhangers}
- 下章预告：{next_preview}""",

            # =========================================================================
            # 组合技模板
            # =========================================================================

            "law_chain_combination": """法则链组合：{chain_1} + {chain_2}

## 组合效果
{combination_effect}

## 施展描写
{casting_description}

## 代价消耗
- 链疲劳：{fatigue_cost}
- 污染度：{pollution_increase}
- 因果债：{karma_debt}""",

            # =========================================================================
            # 冲突升级模板
            # =========================================================================

            "conflict_escalation": """## 冲突升级

### 当前阶段
{current_stage}

### 升级触发
{escalation_trigger}

### 新的局势
{new_situation}

### 各方反应
{parties_reaction}

### 潜在后果
{potential_consequences}"""
        }

    def get_template(self, template_name: str) -> str:
        """
        获取模板

        Args:
            template_name: 模板名称

        Returns:
            模板字符串
        """
        # 优先查找自定义模板
        if template_name in self.custom_templates:
            return self.custom_templates[template_name]

        # 查找默认模板
        if template_name in self.templates:
            return self.templates[template_name]

        # 如果都没有，返回基础模板
        return self._get_fallback_template()

    def _get_fallback_template(self) -> str:
        """获取后备模板"""
        return """请创作第{chapter_number}章的内容。

前情提要：
{previous_context}

本章要求：
{requirements}

请创作约{word_count}字的内容。"""

    def add_custom_template(self, name: str, template: str):
        """
        添加自定义模板

        Args:
            name: 模板名称
            template: 模板内容
        """
        self.custom_templates[name] = template

    def render(self, template_name: str, **kwargs) -> str:
        """
        渲染模板

        Args:
            template_name: 模板名称
            **kwargs: 模板变量

        Returns:
            渲染后的文本
        """
        template = self.get_template(template_name)

        # 合并全局变量和传入变量
        variables = {**self.variables, **kwargs}

        # 处理缺失变量
        def replace_variable(match):
            var_name = match.group(1)
            if var_name in variables:
                value = variables[var_name]
                # 处理不同类型的值
                if isinstance(value, (list, dict)):
                    return json.dumps(value, ensure_ascii=False, indent=2)
                return str(value)
            else:
                # 返回占位符或默认值
                return f"[{var_name}]"

        # 使用正则表达式替换变量
        rendered = re.sub(r'\{(\w+)\}', replace_variable, template)

        return rendered

    def set_global_variable(self, name: str, value: Any):
        """
        设置全局变量

        Args:
            name: 变量名
            value: 变量值
        """
        self.variables[name] = value

    def clear_global_variables(self):
        """清空全局变量"""
        self.variables.clear()

    def create_template_from_example(
        self,
        name: str,
        example_text: str,
        variables: List[str]
    ) -> str:
        """
        从示例文本创建模板

        Args:
            name: 模板名称
            example_text: 示例文本
            variables: 要替换为变量的文本列表

        Returns:
            创建的模板
        """
        template = example_text

        # 将指定文本替换为变量
        for i, var_text in enumerate(variables):
            var_name = f"var_{i+1}"
            template = template.replace(var_text, f"{{{var_name}}}")

        self.custom_templates[name] = template
        return template

    def validate_template(self, template: str) -> Tuple[bool, List[str]]:
        """
        验证模板格式

        Args:
            template: 模板文本

        Returns:
            (是否有效, 变量列表)
        """
        # 查找所有变量
        variables = re.findall(r'\{(\w+)\}', template)

        # 检查括号匹配
        open_count = template.count('{')
        close_count = template.count('}')

        is_valid = open_count == close_count

        return is_valid, list(set(variables))

    def export_templates(self, filepath: str):
        """
        导出模板到文件

        Args:
            filepath: 文件路径
        """
        export_data = {
            "default_templates": self.templates,
            "custom_templates": self.custom_templates,
            "metadata": {
                "version": "1.0.0",
                "exported_at": datetime.now().isoformat()
            }
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

    def import_templates(self, filepath: str):
        """
        从文件导入模板

        Args:
            filepath: 文件路径
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if "custom_templates" in data:
            self.custom_templates.update(data["custom_templates"])

    def get_template_variables(self, template_name: str) -> List[str]:
        """
        获取模板中的变量列表

        Args:
            template_name: 模板名称

        Returns:
            变量名列表
        """
        template = self.get_template(template_name)
        _, variables = self.validate_template(template)
        return variables

    def preview_template(self, template_name: str, **kwargs) -> str:
        """
        预览模板效果（用示例数据填充）

        Args:
            template_name: 模板名称
            **kwargs: 部分变量值

        Returns:
            预览文本
        """
        variables = self.get_template_variables(template_name)

        # 为缺失的变量提供示例值
        example_values = {
            "novel_title": "《裂世九域·法则链纪元》",
            "chapter_number": "十七",
            "scene_type": "战斗场景",
            "word_count": "2000",
            "previous_context": "主角刚刚突破到新的境界...",
            "characters": "林潜（主角），炎无极（对手）",
            "conflicts": "争夺古老传承的决战",
            "story_hooks": "命运链与因果链的首次融合",
            "scene_requirements": "展现新境界的力量",
            "chapter_title": "宿命之战",
            "opening_scene": "晨光初现，决战之地...",
            "objective_1": "展现主角新能力",
            "objective_2": "揭示对手的秘密",
            "objective_3": "推进主线剧情"
        }

        # 合并示例值和传入值
        preview_vars = {**example_values, **kwargs}

        return self.render(template_name, **preview_vars)

    def list_templates(self) -> Dict[str, List[str]]:
        """
        列出所有可用模板

        Returns:
            模板分类列表
        """
        return {
            "default": list(self.templates.keys()),
            "custom": list(self.custom_templates.keys())
        }

    def merge_templates(self, template_names: List[str], separator: str = "\n\n") -> str:
        """
        合并多个模板

        Args:
            template_names: 模板名称列表
            separator: 分隔符

        Returns:
            合并后的模板
        """
        templates = [self.get_template(name) for name in template_names]
        return separator.join(templates)