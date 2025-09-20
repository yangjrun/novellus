# Novellus 人工协作创作工作流使用指南

## 概述

Novellus 人工协作创作系统是一个智能创作助手，它不是取代人工创作，而是通过提供结构化的提示词（prompt）、内容分析和优化建议，帮助作者更高效地创作高质量的小说内容。

## 核心理念

- **人机协作**：系统生成prompt → 用户在Claude客户端创作 → 系统分析并提供改进建议
- **迭代优化**：通过多轮优化，逐步提升内容质量
- **质量控制**：自动分析内容质量，提供具体可操作的改进建议
- **灵活控制**：用户完全掌控创作过程，决定是否采纳建议

## 工作流程

### 1. 启动创作会话

```python
# 开始新的创作会话
response = await start_writing_session(
    novel_id="e1fd1aa4-bde2-4c76-8cee-334e54fa47d1",
    chapter_number=17,
    session_name="第17章-林潜突破场景"
)

# 返回示例
{
    "success": true,
    "session": {
        "session_id": "abc123-def456",
        "novel_id": "e1fd1aa4-bde2-4c76-8cee-334e54fa47d1",
        "chapter_number": 17,
        "session_name": "第17章-林潜突破场景",
        "status": "active"
    }
}
```

### 2. 生成创作Prompt

```python
# 生成创作提示词
response = await generate_writing_prompt(
    novel_id="e1fd1aa4-bde2-4c76-8cee-334e54fa47d1",
    chapter_number=17,
    scene_type="breakthrough",  # 突破场景
    focus_characters="林潜,炎无极",
    target_length=2000,
    style="dramatic",  # 戏剧化风格
    special_requirements="详细描述林潜掌握第三条法则链的突破过程，展现时间法则与空间法则的融合"
)

# 返回的prompt可以直接复制到Claude
{
    "success": true,
    "prompt": {
        "copyable_prompt": "【完整的系统提示词和用户提示词，可直接复制】",
        "components": {
            "system": "系统提示词...",
            "user": "用户提示词..."
        }
    },
    "parameters": {
        "suggested_max_tokens": 3000,
        "suggested_temperature": 0.85,
        "model_recommendation": "Claude 3.5 Sonnet"
    }
}
```

### 3. 用户在Claude客户端创作

将生成的prompt复制到Claude客户端，获得创作内容。

### 4. 分析生成内容

```python
# 将Claude生成的内容返回给系统分析
response = await analyze_generated_content(
    novel_id="e1fd1aa4-bde2-4c76-8cee-334e54fa47d1",
    session_id="abc123-def456",
    generated_content="【从Claude复制的生成内容】",
    user_rating=7,  # 用户满意度评分
    content_type="breakthrough"
)

# 获得详细的分析报告
{
    "success": true,
    "analysis": {
        "overall_score": 0.75,
        "recommendation": "良好，建议根据具体建议进行优化",
        "formatted_report": "【格式化的分析报告】"
    },
    "quality_metrics": {
        "narrative_flow": 0.8,
        "dialogue_quality": 0.7,
        "scene_vividness": 0.75,
        "emotional_impact": 0.8,
        "law_chain_accuracy": 0.65
    },
    "strengths": [
        "叙事流畅，过渡自然",
        "场景描写细腻，感官丰富"
    ],
    "weaknesses": [
        "法则链描述不够具体",
        "缺少角色内心活动描写"
    ],
    "suggestions": {
        "content_improvements": [
            "增加法则链突破时的具体感受描述",
            "加入林潜的内心独白，展现其心理变化"
        ],
        "prompt_improvements": [
            "在prompt中明确要求描述法则链的具体表现形式",
            "要求包含角色的心理活动和情感波动"
        ],
        "next_steps": [
            "根据具体建议微调prompt后重新生成"
        ]
    }
}
```

### 5. 优化Prompt（可选）

