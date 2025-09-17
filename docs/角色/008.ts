const renyu_character_08: Character = {
  id: "char-renyu-lujin-008",
  projectId: "proj-liashi-jiuyu",
  createdAt: new Date("2025-09-17T00:00:00Z"),
  updatedAt: new Date("2025-09-17T00:00:00Z"),

  // 基本信息
  basicInfo: {
    name: "陆瑾",
    alias: ["清节侯", "纸面青天"],
    age: 41,
    gender: "male",
    occupation: "县令（兼缚司总责）",
    socialStatus: "士阶·官署编制"
  },

  // 外貌特征
  appearance: {
    height: "179cm",
    weight: "70kg",
    hairColor: "乌黑束冠（鬓微霜）",
    eyeColor: "深墨",
    skinTone: "偏白",
    bodyType: "清瘦·耐站型",
    specialMarks: ["左手食指节有旧伤，按印久致茧厚", "胸前佩细金命环（隐）"],
    clothingStyle: "玄青官袍、素底朝靴；出巡着便服披风以显亲民"
  },

  // 性格特质
  personality: {
    coreTraits: ["城府深", "自律", "算计", "演示型同理心"],
    values: ["秩序", "名誉", "政绩"],
    beliefs: ["乱世先稳，再谈善", "牺牲少数可保多数"],
    fears: ["御史问罪拔官", "地方财粮崩盘引发民变"],
    desires: ["升任巡链司", "以“样板县”名留石经塔"],
    weaknesses: ["功利化取舍", "对底层真实情状感知迟钝"],
    strengths: ["政策拼装与落地", "驭下术", "危机话术与舆情控场"]
  },

  // 背景故事
  background: {
    birthplace: "御书镇（人域与天域交界学镇）",
    family: "书香门第；妻柳氏（体弱），一子就读九环书院附校",
    childhood: "早龄入塾，熟诵《环典》；父为州府小吏，常耳濡目染权术",
    education: "县学→天域法度馆进修两年（未入祭司序列）",
    importantEvents: [
      "22岁：以优等入仕为县丞，整肃仓税有功",
      "29岁：代理县令，成功处置一次封关期哄抢，获“清节”嘉名",
      "36岁：升正县令，推进‘黑籍配额’与加缚流程标准化",
      "40岁：御环台巡按将至，启动“样板县”工程（粉饰考绩）"
    ],
    trauma: ["青年任上首度封关死伤案被记过，险些撤职", "幼时目睹父亲因顶撞上司被外放"],
    achievements: ["三年内账目合规率全郡第一", "建立县域“舆情日清”班底（灰度操作）"]
  },

  // 能力技能
  abilities: {
    professionalSkills: ["政策拼装与指标管理", "预算平衡与调拨", "公共危机舆情控场", "多方博弈谈判"],
    specialTalents: ["记人不记过失色（能回忆关键人脉细节）", "察言观色与会场节奏掌控"],
    languages: ["通域语", "天域官音", "人域乡言"],
    learningAbility: "阅读—抽象—流程化强，擅将试点固化为规程",
    socialSkills: "面子里子兼顾；能在官商乡三方中保平衡",
    practicalSkills: ["签批矩阵设计", "听证会控场", "应急勘验（走流程）"]
  },

  // 人际关系
  relationships: {
    family: [
      { name: "柳氏", relationship: "夫妻", description: "体弱，持家谨慎，不问政", importance: "medium" },
      { name: "陆澄", relationship: "父子", description: "九环书院附校生，理想主义强", importance: "medium" }
    ],
    friends: [
      { name: "顾止水", relationship: "学友/智囊", description: "天域法度馆外派教习，给其法术与策略建议", importance: "high" }
    ],
    lovers: [],
    enemies: [
      { name: "林岚", relationship: "制度对手", description: "多次在三环亭掀其“样板化”遮羞布", importance: "high" },
      { name: "薛箴", relationship: "异见盟友", description: "在‘中立仓’问题上多次交锋", importance: "medium" }
    ],
    mentors: [
      { name: "巡链司上官（未名）", relationship: "提携者", description: "天域系统派系，考绩与升迁捆绑", importance: "high" }
    ],
    subordinates: [
      { name: "董铖", relationship: "下属", description: "书办，执行力强；亦是背锅之人", importance: "high" },
      { name: "赵槐", relationship: "下属", description: "差役头，押解利器", importance: "medium" }
    ],
    socialCircle: ["州府同僚", "票行股东圈（何舫）", "书院讲习圈"]
  },

  // 生活状况
  lifestyle: {
    residence: "枢链城县署后宅（内设小书斋与密档间）",
    economicStatus: "稳健富足（灰色福利）",
    dailyRoutine: "卯时读报简→辰时早朝→午前签批→午后接见→薄暮会商→夜间密档",
    hobbies: ["观棋但少落子", "收集地方志", "抄写《小环章》批注"],
    foodPreferences: ["清淡小菜", "苦茶", "少酒"],
    entertainment: ["书场听‘清官公案’自我投射", "庭院独步"]
  },

  // 心理状态
  psychology: {
    mentalHealth: "高压高功能；对“不可控变量”焦虑",
    mentalHealthStatus: "good",
    copingMechanisms: [
      { type: "adaptive", strategy: "拆分指标与压期", triggers: ["上级催办","舆情上升"], effectiveness: 8, frequency: "frequent" },
      { type: "maladaptive", strategy: "替罪羊策略（甩锅）", triggers: ["流程出错","问责风险"], effectiveness: 5, frequency: "occasional" }
    ],
    emotionalPatterns: [
      { emotion: "愧疚（被压抑）", triggers: ["个案伤亡","见底层母子"], intensity: 5, duration: "brief", expression: "片刻失神后恢复", impact: "轻微失眠" }
    ],
    trauma: [
      { type: "adult", event: "封关死伤案问责", age: 24, severity: "severe", status: "healing", triggers: ["鼓噪","火光","哭喊"], effects: ["梦魇","握笔过紧"], copingMethods: ["写检讨","加强控场程序"] }
    ],
    growthNeeds: ["低风险纠错通道", "权责分明的替代性处置方案"],
    cognitivePatterns: [
      { type: "heuristic", description: "最小动荡策略", situations: ["群体事件"], impact: "mixed", awareness: "conscious" },
      { type: "bias", description: "权威偏误", situations: ["证词评估"], impact: "negative", awareness: "subconscious" }
    ],
    stressResponses: [
      {
        stressor: "御环台巡按与媒体围观",
        physicalResponse: ["偏头痛","食欲减退"],
        emotionalResponse: ["烦躁","焦虑"],
        behavioralResponse: ["加开会","压封差错"],
        cognitiveResponse: ["过度控制欲","确认偏误"],
        timeframe: "巡按期全程"
      }
    ],
    emotionalIntelligence: {
      selfAwareness: 6, selfRegulation: 7, motivation: 8, empathy: 5, socialSkills: 8,
      strengths: ["场面掌控","资源调度"], weaknesses: ["真实倾听不足","道德迟钝"]
    },
    psychologicalDefenses: ["合理化", "分隔化", "投射"],
    mentalHealthHistory: [
      { date: new Date("2025-03-01"), status: "good", notes: "通过‘样板县’初评，短期情绪回升" }
    ]
  },

  // 故事功能
  storyRole: {
    characterType: "antagonist",
    characterArc: "秩序守护者 → 黑箱导演 →（可选）破框合作者",
    conflictRole: "制度顶层的总导演/考绩导向的压力源",
    symbolism: "金命环=权势与代价；纸面青天=看起来公正的计算",
    readerConnection: "复杂反派：用“稳定”之名做切割选择的人"
  },

  // 特殊设定
  specialSettings: {
    worldBuilding: "裂世九域·法则链纪元",
    culturalBackground: "人域-官署/礼制交汇（受天域法度影响深）",
    historicalContext: "裂世后时代",
    technologyLevel: "链工学-中",
    magicAbilities:
      "法则链：主[命运] 副[因果]；契合度:4；禁忌:[以人祭换保升, 指标替代人命的‘命格置换’]；代表术式:[签运·转祸, 命格·调署(责任再分配), 因果·切面(把责任切给最小圈层)]；代价: 生辰命线磨损、周期性耳鸣与失眠、短时‘道德麻木’后遗",
    culturalIdentity: {
      primaryCulture: "人域-官署文化",
      subcultures: ["天域法度馆学统"],
      culturalValues: ["秩序","政绩","名誉"],
      culturalConflicts: ["与乡社人情/行会契约理念冲突", "与荒域临时断链冲突"],
      assimilationLevel: 8,
      culturalPride: 7,
      traditionalPractices: ["链祭日大礼按时参加"],
      modernAdaptations: ["流程卡、舆情日报、指标看板"]
    },
    religiousBeliefs: {
      religion: "天命信仰",
      denomination: "祭司议会正统",
      devotionLevel: 6,
      practices: ["链祭日", "亲自主持宣誓礼（偶尔）"],
      beliefs: ["天道偏爱稳定"],
      doubts: ["偶尔怀疑‘牺牲少数’的正当性"],
      spiritualExperiences: ["夜半梦见命环发冷，第二日撤回一纸命令"],
      religionInLife: "important"
    },
    languageProfile: {
      nativeLanguage: "通域语",
      fluentLanguages: ["天域官音", "人域乡言"],
      learningLanguages: [],
      accents: ["官话腔稳重缓慢"],
      dialectVariations: [],
      speechPatterns: [
        { characteristic: "政策化表达", examples: ["先稳后处", "以县域为单位统筹"], frequency: "often", context: ["会议","宣告"], origin: "官署训练" }
      ],
      languageBarriers: ["灵域技术语冗长不耐"],
      communicationPreferences: ["会前打点人脉", "会后只留书面要点"]
    },
    behaviorPatterns: [
      { category: "professional", behavior: "三案并陈（主案/备案/兜底）", frequency: "situational", triggers: ["突发事件"], context: ["县堂/会商"], development: "提升稳定但滋生黑箱" },
      { category: "social", behavior: "以清官形象走基层", frequency: "monthly", triggers: ["考绩前"], context: ["市集/祠堂"], development: "维持名望" }
    ],
    rolePlayingNotes: [
      "Domain: 人域",
      "KeyLocations: 县缚司署 / 枢链城 / 三环亭 / 县堂 / 御书镇",
      "F*: F2/F5/F10/F11(可升级)/F14/F17/F19",
      "口头禅: '先稳后处' '以县域为单位统筹'"
    ]
  },

  // 角色成长轨迹
  characterArc: {
    currentStage: "③→④（试炼顶层压力→深渊反噬）",
    developmentGoals: [
      {
        id: "lj-g1",
        category: "professional",
        goal: "保住‘样板县’评定并晋升巡链司",
        motivation: "升迁与派系利益",
        timeline: "半年",
        obstacles: ["御环台巡按", "舆情反噬", "证据曝光"],
        progress: 50,
        priority: "high"
      }
    ],
    growthMilestones: [
      {
        id: "lj-m1",
        title: "撤回一次致命命令",
        description: "在证据公开与祠司证词面前，暂缓黑籍加缚令",
        significance: "价值观松动",
        prerequisites: ["三方证据合围"],
        relatedGoals: ["lj-g1"],
        status: "in_progress"
      }
    ],
    personalityChanges: [
      {
        id: "lj-p1",
        trait: "牺牲观",
        oldValue: "少数可牺牲",
        newValue: "寻找替代性方案",
        trigger: "乡祠预审试点成功与死亡个案梦魇",
        timeline: "一月",
        significance: "moderate",
        stability: "developing"
      }
    ],
    skillProgression: [
      {
        skill: "签运·转祸",
        category: "professional",
        currentLevel: 6,
        targetLevel: 7,
        learningMethod: "法度馆进阶与实案推演",
        timeframe: "两月",
        obstacles: ["反噬耳鸣加剧","舆情监督"],
        mentors: ["顾止水"]
      }
    ],
    relationshipEvolution: [
      {
        relationshipId: "rel-dongcheng-sub",
        personName: "董铖",
        evolutionType: "weakening",
        previousState: "强绑定",
        currentState: "保留与切割并行",
        triggers: ["样板县工程失手与黑箱暴露"],
        timeline: "当前",
        significance: "可能抛弃其背锅"
      }
    ],
    internalConflicts: [
      {
        id: "lj-ic1",
        title: "稳定 vs. 正义",
        description: "当稳定与个体正义不可兼得时的抉择",
        conflictingValues: ["秩序","公义"],
        emotionalImpact: "失眠与自我辩解循环",
        manifestations: ["过度开会","延迟签批"],
        resolutionAttempts: ["引入第三方见证","乡祠预审试点"],
        status: "active"
      }
    ],
    externalChallenges: [
      {
        id: "lj-ec1",
        title: "巡按与媒体联动审查",
        description: "上查下访双向挤压，样板工程被质疑造假",
        source: "society",
        difficulty: 8,
        timeframe: "两月",
        resources: ["法度馆人脉","票行备付池","县内宣传系统"],
        strategies: ["有限公开数据","替代指标转移焦点"],
        status: "current"
      }
    ]
  },

  // 互动行为模式
  behaviorProfile: {
    communicationStyle: {
      primaryStyle: "assertive",
      verbalCharacteristics: ["政策化、被动语态多", "避免绝对词"],
      nonverbalCharacteristics: ["稳步慢语", "目光扫全场再落点名"],
      listeningStyle: "selective",
      feedbackStyle: "书面批示+口头安抚并行",
      conflictCommunication: "先定议题后分组会商",
      culturalInfluences: ["官署合议传统"]
    },
    bodyLanguage: {
      posture: "直立、双手背后",
      gestures: ["指节轻敲案几定节奏", "掌心向下示‘稳’"],
      facialExpressions: ["温和而疏离"],
      eyeContact: "moderate",
      personalSpace: "normal",
      nervousHabits: ["揉食指旧伤", "轻触命环"],
      confidenceIndicators: ["语速稳","停顿把握好"],
      culturalVariations: ["礼仪场合动作标准化"]
    },
    decisionMaking: {
      approach: "analytical",
      timeframe: "deliberate",
      informationGathering: "数据/人情/舆情三表并看",
      riskTolerance: 4,
      influences: ["上级考核","派系利益","地方稳定"],
      biases: ["权威偏误","确认偏误"],
      decisionHistory: ["推进黑籍配额", "粉饰样板县工程"]
    },
    conflictResponse: {
      primaryStyle: "compromising",
      escalationTriggers: ["公开质疑权威","舆情爆点"],
      deescalationMethods: ["换议题与替代指标", "设临时工作组"],
      emotionalReactions: ["克制烦躁"],
      physicalReactions: ["头痛","失眠"],
      recoveryMethods: ["独步","冷茶"],
      conflictHistory: ["三次大规模群体事件未失控"]
    },
    socialBehavior: {
      socialEnergy: "ambivert",
      groupDynamics: "会场核心，善分派角色",
      socialRoles: ["裁决者","稀释冲突的主持人"],
      boundaryManagement: "公私区分严格",
      socialAnxieties: ["被上级当场否定"],
      socialStrengths: ["调度资源","稳场"],
      networkingStyle: "官-商-学三角网络",
      socialAdaptability: 8
    },
    workStyle: {
      productivity: "morning",
      environment: "quiet",
      organization: "highly_organized",
      taskManagement: "看板+红黄绿督办条",
      collaboration: "科室分工+小范围拍板",
      innovation: "制度拼装与流程再造",
      stressManagement: "分解目标与睡眠自控"
    },
    leadershipStyle: {
      type: "situational",
      strengths: ["整合资源","稳定节奏"],
      weaknesses: ["透明度不足","下放信任不足"],
      motivationMethods: ["奖惩与升迁绑定", "公开表扬"],
      delegationStyle: "关键节点握在手里，余者放权",
      feedbackApproach: "书面批示+周例会",
      decisionInclusivity: "中",
      crisisManagement: "先稳后处、三案并陈"
    },
    learningStyle: {
      primary: "reading",
      preferences: ["数据简报", "案例集", "判词"],
      strengths: ["抽象归纳","制度化"],
      challenges: ["一线细节体察不足"],
      motivationFactors: ["升迁","声望"],
      retentionMethods: ["批注", "要点卡片"],
      environments: ["县堂", "书斋"],
      adaptability: 7
    }
  }
};
