-- =============================================================================
-- 跨域冲突矩阵初始化脚本
-- 基于前四域（人域/天域/灵域/荒域）的冲突设定
-- =============================================================================

-- 假设小说ID为1，代表"裂世九域"项目
-- 如果需要其他小说ID，请修改下面的 @novel_id 变量

-- =============================================================================
-- 1. 插入四个域的基础信息
-- =============================================================================

-- 插入人域
INSERT INTO domains (novel_id, name, code, display_name, dominant_law, ruling_power,
                    power_level, civilization_level, stability_level, sort_order,
                    geographic_features, climate_info, resources) VALUES
(1, '人域', 'ren_yu', '人族聚居域', '链籍法系', '乡绅里正体系',
 4, 6, 7, 1,
 '{"terrain": "平原丘陵", "settlements": "县城村镇", "infrastructure": "环印门网络"}',
 '{"type": "温带", "seasons": "四季分明", "agriculture": "适宜耕作"}',
 '{"primary": ["粮食", "链墨", "链纤维"], "secondary": ["人力", "手工制品"], "trade": ["边境互市", "工坊代工"]}');

-- 插入天域
INSERT INTO domains (novel_id, name, code, display_name, dominant_law, ruling_power,
                    power_level, civilization_level, stability_level, sort_order,
                    geographic_features, climate_info, resources) VALUES
(1, '天域', 'tian_yu', '天链统御域', '环约律令', '御环台体系',
 8, 9, 6, 2,
 '{"terrain": "高台宫城", "settlements": "都城军镇", "infrastructure": "链算所网络"}',
 '{"type": "高原", "seasons": "链能丰沛", "environment": "庄严肃穆"}',
 '{"primary": ["链算力", "军事装备", "行政权力"], "secondary": ["税收", "征召权"], "control": ["评印权", "链籍管理", "军事指挥"]}');

-- 插入灵域
INSERT INTO domains (novel_id, name, code, display_name, dominant_law, ruling_power,
                    power_level, civilization_level, stability_level, sort_order,
                    geographic_features, climate_info, resources) VALUES
(1, '灵域', 'ling_yu', '器工造化域', '工程链契', '宗匠公会体系',
 7, 8, 7, 3,
 '{"terrain": "工坊集群", "settlements": "宗门坊市", "infrastructure": "评印院网络"}',
 '{"type": "多样化", "seasons": "适应各类工艺", "environment": "技术导向"}',
 '{"primary": ["链工技术", "精密器械", "评印服务"], "secondary": ["学徒培训", "技术标准"], "innovation": ["新工艺", "链器改良", "界核维护"]}');

-- 插入荒域
INSERT INTO domains (novel_id, name, code, display_name, dominant_law, ruling_power,
                    power_level, civilization_level, stability_level, sort_order,
                    geographic_features, climate_info, resources) VALUES
(1, '荒域', 'huang_yu', '断链部落域', '部落火典', '断链祭司体系',
 6, 4, 4, 4,
 '{"terrain": "沙脊荒原", "settlements": "部落营地", "infrastructure": "火灰印路线"}',
 '{"type": "干旱", "seasons": "裂世夜频发", "environment": "资源稀缺"}',
 '{"primary": ["链矿原料", "断链技术", "游牧产品"], "secondary": ["边境贸易", "护运服务"], "special": ["祖灵火", "断链器", "遗迹探索"]}');

-- =============================================================================
-- 2. 插入摩擦热度矩阵（通过冲突强度体现）
-- =============================================================================

-- 天域 ↔ 人域（高强度：税役/链籍/征召）
INSERT INTO cultural_conflicts (novel_id, primary_domain_id, secondary_domain_id,
                               conflict_type, conflict_name, description,
                               intensity_level, historical_depth, resolution_difficulty,
                               status, current_manifestation, affected_areas, stakeholders)
SELECT 1,
       (SELECT id FROM domains WHERE code = 'tian_yu' AND novel_id = 1),
       (SELECT id FROM domains WHERE code = 'ren_yu' AND novel_id = 1),
       'power', '税役征收冲突', '天域通过链籍制度对人域实施严格的税收和人役征收，引发民众不满',
       8, 3, 8, 'ongoing', '链祭日征收配额上调，黑籍户数量激增',
       '{"economic": "税收负担", "social": "社会分层", "political": "统治合法性"}',
       '["巡链官", "缚司", "乡祭", "里正", "黑籍户", "普通民众"]';

-- 天域 ↔ 灵域（中高强度：监管/评印权/链法）
INSERT INTO cultural_conflicts (novel_id, primary_domain_id, secondary_domain_id,
                               conflict_type, conflict_name, description,
                               intensity_level, historical_depth, resolution_difficulty,
                               status, current_manifestation, affected_areas, stakeholders)
