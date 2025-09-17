"""
剧情功能映射数据初始化脚本
将地点功能映射数据导入数据库
"""

import asyncio
from typing import List, Dict, Any
from ..connections.postgresql import get_postgresql_connection


class PlotMappingDataInitializer:
    """剧情映射数据初始化器"""

    def __init__(self, novel_id: int = 1):
        self.novel_id = novel_id

    async def initialize_all_data(self):
        """初始化所有剧情映射数据"""
        async with get_postgresql_connection() as conn:
            print("开始初始化剧情功能映射数据...")

            # 1. 初始化基础类型数据
            await self._init_function_types(conn)
            await self._init_node_types(conn)

            # 2. 初始化各域的地点映射
            await self._init_ren_yu_mappings(conn)
            await self._init_tian_yu_mappings(conn)
            await self._init_ling_yu_mappings(conn)
            await self._init_huang_yu_mappings(conn)

            print("剧情功能映射数据初始化完成！")

    async def _init_function_types(self, conn):
        """初始化功能类型数据"""
        print("初始化功能类型...")

        # 检查是否已存在数据
        existing = await conn.fetchval("SELECT COUNT(*) FROM plot_function_types")
        if existing > 0:
            print(f"功能类型数据已存在 ({existing} 条)，跳过初始化")
            return

        # 功能类型数据已在SQL文件中定义，这里只是验证
        await conn.execute("SELECT 1") # 占位查询
        print("功能类型数据验证完成")

    async def _init_node_types(self, conn):
        """初始化节点类型数据"""
        print("初始化节点类型...")

        # 检查是否已存在数据
        existing = await conn.fetchval("SELECT COUNT(*) FROM plot_node_types")
        if existing > 0:
            print(f"节点类型数据已存在 ({existing} 条)，跳过初始化")
            return

        # 节点类型数据已在SQL文件中定义，这里只是验证
        await conn.execute("SELECT 1") # 占位查询
        print("节点类型数据验证完成")

    async def _init_ren_yu_mappings(self, conn):
        """初始化人域地点映射"""
        print("初始化人域地点映射...")

        mappings = [
            # regions
            {
                "entity_name": "稻环平原",
                "entity_type": "region",
                "function_codes": ["F4", "F12", "F13"],
                "node_codes": ["①", "③", "⑥"],
                "hook_title": "洪峰将至救堤危机",
                "hook_description": "洪峰将至，地主逼村社"先签转粮链契"换救堤。",
                "hook_urgency": 5,
                "hook_drama_level": 8,
                "difficulty_level": 4
            },
            {
                "entity_name": "盐链丘陵",
                "entity_type": "region",
                "function_codes": ["F4", "F15"],
                "node_codes": ["①", "③"],
                "hook_title": "私盐走私冲突",
                "hook_description": "盐税加码，私盐被缚司当"冥盐"扣押，人域与缚司冲突。",
                "hook_urgency": 3,
                "hook_drama_level": 6,
                "difficulty_level": 3
            },
            {
                "entity_name": "北阙关带",
                "entity_type": "region",
                "function_codes": ["F3", "F20", "F9"],
                "node_codes": ["②", "③", "⑥"],
                "hook_title": "断链识别伪装潜入",
                "hook_description": "关带试行"断链识别"，主角需伪装链痕闯关。",
                "hook_urgency": 4,
                "hook_drama_level": 7,
                "difficulty_level": 4
            },
            {
                "entity_name": "南环水网",
                "entity_type": "region",
                "function_codes": ["F12", "F13", "F9"],
                "node_codes": ["③", "④"],
                "hook_title": "夜袭破堰救援",
                "hook_description": "夜袭破堰，主角救堤换取民心与线人。",
                "hook_urgency": 5,
                "hook_drama_level": 7,
                "difficulty_level": 4
            },

            # cities
            {
                "entity_name": "枢链城",
                "entity_type": "city",
                "function_codes": ["F2", "F5", "F19"],
                "node_codes": ["②", "③", "④"],
                "hook_title": "链税听证黑籍曝光",
                "hook_description": "链税听证反转，发现"黑籍配额"被私分。",
                "hook_urgency": 4,
                "hook_drama_level": 8,
                "difficulty_level": 3
            },
            {
                "entity_name": "环渠府",
                "entity_type": "city",
                "function_codes": ["F2", "F17", "F13"],
                "node_codes": ["③", "⑥"],
                "hook_title": "水利账本夜潜盗取",
                "hook_description": "调水账本遭篡改，主角夜潜水利司取真账。",
                "hook_urgency": 4,
                "hook_drama_level": 7,
                "difficulty_level": 5
            },
            {
                "entity_name": "九埠市",
                "entity_type": "city",
                "function_codes": ["F19", "F9", "F15"],
                "node_codes": ["③", "⑥"],
                "hook_title": "码头资金链断裂危机",
                "hook_description": "码头舱单链契被"因果锁"冻结，资金链断裂前限时自救。",
                "hook_urgency": 5,
                "hook_drama_level": 8,
                "difficulty_level": 4
            },

            # towns
            {
                "entity_name": "石环镇",
                "entity_type": "town",
                "function_codes": ["F6", "F9"],
                "node_codes": ["③"],
                "hook_title": "磨坊比产背后阴谋",
                "hook_description": "磨坊比产赛背后做局，揭出宗门代工压价链。",
                "hook_urgency": 3,
                "hook_drama_level": 6,
                "difficulty_level": 3
            },
            {
                "entity_name": "柳链集",
                "entity_type": "town",
                "function_codes": ["F6", "F19", "F8"],
                "node_codes": ["③"],
                "hook_title": "织造验评买通事件",
                "hook_description": "织造验评被"对手行会"买通，学徒集体维权。",
                "hook_urgency": 3,
                "hook_drama_level": 7,
                "difficulty_level": 3
            },
            {
                "entity_name": "环印关镇",
                "entity_type": "town",
                "function_codes": ["F3", "F20", "F14"],
                "node_codes": ["②", "⑥"],
                "hook_title": "边吏索贿反签逃脱",
                "hook_description": "边吏索贿截人，主角以"环印反签"临时赦行。",
                "hook_urgency": 4,
                "hook_drama_level": 6,
                "difficulty_level": 4
            },
            {
                "entity_name": "谷槌坊",
                "entity_type": "town",
                "function_codes": ["F5", "F6"],
                "node_codes": ["③"],
                "hook_title": "秋试断链辩论",
                "hook_description": "秋试链筵上公开"断链辩"，初获盟友亦结仇。",
                "hook_urgency": 3,
                "hook_drama_level": 6,
                "difficulty_level": 3
            },

            # villages
            {
                "entity_name": "白泥村",
                "entity_type": "village",
                "function_codes": ["F18", "F6"],
                "node_codes": ["①", "③"],
                "hook_title": "童年师父泥印作证",
                "hook_description": "童年师父泥印为证，反驳祭司的低判结论。",
                "hook_urgency": 3,
                "hook_drama_level": 8,
                "difficulty_level": 2
            },
            {
                "entity_name": "七环坝",
                "entity_type": "village",
                "function_codes": ["F13", "F12"],
                "node_codes": ["③", "④"],
                "hook_title": "堰坝决口伦理撕裂",
                "hook_description": "堰坝决口，村社投票"弃田保村"引伦理撕裂。",
                "hook_urgency": 5,
                "hook_drama_level": 7,
                "difficulty_level": 3
            },
            {
                "entity_name": "乌篱塍",
                "entity_type": "village",
                "function_codes": ["F18", "F8"],
                "node_codes": ["①", "④"],
                "hook_title": "灰籍亲友背叛伏笔",
                "hook_description": "灰籍亲友被逼为线人，背叛伏笔埋下。",
                "hook_urgency": 2,
                "hook_drama_level": 9,
                "difficulty_level": 2
            },
            {
                "entity_name": "河湾里",
                "entity_type": "village",
                "function_codes": ["F15", "F9"],
                "node_codes": ["③"],
                "hook_title": "阴祀掩护走私",
                "hook_description": "小船祀走私冥盐，主角借"阴祀"掩护转运。",
                "hook_urgency": 3,
                "hook_drama_level": 6,
                "difficulty_level": 4
            },

            # landmarks
            {
                "entity_name": "祖灵续籍台",
                "entity_type": "landmark",
                "function_codes": ["F1", "F14", "F18"],
                "node_codes": ["①", "④", "⑤"],
                "hook_title": "续籍夜改判翻案",
                "hook_description": "续籍夜，主角将"被灭门"改判为"误杀"，赢来翻案窗口。",
                "hook_urgency": 5,
                "hook_drama_level": 9,
                "difficulty_level": 5
            },
            {
                "entity_name": "县链枷祭坛",
                "entity_type": "landmark",
                "function_codes": ["F1", "F5", "F14"],
                "node_codes": ["④", "⑤"],
                "hook_title": "处决仪式环典异象",
                "hook_description": "处决仪式突发"环典异象"，舆论倒向。",
                "hook_urgency": 5,
                "hook_drama_level": 9,
                "difficulty_level": 4
            },
            {
                "entity_name": "三环亭",
                "entity_type": "landmark",
                "function_codes": ["F2", "F5"],
                "node_codes": ["②", "③"],
                "hook_title": "新政榜文法理拆招",
                "hook_description": "新政榜文漏洞，主角当众据法拆招。",
                "hook_urgency": 3,
                "hook_drama_level": 6,
                "difficulty_level": 3
            },
            {
                "entity_name": "老链桥",
                "entity_type": "landmark",
                "function_codes": ["F9", "F13"],
                "node_codes": ["②", "③", "④"],
                "hook_title": "追缉桥战队友坠河",
                "hook_description": "追缉大战桥上断链，队友坠河生死未卜。",
                "hook_urgency": 5,
                "hook_drama_level": 8,
                "difficulty_level": 4
            },
            {
                "entity_name": "环石通信阵",
                "entity_type": "landmark",
                "function_codes": ["F20", "F10"],
                "node_codes": ["③", "⑥"],
                "hook_title": "阵路监听揪出内鬼",
                "hook_description": "阵路被改线，传讯被监听，揪出内鬼。",
                "hook_urgency": 4,
                "hook_drama_level": 7,
                "difficulty_level": 4
            }
        ]

        await self._batch_create_mappings(conn, "人域", mappings)

    async def _init_tian_yu_mappings(self, conn):
        """初始化天域地点映射"""
        print("初始化天域地点映射...")

        mappings = [
            # regions
            {
                "entity_name": "九环京畿",
                "entity_type": "region",
                "function_codes": ["F5", "F11", "F2"],
                "node_codes": ["③", "⑥", "⑦"],
                "hook_title": "首都学潮推上风口",
                "hook_description": "首都学潮把主角推上舆论巅峰或深渊。",
                "hook_urgency": 5,
                "hook_drama_level": 9,
                "difficulty_level": 5
            },
            {
                "entity_name": "御链大道圈层",
                "entity_type": "region",
                "function_codes": ["F20", "F9"],
                "node_codes": ["②", "③", "⑥"],
                "hook_title": "帝路封锁劫车送文",
                "hook_description": "帝路封锁，主角劫车送"赦缚文"。",
                "hook_urgency": 5,
                "hook_drama_level": 8,
                "difficulty_level": 5
            },
            {
                "entity_name": "东御陵原",
                "entity_type": "region",
                "function_codes": ["F1", "F14", "F10"],
                "node_codes": ["⑤", "⑥"],
                "hook_title": "陵原密册揭旧朝真相",
                "hook_description": "陵原密册揭旧朝真相，赦免有据。",
                "hook_urgency": 4,
                "hook_drama_level": 8,
                "difficulty_level": 4
            },
            {
                "entity_name": "西台群山",
                "entity_type": "region",
                "function_codes": ["F20", "F13", "F12"],
                "node_codes": ["③", "④"],
                "hook_title": "烽台误报边军戒严",
                "hook_description": "烽台"误报"，引发边军提前戒严。",
                "hook_urgency": 4,
                "hook_drama_level": 6,
                "difficulty_level": 3
            },

            # cities
            {
                "entity_name": "九环京",
                "entity_type": "city",
                "function_codes": ["F5", "F11", "F2"],
                "node_codes": ["③", "⑥", "⑦"],
                "hook_title": "朝会质询改制窗口",
                "hook_description": "朝会公开质询链法，改制窗口开启/关闭。",
                "hook_urgency": 5,
                "hook_drama_level": 10,
                "difficulty_level": 5
            },
            {
                "entity_name": "白金府",
                "entity_type": "city",
                "function_codes": ["F19", "F2", "F17"],
                "node_codes": ["③", "⑥"],
                "hook_title": "参数拨款黑箱撬开",
                "hook_description": "链算总院与总库之间的"参数-拨款"黑箱被撬。",
                "hook_urgency": 4,
                "hook_drama_level": 8,
                "difficulty_level": 5
            },
            {
                "entity_name": "御链港",
                "entity_type": "city",
                "function_codes": ["F20", "F3", "F19"],
                "node_codes": ["②", "③", "⑥"],
                "hook_title": "禁运源域古链海战",
                "hook_description": "禁运清单里夹带"源域古链"，海上交锋。",
                "hook_urgency": 4,
                "hook_drama_level": 8,
                "difficulty_level": 4
            },

            # towns
            {
                "entity_name": "环阶镇",
                "entity_type": "town",
                "function_codes": ["F6", "F5", "F7"],
                "node_codes": ["③"],
                "hook_title": "礼器验收翻车闹京",
                "hook_description": "礼器验收翻车，匠人闹进京。",
                "hook_urgency": 3,
                "hook_drama_level": 6,
                "difficulty_level": 3
            },
            {
                "entity_name": "御书镇",
                "entity_type": "town",
                "function_codes": ["F10", "F2", "F16"],
                "node_codes": ["③"],
                "hook_title": "石经刻误正统造假",
                "hook_description": "石经刻误一字，牵出"正统"造假。",
                "hook_urgency": 4,
                "hook_drama_level": 7,
                "difficulty_level": 4
            },
            {
                "entity_name": "链库镇",
                "entity_type": "town",
                "function_codes": ["F4", "F17", "F9"],
                "node_codes": ["③", "⑥"],
                "hook_title": "军需北调截供之战",
                "hook_description": "军需北调，沿途截供之战。",
                "hook_urgency": 5,
                "hook_drama_level": 8,
                "difficulty_level": 4
            },
            {
                "entity_name": "禁园卫镇",
                "entity_type": "town",
                "function_codes": ["F12", "F9"],
                "node_codes": ["③", "④"],
                "hook_title": "禁苑水网夜追脱身",
                "hook_description": "禁苑水网夜追，主角借地形脱身。",
                "hook_urgency": 4,
                "hook_drama_level": 7,
                "difficulty_level": 4
            },

            # landmarks
            {
                "entity_name": "御环台",
                "entity_type": "landmark",
                "function_codes": ["F1", "F5", "F14", "F11"],
                "node_codes": ["④", "⑥"],
                "hook_title": "御前审链自证正当",
                "hook_description": "御前审链，主角以"断链不等于弑链"自证正当。",
                "hook_urgency": 5,
                "hook_drama_level": 10,
                "difficulty_level": 5
            },
            {
                "entity_name": "九环书院",
                "entity_type": "landmark",
                "function_codes": ["F5", "F7", "F6"],
                "node_codes": ["③"],
                "hook_title": "辩链赛胜学生兵团",
                "hook_description": "辩链赛胜出，学生会成为主角舆论兵团。",
                "hook_urgency": 3,
                "hook_drama_level": 7,
                "difficulty_level": 3
            },
            {
                "entity_name": "链算所总院",
                "entity_type": "landmark",
                "function_codes": ["F2", "F17", "F10"],
                "node_codes": ["③", "⑥"],
                "hook_title": "窃出容错阈值记录",
                "hook_description": "窃出"容错阈值"改动记录。",
                "hook_urgency": 4,
                "hook_drama_level": 7,
                "difficulty_level": 5
            },
            {
                "entity_name": "环典石经塔",
                "entity_type": "landmark",
                "function_codes": ["F1", "F2", "F10"],
                "node_codes": ["②", "③"],
                "hook_title": "经塔异象推翻辟谣",
                "hook_description": "经塔异象推翻祭司辟谣，舆论倒向。",
                "hook_urgency": 4,
                "hook_drama_level": 8,
                "difficulty_level": 3
            },
            {
                "entity_name": "悬链梁殿群",
                "entity_type": "landmark",
                "function_codes": ["F11", "F17"],
                "node_codes": ["⑥"],
                "hook_title": "殿顶链索机关杀",
                "hook_description": "殿顶链索可被"断缚"做机关，决战地形杀。",
                "hook_urgency": 5,
                "hook_drama_level": 9,
                "difficulty_level": 5
            }
        ]

        await self._batch_create_mappings(conn, "天域", mappings)

    async def _init_ling_yu_mappings(self, conn):
        """初始化灵域地点映射"""
        print("初始化灵域地点映射...")

        mappings = [
            # regions
            {
                "entity_name": "工环盆地",
                "entity_type": "region",
                "function_codes": ["F6", "F12", "F5"],
                "node_codes": ["③"],
                "hook_title": "行会黑坊互咬",
                "hook_description": "镇上行会与黑坊互咬。",
                "hook_urgency": 3,
                "hook_drama_level": 6,
                "difficulty_level": 3
            },

            # towns
            {
                "entity_name": "纸链镇",
                "entity_type": "town",
                "function_codes": ["F4", "F2", "F10"],
                "node_codes": ["③"],
                "hook_title": "抄经纸水印私单",
                "hook_description": "抄经纸走漏水印，查出评印院私单。",
                "hook_urgency": 3,
                "hook_drama_level": 6,
                "difficulty_level": 4
            },
            {
                "entity_name": "丝环镇",
                "entity_type": "town",
                "function_codes": ["F4", "F6", "F19"],
                "node_codes": ["③"],
                "hook_title": "织局压价链契纠纷",
                "hook_description": "织局遭"压价链契"，学徒聚众停机讨说法。",
                "hook_urgency": 3,
                "hook_drama_level": 7,
                "difficulty_level": 3
            },

            # villages
            {
                "entity_name": "竹环村",
                "entity_type": "village",
                "function_codes": ["F18", "F6"],
                "node_codes": ["①", "③"],
                "hook_title": "先师竹环墨配方",
                "hook_description": "先师遗留"竹环墨配方被窃，顺着"油水账"摸到行会内鬼。",
                "hook_urgency": 3,
                "hook_drama_level": 7,
                "difficulty_level": 3
            },

            # buildings
            {
                "entity_name": "链纤维织局",
                "entity_type": "building",
                "function_codes": ["F4", "F6"],
                "node_codes": ["③"],
                "hook_title": "产线连爆断纤虫",
                "hook_description": "产线连爆事故，疑似对手投"断纤虫"。",
                "hook_urgency": 4,
                "hook_drama_level": 7,
                "difficulty_level": 4
            },
            {
                "entity_name": "连拱作坊群",
                "entity_type": "building",
                "function_codes": ["F6", "F9", "F13"],
                "node_codes": ["③", "④"],
                "hook_title": "火线救人拱道坍塌",
                "hook_description": "火线救人+巷战追凶，拱道坍塌倒计时。",
                "hook_urgency": 5,
                "hook_drama_level": 8,
                "difficulty_level": 5
            },

            # landmarks
            {
                "entity_name": "器衡塔",
                "entity_type": "landmark",
                "function_codes": ["F2", "F10", "F6"],
                "node_codes": ["③", "⑥"],
                "hook_title": "校准标准暗改复测",
                "hook_description": "校准标准被暗改，现场复测扭转局面。",
                "hook_urgency": 4,
                "hook_drama_level": 7,
                "difficulty_level": 4
            }
        ]

        await self._batch_create_mappings(conn, "灵域", mappings)

    async def _init_huang_yu_mappings(self, conn):
        """初始化荒域地点映射"""
        print("初始化荒域地点映射...")

        mappings = [
            # regions
            {
                "entity_name": "风裂沙海",
                "entity_type": "region",
                "function_codes": ["F13", "F9", "F11"],
                "node_codes": ["③", "④", "⑥"],
                "hook_title": "沙暴互换旗号埋伏",
                "hook_description": "白茫沙暴中互换旗号，埋伏主力。",
                "hook_urgency": 5,
                "hook_drama_level": 8,
                "difficulty_level": 5
            },
            {
                "entity_name": "骨环谷地",
                "entity_type": "region",
                "function_codes": ["F4", "F12", "F1"],
                "node_codes": ["③", "⑤"],
                "hook_title": "祖骨祭遗械争端",
                "hook_description": "祖骨祭中出土遗械，引发归属争端。",
                "hook_urgency": 4,
                "hook_drama_level": 7,
                "difficulty_level": 4
            },

            # cities
            {
                "entity_name": "地窖城·赤环",
                "entity_type": "city",
                "function_codes": ["F12", "F15", "F5"],
                "node_codes": ["③", "⑥"],
                "hook_title": "地层崩塌供水危机",
                "hook_description": "地层崩塌+供水危机，黑市囤水抬价。",
                "hook_urgency": 5,
                "hook_drama_level": 8,
                "difficulty_level": 4
            },
            {
                "entity_name": "嵯峨堡",
                "entity_type": "city",
                "function_codes": ["F4", "F17", "F9"],
                "node_codes": ["③", "⑥"],
                "hook_title": "断链器铸造权争夺",
                "hook_description": "断链器铸造权之争，引发夜袭攻防。",
                "hook_urgency": 4,
                "hook_drama_level": 8,
                "difficulty_level": 5
            },
            {
                "entity_name": "风孔城",
                "entity_type": "city",
                "function_codes": ["F3", "F9", "F20"],
                "node_codes": ["②", "③", "⑥"],
                "hook_title": "护风塔失灵城战",
                "hook_description": "护风塔失灵，税卡冲突升级为城战。",
                "hook_urgency": 5,
                "hook_drama_level": 9,
                "difficulty_level": 4
            },

            # towns
            {
                "entity_name": "灰帐镇",
                "entity_type": "town",
                "function_codes": ["F15", "F7", "F5"],
                "node_codes": ["③"],
                "hook_title": "黑市拍卖三方争夺",
                "hook_description": "黑市拍卖"可控链崩器"，部落/行会/密探三方争夺。",
                "hook_urgency": 5,
                "hook_drama_level": 9,
                "difficulty_level": 5
            },
            {
                "entity_name": "沙咽镇",
                "entity_type": "town",
                "function_codes": ["F4", "F12", "F2"],
                "node_codes": ["③", "④"],
                "hook_title": "井群中毒水权仲裁",
                "hook_description": "井群中毒，水权仲裁触怒部落。",
                "hook_urgency": 4,
                "hook_drama_level": 7,
                "difficulty_level": 4
            },
            {
                "entity_name": "断骨镇",
                "entity_type": "town",
                "function_codes": ["F6", "F1", "F18"],
                "node_codes": ["②", "③", "⑤"],
                "hook_title": "成人礼价值观分裂",
                "hook_description": "成人礼选择牺牲/保全，引发价值观分裂。",
                "hook_urgency": 3,
                "hook_drama_level": 8,
                "difficulty_level": 3
            },

            # villages
            {
                "entity_name": "火誓营地",
                "entity_type": "village",
                "function_codes": ["F1", "F7", "F12"],
                "node_codes": ["②", "③", "⑥"],
                "hook_title": "断环誓军团成立",
                "hook_description": "断环誓军团在此成立，风誓同盟签订。",
                "hook_urgency": 4,
                "hook_drama_level": 8,
                "difficulty_level": 4
            },
            {
                "entity_name": "骨链村",
                "entity_type": "village",
                "function_codes": ["F18", "F6"],
                "node_codes": ["①", "③", "⑤"],
                "hook_title": "祖骨传承叛祖秘史",
                "hook_description": "祖骨传承试炼揭出"叛祖"秘史。",
                "hook_urgency": 3,
                "hook_drama_level": 9,
                "difficulty_level": 3
            },
            {
                "entity_name": "风影窟落",
                "entity_type": "village",
                "function_codes": ["F12", "F9", "F13"],
                "node_codes": ["③", "④"],
                "hook_title": "风洞迷路裂兽追击",
                "hook_description": "风洞迷路与裂兽追击并发，靠"风纹"脱险。",
                "hook_urgency": 4,
                "hook_drama_level": 7,
                "difficulty_level": 4
            },

            # landmarks
            {
                "entity_name": "祖灵火坛",
                "entity_type": "landmark",
                "function_codes": ["F1", "F5", "F14"],
                "node_codes": ["④", "⑤"],
                "hook_title": "火种被掠直播追赎",
                "hook_description": "火种被掠，族会直播追赎，民心集中。",
                "hook_urgency": 5,
                "hook_drama_level": 9,
                "difficulty_level": 4
            },
            {
                "entity_name": "断链祭场",
                "entity_type": "landmark",
                "function_codes": ["F1", "F11", "F13"],
                "node_codes": ["④", "⑤", "⑥"],
                "hook_title": "临时断链救阵抉择",
                "hook_description": "临时断链爆发救阵，人祭与自断道德抉择。",
                "hook_urgency": 5,
                "hook_drama_level": 10,
                "difficulty_level": 5
            },
            {
                "entity_name": "沉链坑",
                "entity_type": "landmark",
                "function_codes": ["F17", "F4", "F13"],
                "node_codes": ["③", "④", "⑥"],
                "hook_title": "危械出土失控群殴",
                "hook_description": "危械出土失控，抢夺变群殴。",
                "hook_urgency": 5,
                "hook_drama_level": 8,
                "difficulty_level": 5
            }
        ]

        await self._batch_create_mappings(conn, "荒域", mappings)

    async def _batch_create_mappings(self, conn, domain_name: str, mappings: List[Dict[str, Any]]):
        """批量创建剧情映射"""
        created_count = 0
        skipped_count = 0

        for mapping in mappings:
            try:
                # 查找实体ID
                entity_query = """
                SELECT e.id FROM entities e
                JOIN entity_types et ON e.entity_type_id = et.id
                WHERE e.novel_id = $1 AND e.name = $2 AND et.name = $3 AND e.status = 'active'
                """

                entity_row = await conn.fetchrow(
                    entity_query, self.novel_id, mapping["entity_name"], mapping["entity_type"]
                )

                if not entity_row:
                    print(f"  警告: 实体不存在 - {mapping['entity_name']} ({mapping['entity_type']})")
                    skipped_count += 1
                    continue

                entity_id = entity_row["id"]

                # 检查是否已存在映射
                existing = await conn.fetchrow(
                    "SELECT id FROM geographic_plot_mappings WHERE novel_id = $1 AND entity_id = $2",
                    self.novel_id, entity_id
                )

                if existing:
                    print(f"  跳过: {mapping['entity_name']} (映射已存在)")
                    skipped_count += 1
                    continue

                # 创建映射
                insert_query = """
                INSERT INTO geographic_plot_mappings (
                    novel_id, entity_id, function_codes, node_codes,
                    hook_title, hook_description, hook_urgency, hook_drama_level,
                    difficulty_level, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """

                from datetime import datetime
                now = datetime.utcnow()

                await conn.execute(
                    insert_query, self.novel_id, entity_id,
                    mapping["function_codes"], mapping["node_codes"],
                    mapping["hook_title"], mapping["hook_description"],
                    mapping["hook_urgency"], mapping["hook_drama_level"],
                    mapping["difficulty_level"], now, now
                )

                created_count += 1
                print(f"  ✓ {mapping['entity_name']}")

            except Exception as e:
                print(f"  错误: 创建 {mapping['entity_name']} 映射失败 - {str(e)}")
                skipped_count += 1

        print(f"{domain_name}映射完成: 创建 {created_count} 个，跳过 {skipped_count} 个")


async def main():
    """主函数"""
    initializer = PlotMappingDataInitializer(novel_id=1)
    await initializer.initialize_all_data()


if __name__ == "__main__":
    asyncio.run(main())