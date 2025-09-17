const renyu_character_05: Character = {
  id: "char-renyu-hefang-005",
  projectId: "proj-liashi-jiuyu",
  createdAt: new Date("2025-09-17T00:00:00Z"),
  updatedAt: new Date("2025-09-17T00:00:00Z"),

  // 基本信息
  basicInfo: {
    name: "何舫",
    alias: ["链票公", "七成利"],
    age: 38,
    gender: "male",
    occupation: "链票行账吏长 / 股东（九埠市）",
    socialStatus: "良籍·行会会员"
  },

  // 外貌特征
  appearance: {
    height: "176cm",
    weight: "70kg",
    hairColor: "乌黑（油顺后梳）",
    eyeColor: "墨黑",
    skinTone: "偏白",
    bodyType: "中等·耐坐型",
    specialMarks: ["右手中指与无名指墨渍常年不退", "右门牙贴金"],
    clothingStyle: "深色长袍+窄袖，腰系票袋与小骨算盘，袖内藏细卷宗筒"
  },

  // 性格特质
  personality: {
    coreTraits: ["精于算计", "油滑礼貌", "耐心", "机会主义"],
    values: ["信誉（对上）", "利润（对内）", "风险对冲"],
    beliefs: ["价格即真相", "市场高于人情", "把手伸到水里才知道冷暖"],
    fears: ["挤兑风潮", "御史问罪冻结账户", "失去关卡关系网"],
    desires: ["垄断九埠港融资", "拿到天域背书的官方票据资格"],
    weaknesses: ["逐利心重易低估民意反噬", "对理想主义者天然轻视"],
    strengths: ["账目复盘与造势", "人脉经营", "条款缝补与灰度操作"]
  },

  // 背景故事
  background: {
    birthplace: "九埠市（人域·码头群）",
    family: "票行小户出身；妻沈纨（管账），一子在御书镇读书",
    childhood: "在票柜下长到膝高就开始认票，随父母夜里清账识水火",
    education: "行会账房带教；曾赴天域链算所旁听‘利率与风险’短课",
    importantEvents: [
      "16岁：老票行被闹事焚毁，随父母搬到水巷重开柜台",
      "25岁：首创‘舱单质押+因果锁’周转法，救活三家濒破的商户",
      "32岁：与县衙建立‘应急备付’协议，换取涉案账本优先核对权",
      "36岁：借旱情做空粮价，赚厚利也引来舆情反噬与御史警告"
    ],
    trauma: ["少年时亲历挤兑与焚柜暴力", "旱情做空引发百姓围堵险酿冲突"],
    achievements: ["标准化舱单质押流程", "建立‘中立仓备付池’雏形（与行会）"]
  },

  // 能力技能
  abilities: {
    professionalSkills: ["复式账与审计反审计", "合同条款缝补", "风险对冲设计", "资金调度"],
    specialTalents: ["心算极快（票据拆分/合并）", "听语速辨对方紧张度与撒谎概率"],
    languages: ["通域语", "人域乡言", "天域官音", "灵域匠话（工作流利）"],
    learningAbility: "模式识别型，能把零散事件抽象成可复制的流程",
    socialSkills: "酒局周旋、局势造势、让步换话语权",
    practicalSkills: ["快速做现金流三表", "搭建临时暗仓与逃生通道", "应急账本焚毁/转印"]
  },

  // 人际关系
  relationships: {
    family: [
      { name: "沈纨", relationship: "夫妻", description: "内账主管，擅控制成本与现金流", importance: "high" },
      { name: "何佑", relationship: "父子", description: "御书镇求学，偏文弱", importance: "medium" }
    ],
    friends: [
      { name: "董铖", relationship: "利益同盟", description: "县缚司书办，互通案情与资金", importance: "high" }
    ],
    lovers: [],
    enemies: [
      { name: "薛箴", relationship: "商业对手", description: "中立仓倡议者，拒其垄断", importance: "high" },
      { name: "林岚", relationship: "对立者", description: "在三环亭多次就“粮价操纵”公开质疑", importance: "high" }
    ],
    mentors: [
      { name: "白简", relationship: "账房前辈", description: "教其‘半账留余’法则，后理念渐分歧", importance: "medium" }
    ],
    subordinates: [
      { name: "票脚班", relationship: "班头-班员", description: "三人小队跑关卡递票与收数", importance: "medium" }
    ],
    socialCircle: ["行会会首", "水巷票庄", "关卡税官圈", "码头牙人与经纪"]
  },

  // 生活状况
  lifestyle: {
    residence: "九埠市水巷票行楼上私宅（带密室）",
    economicStatus: "富裕（高现金流但高杠杆）",
    dailyRoutine: "辰时盯备付→午前会客→午后做对冲与条款缝补→夜盘复盘舆情与路书",
    hobbies: ["收集环印拓本稀罕版", "玩票面雕版", "听评话‘商战公案’"],
    foodPreferences: ["鲥鱼", "酒糟小菜", "清酒"],
    entertainment: ["水巷茶局", "小戏园包厢"]
  },

  // 心理状态
  psychology: {
    mentalHealth: "总体稳定，遇舆情挤兑风险时焦虑显著",
    mentalHealthStatus: "good",
    copingMechanisms: [
      { type: "adaptive", strategy: "迅速分散头寸与对冲", triggers: ["封关","抢兑"], effectiveness: 9, frequency: "frequent" },
      { type: "maladaptive", strategy: "放风（造势）压对手", triggers: ["谈判劣势","现金吃紧"], effectiveness: 6, frequency: "occasional" }
    ],
    emotionalPatterns: [
      { emotion: "兴奋", triggers: ["信息不对称","价格剧震"], intensity: 6, duration: "brief", expression: "语速加快、连用比喻", impact: "易高估控制力" }
    ],
    trauma: [
      { type: "adolescent", event: "挤兑焚柜", age: 16, severity: "severe", status: "healing", triggers: ["鼓噪声","火光与纸灰气味"], effects: ["短时僵直","出汗"], copingMethods: ["退场交给副手","转移人群注意力"] }
    ],
    growthNeeds: ["官方合规牌照", "可信第三方清算渠道"],
    cognitivePatterns: [
      { type: "bias", description: "幸存者偏差（只记住赢的案例）", situations: ["投机","并购"], impact: "mixed", awareness: "subconscious" },
      { type: "belief", description: "利益共同体最稳", situations: ["结盟","合并"], impact: "positive", awareness: "conscious" }
    ],
    stressResponses: [
      {
        stressor: "封关叠加抢兑",
        physicalResponse: ["胃酸","指尖发麻"],
        emotionalResponse: ["急躁","戒备"],
        behavioralResponse: ["削价甩货","放风抹黑对手"],
        cognitiveResponse: ["过拟合舆情样本","选择性忽略底层民意"],
        timeframe: "封关期全程"
      }
    ],
    emotionalIntelligence: {
      selfAwareness: 6, selfRegulation: 6, motivation: 9, empathy: 4, socialSkills: 8,
      strengths: ["迅速建局","读懂对方底价"], weaknesses: ["对弱者处境缺乏耐心"]
    },
    psychologicalDefenses: ["合理化","分隔化"],
    mentalHealthHistory: [
      { date: new Date("2024-10-01"), status: "good", notes: "化解一次小规模抢兑，转危为安" }
    ]
  },

  // 故事功能
  storyRole: {
    characterType: "antagonist",
    characterArc: "市场守门人 → 操纵者 →（可选）制度合规者",
    conflictRole: "资金卡喉/票据垄断/舆论操纵",
    symbolism: "银票网=看不见的枷锁；金牙=逐利的笑",
    readerConnection: "又气又服：聪明、有效，却冷血"
  },

  // 特殊设定
  specialSettings: {
    worldBuilding: "裂世九域·法则链纪元",
    culturalBackground: "人域-票行/行会文化（对接官署与码头）",
    historicalContext: "裂世后时代",
    technologyLevel: "链工学-中",
    magicAbilities:
      "法则链：主[因果] 副[金]；契合度:4；禁忌:[价格操纵, 囚票（以债锁人）]；代表术式:[因果锁·汇票, 链息·滚动, 市声·放风, 舱单·质押]；代价: 高频运算导致短时‘数字幻视’与心律不齐，需以冷水与静息压制",
    culturalIdentity: {
      primaryCulture: "人域-行会文化",
      subcultures: ["水巷票庄", "关卡税官茶局"],
      culturalValues: ["契约", "效率", "信誉"],
      culturalConflicts: ["与中立仓/共险金理念冲突", "与基层民意冲突"],
      assimilationLevel: 8,
      culturalPride: 7,
      traditionalPractices: ["开柜祭账", "年终清册谢礼"],
      modernAdaptations: ["票据标准化模板", "对冲工具普及"]
    },
    religiousBeliefs: {
      religion: "天命信仰（实用派）",
      denomination: "行会祠",
      devotionLevel: 3,
      practices: ["开柜小礼"],
      beliefs: ["天意偏爱效率与秩序"],
      doubts: ["祭司干预经济的必要性"],
      spiritualExperiences: ["挤兑夜“听见数字在坠落”从而提前限兑"],
      religionInLife: "minimal"
    },
    languageProfile: {
      nativeLanguage: "通域语",
      fluentLanguages: ["人域乡言","天域官音","灵域匠话（工作）"],
      learningLanguages: [],
      accents: ["票柜腔（数字与术语密集）"],
      dialectVariations: [],
      speechPatterns: [
        { characteristic: "条目化+比喻", examples: ["给我一个对冲位", "你现在在玩裸奔"], frequency: "often", context: ["谈判","危机沟通"], origin: "票行训练+码头话术" }
      ],
      languageBarriers: ["长篇学术辩论不耐"],
      communicationPreferences: ["短会+清单", "书面为准"]
    },
    behaviorPatterns: [
      { category: "professional", behavior: "分账三套：公开/内控/应急", frequency: "daily", triggers: ["监管/舆情/封关"], context: ["票行后台"], development: "提高生存但加剧不透明" },
      { category: "social", behavior: "借茶局放风试探", frequency: "weekly", triggers: ["价格战","政策风向不明"], context: ["水巷茶馆"], development: "造势成瘾" }
    ],
    rolePlayingNotes: [
      "Domain: 人域",
      "KeyLocations: 九埠市 / 枢链城 / 三环亭 / 链票行",
      "F*: F2/F5/F15/F17/F19",
      "口头禅: '给我一个对冲位' '书面写清楚'"
    ]
  },

  // 角色成长轨迹
  characterArc: {
    currentStage: "③ 试炼与盟友（反面势力整局阶段）",
    developmentGoals: [
      {
        id: "hf-g1",
        category: "professional",
        goal: "拿到天域备案的‘官方票据资格’",
        motivation: "做大做强并对抗中立仓",
        timeline: "半年",
        obstacles: ["御史审查","行会内部分化","舆论压力"],
        progress: 30,
        priority: "high"
      }
    ],
    growthMilestones: [
      {
        id: "hf-m1",
        title: "推出新型票据‘三链汇票’",
        description: "绑定舱单+仓单+关卡放行三要素的因果锁汇票",
        significance: "市场支配力上升",
        prerequisites: ["关卡与仓方签合作"],
        relatedGoals: ["hf-g1"],
        status: "planned"
      }
    ],
    personalityChanges: [
      {
        id: "hf-p1",
        trait: "对民意的判断",
        oldValue: "忽视",
        newValue: "不得不考虑‘舆论成本’",
        trigger: "做空粮价后被围堵与御史警告",
        timeline: "两月",
        significance: "moderate",
        stability: "developing"
      }
    ],
    skillProgression: [
      {
        skill: "舆情对冲",
        category: "professional",
        currentLevel: 4,
        targetLevel: 7,
        learningMethod: "与报馆/书场合作造势与澄清",
        timeframe: "三月",
        obstacles: ["口碑损耗","反噬不可控"],
        mentors: ["无（自学成派）"]
      }
    ],
    relationshipEvolution: [
      {
        relationshipId: "rel-dongcheng",
        personName: "董铖",
        evolutionType: "strengthening",
        previousState: "互通有无",
        currentState: "深度互绑（案情与资金）",
        triggers: ["封关期联手控盘"],
        timeline: "当前",
        significance: "共同风险上升"
      }
    ],
    internalConflicts: [
      {
        id: "hf-ic1",
        title: "利润 vs. 口碑",
        description: "短期利润最大化与长期信誉之间的拉扯",
        conflictingValues: ["效率","公平"],
        emotionalImpact: "焦虑与强迫复盘",
        manifestations: ["连夜改条款","频繁换盟友"],
        resolutionAttempts: ["设备付池护城河"],
        status: "active"
      }
    ],
    externalChallenges: [
      {
        id: "hf-ec1",
        title: "中立仓与共险金扩张",
        description: "薛箴推动的制度降低其垄断能力",
        source: "society",
        difficulty: 7,
        timeframe: "汛季",
        resources: ["官署关系网","三链汇票"],
        strategies: ["联合官署设置准入门槛","舆论抹黑‘共险金’"],
        status: "current"
      }
    ]
  },

  // 互动行为模式
  behaviorProfile: {
    communicationStyle: {
      primaryStyle: "assertive",
      verbalCharacteristics: ["条目化与比喻结合", "数字先行"],
      nonverbalCharacteristics: ["微笑不露齿", "指尖敲桌配合节拍"],
      listeningStyle: "selective",
      feedbackStyle: "给价与期限两档选择",
      conflictCommunication: "先压价后给退路",
      culturalInfluences: ["票行与关卡茶局文化"]
    },
    bodyLanguage: {
      posture: "坐姿略后仰（示从容）",
      gestures: ["拇指与食指捏‘小圈’示意额度", "掌心向外示意暂停"],
      facialExpressions: ["礼貌笑", "眼角下垂显冷淡"],
      eyeContact: "moderate",
      personalSpace: "normal",
      nervousHabits: ["摩挲金牙", "搓指尖墨渍"],
      confidenceIndicators: ["语速稳", "停顿拿捏好"],
      culturalVariations: ["对官员拱手不俯身"]
    },
    decisionMaking: {
      approach: "analytical",
      timeframe: "quick",
      informationGathering: "价差/天气/封关/舆情四象盘",
      riskTolerance: 7,
      influences: ["现金流", "监管风向"],
      biases: ["幸存者偏差", "控制错觉"],
      decisionHistory: ["旱情做空", "与官署签备付协定"]
    },
    conflictResponse: {
      primaryStyle: "compromising",
      escalationTriggers: ["抢兑", "合约撕毁", "媒体暴露黑箱"],
      deescalationMethods: ["分批兑付", "质押扩抵", "放风转移焦点"],
      emotionalReactions: ["隐怒转冷笑"],
      physicalReactions: ["指尖发麻", "胃酸"],
      recoveryMethods: ["冷水洗手", "独处清单复盘"],
      conflictHistory: ["多次平息小规模挤兑"]
    },
    socialBehavior: {
      socialEnergy: "ambivert",
      groupDynamics: "局中拉线者，善拆分群体诉求",
      socialRoles: ["撮合者","暗盘庄家"],
      boundaryManagement: "公私分明但留人情债",
      socialAnxieties: ["被当众质询条款漏洞"],
      socialStrengths: ["把握人群情绪", "搭桥换利益"],
      networkingStyle: "茶局-账本双线",
      socialAdaptability: 8
    },
    workStyle: {
      productivity: "evening",
      environment: "bustling",
      organization: "highly_organized",
      taskManagement: "三账并行（公开/内控/应急）",
      collaboration: "小圈层授权制",
      innovation: "票据结构创新与流程灰度化",
      stressManagement: "对冲+放风+冷处理"
    },
    leadershipStyle: {
      type: "situational",
      strengths: ["资源整合", "局势控盘"],
      weaknesses: ["透明度低", "信任脆弱"],
      motivationMethods: ["差异化分润", "人情债绑定"],
      delegationStyle: "按忠诚度与能力加权分配",
      feedbackApproach: "结果导向冷评",
      decisionInclusivity: "低-中",
      crisisManagement: "限兑+分仓+放风"
    },
    learningStyle: {
      primary: "reading",
      preferences: ["报表与清单", "案例集"],
      strengths: ["抽象-实践转化快"],
      challenges: ["价值辩论不耐"],
      motivationFactors: ["扩大市场份额", "获取牌照"],
      retentionMethods: ["对照表", "口诀"],
      environments: ["票行账房", "茶馆包厢"],
      adaptability: 7
    }
  }
};
