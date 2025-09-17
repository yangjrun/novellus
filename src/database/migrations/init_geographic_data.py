"""
地理数据初始化脚本
为裂世九域小说初始化四个域的地理数据
"""

import asyncio
from typing import Dict, List, Any
from datetime import datetime

from ..connections.postgresql import get_postgresql_connection
from ..models.geographic_models import GeographicDataImport


class GeographicDataInitializer:
    """地理数据初始化器"""

    def __init__(self, novel_id: int = 1):
        self.novel_id = novel_id
        self.entity_type_mapping = {
            'regions': 'region',
            'cities': 'city',
            'towns': 'town',
            'villages': 'village',
            'landmarks': 'landmark',
            'buildings': 'building',
            'natural_features': 'natural_feature',
            'infrastructure': 'infrastructure'
        }

    async def initialize_all_domains(self):
        """初始化所有域的地理数据"""
        domains_data = {
            'ren_yu': self._get_ren_yu_data(),
            'tian_yu': self._get_tian_yu_data(),
            'ling_yu': self._get_ling_yu_data(),
            'huang_yu': self._get_huang_yu_data()
        }

        async with get_postgresql_connection() as conn:
            for domain_code, data in domains_data.items():
                print(f"正在初始化 {domain_code} 的地理数据...")
                await self._initialize_domain_data(conn, domain_code, data)
                print(f"{domain_code} 初始化完成")

    async def _initialize_domain_data(self, conn, domain_code: str, data: Dict[str, List[Dict]]):
        """初始化单个域的地理数据"""

        # 获取实体类型ID映射
        entity_type_ids = await self._get_entity_type_ids(conn)

        # 存储实体ID映射，用于建立关系
        entity_id_mapping = {}

        # 按层级顺序创建实体
        creation_order = ['regions', 'cities', 'towns', 'villages', 'landmarks', 'buildings', 'natural_features', 'infrastructure']

        for category in creation_order:
            if category in data:
                entities = data[category]
                entity_type = self.entity_type_mapping[category]
                entity_type_id = entity_type_ids.get(entity_type)

                if not entity_type_id:
                    print(f"警告: 未找到实体类型 {entity_type}")
                    continue

                for entity_data in entities:
                    entity_id = await self._create_entity(
                        conn, entity_type_id, entity_data, domain_code
                    )

                    # 存储实体ID映射
                    entity_name = entity_data['name']
                    entity_id_mapping[f"{category}_{entity_name}"] = entity_id

        # 建立地理层级关系
        await self._create_geographic_relationships(conn, entity_id_mapping, domain_code)

    async def _get_entity_type_ids(self, conn) -> Dict[str, int]:
        """获取实体类型ID映射"""
        query = """
        SELECT name, id FROM entity_types
        WHERE novel_id = $1 AND name IN ('region', 'city', 'town', 'village', 'landmark', 'building', 'natural_feature', 'infrastructure')
        """

        rows = await conn.fetch(query, self.novel_id)
        return {row['name']: row['id'] for row in rows}

    async def _create_entity(self, conn, entity_type_id: int, entity_data: Dict[str, str], domain_code: str) -> int:
        """创建单个地理实体"""
        query = """
        INSERT INTO entities (novel_id, entity_type_id, name, code, attributes, tags, priority, created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING id
        """

        name = entity_data['name']
        note = entity_data.get('note', '')

        # 生成代码标识
        code = f"{domain_code}_{name.replace(' ', '_').lower()}"

        # 构建属性
        attributes = {
            'note': note,
            'domain_code': domain_code,
            'geographic_type': self._infer_geographic_type(name, note),
            'original_data': entity_data
        }

        # 根据描述推断重要性
        priority = self._calculate_priority(name, note)

        tags = [domain_code, self._extract_tags_from_note(note)]
        tags = [tag for tag in tags if tag]  # 过滤空标签

        now = datetime.utcnow()

        row = await conn.fetchrow(
            query, self.novel_id, entity_type_id, name, code,
            attributes, tags, priority, now, now
        )

        return row['id']

    async def _create_geographic_relationships(self, conn, entity_mapping: Dict[str, int], domain_code: str):
        """创建地理层级关系"""

        # 定义层级关系规则
        hierarchy_rules = [
            # 区域包含城市
            ('regions', 'cities', 'contains'),
            # 城市包含城镇
            ('cities', 'towns', 'contains'),
            # 城镇包含村庄
            ('towns', 'villages', 'contains'),
            # 城市包含地标和建筑
            ('cities', 'landmarks', 'contains'),
            ('cities', 'buildings', 'contains'),
            # 基础设施连接各地
            ('infrastructure', 'cities', 'connects'),
            ('infrastructure', 'towns', 'connects'),
        ]

        for source_type, target_type, relationship_type in hierarchy_rules:
            await self._create_relationships_between_types(
                conn, entity_mapping, source_type, target_type, relationship_type, domain_code
            )

    async def _create_relationships_between_types(self, conn, entity_mapping: Dict[str, int],
                                                source_type: str, target_type: str,
                                                relationship_type: str, domain_code: str):
        """在两种实体类型之间创建关系"""

        source_entities = [k for k in entity_mapping.keys() if k.startswith(source_type)]
        target_entities = [k for k in entity_mapping.keys() if k.startswith(target_type)]

        for source_key in source_entities:
            for target_key in target_entities:
                # 简单的关系匹配逻辑（实际应用中可能需要更复杂的逻辑）
                if self._should_create_relationship(source_key, target_key, relationship_type):
                    await self._create_relationship(
                        conn,
                        entity_mapping[source_key],
                        entity_mapping[target_key],
                        relationship_type
                    )

    def _should_create_relationship(self, source_key: str, target_key: str, relationship_type: str) -> bool:
        """判断是否应该创建关系（简化逻辑）"""
        # 这里可以根据实际需求实现更复杂的匹配逻辑
        return True  # 简化：创建所有可能的关系

    async def _create_relationship(self, conn, source_id: int, target_id: int, relationship_type: str):
        """创建实体关系"""
        query = """
        INSERT INTO entity_relationships (novel_id, source_entity_id, target_entity_id, relationship_type, strength, created_at)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (source_entity_id, target_entity_id, relationship_type, valid_from) DO NOTHING
        """

        await conn.execute(
            query, self.novel_id, source_id, target_id,
            relationship_type, 5, datetime.utcnow()
        )

    def _infer_geographic_type(self, name: str, note: str) -> str:
        """从名称和描述推断地理类型"""
        if '平原' in name or '平原' in note:
            return '平原'
        elif '丘陵' in name or '丘陵' in note:
            return '丘陵'
        elif '高地' in name or '高地' in note:
            return '高地'
        elif '盆地' in name or '盆地' in note:
            return '盆地'
        elif '水网' in name or '水网' in note:
            return '水网'
        else:
            return '其他'

    def _calculate_priority(self, name: str, note: str) -> int:
        """根据名称和描述计算重要性"""
        priority = 1

        # 根据关键词提升重要性
        high_priority_keywords = ['都', '京', '府', '总', '中心', '枢纽', '皇']
        medium_priority_keywords = ['城', '镇', '关', '港']

        for keyword in high_priority_keywords:
            if keyword in name:
                priority = max(priority, 8)
                break

        for keyword in medium_priority_keywords:
            if keyword in name:
                priority = max(priority, 5)
                break

        return priority

    def _extract_tags_from_note(self, note: str) -> str:
        """从描述中提取标签"""
        tags = []

        # 功能标签
        if '治所' in note or '官' in note:
            tags.append('行政')
        if '市' in note or '商' in note or '贸易' in note:
            tags.append('商业')
        if '工坊' in note or '制造' in note or '炼' in note:
            tags.append('工业')
        if '祭' in note or '神' in note or '宗' in note:
            tags.append('宗教')
        if '军' in note or '防' in note or '关' in note:
            tags.append('军事')

        return ','.join(tags)

    def _get_ren_yu_data(self) -> Dict[str, List[Dict]]:
        """人域地理数据"""
        return {
            'regions': [
                {'name': '稻环平原', 'note': '粮仓腹地与环渠网核心'},
                {'name': '盐链丘陵', 'note': '小盐泽密布, 以盐铁作坊著称'},
                {'name': '北阙关带', 'note': '护境要冲, 与荒域互市并存'},
                {'name': '南环水网', 'note': '水乡泽国, 小航运与渔税'}
            ],
            'cities': [
                {'name': '枢链城', 'note': '州府治所, 缚司与祭司分坊并设'},
                {'name': '环渠府', 'note': '水利总渠与仓税环库所在'},
                {'name': '九埠市', 'note': '散口码头群, 链票结算中心'}
            ],
            'towns': [
                {'name': '石环镇', 'note': '县城, 以石作环窗与磨坊出名'},
                {'name': '柳链集', 'note': '织造与链纤维代工镇'},
                {'name': '环印关镇', 'note': '人域北出关卡, 验票与巡链'},
                {'name': '谷槌坊', 'note': '粮市与秋试主会场'}
            ],
            'villages': [
                {'name': '白泥村', 'note': '陶泥与水车作坊'},
                {'name': '七环坝', 'note': '七级堰坝护田'},
                {'name': '乌篱塍', 'note': '黑篱防风, 多苦役灰籍'},
                {'name': '河湾里', 'note': '小渔村, 私刻船祀常见'}
            ],
            'landmarks': [
                {'name': '祖灵续籍台', 'note': '家谱与环史备案处'},
                {'name': '县链枷祭坛', 'note': '公刑与链祭日仪场'},
                {'name': '三环亭', 'note': '驿路节点, 公示链告'},
                {'name': '老链桥', 'note': '木石老桥, 传说断链共存'},
                {'name': '环石通信阵', 'note': '乡间传讯石环'}
            ],
            'buildings': [
                {'name': '县缚司署', 'note': '执法中枢, 断链排查'},
                {'name': '祭司分坊', 'note': '新生链测与丧葬登记'},
                {'name': '宗门外堂', 'note': '收童生与基本术教'},
                {'name': '链票行', 'note': '小额结算与押契'},
                {'name': '仓税环库', 'note': '粮盐与链税双管'},
                {'name': '环史档案阁', 'note': '家谱与链籍卷宗'}
            ],
            'natural_features': [
                {'name': '环渠总干', 'note': '三岔并流, 旱涝调度'},
                {'name': '青脊岗', 'note': '低山岗地, 风标好立'},
                {'name': '盐泽', 'note': '半咸淡洼地, 产祭盐'},
                {'name': '芦湾湿地', 'note': '候鸟地, 渔猎纠纷多'},
                {'name': '断崖粮道', 'note': '崖上险道, 贼患时常'}
            ],
            'infrastructure': [
                {'name': '环印南门', 'note': '城门验印与边商通关'},
                {'name': '驿路环碑', 'note': '里程与链告合刻'},
                {'name': '水车环堰', 'note': '村社自治维护'},
                {'name': '互市小码头', 'note': '人域—荒域换盐粮口'}
            ]
        }

    def _get_tian_yu_data(self) -> Dict[str, List[Dict]]:
        """天域地理数据"""
        return {
            'regions': [
                {'name': '九环京畿', 'note': '皇城辐射圈, 礼制最严'},
                {'name': '御链大道圈层', 'note': '帝路九辐连诸郡'},
                {'name': '东御陵原', 'note': '皇陵与禁苑, 祭典重地'},
                {'name': '西台群山', 'note': '巡链烽台带与矿监'}
            ],
            'cities': [
                {'name': '九环京', 'note': '帝都, 御环台与九环书院所在'},
                {'name': '白金府', 'note': '链库总库与链算所总院'},
                {'name': '御链港', 'note': '南向贸易与仪仗船坞'}
            ],
            'towns': [
                {'name': '环阶镇', 'note': '仪仗工坊密集, 供宫廷礼器'},
                {'name': '御书镇', 'note': '抄经与官刻石经'},
                {'name': '链库镇', 'note': '粮械双库, 军需枢纽'},
                {'name': '禁园卫镇', 'note': '禁苑外围, 护猎与水利'}
            ],
            'villages': [
                {'name': '金环庄', 'note': '供奉链神的贵族庄园群'},
                {'name': '石枢里', 'note': '石作匠户, 修葺环阶'},
                {'name': '御牧堡', 'note': '仪驾马匹饲养地'},
                {'name': '环工屯', 'note': '朝役工匠家属聚居'}
            ],
            'landmarks': [
                {'name': '御环台', 'note': '最高审链与国礼台'},
                {'name': '九环书院', 'note': '仕学与链学最高学府'},
                {'name': '链算所总院', 'note': '占测与风险定价权威'},
                {'name': '环典石经塔', 'note': '正统教律象征'},
                {'name': '悬链梁殿群', 'note': '皇城内廷, 九环阶环庭'}
            ],
            'buildings': [
                {'name': '祭司议会殿', 'note': '释链定法中心'},
                {'name': '链库总库', 'note': '国家储备与御用器库'},
                {'name': '环印门·四正门', 'note': '国都四向正门, 礼制严'},
                {'name': '九阶朝台', 'note': '朝会礼阶, 断链者不得上'},
                {'name': '御史台/巡链司总部', 'note': '御察与巡缚合署'},
                {'name': '万环谱馆', 'note': '典藏历代环印拓与谱录'}
            ],
            'natural_features': [
                {'name': '御河环湾', 'note': '河道绕城三曲, 舟礼巡行'},
                {'name': '五环丘', 'note': '丘陵五连, 祭天备用'},
                {'name': '雾栈林', 'note': '晨雾浓, 宫苑外防区'},
                {'name': '白阶崖', 'note': '白岩峭壁, 刻御诏'},
                {'name': '金环谷', 'note': '秋祭撒谷地, 民俗丰收礼'}
            ],
            'infrastructure': [
                {'name': '帝路九辐', 'note': '从九环京放射诸省'},
                {'name': '环巡烽台带', 'note': '讯号与边警一体'},
                {'name': '链讯塔阵', 'note': '官用长距传讯阵列'},
                {'name': '环轨马道', 'note': '快马换乘站系'}
            ]
        }

    def _get_ling_yu_data(self) -> Dict[str, List[Dict]]:
        """灵域地理数据"""
        return {
            'regions': [
                {'name': '工环盆地', 'note': '工坊群与展馆密集'},
                {'name': '青陶丘', 'note': '陶土矿与釉坊'},
                {'name': '炉峰群', 'note': '炉山连岭, 炼器村落散布'},
                {'name': '印评廊带', 'note': '评印院与试场轴线'}
            ],
            'cities': [
                {'name': '多环城', 'note': '匠都, 链工博览与万器朝链广场'},
                {'name': '匠阙', 'note': '三大会所与工程链契司'},
                {'name': '评印都', 'note': '评印院总馆与器衡塔'}
            ],
            'towns': [
                {'name': '炉前镇', 'note': '炼器镇, 师承祖炉林立'},
                {'name': '釉环镇', 'note': '彩釉环砖与陶模'},
                {'name': '纸链镇', 'note': '链墨抄纸与拓印'},
                {'name': '丝环镇', 'note': '链纤维织造专镇'}
            ],
            'villages': [
                {'name': '竹环村', 'note': '竹纹器胚与环窗框'},
                {'name': '砂坡里', 'note': '铸模砂坑与童工争议'},
                {'name': '石墨坞', 'note': '墨矿与配方秘窟'},
                {'name': '匠徒营', 'note': '学徒集中居住区'}
            ],
            'landmarks': [
                {'name': '链工博览园', 'note': '年度展会与合环奖评选'},
                {'name': '万器朝链广场', 'note': '巨型仪式环与发布场'},
                {'name': '评印院总馆', 'note': '作品评级与仲裁'},
                {'name': '界核试验场', 'note': '高危试验, 常封锁'},
                {'name': '师承祖炉', 'note': '祖师传承圣地'}
            ],
            'buildings': [
                {'name': '链墨坊', 'note': '配方机密, 监管严格'},
                {'name': '链纤维织局', 'note': '高强度纤维织造'},
                {'name': '连拱作坊群', 'note': '通风耐火的厂群'},
                {'name': '器衡塔', 'note': '精度校准与标准发布'},
                {'name': '工程链契司', 'note': '大宗项目合同中心'},
                {'name': '匠会公所', 'note': '行规颁行与纠纷调解'}
            ],
            'natural_features': [
                {'name': '炉泉', 'note': '地热温泉, 炉火常年'},
                {'name': '黏土坑', 'note': '胶性佳, 釉砖之本'},
                {'name': '环穹洞', 'note': '圆穹石洞, 声学试验地'},
                {'name': '风谷', 'note': '高风速谷地, 自然鼓风'},
                {'name': '矿脉断面', 'note': '教学用露天剖面'}
            ],
            'infrastructure': [
                {'name': '环吊桥', 'note': '重载运材专用'},
                {'name': '匠运渠', 'note': '水运原材到厂'},
                {'name': '评印通道', 'note': '作品从试场到评审闭环'},
                {'name': '合环奖展馆', 'note': '常年陈列获奖器'}
            ]
        }

    def _get_huang_yu_data(self) -> Dict[str, List[Dict]]:
        """荒域地理数据"""
        return {
            'regions': [
                {'name': '火灰走带', 'note': '由祖灵火台串起的迁徙通道'},
                {'name': '荒脊高地', 'note': '山脊堡城, 断链器锻造'},
                {'name': '风孔城', 'note': '风口上建, 护风塔阵环绕'}
            ],
            'cities': [],  # 荒域没有传统意义的城市
            'towns': [
                {'name': '灰帐镇', 'note': '帆幕营常驻, 黑市互易'},
                {'name': '沙咽镇', 'note': '深井群与水仓'},
                {'name': '断骨镇', 'note': '骨器与狩猎分发'},
                {'name': '矿脉哨镇', 'note': '链矿出入口与火灰印局'}
            ],
            'villages': [
                {'name': '环石营', 'note': '立石围营, 商旅歇脚'},
                {'name': '火誓营地', 'note': '战前集结与断环誓'},
                {'name': '骨链村', 'note': '骨饰与图腾传承'},
                {'name': '风影窟落', 'note': '洞穴群, 迁徙季居住'}
            ],
            'landmarks': [
                {'name': '祖灵火坛', 'note': '部落之心, 裂世夜守护'},
                {'name': '断链祭场', 'note': '临时断链与重缚仪式地'},
                {'name': '环石标带', 'note': '风暴航标, 指路避灾'},
                {'name': '风口门', 'note': '风墙缺口, 设税与盘查'},
                {'name': '沉链坑', 'note': '古战遗坑, 常出危械'}
            ],
            'buildings': [
                {'name': '帆幕营群', 'note': '可拆装城市, 顺风而迁'},
                {'name': '沙下水仓', 'note': '地下水库与蓄水系统'}
            ],
            'natural_features': [],  # 荒域的自然景观在landmarks中体现
            'infrastructure': [
                {'name': '荒行驿路', 'note': '环石与烽堠串联的安全线'},
                {'name': '火灰印关卡', 'note': '验印与互市税台'},
                {'name': '移动帆幕桥', 'note': '快速跨越沙沟'},
                {'name': '风壁栈道', 'note': '山脊侧壁行道'}
            ]
        }


async def main():
    """主函数"""
    initializer = GeographicDataInitializer(novel_id=1)
    await initializer.initialize_all_domains()
    print("所有域的地理数据初始化完成!")


if __name__ == "__main__":
    asyncio.run(main())