```python
# 基于分析结果优化prompt
response = await optimize_prompt_based_on_feedback(
    session_id="abc123-def456",
    issues_found="法则链描述不够具体,缺少内心活动",
    desired_improvements="增加法则链细节,深化心理描写,增强戏剧冲突"
)

# 返回优化后的prompt
{
    "success": true,
    "optimized_prompt": {
        "copyable_prompt": "【优化后的完整prompt】",
        "components": {
            "system": "【加强了法则链描写指导的系统提示词】",
            "user": "【增加了心理活动要求的用户提示词】"
        }
    },
    "parameters": {
        "suggested_temperature": 0.9  # 可能会调整温度参数
    },
    "optimization_notes": [
        "根据2个问题进行了优化",
        "应用了3个改进建议",
        "温度参数已根据需求调整"
    ]
}
```

### 6. 迭代改进

重复步骤2-5，直到满意为止。

### 7. 保存最终内容

```python
# 保存最终确定的内容
response = await save_final_content(
    session_id="abc123-def456",
    final_content="【最终满意的内容】",
    content_metadata=json.dumps({
        "version": 3,
        "user_satisfaction": 9,
        "save_to_database": true,
        "batch_id": "batch-id-if-needed",
        "title": "林潜突破·时空法则融合",
        "tags": ["突破", "法则链", "时间法则", "空间法则"],
        "comments": "第三次迭代效果最佳"
    })
)

# 返回保存结果
{
    "success": true,
    "saved": {
        "session_id": "abc123-def456",
        "final_content_length": 2156,
        "saved_to_database": true,
        "segment_id": "segment-uuid"
    },
    "session_summary": {
        "total_iterations": 3,
        "total_time_minutes": 45.5,
        "average_rating": 7.3,
        "best_rating": 9,
        "improvement_trend": "improving"
    }
}
```

## 高级功能

### 比较不同迭代版本

```python
# 比较两次迭代的内容质量
response = await compare_iterations(
    session_id="abc123-def456",
    iteration_a=1,  # 第一次生成
    iteration_b=3   # 第三次生成
)

# 返回详细对比
{
    "comparison": {
        "iteration_a": {
            "overall_score": 0.65,
            "user_rating": 6
        },
        "iteration_b": {
            "overall_score": 0.85,
            "user_rating": 9
        },
        "improvements": {
            "score_change": 0.2,
            "score_change_percentage": "+20.0%",
            "rating_change": 3
        },
        "quality_comparison": {
            "narrative_flow": {
                "a": 0.6,
                "b": 0.85,
                "improved": true
            }
        },
        "recommendation": "迭代B更优"
    }
}
```

### 查看会话历史

```python
# 获取会话的完整历史
response = await get_session_history(
    session_id="abc123-def456"
)

# 返回会话历史记录
{
    "history": {
        "session_info": {
            "session_id": "abc123-def456",
            "chapter_number": 17,
            "status": "completed"
        },
        "iterations": [
            {
                "index": 1,
                "user_rating": 6,
                "overall_score": 0.65,
                "strengths": ["叙事流畅"],
                "weaknesses": ["法则链描述不够具体"]
            },
            {
                "index": 2,
                "user_rating": 8,
                "overall_score": 0.78
            },
            {
                "index": 3,
                "user_rating": 9,
                "overall_score": 0.85
            }
        ],
        "final_content": {
            "saved": true,
            "preview": "最终内容预览..."
        }
    }
}
```

### 获取活跃会话列表

```python
# 查看某个小说的所有活跃创作会话
response = await get_active_sessions(
    novel_id="e1fd1aa4-bde2-4c76-8cee-334e54fa47d1"
)

# 返回活跃会话列表
{
    "sessions": [
        {
            "session_id": "abc123-def456",
            "session_name": "第17章-林潜突破场景",
            "chapter_number": 17,
            "iteration_count": 3,
            "average_rating": 7.3,
            "status": "active"
        }
    ]
}
```

## 场景类型说明

- `narrative` - 叙事场景：一般性的故事叙述
- `dialogue` - 对话场景：以角色对话为主
- `action` - 动作场景：战斗、追逐等动作戏
- `description` - 描写场景：环境、人物等静态描写
- `transition` - 过渡场景：章节之间的衔接
- `breakthrough` - 突破场景：角色实力提升
- `chapter_opening` - 章节开头
- `chapter_ending` - 章节结尾

