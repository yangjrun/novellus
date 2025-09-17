const renyu_character_06: Character = {
  id: "char-renyu-wenyan-006",
  projectId: "proj-liashi-jiuyu",
  createdAt: new Date("2025-09-17T00:00:00Z"),
  updatedAt: new Date("2025-09-17T00:00:00Z"),

  // 基本信息
  basicInfo: {
    name: "温砚",
    alias: ["乡祠先生", "白鬓祷者"],
    age: 45,
    gender: "male",
    occupation: "乡祭（乡祠司/链祭执行者）",
    socialStatus: "良籍·乡祠编制"
  },

  // 外貌特征
  appearance: {
    height: "174cm",
    weight: "63kg",
    hairColor: "黑间白",
    eyeColor: "深褐",
    skinTone: "偏白",
    bodyType: "清瘦·久立型",
    specialMarks: ["右鬓早白", "喉结下有细小环痕（誓印遗痕）"],
    clothingStyle: "素灰祭袍与深色儒巾，常携折叠木诏与小铜铃"
  },

  // 性格特质
  personality: {
    coreTraits: ["审慎", "克制", "矛盾", "怜悯"],
    values: ["礼法", "清誉", "守护弱者"],
    beliefs: ["礼能安人心", "救人需在制度内求解"],
    fears: ["私赦牵连乡众", "被祭司议会问罪"],
    desires: ["恢复乡祠公信力", "让‘赦缚礼’真正救人"],
    weaknesses: ["优柔寡断", "过度在意名声"],
    strengths: ["仪式学通达", "言辞安抚", "稳场能力强"]
  },

  // 背景故事
  background: {
    birthplace: "白泥村（人域·南环水网）",
    family: "书香小户，妻亡早；一侄在县学读书",
    childhood: "在祖灵续籍台旁长大，随祖父学礼记与刻印",
    education: "乡学→县学助教→被荐任乡祭；曾赴天域环典石经塔短期进修",
    importantEvents: [
      "25岁：接任乡祭，主持首次‘续籍赦’成功赢口碑",
      "33岁：一次‘赦缚礼’失败致当事人转押县祭坛，自责成疾",
      "41岁：被迫配合‘黑籍配额’名单，心存疑虑却签押",
      "44岁：三环亭听证上被林岚当众追问旧案流程缺陷，声誉受损"
    ],
    trauma: ["赦缚失败个案留下噩梦", "被迫签押黑籍名单的耻感"],
    achievements: ["修复乡祠仪程并简化流程，减少误判时延", "在小疫年组织祈链与物资分配，稳住乡社"]
  },

  // 能力技能
  abilities: {
    professionalSkills: ["礼仪设计与执行", "誓印校核", "乡社调解", "碑刻与拓印"],
    specialTalents: ["以声律稳心（钟磬节奏调息）", "能从誓词细节分辨真假"],
    languages: ["通域语", "人域乡言", "天域官音（礼仪口）"],
    learningAbility: "读写强、记诵力佳，善归纳流程",
    socialSkills: "安抚群情与权衡多方诉求",
    practicalSkills: ["小范围赦缚礼", "刻印与修谱", "夜间守灵与仪式净场"]
  },

  // 人际关系
  relationships: {
    family: [
      { name: "温礼", relationship: "叔侄", description: "县学生，常替他查典", importance: "medium" }
    ],
    friends: [
      { name: "赵绢师", relationship: "旧识", description: "柳链集老质检师，常请其为工伤者作安抚礼", importance: "medium" }
    ],
    lovers: [],
    enemies: [
      { name: "何舫", relationship: "对立/警惕", description: "不齿其操纵物价与人心", importance: "medium" }
    ],
    mentors: [
      { name: "陆瑾", relationship: "上级/授命者", description: "县缚司；多次以‘上意’压其立场", importance: "high" }
    ],
    subordinates: [
      { name: "祠役两名", relationship: "主仆", description: "负责净场与钟鼓", importance: "low" }
    ],
    socialCircle: ["乡老会", "县学讲习", "乡社义庄"]
  },

  // 生活状况
  lifestyle: {
    residence: "白泥村乡祠后院小屋",
    economicStatus: "清贫（靠供奉与讲习微薄收入）",
    dailyRoutine: "晨课诵经→查谱修印→接待乡众求礼→黄昏净场→夜记礼案",
    hobbies: ["拓经", "修谱", "听河声定节"],
    foodPreferences: ["素食为主", "粥与腌菜", "偶尔鱼汤"],
    entertainment: ["庙会上听评话", "与乡老下棋"]
  },

  // 心理状态
  psychology: {
    mentalHealth: "长期内疚与焦虑并存，遇审问趋避",
    mentalHealthStatus: "fair",
    copingMechanisms: [
      { type: "healthy", strategy: "钟磬调息与写祷", triggers: ["噩梦","群情激动"], effectiveness: 7, frequency: "frequent" },
      { type: "maladaptive", strategy: "拖延决断等待上意", triggers: ["两难案","上级施压"], effectiveness: 3, frequency: "occasional" }
    ],
    emotionalPatterns: [
      { emotion: "羞耻", triggers: ["被质疑旧案","提及黑籍名单"], intensity: 7, duration: "moderate", expression: "回避目光、干咳", impact: "降低行动力" }
    ],
    trauma: [
      { type: "adult", event: "赦缚失败案", age: 33, severity: "severe", status: "unresolved", triggers: ["链枷声","鼓点"], effects: ["噩梦","手抖"], copingMethods: ["钟磬调息","誓文抄写百遍"] }
    ],
    growthNeeds: ["独立于县署的合法缓冲通道", "公开纠错而不株连的制度"],
    cognitivePatterns: [
      { type: "assumption", description: "制度外行动只会害更多人", situations: ["群众请愿","临时断链请求"], impact: "mixed", awareness: "conscious" }
    ],
    stressResponses: [
      {
        stressor: "上级要求配合不当名单",
        physicalResponse: ["喉紧","手抖"],
        emotionalResponse: ["焦虑","自责"],
        behavioralResponse: ["拖延签押","试图改字眼"],
        cognitiveResponse: ["过度权衡后果"],
        timeframe: "1-3日"
      }
    ],
    emotionalIntelligence: {
      selfAwareness: 7, selfRegulation: 6, motivation: 6, empathy: 8, socialSkills: 7,
      strengths: ["安抚与倾听", "礼仪设计"], weaknesses: ["决断慢","惧权威"]
    },
    psychologicalDefenses: ["合理化", "退行（回到仪式细节以逃避选择）"],
    mentalHealthHistory: [
      { date: new Date("2025-01-01"), status: "fair", notes: "冬祭后梦魇频发", triggers: ["鼓点"], improvements: ["晨课与步行"] }
    ]
  },

  // 故事功能
  storyRole: {
    characterType: "supporting",
    characterArc: "守礼司 → 夹层见证者 → 吹哨人",
    conflictRole: "仪式与赦免的守门人/可能的关键证人",
    symbolism: "钟磬=安人心；白鬓=礼之代价",
    readerConnection: "善良而软弱的体制人，令人又急又怜"
  },

  // 特殊设定
  specialSettings: {
    worldBuilding: "裂世九域·法则链纪元",
    culturalBackground: "人域-乡祠/礼制文化（与天域正统礼制相连）",
    historicalContext: "裂世后时代",
    technologyLevel: "链工学-中",
    magicAbilities:
      "法则链：主[命运] 副[因果]；契合度:3；禁忌:[私赦换人情, 改签未备案]；代表术式:[环誓·定分, 续籍·回录, 赦缚·解环]；代价: 命线磨损与早生白发，过度施礼后喉痛失声",
    culturalIdentity: {
      primaryCulture: "人域-乡祠文化",
      subcultures: ["县学讲习","乡老会"],
      culturalValues: ["礼让","清誉","稳定"],
      culturalConflicts: ["与官署黑箱冲突","与荒域临断观念冲突"],
      assimilationLevel: 7,
      culturalPride: 6,
      traditionalPractices: ["祖灵续籍", "清明修谱"],
      modernAdaptations: ["礼仪流程卡片化，减少误判"]
    },
    religiousBeliefs: {
      religion: "天命信仰",
      denomination: "祭司议会正统（乡祠体系）",
      devotionLevel: 7,
      practices: ["晨课", "链祭日大礼", "赦缚祷"],
      beliefs: ["礼可缓命"],
      doubts: ["当礼与权相悖时应如何"],
      spiritualExperiences: ["夜半河声与钟律同拍，短暂‘无念’"],
      religionInLife: "central"
    },
    languageProfile: {
      nativeLanguage: "通域语",
      fluentLanguages: ["人域乡言", "天域官音（礼仪口）"],
      learningLanguages: [],
      accents: ["礼仪腔，语速缓"],
      dialectVariations: [],
      speechPatterns: [
        { characteristic: "祷文式表达", examples: ["以礼请安", "愿链缓之"], frequency: "often", context: ["仪式","安抚"], origin: "乡祠训练" }
      ],
      languageBarriers: ["与灵域技术术语不熟"],
      communicationPreferences: ["面对面低声沟通","避免公开争执"]
    },
    behaviorPatterns: [
      { category: "professional", behavior: "先净场后发言（控制节奏）", frequency: "situational", triggers: ["群情激动"], context: ["祠堂","祭坛"], development: "降低冲突" },
      { category: "personal", behavior: "夜半抄誓文", frequency: "weekly", triggers: ["自责","噩梦"], context: ["书案"], development: "短期缓解焦虑" }
    ],
    rolePlayingNotes: [
      "Domain: 人域",
      "KeyLocations: 祖灵续籍台 / 县链枷祭坛 / 三环亭 / 白泥村乡祠",
      "F*: F1/F5/F14/F10",
      "口头禅: '以礼缓之' '先净场后言'"
    ]
  },

  // 角色成长轨迹
  characterArc: {
    currentStage: "③→④（夹层与深渊的触发者/证人）",
    developmentGoals: [
      {
        id: "wy-g1",
        category: "professional",
        goal: "建立‘乡祠预审’以替代部分加缚流程",
        motivation: "减少错押与伤亡",
        timeline: "三月",
        obstacles: ["县署抵制","指标压力","礼制缺法源"],
        progress: 20,
        priority: "high"
      }
    ],
    growthMilestones: [
      {
        id: "wy-m1",
        title: "公开承认旧案流程缺陷",
        description: "在三环亭作证，承认黑籍名单存在问题",
        significance: "公信力重建的第一步",
        prerequisites: ["获得乡老会与书院生背书"],
        relatedGoals: ["wy-g1"],
        status: "planned"
      }
    ],
    personalityChanges: [
      {
        id: "wy-p1",
        trait: "决断力",
        oldValue: "拖延等待上意",
        newValue: "在证据充分下先行承担",
        trigger: "林岚以证据还原赦缚失败案",
        timeline: "一月",
        significance: "moderate",
        stability: "developing"
      }
    ],
    skillProgression: [
      {
        skill: "赦缚·解环",
        category: "professional",
        currentLevel: 5,
        targetLevel: 7,
        learningMethod: "与书院/行会协作改良流程",
        timeframe: "两月",
        obstacles: ["嗓音受损","法源欠缺"],
        mentors: ["九环书院礼学士（远程）"]
      }
    ],
    relationshipEvolution: [
      {
        relationshipId: "rel-linlan-witness",
        personName: "林岚",
        evolutionType: "changing",
        previousState: "被质询对象",
        currentState: "关键证人与协作者",
        triggers: ["共同推进‘预审礼’试点"],
        timeline: "持续",
        significance: "为⑤涅槃提供制度支点"
      }
    ],
    internalConflicts: [
      {
        id: "wy-ic1",
        title: "清誉 vs. 救人",
        description: "出面承认失误会毁掉名声，但能救更多人",
        conflictingValues: ["名誉","仁慈"],
        emotionalImpact: "羞耻与解脱并存",
        manifestations: ["夜咳","回避会见"],
        resolutionAttempts: ["书面先道歉","再公开作证"],
        status: "active"
      }
    ],
    externalChallenges: [
      {
        id: "wy-ec1",
        title: "县署打压与祭司议会质询",
        description: "被指越权，面临革职与问罪",
        source: "society",
        difficulty: 8,
        timeframe: "当前两月",
        resources: ["乡老会支持","书院生舆论"],
        strategies: ["制度化试点","联名上书"],
        status: "upcoming"
      }
    ]
  },

  // 互动行为模式
  behaviorProfile: {
    communicationStyle: {
      primaryStyle: "indirect",
      verbalCharacteristics: ["祷文式、缓慢", "以比喻安抚"],
      nonverbalCharacteristics: ["先示意静默", "以钟声定节"],
      listeningStyle: "active",
      feedbackStyle: "以礼语转述与复诵",
      conflictCommunication: "先净场后议，提出折中仪程",
      culturalInfluences: ["乡祠礼仪传统"]
    },
    bodyLanguage: {
      posture: "直立端正",
      gestures: ["合掌扣环礼", "双手平举示停"],
      facialExpressions: ["温和", "眼袋明显"],
      eyeContact: "minimal",
      personalSpace: "normal",
      nervousHabits: ["清喉咙", "抚摸木诏边角"],
      confidenceIndicators: ["仪式中稳定", "声律稳"],
      culturalVariations: ["见长者与亡者皆行相同礼节"]
    },
    decisionMaking: {
      approach: "cautious",
      timeframe: "deliberate",
      informationGathering: "查谱/问证/请示三步",
      riskTolerance: 3,
      influences: ["上意","乡众安危"],
      biases: ["权威偏好","名誉维护"],
      decisionHistory: ["签押过黑籍名单", "在三环亭被迫承认流程缺陷"]
    },
    conflictResponse: {
      primaryStyle: "compromising",
      escalationTriggers: ["公开羞辱","逼其站队"],
      deescalationMethods: ["转为礼仪讨论", "请求过堂测试"],
      emotionalReactions: ["咳嗽/失声"],
      physicalReactions: ["手抖","胸闷"],
      recoveryMethods: ["钟磬调息","步行绕祠"],
      conflictHistory: ["两次化解乡社群体冲突"]
    },
    socialBehavior: {
      socialEnergy: "introverted",
      groupDynamics: "在仪式场域具权威，在政治场域退让",
      socialRoles: ["安抚者","见证人"],
      boundaryManagement: "公私严格区分",
      socialAnxieties: ["被官署点名问责"],
      socialStrengths: ["稳场","共情"],
      networkingStyle: "礼仪网络（乡老-学子-祠役）",
      socialAdaptability: 6
    },
    workStyle: {
      productivity: "morning",
      environment: "quiet",
      organization: "highly_organized",
      taskManagement: "礼案台账与流程卡",
      collaboration: "与乡老/书院生/祠役分工",
      innovation: "在传统内做微改",
      stressManagement: "祷文抄写与步行"
    },
    leadershipStyle: {
      type: "servant",
      strengths: ["稳定情绪","照拂弱者"],
      weaknesses: ["难以拍板","畏惧冲突"],
      motivationMethods: ["以身作则与祷文激励"],
      delegationStyle: "按熟练度分配仪式环节",
      feedbackApproach: "温和面谈",
      decisionInclusivity: "中",
      crisisManagement: "先净场、次安抚、后决策"
    },
    learningStyle: {
      primary: "reading",
      preferences: ["经卷与判例", "碑刻拓本"],
      strengths: ["记诵与归纳"],
      challenges: ["临机创变慢半拍"],
      motivationFactors: ["守护乡众", "修正过错"],
      retentionMethods: ["抄写与诵读"],
      environments: ["祠堂书案", "经塔讲习"],
      adaptability: 6
    }
  }
};
