const renyu_character_15: Character = {
  id: "char-renyu-baihui-015",
  projectId: "proj-liashi-jiuyu",
  createdAt: new Date("2025-09-17T00:00:00Z"),
  updatedAt: new Date("2025-09-17T00:00:00Z"),

  // 基本信息
  basicInfo: {
    name: "白荟",
    alias: ["牙铃", "水巷红签"],
    age: 28,
    gender: "female",
    occupation: "码头牙人/经纪（货运撮合·证据见证跑单）",
    socialStatus: "良籍·行会挂号牙人"
  },

  // 外貌特征
  appearance: {
    height: "163cm",
    weight: "52kg",
    hairColor: "乌黑（高马尾）",
    eyeColor: "深褐",
    skinTone: "偏白",
    bodyType: "轻巧·敏捷型",
    specialMarks: ["左耳佩小牙铃串（身份识别）", "右虎口老茧（常携竹签板）", "脚踝有细小风纹刺青"],
    clothingStyle: "短打窄袖+马甲口袋多，腰系票夹与小拓印盒，雨天披薄油布斗篷"
  },

  // 性格特质
  personality: {
    coreTraits: ["机敏", "爽利", "实用主义", "重信誉"],
    values: ["说话算数", "公开可证", "弱方保护"],
    beliefs: ["价差不是罪，隐瞒才是", "让信息通畅，冲突就降一半"],
    fears: ["背了黑锅被封号", "消息源被报复"],
    desires: ["把‘公开报价+见证交割’做成码头行规", "拥有一支自己的见证小队"],
    weaknesses: ["对长篇礼仪腔不耐", "急躁，容易抢话"],
    strengths: ["现场撮合", "价格与路线直觉", "把复杂条款讲成三句话"]
  },

  // 背景故事
  background: {
    birthplace: "九埠市水巷（人域）",
    family: "叔父白简（行会老账房/编辑）；父母早亡，由叔照拂",
    childhood: "在码头与报馆间长大，替人跑票与递话，十二岁就会独立撮合小单",
    education: "行会牙人短训+随白简学‘白话条款’；识字良好",
    importantEvents: [
      "16岁：首单撮合成功并追回应收，名声初立",
      "21岁：组织‘红签榜’（公开报价与路线时窗），遭黑市威胁",
      "24岁：与中立仓首次合作‘三方见证交割’",
      "27岁：参与‘事实墙听证’，把报价与赔付上墙示众"
    ],
    trauma: ["少年时一次被围堵逼签假票，险些丧命", "目睹押解夜里货主被打昏带走"],
    achievements: [
      "红/蓝两色签牌体系（红=公开价，蓝=议价区间）",
      "‘三步撮合’清单（需求—证据—交割）在码头流行"
    ]
  },

  // 能力技能
  abilities: {
    professionalSkills: ["行情情报采集", "报价撮合与合同口译", "交割见证与纠纷调处", "风险预案编制"],
    specialTalents: ["风向嗅觉（舆情/行情将变前能嗅到异味）", "人群中定位关键人并迅速建立信任"],
    languages: ["通域语", "人域乡言", "天域官音（交易口）", "荒域部落言（口令级）"],
    learningAbility: "场景-清单化极强，能把一场混乱整理成三条执行要点",
    socialSkills: "人缘广，能在官/商/民三方间游走并留后路",
    practicalSkills: ["誊影·摹真（票据快速拓印）", "价差·平衡（撮合双边让渡）", "交割流程封箱与封蜡"]
  },

  // 人际关系
  relationships: {
    family: [
      { name: "白简", relationship: "叔侄", description: "精神与方法导师，彼此互证彼此背书", importance: "high" }
    ],
    friends: [
      { name: "裴青笺", relationship: "盟友", description: "事实墙合作人，互通线索与证据", importance: "high" },
      { name: "鲁三", relationship: "业务同盟", description: "护运队长，多次共退黑钩之劫", importance: "high" }
    ],
    lovers: [],
    enemies: [
      { name: "黑钩", relationship: "宿敌", description: "荒域劫路头，屡破其公开交割规则", importance: "high" },
      { name: "何舫", relationship: "利益对立/博弈", description: "不满其公开报价削弱票行信息优势", importance: "medium" }
    ],
    mentors: [
      { name: "白简", relationship: "导师", description: "‘半账留余’与白话条款启蒙", importance: "high" }
    ],
    subordinates: [
      { name: "见证小队（雏形）", relationship: "队头-队员", description: "三人编组：拓印/照相/封箱", importance: "medium" }
    ],
    socialCircle: ["码头牙人圈", "中立仓守仓人", "行会护运队", "书场/报馆串联者"]
  },

  // 生活状况
  lifestyle: {
    residence: "九埠市水巷旧楼二层（近码头）",
    economicStatus: "小康稳定（靠抽成与见证费）",
    dailyRoutine: "清晨看红签榜→上午集市撮合→午后交割见证→傍晚整理事实墙材料→夜间复盘行情",
    hobbies: ["收集各地价目签", "做口袋清单", "练快步与绕桩"],
    foodPreferences: ["热汤面", "卤味", "浓茶"],
    entertainment: ["码头对歌", "书场听市井公案"]
  },

  // 心理状态 (增强版)
  psychology: {
    mentalHealth: "高功能、轻度过警觉；在被盯梢期焦虑上行",
    mentalHealthStatus: "good",
    copingMechanisms: [
      { type: "healthy", strategy: "把风险拆成‘三步撮合清单’并公示", triggers: ["舆情翻转","黑市放风"], effectiveness: 8, frequency: "frequent" },
      { type: "adaptive", strategy: "更换动线与临时据点", triggers: ["被尾随","被放暗风"], effectiveness: 7, frequency: "occasional" }
    ],
    emotionalPatterns: [
      { emotion: "急躁", triggers: ["绕圈话术","压价羞辱"], intensity: 6, duration: "brief", expression: "抢话、敲牙铃", impact: "易得罪权势方" }
    ],
    trauma: [
      { type: "adolescent", event: "被围堵逼签假票", age: 15, severity: "severe", status: "healing", triggers: ["背风小巷","多人半环围位"], effects: ["掌心出汗","心跳快"], copingMethods: ["保持开阔场地交易","引入第三方见证"] }
    ],
    growthNeeds: ["县署备案的‘公开报价+见证交割’流程", "见证队的合法身份与保护"],
    cognitivePatterns: [
      { type: "belief", description: "公开与见证能让坏事难做", situations: ["交易","纠纷"], impact: "positive", awareness: "conscious" },
      { type: "bias", description: "倾向相信底层小商", situations: ["价差纠纷"], impact: "mixed", awareness: "conscious" }
    ],
    stressResponses: [
      {
        stressor: "黑市联手压价+尾随恐吓",
        physicalResponse: ["肩颈紧", "手心汗"],
        emotionalResponse: ["警觉", "恼怒"],
        behavioralResponse: ["转移交割地点", "加请中立仓见证"],
        cognitiveResponse: ["快速列风险与退路"],
        timeframe: "1-2日"
      }
    ],
    emotionalIntelligence: {
      selfAwareness: 7, selfRegulation: 6, motivation: 8, empathy: 6, socialSkills: 8,
      strengths: ["快速信任建立", "把冲突转为交易"], weaknesses: ["脾气急", "对权力话术不耐"]
    },
    psychologicalDefenses: ["理智化", "幽默化"],
    mentalHealthHistory: [
      { date: new Date("2025-01-20"), status: "good", notes: "完成三起高风险交割无伤害，红签榜口碑上升" }
    ]
  },

  // 故事功能
  storyRole: {
    characterType: "supporting",
    characterArc: "市井牙人 → 公开与见证的制度推手 →（可选）见证小队队长",
    conflictRole: "信息流与资金流的‘阀门’/把交易变安全的关键节点",
    symbolism: "牙铃=信誉与召集；红签=透明的价格之光",
    readerConnection: "有锋利与温度的市井女性：快、准、讲理、有担当"
  },

  // 特殊设定 (增强版)
  specialSettings: {
    worldBuilding: "裂世九域·法则链纪元",
    culturalBackground: "人域-码头/牙人文化（与行会/中立仓/报馆耦合）",
    historicalContext: "裂世后时代",
    technologyLevel: "链工学-中",
    magicAbilities:
      "法则链：主[风] 副[因果]；契合度:3；禁忌:[放风造谣、诱导性错价、暗室逼签]；代表术式:[风信·撮合(快速聚合供需), 口约·留痕(将口头约定化作短期可证印), 价差·平衡(以因果抵扣式让渡达成交易)]; 代价: 过度施术引发嗓音沙哑、短时耳鸣与‘社交性疲惫’",
    culturalIdentity: {
      primaryCulture: "人域-码头牙人文化",
      subcultures: ["行会护运圈", "中立仓守仓网络", "书场/报馆串联"],
      culturalValues: ["信誉","公开","效率"],
      culturalConflicts: ["与票行信息不对称博弈", "与黑市‘暗房交易’冲突"],
      assimilationLevel: 7,
      culturalPride: 7,
      traditionalPractices: ["开市摇铃礼", "成交后‘三证’互拓"],
      modernAdaptations: ["红/蓝签榜与现场见证视频化（誊影摹真）"]
    },
    religiousBeliefs: {
      religion: "源祖传说（市井守望派）",
      denomination: "码头河祠",
      devotionLevel: 3,
      practices: ["开市对河风一礼", "祭亡名册默念"],
      beliefs: ["风带来消息，消息救人"],
      doubts: ["祠司是否该介入价格？"],
      spiritualExperiences: ["暴涨前一夜‘风声’异常，提前劝退两单投机，救下一家小商"],
      religionInLife: "minimal"
    },
    languageProfile: {
      nativeLanguage: "通域语",
      fluentLanguages: ["人域乡言", "天域官音（交易口）", "荒域部落言（口令级）"],
      learningLanguages: [],
      accents: ["码头快语（节拍明显）"],
      dialectVariations: [],
      speechPatterns: [
        { characteristic: "三句成交", examples: ["要多少", "我有谁", "这里见证交割"], frequency: "often", context: ["撮合","交割"], origin: "牙人训练" }
      ],
      languageBarriers: ["冗长礼仪腔与学术辩经"],
      communicationPreferences: ["当面+短句+证据上墙"]
    },
    behaviorPatterns: [
      { category: "professional", behavior: "出摊即挂‘红签榜’并开放比价", frequency: "daily", triggers: ["开市"], context: ["码头"], development: "压低暗盘价格操纵" },
      { category: "professional", behavior: "交割必引入第三方见证并誊影存档", frequency: "situational", triggers: ["大额/跨域交易"], context: ["中立仓/三环亭"], development: "纠纷率下降" },
      { category: "personal", behavior: "晚间复盘‘风声簿’并写次日提醒", frequency: "daily", triggers: ["行情波动"], context: ["私室"], development: "提高预警准确率" }
    ],
    rolePlayingNotes: [
      "Domain: 人域",
      "KeyLocations: 九埠市码头 / 中立仓 / 三环亭 / 水巷红签摊位",
      "F*: F5/F6/F12/F17/F19/F20",
      "口头禅: '明牌不伤人' '先见证，后交割'"
    ]
  },

  // 角色成长轨迹 (新增)
  characterArc: {
    currentStage: "③ 试炼与盟友（公开与见证推进者）",
    developmentGoals: [
      {
        id: "bh-g1",
        category: "professional",
        goal: "把‘公开报价+见证交割’写入码头行规并获县署备案",
        motivation: "降低交易暴力成本",
        timeline: "两个月",
        obstacles: ["票行与黑市阻力","官署观望","人身安全"],
        progress: 40,
        priority: "high"
      }
    ],
    growthMilestones: [
      {
        id: "bh-m1",
        title: "红签榜+三证交割首场全流程落地",
        description: "一场大额交易在三环亭—中立仓双点完成，纠纷零暴力",
        significance: "树立样本与口碑",
        prerequisites: ["见证队训练","官署备案试点"],
        relatedGoals: ["bh-g1"],
        status: "planned"
      }
    ],
    personalityChanges: [
      {
        id: "bh-p1",
        trait: "对权力话术的处理",
        oldValue: "正面硬顶",
        newValue: "以‘程序’与‘见证’绕过对撞",
        trigger: "一次传唤后由白简点拨",
        timeline: "一月",
        significance: "moderate",
        stability: "developing"
      }
    ],
    skillProgression: [
      {
        skill: "口约·留痕",
        category: "professional",
        currentLevel: 5,
        targetLevel: 7,
        learningMethod: "与乡祠/报馆共制‘口约模板’",
        timeframe: "两月",
        obstacles: ["设备与人手不足","部分商户抵触"],
        mentors: ["白简","温砚"]
      }
    ],
    relationshipEvolution: [
      {
        relationshipId: "rel-peiqingjian-synergy",
        personName: "裴青笺",
        evolutionType: "strengthening",
        previousState: "线索互助",
        currentState: "制度化合作（事实墙+红签榜联动）",
        triggers: ["大额交割直播核验"],
        timeline: "持续",
        significance: "提高公众信任度"
      }
    ],
    internalConflicts: [
      {
        id: "bh-ic1",
        title: "赚钱 vs. 公益",
        description: "抽成与‘公开压价’的矛盾",
        conflictingValues: ["个人收益","公共信誉"],
        emotionalImpact: "短期焦虑与摇摆",
        manifestations: ["夜里反复改签榜", "与买家拉扯"],
        resolutionAttempts: ["设置透明服务费","公示抽成比例"],
        status: "active"
      }
    ],
    externalChallenges: [
      {
        id: "bh-ec1",
        title: "黑市干扰与票行游说",
        description: "被逼撤红签、改回暗盘谈价",
        source: "society",
        difficulty: 7,
        timeframe: "两月",
        resources: ["见证队","中立仓","报馆曝光渠道"],
        strategies: ["选择性公开案例","联合护运队护场","法律与祠司双见证"],
        status: "upcoming"
      }
    ]
  },

  // 互动行为模式 (新增)
  behaviorProfile: {
    communicationStyle: {
      primaryStyle: "assertive",
      verbalCharacteristics: ["短句、结论先行", "价格与条款并列说清"],
      nonverbalCharacteristics: ["敲牙铃定节奏", "举签板示意‘公开’"],
      listeningStyle: "active",
      feedbackStyle: "三点式（价/证/时窗）回馈",
      conflictCommunication: "请见证→上墙→再谈价差",
      culturalInfluences: ["码头口令文化","行会白话条款"]
    },
    bodyLanguage: {
      posture: "站姿灵活，重心前",
      gestures: ["两指并拢指价", "掌心向下示稳", "举签板示约束"],
      facialExpressions: ["爽朗", "遇欺压时冷硬"],
      eyeContact: "frequent",
      personalSpace: "normal",
      nervousHabits: ["脚尖点地", "摩挲牙铃"],
      confidenceIndicators: ["语速稳", "节奏清晰"],
      culturalVariations: ["对长者与祠司礼数周到，对黑市强硬"]
    },
    decisionMaking: {
      approach: "analytical",
      timeframe: "quick",
      informationGathering: "行情+路书+证据三表并看",
      riskTolerance: 5,
      influences: ["信誉","安全","效率"],
      biases: ["底层商户偏好"],
      decisionHistory: ["推动红签公开", "多次三方见证交割成功"]
    },
    conflictResponse: {
      primaryStyle: "collaborating",
      escalationTriggers: ["暗室逼签","毁约压价"],
      deescalationMethods: ["引入中立仓/祠司见证", "事实墙即时公开"],
      emotionalReactions: ["短怒→快速转程序"],
      physicalReactions: ["手心汗","喉紧"],
      recoveryMethods: ["快步绕桩三圈", "热茶"],
      conflictHistory: ["多起纠纷转为公开交割并结清"]
    },
    socialBehavior: {
      socialEnergy: "extroverted",
      groupDynamics: "能在嘈杂中定点分工与节奏",
      socialRoles: ["撮合者","见证召集人"],
      boundaryManagement: "抽成比例与流程公开，边界清晰",
      socialAnxieties: ["被点名在官场长谈礼仪话"],
      socialStrengths: ["快速破冰", "把复杂讲成三句"],
      networkingStyle: "码头-护运-中立仓-报馆四角",
      socialAdaptability: 8
    },
    workStyle: {
      productivity: "morning",
      environment: "bustling",
      organization: "highly_organized",
      taskManagement: "签榜+口袋清单+时窗提醒",
      collaboration: "与护运/中立仓/报馆协同",
      innovation: "把‘公开’与‘见证’工具化",
      stressManagement: "复盘风声簿+快步绕桩"
    },
    leadershipStyle: {
      type: "situational",
      strengths: ["现场调度", "定节奏"],
      weaknesses: ["对长会冗谈不耐"],
      motivationMethods: ["抽成透明+案例荣誉榜"],
      delegationStyle: "按职能分配（拓印/封箱/照相）",
      feedbackApproach: "事后三点式复盘",
      decisionInclusivity: "中",
      crisisManagement: "先见证后交割、必要时转中立仓"
    },
    learningStyle: {
      primary: "multimodal",
      preferences: ["现场+图表+口令"],
      strengths: ["整合多源信息", "口袋清单化"],
      challenges: ["学术化论证"],
      motivationFactors: ["口碑与安全", "叔父期望"],
      retentionMethods: ["清单卡片", "红签边注"],
      environments: ["码头", "中立仓", "三环亭"],
      adaptability: 8
    }
  }
};
