const renyu_character_03: Character = {
  id: "char-renyu-suyao-003",
  projectId: "proj-liashi-jiuyu",
  createdAt: new Date("2025-09-17T00:00:00Z"),
  updatedAt: new Date("2025-09-17T00:00:00Z"),

  // 基本信息
  basicInfo: {
    name: "苏杳",
    alias: ["小杳", "结丝手"],
    age: 18,
    gender: "female",
    occupation: "柳链集织局学徒（质检/打样）",
    socialStatus: "良籍·行会登记户"
  },

  // 外貌特征
  appearance: {
    height: "160cm",
    weight: "47kg",
    hairColor: "乌黑（常束发）",
    eyeColor: "浅棕",
    skinTone: "偏白",
    bodyType: "纤细·灵巧型",
    specialMarks: ["食指与中指针眼茧", "左颧小刀口旧痕"],
    clothingStyle: "浅灰工裙+护指缠带，外披薄色披衫便于藏线"
  },

  // 性格特质
  personality: {
    coreTraits: ["细致", "机敏", "务实", "护短"],
    values: ["体面劳动", "互助", "诚信"],
    beliefs: ["好工要有好价", "小人物也能改变流程"],
    fears: ["被评印一票否决", "同伴再次工伤致残"],
    desires: ["让学徒签上公平链契", "做出能进城展的打样"],
    weaknesses: ["胆大心细但偶尔逞强", "对权威天然不信"],
    strengths: ["手上功夫稳定", "察觉瑕疵与伪造", "结网联络能力强"]
  },

  // 背景故事
  background: {
    birthplace: "柳链集（人域·织造镇）",
    family: "父苏成（染坊短工），母温荷（家庭织女）",
    childhood: "自小帮母理线，识布纹早；常去九埠市帮搬货",
    education: "乡学识字，织局学徒制三年；外堂讲习旁听过一季",
    importantEvents: [
      "14岁：学徒期替同伴顶班，首次被派做质检",
      "16岁：同伴手指卷入机头，促成车间加装护罩",
      "17岁：因拒签空白链契被停工一月，暗中记下证据",
      "18岁：与林岚合作，整理织局欠薪与伪契据链"
    ],
    trauma: ["目击工伤致残", "停工期间被监工多次威胁"],
    achievements: ["提出护罩改良建议被采纳", "打样《细环纹》入围镇展"]
  },

  // 能力技能
  abilities: {
    professionalSkills: ["布匹质检", "打样与版花", "产线节拍优化", "小账核对"],
    specialTalents: ["结丝传印（以丝线转印微弱环纹）", "听织判伪（凭机声辨产线异常）"],
    languages: ["通域语", "人域乡言", "灵域匠话（入门）"],
    learningAbility: "手眼协调强，靠模仿与复刻学习快",
    socialSkills: "能在学徒间建立互助小组，善激励与分工",
    practicalSkills: ["藏线传讯", "夜行避哨", "简易止血包扎"]
  },

  // 人际关系
  relationships: {
    family: [
      { name: "苏成", relationship: "父女", description: "染坊短工，支持她维权但怕得罪人", importance: "medium" },
      { name: "温荷", relationship: "母女", description: "家庭织女，传承手艺与勤俭观", importance: "high" }
    ],
    friends: [
      { name: "林岚", relationship: "至交/搭档", description: "证据链伙伴，互为线人", importance: "high" }
    ],
    lovers: [],
    enemies: [
      { name: "沈合", relationship: "对手", description: "织局头工，推动空白链契与压价", importance: "high" }
    ],
    mentors: [
      { name: "赵绢师", relationship: "师徒", description: "老质检师，教她‘听织’与瑕疵分类", importance: "medium" }
    ],
    subordinates: [
      { name: "学徒小组", relationship: "组长-组员", description: "三人互助小组，记录工时与事故", importance: "medium" }
    ],
    socialCircle: ["学徒圈", "九埠市搬运脚夫", "小贩与布行掌柜"]
  },

  // 生活状况
  lifestyle: {
    residence: "柳链集东巷·学徒宿舍（与两名女学徒合住）",
    economicStatus: "勉强自给（常被拖欠）",
    dailyRoutine: "辰时上工→午后质检与打样→晚间记账与整理证据→夜练结丝",
    hobbies: ["收集旧布样", "去九埠市逛二手器具摊"],
    foodPreferences: ["面饼蘸汤", "清炒野菜", "偶尔咸鱼"],
    entertainment: ["看社戏‘环鼓’", "听说书摊工棚段子"]
  },

  // 心理状态
  psychology: {
    mentalHealth: "总体良好，维权期压力显著升高",
    mentalHealthStatus: "good",
    copingMechanisms: [
      { type: "healthy", strategy: "与同伴分担与记录", triggers: ["被威胁","欠薪"], effectiveness: 8, frequency: "frequent" },
      { type: "adaptive", strategy: "夜间编花样转移注意", triggers: ["焦虑","恐惧"], effectiveness: 6, frequency: "occasional" }
    ],
    emotionalPatterns: [
      { emotion: "警觉", triggers: ["监工靠近","突击抽检"], intensity: 6, duration: "moderate", expression: "停手观察再应对", impact: "减少冲动失误" }
    ],
    trauma: [
      { type: "adolescent", event: "同伴工伤致残", age: 16, severity: "severe", status: "healing", triggers: ["机头突响","血迹气味"], effects: ["短时僵直","噩梦"], copingMethods: ["深呼吸","转移注意力到指尖动作"] }
    ],
    growthNeeds: ["法律援助与外部背书", "更稳定收入与人身安全"],
    cognitivePatterns: [
      { type: "belief", description: "集体才能保住个体权益", situations: ["谈判","停工"], impact: "positive", awareness: "conscious" }
    ],
    stressResponses: [
      {
        stressor: "停工威胁与扣工分",
        physicalResponse: ["胃胀","手心出汗"],
        emotionalResponse: ["焦虑","恼怒"],
        behavioralResponse: ["深夜织样","加快收集证据"],
        cognitiveResponse: ["过度演练谈判台词"],
        timeframe: "持续至谈判结束"
      }
    ],
    emotionalIntelligence: {
      selfAwareness: 7, selfRegulation: 6, motivation: 8, empathy: 7, socialSkills: 8,
      strengths: ["化解学徒内讧","安抚与动员兼顾"], weaknesses: ["对权威硬顶易受伤"]
    },
    psychologicalDefenses: ["幽默化解", "理智化"],
    mentalHealthHistory: [
      { date: new Date("2025-04-01"), status: "good", notes: "护罩改良后噩梦减少" }
    ]
  },

  // 故事功能
  storyRole: {
    characterType: "supporting",
    characterArc: "被压迫学徒 → 组织者 → 吹哨人",
    conflictRole: "证据持有人/工伤维权组织者",
    symbolism: "结丝=连接个体，织布=编织新契约",
    readerConnection: "打工人视角的勇敢与机巧"
  },

  // 特殊设定
  specialSettings: {
    worldBuilding: "裂世九域·法则链纪元",
    culturalBackground: "人域-织造镇工坊文化（与灵域工艺链路相通）",
    historicalContext: "裂世后时代",
    technologyLevel: "链工学-中",
    magicAbilities:
      "法则链：主[因果] 副[风]；契合度:2；禁忌:[以结丝私转官印]；代表术式:[结丝·移印, 听织·判伪, 织纹·固形]；代价: 指尖麻木、偶发耳鸣（织机声幻听）",
    culturalIdentity: {
      primaryCulture: "人域-工坊文化",
      subcultures: ["柳链集学徒圈", "九埠市码头小贩圈"],
      culturalValues: ["勤俭", "互助", "诚信"],
      culturalConflicts: ["对评印黑箱的不信任", "与官署话术冲突"],
      assimilationLevel: 6,
      culturalPride: 6,
      traditionalPractices: ["秋试链筵围观与助阵"],
      modernAdaptations: ["用链票记账", "小组互助基金"]
    },
    religiousBeliefs: {
      religion: "源祖传说",
      denomination: "乡祠环祖",
      devotionLevel: 4,
      practices: ["祖灵续籍祭随家人参加"],
      beliefs: ["命运可被一点点缝补"],
      doubts: ["祭司对工人是否公平"],
      spiritualExperiences: ["夜里打样时感到‘纹理会说话’"],
      religionInLife: "minimal"
    },
    languageProfile: {
      nativeLanguage: "通域语",
      fluentLanguages: ["人域乡言", "灵域匠话（入门）"],
      learningLanguages: [],
      accents: ["织局短句节奏"],
      dialectVariations: [],
      speechPatterns: [
        { characteristic: "短句下指令", examples: ["停机，看纬", "慢三拍"], frequency: "often", context: ["车间","应急"], origin: "工位训练" }
      ],
      languageBarriers: ["天域官话礼仪性表达不擅长"],
      communicationPreferences: ["面对面+手势辅助", "谈判前先排练"]
    },
    behaviorPatterns: [
      { category: "professional", behavior: "先停机再排查", frequency: "situational", triggers: ["异常声响"], context: ["车间"], development: "减少事故与损耗" },
      { category: "social", behavior: "私下建小群共享证据", frequency: "situational", triggers: ["欠薪","评印抽检"], context: ["学徒宿舍","码头茶棚"], development: "形成微型网络" }
    ],
    rolePlayingNotes: [
      "Domain: 人域",
      "KeyLocations: 柳链集 / 九埠市 / 枢链城 / 三环亭",
      "F*: F5/F6/F8/F15/F19",
      "口头禅: '先停机' '线会说话'"
    ]
  },

  // 角色成长轨迹
  characterArc: {
    currentStage: "③ 试炼与盟友（学徒维权线）",
    developmentGoals: [
      {
        id: "suy-g1",
        category: "professional",
        goal: "推动公平链契模板在柳链集试行",
        motivation: "保护同伴、保障体面劳动",
        timeline: "两个月",
        obstacles: ["头工阻挠","评印抽检卡脖子"],
        progress: 35,
        priority: "high"
      }
    ],
    growthMilestones: [
      {
        id: "suy-m1",
        title: "拿到第一份真凭据",
        description: "掌握空白链契与伪印样本",
        significance: "谈判筹码大增",
        prerequisites: [],
        relatedGoals: ["suy-g1"],
        status: "in_progress"
      }
    ],
    personalityChanges: [
      {
        id: "suy-p1",
        trait: "对权威的态度",
        oldValue: "逞强硬顶",
        newValue: "学会借助外援与舆论",
        trigger: "与林岚、商队合作成功",
        timeline: "一月",
        significance: "moderate",
        stability: "developing"
      }
    ],
    skillProgression: [
      {
        skill: "结丝·移印",
        category: "professional",
        currentLevel: 3,
        targetLevel: 6,
        learningMethod: "师徒口传+反复演练",
        timeframe: "三个月",
        obstacles: ["指尖麻木","耳鸣"],
        mentors: ["赵绢师"]
      }
    ],
    relationshipEvolution: [
      {
        relationshipId: "rel-linlan-ally",
        personName: "林岚",
        evolutionType: "strengthening",
        previousState: "同乡朋友",
        currentState: "证据搭档",
        triggers: ["共同应对评印抽检与停工威胁"],
        timeline: "持续",
        significance: "互补长短、扩大影响"
      }
    ],
    internalConflicts: [
      {
        id: "suy-ic1",
        title: "冲动维权 vs. 同伴安全",
        description: "公开爆料会否牵连弱者",
        conflictingValues: ["正义","保护"],
        emotionalImpact: "自责与犹豫",
        manifestations: ["半夜删改爆料稿"],
        resolutionAttempts: ["改为分步公开与匿名存证"],
        status: "active"
      }
    ],
    externalChallenges: [
      {
        id: "suy-ec1",
        title: "停工威胁与连坐",
        description: "头工欲以连坐破小组",
        source: "professional",
        difficulty: 7,
        timeframe: "两周",
        resources: ["证据链","商队中立仓借地谈判"],
        strategies: ["舆论预热","法律条款备查"],
        status: "current"
      }
    ]
  },

  // 互动行为模式
  behaviorProfile: {
    communicationStyle: {
      primaryStyle: "assertive",
      verbalCharacteristics: ["短句清晰", "先事实后要求"],
      nonverbalCharacteristics: ["手势指向布面/机件", "点头确认节拍"],
      listeningStyle: "active",
      feedbackStyle: "即时纠错+示范",
      conflictCommunication: "提出可执行替代方案",
      culturalInfluences: ["工坊讲究‘手上见真章’"]
    },
    bodyLanguage: {
      posture: "轻盈灵活",
      gestures: ["两指捏线示意", "掌心平摊示意停机"],
      facialExpressions: ["专注", "微笑鼓劲"],
      eyeContact: "moderate",
      personalSpace: "normal",
      nervousHabits: ["捻线头", "咬下唇"],
      confidenceIndicators: ["动作干净", "语速稳定"],
      culturalVariations: ["对长辈行小扣环礼"]
    },
    decisionMaking: {
      approach: "collaborative",
      timeframe: "quick",
      informationGathering: "同伴回报+现场观察",
      riskTolerance: 6,
      influences: ["同伴安全", "证据充分度"],
      biases: ["偏信工友而不信官话"],
      decisionHistory: ["拒签空白契", "组织互助小组"]
    },
    conflictResponse: {
      primaryStyle: "collaborating",
      escalationTriggers: ["空白链契", "拖欠工分"],
      deescalationMethods: ["停机点检", "请第三方见证"],
      emotionalReactions: ["先压怒后据理"],
      physicalReactions: ["手心出汗", "呼吸变浅"],
      recoveryMethods: ["编花样", "与同伴闲聊排压"],
      conflictHistory: ["两次小规模停机示警无伤亡"]
    },
    socialBehavior: {
      socialEnergy: "ambivert",
      groupDynamics: "小组核心，能协调不同脾气",
      socialRoles: ["组织者", "通气人"],
      boundaryManagement: "对外谨慎，对内坦诚",
      socialAnxieties: ["公开演讲紧张"],
      socialStrengths: ["一线信息收集快", "信任构建快"],
      networkingStyle: "织网式连点成面",
      socialAdaptability: 8
    },
    workStyle: {
      productivity: "morning",
      environment: "bustling",
      organization: "moderately_organized",
      taskManagement: "白板列点+节拍卡",
      collaboration: "分工清楚、互相顶班",
      innovation: "小改小革不断",
      stressManagement: "分解任务+同伴分担"
    },
    leadershipStyle: {
      type: "servant",
      strengths: ["照顾队友", "提升士气"],
      weaknesses: ["易自我消耗", "不擅向上沟通"],
      motivationMethods: ["榜样示范", "小奖励"],
      delegationStyle: "按强项分配",
      feedbackApproach: "事后复盘表扬多于批评",
      decisionInclusivity: "中高",
      crisisManagement: "先保人身安全再谈指标"
    },
    learningStyle: {
      primary: "kinesthetic",
      preferences: ["手把手演示", "样品对照"],
      strengths: ["动作记忆强", "复刻稳定"],
      challenges: ["理论术语吸收慢"],
      motivationFactors: ["同伴受益", "作品被认可"],
      retentionMethods: ["反复练手", "口传口诀"],
      environments: ["车间", "样品室"],
      adaptability: 7
    }
  }
};
