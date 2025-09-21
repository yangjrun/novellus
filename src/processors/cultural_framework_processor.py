#!/usr/bin/env python3
"""
裂世九域·法则链纪元 - 文化框架数据处理主脚本
用于解析、导入和验证文化框架文本数据
"""

import os
import sys
import asyncio
import argparse
import logging
from pathlib import Path
from typing import Dict, Any
from uuid import UUID

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.config import config
# 直接导入避免ETL模块的依赖冲突
import sys
sys.path.append(str(PROJECT_ROOT / "src" / "etl"))
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cultural_framework_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 项目和小说ID
PROJECT_ID = "29c170c5-4a3e-4829-a242-74c1acb96453"
NOVEL_ID = "e1fd1aa4-bde2-4c76-8cee-334e54fa47d1"

# 示例文化框架文本数据 (由于没有提供实际文本，这里使用示例数据)
SAMPLE_CULTURAL_TEXT = """
# 裂世九域·法则链纪元 - 文化框架

## 人域
人域作为九大域之一，是人类文明的核心聚集地。

### A. 神话与宗教
人域的宗教体系以法则链信仰为核心。居民相信法则链是连接世界本源的神圣纽带，能够赋予修炼者强大的力量。主要信仰包括：
- 链神崇拜：认为法则链由古老的链神创造
- 环印仪式：通过特殊仪式获得环印，标志着修炼身份
- 断链禁忌：禁止随意断裂他人的法则链

### B. 权力与法律
人域实行天命王朝统治，建立了严格的链籍三等制社会体系：
- 天命王朝：统治整个人域的政治实体
- 链籍三等制：根据法则链强度划分社会等级
- 祭司议会：负责宗教事务和法则链认证的权力机构
- 断链律：规范法则链使用的法律体系

### C. 经济与技术
人域的经济体系以链票为主要货币，技术发展围绕法则链应用：
- 链票：以法则链能量为担保的货币体系
- 锻链术：制造和强化法则链的技术工艺
- 环铸法：制作环印的精密技术
- 链金矿：开采法则链原材料的重要产业

### D. 家庭与教育
人域的家庭结构和教育体系深受法则链文化影响：
- 师承制：法则链修炼的传统师父制度
- 血契制：家族内部的法则链传承制度
- 链学院：专门教授法则链知识的教育机构
- 传承仪式：家族法则链传承的正式仪式

### E. 仪式与日常
人域的日常生活充满了与法则链相关的仪式活动：
- 裂世夜：纪念法则链诞生的重要节日
- 归环礼：年轻人获得第一个环印的成年仪式
- 拾链礼：修复断裂法则链的神圣仪式
- 链诞节：庆祝新法则链诞生的节日

### F. 艺术与娱乐
人域的艺术和娱乐活动体现了法则链文化的美学：
- 链舞：模仿法则链流动的优美舞蹈
- 环音乐：使用环印共振产生的音乐形式
- 断链戏：以法则链冲突为主题的戏剧表演
- 链技竞赛：展示法则链操控技巧的竞技活动

### 剧情事件钩子
【剧情钩子】天命王朝内部爆发了关于链籍三等制改革的激烈争论。保守派祭司议会坚持传统制度，而改革派希望建立更公平的法则链分配机制。这一冲突可能引发整个人域的政治动荡，为主角提供选择立场和影响历史走向的机会。

## 天域
天域是九大域中最神秘的领域，被认为是法则链的起源之地。

### A. 神话与宗教
天域的宗教体系更加古老和神秘：
- 源链信仰：相信存在一条连接所有法则链的源头链条
- 天链守护者：保护天域法则链不被污染的神秘组织
- 净化仪式：清除法则链腐化的神圣仪式
- 天启预言：关于法则链未来命运的古老预言

### B. 权力与法律
天域的政治结构以守源会为核心：
- 守源会：维护法则链纯净的最高权力机构
- 链法典：天域独有的法则链管理法典
- 天链议事：处理跨域法则链争议的议事机制
- 源链裁决：针对重大法则链违法行为的最高裁决

### C. 经济与技术
天域掌握着最先进的法则链技术：
- 源能晶：天域独有的高纯度能量货币
- 天链工艺：制造顶级法则链的技术
- 净化术：清除法则链腐化的高级技术
- 源链探测：寻找新法则链源头的技术

## 魔域
魔域是九大域中最危险的区域，充满了腐化的法则链和邪恶力量。

### A. 神话与宗教
魔域的宗教体系围绕腐化法则链展开：
- 暗链崇拜：崇拜腐化法则链力量的邪教
- 断链仪式：故意断裂法则链获取邪恶力量的仪式
- 腐化契约：与邪恶实体签订的危险契约
- 末链预言：关于法则链最终毁灭的黑暗预言

### B. 权力与法律
魔域实行弱肉强食的统治模式：
- 魔链霸主：通过力量统治魔域的强者
- 腐化法则：鼓励法则链腐化的扭曲法律
- 血契盟：以血为誓的邪恶同盟组织
- 断链权：强者夺取他人法则链的特权

### 剧情事件钩子
【剧情钩子】魔域的一位神秘魔链霸主声称掌握了净化腐化法则链的秘密技术，但要求各域派遣使者参与一场危险的试炼。这个提议在九域中引起了巨大争议，因为没人知道这是否是陷阱，还是真的拯救法则链世界的机会。

## 虚域
虚域是一个充满空间扭曲和时间异常的神秘领域。

### A. 神话与宗教
虚域的信仰体系关注空间和时间的本质：
- 虚空法则：认为虚域连接着所有时空的理论
- 时链仪式：操控时间流动的危险仪式
- 空间守护：保护空间稳定的神秘力量
- 虚实转换：在虚幻和现实间转换的能力

### B. 权力与法律
虚域的政治结构非常特殊：
- 虚影议会：由各个时空的代表组成的虚幻议会
- 时空法典：规范时空操作的复杂法律
- 维度守卫：维护空间稳定的执法者
- 虚实协议：处理跨时空事务的协议

## 海域
海域覆盖了九域的海洋区域，是水生文明的家园。

### A. 神话与宗教
海域的宗教围绕海洋和水的力量：
- 潮汐信仰：相信潮汐中蕴含着法则链的韵律
- 深海仪式：在海底进行的神秘宗教仪式
- 水链净化：使用海水净化法则链的技术
- 海神崇拜：崇拜掌管海洋的古老神祇

### B. 权力与法律
海域实行联邦制的政治体系：
- 海域联邦：各个海岛和水下城市的联合政府
- 潮汐法典：基于潮汐循环的法律体系
- 深海议会：处理深海事务的权力机构
- 航海公约：规范海上航行的国际协议

### 剧情事件钩子
【剧情钩子】海域深处发现了一个古老的水下遗迹，里面似乎隐藏着法则链起源的秘密。但遗迹被强大的海洋生物守护，需要九域合作才能探索。这个发现可能改变对法则链历史的认知，但也可能释放出危险的古老力量。

## 冥域
冥域是死亡和灵魂的领域，与生死法则密切相关。

### A. 神话与宗教
冥域的宗教体系专注于死亡和灵魂：
- 灵链信仰：认为灵魂通过法则链连接
- 死者仪式：帮助死者灵魂安息的仪式
- 轮回理论：灵魂通过法则链轮回转世
- 冥神崇拜：崇拜掌管死亡的冥界神祇

### B. 权力与法律
冥域的政治结构围绕死亡秩序：
- 冥司殿：管理死亡秩序的权力机构
- 灵魂法典：规范灵魂和死亡的法律
- 死神审判：对死者进行审判的制度
- 亡灵协约：与亡灵达成的特殊协议

## 荒域
荒域是原始和野性的领域，保持着最古老的法则链形态。

### A. 神话与宗教
荒域的信仰体系强调自然和原始：
- 原始法则：认为最初的法则链来自自然
- 野性仪式：回归原始状态的仪式
- 兽链契约：与野兽建立法则链连接
- 自然崇拜：崇拜自然中的法则链力量

### B. 权力与法律
荒域实行部落制的政治体系：
- 部落联盟：各个部落组成的松散联盟
- 兽王统治：由强大的兽链使用者统治
- 野性法则：基于自然法则的原始法律
- 狩猎协定：规范狩猎和领地的协定

### 剧情事件钩子
【剧情钩子】荒域的原始部落声称发现了最初的法则链形态，但这个发现威胁到了其他域的既得利益。各域都想获得这个秘密，导致了一场围绕原始法则链的争夺战。主角必须在保护原始知识和维护九域平衡之间做出选择。
"""