SELECT 1,
       (SELECT id FROM domains WHERE code = 'tian_yu' AND novel_id = 1),
       (SELECT id FROM domains WHERE code = 'ling_yu' AND novel_id = 1),
       'power', '评印权争夺', '天域试图控制灵域的技术标准和评印权，与宗匠自治传统冲突',
       7, 2, 7, 'escalating', '万器朝链仪式中评印院抗议新规，多项标案被政治化',
       '{"technical": "标准制定", "economic": "承包利益", "professional": "行业自治"}',
       '["评印院执事", "链算所监理", "宗匠", "公会头人"]';

-- 天域 ↔ 荒域（高强度：断链/矿脉/军镇）
INSERT INTO cultural_conflicts (novel_id, primary_domain_id, secondary_domain_id,
                               conflict_type, conflict_name, description,
                               intensity_level, historical_depth, resolution_difficulty,
                               status, current_manifestation, affected_areas, stakeholders)
SELECT 1,
       (SELECT id FROM domains WHERE code = 'tian_yu' AND novel_id = 1),
       (SELECT id FROM domains WHERE code = 'huang_yu' AND novel_id = 1),
       'territory', '边域控制争端', '天域军镇与荒域部落在边境资源和断链者庇护问题上长期对立',
       9, 5, 9, 'escalating', '裂世夜取缔令执行，多个部落祖灵火被强制熄灭',
       '{"territorial": "边境控制", "resource": "链矿开采", "cultural": "断链权利"}',
       '["军镇都尉", "断链祭司", "部落首领", "天域密探"]';

-- 人域 ↔ 灵域（中强度：学徒/供货/评印）
INSERT INTO cultural_conflicts (novel_id, primary_domain_id, secondary_domain_id,
                               conflict_type, conflict_name, description,
                               intensity_level, historical_depth, resolution_difficulty,
                               status, current_manifestation, affected_areas, stakeholders)
SELECT 1,
       (SELECT id FROM domains WHERE code = 'ren_yu' AND novel_id = 1),
       (SELECT id FROM domains WHERE code = 'ling_yu' AND novel_id = 1),
       'resource', '劳工关系纠纷', '灵域工坊大量使用人域学徒和代工，但待遇和安全问题引发冲突',
       5, 2, 6, 'simmering', '合环奖季外包爆雷，数百学徒被迫签署不平等契约',
       '{"labor": "用工关系", "economic": "价格体系", "social": "阶层流动"}',
       '["坊主", "宗匠", "乡绅中介", "学徒家属", "评印巡官"]';

-- 人域 ↔ 荒域（中高强度：边贸/走私/治安）
INSERT INTO cultural_conflicts (novel_id, primary_domain_id, secondary_domain_id,
                               conflict_type, conflict_name, description,
                               intensity_level, historical_depth, resolution_difficulty,
                               status, current_manifestation, affected_areas, stakeholders)
SELECT 1,
       (SELECT id FROM domains WHERE code = 'ren_yu' AND novel_id = 1),
       (SELECT id FROM domains WHERE code = 'huang_yu' AND novel_id = 1),
       'resource', '边贸监管争议', '人域与荒域边境贸易中的税收、走私和治安问题持续发酵',
       6, 3, 5, 'ongoing', '火灰印被仿造，正当商队被误认为盗匪遭到围剿',
       '{"trade": "边境贸易", "security": "治安管理", "legal": "税收执法"}',
       '["互市头人", "护运队长", "县缚司", "部落青年"]';

-- 灵域 ↔ 荒域（中高强度：黑市器/矿料/遗械）
INSERT INTO cultural_conflicts (novel_id, primary_domain_id, secondary_domain_id,
                               conflict_type, conflict_name, description,
                               intensity_level, historical_depth, resolution_difficulty,
                               status, current_manifestation, affected_areas, stakeholders)
SELECT 1,
       (SELECT id FROM domains WHERE code = 'ling_yu' AND novel_id = 1),
       (SELECT id FROM domains WHERE code = 'huang_yu' AND novel_id = 1),
       'resource', '危械交易争端', '灵域黑市向荒域提供断链器械，但监管和遗迹开发权引发复杂纠纷',
       7, 2, 7, 'escalating', '遗迹发现可控链崩器，双方对处置权产生严重分歧',
       '{"technology": "危险技术", "resource": "遗迹开发", "trade": "黑市交易"}',
       '["黑坊宗匠", "部落锻师", "评印巡官", "断链祭司"]';

-- =============================================================================
-- 3. 插入相关剧情钩子
-- =============================================================================

-- 3.1 天域 ↔ 人域 剧情钩子
INSERT INTO plot_hooks (novel_id, domain_id, title, description, hook_type,
                       drama_level, scope, urgency_level, potential_outcomes,
                       involved_entities, status)
