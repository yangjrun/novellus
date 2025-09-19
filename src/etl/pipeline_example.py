"""
Complete ETL Pipeline Example for "裂世九域·法则链纪元"

This example demonstrates the full ETL pipeline workflow including:
- Batch processing of novel content
- Real-time streaming updates
- Entity extraction and validation
- Incremental updates with conflict resolution
- Cross-database synchronization
"""

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import json

from .pipeline_manager import (
    PipelineManager, PipelineConfig, ContentType, PipelineStatus
)
from .text_processor import TextProcessor, TextType
from .entity_extractor import EntityExtractor, EntityType
from .data_validator import DataValidator, ValidationSeverity
from .stream_processor import StreamProcessor, StreamEventType, StreamEvent
from .incremental_processor import IncrementalProcessor, ChangeType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NovelETLDemo:
    """
    Demonstration of the complete ETL pipeline for novel content processing.

    This class showcases:
    1. Batch processing workflow
    2. Streaming processing setup
    3. Incremental updates and conflict resolution
    4. Data quality monitoring
    5. Entity relationship mapping
    """

    def __init__(self):
        # Initialize pipeline components
        self.config = PipelineConfig(
            batch_size=50,
            max_workers=4,
            enable_streaming=True,
            enable_validation=True,
            enable_entity_extraction=True,
            chinese_segmentation=True,
            traditional_to_simplified=False
        )

        self.pipeline_manager = PipelineManager(self.config)
        self.text_processor = TextProcessor(
            enable_chinese_segmentation=True,
            traditional_to_simplified=False
        )
        self.entity_extractor = EntityExtractor()
        self.data_validator = DataValidator()
        self.stream_processor = StreamProcessor(self.config)
        self.incremental_processor = IncrementalProcessor()

        # Sample novel content for demonstration
        self.sample_content = self._create_sample_content()

        logger.info("NovelETLDemo initialized")

    def _create_sample_content(self) -> Dict[ContentType, List[Dict[str, Any]]]:
        """Create sample novel content for demonstration."""
        return {
            ContentType.WORLDVIEW: [
                {
                    "id": "world_001",
                    "title": "九域概述",
                    "content": """裂世九域是一个庞大的修仙世界，由九个不同的域构成。天权域位于九域之首，
                    控制着整个世界的法则链运行。地煞域以其强大的地脉之力著称，人皇域则是凡人修士的聚集地。
                    修罗域充满杀戮与争斗，魔渊域深藏无尽的魔气。仙境域是仙人的居所，神界域更是神明的领域。
                    混沌域处于时空的边缘，而虚无域则是一切的终极归宿。每个域都有其独特的修炼体系和法则。"""
                },
                {
                    "id": "world_002",
                    "title": "修炼体系",
                    "content": """修炼之路分为多个境界：筑基期是入门阶段，修士需要打通经脉、凝聚灵力。
                    结丹期要凝结金丹，储存更多灵力。元婴期则是元神初成，可以离体而行。
                    化神期神魂强大，能够操控天地法则。合体期是与天地合一，大乘期更是接近仙人。
                    渡劫期需要经历天劫考验，成功后可成为散仙。之后还有地仙、天仙、金仙、太乙、大罗等更高境界。"""
                }
            ],
            ContentType.CHARACTER: [
                {
                    "id": "char_001",
                    "name": "李逍遥",
                    "content": """李逍遥，天权域出身，年仅二十三岁已达结丹期巅峰。
                    拥有稀有的混沌灵根，修炼《天权剑诀》。性格坚毅不屈，重情重义。
                    曾在地煞域历练三年，与魔渊域的魔修有过激战。师承天权域长老王玄机，
                    与同门师姐林若雪关系密切。目前正在寻找突破元婴期的机缘。"""
                },
                {
                    "id": "char_002",
                    "name": "林若雪",
                    "content": """林若雪，天权域天才女修，拥有冰灵根，修炼《玄冰诀》。
                    现为元婴期初期修为，年仅二十五岁。容貌绝美，性格冰冷却内心善良。
                    是李逍遥的师姐，两人青梅竹马。曾获得仙境域传承，实力不可小觑。
                    擅长冰系法术和剑法，拥有上品法宝寒月剑。"""
                }
            ],
            ContentType.PLOT: [
                {
                    "id": "plot_001",
                    "title": "天权域大比",
                    "content": """天权域十年一度的大比即将开始，各域年轻修士齐聚天权城。
                    李逍遥代表天权域参赛，面对来自其他域的强劲对手。首轮比赛中，
                    他遇到了修罗域的血煞宗弟子，对方修炼杀戮之道，实力不凡。
                    经过激烈战斗，李逍遥凭借《天权剑诀》的精妙招式险胜。
                    但在决赛中，他将面对魔渊域的天才魔修，那将是真正的考验。"""
                },
                {
                    "id": "plot_002",
                    "title": "魔渊探宝",
                    "content": """为了寻找突破元婴期的机缘，李逍遥和林若雪决定深入魔渊域探宝。
                    魔渊域危险重重，到处都是强大的魔兽和魔修。两人小心翼翼地前进，
                    终于在一处古老的魔殿中发现了传说中的化神丹。但是魔殿的守护者
                    是一只化神期的魔龙，想要获得化神丹，必须先击败这头魔龙。
                    一场生死搏斗即将展开。"""
                }
            ],
            ContentType.SCENE: [
                {
                    "id": "scene_001",
                    "location": "天权城",
                    "content": """天权城巍峨壮观，城墙高达千丈，由特殊的灵石砌成，
                    闪闪发光如同仙境。城中央矗立着天权塔，高耸入云，是整个天权域的象征。
                    大街小巷车水马龙，各种修士来来往往。街边有法宝店、丹药铺、
                    灵兽园等修仙相关的店铺。城北是天权宗的山门，云雾缭绕，仙气十足。
                    护城大阵时刻运转，守护着这座修仙圣城。"""
                },
                {
                    "id": "scene_002",
                    "location": "魔渊深处",
                    "content": """魔渊深处阴森恐怖，天空永远是血红色的，空气中弥漫着浓郁的魔气。
                    地面崎岖不平，到处都是巨大的魔石和枯骨。远处传来阵阵魔兽的咆哮声，
                    让人不寒而栗。古老的魔殿半埋在地下，殿门雕刻着邪恶的魔纹，
                    散发着令人恐惧的威压。殿内漆黑一片，只有偶尔闪烁的魔火提供微弱光亮。
                    这里是魔修和魔兽的天堂，也是正道修士的噩梦。"""
                }
            ],
            ContentType.DIALOGUE: [
                {
                    "id": "dialogue_001",
                    "speakers": ["李逍遥", "林若雪"],
                    "content": """"师姐，这次魔渊之行凶险异常，要不你还是不要去了。"李逍遥担忧地说道。

                    "师弟，我们一起长大，一起修炼，岂能让你独自面对危险？"林若雪坚定地回答，
                    "而且我的《玄冰诀》对魔气有克制作用，说不定能帮到你。"

                    "好吧，那我们就一起去吧。不过一定要小心，魔渊域的魔修都很狡猾。"

                    "放心，我们配合这么多年，默契度不是问题。只要小心谨慎，应该没问题。"""
                }
            ]
        }

    async def demonstrate_batch_processing(self):
        """演示批处理工作流程。"""
        logger.info("=== 开始批处理演示 ===")

        # 设置回调函数
        async def on_batch_complete(batch_num, total_batches):
            logger.info(f"批次 {batch_num}/{total_batches} 处理完成")

        async def on_error(error, batch_data):
            logger.error(f"批处理错误: {error}")

        async def on_pipeline_complete(metrics):
            logger.info(f"管道完成 - 处理记录: {metrics.processed_records}, "
                       f"失败记录: {metrics.failed_records}, "
                       f"处理速率: {metrics.processing_rate:.2f} 记录/秒")

        self.pipeline_manager.on_batch_complete = on_batch_complete
        self.pipeline_manager.on_error = on_error
        self.pipeline_manager.on_pipeline_complete = on_pipeline_complete

        # 处理每种内容类型
        for content_type, content_list in self.sample_content.items():
            logger.info(f"处理 {content_type.value} 内容...")

            # 模拟数据源（实际使用中会从文件或数据库读取）
            data_source = f"sample_{content_type.value}_data"

            try:
                # 开始批处理
                metrics = await self.pipeline_manager.process_batch(
                    content_type=content_type,
                    data_source=data_source,
                    resume_from_checkpoint=True
                )

                logger.info(f"{content_type.value} 处理完成: {metrics.processed_records} 记录")

            except Exception as e:
                logger.error(f"批处理失败 {content_type.value}: {e}")

        # 获取管道状态
        status = self.pipeline_manager.get_pipeline_status()
        logger.info(f"管道状态: {json.dumps(status, indent=2, ensure_ascii=False)}")

    async def demonstrate_text_processing(self):
        """演示文本处理功能。"""
        logger.info("=== 开始文本处理演示 ===")

        sample_text = self.sample_content[ContentType.WORLDVIEW][0]["content"]

        # 文本清洗和标准化
        cleaned_text = await self.text_processor.clean_text(sample_text, TextType.NARRATIVE)
        logger.info(f"清洗后文本长度: {len(cleaned_text)}")

        # 文本分词和词性标注
        segments, pos_tags = await self.text_processor.segment_text(cleaned_text)
        logger.info(f"分词结果: {segments[:10]}...")  # 只显示前10个词
        logger.info(f"词性标注: {pos_tags[:5]}...")   # 只显示前5个

        # 内容要素提取
        elements = await self.text_processor.extract_content_elements(cleaned_text)
        logger.info(f"提取的要素: {json.dumps(elements, ensure_ascii=False, indent=2)}")

        # 完整处理流程
        result = await self.text_processor.process_text(sample_text, TextType.NARRATIVE)
        logger.info(f"处理统计: 原文长度={result.metadata['original_length']}, "
                   f"清洗后长度={result.metadata['cleaned_length']}, "
                   f"分词数量={result.metadata['segment_count']}, "
                   f"处理时间={result.processing_time:.3f}秒")

    async def demonstrate_entity_extraction(self):
        """演示实体提取功能。"""
        logger.info("=== 开始实体提取演示 ===")

        # 提取世界观内容的实体
        worldview_text = self.sample_content[ContentType.WORLDVIEW][0]["content"]
        entities = await self.entity_extractor.extract_entities(
            worldview_text, ContentType.WORLDVIEW
        )

        logger.info(f"从世界观文本中提取到 {len(entities)} 个实体:")
        for entity in entities:
            logger.info(f"  - {entity.canonical_name} ({entity.entity_type.value}): "
                       f"置信度={entity.confidence:.2f}, 提及次数={entity.mention_count}")

        # 提取人物内容的实体
        character_text = self.sample_content[ContentType.CHARACTER][0]["content"]
        char_entities = await self.entity_extractor.extract_entities(
            character_text, ContentType.CHARACTER
        )

        logger.info(f"从人物文本中提取到 {len(char_entities)} 个实体:")
        for entity in char_entities:
            logger.info(f"  - {entity.canonical_name} ({entity.entity_type.value}): "
                       f"置信度={entity.confidence:.2f}")
            if entity.relationships:
                logger.info(f"    关系: {entity.relationships}")

        # 实体统计
        stats = self.entity_extractor.get_entity_statistics()
        logger.info(f"实体统计: {json.dumps(stats, ensure_ascii=False)}")

        # 实体搜索
        search_results = self.entity_extractor.search_entities("李逍遥")
        logger.info(f"搜索'李逍遥'结果: {json.dumps(search_results, ensure_ascii=False)}")

    async def demonstrate_data_validation(self):
        """演示数据验证功能。"""
        logger.info("=== 开始数据验证演示 ===")

        # 创建测试记录
        test_record = {
            "original_id": "test_001",
            "content_type": "worldview",
            "original_content": self.sample_content[ContentType.WORLDVIEW][0]["content"],
            "cleaned_content": "cleaned version of content...",
            "entities": [],
            "metadata": {"source": "demo"},
            "processed_at": datetime.now().isoformat(),
            "pipeline_version": "1.0"
        }

        # 验证记录
        validation_result = await self.data_validator.validate_record(
            test_record, ContentType.WORLDVIEW
        )

        logger.info(f"验证结果: 有效={validation_result.is_valid}, "
                   f"总分={validation_result.overall_score:.2f}, "
                   f"问题数量={len(validation_result.issues)}")

        # 显示验证问题
        for issue in validation_result.issues:
            logger.info(f"  {issue.severity.value}: {issue.message}")

        # 验证统计
        stats = self.data_validator.get_validation_statistics()
        if stats:
            logger.info(f"验证统计: {json.dumps(stats, ensure_ascii=False)}")

        # 异常检测
        anomalies = self.data_validator.detect_anomalies()
        if anomalies:
            logger.info(f"检测到 {len(anomalies)} 个异常")

    async def demonstrate_streaming_processing(self):
        """演示流式处理功能。"""
        logger.info("=== 开始流式处理演示 ===")

        # 设置事件处理器
        async def handle_content_event(event):
            logger.info(f"处理流事件: {event.event_type.value} - {event.event_id}")

        async def handle_batch_complete(window_stats):
            logger.info(f"窗口处理完成: {window_stats['window_id']}, "
                       f"事件数量: {window_stats['event_count']}")

        self.stream_processor.add_event_handler(StreamEventType.CONTENT_ADDED, handle_content_event)
        self.stream_processor.add_event_handler(StreamEventType.BATCH_COMPLETE, handle_batch_complete)

        # 模拟消息队列源配置
        source_config = {
            'type': 'message_queue',
            'queue_name': 'novel_content_updates',
            'poll_interval': 2
        }

        # 启动流处理（在后台运行）
        stream_task = asyncio.create_task(
            self.stream_processor.start_stream(ContentType.PLOT, source_config)
        )

        # 模拟发送一些流事件
        for i in range(5):
            await asyncio.sleep(1)

            # 模拟消息
            self.stream_processor.simulate_message({
                "content": f"这是第 {i+1} 个流式更新的情节内容...",
                "metadata": {"update_type": "plot_development"}
            })

        # 运行一段时间后停止
        await asyncio.sleep(10)
        await self.stream_processor.stop_stream()

        # 等待任务完成
        try:
            await asyncio.wait_for(stream_task, timeout=5.0)
        except asyncio.TimeoutError:
            logger.warning("流处理任务超时")

        # 获取流处理状态
        status = self.stream_processor.get_stream_status()
        logger.info(f"流处理状态: {json.dumps(status, ensure_ascii=False)}")

    async def demonstrate_incremental_processing(self):
        """演示增量处理功能。"""
        logger.info("=== 开始增量处理演示 ===")

        # 原始记录
        original_data = {
            "original_id": "char_001",
            "content_type": "character",
            "original_content": self.sample_content[ContentType.CHARACTER][0]["content"],
            "cleaned_content": "李逍遥，天权域出身...",
            "entities": [{"name": "李逍遥", "type": "character"}],
            "metadata": {"source": "manual"},
            "processed_at": datetime.now().isoformat(),
            "pipeline_version": "1.0"
        }

        # 模拟更新
        updated_data = original_data.copy()
        updated_data["cleaned_content"] = "李逍遥，天权域出身，现已突破到元婴期..."
        updated_data["entities"].append({"name": "元婴期", "type": "cultivation_level"})
        updated_data["processed_at"] = (datetime.now() + timedelta(minutes=5)).isoformat()

        # 处理增量更新
        result = await self.incremental_processor.process_incremental_update(
            ContentType.CHARACTER, "char_001", updated_data, "auto_update"
        )

        logger.info(f"增量更新结果: {json.dumps(result, ensure_ascii=False)}")

        # 获取变更历史
        change_history = await self.incremental_processor.get_change_history("char_001")
        logger.info(f"变更历史: {len(change_history)} 条记录")

        # 获取版本历史
        version_history = await self.incremental_processor.get_version_history("char_001")
        logger.info(f"版本历史: {len(version_history)} 个版本")

        # 获取未解决的冲突
        conflicts = await self.incremental_processor.get_unresolved_conflicts()
        if conflicts:
            logger.info(f"未解决冲突: {len(conflicts)} 个")

        # 处理统计
        stats = self.incremental_processor.get_processing_statistics()
        logger.info(f"处理统计: {json.dumps(stats, ensure_ascii=False)}")

    async def run_complete_demo(self):
        """运行完整的演示流程。"""
        logger.info("开始小说ETL管道完整演示")
        logger.info("=" * 60)

        try:
            # 1. 文本处理演示
            await self.demonstrate_text_processing()
            logger.info("")

            # 2. 实体提取演示
            await self.demonstrate_entity_extraction()
            logger.info("")

            # 3. 数据验证演示
            await self.demonstrate_data_validation()
            logger.info("")

            # 4. 批处理演示
            await self.demonstrate_batch_processing()
            logger.info("")

            # 5. 增量处理演示
            await self.demonstrate_incremental_processing()
            logger.info("")

            # 6. 流式处理演示
            await self.demonstrate_streaming_processing()
            logger.info("")

            logger.info("=" * 60)
            logger.info("小说ETL管道演示完成！")

        except Exception as e:
            logger.error(f"演示过程中发生错误: {e}")
            raise


async def main():
    """主函数 - 运行ETL管道演示。"""
    demo = NovelETLDemo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    asyncio.run(main())