const renyu_character_09: Character = {
  id: "char-renyu-shenwan-009",
  projectId: "proj-liashi-jiuyu",
  createdAt: new Date("2025-09-17T00:00:00Z"),
  updatedAt: new Date("2025-09-17T00:00:00Z"),

  // 基本信息
  basicInfo: {
    name: "沈纨",
    alias: ["内账娘子", "冷算盘"],
    age: 35,
    gender: "female",
    occupation: "链票行内账主管（九埠市）",
    socialStatus: "良籍·行会会员"
  },

  // 外貌特征
  appearance: {
    height: "165cm",
    weight: "50kg",
    hairColor: "乌黑（绾低髻）",
    eyeColor: "深褐",
    skinTone: "偏白",
    bodyType: "纤长·耐坐型",
    specialMarks: ["左手无名指有细薄护环（算环）", "右太阳穴常年轻微青筋"],
    clothingStyle: "素色长衫+窄袖，腰佩小铜算与密钥筒，袖内薄皮指套"
  },

  // 性格特质
  personality: {
    coreTraits: ["冷静", "克制", "精准", "守序但有底线"],
    values: ["账目真实", "家庭安稳", "可追溯的流程"],
    beliefs: ["数字不会说谎，但会被安排", "透明是最好的保险"],
    fears: ["挤兑失控殃及无辜", "丈夫因灰度操作被问罪"],
    desires: ["建立可审计的内控体系", "让票行拿到正规牌照"],
    weaknesses: ["情感表达节制", "对冒险改革犹疑"],
    strengths: ["复式账审计", "异常模式识别", "冷场中迅速定调"]
  },

  // 背景故事
  background: {
    birthplace: "九埠市（水巷）",
    family: "与何舫为伉俪，一子何佑在御书镇读书",
    childhood: "生于小票庄书案后，幼年随父母记账，天生数字感强",
    education: "行会账房带教+天域链算所短训‘内控与审计’一季",
    importantEvents: [
      "18岁：接手小票庄内账，止住一次小型挤兑",
      "25岁：嫁何舫，重整票行账簿与备付池结构",
      "32岁：发现‘空白链契’风险，提出三道关卡遭搁置",
      "36岁：旱情做空事件后，秘建“镜账”留证防反噬"
    ],
    trauma: ["少年目击焚柜与挤兑造成伤亡", "旱情做空后被围堵险遭伤害"],
    achievements: ["设计舱单-仓单-备付三表联动", "导入‘镜账·对照’周度盘点程序"]
  },

  // 能力技能
  abilities: {
    professionalSkills: ["复式账/审计", "内控设计", "风险预警模型", "资金日流监控"],
    specialTalents: ["数字模式嗅觉（异常联想能力）", "冷场定调（三句归纳现状/风险/对策）"],
    languages: ["通域语", "人域乡言", "天域官音"],
    learningAbility: "抽象-实践结合，能把规则固化为表格与流程卡",
    socialSkills: "场面话少但有效；能让强势人物坐回桌边看数据",
    practicalSkills: ["镜账·对照（账证影像化）", "链息·止损（临时冻结资金路径）", "应急备付调拨"]
  },

  // 人际关系
  relationships: {
    family: [
      { name: "何舫", relationship: "夫妻", description: "票行账吏长/股东，理念互补亦相冲", importance: "high" },
      { name: "何佑", relationship: "母子", description: "御书镇读书，体弱文静", importance: "high" }
    ],
    friends: [
      { name: "白简", relationship: "前辈", description: "行会老账房，理念‘半账留余’影响其早期方法", importance: "medium" }
    ],
    lovers: [],
    enemies: [
      { name: "沈合", relationship: "职业对立", description: "柳链集头工，排斥透明合同与工账", importance: "medium" }
    ],
    mentors: [
      { name: "链算所讲习导师（未名）", relationship: "导师", description: "教其建立‘三表联动’", importance: "medium" }
    ],
    subordinates: [
      { name: "内账小组", relationship: "组长-组员", description: "三人小队，负责镜账与备付核对", importance: "high" }
    ],
    socialCircle: ["行会内账圈", "链算所旧同学", "书场报馆记者（弱联系）"]
  },

  // 生活状况
  lifestyle: {
    residence: "九埠市水巷票行楼上私宅（与丈夫同住）",
    economicStatus: "稳健富足（偏保守理财）",
    dailyRoutine: "卯时汇总三表→辰时内控例会→午后抽查镜账→傍晚更新风险清单→夜间与何舫复盘",
    hobbies: ["装帧账本", "收集各地算环", "抄写对照表"],
    foodPreferences: ["清粥小菜", "素面", "温茶"],
    entertainment: ["偶听书场‘商战公案’", "与学子交流算术题"]
  },

  // 心理状态 (增强版)
  psychology: {
    mentalHealth: "高功能+高紧张；对‘不确定性’高度敏感",
    mentalHealthStatus: "good",
    copingMechanisms: [
      { type: "healthy", strategy: "把风险拆成清单与时窗", triggers: ["封关","抢兑"], effectiveness: 9, frequency: "frequent" },
      { type: "adaptive", strategy: "情感抽离只谈数据", triggers: ["夫妻理念冲突"], effectiveness: 6, frequency: "occasional" }
    ],
    emotionalPatterns: [
      { emotion: "焦虑", triggers: ["备付低于阈值","市场剧震"], intensity: 6, duration: "moderate", expression: "语速更慢、句子更短", impact: "压住情绪但耗能高" }
    ],
    trauma: [
      { type: "adolescent", event: "挤兑与焚柜", age: 15, severity: "severe", status: "healing", triggers: ["鼓噪","纸灰气味"], effects: ["手心出汗","短时头痛"], copingMethods: ["深呼吸五息法","转移到数据操作"] }
    ],
    growthNeeds: ["官方合规牌照与第三方清算", "外部独立审计背书"],
    cognitivePatterns: [
      { type: "belief", description: "透明可降低暴力成本", situations: ["谈判","危机沟通"], impact: "positive", awareness: "conscious" },
      { type: "bias", description: "数据优先于人情", situations: ["家庭/工作取舍"], impact: "mixed", awareness: "conscious" }
    ],
    stressResponses: [
      {
        stressor: "封关叠加抢兑与舆情",
        physicalResponse: ["太阳穴跳痛","轻微心悸"],
        emotionalResponse: ["焦虑","压抑"],
        behavioralResponse: ["冻结非核心支出","加强抽查频率"],
        cognitiveResponse: ["过度演练最坏情形"],
        timeframe: "事件全程"
      }
    ],
    emotionalIntelligence: {
      selfAwareness: 7, selfRegulation: 7, motivation: 8, empathy: 5, socialSkills: 7,
      strengths: ["在混乱中建立秩序"], weaknesses: ["情感沟通不足"]
    },
    psychologicalDefenses: ["理智化", "分隔化"],
    mentalHealthHistory: [
      { date: new Date("2024-11-01"), status: "good", notes: "完成一次周度镜账对冲，安全度提升" }
    ]
  },

  // 故事功能
  storyRole: {
    characterType: "supporting",
    characterArc: "守序内账 → 夹层制衡者 → 吹哨与改革推手",
    conflictRole: "票行内部制衡/关键账证持有人",
    symbolism: "算环=约束与护身；镜账=真相镜像",
    readerConnection: "冷静可靠、在亲密与原则间艰难取舍的人"
  },

  // 特殊设定 (增强版)
  specialSettings: {
    worldBuilding: "裂世九域·法则链纪元",
    culturalBackground: "人域-行会/票行文化（与官署与码头双向耦合）",
    historicalContext: "裂世后时代",
    technologyLevel: "链工学-中",
    magicAbilities:
      "法则链：主[金] 副[因果]；契合度:3；禁忌:[双簿制隐匿, 以债锁人（囚票）]；代表术式:[镜账·对照(账证影像化追溯), 链息·止损(临时冻结资金链), 底账·回放(还原资金轨迹)]；代价: 长时演算致偏头痛与短暂数字色弱；过用后出现情感冷却",
    culturalIdentity: {
      primaryCulture: "人域-行会文化",
      subcultures: ["链算所学统", "水巷票庄圈"],
      culturalValues: ["信誉","透明","风险对冲"],
      culturalConflicts: ["与官署‘流程优先’冲突", "与黑市‘无契约’冲突"],
      assimilationLevel: 8,
      culturalPride: 7,
      traditionalPractices: ["开柜祭账", "年终对照帐拜仪"],
      modernAdaptations: ["镜账制度化", "三表联动看板"]
    },
    religiousBeliefs: {
      religion: "天命信仰（实用派）",
      denomination: "行会祠",
      devotionLevel: 3,
      practices: ["开柜小礼"],
      beliefs: ["秩序来源于清算"],
      doubts: ["祭司干预市场的效率"],
      spiritualExperiences: ["一次夜盘对账似闻‘数声’指向错项而避险"],
      religionInLife: "minimal"
    },
    languageProfile: {
      nativeLanguage: "通域语",
      fluentLanguages: ["人域乡言","天域官音"],
      learningLanguages: [],
      accents: ["票柜腔（数字密度高、句短）"],
      dialectVariations: [],
      speechPatterns: [
        { characteristic: "三句定调", examples: ["现状一句", "风险一句", "对策一句"], frequency: "often", context: ["危机沟通","内会"], origin: "内控训练" }
      ],
      languageBarriers: ["冗长礼仪腔不耐"],
      communicationPreferences: ["白板+数据", "书面纪要为准"]
    },
    behaviorPatterns: [
      { category: "professional", behavior: "周度镜账抽查（随机+风险加权）", frequency: "weekly", triggers: ["资金异常","舆情上升"], context: ["账房"], development: "降低舞弊空间" },
      { category: "personal", behavior: "晚间与家书或与子通话", frequency: "weekly", triggers: ["压力高"], context: ["私宅"], development: "缓解情感冷却" }
    ],
    rolePlayingNotes: [
      "Domain: 人域",
      "KeyLocations: 链票行内账室 / 九埠市 / 三环亭 / 枢链城",
      "F*: F5/F12/F15(灰度)/F17/F19",
      "口头禅: '先看数据' '把对照表拿来'"
    ]
  },

  // 角色成长轨迹 (新增)
  characterArc: {
    currentStage: "③ 试炼与盟友（夹层制衡）→ ④ 深渊时刻（夫妻理念冲突激化）",
    developmentGoals: [
      {
        id: "sw-g1",
        category: "professional",
        goal: "将‘镜账·对照’与‘链息·止损’写入行会标准并获县署备案",
        motivation: "让透明成为行业底线与护身符",
        timeline: "三个月",
        obstacles: ["何舫逐利策略","官署与黑市共同阻力"],
        progress: 35,
        priority: "high"
      }
    ],
    growthMilestones: [
      {
        id: "sw-m1",
        title: "一次止损救下挤兑",
        description: "在封关夜以链息冻结错误通道，避免群体踩踏",
        significance: "树立公信力",
        prerequisites: ["备案临时通道"],
        relatedGoals: ["sw-g1"],
        status: "planned"
      }
    ],
    personalityChanges: [
      {
        id: "sw-p1",
        trait: "对公开的态度",
        oldValue: "内部解决为先",
        newValue: "必要时公开到三环亭",
        trigger: "旱情做空舆情反噬",
        timeline: "一月",
        significance: "moderate",
        stability: "developing"
      }
    ],
    skillProgression: [
      {
        skill: "底账·回放",
        category: "professional",
        currentLevel: 5,
        targetLevel: 7,
        learningMethod: "案例训练+链算所模型",
        timeframe: "两月",
        obstacles: ["头痛与色弱","数据缺口"],
        mentors: ["链算所讲习导师"]
      }
    ],
    relationshipEvolution: [
      {
        relationshipId: "rel-hefang-spouse",
        personName: "何舫",
        evolutionType: "changing",
        previousState: "理念互补",
        currentState: "在透明与逐利之间拉锯",
        triggers: ["封关期对冲与放风事件"],
        timeline: "当前",
        significance: "影响票行走向与家庭稳定"
      }
    ],
    internalConflicts: [
      {
        id: "sw-ic1",
        title: "家庭 vs. 原则",
        description: "揭露灰度将伤及丈夫与票行，但沉默将伤及无辜",
        conflictingValues: ["家庭","公义"],
        emotionalImpact: "深度内耗",
        manifestations: ["头痛加剧","夜间抄表自问"],
        resolutionAttempts: ["先行匿名存证","寻求第三方清算"],
        status: "active"
      }
    ],
    externalChallenges: [
      {
        id: "sw-ec1",
        title: "巡按与媒体联审",
        description: "三环亭听证或要求公开账证",
        source: "society",
        difficulty: 7,
        timeframe: "两月",
        resources: ["镜账证据","行会内控盟友","中立仓支持"],
        strategies: ["选择性公开","签订保护协议"],
        status: "upcoming"
      }
    ]
  },

  // 互动行为模式 (新增)
  behaviorProfile: {
    communicationStyle: {
      primaryStyle: "assertive",
      verbalCharacteristics: ["短句+数字", "结论先行"],
      nonverbalCharacteristics: ["目光稳定", "用笔敲白板定节奏"],
      listeningStyle: "active",
      feedbackStyle: "风险-方案-时窗三点式",
      conflictCommunication: "先数据后立场",
      culturalInfluences: ["票行与链算所双重语境"]
    },
    bodyLanguage: {
      posture: "坐姿端正",
      gestures: ["两指并拢指表格", "掌心向下示意‘稳’"],
      facialExpressions: ["克制", "轻蹙眉思考"],
      eyeContact: "moderate",
      personalSpace: "normal",
      nervousHabits: ["揉太阳穴", "拇指摩挲算环"],
      confidenceIndicators: ["语速稳", "停顿得体"],
      culturalVariations: ["对长者行简礼，对官员不卑不亢"]
    },
    decisionMaking: {
      approach: "analytical",
      timeframe: "moderate",
      informationGathering: "三表联看（现金流/仓单/舱单）+舆情热度",
      riskTolerance: 4,
      influences: ["家庭安全","行业底线"],
      biases: ["数据至上"],
      decisionHistory: ["拒绝双簿制", "推动镜账与止损程序"]
    },
    conflictResponse: {
      primaryStyle: "collaborating",
      escalationTriggers: ["隐匿账证", "囚票行为"],
      deescalationMethods: ["阶段性公开", "第三方见证"],
      emotionalReactions: ["先冷再硬"],
      physicalReactions: ["太阳穴跳痛"],
      recoveryMethods: ["静息五息", "对照表复盘"],
      conflictHistory: ["两次内部争议转为制度改良"]
    },
    socialBehavior: {
      socialEnergy: "introverted",
      groupDynamics: "在关键节点发言定调",
      socialRoles: ["内控者","证据守门人"],
      boundaryManagement: "公私分明",
      socialAnxieties: ["被迫公开情感"],
      socialStrengths: ["让对手在数据前坐下", "把复杂事讲清"],
      networkingStyle: "专业网络为主",
      socialAdaptability: 7
    },
    workStyle: {
      productivity: "morning",
      environment: "quiet",
      organization: "highly_organized",
      taskManagement: "看板+阈值预警",
      collaboration: "小组分工明确",
      innovation: "把经验固化为制度",
      stressManagement: "规律作息+静息法"
    },
    leadershipStyle: {
      type: "situational",
      strengths: ["稳场控节奏", "以理服人"],
      weaknesses: ["号召力不如外向型领袖"],
      motivationMethods: ["奖惩清晰+透明分润"],
      delegationStyle: "按可靠度与敏感度分配",
      feedbackApproach: "书面清单+面谈要点",
      decisionInclusivity: "中",
      crisisManagement: "先止损后追责"
    },
    learningStyle: {
      primary: "reading",
      preferences: ["报表/案例", "对照表"],
      strengths: ["抽象归纳", "制度化"],
      challenges: ["公众演讲"],
      motivationFactors: ["家庭安全", "行业底线"],
      retentionMethods: ["卡片/口诀"],
      environments: ["账房", "小会议室"],
      adaptability: 7
    }
  }
};