SELECT 1,
       (SELECT id FROM domains WHERE code = 'tian_yu' AND novel_id = 1),
       '黑籍配额暗增',
       '链祭日前夕，县府突然增加"黑籍配额"，里社档册被秘密修改，多个清白家庭面临降籍危机',
       'crisis', 8, 'regional', 4,
       '{"success": "揭露腐败，恢复清白", "failure": "大量民众被降为黑籍", "complications": "引发更大规模抗议"}',
       '["巡链官", "缚司", "里正", "受害家庭"]', 'available';

INSERT INTO plot_hooks (novel_id, domain_id, title, description, hook_type,
                       drama_level, scope, urgency_level, potential_outcomes,
                       involved_entities, status)
SELECT 1,
       (SELECT id FROM domains WHERE code = 'tian_yu' AND novel_id = 1),
       '链测受贿疑云',
       '新生链测出现大规模"集体低判"，众多天赋儿童被判定为黑籍，背后怀疑祭司收受贿赂换籍',
       'mystery', 7, 'domain', 3,
       '{"discovery": "揭露祭司腐败网络", "cover_up": "证据被销毁，祭司转移", "escalation": "影响整个链籍制度公信力"}',
       '["链测祭司", "受影响家庭", "巡链官", "知情官员"]', 'available';

-- 3.2 天域 ↔ 灵域 剧情钩子
INSERT INTO plot_hooks (novel_id, domain_id, title, description, hook_type,
                       drama_level, scope, urgency_level, potential_outcomes,
                       involved_entities, status)
SELECT 1,
       (SELECT id FROM domains WHERE code = 'tian_yu' AND novel_id = 1),
       '界核招标内幕',
       '御前项目"界核·九阶"招标中，唯一合格的技术标准被指控为某个大宗门量身定制，存在利益输送嫌疑',
       'conflict', 9, 'domain', 4,
       '{"exposure": "招标重新进行，建立公平标准", "cover_up": "异议者被压制，垄断加剧", "compromise": "标准微调，多方利益平衡"}',
       '["评印院执事", "涉事宗门", "竞争宗门", "链算所监理"]', 'available';

INSERT INTO plot_hooks (novel_id, domain_id, title, description, hook_type,
                       drama_level, scope, urgency_level, potential_outcomes,
                       involved_entities, status)
SELECT 1,
       (SELECT id FROM domains WHERE code = 'tian_yu' AND novel_id = 1),
       '链压崩塌事故',
       '链算所暗中修改容错参数，导致边境小城链压系统崩塌，伤亡惨重，技术责任与政治阴谋交织',
       'crisis', 10, 'regional', 5,
       '{"accountability": "技术标准改革，责任人问责", "cover_up": "事故归咎于意外，真相被掩盖", "escalation": "更多城市链压系统受到质疑"}',
       '["链算所技师", "受灾民众", "调查官员", "宗匠技术专家"]', 'available';

-- 3.3 天域 ↔ 荒域 剧情钩子
INSERT INTO plot_hooks (novel_id, domain_id, title, description, hook_type,
                       drama_level, scope, urgency_level, potential_outcomes,
                       involved_entities, status)
SELECT 1,
       (SELECT id FROM domains WHERE code = 'huang_yu' AND novel_id = 1),
       '祖灵火危机',
       '裂世夜被强制解散，部落守火者遭到逮捕，多个部落的祖灵火面临熄灭危险，触及荒域文化根基',
       'crisis', 9, 'domain', 5,
       '{"resistance": "部落联合抗击，重燃祖灵火", "submission": "接受天域管制，传统断绝", "escalation": "全面战争爆发"}',
       '["断链祭司", "部落首领", "守火者", "军镇都尉"]', 'available';

INSERT INTO plot_hooks (novel_id, domain_id, title, description, hook_type,
                       drama_level, scope, urgency_level, potential_outcomes,
                       involved_entities, status)
SELECT 1,
       (SELECT id FROM domains WHERE code = 'tian_yu' AND novel_id = 1),
       '伪部落诱捕',
       '边墙内发现"天域伪部落"，专门设局诱捕真正的荒域部落成员，这种渗透策略引发荒域愤怒',
       'betrayal', 8, 'regional', 4,
       '{"exposure": "伪装被识破，天域计划失败", "success": "大量部落成员被捕", "retaliation": "荒域发起报复行动"}',
       '["天域密探", "伪装部落", "真部落成员", "边境守军"]', 'available';

-- 3.4 人域 ↔ 灵域 剧情钩子
INSERT INTO plot_hooks (novel_id, domain_id, title, description, hook_type,
                       drama_level, scope, urgency_level, potential_outcomes,
                       involved_entities, status)
