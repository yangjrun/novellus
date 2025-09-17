const renyu_character_07: Character = {
  id: "char-renyu-zhaohuai-007",
  projectId: "proj-liashi-jiuyu",
  createdAt: new Date("2025-09-17T00:00:00Z"),
  updatedAt: new Date("2025-09-17T00:00:00Z"),

  // 基本信息
  basicInfo: {
    name: "赵槐",
    alias: ["铜锁", "押夜头"],
    age: 34,
    gender: "male",
    occupation: "差役头 / 押解队长（县缚司）",
    socialStatus: "良籍·官署编制"
  },

  // 外貌特征
  appearance: {
    height: "182cm",
    weight: "78kg",
    hairColor: "乌黑平头",
    eyeColor: "深褐",
    skinTone: "古铜",
    bodyType: "壮实·爆发力型",
    specialMarks: ["右颧骨旧裂痕", "双腕缠护带留勒痕", "肩背链甲磨痕"],
    clothingStyle: "短甲+灰蓝差服，腰悬三环锁与短环杖，夜勤披黑披风"
  },

  // 性格特质
  personality: {
    coreTraits: ["执行力强", "服从权威", "谨慎多疑", "护短"],
    values: ["纪律", "安全", "兄弟情"],
    beliefs: ["规矩之外皆危险", "善意必须有代价"],
    fears: ["押解翻车被追责", "家人受牵连"],
    desires: ["升做捕司", "置办城内小宅安置母亲"],
    weaknesses: ["同理心不足", "逞强不愿求援"],
    strengths: ["现场控场", "近身擒拿", "夜行搜捕"]
  },

  // 背景故事
  background: {
    birthplace: "枢链城西巷（人域）",
    family: "寡母宋氏在；弟在码头做脚夫",
    childhood: "贫坊长大，早岁为保安行脚，后被招入县衙当差",
    education: "县衙武训+法度馆短训‘押解流程’一季",
    importantEvents: [
      "20岁：夜捕涉黑案立功，升为小队副",
      "26岁：押解途中遭伏击，护住卷宗但丢一名队友（心结）",
      "30岁：被董铖提为差役头，参与‘黑籍配额’执行",
      "33岁：三环亭听证护场，与林岚第一次正面交锋"
    ],
    trauma: ["队友在自己身后被射穿而亡", "母亲险因欠税被贴封条"],
    achievements: ["建立夜路押解‘三点一线’巡守法", "改良三环锁抛掷式，缩短缚距"]
  },

  // 能力技能
  abilities: {
    professionalSkills: ["队列与押解编组", "近身擒拿与束缚", "夜间搜捕与巡线", "现场威慑与人群疏散"],
    specialTalents: ["黑暗中方位感强（听风判向）", "能从脚印估算人数体重"],
    languages: ["通域语", "人域乡言", "天域官音（执法口）"],
    learningAbility: "动作-程序化学习，偏经验复盘",
    socialSkills: "对上服从、对下强硬，能以利益稳住小队",
    practicalSkills: ["三环锁抛缚", "简易止血包扎", "临时设卡与搜身流程"]
  },

  // 人际关系
  relationships: {
    family: [
      { name: "宋氏", relationship: "母子", description: "体弱，盼其转文职", importance: "high" }
    ],
    friends: [
      { name: "鲁三", relationship: "旧识/亦敌亦友", description: "护运队长，数度交手，互相点到为止", importance: "medium" }
    ],
    lovers: [],
    enemies: [
      { name: "林岚", relationship: "对立", description: "多次在听证与街头行动上拆其押解", importance: "high" }
    ],
    mentors: [
      { name: "董铖", relationship: "上司", description: "书办，提携与约束并重", importance: "high" }
    ],
    subordinates: [
      { name: "夜巡小队", relationship: "队长-队员", description: "六人编组，懂默契手势", importance: "high" }
    ],
    socialCircle: ["县衙差役圈", "保安行脚旧同事", "码头脚夫圈（弟牵线）"]
  },

  // 生活状况
  lifestyle: {
    residence: "县衙后巷租屋（与母同住）",
    economicStatus: "温饱略上（靠夜勤补贴）",
    dailyRoutine: "晨练→午休→黄昏点名→夜巡/押解→黎明复盘",
    hobbies: ["打磨三环锁", "练石锁", "喂一只流浪黑狗"],
    foodPreferences: ["硬馍就肉", "烧酒少量"],
    entertainment: ["校场看把式", "听书场捕盗段子"]
  },

  // 心理状态
  psychology: {
    mentalHealth: "轻度创伤后警觉高；总体功能良好",
    mentalHealthStatus: "good",
    copingMechanisms: [
      { type: "healthy", strategy: "训练与流程化复盘", triggers: ["押解失控预感"], effectiveness: 8, frequency: "frequent" },
      { type: "maladaptive", strategy: "情绪压抑与酒精", triggers: ["队友牺牲回忆"], effectiveness: 3, frequency: "occasional" }
    ],
    emotionalPatterns: [
      { emotion: "愤怒", triggers: ["被公开羞辱","队员受伤"], intensity: 6, duration: "brief", expression: "提高音量、短促指令", impact: "易过度用力" }
    ],
    trauma: [
      { type: "adult", event: "押解伏击队友身亡", age: 26, severity: "severe", status: "healing", triggers: ["弩弦声","雨夜土腥味"], effects: ["握拳发抖","短时失神"], copingMethods: ["训练转移","与母对话"] }
    ],
    growthNeeds: ["更清晰的责权保护", "替代暴力的控场工具"],
    cognitivePatterns: [
      { type: "assumption", description: "善意常被利用", situations: ["群众求情","放人请求"], impact: "negative", awareness: "conscious" }
    ],
    stressResponses: [
      {
        stressor: "连续夜勤与舆情围观",
        physicalResponse: ["肩颈僵硬","手腕疼"],
        emotionalResponse: ["烦躁","麻木"],
        behavioralResponse: ["提高押解等级","收紧队列"],
        cognitiveResponse: ["确认偏误增强"],
        timeframe: "一周"
      }
    ],
    emotionalIntelligence: {
      selfAwareness: 5, selfRegulation: 6, motivation: 7, empathy: 3, socialSkills: 6,
      strengths: ["稳场", "清晰指令"], weaknesses: ["倾听不足", "黑白思维"]
    },
    psychologicalDefenses: ["合理化", "分隔化"],
    mentalHealthHistory: [
      { date: new Date("2024-05-01"), status: "fair", notes: "伏击周年期波动", triggers: ["雨夜","弩声"], improvements: ["增加白日休整"] }
    ]
  },

  // 故事功能
  storyRole: {
    characterType: "supporting",
    characterArc: "执行者 → 犹疑者 →（可选）倒戈证人",
    conflictRole: "关卡/押解的执行力与暴力工具",
    symbolism: "三环锁=秩序的铁面；黑狗=忠诚与野性",
    readerConnection: "硬汉外壳下的普通人：被制度使用也自我说服"
  },

  // 特殊设定
  specialSettings: {
    worldBuilding: "裂世九域·法则链纪元",
    culturalBackground: "人域-官署/差役文化",
    historicalContext: "裂世后时代",
    technologyLevel: "链工学-中",
    magicAbilities:
      "法则链：主[土] 副[金]；契合度:2；禁忌:[私设路卡, 过度束缚]；代表术式:[锁步·定身, 三环·抛缚, 地势·压阵]；代价: 肩肘劳损与短时‘感觉迟钝’，事后出现迟滞痛",
    culturalIdentity: {
      primaryCulture: "人域-官署文化",
      subcultures: ["保安行脚旧风"],
      culturalValues: ["纪律","安全","服从"],
      culturalConflicts: ["与乡社人情逻辑冲突","与行会谈判文化冲突"],
      assimilationLevel: 7,
      culturalPride: 6,
      traditionalPractices: ["巡夜祭火", "押解前静握铜锁"],
      modernAdaptations: ["流程卡片化押解清单"]
    },
    religiousBeliefs: {
      religion: "天命信仰（朴素）",
      denomination: "县祠",
      devotionLevel: 4,
      practices: ["巡夜前简礼", "亡者名册默念"],
      beliefs: ["命有定数，人要尽责"],
      doubts: ["黑籍配额是否正当"],
      spiritualExperiences: ["伏击夜听到‘地声’提前换位活命"],
      religionInLife: "minimal"
    },
    languageProfile: {
      nativeLanguage: "通域语",
      fluentLanguages: ["人域乡言","天域官音（执法口）"],
      learningLanguages: [],
      accents: ["短句口令腔"],
      dialectVariations: [],
      speechPatterns: [
        { characteristic: "口令化", examples: ["靠边", "不许动", "手展平"], frequency: "often", context: ["押解","搜捕"], origin: "县衙训练" }
      ],
      languageBarriers: ["长篇礼仪与学术辩论不耐"],
      communicationPreferences: ["现场口令+手势", "书面回执简短"]
    },
    behaviorPatterns: [
      { category: "professional", behavior: "押解前做‘三检’：人/物/路", frequency: "situational", triggers: ["跨镇运押"], context: ["出发前"], development: "事故率下降" },
      { category: "personal", behavior: "喂流浪黑狗", frequency: "daily", triggers: ["收队后"], context: ["后巷"], development: "情绪缓冲" }
    ],
    rolePlayingNotes: [
      "Domain: 人域",
      "KeyLocations: 县缚司署 / 环印关镇 / 三环亭 / 老链桥",
      "F*: F3/F9/F12/F17",
      "口头禅: '规矩摆在这儿' '不想吃苦就别闹'"
    ]
  },

  // 角色成长轨迹
  characterArc: {
    currentStage: "③ 试炼（强势执法）→ ④ 深渊（行动失手）",
    developmentGoals: [
      {
        id: "zh-g1",
        category: "professional",
        goal: "将押解流程升级为‘无伤押解’示范队",
        motivation: "减少伤亡、避免问责",
        timeline: "三月",
        obstacles: ["上级绩效偏好强硬", "装备不足"],
        progress: 25,
        priority: "medium"
      }
    ],
    growthMilestones: [
      {
        id: "zh-m1",
        title: "在三环亭放下环杖一次",
        description: "接受第三方见证搜索而非强行带走",
        significance: "价值观松动",
        prerequisites: ["舆情与证据压力"],
        relatedGoals: ["zh-g1"],
        status: "planned"
      }
    ],
    personalityChanges: [
      {
        id: "zh-p1",
        trait: "对善意的判断",
        oldValue: "一律视为风险",
        newValue: "在见证下有限信任",
        trigger: "一次押解误伤与赔偿",
        timeline: "一月",
        significance: "moderate",
        stability: "developing"
      }
    ],
    skillProgression: [
      {
        skill: "三环·抛缚",
        category: "physical",
        currentLevel: 7,
        targetLevel: 8,
        learningMethod: "负重练习+模拟演练",
        timeframe: "两月",
        obstacles: ["肩肘疼痛","装备磨损"],
        mentors: ["老捕司（匿名）"]
      }
    ],
    relationshipEvolution: [
      {
        relationshipId: "rel-dongcheng-guard",
        personName: "董铖",
        evolutionType: "weakening",
        previousState: "完全服从",
        currentState: "开始保留意见",
        triggers: ["黑籍执行酿成民变险情"],
        timeline: "当前",
        significance: "可能成为倒戈证人"
      }
    ],
    internalConflicts: [
      {
        id: "zh-ic1",
        title: "服从 vs. 良知",
        description: "执行命令与避免无辜受伤的冲突",
        conflictingValues: ["纪律","仁慈"],
        emotionalImpact: "失眠与噩梦",
        manifestations: ["酒后沉默","与母少言"],
        resolutionAttempts: ["改良流程","请求第三方见证"],
        status: "active"
      }
    ],
    externalChallenges: [
      {
        id: "zh-ec1",
        title: "跨域押解的风评与风险",
        description: "路卡冲突、媒体围观与黑市劫囚",
        source: "society",
        difficulty: 7,
        timeframe: "两月",
        resources: ["改良押解流程","与商队建立临时共护"],
        strategies: ["路线错峰","证据公开与见证"],
        status: "upcoming"
      }
    ]
  },

  // 互动行为模式
  behaviorProfile: {
    communicationStyle: {
      primaryStyle: "direct",
      verbalCharacteristics: ["口令短促", "避免赘述"],
      nonverbalCharacteristics: ["手势明确", "站位压迫感强"],
      listeningStyle: "selective",
      feedbackStyle: "合规/不合规二分",
      conflictCommunication: "先稳控再沟通",
      culturalInfluences: ["官署执法语境"]
    },
    bodyLanguage: {
      posture: "重心前倾",
      gestures: ["掌心向下压场", "两指示位"],
      facialExpressions: ["冷硬", "紧咬后槽牙"],
      eyeContact: "frequent",
      personalSpace: "distant",
      nervousHabits: ["拇指摩挲锁环", "咬腮帮"],
      confidenceIndicators: ["步幅大", "节奏稳"],
      culturalVariations: ["对长者保持礼数但不多言"]
    },
    decisionMaking: {
      approach: "cautious",
      timeframe: "quick",
      informationGathering: "路探+耳目+线人",
      riskTolerance: 5,
      influences: ["上级命令","队友安全"],
      biases: ["确认偏误", "对善意的怀疑"],
      decisionHistory: ["两次平安押解跨镇重犯", "一次误伤赔偿案"]
    },
    conflictResponse: {
      primaryStyle: "competing",
      escalationTriggers: ["围观逼近", "撕扯押解链"],
      deescalationMethods: ["后退一步示位", "请第三方见证"],
      emotionalReactions: ["短怒"],
      physicalReactions: ["肩颈绷紧"],
      recoveryMethods: ["练石锁", "与黑狗散步"],
      conflictHistory: ["多次夜捕无伤控制成功"]
    },
    socialBehavior: {
      socialEnergy: "introverted",
      groupDynamics: "小队里权威核心",
      socialRoles: ["队长","护押者"],
      boundaryManagement: "公私分明",
      socialAnxieties: ["大庭广众被质询"],
      socialStrengths: ["稳场", "保护队友"],
      networkingStyle: "同袍与旧路子",
      socialAdaptability: 6
    },
    workStyle: {
      productivity: "night",
      environment: "bustling",
      organization: "highly_organized",
      taskManagement: "清单化与口令化",
      collaboration: "小队分工明确",
      innovation: "押解流程与装备改良",
      stressManagement: "体能训练与规程复盘"
    },
    leadershipStyle: {
      type: "situational",
      strengths: ["稳定军心", "执行到位"],
      weaknesses: ["沟通粗糙", "对变化迟钝"],
      motivationMethods: ["以身作则+分配夜勤补贴"],
      delegationStyle: "按体能与经验排位",
      feedbackApproach: "口头简评+罚夜勤",
      decisionInclusivity: "低",
      crisisManagement: "先控人再沟通"
    },
    learningStyle: {
      primary: "kinesthetic",
      preferences: ["实战演练", "情景模拟"],
      strengths: ["动作记忆", "在高压下执行"],
      challenges: ["文书冗长内容"],
      motivationFactors: ["队友安全", "升迁"],
      retentionMethods: ["手势口令", "场景复盘"],
      environments: ["校场", "夜路"],
      adaptability: 6
    }
  }
};
