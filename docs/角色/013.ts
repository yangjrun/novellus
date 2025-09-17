const renyu_character_13: Character = {
  id: "char-renyu-baijian-013",
  projectId: "proj-liashi-jiuyu",
  createdAt: new Date("2025-09-17T00:00:00Z"),
  updatedAt: new Date("2025-09-17T00:00:00Z"),

  // 基本信息
  basicInfo: {
    name: "白简",
    alias: ["半账先生", "老账房", "白编"],
    age: 58,
    gender: "male",
    occupation: "行会老账房 / 《风骨小报》兼职编辑 / 民间仲裁顾问",
    socialStatus: "良籍·行会长老（非编制顾问）"
  },

  // 外貌特征
  appearance: {
    height: "170cm",
    weight: "62kg",
    hairColor: "花白（发量稀）",
    eyeColor: "深褐",
    skinTone: "偏黄",
    bodyType: "清瘦·久坐型",
    specialMarks: [
      "右手食指与中指常年墨痕",
      "胸口随身小木牌（刻：半账留余）",
      "久咳导致喉间低哑"
    ],
    clothingStyle: "素色直裰+夹背心口袋多，袖藏细算尺与封蜡小盒，出席听证披旧呢大氅"
  },

  // 性格特质
  personality: {
    coreTraits: ["温和", "谨严", "抑制", "机敏", "以退为进"],
    values: ["信誉", "可执行的公平", "留余地"],
    beliefs: ["制度要让普通人用得起", "赢也要留人路"],
    fears: ["年轻人走极端两败俱伤", "被权力借壳利用"],
    desires: ["把‘半账留余’写成行会与三环亭共用的仲裁准则", "建一本人人读得懂的《小环账例》"],
    weaknesses: ["体弱多咳", "对黑箱妥协度过高时显得保守"],
    strengths: ["复盘与取证", "把复杂条款翻译成白话", "调停对立双方"]
  },

  // 背景故事
  background: {
    birthplace: "九埠市水巷旧里（人域）",
    family: "寡居；一侄女在码头做牙人",
    childhood: "生于小账房，十岁能独记流水，十五起随师巡各码头做清账",
    education: "行会账房正宗出身；自修法度馆公开课‘合同与风险’",
    importantEvents: [
      "25岁：提出‘半账留余’操作法（纠纷中双方各退一步并留执行路）",
      "33岁：参与首起跨域仲裁，成功用三方见证化解争端",
      "45岁：受报馆邀写‘白话合同课’，广受底层欢迎",
      "54岁：亲历封关挤兑，开始推动‘共险金+中立仓’组合"
    ],
    trauma: ["早年一次清账被打断肋骨，目睹暴力夺账本", "挤兑夜见底层母子跪求而无力回天"],
    achievements: [
      "《半账三术》小册（口口相传的实用合同读本）",
      "行会内首批‘镜账’试点倡议人",
      "三环亭‘事实墙’早期方法顾问"
    ]
  },

  // 能力技能
  abilities: {
    professionalSkills: [
      "复式账与证据链构建",
      "合同白话化与条款缝补",
      "民间仲裁与调停",
      "风险分摊与共险设计"
    ],
    specialTalents: [
      "三问定调（事实/风险/退路）",
      "一眼看穿账目里‘假饱真空’的现金流错觉"
    ],
    languages: ["通域语", "人域乡言", "天域官音（礼仪/法度口）"],
    learningAbility: "抽象-转译-示例三步走，擅把高深法度落到小民可用",
    socialSkills: "柔性说服强，能让极端立场的人坐下读条款",
    practicalSkills: ["简易审计", "事实墙证据编目", "听证会纪要与要点卡制作"]
  },

  // 人际关系
  relationships: {
    family: [
      { name: "白荟", relationship: "叔侄", description: "码头牙人，常给他带一线信息", importance: "medium" }
    ],
    friends: [
      { name: "薛箴", relationship: "亦师亦友", description: "‘共险金’与‘中立仓’倡议同盟", importance: "high" },
      { name: "温砚", relationship: "同道", description: "礼制改革的温和派盟友", importance: "medium" }
    ],
    lovers: [],
    enemies: [
      { name: "何舫", relationship: "价值冲突", description: "对白的‘留余’不以为然，多次唱反调", importance: "high" }
    ],
    mentors: [
      { name: "旧会首（未名）", relationship: "启蒙师", description: "授以‘账不欺人，人亦莫欺账’", importance: "medium" }
    ],
    subordinates: [
      { name: "报馆小编两名", relationship: "编辑-学徒", description: "协助整理‘白话合同课’与事实墙手册", importance: "low" }
    ],
    socialCircle: ["行会长老圈", "报馆编辑圈", "三环亭志愿者", "乡祠礼学士"]
  },

  // 生活状况
  lifestyle: {
    residence: "九埠市水巷旧宅（书架占满半屋）",
    economicStatus: "清贫而稳定（稿费+顾问金）",
    dailyRoutine: "清晨散步理气→上午收案做笔记→午后会客或旁听→夜里修订白话条款",
    hobbies: ["修旧账本", "收集各地合同范本", "写边栏批注"],
    foodPreferences: ["清粥小菜", "姜茶润喉"],
    entertainment: ["书场听公案", "与小辈对练‘一题三解’"]
  },

  // 心理状态 (增强版)
  psychology: {
    mentalHealth: "慢性咳喘与轻度失眠；情绪总体稳定",
    mentalHealthStatus: "good",
    copingMechanisms: [
      { type: "healthy", strategy: "散步与热姜茶、分段工作法", triggers: ["咳喘","久坐疲劳"], effectiveness: 7, frequency: "frequent" },
      { type: "adaptive", strategy: "以幽默化解尖锐冲突", triggers: ["会场对骂","被逼站队"], effectiveness: 7, frequency: "occasional" }
    ],
    emotionalPatterns: [
      { emotion: "愧疚（低频）", triggers: ["挤兑旧案回想"], intensity: 4, duration: "brief", expression: "长叹后转入写作", impact: "推动制度化改良" }
    ],
    trauma: [
      {
        type: "adult",
        event: "账房被打砸与夺账本",
        age: 27,
        severity: "moderate",
        status: "healing",
        triggers: ["木柜倒地声","纸灰味"],
        effects: ["短暂停顿","握笔过紧"],
        copingMethods: ["把关键账面镜像备份","公开透明以自保"]
      }
    ],
    growthNeeds: ["官方备案的半账仲裁准则", "青年代际传承团队"],
    cognitivePatterns: [
      { type: "belief", description: "留余地是长久之道", situations: ["仲裁","谈判"], impact: "positive", awareness: "conscious" },
      { type: "heuristic", description: "三问定调（事实/风险/退路）", situations: ["决策","听证"], impact: "positive", awareness: "conscious" }
    ],
    stressResponses: [
      {
        stressor: "被迫站队/极端舆论裹挟",
        physicalResponse: ["咳嗽加重","胸口闷"],
        emotionalResponse: ["焦虑","悲悯"],
        behavioralResponse: ["暂缓发声","改写白话条款"],
        cognitiveResponse: ["寻找折中执行路径"],
        timeframe: "1-3日"
      }
    ],
    emotionalIntelligence: {
      selfAwareness: 8, selfRegulation: 7, motivation: 7, empathy: 8, socialSkills: 8,
      strengths: ["把复杂简化", "稳住场面"], weaknesses: ["被指保守","对黑箱容忍度偏高"]
    },
    psychologicalDefenses: ["理智化", "幽默化"],
    mentalHealthHistory: [
      { date: new Date("2025-04-01"), status: "good", notes: "完成《小环账例》初稿二十条" }
    ]
  },

  // 故事功能
  storyRole: {
    characterType: "supporting",
    characterArc: "温和改革派导师 → 关键见证人 → 制度共创者",
    conflictRole: "条款翻译器/仲裁与共险金的制度推手",
    symbolism: "小木牌‘半账留余’=给彼此一道可走的路；旧账本=集体记忆",
    readerConnection: "温和但有锋芒的老人，像一把不会伤人的钝刀，慢慢把结切开"
  },

  // 特殊设定 (增强版)
  specialSettings: {
    worldBuilding: "裂世九域·法则链纪元",
    culturalBackground: "人域-行会/书场交汇文化（实务与传播并用）",
    historicalContext: "裂世后时代",
    technologyLevel: "链工学-中",
    magicAbilities:
      "法则链：主[因果] 副[风]；契合度:3；禁忌:[以话术遮蔽关键事实, 用因果锁压迫弱者签不平条款]；代表术式:[因果·平衡(对冲双方风险), 账印·见证(在场印与镜账联动), 风言·止谣(以事实清单降低舆潮)]；代价: 长时演算致胸闷与咳嗽复发，过用‘止谣’后短时失声",
    culturalIdentity: {
      primaryCulture: "人域-行会文化",
      subcultures: ["报馆编辑圈", "三环亭志愿网络"],
      culturalValues: ["信誉","留余","可执行"],
      culturalConflicts: ["与票行逐利派冲突", "与官署‘数据好看’倾向冲突"],
      assimilationLevel: 8,
      culturalPride: 7,
      traditionalPractices: ["开账前滴蜡印‘不欺账’"],
      modernAdaptations: ["白话合同模板", "事实墙证据编目法"]
    },
    religiousBeliefs: {
      religion: "天命信仰（实用/温和派）",
      denomination: "行会祠",
      devotionLevel: 4,
      practices: ["开账小礼", "祭亡名册默念"],
      beliefs: ["善意要能落地，否则是空话"],
      doubts: ["过度神秘化无助于民生"],
      spiritualExperiences: ["夜半伏案时‘一线风’拂页，灵感成章"],
      religionInLife: "minimal"
    },
    languageProfile: {
      nativeLanguage: "通域语",
      fluentLanguages: ["人域乡言","天域官音（礼仪/法度口）"],
      learningLanguages: [],
      accents: ["平缓账房腔（短句、停顿多）"],
      dialectVariations: [],
      speechPatterns: [
        { characteristic: "白话化/比兴多", examples: ["这条款像窄桥，要让人能过", "赢也要留人路"], frequency: "often", context: ["仲裁","教导"], origin: "账房与书场双重训练" }
      ],
      languageBarriers: ["过度学术化法条不耐"],
      communicationPreferences: ["清单+范本+案例一页纸"]
    },
    behaviorPatterns: [
      { category: "professional", behavior: "三问定调（事实/风险/退路）后再提方案", frequency: "situational", triggers: ["仲裁/听证"], context: ["三环亭","行会会馆"], development: "冲突降级" },
      { category: "personal", behavior: "晨起慢走、记‘一日三善’", frequency: "daily", triggers: ["失眠","胸闷"], context: ["水巷"], development: "情绪平稳" }
    ],
    rolePlayingNotes: [
      "Domain: 人域",
      "KeyLocations: 行会会馆 / 三环亭 / 九埠市 / 报馆",
      "F*: F5/F12/F15(灰度低容忍)/F17/F19/F20",
      "口头禅: '赢也要留人路' '先把话讲明白'"
    ]
  },

  // 角色成长轨迹 (新增)
  characterArc: {
    currentStage: "②→③（跨门槛后的试炼期导师/枢纽）",
    developmentGoals: [
      {
        id: "bj-g1",
        category: "professional",
        goal: "将‘半账仲裁准则’写入三环亭正式流程并获县署备案",
        motivation: "减少暴力成本，让弱者也能用规程自保",
        timeline: "三个月",
        obstacles: ["官署面子工程","票行阻力","流程冗长"],
        progress: 45,
        priority: "high"
      }
    ],
    growthMilestones: [
      {
        id: "bj-m1",
        title: "《小环账例》发布（白话二十条）",
        description: "在报馆连载并于行会免费发放，配‘事实墙’操作手册",
        significance: "把理念落成工具",
        prerequisites: ["样稿通过审读","经费赞助"],
        relatedGoals: ["bj-g1"],
        status: "planned"
      }
    ],
    personalityChanges: [
      {
        id: "bj-p1",
        trait: "对‘灰度’的容忍",
        oldValue: "必要时容忍灰度换时间",
        newValue: "以公开与见证削减灰度空间",
        trigger: "挤兑夜的无力感与年轻人受伤",
        timeline: "一季",
        significance: "moderate",
        stability: "stable"
      }
    ],
    skillProgression: [
      {
        skill: "账印·见证",
        category: "professional",
        currentLevel: 6,
        targetLevel: 7,
        learningMethod: "与链算所/乡祠合作完善镜账与在场印",
        timeframe: "两月",
        obstacles: ["体力不支","设备不足"],
        mentors: ["链算所讲习导师"]
      }
    ],
    relationshipEvolution: [
      {
        relationshipId: "rel-linlan-mentor",
        personName: "林岚",
        evolutionType: "strengthening",
        previousState: "温和导师",
        currentState: "制度共创伙伴",
        triggers: ["事实墙听证与半账准则并行试点"],
        timeline: "持续",
        significance: "为⑤涅槃夯实制度底座"
      }
    ],
    internalConflicts: [
      {
        id: "bj-ic1",
        title: "留余 vs. 见血",
        description: "当对手不守底线时，是否该以硬碰硬",
        conflictingValues: ["温和改革","强硬正义"],
        emotionalImpact: "失眠与咳嗽加重",
        manifestations: ["延迟表态","改写条款寻找替代路"],
        resolutionAttempts: ["引入第三方见证","设置硬阈值条款"],
        status: "active"
      }
    ],
    externalChallenges: [
      {
        id: "bj-ec1",
        title: "样板化与真改良的拉锯",
        description: "官署要面子、票行要利润、群众要结果",
        source: "society",
        difficulty: 7,
        timeframe: "两月",
        resources: ["报馆平台","行会网络","乡祠礼学士"],
        strategies: ["小步快跑试点","公布成功样例","培养青年讲解员"],
        status: "upcoming"
      }
    ]
  },

  // 互动行为模式 (新增)
  behaviorProfile: {
    communicationStyle: {
      primaryStyle: "assertive",
      verbalCharacteristics: ["白话短句", "比喻与类比", "结论前置"],
      nonverbalCharacteristics: ["举笔点要", "掌心向下示‘稳’"],
      listeningStyle: "active",
      feedbackStyle: "三问定调（事实/风险/退路）回馈",
      conflictCommunication: "请见证→摆清单→定时窗",
      culturalInfluences: ["行会谈判礼", "书场讲解风"]
    },
    bodyLanguage: {
      posture: "坐姿略前倾",
      gestures: ["两指并拢点条款", "轻敲案几定节奏"],
      facialExpressions: ["和缓","偶带疲色"],
      eyeContact: "moderate",
      personalSpace: "normal",
      nervousHabits: ["清嗓", "揉喉间小木牌"],
      confidenceIndicators: ["语速稳","停顿恰当"],
      culturalVariations: ["对长者与祭司行简礼，对底层放慢语速"]
    },
    decisionMaking: {
      approach: "analytical",
      timeframe: "moderate",
      informationGathering: "账证/证词/条款三位一体",
      riskTolerance: 4,
      influences: ["公众利益","可执行性"],
      biases: ["温和偏好"],
      decisionHistory: ["推动共险金与中立仓","编写白话条款"]
    },
    conflictResponse: {
      primaryStyle: "collaborating",
      escalationTriggers: ["耍赖毁约","暴力夺账"],
      deescalationMethods: ["引入第三方见证","设置软硬阈值"],
      emotionalReactions: ["轻叹后转入逻辑"],
      physicalReactions: ["短咳","按喉"],
      recoveryMethods: ["姜茶", "散步"],
      conflictHistory: ["多起纠纷化解转仲裁"]
    },
    socialBehavior: {
      socialEnergy: "ambivert",
      groupDynamics: "会场里的稳定器",
      socialRoles: ["讲解员","仲裁者","抚锋芒者"],
      boundaryManagement: "公私分明",
      socialAnxieties: ["被迫公开站队极端派"],
      socialStrengths: ["翻译复杂","稳情绪"],
      networkingStyle: "行会-报馆-乡祠三角",
      socialAdaptability: 8
    },
    workStyle: {
      productivity: "morning",
      environment: "quiet",
      organization: "highly_organized",
      taskManagement: "要点卡/范本/清单",
      collaboration: "小团队伴读与修订",
      innovation: "把理念落为工具（模板/清单/样本）",
      stressManagement: "分段工作+散步"
    },
    leadershipStyle: {
      type: "servant",
      strengths: ["教学","扶持新人","温和稳定"],
      weaknesses: ["推进速度慢","容易被贴保守标签"],
      motivationMethods: ["小成就反馈","署名与致谢"],
      delegationStyle: "按能力分配条款章节",
      feedbackApproach: "一页纸红蓝批注",
      decisionInclusivity: "中高",
      crisisManagement: "先稳情绪→再稳事实→后稳方案"
    },
    learningStyle: {
      primary: "reading",
      preferences: ["案例与范本", "边做边讲"],
      strengths: ["抽象与转译"],
      challenges: ["高强度连续会务"],
      motivationFactors: ["让普通人也能用规则自保"],
      retentionMethods: ["卡片化与口诀化"],
      environments: ["会馆书房","三环亭小间"],
      adaptability: 7
    }
  }
};