SELECT 1,
       (SELECT id FROM domains WHERE code = 'ling_yu' AND novel_id = 1),
       '合环奖爆雷',
       '"合环奖"季外包项目突然爆雷，数百学徒被迫签署"空白链契"，沦为廉价劳动力',
       'crisis', 7, 'regional', 4,
       '{"rescue": "学徒获得解救，不平等契约被废除", "exploitation": "更多学徒被迫签约", "reform": "学徒保护法规建立"}',
       '["坊主", "被困学徒", "学徒家属", "宗匠", "乡绅中介"]', 'available';

INSERT INTO plot_hooks (novel_id, domain_id, title, description, hook_type,
                       drama_level, scope, urgency_level, potential_outcomes,
                       involved_entities, status)
SELECT 1,
       (SELECT id FROM domains WHERE code = 'ling_yu' AND novel_id = 1),
       '评印恶性竞争',
       '评印抽检连续毁掉三个村庄的代工产业，调查发现竞争对手恶意举报引流，行业内幕黑暗',
       'discovery', 6, 'local', 3,
       '{"justice": "恶意竞争被制止，受害村庄获得补偿", "escalation": "恶性竞争蔓延，更多代工受害", "corruption": "评印系统腐败曝光"}',
       '["评印巡官", "受害村民", "竞争坊主", "举报者"]', 'available';

-- 3.5 人域 ↔ 荒域 剧情钩子
INSERT INTO plot_hooks (novel_id, domain_id, title, description, hook_type,
                       drama_level, scope, urgency_level, potential_outcomes,
                       involved_entities, status)
SELECT 1,
       (SELECT id FROM domains WHERE code = 'huang_yu' AND novel_id = 1),
       '救灾粮争议',
       '灾年荒骑冒险护送"救灾粮"进入人域，却被县府以"未税走私"名义扣押，人道主义与法规冲突',
       'conflict', 6, 'regional', 4,
       '{"humanitarian": "救灾粮被放行，建立紧急援助机制", "bureaucratic": "严格执法，救灾粮被没收", "compromise": "补交税款后放行，但效率低下"}',
       '["荒骑护送队", "县缚司", "灾民", "互市头人"]', 'available';

INSERT INTO plot_hooks (novel_id, domain_id, title, description, hook_type,
                       drama_level, scope, urgency_level, potential_outcomes,
                       involved_entities, status)
SELECT 1,
       (SELECT id FROM domains WHERE code = 'ren_yu' AND novel_id = 1),
       '火灰印伪造',
       '火灰印被恶意仿造，合法商队被误认为盗匪遭到围剿，边贸信任体系面临崩塌',
       'betrayal', 7, 'regional', 4,
       '{"investigation": "找出伪造者，恢复火灰印信誉", "chaos": "边贸秩序崩坏，冲突加剧", "reform": "建立新的认证体系"}',
       '["正当商队", "护运队长", "县缚司", "边境民兵"]', 'available';

-- 3.6 灵域 ↔ 荒域 剧情钩子
INSERT INTO plot_hooks (novel_id, domain_id, title, description, hook_type,
                       drama_level, scope, urgency_level, potential_outcomes,
                       involved_entities, status)
SELECT 1,
       (SELECT id FROM domains WHERE code = 'ling_yu' AND novel_id = 1),
       '链崩器争夺',
       '遗迹口发现"可控链崩器"，灵域希望封存研究，荒域要带走对付军镇，危险技术引发激烈争夺',
       'discovery', 9, 'domain', 5,
       '{"containment": "危险技术被安全封存", "weaponization": "技术被用于战争，后果不堪设想", "research": "合作研究，找到安全应用方式"}',
       '["黑坊宗匠", "部落锻师", "断链祭司", "评印院专家"]', 'available';

INSERT INTO plot_hooks (novel_id, domain_id, title, description, hook_type,
                       drama_level, scope, urgency_level, potential_outcomes,
                       involved_entities, status)
SELECT 1,
       (SELECT id FROM domains WHERE code = 'ling_yu' AND novel_id = 1),
       '环价操控',
       '黑市"环价联动"操控矿料价格，部落和工坊都被收割，背后操盘手身份神秘，利益网络复杂',
       'mystery', 8, 'cross_domain', 3,
       '{"exposure": "操控网络被曝光，价格体系重建", "consolidation": "操控者控制更多资源", "rebellion": "部落和工坊联合反击"}',
       '["神秘操盘手", "部落首领", "工坊主", "黑市商人"]', 'available';

-- =============================================================================
-- 4. 插入文化维度和框架（用于组织法条仪式等要素）
-- =============================================================================

-- 插入法律制度维度（如果不存在）
INSERT INTO cultural_dimensions (code, name, display_name, description, dimension_type, importance_weight, sort_order)
VALUES ('legal_system', '法律制度', '法律制度与规范体系', '各域的法律条文、制度规范和执行机制', 'political', 8, 1)
ON CONFLICT (code) DO NOTHING;

