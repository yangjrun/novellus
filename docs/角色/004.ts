const renyu_character_04: Character = {
  id: "char-renyu-xuezhen-004",
  projectId: "proj-liashi-jiuyu",
  createdAt: new Date("2025-09-17T00:00:00Z"),
  updatedAt: new Date("2025-09-17T00:00:00Z"),

  // 基本信息
  basicInfo: {
    name: "薛箴",
    alias: ["算风客", "半账先生"],
    age: 36,
    gender: "male",
    occupation: "九埠市商队头人（河陆联运）",
    socialStatus: "行会会员·良籍"
  },

  // 外貌特征
  appearance: {
    height: "181cm",
    weight: "72kg",
    hairColor: "乌黑（鬓微霜）",
    eyeColor: "深棕",
    skinTone: "小麦",
    bodyType: "修长・耐力型",
    specialMarks: ["右拇指火漆灼痕（环印常用位）", "左眉尾细小旧伤"],
    clothingStyle: "深色旅行斗篷＋皮靴＋可藏卷宗的多袋马甲，随身铜环骨算盘"
  },

  // 性格特质
  personality: {
    coreTraits: ["审慎", "务实", "讲信", "压仓式冷静", "对冲思维"],
    values: ["契约", "信誉", "生存优先"],
    beliefs: ["公平来自可执行的条款", "风险要被定价"],
    fears: ["队员伤亡", "账面失真导致破产"],
    desires: ["把九埠市打造成跨域中立港", "建立标准化互市合同"],
    weaknesses: ["过度算计导致疏离感", "对理想主义者的怀疑"],
    strengths: ["风险评估", "跨域谈判", "临场指挥与路线改造"]
  },

  // 背景故事
  background: {
    birthplace: "九埠市（人域·码头群）",
    family: "祖上小商，父早逝，随舅跑船；妻亡（疫年），一女寄读于御书镇",
    childhood: "自小在码头长大，学会三地行话与最原始的对换贸易",
    education: "行会账房带教＋天域法度馆短训“合同与风险”一季",
    importantEvents: [
      "18岁：首次独立带队渡汛成功，救下一船货与三名脚夫",
      "24岁：疫年失妻，誓言建立‘共险金’避免单人破产",
      "30岁：推动互市小码头设‘中立仓’，缓和关卡冲突",
      "35岁：在‘黑籍配额上调’风波中暗护三十余人越境"
    ],
    trauma: ["疫年失妻与幼子", "一次夜渡翻船造成两名脚夫溺亡"],
    achievements: ["共险金制度倡议者之一", "首批跨域标准舱单链契制定人"]
  },

  // 能力技能
  abilities: {
    professionalSkills: ["路线设计与调度", "合同拟定与仲裁", "资金周转与对冲", "舱单与清关流程管理"],
    specialTalents: ["听风判潮（气压与水位联动）", "人情账本（记人不记数亦能还原交易网络）"],
    languages: ["通域语", "人域乡言", "天域官音", "灵域匠话（工作流利）", "荒域部落言（口语）"],
    learningAbility: "抽象-实操双通道，善于把经验固化为流程卡",
    socialSkills: "跨阶层沟通强；能在冲突双方找折中与‘可执行’方案",
    practicalSkills: ["队列行军与守夜编组", "简易应急修缮（舟车）", "伤口包扎与溺急救"]
  },

  // 人际关系
  relationships: {
    family: [
      { name: "薛弦", relationship: "父女", description: "寄读御书镇，聪敏但体弱", importance: "high" }
    ],
    friends: [
      { name: "鲁三", relationship: "把兄弟", description: "护运队长，掌舵与弩术皆精", importance: "high" }
    ],
    lovers: [],
    enemies: [
      { name: "何舫", relationship: "利益对手", description: "九埠市链票行股东，常以金融手段卡其现金流", importance: "high" }
    ],
    mentors: [
      { name: "白简", relationship: "行会前辈", description: "老账房，传其‘半账法’与风险分摊术", importance: "medium" }
    ],
    subordinates: [
      { name: "护运队", relationship: "队长-队员", description: "二十余人编组，轮换制", importance: "high" }
    ],
    socialCircle: ["行会会首", "码头牙人", "天域巡链驻港联络官", "灵域物料经纪"]
  },

  // 生活状况
  lifestyle: {
    residence: "九埠市·水巷行会会馆后院独间（多在路上）",
    economicStatus: "稳健上升（现金流紧、信誉高）",
    dailyRoutine: "晨会分工→核对舱单与天气→走关卡路→夜间复盘与路书更新",
    hobbies: ["收集各地环印拓本", "绘制路书‘风骨图’"],
    foodPreferences: ["清淡咸鲜", "耐储干粮", "偶尔烈酒"],
    entertainment: ["河上对歌", "看码头‘说风’"]
  },

  // 心理状态 (增强版)
  psychology: {
    mentalHealth: "总体稳定，逢汛季压力显著上升",
    mentalHealthStatus: "good",
    copingMechanisms: [
      { type: "healthy", strategy: "路书复盘与对冲表", triggers: ["暴雨预警","现金流吃紧"], effectiveness: 9, frequency: "frequent" },
      { type: "adaptive", strategy: "情感抽离处理事故", triggers: ["伤亡","纠纷"], effectiveness: 6, frequency: "situational" }
    ],
    emotionalPatterns: [
      { emotion: "焦虑", triggers: ["队员受伤","边关封锁"], intensity: 6, duration: "moderate", expression: "压仓式沉默", impact: "短时与人疏离" }
    ],
    trauma: [
      { type: "adult", event: "夜渡翻船溺亡事故", age: 27, severity: "severe", status: "healing", triggers: ["鼓风骤起","水位突涨"], effects: ["短时僵直","噩梦"], copingMethods: ["改制夜航规则","双舵双锚"] }
    ],
    growthNeeds: ["制度化风险共担的官方背书", "稳定的跨域通行权"],
    cognitivePatterns: [
      { type: "heuristic", description: "最小损失规则（留有余地）", situations: ["谈判","撤退"], impact: "positive", awareness: "conscious" }
    ],
    stressResponses: [
      {
        stressor: "连续封关与货主逼款",
        physicalResponse: ["胃酸","肩颈痛"],
        emotionalResponse: ["烦躁","倦怠"],
        behavioralResponse: ["减少睡眠","加班做路书"],
        cognitiveResponse: ["反复推演路线变体"],
        timeframe: "封关期全程"
      }
    ],
    emotionalIntelligence: {
      selfAwareness: 7, selfRegulation: 7, motivation: 8, empathy: 7, socialSkills: 8,
      strengths: ["跨阵营沟通","安抚冲突群体"], weaknesses: ["与亲近者情感表达不足"]
    },
    psychologicalDefenses: ["理智化", "分隔化"],
    mentalHealthHistory: [
      { date: new Date("2024-08-01"), status: "good", notes: "完成一次无损撤离，心态恢复" }
    ]
  },

  // 故事功能
  storyRole: {
    characterType: "supporting",
    characterArc: "稳健商贾 → 中立仲裁者 → 新秩序设计者",
    conflictRole: "跨域物流与资金枢纽/中立仓的守门人",
    symbolism: "铜环骨算盘=权衡与对冲；半账=留有余地不走极端",
    readerConnection: "冷静靠谱的大人形象，给主角提供“可执行”的路"
  },

  // 特殊设定 (增强版)
  specialSettings: {
    worldBuilding: "裂世九域·法则链纪元",
    culturalBackground: "人域-码头/行会文化（与灵域、荒域贸易相连）",
    historicalContext: "裂世后时代",
    technologyLevel: "链工学-中",
    magicAbilities:
      "法则链：主[因果] 副[水]；契合度:3；禁忌:[以命相押的赌约]；代表术式:[因果对冲(风险分摊), 舱单·因果锁, 水势·借流]；代价: 过度对冲导致短时‘判断迟滞’，汛季手指发麻",
    culturalIdentity: {
      primaryCulture: "人域-行会文化",
      subcultures: ["九埠市码头群", "关带互市"],
      culturalValues: ["契约", "信誉", "互利"],
      culturalConflicts: ["与官署‘流程优先’的冲突", "与黑市‘无契约’的冲突"],
      assimilationLevel: 7,
      culturalPride: 7,
      traditionalPractices: ["开潮前祈流", "共险金祭账"],
      modernAdaptations: ["中立仓制度", "标准舱单链契"]
    },
    religiousBeliefs: {
      religion: "天命信仰（务实派）",
      denomination: "行会祠",
      devotionLevel: 4,
      practices: ["开航小礼", "祭亡名册"],
      beliefs: ["人定胜天需先算清成本"],
      doubts: ["祭司干预经济的必要性"],
      spiritualExperiences: ["夜航时‘听见风骨’改变航向避祟"],
      religionInLife: "minimal"
    },
    languageProfile: {
      nativeLanguage: "通域语",
      fluentLanguages: ["人域乡言","天域官音","灵域匠话（工作流利）","荒域部落言（口语）"],
      learningLanguages: [],
      accents: ["码头快语"],
      dialectVariations: [],
      speechPatterns: [
        { characteristic: "交易条款化", examples: ["给我两个可执行选项", "我们做个对冲"], frequency: "often", context: ["谈判","危机处置"], origin: "行会训练" }
      ],
      languageBarriers: ["学院化长辩不耐"],
      communicationPreferences: ["短句+数字", "白板列项"]
    },
    behaviorPatterns: [
      { category: "professional", behavior: "每次行动前做‘三案’：正案/备案/撤案", frequency: "situational", triggers: ["跨域任务"], context: ["码头指挥","关卡谈判"], development: "降低灾损" },
      { category: "personal", behavior: "夜读路书并更新‘风骨图’", frequency: "daily", triggers: ["汛季"], context: ["船舱","会馆"], development: "形成个人知识库" }
    ],
    rolePlayingNotes: [
      "Domain: 人域",
      "KeyLocations: 九埠市 / 互市小码头 / 枢链城 / 环印关镇 / 三环亭",
      "F*: F7/F12/F15(灰度)/F19/F20",
      "口头禅: '给我可执行的方案' '我们对冲一下风险'"
    ]
  },

  // 角色成长轨迹 (新增)
  characterArc: {
    currentStage: "②→③（跨门槛与试炼期的盟友/后勤中枢）",
    developmentGoals: [
      {
        id: "xz-g1",
        category: "professional",
        goal: "把‘中立仓’写入互市环约并获天域备案",
        motivation: "降低封关期社会成本",
        timeline: "半年",
        obstacles: ["官署抵触","黑市破坏","资金压力"],
        progress: 40,
        priority: "high"
      }
    ],
    growthMilestones: [
      {
        id: "xz-m1",
        title: "首份跨域标准合同落地",
        description: "在三环亭完成三方签署并执行一轮无纠纷结算",
        significance: "样板效应",
        prerequisites: ["获得两域背书"],
        relatedGoals: ["xz-g1"],
        status: "planned"
      }
    ],
    personalityChanges: [
      {
        id: "xz-p1",
        trait: "对理想主义者的态度",
        oldValue: "本能怀疑",
        newValue: "愿意托底并给出可执行路径",
        trigger: "林岚在救堤与维权中的表现",
        timeline: "一季",
        significance: "moderate",
        stability: "developing"
      }
    ],
    skillProgression: [
      {
        skill: "因果对冲术",
        category: "professional",
        currentLevel: 6,
        targetLevel: 8,
        learningMethod: "实务演算+案例归档",
        timeframe: "四月",
        obstacles: ["数据样本不足","外部干预"],
        mentors: ["白简"]
      }
    ],
    relationshipEvolution: [
      {
        relationshipId: "rel-linlan-mentor",
        personName: "林岚",
        evolutionType: "strengthening",
        previousState: "引路人-受教者",
        currentState: "共谋改革伙伴",
        triggers: ["共同完成一次跨域救援与合同试点"],
        timeline: "持续",
        significance: "为‘新链约’铺路"
      }
    ],
    internalConflicts: [
      {
        id: "xz-ic1",
        title: "利润 vs. 公益",
        description: "当公共利益与自身账面冲突时的抉择",
        conflictingValues: ["生存","公平"],
        emotionalImpact: "自责与犹疑",
        manifestations: ["延迟结算给自己吃紧"],
        resolutionAttempts: ["建立共险金缓冲"],
        status: "active"
      }
    ],
    externalChallenges: [
      {
        id: "xz-ec1",
        title: "封关与黑市扰局",
        description: "官方封锁叠加黑市抬价，供应链紊乱",
        source: "society",
        difficulty: 8,
        timeframe: "汛季",
        resources: ["中立仓","行会网络","因果锁合同"],
        strategies: ["舆论公开账目","与官署建立快速通道"],
        status: "current"
      }
    ]
  },

  // 互动行为模式 (新增)
  behaviorProfile: {
    communicationStyle: {
      primaryStyle: "direct",
      verbalCharacteristics: ["条目化指令", "数字与时间窗优先"],
      nonverbalCharacteristics: ["目光扫全场", "指节轻敲算盘节拍"],
      listeningStyle: "active",
      feedbackStyle: "结果导向+复盘清单",
      conflictCommunication: "给备选方案与代价清单",
      culturalInfluences: ["码头快语与行会谈判礼"]
    },
    bodyLanguage: {
      posture: "放松但随时可动",
      gestures: ["两指比出‘时窗’", "掌心向下示意压住情绪"],
      facialExpressions: ["沉稳", "短促点头"],
      eyeContact: "moderate",
      personalSpace: "normal",
      nervousHabits: ["揉拇指火漆痕", "摸算盘"],
      confidenceIndicators: ["语速稳", "步伐有节奏"],
      culturalVariations: ["对长者与官员行半礼不全跪"]
    },
    decisionMaking: {
      approach: "analytical",
      timeframe: "quick",
      informationGathering: "天气+路书+价格+风向四元模型",
      riskTolerance: 6,
      influences: ["队员安全", "现金流", "政治风向"],
      biases: ["对不对称条款高度警惕"],
      decisionHistory: ["夜撤保人弃货一次", "封关期为邻镇保供一次"]
    },
    conflictResponse: {
      primaryStyle: "compromising",
      escalationTriggers: ["撕毁合同", "掳人勒索"],
      deescalationMethods: ["人货分离先救人", "设中立仓托管"],
      emotionalReactions: ["冷静压制怒气"],
      physicalReactions: ["肩颈紧绷"],
      recoveryMethods: ["跑码头放松", "与女儿书信"],
      conflictHistory: ["处理三起跨域冲突无人员伤亡"]
    },
    socialBehavior: {
      socialEnergy: "ambivert",
      groupDynamics: "能在群体中迅速建立秩序",
      socialRoles: ["调解者","指挥者"],
      boundaryManagement: "公私分明，交易即交易",
      socialAnxieties: ["公开仪式性长辩不适"],
      socialStrengths: ["跨阵营协调", "信誉资源"],
      networkingStyle: "节点型网络（官-商-工-民）",
      socialAdaptability: 8
    },
    workStyle: {
      productivity: "morning",
      environment: "bustling",
      organization: "highly_organized",
      taskManagement: "白板+路书+备用计划",
      collaboration: "小队自治+头人拍板",
      innovation: "把经验固化为流程卡与模板",
      stressManagement: "运动+复盘+分摊风险"
    },
    leadershipStyle: {
      type: "situational",
      strengths: ["临机分工","稳场控节奏"],
      weaknesses: ["对情感支持不足"],
      motivationMethods: ["以身作则+收益分配透明"],
      delegationStyle: "按专长授权队长",
      feedbackApproach: "事后复盘表",
      decisionInclusivity: "中",
      crisisManagement: "先保人后保货"
    },
    learningStyle: {
      primary: "multimodal",
      preferences: ["地图与数据", "案例复盘"],
      strengths: ["整合多源信息"],
      challenges: ["冗长理论课"],
      motivationFactors: ["降低损失", "提升信誉"],
      retentionMethods: ["路书笔记", "口述录音"],
      environments: ["码头", "会馆作战室"],
      adaptability: 8
    }
  }
};
