const renyu_character_12: Character = {
  id: "char-renyu-lusan-012",
  projectId: "proj-liashi-jiuyu",
  createdAt: new Date("2025-09-17T00:00:00Z"),
  updatedAt: new Date("2025-09-17T00:00:00Z"),

  // 基本信息
  basicInfo: {
    name: "鲁三",
    alias: ["舵狼", "断浪手"],
    age: 33,
    gender: "male",
    occupation: "护运队长（九埠市商队·河陆联运）",
    socialStatus: "良籍·行会雇员（高级随从编）"
  },

  // 外貌特征
  appearance: {
    height: "178cm",
    weight: "76kg",
    hairColor: "乌黑短发",
    eyeColor: "深褐",
    skinTone: "古铜",
    bodyType: "结实·耐力型",
    specialMarks: ["左肩有舟阵纹身（护运识别）", "右眉尾一道细小刀痕", "掌心厚茧"],
    clothingStyle: "短甲外披防水斗篷，腰挂骨弩与折叠舟钩，脚穿防滑钉靴"
  },

  // 性格特质
  personality: {
    coreTraits: ["果断", "忠诚", "务实", "守信"],
    values: ["队伍安全", "信誉", "规则简明可执行"],
    beliefs: ["没有不可能的路，只有没准备的队"],
    fears: ["队员伤亡", "被迫背锅"],
    desires: ["把护运队打造成跨域一流样板", "攒钱给母亲在城里置小院"],
    weaknesses: ["对风险直觉型，书面条款耐心不足", "情绪上头时不愿撤退"],
    strengths: ["临场指挥", "水陆协同", "武器使用与阵位布置"]
  },

  // 背景故事
  background: {
    birthplace: "九埠市下游渔村（人域）",
    family: "寡母在，独子；幼时随舅在河上讨生活",
    childhood: "少年掌舵，习得观风看水；曾为保安行脚，后转护运",
    education: "行会武训+薛箴亲授‘三案’路书；识字能读路书与舱单",
    importantEvents: [
      "18岁：暴雨夜断缆，独力借流救下一船人，入护运队",
      "24岁：升队副，提出‘舟陆交替护圈’降低劫路风险",
      "28岁：汛季率队在边关解围，保护人质换取放行",
      "32岁：与赵槐夜路对峙，以中立仓见证化险为夷"
    ],
    trauma: ["童年亲眼见到一艘小船翻覆，父亲溺亡", "一次护运误判导致车队侧翻，造成轻伤三人"],
    achievements: ["优化‘舟陆护圈’流程卡", "建立‘三信号’（灯、旗、哨）统一口令"]
  },

  // 能力技能
  abilities: {
    professionalSkills: ["队列编组与护圈布置", "河路换乘与时窗把握", "危机撤离与人质谈判", "武器与器具维护"],
    specialTalents: ["听浪辨浅（夜间靠声波与回响判断水深）", "阵位直觉（看到地形能迅速定护圈站位）"],
    languages: ["通域语", "人域乡言", "天域官音（应付）", "荒域部落言（基础口令）"],
    learningAbility: "场景化学习，擅把经验固化为‘一句口令+一个动作’",
    socialSkills: "对内强势凝聚，对外以结果换信任",
    practicalSkills: ["舟阵·护航", "弩术/短刀", "止血包扎/夹板固定", "简易绞盘修复"]
  },

  // 人际关系
  relationships: {
    family: [
      { name: "鲁母", relationship: "母子", description: "寡母体弱，盼其早安定成家", importance: "high" }
    ],
    friends: [
      { name: "薛箴", relationship: "把兄弟/上司", description: "互信深，执行其路书‘三案’", importance: "high" }
    ],
    lovers: [],
    enemies: [
      { name: "黑钩", relationship: "宿敌", description: "荒域出没的劫路头，擅夜间登舟", importance: "high" }
    ],
    mentors: [
      { name: "老舵公（未名）", relationship: "启蒙", description: "教其借流与观风", importance: "medium" }
    ],
    subordinates: [
      { name: "护运一队", relationship: "队长-队员", description: "十二人编组，熟悉灯旗哨三信号", importance: "high" }
    ],
    socialCircle: ["行会护运圈", "码头牙人", "边关中立仓守仓人", "乡祠急救志愿队"]
  },

  // 生活状况
  lifestyle: {
    residence: "九埠市会馆后院铺位（常年在路上）",
    economicStatus: "稳中偏紧（把钱寄回家）",
    dailyRoutine: "黎明训练→核对路书与气象→执行护运→夜间复盘并保养器具",
    hobbies: ["打磨舟钩", "收集各地水纹石", "记‘风骨图’边注"],
    foodPreferences: ["高盐耐储", "鱼干", "热汤"],
    entertainment: ["码头对歌", "与队员掷石锁比赛"]
  },

  // 心理状态 (增强版)
  psychology: {
    mentalHealth: "高压高功能，靠规律训练维持；对水患有隐性触发",
    mentalHealthStatus: "good",
    copingMechanisms: [
      { type: "healthy", strategy: "动作化复盘（站位-口令-撤退）", triggers: ["行动失败","伤员"], effectiveness: 9, frequency: "frequent" },
      { type: "adaptive", strategy: "自嘲+队内小仪式缓和气氛", triggers: ["连续夜行","封关"], effectiveness: 6, frequency: "occasional" }
    ],
    emotionalPatterns: [
      { emotion: "警觉", triggers: ["风向突变","灯号异常"], intensity: 7, duration: "brief", expression: "立刻下令换阵", impact: "避免事故" }
    ],
    trauma: [
      { type: "childhood", event: "父亲溺亡", age: 9, severity: "severe", status: "integrated", triggers: ["浪头拍岸声","冷涌"], effects: ["心跳加速","短时屏息"], copingMethods: ["口令自稳‘吸一吐二’","确认退路"] }
    ],
    growthNeeds: ["制度化的人命优先条款", "与官署/荒域部落的通用口令备忘"],
    cognitivePatterns: [
      { type: "belief", description: "撤退是胜利的一种", situations: ["遭遇劫路","自然灾害"], impact: "positive", awareness: "conscious" },
      { type: "bias", description: "过度依赖直觉", situations: ["谈判","复杂条款"], impact: "mixed", awareness: "conscious" }
    ],
    stressResponses: [
      {
        stressor: "封关叠加暴雨",
        physicalResponse: ["肩颈硬", "手腕酸痛"],
        emotionalResponse: ["烦躁", "专注过度"],
        behavioralResponse: ["加密口令频率", "缩紧护圈"],
        cognitiveResponse: ["对外沟通减少，偏重行动"],
        timeframe: "整段任务期"
      }
    ],
    emotionalIntelligence: {
      selfAwareness: 6, selfRegulation: 7, motivation: 8, empathy: 6, socialSkills: 7,
      strengths: ["稳住队伍情绪"], weaknesses: ["表达粗粝，易被误解为强硬"]
    },
    psychologicalDefenses: ["理智化", "幽默化"],
    mentalHealthHistory: [
      { date: new Date("2025-06-01"), status: "good", notes: "完成连续两次危险护运零伤亡" }
    ]
  },

  // 故事功能
  storyRole: {
    characterType: "supporting",
    characterArc: "硬核护运者 → 人命优先倡议者 →（可选）护法队教官",
    conflictRole: "跨域行动的人身安全与撤退权守门人",
    symbolism: "舟钩=不放弃任何一个人；三信号=秩序与默契",
    readerConnection: "靠谱、能托付后背的专业人士"
  },

  // 特殊设定 (增强版)
  specialSettings: {
    worldBuilding: "裂世九域·法则链纪元",
    culturalBackground: "人域-行会护运文化（与码头/边关/中立仓耦合）",
    historicalContext: "裂世后时代",
    technologyLevel: "链工学-中",
    magicAbilities:
      "法则链：主[水] 副[土]；契合度:3；禁忌:[以命换行（强行夜航超限）]；代表术式:[水势·借流(借势过险滩), 护圈·定位(以土链稳阵脚), 潮声·预警(微震提前量)]；代价: 关节寒痛、暴雨夜听觉过敏与短时眩晕",
    culturalIdentity: {
      primaryCulture: "人域-行会护运文化",
      subcultures: ["码头班头圈","中立仓守仓人网络"],
      culturalValues: ["纪律","信誉","人命优先"],
      culturalConflicts: ["与官署强制押解冲突", "与黑市抢货文化冲突"],
      assimilationLevel: 7,
      culturalPride: 7,
      traditionalPractices: ["开航前‘摸水礼’", "收队后‘点名杯’"],
      modernAdaptations: ["三信号统一口令卡", "撤退权条款写入合同（试点）"]
    },
    religiousBeliefs: {
      religion: "源祖/河神混合信仰（务实派）",
      denomination: "码头河祠",
      devotionLevel: 4,
      practices: ["出航滴水礼", "祭亡名册"],
      beliefs: ["水性无常，敬畏方得全身而退"],
      doubts: ["祭司对现实航路的指导有限"],
      spiritualExperiences: ["暴雨夜似闻‘回水’之声，提前转向避险"],
      religionInLife: "minimal"
    },
    languageProfile: {
      nativeLanguage: "通域语",
      fluentLanguages: ["人域乡言","天域官音（应付）","荒域部落言（基础口令）"],
      learningLanguages: [],
      accents: ["码头快语+口令腔"],
      dialectVariations: [],
      speechPatterns: [
        { characteristic: "口令化三段句", examples: ["收圈—让路—换位", "二号位上风", "撤！"], frequency: "often", context: ["执行","危机处置"], origin: "护运训练" }
      ],
      languageBarriers: ["冗长礼仪腔不耐"],
      communicationPreferences: ["短句+手势+灯旗哨"]
    },
    behaviorPatterns: [
      { category: "professional", behavior: "每次出发做‘三信号’演练", frequency: "daily", triggers: ["出航/出车前"], context: ["码头/出城口"], development: "反应时间缩短20%" },
      { category: "personal", behavior: "回城必写路书边注", frequency: "situational", triggers: ["重大事件后"], context: ["会馆"], development: "经验沉淀为流程卡" }
    ],
    rolePlayingNotes: [
      "Domain: 人域",
      "KeyLocations: 九埠市 / 中立仓 / 边关渡口 / 三环亭",
      "F*: F3/F7/F12/F18/F19/F20",
      "口头禅: '人先货后' '看风，不要硬扛'"
    ]
  },

  // 角色成长轨迹 (新增)
  characterArc: {
    currentStage: "③ 试炼与盟友（护运中枢）→ ④ 深渊（人质/劫路危机）",
    developmentGoals: [
      {
        id: "ls-g1",
        category: "professional",
        goal: "把‘撤退权条款’写入三方合同并获备案",
        motivation: "减少无谓牺牲",
        timeline: "两个月",
        obstacles: ["官署绩效倾向强硬","票行成本考量","黑市干扰"],
        progress: 40,
        priority: "high"
      }
    ],
    growthMilestones: [
      {
        id: "ls-m1",
        title: "零伤亡强撤一次",
        description: "在风暴夜以‘水势·借流’带队退至中立仓避险",
        significance: "确立‘撤退也是胜利’",
        prerequisites: ["中立仓预案","三信号操练熟"],
        relatedGoals: ["ls-g1"],
        status: "planned"
      }
    ],
    personalityChanges: [
      {
        id: "ls-p1",
        trait: "撤退观",
        oldValue: "硬顶为荣",
        newValue: "人命优先、可撤即撤",
        trigger: "队友险情与母亲落泪相劝",
        timeline: "一月",
        significance: "major",
        stability: "developing"
      }
    ],
    skillProgression: [
      {
        skill: "护圈·定位",
        category: "physical",
        currentLevel: 6,
        targetLevel: 8,
        learningMethod: "地形沙盘+夜训",
        timeframe: "两月",
        obstacles: ["队员疲劳","装备耗损"],
        mentors: ["薛箴"]
      }
    ],
    relationshipEvolution: [
      {
        relationshipId: "rel-zhaohuai-opp",
        personName: "赵槐",
        evolutionType: "changing",
        previousState: "对峙",
        currentState: "有限协作（第三方见证下）",
        triggers: ["一次跨域押解与护运错峰协同"],
        timeline: "短期",
        significance: "降低冲突成本"
      }
    ],
    internalConflicts: [
      {
        id: "ls-ic1",
        title: "职责 vs. 家庭",
        description: "继续冒险带队与照顾母亲的矛盾",
        conflictingValues: ["荣誉","亲情"],
        emotionalImpact: "失眠与自责",
        manifestations: ["加训以求万全","推迟相亲"],
        resolutionAttempts: ["培养副队", "限定出勤周期"],
        status: "active"
      }
    ],
    externalChallenges: [
      {
        id: "ls-ec1",
        title: "劫路与封关双重压力",
        description: "黑市抬价诱劫，官署限时放行催逼",
        source: "society",
        difficulty: 8,
        timeframe: "汛季",
        resources: ["中立仓预案","撤退权条款","三信号"],
        strategies: ["错峰出行","公开路书边注供见证","与乡祠急救联动"],
        status: "upcoming"
      }
    ]
  },

  // 互动行为模式 (新增)
  behaviorProfile: {
    communicationStyle: {
      primaryStyle: "direct",
      verbalCharacteristics: ["口令短句", "结论先行"],
      nonverbalCharacteristics: ["手势明确", "哨声定节"],
      listeningStyle: "active",
      feedbackStyle: "事后复盘三点式（做得好/需改/下次）",
      conflictCommunication: "请见证→划定安全线→再谈",
      culturalInfluences: ["行会护运文化","码头口令传统"]
    },
    bodyLanguage: {
      posture: "站位略前、重心稳",
      gestures: ["掌心向下压稳", "两指并拢指位"],
      facialExpressions: ["专注", "偶露狠劲"],
      eyeContact: "moderate",
      personalSpace: "normal",
      nervousHabits: ["抚舟钩柄", "舌抵上颚短促呼吸"],
      confidenceIndicators: ["步伐有节奏", "哨声清晰"],
      culturalVariations: ["对老人/祠司行简礼，对官差保持职业距离"]
    },
    decisionMaking: {
      approach: "analytical",
      timeframe: "quick",
      informationGathering: "风向+水位+地形+队伍状态四象",
      riskTolerance: 5,
      influences: ["人命优先","路书‘三案’"],
      biases: ["直觉偏好"],
      decisionHistory: ["两次成功强撤","一次错判导致小伤"]
    },
    conflictResponse: {
      primaryStyle: "collaborating",
      escalationTriggers: ["人身威胁","撕毁合同"],
      deescalationMethods: ["中立仓托管","人货分离"],
      emotionalReactions: ["短怒后迅速冷静"],
      physicalReactions: ["肩颈绷紧"],
      recoveryMethods: ["热姜汤", "夜跑"],
      conflictHistory: ["多起冲突转为有序撤退"]
    },
    socialBehavior: {
      socialEnergy: "ambivert",
      groupDynamics: "队内核心，能在混乱中分派角色",
      socialRoles: ["指挥者","救援者"],
      boundaryManagement: "公私分明（队规先行）",
      socialAnxieties: ["公众场合长谈判辞"],
      socialStrengths: ["建立信任","稳定情绪"],
      networkingStyle: "行会-中立仓-乡祠三角",
      socialAdaptability: 8
    },
    workStyle: {
      productivity: "morning",
      environment: "bustling",
      organization: "highly_organized",
      taskManagement: "行动清单+站位图",
      collaboration: "小队自治+队长拍板",
      innovation: "把经验做成口令卡",
      stressManagement: "体能训练+热汤+复盘"
    },
    leadershipStyle: {
      type: "transformational",
      strengths: ["以身作则","激励与赋能"],
      weaknesses: ["对文书流程不耐","偶有逞强"],
      motivationMethods: ["荣誉记名+休整日", "家属慰问"],
      delegationStyle: "按特长分配（弩/盾/医）",
      feedbackApproach: "战后复盘+个别谈话",
      decisionInclusivity: "中",
      crisisManagement: "人命优先、可撤即撤"
    },
    learningStyle: {
      primary: "kinesthetic",
      preferences: ["沙盘演练","夜训实操"],
      strengths: ["动作记忆强","高压下执行"],
      challenges: ["长篇条款"],
      motivationFactors: ["队友性命","母亲嘱托"],
      retentionMethods: ["口令卡","站位图"],
      environments: ["码头","边关","会馆操场"],
      adaptability: 8
    }
  }
};