-- 插入仪式传统维度（如果不存在）
INSERT INTO cultural_dimensions (code, name, display_name, description, dimension_type, importance_weight, sort_order)
VALUES ('ritual_tradition', '仪式传统', '仪式传统与文化实践', '各域的传统仪式、庆典和文化实践', 'cultural', 7, 2)
ON CONFLICT (code) DO NOTHING;

-- 为各域创建法律制度框架
INSERT INTO cultural_frameworks (novel_id, domain_id, dimension_id, framework_name, core_concept, key_features, completeness_score)
SELECT 1,
       d.id,
       (SELECT id FROM cultural_dimensions WHERE code = 'legal_system'),
       d.display_name || '法律制度框架',
       CASE d.code
           WHEN 'tian_yu' THEN '环约律令体系，以链籍制度为核心的统治法律'
           WHEN 'ren_yu' THEN '传统乡治法系，以里社组织为基础的民间法'
           WHEN 'ling_yu' THEN '工程契约法系，以技术标准和行业规范为主'
           WHEN 'huang_yu' THEN '部落火典法系，以祖先传统和断链权利为基础'
       END,
       CASE d.code
           WHEN 'tian_yu' THEN '{"sovereignty": "绝对统治权", "control": "链籍管控", "enforcement": "强制执行"}'
           WHEN 'ren_yu' THEN '{"autonomy": "乡村自治", "tradition": "传统习俗", "mediation": "调解为主"}'
           WHEN 'ling_yu' THEN '{"standards": "技术标准", "contracts": "契约精神", "peer_review": "同业监督"}'
           WHEN 'huang_yu' THEN '{"ancestral": "祖先法则", "freedom": "断链自由", "tribal": "部落决议"}'
       END,
       75
FROM domains d
WHERE d.novel_id = 1;

-- 为各域创建仪式传统框架
INSERT INTO cultural_frameworks (novel_id, domain_id, dimension_id, framework_name, core_concept, key_features, completeness_score)
SELECT 1,
       d.id,
       (SELECT id FROM cultural_dimensions WHERE code = 'ritual_tradition'),
       d.display_name || '仪式传统框架',
       CASE d.code
           WHEN 'tian_yu' THEN '环约仪式体系，强化统治秩序和等级观念'
           WHEN 'ren_yu' THEN '乡土礼仪传统，维系社区凝聚力和道德规范'
           WHEN 'ling_yu' THEN '师承技艺仪式，传承工艺技能和行业文化'
           WHEN 'huang_yu' THEN '祖灵崇拜仪式，维护部落认同和断链传统'
       END,
       CASE d.code
           WHEN 'tian_yu' THEN '{"hierarchy": "等级强化", "loyalty": "忠诚宣誓", "control": "思想统一"}'
           WHEN 'ren_yu' THEN '{"community": "社区凝聚", "morality": "道德教化", "harmony": "和谐共处"}'
           WHEN 'ling_yu' THEN '{"mastery": "技艺传承", "innovation": "创新鼓励", "excellence": "卓越追求"}'
           WHEN 'huang_yu' THEN '{"ancestors": "祖先敬拜", "freedom": "自由精神", "survival": "生存智慧"}'
       END,
       70
FROM domains d
WHERE d.novel_id = 1;

-- =============================================================================
-- 5. 插入具体的法条仪式等文化要素
-- =============================================================================

-- 5.1 天域法条仪式
INSERT INTO cultural_elements (novel_id, framework_id, element_type, name, code, category, attributes, importance, influence_scope, status, tags)
SELECT 1,
       cf.id,
       'rule',
       '《链籍法》',
       'chain_record_law',
       '基础法律',
       '{"purpose": "维护链籍制度", "scope": "全域适用", "enforcement": "巡链司执行", "penalties": "降籍/黑籍"}',
       10, 'domain', 'active',
       '["法律", "链籍", "统治", "等级"]'
FROM cultural_frameworks cf
JOIN domains d ON cf.domain_id = d.id
JOIN cultural_dimensions cd ON cf.dimension_id = cd.id
WHERE d.code = 'tian_yu' AND cd.code = 'legal_system' AND cf.novel_id = 1;

INSERT INTO cultural_elements (novel_id, framework_id, element_type, name, code, category, attributes, importance, influence_scope, status, tags)
SELECT 1,
       cf.id,
       'ritual',
       '链祭日',
       'chain_sacrifice_day',
       '国家仪式',
       '{"frequency": "年度", "purpose": "强化链籍制度", "participants": "全域民众", "activities": ["链枷示众", "忠诚宣誓", "等级展示"]}',
       9, 'domain', 'active',
       '["仪式", "链籍", "忠诚", "统治"]'