## 创作风格说明

- `default` - 默认风格：平衡各方面
- `dramatic` - 戏剧化：冲突激烈，情绪起伏大
- `poetic` - 诗意风格：语言优美，意境深远
- `concise` - 简洁风格：直击要点，避免冗长

## 质量评分说明

### 总体评分等级
- 0.8-1.0：优秀，可以直接使用或稍作润色
- 0.6-0.8：良好，建议根据具体建议进行优化
- 0.4-0.6：一般，需要较大幅度的改进
- 0.0-0.4：需要重新生成或大幅修改

### 各维度评分
- **叙事流畅度**：过渡词使用、时间标记、段落衔接
- **对话质量**：对话数量、多样性、角色个性体现
- **场景生动性**：感官描写丰富度（视觉、听觉、触觉）
- **情感冲击力**：情感词汇使用、情绪强度
- **法则链准确性**：世界观术语使用、系统一致性

## 最佳实践

1. **明确需求**：在生成prompt时尽可能详细地描述需求
2. **多轮迭代**：通常需要2-3轮迭代才能获得满意结果
3. **重视分析**：认真阅读分析报告，理解问题所在
4. **灵活调整**：根据实际需要调整风格和参数
5. **保存版本**：可以保存多个满意的版本供后续选择

## 常见问题

### Q: 为什么不直接调用AI API？
A: 人工协作模式让创作者完全掌控创作过程，可以：
- 使用自己的Claude账号和配额
- 实时调整和干预生成过程
- 结合人工创意进行修改
- 避免API调用成本

### Q: 分析结果不准确怎么办？
A: 分析只是参考，最终决定权在创作者手中。如果分析不准确，可以：
- 忽略不合理的建议
- 根据自己的判断优化prompt
- 直接保存满意的内容

### Q: 可以同时进行多个创作会话吗？
A: 可以。每个会话独立管理，互不干扰。适合同时创作多个章节或场景。

## 示例工作流

```python
# 完整的创作流程示例
async def create_chapter_scene():
    # 1. 开始会话
    session = await start_writing_session(
        novel_id="your-novel-id",
        chapter_number=17,
        session_name="第17章突破场景"
    )
    session_id = session["session"]["session_id"]

    # 2. 生成初始prompt
    prompt = await generate_writing_prompt(
        novel_id="your-novel-id",
        chapter_number=17,
        scene_type="breakthrough",
        focus_characters="林潜,炎无极",
        target_length=2000,
        style="dramatic"
    )

    # 3. 用户复制prompt到Claude，获得内容...

    # 4. 分析第一次生成的内容
    analysis = await analyze_generated_content(
        novel_id="your-novel-id",
        session_id=session_id,
        generated_content="【第一次生成的内容】",
        user_rating=6
    )

    # 5. 如果不满意，优化prompt
    if analysis["analysis"]["overall_score"] < 0.8:
        optimized = await optimize_prompt_based_on_feedback(
            session_id=session_id,
            issues_found="描写不够细致,缺少冲突",
            desired_improvements="增加细节,加强戏剧冲突"
        )

        # 6. 使用优化后的prompt再次生成...

        # 7. 分析第二次内容
        analysis2 = await analyze_generated_content(
            novel_id="your-novel-id",
            session_id=session_id,
            generated_content="【第二次生成的内容】",
            user_rating=9
        )

    # 8. 满意后保存
    result = await save_final_content(
        session_id=session_id,
        final_content="【最终内容】",
        content_metadata=json.dumps({
            "version": 2,
            "user_satisfaction": 9,
            "save_to_database": True
        })
    )

    return result
```

## 结语

Novellus人工协作创作系统旨在成为创作者的智能助手，通过提供专业的分析和建议，帮助创作者更高效地产出高质量的小说内容。系统不会替代人工创作，而是增强创作者的能力，让创作过程更加科学和高效。