async def initialize_database():
    """初始化数据库结构"""
    logger.info("正在初始化数据库结构...")

    try:
        # 连接PostgreSQL并执行表创建脚本
        pg_pool = await asyncpg.create_pool(
            host=config.postgres_host,
            port=config.postgres_port,
            database=config.postgres_db,
            user=config.postgres_user,
            password=config.postgres_password
        )

        # 读取并执行PostgreSQL脚本
        sql_script_path = PROJECT_ROOT / "src" / "database" / "schemas" / "cultural_framework_tables_simple.sql"
        with open(sql_script_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        async with pg_pool.acquire() as conn:
            await conn.execute(sql_script)
            logger.info("PostgreSQL表结构创建成功")

        await pg_pool.close()

        # 连接MongoDB并执行集合创建脚本
        mongo_client = AsyncIOMotorClient(config.mongodb_url)
        mongo_db = mongo_client[config.mongodb_db]

        # 由于JavaScript脚本无法直接在Python中执行，这里手动创建集合
        collections_to_create = [
            "cultural_details",
            "plot_hooks_detailed",
            "concepts_dictionary",
            "cross_domain_analysis",
            "processing_logs",
            "cultural_entities_detailed"
        ]

        for collection_name in collections_to_create:
            if collection_name not in await mongo_db.list_collection_names():
                await mongo_db.create_collection(collection_name)
                logger.info(f"MongoDB集合 {collection_name} 创建成功")

        # 创建索引
        await mongo_db.cultural_details.create_index([("novelId", 1), ("domainType", 1)])
        await mongo_db.concepts_dictionary.create_index([("novelId", 1), ("term", 1)], unique=True)
        await mongo_db.processing_logs.create_index([("novelId", 1), ("processType", 1)])

        mongo_client.close()
        logger.info("数据库初始化完成")

    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise


async def process_cultural_text(text: str = None, file_path: str = None) -> Dict[str, Any]:
    """处理文化框架文本"""
    if file_path:
        logger.info(f"从文件读取文本: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    elif not text:
        logger.info("使用示例文本数据")
        text = SAMPLE_CULTURAL_TEXT

    logger.info(f"开始处理文化框架文本，长度: {len(text)}")

    try:
        # 执行数据导入
        result = await import_cultural_framework_text(
            text=text,
            novel_id=NOVEL_ID,
            source_info={
                "project_id": PROJECT_ID,
                "source_type": "file" if file_path else "sample",
                "source_path": file_path if file_path else "sample_data",
                "processing_date": "2024-09-19"
            }
        )

        logger.info(f"数据导入成功，处理时间: {result['processing_time']:.2f}秒")
        logger.info(f"导入统计: {result['statistics']}")

        return result

    except Exception as e:
        logger.error(f"文化框架处理失败: {e}")
        raise


async def validate_imported_data() -> Dict[str, Any]:
    """验证导入的数据质量"""
    logger.info("开始验证导入的数据质量...")

    try:
        # 连接数据库
        pg_pool = await asyncpg.create_pool(
            host=config.postgres_host,
            port=config.postgres_port,
            database=config.postgres_db,
            user=config.postgres_user,
            password=config.postgres_password
        )

        mongo_client = AsyncIOMotorClient(config.mongodb_url)
        mongo_db = mongo_client[config.mongodb_db]

        # 执行验证
        validation_result = await validate_database_cultural_data(
            novel_id=NOVEL_ID,
            pg_pool=pg_pool,
            mongo_db=mongo_db
        )

        await pg_pool.close()
        mongo_client.close()

        logger.info(f"数据验证完成")
        logger.info(f"验证结果: {'通过' if validation_result.passed else '未通过'}")
        logger.info(f"质量分数: {validation_result.quality_score:.2f}")
        logger.info(f"完整性分数: {validation_result.completeness_score:.2f}")

        # 输出问题详情
        if validation_result.issues:
            logger.info("发现的问题:")
            for issue in validation_result.issues:
                logger.info(f"  [{issue.severity.upper()}] {issue.category}: {issue.message}")

        # 输出改进建议
        if validation_result.suggestions:
            logger.info("改进建议:")
            for suggestion in validation_result.suggestions:
                logger.info(f"  - {suggestion}")

        return {
            "passed": validation_result.passed,
            "quality_score": validation_result.quality_score,
            "completeness_score": validation_result.completeness_score,
            "issues_count": len(validation_result.issues),
            "suggestions_count": len(validation_result.suggestions)
        }

    except Exception as e:
        logger.error(f"数据验证失败: {e}")
        raise


async def generate_summary_report() -> Dict[str, Any]:
    """生成处理总结报告"""
    logger.info("生成处理总结报告...")

    try:
        # 连接数据库查询统计信息
        pg_pool = await asyncpg.create_pool(
            host=config.postgres_host,
            port=config.postgres_port,
            database=config.postgres_db,
            user=config.postgres_user,
            password=config.postgres_password
        )

        async with pg_pool.acquire() as conn:
            # 查询各类数据统计
            frameworks_count = await conn.fetchval(
                "SELECT COUNT(*) FROM cultural_frameworks WHERE novel_id = $1", NOVEL_ID
            )
            entities_count = await conn.fetchval(
                "SELECT COUNT(*) FROM cultural_entities WHERE novel_id = $1", NOVEL_ID
            )
            relations_count = await conn.fetchval(
                "SELECT COUNT(*) FROM cultural_relations WHERE novel_id = $1", NOVEL_ID
            )
            hooks_count = await conn.fetchval(
                "SELECT COUNT(*) FROM plot_hooks WHERE novel_id = $1", NOVEL_ID
            )
            concepts_count = await conn.fetchval(
                "SELECT COUNT(*) FROM concept_dictionary WHERE novel_id = $1", NOVEL_ID
            )

            # 查询域分布
            domain_distribution = await conn.fetch("""
                SELECT domain_type, COUNT(*) as count
                FROM cultural_frameworks
                WHERE novel_id = $1
                GROUP BY domain_type
                ORDER BY count DESC
            """, NOVEL_ID)

            # 查询维度分布
            dimension_distribution = await conn.fetch("""
                SELECT dimension, COUNT(*) as count
                FROM cultural_frameworks
                WHERE novel_id = $1
                GROUP BY dimension
                ORDER BY count DESC
            """, NOVEL_ID)

        await pg_pool.close()

        # 连接MongoDB查询处理日志
        mongo_client = AsyncIOMotorClient(config.mongodb_url)
        mongo_db = mongo_client[config.mongodb_db]

        processing_logs = await mongo_db.processing_logs.find(
            {"novelId": NOVEL_ID}
        ).sort("createdAt", -1).to_list(length=10)

        mongo_client.close()

        # 生成报告
        report = {
            "novel_id": NOVEL_ID,
            "project_id": PROJECT_ID,
            "processing_date": "2024-09-19",
            "data_statistics": {
                "frameworks": frameworks_count,
                "entities": entities_count,
                "relations": relations_count,
                "plot_hooks": hooks_count,
                "concepts": concepts_count
            },
            "domain_distribution": {row['domain_type']: row['count'] for row in domain_distribution},
            "dimension_distribution": {row['dimension']: row['count'] for row in dimension_distribution},
            "processing_logs_count": len(processing_logs),
            "latest_processing_status": processing_logs[0]['status'] if processing_logs else "unknown"
        }

        logger.info("处理总结报告:")
        logger.info(f"  文化框架: {frameworks_count}")
        logger.info(f"  文化实体: {entities_count}")
        logger.info(f"  实体关系: {relations_count}")
        logger.info(f"  剧情钩子: {hooks_count}")
        logger.info(f"  概念词典: {concepts_count}")
        logger.info(f"  域分布: {report['domain_distribution']}")
        logger.info(f"  维度分布: {report['dimension_distribution']}")

        return report

    except Exception as e:
        logger.error(f"生成报告失败: {e}")
        raise


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="裂世九域·法则链纪元文化框架处理器")
    parser.add_argument("--init-db", action="store_true", help="初始化数据库")
    parser.add_argument("--file", help="要处理的文化框架文本文件路径")
    parser.add_argument("--validate", action="store_true", help="验证数据质量")
    parser.add_argument("--report", action="store_true", help="生成总结报告")
    parser.add_argument("--all", action="store_true", help="执行完整流程")

    args = parser.parse_args()

    try:
        if args.all or args.init_db:
            await initialize_database()

        if args.all or args.file or not any([args.init_db, args.validate, args.report]):
            # 如果没有指定特定操作，默认处理示例文本
            process_result = await process_cultural_text(file_path=args.file)
            print(f"\n数据导入结果:")
            print(f"成功: {process_result['success']}")
            print(f"处理时间: {process_result['processing_time']:.2f}秒")
            print(f"统计信息: {process_result['statistics']}")

        if args.all or args.validate:
            validation_result = await validate_imported_data()
            print(f"\n数据验证结果:")
            print(f"验证通过: {validation_result['passed']}")
            print(f"质量分数: {validation_result['quality_score']:.2f}")
            print(f"完整性分数: {validation_result['completeness_score']:.2f}")

        if args.all or args.report:
            report = await generate_summary_report()
            print(f"\n处理总结:")
            print(f"数据统计: {report['data_statistics']}")
            print(f"域分布: {report['domain_distribution']}")
            print(f"维度分布: {report['dimension_distribution']}")

        print(f"\n✅ 文化框架数据处理完成!")

    except Exception as e:
        logger.error(f"处理失败: {e}")
        print(f"\n❌ 处理失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())