FROM cultural_frameworks cf
JOIN domains d ON cf.domain_id = d.id
JOIN cultural_dimensions cd ON cf.dimension_id = cd.id
WHERE d.code = 'tian_yu' AND cd.code = 'ritual_tradition' AND cf.novel_id = 1;

INSERT INTO cultural_elements (novel_id, framework_id, element_type, name, code, category, attributes, importance, influence_scope, status, tags)
SELECT 1,
       cf.id,
       'practice',
       '新生链测',
       'newborn_chain_test',
       '制度实践',
       '{"frequency": "每个新生儿", "purpose": "确定链籍等级", "officials": "链测祭司", "corruption_risk": "高"}',
       8, 'domain', 'active',
       '["测试", "链籍", "等级", "腐败"]'
FROM cultural_frameworks cf
JOIN domains d ON cf.domain_id = d.id
JOIN cultural_dimensions cd ON cf.dimension_id = cd.id
WHERE d.code = 'tian_yu' AND cd.code = 'ritual_tradition' AND cf.novel_id = 1;

INSERT INTO cultural_elements (novel_id, framework_id, element_type, name, code, category, attributes, importance, influence_scope, status, tags)
SELECT 1,
       cf.id,
       'practice',
       '环约巡誓',
       'covenant_patrol_oath',
       '执法仪式',
       '{"frequency": "定期", "purpose": "执法宣誓", "participants": "巡链官", "symbolism": "权威展示"}',
       7, 'regional', 'active',
       '["执法", "宣誓", "权威", "巡查"]'
FROM cultural_frameworks cf
JOIN domains d ON cf.domain_id = d.id
JOIN cultural_dimensions cd ON cf.dimension_id = cd.id
WHERE d.code = 'tian_yu' AND cd.code = 'ritual_tradition' AND cf.novel_id = 1;

-- 5.2 灵域法条仪式
INSERT INTO cultural_elements (novel_id, framework_id, element_type, name, code, category, attributes, importance, influence_scope, status, tags)
SELECT 1,
       cf.id,
       'rule',
       '《环印律》',
       'circle_seal_law',
       '技术法规',
       '{"purpose": "规范评印标准", "scope": "技术认证", "enforcement": "评印院", "standards": "技术准则"}',
       9, 'domain', 'active',
       '["法规", "技术", "标准", "认证"]'
FROM cultural_frameworks cf
JOIN domains d ON cf.domain_id = d.id
JOIN cultural_dimensions cd ON cf.dimension_id = cd.id
WHERE d.code = 'ling_yu' AND cd.code = 'legal_system' AND cf.novel_id = 1;

INSERT INTO cultural_elements (novel_id, framework_id, element_type, name, code, category, attributes, importance, influence_scope, status, tags)
SELECT 1,
       cf.id,
       'rule',
       '《工程链契》',
       'engineering_chain_contract',
       '契约法规',
       '{"purpose": "规范工程承包", "scope": "大型项目", "enforcement": "链算所", "disputes": "技术仲裁"}',
       8, 'domain', 'active',
       '["契约", "工程", "承包", "仲裁"]'
FROM cultural_frameworks cf
JOIN domains d ON cf.domain_id = d.id
JOIN cultural_dimensions cd ON cf.dimension_id = cd.id
WHERE d.code = 'ling_yu' AND cd.code = 'legal_system' AND cf.novel_id = 1;

INSERT INTO cultural_elements (novel_id, framework_id, element_type, name, code, category, attributes, importance, influence_scope, status, tags)
SELECT 1,
       cf.id,
       'ritual',
       '万器朝链',
       'myriad_tools_bow_to_chain',
       '行业庆典',
       '{"frequency": "年度", "purpose": "展示技术成就", "participants": "各宗门工匠", "activities": ["技术展示", "评印大会", "创新评选"]}',
       8, 'domain', 'active',
       '["庆典", "技术", "展示", "评选"]'
FROM cultural_frameworks cf
JOIN domains d ON cf.domain_id = d.id
JOIN cultural_dimensions cd ON cf.dimension_id = cd.id
WHERE d.code = 'ling_yu' AND cd.code = 'ritual_tradition' AND cf.novel_id = 1;

INSERT INTO cultural_elements (novel_id, framework_id, element_type, name, code, category, attributes, importance, influence_scope, status, tags)
SELECT 1,
       cf.id,
       'ritual',
       '师承刻环礼',
       'master_apprentice_ring_ceremony',
       '传承仪式',
       '{"frequency": "学徒入门", "purpose": "确立师徒关系", "participants": "宗匠和学徒", "symbolism": "技艺传承"}',
       7, 'local', 'active',
       '["传承", "师徒", "仪式", "技艺"]'
FROM cultural_frameworks cf
JOIN domains d ON cf.domain_id = d.id
JOIN cultural_dimensions cd ON cf.dimension_id = cd.id
WHERE d.code = 'ling_yu' AND cd.code = 'ritual_tradition' AND cf.novel_id = 1;

