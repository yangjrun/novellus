const renyu_character_10: Character = {
  id: "char-renyu-peiqingjian-010",
  projectId: "proj-liashi-jiuyu",
  createdAt: new Date("2025-09-17T00:00:00Z"),
  updatedAt: new Date("2025-09-17T00:00:00Z"),

  // 基本信息
  basicInfo: {
    name: "裴青笺",
    alias: ["小笺", "纸风子"],
    age: 22,
    gender: "male",
    occupation: "书场小记者 / 报馆跑稿（《风骨小报》）",
    socialStatus: "良籍·书场/报馆挂名"
  },

  // 外貌特征
  appearance: {
    height: "172cm",
    weight: "56kg",
    hairColor: "乌黑（碎刘海）",
    eyeColor: "深褐",
    skinTone: "偏白",
    bodyType: "清瘦·耐跑型",
    specialMarks: ["右食指常年墨迹", "喉结下方细小风纹胎记"],
    clothingStyle: "浅色窄袖长衫+单肩挎包，随身速写板与小型拓印盒"
  },

  // 性格特质
  personality: {
    coreTraits: ["好奇", "敏感", "正直", "嘴快", "韧性强"],
    values: ["真实可证", "公众知情", "弱者优先"],
    beliefs: ["话语能改命", "现场比传言更可信"],
    fears: ["被封口或牵连消息源", "热度冲昏判断"],
    desires: ["把三环亭做成公开议事的常态", "写出一篇能改变流程的报道"],
    weaknesses: ["情绪易受舆论裹挟", "口快得罪权贵"],
    strengths: ["现场记录快", "嗅觉灵敏", "把复杂事讲清楚"]
  },

  // 背景故事
  background: {
    birthplace: "枢链城书坊巷（人域）",
    family: "父裴楮在纸坊打工，母早逝；与外婆同住多年",
    childhood: "在书场与纸坊间长大，帮人誊抄换饭票",
    education: "县学旁听两年辍学→书场学徒→报馆跑稿",
    importantEvents: [
      "16岁：首次把洪水夜的目击写成小报边栏，被转载",
      "19岁：揭露一处关卡乱收费，遭短期封口",
      "21岁：三环亭旁搭‘事实墙’，收集证词与物证影拓",
      "22岁：参与柳链集工伤系列报道，引发县内检查"
    ],
    trauma: ["曾因报道导致消息源被秋后算账，长期内疚", "封口期被围殴夺稿"],
    achievements: ["‘事实墙’方法被民间自发复制", "建立‘匿名存证箱’（与行会/乡祠合作）"]
  },

  // 能力技能
  abilities: {
    professionalSkills: ["速记与口述整理", "实地采访与取证", "版面故事结构", "危机沟通"],
    specialTalents: ["听风辨意（从人群噪声里捕捉异议点）", "誊影速拓（快速拓印印迹/票据）"],
    languages: ["通域语", "人域乡言", "天域官音（应付）"],
    learningAbility: "现场-案例型，边跑边学，能快速形成操作清单",
    socialSkills: "与底层打成一片；能在冲突双方间建立‘说给我听’的窗口",
    practicalSkills: ["匿名存证流程", "简单伤口处理", "逃生路线规划"]
  },

  // 人际关系
  relationships: {
    family: [
      { name: "裴楮", relationship: "父子", description: "纸坊短工，怕祸上身，劝其收敛", importance: "medium" }
    ],
    friends: [
      { name: "林岚", relationship: "同盟/线人互助", description: "证据链搭档之一，负责技术细节与条款", importance: "high" },
      { name: "苏杳", relationship: "友人", description: "学徒圈吹哨人，为报道提供一线素材", importance: "high" }
    ],
    lovers: [],
    enemies: [
      { name: "董铖", relationship: "对立", description: "多次以‘不当报道’为由传唤", importance: "high" },
      { name: "何舫", relationship: "利益冲突", description: "试图买断或导流舆情失败后反噬", importance: "medium" }
    ],
    mentors: [
      { name: "白简", relationship: "报馆老编辑/半师", description: "教其‘半步怀疑’与自证规则", importance: "medium" }
    ],
    subordinates: [
      { name: "小报志愿者", relationship: "组织者-志愿者", description: "维护事实墙与匿名存证箱", importance: "medium" }
    ],
    socialCircle: ["书场说书人", "报馆编辑圈", "行会与乡祠的非正式联络人"]
  },

  // 生活状况
  lifestyle: {
    residence: "枢链城书坊巷合租小阁楼（与两名写手合住）",
    economicStatus: "清贫（稿费为主，偶有赞助）",
    dailyRoutine: "清晨巡讯→白日跑现场→傍晚整理素材→夜间排版与投递",
    hobbies: ["收集各地小报", "刻私章", "画人物小像"],
    foodPreferences: ["便携干粮", "浓茶续命", "炸饼摊"],
    entertainment: ["书场听段子", "码头看相声‘说风’"]
  },

  // 心理状态 (增强版)
  psychology: {
    mentalHealth: "高敏感+高动机；陷入舆论风暴时焦虑飙升",
    mentalHealthStatus: "good",
    copingMechanisms: [
      { type: "healthy", strategy: "事实清单+三证规则（目击/物证/对照）", triggers: ["被攻击","质疑"], effectiveness: 9, frequency: "frequent" },
      { type: "adaptive", strategy: "自嘲与短视频记录", triggers: ["封口","围堵"], effectiveness: 6, frequency: "occasional" }
    ],
    emotionalPatterns: [
      { emotion: "义愤", triggers: ["现场暴力","加缚令"], intensity: 7, duration: "brief", expression: "连发短句与提问", impact: "易被贴标签" }
    ],
    trauma: [
      { type: "recent", event: "消息源被秋后算账", age: 21, severity: "severe", status: "healing", triggers: ["夜敲门","不明尾随"], effects: ["惊醒","手抖"], copingMethods: ["与乡祠/行会建立保护名单","匿名化流程"] }
    ],
    growthNeeds: ["可核验的公开渠道", "法律援助与人身保护"],
    cognitivePatterns: [
      { type: "belief", description: "公开是最好的防身", situations: ["威胁","封口"], impact: "mixed", awareness: "conscious" },
      { type: "bias", description: "倾向相信底层叙述", situations: ["冲突采访"], impact: "mixed", awareness: "conscious" }
    ],
    stressResponses: [
      {
        stressor: "报馆被查+个人被传唤",
        physicalResponse: ["喉紧","手抖","心悸"],
        emotionalResponse: ["焦虑","愤怒"],
        behavioralResponse: ["连夜备份","开启匿名渠道"],
        cognitiveResponse: ["过度演练问话场景"],
        timeframe: "1-3日"
      }
    ],
    emotionalIntelligence: {
      selfAwareness: 6, selfRegulation: 6, motivation: 9, empathy: 7, socialSkills: 7,
      strengths: ["把复杂议题转成故事", "在混乱中抓重点"], weaknesses: ["自我保护不足","冲动发声"]
    },
    psychologicalDefenses: ["理智化", "幽默化"],
    mentalHealthHistory: [
      { date: new Date("2025-02-15"), status: "good", notes: "完成‘事实墙’系统化，安全边界上升" }
    ]
  },

  // 故事功能
  storyRole: {
    characterType: "supporting",
    characterArc: "旁观者 → 吹哨者 → 地下记录者",
    conflictRole: "舆论放大与证据保全的关键枢纽",
    symbolism: "纸与风：文字乘风，或救人，或杀人；‘事实墙’=公共记忆",
    readerConnection: "像极现实中的热血记者：真诚、莽撞、管用"
  },

  // 特殊设定 (增强版)
  specialSettings: {
    worldBuilding: "裂世九域·法则链纪元",
    culturalBackground: "人域-书场/报馆文化（与行会/乡祠形成保护网）",
    historicalContext: "裂世后时代",
    technologyLevel: "链工学-中",
    magicAbilities:
      "法则链：主[风] 副[因果]；契合度:2；禁忌:[造谣以攻, 以匿名诬陷]；代表术式:[风言·传布(扩散可核信息), 舆潮·回响(把同类证词聚拢成合唱), 誊影·摹真(快速拓印印迹/票据)]；代价: 声带疲劳与短时耳鸣，舆论反噬引发‘社会性窒息’感",
    culturalIdentity: {
      primaryCulture: "人域-书场/报馆文化",
      subcultures: ["码头说风圈", "书院旁听生"],
      culturalValues: ["公开","可证","同理"],
      culturalConflicts: ["与官署‘流程优先’冲突", "与票行‘信息不对称’冲突"],
      assimilationLevel: 6,
      culturalPride: 6,
      traditionalPractices: ["登报前‘三证礼’：目击、物证、对照"],
      modernAdaptations: ["匿名存证箱与事实墙制度化"]
    },
    religiousBeliefs: {
      religion: "源祖传说（自由派）",
      denomination: "书场私祠",
      devotionLevel: 3,
      practices: ["对纸火行小礼（敬文字）"],
      beliefs: ["文字是‘小链’，可束亦可救"],
      doubts: ["祭司是否应干预言论"],
      spiritualExperiences: ["在风口处写稿，有‘耳语’指向关键线索的错觉"],
      religionInLife: "minimal"
    },
    languageProfile: {
      nativeLanguage: "通域语",
      fluentLanguages: ["人域乡言","天域官音（勉强）"],
      learningLanguages: [],
      accents: ["书场快语（短句、节拍分明）"],
      dialectVariations: [],
      speechPatterns: [
        { characteristic: "三问一结", examples: ["发生了什么？", "谁在场？", "有无凭据？", "结论：先保人。"], frequency: "often", context: ["采访","直播口述"], origin: "报馆训练" }
      ],
      languageBarriers: ["官样文章冗长不耐"],
      communicationPreferences: ["当面+录音", "公开核验渠道"]
    },
    behaviorPatterns: [
      { category: "professional", behavior: "搭‘事实墙’与匿名存证箱", frequency: "situational", triggers: ["群体事件","封关"], context: ["三环亭","码头"], development: "提升证据密度与可核性" },
      { category: "personal", behavior: "夜跑后录‘一分记’，复盘当天偏见", frequency: "daily", triggers: ["情绪波动"], context: ["河堤"], development: "降低冲动发声" }
    ],
    rolePlayingNotes: [
      "Domain: 人域",
      "KeyLocations: 三环亭 / 书场 / 九埠市码头 / 枢链城",
      "F*: F5/F6/F8/F15/F19/F20",
      "口头禅: '先核再发' '事实贴上墙'"
    ]
  },

  // 角色成长轨迹 (新增)
  characterArc: {
    currentStage: "③ 试炼与盟友（舆论放大/证据保全）",
    developmentGoals: [
      {
        id: "pqj-g1",
        category: "professional",
        goal: "把‘事实墙+匿名存证’写入三环亭听证的正式流程",
        motivation: "让公开核验成为制度",
        timeline: "两个月",
        obstacles: ["官署阻力","票行舆情操纵","消息源安全"],
        progress: 40,
        priority: "high"
      }
    ],
    growthMilestones: [
      {
        id: "pqj-m1",
        title: "首场‘事实墙听证’",
        description: "一场听证全程使用事实墙与匿名存证，舆情由吵闹转为可证",
        significance: "舆论转向‘证据主义’",
        prerequisites: ["乡祠与行会背书"],
        relatedGoals: ["pqj-g1"],
        status: "planned"
      }
    ],
    personalityChanges: [
      {
        id: "pqj-p1",
        trait: "发声节制",
        oldValue: "热度即正义",
        newValue: "核验先于热度",
        trigger: "一次错误报道带来伤害",
        timeline: "一月",
        significance: "major",
        stability: "developing"
      }
    ],
    skillProgression: [
      {
        skill: "舆潮·回响",
        category: "professional",
        currentLevel: 4,
        targetLevel: 7,
        learningMethod: "与书院法度生合作做证据可视化",
        timeframe: "两月",
        obstacles: ["数据处理能力不足","设备短缺"],
        mentors: ["白简"]
      }
    ],
    relationshipEvolution: [
      {
        relationshipId: "rel-linlan-media",
        personName: "林岚",
        evolutionType: "strengthening",
        previousState: "互通线索",
        currentState: "制度化合作",
        triggers: ["共同推进‘事实墙听证’试点"],
        timeline: "持续",
        significance: "使主线证据链更稳"
      }
    ],
    internalConflicts: [
      {
        id: "pqj-ic1",
        title: "公开与保护的冲突",
        description: "报道会伤到弱者吗？",
        conflictingValues: ["真相","保护"],
        emotionalImpact: "自责与犹疑",
        manifestations: ["改稿改到凌晨","延迟发稿"],
        resolutionAttempts: ["匿名化+延迟公开", "先给法律援助"],
        status: "active"
      }
    ],
    externalChallenges: [
      {
        id: "pqj-ec1",
        title: "封口与造谣指控",
        description: "被指‘扰乱秩序’，面临传唤与禁言",
        source: "society",
        difficulty: 7,
        timeframe: "两月",
        resources: ["行会/乡祠背书","中立仓作会议点","镜账式证据库"],
        strategies: ["全程录音录像","事实墙现场核验","律师与祠司见证"],
        status: "upcoming"
      }
    ]
  },

  // 互动行为模式 (新增)
  behaviorProfile: {
    communicationStyle: {
      primaryStyle: "assertive",
      verbalCharacteristics: ["短句提问", "结论在后", "反复核对细节"],
      nonverbalCharacteristics: ["笔尖敲板定节", "点头复述他人观点"],
      listeningStyle: "active",
      feedbackStyle: "三点式回馈（事实/疑点/待核）",
      conflictCommunication: "请见证、上墙、再对话",
      culturalInfluences: ["书场快语与报馆纪律"]
    },
    bodyLanguage: {
      posture: "微前倾（倾听姿态）",
      gestures: ["举笔示停", "两指并拢指向证据"],
      facialExpressions: ["专注", "偶露少年气的倔强"],
      eyeContact: "moderate",
      personalSpace: "normal",
      nervousHabits: ["抠墨迹", "清嗓"],
      confidenceIndicators: ["语速稳", "停顿恰当"],
      culturalVariations: ["对长者与祠司使用敬语，避免顶撞"]
    },
    decisionMaking: {
      approach: "analytical",
      timeframe: "quick",
      informationGathering: "三证规则+多源交叉验证",
      riskTolerance: 5,
      influences: ["消息源安全","公共利益"],
      biases: ["底层叙述偏好"],
      decisionHistory: ["多起小规模报道推动流程修补"]
    },
    conflictResponse: {
      primaryStyle: "collaborating",
      escalationTriggers: ["删稿封口", "暴力驱离"],
      deescalationMethods: ["引入第三方见证", "事实墙公开核验"],
      emotionalReactions: ["短暂激动后自控"],
      physicalReactions: ["喉紧","心跳快"],
      recoveryMethods: ["夜跑", "录一分记"],
      conflictHistory: ["两次被驱离仍以证据回击成功"]
    },
    socialBehavior: {
      socialEnergy: "ambivert",
      groupDynamics: "能在人群中快速聚焦议题并分工",
      socialRoles: ["记录者","放大器"],
      boundaryManagement: "保护消息源的边界很硬",
      socialAnxieties: ["公开演讲前五分钟紧张"],
      socialStrengths: ["让人愿意开口", "把复杂说清楚"],
      networkingStyle: "书场-行会-乡祠三角网络",
      socialAdaptability: 8
    },
    workStyle: {
      productivity: "evening",
      environment: "bustling",
      organization: "moderately_organized",
      taskManagement: "清单+时窗+备份",
      collaboration: "与编辑/志愿者协作",
      innovation: "事实墙/匿名存证流程化",
      stressManagement: "夜跑+口述复盘"
    },
    leadershipStyle: {
      type: "situational",
      strengths: ["临场调度", "舆论引导"],
      weaknesses: ["情绪上头时判断易偏"],
      motivationMethods: ["公开署名与事实奖励"],
      delegationStyle: "按可信度与技能分配任务",
      feedbackApproach: "事实-改进-再核",
      decisionInclusivity: "中高",
      crisisManagement: "先保人后发稿"
    },
    learningStyle: {
      primary: "multimodal",
      preferences: ["现场/录音/图像并用"],
      strengths: ["整合多源证据"],
      challenges: ["长篇理论枯燥"],
      motivationFactors: ["改变现实", "保护弱者"],
      retentionMethods: ["卡片与时间线", "事实墙"],
      environments: ["书场", "三环亭", "码头"],
      adaptability: 8
    }
  }
};
