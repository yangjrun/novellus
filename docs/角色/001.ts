const renyu_character_01: Character = {
  id: "char-renyu-linlan-001",
  projectId: "proj-liashi-jiuyu",
  createdAt: new Date("2025-09-17T00:00:00Z"),
  updatedAt: new Date("2025-09-17T00:00:00Z"),

  // 基本信息
  basicInfo: {
    name: "林岚",
    alias: ["小岚", "半环"],
    age: 18,
    gender: "female",
    occupation: "外堂童生（水工学徒/抄写）",
    socialStatus: "灰籍"
  },

  // 外貌特征
  appearance: {
    height: "167cm",
    weight: "52kg",
    hairColor: "黑",
    eyeColor: "深棕",
    skinTone: "麦色",
    bodyType: "纤细·耐力型",
    specialMarks: ["左腕淡色半环印", "颈后水纹胎记"],
    clothingStyle: "粗织链纤维短襟＋束带，便于奔走与水工作业"
  },

  // 性格特质
  personality: {
    coreTraits: ["坚韧", "共情强", "好奇", "原则感"],
    values: ["公义", "自由", "守诺"],
    beliefs: ["链应服务于人而非枷锁", "真相可以被证明"],
    fears: ["亲友再次被加缚", "自己被利用成工具"],
    desires: ["为家复案", "让灰籍获得体面身份"],
    weaknesses: ["易自责", "行动时忽略后勤与休息"],
    strengths: ["临场判断", "细节记忆", "水势判断与文书双修"]
  },

  // 背景故事
  background: {
    birthplace: "白泥村（人域·南环水网）",
    family: "父林瑜（溺亡存疑，水工匠），母许霜（失踪），叔林仲（黑籍服役）",
    childhood: "随父巡渠与作图，常被宗门拒之门外；在乡祠抄写《小环章》",
    education: "宗门外堂启蒙；票行做零工学基本账册与契据",
    importantEvents: [
      "12岁：七环坝决堤夜参与救堤，被记为“擅自调闸”",
      "15岁：家族被判伪造链籍，母失踪、父溺亡；灰籍加缚在即",
      "17岁：秋试链筵当众质疑祭司判词，被逐出考场"
    ],
    trauma: ["亲眼见同伴在县链枷祭坛被加缚", "父案档册被调包、无处申诉"],
    achievements: ["复原旧渠侧闸法式并成功应用于小洪峰", "因救堤被乡社记功一次"]
  },

  // 能力技能
  abilities: {
    professionalSkills: ["水工测绘", "账册核对", "基层法条应用", "野外生存"],
    specialTalents: ["过目不忘（文书/图样）", "水势瞬时判断"],
    languages: ["通域语", "人域乡言", "天域官音（基础）"],
    learningAbility: "实验型快速吸收（偏实践）",
    socialSkills: "同理沟通，擅说服基层协作",
    practicalSkills: ["简易断缚/反签", "舟桥操作", "夜行追迹"]
  },

  // 人际关系
  relationships: {
    family: [
      { name: "林瑜", relationship: "父女", description: "水工手记的遗留者，真相未明", importance: "high" },
      { name: "许霜", relationship: "母女", description: "失踪，疑涉档案调包案", importance: "high" }
    ],
    friends: [
      { name: "苏杳", relationship: "青梅", description: "柳链集织局学徒，可靠内应", importance: "medium" }
    ],
    lovers: [],
    enemies: [
      { name: "董铖", relationship: "对立官吏", description: "县缚司书办，执行加缚令并遮掩黑籍配额", importance: "high" }
    ],
    mentors: [
      { name: "薛箴", relationship: "引路人", description: "九埠市商队头人，授其契约与因果反签之术", importance: "high" }
    ],
    subordinates: [],
    socialCircle: ["水工行会外围", "外堂落第生小群", "互市脚夫与码头牙人"]
  },

  // 生活状况
  lifestyle: {
    residence: "枢链城南郊·租住坊间",
    economicStatus: "拮据（靠临时抄写与水工活）",
    dailyRoutine: "清晨练字记账→白日水工/抄写→夜读档册与练反签",
    hobbies: ["拓印驿路环碑", "记录口述史"],
    foodPreferences: ["清粥咸菜", "河鲜", "芦根饼"],
    entertainment: ["说书摊听《断链公案》", "秋试观辩"]
  },

  // 心理状态 (增强版)
  psychology: {
    mentalHealth: "长期哀伤与高警觉并存；对‘链枷’声敏感",
    mentalHealthStatus: "fair",
    copingMechanisms: [
      { type: "adaptive", strategy: "书写与整理证据", triggers: ["无力感","被误判"], effectiveness: 8, frequency: "frequent" },
      { type: "healthy", strategy: "固定作息与夜跑数息", triggers: ["失眠","惊醒"], effectiveness: 6, frequency: "occasional" }
    ],
    emotionalPatterns: [
      { emotion: "愤怒", triggers: ["加缚令","灰籍歧视"], intensity: 7, duration: "moderate", expression: "克制辩驳而非爆发", impact: "推动行动但易过劳" },
      { emotion: "悲伤", triggers: ["父亲旧物","祭坛鼓点"], intensity: 6, duration: "moderate", expression: "沉默与回避", impact: "短时社交退缩" }
    ],
    trauma: [
      { type: "adolescent", event: "同伴被加缚处刑", age: 15, severity: "severe", status: "healing", triggers: ["环枷声","祭坛鼓点"], effects: ["惊醒","闪回"], copingMethods: ["数息","离场","握住半环印"] }
    ],
    growthNeeds: ["安全边界感", "稳定盟友网络", "制度内的合法发声渠道"],
    cognitivePatterns: [
      { type: "belief", description: "证据能改变一切", situations: ["申诉","辩论","公开听证"], impact: "mixed", awareness: "conscious" },
      { type: "bias", description: "倾向相信底层证词", situations: ["冲突调解","口述史采集"], impact: "mixed", awareness: "conscious" }
    ],
    stressResponses: [
      {
        stressor: "家案被翻旧账/公开羞辱",
        physicalResponse: ["心悸","手冷","胃痉挛"],
        emotionalResponse: ["愤懑","悲伤"],
        behavioralResponse: ["夜巡查","加班整理材料","减少睡眠"],
        cognitiveResponse: ["过度反刍","选择性回避社交"],
        timeframe: "1-3天"
      }
    ],
    emotionalIntelligence: {
      selfAwareness: 7,
      selfRegulation: 6,
      motivation: 9,
      empathy: 8,
      socialSkills: 7,
      strengths: ["倾听与复述","快速建立信任"],
      weaknesses: ["难以求助","承担过多"]
    },
    psychologicalDefenses: ["理智化","投射性认同（轻度）"],
    mentalHealthHistory: [
      { date: new Date("2024-12-01"), status: "fair", notes: "处刑目击后失眠一月", triggers: ["鼓点","锁链声"], improvements: ["固定作息","夜跑"] }
    ]
  },

  // 故事功能
  storyRole: {
    characterType: "protagonist",
    characterArc: "被压迫者 → 复仇者 → 改命者",
    conflictRole: "制度对抗者 / 证据搜集者",
    symbolism: "半环印=缺陷亦是入口；水链=柔能克刚",
    readerConnection: "底层抗争、以证据推翻不公、情理法三线并举"
  },

  // 特殊设定 (增强版)
  specialSettings: {
    worldBuilding: "裂世九域·法则链纪元",
    culturalBackground: "人域-乡社文化 / 关带互市",
    historicalContext: "裂世后时代",
    technologyLevel: "链工学-中",
    magicAbilities:
      "法则链：主[水] 副[因果]；契合度:2；禁忌:[反签官印]；代表术式:[缓缚·借势, 断缚·回环]；代价: 反噬导致短时失温与手指麻木",
    culturalIdentity: {
      primaryCulture: "人域-乡社文化",
      subcultures: ["河网渔乡", "关带互市"],
      culturalValues: ["守诺", "勤俭", "互助"],
      culturalConflicts: ["灰籍歧视", "税役剥夺"],
      assimilationLevel: 6,
      culturalPride: 6,
      traditionalPractices: ["开耕祈链", "祖灵续籍祭"],
      modernAdaptations: ["票据记账", "水工新法"]
    },
    religiousBeliefs: {
      religion: "源祖传说",
      denomination: "乡祠环祖",
      devotionLevel: 5,
      practices: ["链祭日遥拜", "祖灵续籍"],
      beliefs: ["九域应回归一体", "链应被重写为契约"],
      doubts: ["祭司公正性"],
      spiritualExperiences: ["老链桥雨夜感水势回环"],
      religionInLife: "moderate"
    },
    languageProfile: {
      nativeLanguage: "通域语",
      fluentLanguages: ["人域乡言", "天域官音（基础）"],
      learningLanguages: [],
      accents: ["轻微乡音"],
      dialectVariations: [],
      speechPatterns: [
        { characteristic: "据例自证", examples: ["给我看原账", "先读条款"], frequency: "often", context: ["辩链","交易"], origin: "外堂训练+票行耳濡目染" }
      ],
      languageBarriers: ["贵族术语不熟"],
      communicationPreferences: ["有证据再争辩", "避免公共指责"]
    },
    behaviorPatterns: [
      { category: "professional", behavior: "先记录后行动", frequency: "situational", triggers: ["冲突与盘问"], context: ["场面失控","需要留证"], development: "逐渐形成流程化取证" },
      { category: "personal", behavior: "夜跑数息", frequency: "weekly", triggers: ["失眠"], context: ["独处"], development: "配合固定作息，改善睡眠" }
    ],
    rolePlayingNotes: [
      "Domain: 人域",
      "KeyLocations: 枢链城 / 环印关镇 / 县链枷祭坛 / 环渠总干",
      "F*: F2/F5/F6/F9/F10/F12/F14/F20",
      "口头禅: '先把账本拿来' '条款先读清'"
    ]
  },

  // 角色成长轨迹 (新增)
  characterArc: {
    currentStage: "② 跨越复仇门槛（准备进入荒域取证）",
    developmentGoals: [
      {
        id: "g1",
        category: "personal",
        goal: "为父翻案并撤销灰籍加缚",
        motivation: "洗刷家耻与自我救赎",
        timeline: "三个月内",
        obstacles: ["档案封存", "证人失踪", "县府施压"],
        progress: 30,
        priority: "high"
      }
    ],
    growthMilestones: [
      {
        id: "m1",
        title: "首次反签成功",
        description: "以反签救下被错捕的脚夫",
        significance: "赢得基层信任与关键线人",
        prerequisites: [],
        relatedGoals: ["g1"],
        status: "in_progress"
      }
    ],
    personalityChanges: [
      {
        id: "p1",
        trait: "信任边界",
        oldValue: "高度防备",
        newValue: "选择性信任",
        trigger: "与商队协作成功",
        timeline: "两周",
        significance: "moderate",
        stability: "developing"
      }
    ],
    skillProgression: [
      {
        skill: "反签术",
        category: "professional",
        currentLevel: 3,
        targetLevel: 7,
        learningMethod: "实战与口传",
        timeframe: "半年",
        obstacles: ["反噬失温","器材匮乏"],
        mentors: ["薛箴"]
      }
    ],
    relationshipEvolution: [
      {
        relationshipId: "rel-suyao",
        personName: "苏杳",
        evolutionType: "strengthening",
        previousState: "普通同乡",
        currentState: "互为线人",
        triggers: ["织局欠薪调查并肩作战"],
        timeline: "一月",
        significance: "提供灵域证据入口"
      }
    ],
    internalConflicts: [
      {
        id: "ic1",
        title: "法条 vs. 人情",
        description: "严格按条或保护弱者？",
        conflictingValues: ["公义","慈悲"],
        emotionalImpact: "拉扯与自责并存",
        manifestations: ["失眠","回避困难对话"],
        resolutionAttempts: ["以证据与临时措施兼顾"],
        status: "active"
      }
    ],
    externalChallenges: [
      {
        id: "ec1",
        title: "黑籍配额上调",
        description: "家属受牵连，村社不稳",
        source: "society",
        difficulty: 7,
        timeframe: "即时",
        resources: ["乡社支持","商队护送"],
        strategies: ["公开听证辩链","寻求跨域证据"],
        status: "current"
      }
    ]
  },

  // 互动行为模式 (新增)
  behaviorProfile: {
    communicationStyle: {
      primaryStyle: "assertive",
      verbalCharacteristics: ["先问证据", "复述对方观点再反驳"],
      nonverbalCharacteristics: ["目光稳定", "下颌微抬"],
      listeningStyle: "active",
      feedbackStyle: "具体到条款与动作",
      conflictCommunication: "先降温后拆招",
      culturalInfluences: ["人域讲理务实的沟通传统"]
    },
    bodyLanguage: {
      posture: "放松但重心前倾",
      gestures: ["指向文书边角", "双掌向下按压示意冷静"],
      facialExpressions: ["微皱眉", "专注凝视"],
      eyeContact: "moderate",
      personalSpace: "normal",
      nervousHabits: ["搓袖口", "轻敲指节"],
      confidenceIndicators: ["步伐稳", "语速均匀"],
      culturalVariations: ["在祭坛或长者前先行扣环礼"]
    },
    decisionMaking: {
      approach: "analytical",
      timeframe: "moderate",
      informationGathering: "现场取证+口述采集+比对账册",
      riskTolerance: 6,
      influences: ["父亲水工手记", "外堂条款训练"],
      biases: ["倾向相信底层证词"],
      decisionHistory: ["救堤夜主动担责", "秋试公开质疑祭司"]
    },
    conflictResponse: {
      primaryStyle: "collaborating",
      escalationTriggers: ["加缚令", "歧视灰籍", "伪造档册"],
      deescalationMethods: ["提出具体解决流程", "先保人再追责"],
      emotionalReactions: ["愤怒后迅速冷静"],
      physicalReactions: ["手冷", "心跳加速"],
      recoveryMethods: ["夜跑数息", "记录复盘"],
      conflictHistory: ["与缚司在县衙公开交锋一次"]
    },
    socialBehavior: {
      socialEnergy: "ambivert",
      groupDynamics: "小队协作时能自然而然承担组织",
      socialRoles: ["记录者","协调者"],
      boundaryManagement: "对陌生人设明确边界，对弱者放宽",
      socialAnxieties: ["在贵族语境下表达不自信"],
      socialStrengths: ["跨层沟通", "迅速建立共同目标"],
      networkingStyle: "凭口碑与互助网络",
      socialAdaptability: 7
    },
    workStyle: {
      productivity: "variable",
      environment: "bustling",
      organization: "moderately_organized",
      taskManagement: "清单+证据优先级排序",
      collaboration: "愿意分工并记录流程",
      innovation: "擅长现场改造、临时工具",
      stressManagement: "以行动与复盘对冲压力"
    },
    leadershipStyle: {
      type: "situational",
      strengths: ["临机处置", "尊重专业意见"],
      weaknesses: ["容易亲力亲为过度消耗"],
      motivationMethods: ["目标拆分与即时反馈"],
      delegationStyle: "按技能分配小任务",
      feedbackApproach: "事后复盘+正反例对照",
      decisionInclusivity: "邀请相关者短会投票",
      crisisManagement: "先保人命与证据"
    },
    learningStyle: {
      primary: "multimodal",
      preferences: ["图像化笔记", "实操演练"],
      strengths: ["举一反三", "快速复盘"],
      challenges: ["理论术语理解慢半拍"],
      motivationFactors: ["能见效的任务", "对弱者有帮助"],
      retentionMethods: ["案例卡片", "口述复盘"],
      environments: ["近水环境", "有样本与工具的作坊"],
      adaptability: 8
    }
  }
};