-- 5.3 人域法条仪式
INSERT INTO cultural_elements (novel_id, framework_id, element_type, name, code, category, attributes, importance, influence_scope, status, tags)
SELECT 1,
       cf.id,
       'rule',
       '《工坊用工契》',
       'workshop_labor_contract',
       '劳动法规',
       '{"purpose": "规范用工关系", "scope": "工坊代工", "protection": "学徒权益", "disputes": "乡绅调解"}',
       6, 'regional', 'active',
       '["劳动", "契约", "权益", "调解"]'
FROM cultural_frameworks cf
JOIN domains d ON cf.domain_id = d.id
JOIN cultural_dimensions cd ON cf.dimension_id = cd.id
WHERE d.code = 'ren_yu' AND cd.code = 'legal_system' AND cf.novel_id = 1;

INSERT INTO cultural_elements (novel_id, framework_id, element_type, name, code, category, attributes, importance, influence_scope, status, tags)
SELECT 1,
       cf.id,
       'rule',
       '《互市环约》',
       'mutual_market_covenant',
       '贸易法规',
       '{"purpose": "规范边境贸易", "scope": "边市交易", "taxation": "关税规定", "disputes": "商会调解"}',
       7, 'regional', 'active',
       '["贸易", "边境", "税收", "商会"]'
FROM cultural_frameworks cf
JOIN domains d ON cf.domain_id = d.id
JOIN cultural_dimensions cd ON cf.dimension_id = cd.id
WHERE d.code = 'ren_yu' AND cd.code = 'legal_system' AND cf.novel_id = 1;

-- 5.4 荒域法条仪式
INSERT INTO cultural_elements (novel_id, framework_id, element_type, name, code, category, attributes, importance, influence_scope, status, tags)
SELECT 1,
       cf.id,
       'rule',
       '《边域缚约》',
       'borderland_binding_covenant',
       '边境法规',
       '{"purpose": "规范边境管制", "scope": "边境地区", "enforcement": "军镇", "conflicts": "与部落传统冲突"}',
       7, 'regional', 'active',
       '["边境", "管制", "军事", "冲突"]'
FROM cultural_frameworks cf
JOIN domains d ON cf.domain_id = d.id
JOIN cultural_dimensions cd ON cf.dimension_id = cd.id
WHERE d.code = 'huang_yu' AND cd.code = 'legal_system' AND cf.novel_id = 1;

INSERT INTO cultural_elements (novel_id, framework_id, element_type, name, code, category, attributes, importance, influence_scope, status, tags)
SELECT 1,
       cf.id,
       'rule',
       '《危械禁令》',
       'dangerous_device_prohibition',
       '安全法规',
       '{"purpose": "禁止危险器械", "scope": "跨域执行", "enforcement": "评印院", "exemptions": "军用许可"}',
       8, 'cross_domain', 'active',
       '["安全", "禁令", "器械", "许可"]'
FROM cultural_frameworks cf
JOIN domains d ON cf.domain_id = d.id
JOIN cultural_dimensions cd ON cf.dimension_id = cd.id
WHERE d.code = 'huang_yu' AND cd.code = 'legal_system' AND cf.novel_id = 1;

INSERT INTO cultural_elements (novel_id, framework_id, element_type, name, code, category, attributes, importance, influence_scope, status, tags)
SELECT 1,
       cf.id,
       'ritual',
       '裂世夜',
       'world_rending_night',
       '部落庆典',
       '{"frequency": "不定期", "purpose": "庆祝断链自由", "participants": "部落勇士", "activities": ["祖灵火祭", "断链仪式", "部落聚会"], "threat_level": "被天域视为危险"}',
       9, 'domain', 'threatened',
       '["庆典", "断链", "自由", "祖灵"]'
FROM cultural_frameworks cf
JOIN domains d ON cf.domain_id = d.id
JOIN cultural_dimensions cd ON cf.dimension_id = cd.id
WHERE d.code = 'huang_yu' AND cd.code = 'ritual_tradition' AND cf.novel_id = 1;

INSERT INTO cultural_elements (novel_id, framework_id, element_type, name, code, category, attributes, importance, influence_scope, status, tags)
SELECT 1,
       cf.id,
       'practice',
       '火灰印通关',
       'fire_ash_seal_passage',
       '通行制度',
       '{"purpose": "边境通行认证", "issuer": "部落祭司", "scope": "边境贸易", "security": "防伪标识"}',
       6, 'regional', 'active',
       '["通行", "认证", "贸易", "防伪"]'
FROM cultural_frameworks cf
JOIN domains d ON cf.domain_id = d.id
JOIN cultural_dimensions cd ON cf.dimension_id = cd.id
WHERE d.code = 'huang_yu' AND cd.code = 'ritual_tradition' AND cf.novel_id = 1;

