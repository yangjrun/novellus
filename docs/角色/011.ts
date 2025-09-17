const renyu_character_11: Character = {
  id: "char-renyu-shenhe-011",
  projectId: "proj-liashi-jiuyu",
  createdAt: new Date("2025-09-17T00:00:00Z"),
  updatedAt: new Date("2025-09-17T00:00:00Z"),

  // 基本信息
  basicInfo: {
    name: "沈合",
    alias: ["头工", "火梭"],
    age: 39,
    gender: "male",
    occupation: "柳链集织局头工/产线督头",
    socialStatus: "良籍·行会挂名（与票行有债权关系）"
  },

  // 外貌特征
  appearance: {
    height: "177cm",
    weight: "73kg",
    hairColor: "乌黑（油亮后梳）",
    eyeColor: "深褐",
    skinTone: "小麦偏暗",
    bodyType: "结实·久站型",
    specialMarks: [
      "两掌虎口厚茧",
      "右前臂有烫伤大片旧痕",
      "左耳佩细铁环（工头识别）"
    ],
    clothingStyle: "深灰短褂配护腕与皮围裙，腰挂铜哨与点工牌"
  },

  // 性格特质
  personality: {
    coreTraits: ["强势", "功利", "现实主义", "护短（对自己人）"],
    values: ["产量", "效率", "服从"],
    beliefs: ["好人管不住机台", "规矩要跟产量走"],
    fears: ["停机风潮", "被行会撤换头工牌"],
    desires: ["拿下新一线的承包权", "把‘空白链契’固化成行规"],
    weaknesses: ["轻视安全", "对舆论与证据意识薄弱"],
    strengths: ["现场压场", "机台节拍把握", "人手调度与威慑"]
  },

  // 背景故事
  background: {
    birthplace: "柳链集后街（人域）",
    family: "妻刘氏经营小饭摊，一子一女在乡学",
    childhood: "贫巷长大，早年做机夫，靠肯吃苦爬到头工",
    education: "行会简训与师徒制；识字能看产线账，不通条文细节",
    importantEvents: [
      "20岁：夜班救火护住主机，升小工头",
      "28岁：在行会比产中夺标，转正为头工",
      "34岁：与票行达成预支协议，产量压条款绑定学徒",
      "37岁：推动‘空白链契’，由此与学徒圈长期对立"
    ],
    trauma: ["早年失足坠台致同伴手指截断，内心自责但外化为强硬", "一次停机维权导致罚款与差点撤牌"],
    achievements: ["改良‘双梭并行’节拍法，产量曾提升一成半", "建立‘红黑牌’出勤考核（高压版本）"]
  },

  // 能力技能
  abilities: {
    professionalSkills: [
      "产线节拍控制",
      "工位分配与人手调度",
      "设备应急修理（轻度）",
      "粗放型成本压降"
    ],
    specialTalents: [
      "听梭辨速（凭机声判断纬纱张力）",
      "以小利与威慑维持队伍稳定"
    ],
    languages: ["通域语", "人域乡言", "灵域匠话（听得懂些）"],
    learningAbility: "经验-模仿型，偏现场复盘而非书面学习",
    socialSkills: "对下强硬，对上会说产量话；会用小恩小惠笼络骨干",
    practicalSkills: [
      "火梭·急停（以火链定住主轴短停）",
      "值夜巡检",
      "工伤现场止血与包扎（粗糙）"
    ]
  },

  // 人际关系
  relationships: {
    family: [
      { name: "刘氏", relationship: "夫妻", description: "在厂门口经营饭摊，打点学徒小恩小惠", importance: "medium" },
      { name: "沈杉/沈柏", relationship: "父子/父女", description: "就读乡学，对父亲强硬作风敬畏", importance: "low" }
    ],
    friends: [
      { name: "何舫", relationship: "利益同盟", description: "票行账吏长，提供预支；以账压人", importance: "high" }
    ],
    lovers: [],
    enemies: [
      { name: "苏杳", relationship: "对立", description: "学徒互助小组组织者，多次抗拒空白链契", importance: "high" },
      { name: "林岚", relationship: "对立", description: "在三环亭质疑其安全与契约问题", importance: "high" }
    ],
    mentors: [
      { name: "赵绢师", relationship: "旧上级/亦敌亦友", description: "曾教其质检常识，后分道扬镳", importance: "medium" }
    ],
    subordinates: [
      { name: "监工二人", relationship: "上级-下属", description: "专盯迟到与停机，执行‘红黑牌’", importance: "medium" }
    ],
    socialCircle: ["行会头领圈", "票行茶局", "设备修理小作坊老板"]
  },

  // 生活状况
  lifestyle: {
    residence: "柳链集后街两层小院（靠近织局）",
    economicStatus: "小富（现金流不稳，负债与回扣并存）",
    dailyRoutine: "卯时巡机→辰时点名→午后追产量→黄昏核工分→夜间与票行/行会碰头",
    hobbies: ["摆弄火梭", "收集老机件", "掼石锁比力气"],
    foodPreferences: ["重油重盐", "烈酒", "下酒小菜"],
    entertainment: ["站工棚看戏", "茶摊吹牛比产"]
  },

  // 心理状态 (增强版)
  psychology: {
    mentalHealth: "功能尚可，慢性焦虑与愤怒易积压",
    mentalHealthStatus: "fair",
    copingMechanisms: [
      { type: "unhealthy", strategy: "以酒压情绪", triggers: ["停机维权","舆论围堵"], effectiveness: 3, frequency: "occasional" },
      { type: "adaptive", strategy: "深夜巡机独行", triggers: ["设备连故障","上层压产"], effectiveness: 6, frequency: "frequent" }
    ],
    emotionalPatterns: [
      { emotion: "恼怒", triggers: ["被质疑","停机"], intensity: 7, duration: "brief", expression: "拍桌、吹哨、点名罚工", impact: "激化矛盾" }
    ],
    trauma: [
      { type: "adult", event: "坠台致同伴截指", age: 23, severity: "severe", status: "healing", triggers: ["金属碰撞巨响","血腥味"], effects: ["短时僵直","手心冒汗"], copingMethods: ["回避讨论安全话题","用‘强硬’掩饰内疚"] }
    ],
    growthNeeds: ["安全与产量的替代性考核", "合规合同模板与第三方见证"],
    cognitivePatterns: [
      { type: "assumption", description: "工人给足钱就不闹", situations: ["停机谈判"], impact: "negative", awareness: "subconscious" },
      { type: "bias", description: "把维权者视为带头闹事", situations: ["抽检","点名"], impact: "negative", awareness: "conscious" }
    ],
    stressResponses: [
      {
        stressor: "封关+原料断供+舆情",
        physicalResponse: ["胃酸","耳鸣"],
        emotionalResponse: ["烦躁","易怒"],
        behavioralResponse: ["延长工时","私改安全开关"],
        cognitiveResponse: ["短视决策","否认风险"],
        timeframe: "整段封关期"
      }
    ],
    emotionalIntelligence: {
      selfAwareness: 4, selfRegulation: 5, motivation: 7, empathy: 3, socialSkills: 6,
      strengths: ["压场与执行"], weaknesses: ["倾听不足","对制度化改良抗拒"]
    },
    psychologicalDefenses: ["否认", "投射", "合理化"],
    mentalHealthHistory: [
      { date: new Date("2024-09-01"), status: "fair", notes: "封关停机后与行会冲突，情绪不稳" }
    ]
  },

  // 故事功能
  storyRole: {
    characterType: "antagonist",
    characterArc: "高压头工 → 舆论反噬的代罪羊/或觉醒合作者（可选）",
    conflictRole: "空白链契与高压产线的执行枢纽",
    symbolism: "火梭=以速度压住一切；红黑牌=粗暴的秩序",
    readerConnection: "令人厌恶又真实的中层夹心：既压人也被压"
  },

  // 特殊设定 (增强版)
  specialSettings: {
    worldBuilding: "裂世九域·法则链纪元",
    culturalBackground: "人域-工坊/行会边缘文化（与票行资金链绑定）",
    historicalContext: "裂世后时代",
    technologyLevel: "链工学-中",
    magicAbilities:
      "法则链：主[金] 副[火]；契合度:3；禁忌:[空白链契, 伪印, 强制超时]；代表术式:[机势·合拍(以金链稳机节拍), 火梭·急停(以火链刹轴), 印槽·偷换(灰度替印)]; 代价: 长期耳鸣与手臂灼痛，过用后出现‘听阈错判’导致误判机况",
    culturalIdentity: {
      primaryCulture: "人域-工坊文化",
      subcultures: ["头工小圈", "票行茶局"],
      culturalValues: ["产量","纪律","忠诚"],
      culturalConflicts: ["与学徒互助/透明合同冲突", "与乡祠安全礼制冲突"],
      assimilationLevel: 7,
      culturalPride: 5,
      traditionalPractices: ["开机前敲三下机座当‘醒梭礼’"],
      modernAdaptations: ["‘红黑牌’考核与点工牌刷印"]
    },
    religiousBeliefs: {
      religion: "源祖传说（工具祖灵）",
      denomination: "工棚私祠",
      devotionLevel: 2,
      practices: ["开机小礼"],
      beliefs: ["工具有性子，顺了就快"],
      doubts: ["祭司/书生管不了机台"],
      spiritualExperiences: ["夜里独修机时似闻‘金声’，以为祖灵赐速"],
      religionInLife: "minimal"
    },
    languageProfile: {
      nativeLanguage: "通域语",
      fluentLanguages: ["人域乡言","灵域匠话（入门）"],
      learningLanguages: [],
      accents: ["工棚短句腔（命令式）"],
      dialectVariations: [],
      speechPatterns: [
        { characteristic: "口令化+比粗话", examples: ["加一拍", "闭嘴干活", "谁敢停机"], frequency: "often", context: ["车间","点名"], origin: "工棚文化" }
      ],
      languageBarriers: ["官话礼仪与法律术语不熟"],
      communicationPreferences: ["当面喝令", "白板产量曲线"]
    },
    behaviorPatterns: [
      { category: "professional", behavior: "红黑牌出勤与迟到双重罚", frequency: "daily", triggers: ["迟到","停机"], context: ["产线"], development: "提高出勤但加剧矛盾" },
      { category: "personal", behavior: "夜巡独坐机座抽闷烟", frequency: "weekly", triggers: ["舆情升温"], context: ["空车间"], development: "短暂降压" }
    ],
    rolePlayingNotes: [
      "Domain: 人域",
      "KeyLocations: 柳链集织局 / 学徒宿舍巷 / 三环亭 / 九埠市票行茶局",
      "F*: F6/F8/F12/F15/F17",
      "口头禅: '加一拍' '别跟我谈规矩，先过产'"
    ]
  },

  // 角色成长轨迹 (新增)
  characterArc: {
    currentStage: "③ 试炼与盟友（反面势力）→ ④ 深渊（事故/舆情反噬）",
    developmentGoals: [
      {
        id: "sh-g1",
        category: "professional",
        goal: "稳住产量同时避免撤牌",
        motivation: "保饭碗与还债",
        timeline: "两个月",
        obstacles: ["舆论与证据曝光","行会考核","安全事故隐患"],
        progress: 30,
        priority: "high"
      }
    ],
    growthMilestones: [
      {
        id: "sh-m1",
        title: "首次签署‘公平链契’样本",
        description: "在三环亭压力下被迫接受见证合同模板",
        significance: "态度松动的开始",
        prerequisites: ["证据上墙","票行与官署双向施压"],
        relatedGoals: ["sh-g1"],
        status: "planned"
      }
    ],
    personalityChanges: [
      {
        id: "sh-p1",
        trait: "对安全的重视",
        oldValue: "安全不出事就行",
        newValue: "安全先于产量",
        trigger: "一次设备爆线致工伤与赔偿",
        timeline: "一月",
        significance: "major",
        stability: "developing"
      }
    ],
    skillProgression: [
      {
        skill: "机势·合拍",
        category: "professional",
        currentLevel: 6,
        targetLevel: 7,
        learningMethod: "与灵域匠师联合调机",
        timeframe: "两月",
        obstacles: ["耳鸣加剧","技术术语不熟"],
        mentors: ["灵域外聘匠师（未名）"]
      }
    ],
    relationshipEvolution: [
      {
        relationshipId: "rel-su-yao-opp",
        personName: "苏杳",
        evolutionType: "changing",
        previousState: "强对立",
        currentState: "有限妥协（在证据与见证下）",
        triggers: ["公平链契样本落地试行"],
        timeline: "短期",
        significance: "学徒线冲突缓和的关键"
      }
    ],
    internalConflicts: [
      {
        id: "sh-ic1",
        title: "产量 vs. 安全",
        description: "高压产线指标与人员安全的取舍",
        conflictingValues: ["效率","生命"],
        emotionalImpact: "愤怒与内疚交替",
        manifestations: ["夜巡独坐","迁怒学徒"],
        resolutionAttempts: ["护罩升级","见证合同"],
        status: "active"
      }
    ],
    externalChallenges: [
      {
        id: "sh-ec1",
        title: "三方挤压：行会-票行-舆论",
        description: "资金与合同被锁，舆情上墙，撤牌在即",
        source: "society",
        difficulty: 8,
        timeframe: "一至两月",
        resources: ["骨干监工","与票行的旧人情"],
        strategies: ["有限让步换时间","引入灵域匠师背书"],
        status: "upcoming"
      }
    ]
  },

  // 互动行为模式 (新增)
  behaviorProfile: {
    communicationStyle: {
      primaryStyle: "aggressive",
      verbalCharacteristics: ["命令句多", "夹粗话", "以数字压人"],
      nonverbalCharacteristics: ["吹铜哨", "拍桌", "盯视"],
      listeningStyle: "distracted",
      feedbackStyle: "就事就罚/就赏",
      conflictCommunication: "先压制后谈条件",
      culturalInfluences: ["工棚强人文化"]
    },
    bodyLanguage: {
      posture: "前倾压人",
      gestures: ["食指点人", "手掌下压示停机不可"],
      facialExpressions: ["冷横眉", "薄笑"],
      eyeContact: "frequent",
      personalSpace: "close",
      nervousHabits: ["抠护腕带", "敲铜哨"],
      confidenceIndicators: ["步伐快", "声音大"],
      culturalVariations: ["对官员与票行会稍放低姿态"]
    },
    decisionMaking: {
      approach: "spontaneous",
      timeframe: "quick",
      informationGathering: "凭经验与机声判断为主",
      riskTolerance: 7,
      influences: ["产量指标", "票行债压"],
      biases: ["现状偏差", "控制错觉"],
      decisionHistory: ["延长工时压产", "反对护罩升级（早期）"]
    },
    conflictResponse: {
      primaryStyle: "competing",
      escalationTriggers: ["公开质疑", "停机/上墙"],
      deescalationMethods: ["小利封口", "威胁撤人"],
      emotionalReactions: ["恼怒爆发"],
      physicalReactions: ["耳鸣", "胃酸"],
      recoveryMethods: ["夜巡独坐", "烈酒"],
      conflictHistory: ["多次与学徒对峙，曾引发小规模冲突"]
    },
    socialBehavior: {
      socialEnergy: "extroverted",
      groupDynamics: "在工棚中具强支配力",
      socialRoles: ["督头", "执鞭者"],
      boundaryManagement: "公私混杂（以小恩小惠换忠诚）",
      socialAnxieties: ["被三环亭点名质询"],
      socialStrengths: ["快速集结人手", "压住混乱"],
      networkingStyle: "头工-票行-行会三角",
      socialAdaptability: 6
    },
    workStyle: {
      productivity: "afternoon",
      environment: "bustling",
      organization: "flexible",
      taskManagement: "口头指令+红黑牌",
      collaboration: "核心监工小圈子",
      innovation: "实用小改，抗拒制度化",
      stressManagement: "强撑+发泄"
    },
    leadershipStyle: {
      type: "autocratic",
      strengths: ["执行快","压场强"],
      weaknesses: ["决策短视","事故风险高"],
      motivationMethods: ["即时奖惩","加班补贴"],
      delegationStyle: "重用亲近骨干",
      feedbackApproach: "当众喝令",
      decisionInclusivity: "低",
      crisisManagement: "强压停机→再谈条件"
    },
    learningStyle: {
      primary: "kinesthetic",
      preferences: ["看你做我再做", "现场口传"],
      strengths: ["动作记忆强", "临场处置快"],
      challenges: ["条文/合同阅读弱"],
      motivationFactors: ["保住头工牌", "奖金"],
      retentionMethods: ["口诀与手势"],
      environments: ["工棚", "产线"],
      adaptability: 5
    }
  }
};
