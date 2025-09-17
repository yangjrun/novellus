const renyu_character_14: Character = {
  id: "char-renyu-liangshouwei-014",
  projectId: "proj-liashi-jiuyu",
  createdAt: new Date("2025-09-17T00:00:00Z"),
  updatedAt: new Date("2025-09-17T00:00:00Z"),

  // 基本信息
  basicInfo: {
    name: "梁守圩",
    alias: ["圩头", "老梁"],
    age: 52,
    gender: "male",
    occupation: "白泥村里正 / 乡老会头",
    socialStatus: "良籍·乡社公职（选任）"
  },

  // 外貌特征
  appearance: {
    height: "171cm",
    weight: "68kg",
    hairColor: "花白短发",
    eyeColor: "深褐",
    skinTone: "古铜（常年风晒）",
    bodyType: "结实·劳作型",
    specialMarks: ["右膝旧伤导致微跛", "手背老茧厚", "腰间常系泥色护腰布"],
    clothingStyle: "粗布短褂+系腰护带，雨天披油布蓑衣，脚蹬防滑草靴"
  },

  // 性格特质
  personality: {
    coreTraits: ["稳重", "务实", "护短", "不轻诺", "韧性强"],
    values: ["乡社存续", "公平执行", "人命优先"],
    beliefs: ["先保圩，再谈功", "说到就要做到"],
    fears: ["官令一纸压垮乡社", "洪水夺圩酿人祸"],
    desires: ["把‘乡社预审+事实墙’固化成村规", "建永久圩粮互助仓"],
    weaknesses: ["对外部新术语适应慢", "对城里折中术不耐"],
    strengths: ["组织调度", "折冲两端", "在危机中定场"]
  },

  // 背景故事
  background: {
    birthplace: "白泥村（人域·南环水网）",
    family: "妻周氏，子梁水旺（河工），女梁芷（在乡学）",
    childhood: "自小随父护圩巡堤，十六岁顶替父位成圩丁",
    education: "乡学基础；后来跟温砚学礼、跟薛箴听过‘三案预案’讲习",
    importantEvents: [
      "23岁：洪水夜带圩丁抢堵决口，救下半村田",
      "34岁：组织‘圩粮互助仓’雏形，以劳换粮过荒年",
      "45岁：与中立仓试点‘人货分离避险’在白泥渡口落地",
      "50岁：带头反对‘黑籍配额’下的连坐抓人，促成三环亭听证"
    ],
    trauma: ["早年一次决口冲走两名圩丁，自责多年", "旱情年看见老人以草根充饥"],
    achievements: ["把‘河情—堤情—人情’做成每日三卡", "推动乡社预审礼试点（与温砚）"]
  },

  // 能力技能
  abilities: {
    professionalSkills: ["乡社组织与资源调度", "堤圩巡检与险情处置", "矛盾调解", "危机物资分配"],
    specialTalents: ["看云听水可预判小洪（经验法）", "能让对立双方在一碗热汤前坐下"],
    languages: ["通域语", "人域乡言", "天域官音（事务口）"],
    learningAbility: "实践-清单型；擅把经验固化为‘一句话三动作’",
    socialSkills: "与乡老、祠司、差役都能打交道，守底线不失分寸",
    practicalSkills: ["土势·固岸（简术）", "应急堤袋编扎", "伤口清洗与包扎", "现场分发统筹"]
  },

  // 人际关系
  relationships: {
    family: [
      { name: "周氏", relationship: "夫妻", description: "打理家中与互助仓的账面与分发", importance: "high" },
      { name: "梁水旺", relationship: "父子", description: "河工，汛期外出援堤", importance: "medium" },
      { name: "梁芷", relationship: "父女", description: "乡学学生，帮抄村规", importance: "medium" }
    ],
    friends: [
      { name: "温砚", relationship: "同盟", description: "乡祭/祠司，合作‘乡祠预审’", importance: "high" },
      { name: "白简", relationship: "顾问", description: "把村规写成白话条款", importance: "high" }
    ],
    lovers: [],
    enemies: [
      { name: "何舫", relationship: "制度-利益对立", description: "曾在旱年做空粮价，乡社与其针锋相对", importance: "high" },
      { name: "沈合", relationship: "冲突", description: "学徒工伤赔付多次推诿遭其堵厂门", importance: "medium" }
    ],
    mentors: [
      { name: "老圩头（未名）", relationship: "师傅", description: "传其‘先人后事’圩规", importance: "medium" }
    ],
    subordinates: [
      { name: "圩丁队", relationship: "队头-圩丁", description: "十二人常备；汛期可扩至三十", importance: "high" }
    ],
    socialCircle: ["乡老会", "义庄", "妇女互助队", "中立仓守仓人", "书场志愿者"]
  },

  // 生活状况
  lifestyle: {
    residence: "白泥村圩内砖屋（临近互助仓）",
    economicStatus: "朴素稳当（靠公职补贴与自家小田）",
    dailyRoutine: "破晓巡圩→上午调度与访户→午后处理纠纷→傍晚练沙袋堤→夜里写日清卡",
    hobbies: ["修旧铲", "晒堤草", "收集各地堤样图"],
    foodPreferences: ["热汤面", "腌菜", "河鱼"],
    entertainment: ["庙会看大戏", "与乡老下棋"]
  },

  // 心理状态
  psychology: {
    mentalHealth: "总体稳定；逢汛季警觉升高并伴旧伤痛",
    mentalHealthStatus: "good",
    copingMechanisms: [
      { type: "healthy", strategy: "三卡日清（堤/人/物）", triggers: ["汛期", "封关"], effectiveness: 9, frequency: "frequent" },
      { type: "adaptive", strategy: "以幽默降压", triggers: ["会场对峙"], effectiveness: 6, frequency: "occasional" }
    ],
    emotionalPatterns: [
      { emotion: "焦虑", triggers: ["连日暴雨", "加缚名单"], intensity: 6, duration: "moderate", expression: "步伐快、复述要点", impact: "推动行动但耗体力" }
    ],
    trauma: [
      { type: "adult", event: "决口失人", age: 23, severity: "severe", status: "healing", triggers: ["闷雷", "夜里长潮声"], effects: ["短时失神", "握拳过紧"], copingMethods: ["拉人结队巡堤", "热姜汤与压腿"] }
    ],
    growthNeeds: ["县署备案的‘乡社预审+撤退权’条款", "防汛经费透明与共险金接入"],
    cognitivePatterns: [
      { type: "belief", description: "人命优先", situations: ["冲突", "调度"], impact: "positive", awareness: "conscious" },
      { type: "assumption", description: "城里话多、落地难", situations: ["听证", "政策宣讲"], impact: "mixed", awareness: "conscious" }
    ],
    stressResponses: [
      {
        stressor: "汛期叠加押解/抓人",
        physicalResponse: ["右膝酸痛", "背部紧绷"],
        emotionalResponse: ["恼怒", "沉默"],
        behavioralResponse: ["强行把场切到‘先保人’议题", "安排妇幼先撤"],
        cognitiveResponse: ["排除干扰专注执行"],
        timeframe: "整段事件期"
      }
    ],
    emotionalIntelligence: {
      selfAwareness: 7, selfRegulation: 7, motivation: 8, empathy: 7, socialSkills: 7,
      strengths: ["稳人心", "用最朴素的语言对齐目标"], weaknesses: ["对复杂条款耐心不足"]
    },
    psychologicalDefenses: ["理智化", "幽默化", "升华（把痛转为制度）"],
    mentalHealthHistory: [
      { date: new Date("2025-05-10"), status: "good", notes: "完成‘互助仓’扩容与账面公开榜" }
    ]
  },

  // 故事功能
  storyRole: {
    characterType: "supporting",
    characterArc: "乡社守门人 → 关键证人与组织者 → 制度化合作者",
    conflictRole: "把抽象改革落地到乡里的执行中枢/‘人命优先’的实体化",
    symbolism: "护腰布=把命系在身上；圩粮仓=乡社自救的胃",
    readerConnection: "可靠的‘村口大树’：不漂亮、却能挡风遮雨"
  },

  // 特殊设定
  specialSettings: {
    worldBuilding: "裂世九域·法则链纪元",
    culturalBackground: "人域-乡社/圩治文化（与乡祠/行会/中立仓耦合）",
    historicalContext: "裂世后时代",
    technologyLevel: "链工学-中（土工术实用派）",
    magicAbilities:
      "法则链：主[土] 副[木]；契合度:3；禁忌:[以土锁人, 以圩为名私挟报复]；代表术式:[土势·固岸(稳堤脚), 地契·界定(白线定纷), 田陌·起脊(快速筑脊引水)]; 代价: 腰膝负担加剧与短时反应迟缓，汛季过用后需热敷与静息",
    culturalIdentity: {
      primaryCulture: "人域-乡社文化",
      subcultures: ["圩丁队", "妇女互助队", "义庄"],
      culturalValues: ["守望相助", "公道", "务实"],
      culturalConflicts: ["与官署绩效导向冲突", "与票行逐利导向冲突"],
      assimilationLevel: 7,
      culturalPride: 7,
      traditionalPractices: ["开汛祭圩", "秋后谢圩"],
      modernAdaptations: ["村规白话化上墙", "互助仓账目公开"]
    },
    religiousBeliefs: {
      religion: "源祖/河祠并修（务实派）",
      denomination: "乡祠—圩祠",
      devotionLevel: 5,
      practices: ["汛前小礼", "祭亡名册"],
      beliefs: ["敬水、守土、人命最大"],
      doubts: ["书面神学帮不上堤"],
      spiritualExperiences: ["决口夜似闻‘地声’，带人改位止险"],
      religionInLife: "important"
    },
    languageProfile: {
      nativeLanguage: "人域乡言",
      fluentLanguages: ["通域语", "天域官音（事务）"],
      learningLanguages: [],
      accents: ["乡音厚重、句式短"],
      dialectVariations: [],
      speechPatterns: [
        { characteristic: "三句定事（先保命/再止水/后清账）", examples: ["人先走", "沙袋跟上", "账回头看"], frequency: "often", context: ["现场调度","会商"], origin: "圩治口令" }
      ],
      languageBarriers: ["学术腔与冗长官话"],
      communicationPreferences: ["白话+手指图", "把账上墙"]
    },
    behaviorPatterns: [
      { category: "professional", behavior: "‘三卡日清’（堤情/人情/物情）", frequency: "daily", triggers: ["汛期","封关"], context: ["乡社"], development: "把混乱变成秩序" },
      { category: "personal", behavior: "每晚热敷压腿与静息", frequency: "daily", triggers: ["巡圩归来"], context: ["家中"], development: "缓解旧伤" }
    ],
    rolePlayingNotes: [
      "Domain: 人域",
      "KeyLocations: 白泥村乡祠 / 互助仓 / 圩堤 / 三环亭",
      "F*: F1/F3/F4/F10/F14/F18/F19",
      "口头禅: '先保命' '账回头看'"
    ]
  },

  // 角色成长轨迹
  characterArc: {
    currentStage: "③ 试炼与盟友（乡社执行）→ ④ 深渊（汛期+黑籍冲突）",
    developmentGoals: [
      {
        id: "lsw-g1",
        category: "social",
        goal: "把‘乡社预审+事实墙’写入县内村规通用样本",
        motivation: "让弱村也能自保",
        timeline: "三个月",
        obstacles: ["官署阻力","票行反对","执行成本"],
        progress: 35,
        priority: "high"
      }
    ],
    growthMilestones: [
      {
        id: "lsw-m1",
        title: "首批村规白话样本上墙",
        description: "白泥村率先试行并通过三环亭公开见证",
        significance: "从口号到执行的跨步",
        prerequisites: ["白简与温砚共同修订"],
        relatedGoals: ["lsw-g1"],
        status: "planned"
      }
    ],
    personalityChanges: [
      {
        id: "lsw-p1",
        trait: "对外协作的态度",
        oldValue: "村里自己扛",
        newValue: "与中立仓/行会/书场联合扛",
        trigger: "一次押解与汛情叠加险情",
        timeline: "一月",
        significance: "moderate",
        stability: "developing"
      }
    ],
    skillProgression: [
      {
        skill: "地契·界定（民事纠纷）",
        category: "professional",
        currentLevel: 5,
        targetLevel: 7,
        learningMethod: "请书院与祠司旁听纠纷并复盘",
        timeframe: "两月",
        obstacles: ["法源解释差异"],
        mentors: ["温砚","白简"]
      }
    ],
    relationshipEvolution: [
      {
        relationshipId: "rel-wenyan-alliance",
        personName: "温砚",
        evolutionType: "strengthening",
        previousState: "乡里衔接",
        currentState: "制度合作者",
        triggers: ["预审礼与村规上墙联动"],
        timeline: "持续",
        significance: "形成制度闭环"
      }
    ],
    internalConflicts: [
      {
        id: "lsw-ic1",
        title: "守土 vs. 求援",
        description: "靠自己撑面子还是向外求援更保人",
        conflictingValues: ["自尊","务实"],
        emotionalImpact: "短暂自责与愤怒",
        manifestations: ["沉默寡言","夜巡加倍"],
        resolutionAttempts: ["设立外援联系人清单","演练撤退方案"],
        status: "active"
      }
    ],
    externalChallenges: [
      {
        id: "lsw-ec1",
        title: "汛情叠加加缚名单冲突",
        description: "同一晚既要护堤又要护人，官署与票行逼签",
        source: "society",
        difficulty: 8,
        timeframe: "汛季核心期",
        resources: ["互助仓粮", "圩丁队", "中立仓避险点"],
        strategies: ["人货分离", "第三方见证", "事实墙即时公示"],
        status: "upcoming"
      }
    ]
  },

  // 互动行为模式
  behaviorProfile: {
    communicationStyle: {
      primaryStyle: "assertive",
      verbalCharacteristics: ["白话短句", "结论先行", "不空话"],
      nonverbalCharacteristics: ["手掌下压示‘稳住’", "指图讲解"],
      listeningStyle: "active",
      feedbackStyle: "三点式（先保命/再执行/后追账）",
      conflictCommunication: "请见证→划安全线→再谈责",
      culturalInfluences: ["乡社/圩治口令文化"]
    },
    bodyLanguage: {
      posture: "站姿稳、微跛但不失力",
      gestures: ["两指并拢点图", "掌心向外示停"],
      facialExpressions: ["沉稳", "眉目常皱"],
      eyeContact: "moderate",
      personalSpace: "normal",
      nervousHabits: ["按压右膝", "挠后颈"],
      confidenceIndicators: ["语速稳", "停顿准"],
      culturalVariations: ["对祠司与长者礼数周全，对城里客人少寒暄多实话"]
    },
    decisionMaking: {
      approach: "analytical",
      timeframe: "moderate",
      informationGathering: "三卡（堤/人/物）+现场口述",
      riskTolerance: 4,
      influences: ["人命优先","乡社存续"],
      biases: ["对城里方案天然怀疑"],
      decisionHistory: ["多次平衡押解与护堤冲突","建立互助仓公开榜"]
    },
    conflictResponse: {
      primaryStyle: "collaborating",
      escalationTriggers: ["人命被忽视", "强拉人走"],
      deescalationMethods: ["请祠司/书场见证", "划定‘安全线’"],
      emotionalReactions: ["短怒后压住"],
      physicalReactions: ["右膝疼", "肩颈紧"],
      recoveryMethods: ["热敷", "慢走巡圩"],
      conflictHistory: ["多起村事化解转听证"]
    },
    socialBehavior: {
      socialEnergy: "ambivert",
      groupDynamics: "会场‘压舱石’，能让众人按点行动",
      socialRoles: ["里正", "队头", "分发官"],
      boundaryManagement: "公私分明（亲友也按规）",
      socialAnxieties: ["被迫在城里大场合长演说"],
      socialStrengths: ["稳场", "把复杂话说清"],
      networkingStyle: "乡社-祠司-行会-中立仓四角网络",
      socialAdaptability: 7
    },
    workStyle: {
      productivity: "morning",
      environment: "bustling",
      organization: "highly_organized",
      taskManagement: "口令卡+白板+上墙公示",
      collaboration: "分工明确（圩丁/妇幼/老人）",
      innovation: "把经验固化为村规与动作",
      stressManagement: "热敷+慢走+分段睡"
    },
    leadershipStyle: {
      type: "servant",
      strengths: ["以身作则", "稳情绪", "公平分配"],
      weaknesses: ["对外演讲弱", "政策文字转换慢"],
      motivationMethods: ["公开表扬‘上墙’", "分发优先权奖励"],
      delegationStyle: "按熟练度派位（沙袋/巡堤/分发）",
      feedbackApproach: "当面三句定事与次日复盘",
      decisionInclusivity: "中高",
      crisisManagement: "人命优先、划安全线、请见证"
    },
    learningStyle: {
      primary: "kinesthetic",
      preferences: ["看图说话", "现场演练"],
      strengths: ["动作记忆强", "组织调度"],
      challenges: ["抽象条款冗长"],
      motivationFactors: ["护乡社", "护家人"],
      retentionMethods: ["口令卡", "上墙图"],
      environments: ["圩堤", "乡祠", "三环亭小间"],
      adaptability: 7
    }
  }
};