-- =============================================================================
-- 6. 数据完整性检查和统计信息
-- =============================================================================

-- 更新域的框架数量统计（如果有相关字段）
-- UPDATE domains SET framework_count = (
--     SELECT COUNT(*) FROM cultural_frameworks WHERE domain_id = domains.id
-- ) WHERE novel_id = 1;

-- =============================================================================
-- 7. 查询示例和使用指南
-- =============================================================================

/*
-- 查询跨域冲突矩阵热度总览
SELECT
    d1.name AS primary_domain,
    d2.name AS secondary_domain,
    cc.conflict_type,
    cc.intensity_level,
    cc.status,
    cc.current_manifestation
FROM cultural_conflicts cc
JOIN domains d1 ON cc.primary_domain_id = d1.id
JOIN domains d2 ON cc.secondary_domain_id = d2.id
WHERE cc.novel_id = 1
ORDER BY cc.intensity_level DESC, d1.sort_order, d2.sort_order;

-- 查询特定域的所有剧情钩子
SELECT
    ph.title,
    ph.description,
    ph.hook_type,
    ph.drama_level,
    ph.scope,
    ph.status,
    d.name AS domain_name
FROM plot_hooks ph
LEFT JOIN domains d ON ph.domain_id = d.id
WHERE ph.novel_id = 1 AND d.code = 'tian_yu'
ORDER BY ph.drama_level DESC;

-- 查询域的文化要素概览
SELECT
    d.name AS domain_name,
    cd.name AS dimension_name,
    cf.framework_name,
    ce.element_type,
    ce.name AS element_name,
    ce.importance,
    ce.status
FROM cultural_elements ce
JOIN cultural_frameworks cf ON ce.framework_id = cf.id
JOIN domains d ON cf.domain_id = d.id
JOIN cultural_dimensions cd ON cf.dimension_id = cd.id
WHERE ce.novel_id = 1
ORDER BY d.sort_order, cd.sort_order, ce.importance DESC;

-- 查询冲突相关的剧情钩子
SELECT
    cc.conflict_name,
    cc.intensity_level,
    ph.title AS hook_title,
    ph.drama_level,
    ph.urgency_level,
    ph.status
FROM cultural_conflicts cc
LEFT JOIN plot_hooks ph ON (
    ph.domain_id = cc.primary_domain_id OR
    ph.domain_id = cc.secondary_domain_id
)
WHERE cc.novel_id = 1
ORDER BY cc.intensity_level DESC, ph.drama_level DESC;

-- 查询特定类型的文化要素（如法律）
SELECT
    d.name AS domain_name,
    ce.name AS element_name,
    ce.element_type,
    ce.category,
    ce.importance,
    ce.influence_scope,
    ce.attributes->>'purpose' AS purpose
FROM cultural_elements ce
JOIN cultural_frameworks cf ON ce.framework_id = cf.id
JOIN domains d ON cf.domain_id = d.id
JOIN cultural_dimensions cd ON cf.dimension_id = cd.id
WHERE ce.novel_id = 1 AND cd.code = 'legal_system'
ORDER BY d.sort_order, ce.importance DESC;
*/

-- =============================================================================
-- 8. 脚本总结
-- =============================================================================

/*
跨域冲突矩阵初始化完成总结：

✅ 已创建内容：
1. 四个域基础信息（人域、天域、灵域、荒域）
2. 六组跨域冲突详细信息：
   - 天域 ↔ 人域（高强度）
   - 天域 ↔ 灵域（中高强度）
   - 天域 ↔ 荒域（高强度）
   - 人域 ↔ 灵域（中强度）
   - 人域 ↔ 荒域（中高强度）
   - 灵域 ↔ 荒域（中高强度）
3. 12个剧情钩子（每组冲突2个）
4. 2个文化维度（法律制度、仪式传统）
5. 8个文化框架（每域2个框架）
6. 15个文化要素（法条、仪式、实践）

📊 数据统计：
- 域数量：4个
- 冲突记录：6条
- 剧情钩子：12个
- 文化框架：8个
- 文化要素：15个

🎯 涵盖的冲突类型：
- 权力冲突（天域主导）
- 资源争夺（边境贸易）
- 技术标准争议
- 劳工关系纠纷
- 文化价值冲突

🔗 系统特性：
- 支持跨域冲突分析
- 剧情钩子自动关联
- 文化要素结构化存储
- 完整的审计追踪
- 丰富的查询视图

使用时请注意：
1. 修改 novel_id 为实际的小说项目ID
2. 可根据实际需要调整冲突强度和重要性评分
3. 剧情钩子可根据故事发展动态更新状态
4. 文化要素支持扩展和细化
*/
