const renyu_character_02: Character = {
  id: "char-renyu-dongcheng-002",
  projectId: "proj-liashi-jiuyu",
  createdAt: new Date("2025-09-17T00:00:00Z"),
  updatedAt: new Date("2025-09-17T00:00:00Z"),

  // 基本信息
  basicInfo: {
    name: "董铖",
    alias: ["铁环手", "书办爷"],
    age: 32,
    gender: "male",
    occupation: "县缚司书办（实际掌印与案卷主办）",
    socialStatus: "良籍（官署编制）"
  },

  // 外貌特征
  appearance: {
    height: "178cm",
    weight: "68kg",
    hairColor: "乌黑（后梳）",
    eyeColor: "墨黑",
    skinTone: "偏白",
    bodyType: "清瘦·筋骨分明",
    specialMarks: ["右耳后细小环印刺青（誓忠印）", "右手食中指指节因长年按印而肿大"],
    clothingStyle: "青黛缚司官服，束黑皮环带；常携折叠案板与印盒"
  },

  // 性格特质
  personality: {
    coreTraits: ["谨慎", "冷静", "权威导向", "记忆力强", "规训型"],
    values: ["秩序", "功绩", "名誉"],
    beliefs: ["弱者需要被管理", "法条即真相", "稳定重于善意"],
    fears: ["失去印权与话语权", "被御史问罪牵连上级"],
    desires: ["升任巡链司", "建立“标准化加缚流程”以留名"],
    weaknesses: ["僵化", "风险回避导致错失修正时机", "对底层证词天然不信任"],
    strengths: ["条款博闻", "档案管理与印鉴鉴别", "讯问时掌控节奏"]
  },

  // 背景故事
  background: {
    birthplace: "枢链城（人域·州府）",
    family: "书吏世家；父董穆为县档案吏，曾被问罪革职；母为县学教谕助理",
    childhood: "在县学抄写碑拓长大，熟背《小环章》，对“按印即权”观念根深蒂固",
    education: "县学出身，后入天域派驻的法度馆短训三年（未入正科）",
    importantEvents: [
      "16岁：以全县第一的抄写手入县衙当书办学徒",
      "24岁：破获假票案获县令提拔，开始代行掌印",
      "28岁：父亲因旧案失察被追加处分，董铖立誓“绝不让漏洞发生”",
      "30岁：参与推进“黑籍配额改革”并制定加缚清单（实有造假成分）"
    ],
    trauma: ["父亲再处分导致家族名誉受损", "一次押解途中遭伏击险死，右手指骨受伤后遗"],
    achievements: ["建立县衙印鉴底库与签批流程", "三年整肃伪票与冒籍案，案结率全郡前列"]
  },

  // 能力技能
  abilities: {
    professionalSkills: [
      "法条适用与条文检索",
      "印鉴鉴别与档案稽核",
      "讯问与谈判",
      "流程设计与风险控制"
    ],
    specialTalents: ["过耳不忘（口供细节）", "能从笔迹判断书写人状态"],
    languages: ["通域语", "天域官音", "人域乡言（能听会讲）"],
    learningAbility: "分析-归档型；擅将个案标准化",
    socialSkills: "威慑与冷面谈判；善用沉默制造压力",
    practicalSkills: ["缚印·加环（程序化）", "因果钉（口供与物证绑定）", "短兵器自卫（环匕）"]
  },

  // 人际关系
  relationships: {
    family: [
      { name: "董穆", relationship: "父子", description: "前档案吏，旧案连坐后心灰", importance: "medium" },
      { name: "沈氏", relationship: "母子", description: "县学教谕助理，期望其仕途稳定", importance: "medium" }
    ],
    friends: [
      { name: "何舫", relationship: "酒友/利益同盟", description: "九埠市链票行股东，常互通案情与财脉", importance: "medium" }
    ],
    lovers: [],
    enemies: [
      { name: "林岚", relationship: "对手", description: "多次在公开听证中拆其流程漏洞", importance: "high" }
    ],
    mentors: [
      { name: "陆瑾", relationship: "上司/拔擢者", description: "县缚司；授其掌印权亦施压背锅", importance: "high" },
      { name: "顾止水", relationship: "法规教习", description: "天域法度馆外派讲习，传其“因果钉”技巧", importance: "medium" }
    ],
    subordinates: [
      { name: "赵槐", relationship: "差役头", description: "押解与缉拿骨干，执行力强但心狠", importance: "medium" }
    ],
    socialCircle: ["县衙文案圈", "链票行晚宴圈", "法度馆旧同学"]
  },

  // 生活状况
  lifestyle: {
    residence: "枢链城东署官舍·二层小院",
    economicStatus: "中产偏上（灰色收入可观）",
    dailyRoutine: "辰时开印核签→午前讯问与卷宗会签→午后外勤巡查→夜间整理底库",
    hobbies: ["收集环印拓本", "抄碑", "茶道（专好苦茶）"],
    foodPreferences: ["清淡", "腌菜", "苦茶"],
    entertainment: ["打谱拓印会", "官圈茶局"]
  },

  // 心理状态 (增强版)
  psychology: {
    mentalHealth: "表面稳定，内在焦虑；对“失控”高度敏感",
    mentalHealthStatus: "good",
    copingMechanisms: [
      { type: "adaptive", strategy: "强迫性记录与归档", triggers: ["流程失控","上级问责"], effectiveness: 7, frequency: "frequent" },
      { type: "maladaptive", strategy: "加班至深夜压抑情绪", triggers: ["重大舆情","案卷被驳回"], effectiveness: 4, frequency: "occasional" }
    ],
    emotionalPatterns: [
      { emotion: "愤怒", triggers: ["流程被绕过","公开质疑"], intensity: 6, duration: "moderate", expression: "冷面加码与反问", impact: "激化矛盾" },
      { emotion: "羞耻", triggers: ["父案被提及"], intensity: 7, duration: "brief", expression: "转移话题、强势定性", impact: "做出过度加缚决定" }
    ],
    trauma: [
      { type: "adult", event: "押解途中伏击致死伤", age: 26, severity: "severe", status: "healing", triggers: ["金属链撞击声","夜路风声"], effects: ["握拳不自觉发抖","夜惊"], copingMethods: ["以工作转移","苦茶压制"] }
    ],
    growthNeeds: ["重新定义秩序与正义的关系", "获得可承担的纠错渠道"],
    cognitivePatterns: [
      { type: "bias", description: "权威偏误（更相信官署口供）", situations: ["审讯","听证"], impact: "negative", awareness: "subconscious" },
      { type: "assumption", description: "底层证词多受操弄", situations: ["群体事件","媒体围观"], impact: "negative", awareness: "conscious" }
    ],
    stressResponses: [
      {
        stressor: "上级施压与御史巡察",
        physicalResponse: ["偏头痛","指节疼痛"],
        emotionalResponse: ["易怒","不安"],
        behavioralResponse: ["加班审卷","提高押解强度"],
        cognitiveResponse: ["过度归因与过拟合"],
        timeframe: "1周"
      }
    ],
    emotionalIntelligence: {
      selfAwareness: 5, selfRegulation: 6, motivation: 7, empathy: 3, socialSkills: 6,
      strengths: ["程序设计","情境控制"], weaknesses: ["同理心弱","框架僵硬"]
    },
    psychologicalDefenses: ["合理化", "投射", "分隔化"],
    mentalHealthHistory: [
      { date: new Date("2024-06-01"), status: "good", notes: "押解伏击后短期失眠", triggers: ["链声","夜路"], improvements: ["固定作息","茶道放空"] }
    ]
  },

  // 故事功能
  storyRole: {
    characterType: "antagonist",
    characterArc: "守门人 → 黑箱执行者 →（可选）破框者",
    conflictRole: "黑箱守门人/法条杠杆与加缚执行",
    symbolism: "铁环之手：流程与秩序的冰冷面孔",
    readerConnection: "可恨亦可怜：制度如何塑造并吞噬人"
  },

  // 特殊设定 (增强版)
  specialSettings: {
    worldBuilding: "裂世九域·法则链纪元",
    culturalBackground: "人域-县府官署文化 / 与天域法度馆挂钩",
    historicalContext: "裂世后时代",
    technologyLevel: "链工学-中",
    magicAbilities:
      "法则链：主[因果] 副[命运]；契合度:3；禁忌:[过度加缚, 以口供替代物证]；代表术式:[缚印·加环, 因果钉, 链籍改签]；代价: 指节慢性损伤、夜听链声幻鸣、对偶发因果产生过拟合错感",
    culturalIdentity: {
      primaryCulture: "人域-官署文化",
      subcultures: ["天域法度馆短训"],
      culturalValues: ["秩序","程序","功绩"],
      culturalConflicts: ["与乡社的人情逻辑冲突","与荒域临时断链观念冲突"],
      assimilationLevel: 8,
      culturalPride: 6,
      traditionalPractices: ["链祭日随官署行礼"],
      modernAdaptations: ["底库电子化（以链算所工具）"]
    },
    religiousBeliefs: {
      religion: "天命信仰",
      denomination: "祭司议会正统",
      devotionLevel: 6,
      practices: ["链祭日行礼","对环念"],
      beliefs: ["天道以链示人", "秩序是善的形式"],
      doubts: ["偶尔怀疑个案牺牲是否必要"],
      spiritualExperiences: ["押解夜里幻听链声似在提醒‘再核查一次’"],
      religionInLife: "important"
    },
    languageProfile: {
      nativeLanguage: "通域语",
      fluentLanguages: ["天域官音", "人域乡言"],
      learningLanguages: [],
      accents: ["官话腔"],
      dialectVariations: [],
      speechPatterns: [
        { characteristic: "法条化表达", examples: ["按例办理", "流程在先"], frequency: "often", context: ["审讯","通告"], origin: "官署训练" }
      ],
      languageBarriers: ["对灵域术语不耐"],
      communicationPreferences: ["书面为准", "会议纪要优先"]
    },
    behaviorPatterns: [
      { category: "professional", behavior: "凡事立据存档", frequency: "daily", triggers: ["任何口头承诺"], context: ["办案","会签"], development: "把控风险但降低灵活性" },
      { category: "social", behavior: "在茶局交换人情与信息", frequency: "weekly", triggers: ["案子卡关"], context: ["链票行","县学旧友"], development: "形成灰色依赖" }
    ],
    rolePlayingNotes: [
      "Domain: 人域",
      "KeyLocations: 县缚司署 / 枢链城 / 环印关镇 / 县链枷祭坛",
      "F*: F2/F3/F10/F14/F17/F19",
      "口头禅: '按例' '流程在先' '你有无书面？'"
    ]
  },

  // 角色成长轨迹 (新增)
  characterArc: {
    currentStage: "③ 试炼与盟友（对主角设置制度关卡）",
    developmentGoals: [
      {
        id: "dg-dc-01",
        category: "professional",
        goal: "升任巡链司并在全郡推广标准化加缚流程",
        motivation: "功绩与名誉补偿家族创伤",
        timeline: "一年内",
        obstacles: ["御史巡察质疑", "民间舆情", "林岚的证据反击"],
        progress: 40,
        priority: "high"
      }
    ],
    growthMilestones: [
      {
        id: "ms-dc-01",
        title: "流程黑箱被当众指出并修复一次",
        description: "在三环亭听证会中被迫更正条款，首次让步",
        targetDate: undefined,
        completedDate: undefined,
        significance: "价值观松动",
        prerequisites: ["舆论压力高涨"],
        relatedGoals: ["dg-dc-01"],
        status: "in_progress"
      }
    ],
    personalityChanges: [
      {
        id: "pc-dc-01",
        trait: "对证词的偏见",
        oldValue: "几乎不信底层证词",
        newValue: "在强证据下接受个案例外",
        trigger: "老链桥案中物证反转",
        timeline: "两周",
        significance: "moderate",
        stability: "developing"
      }
    ],
    skillProgression: [
      {
        skill: "因果钉",
        category: "professional",
        currentLevel: 6,
        targetLevel: 8,
        learningMethod: "法度馆高阶研修",
        timeframe: "三月",
        obstacles: ["幻鸣干扰判断","个案样本不足"],
        mentors: ["顾止水"]
      }
    ],
    relationshipEvolution: [
      {
        relationshipId: "rel-linlan-01",
        personName: "林岚",
        evolutionType: "changing",
        previousState: "纯粹对立",
        currentState: "在个别案件上被迫协作",
        triggers: ["御环台巡按要求共线复核"],
        timeline: "短期",
        significance: "为后续‘破框’埋伏笔"
      }
    ],
    internalConflicts: [
      {
        id: "ic-dc-01",
        title: "秩序 vs. 正义",
        description: "当法条与显而易见的善相冲突时如何选择？",
        conflictingValues: ["秩序","公正"],
        emotionalImpact: "焦虑与愤怒交替",
        manifestations: ["强迫加班","提高押解力度"],
        resolutionAttempts: ["寻求上级背书","以流程优化自我安慰"],
        status: "active"
      }
    ],
    externalChallenges: [
      {
        id: "ec-dc-01",
        title: "御环台巡察",
        description: "上级突击检查黑籍配额与加缚流程",
        source: "society",
        difficulty: 8,
        timeframe: "当前一月",
        resources: ["档案底库","票行财脉支持"],
        strategies: ["舆情控管","甩锅下属或前任"],
        status: "current"
      }
    ]
  },

  // 互动行为模式 (新增)
  behaviorProfile: {
    communicationStyle: {
      primaryStyle: "direct",
      verbalCharacteristics: ["法条化、被动语态多", "强调程序与责任归属"],
      nonverbalCharacteristics: ["极少外露情绪", "目光停留在文书而非人脸"],
      listeningStyle: "selective",
      feedbackStyle: "以红笔批注与书面通告为主",
      conflictCommunication: "先定性再沟通，必要时提高押解等级",
      culturalInfluences: ["官署讲规训的表达传统"]
    },
    bodyLanguage: {
      posture: "背直、肩平",
      gestures: ["拇指与食指比示‘环’", "敲击桌面提示时间到"],
      facialExpressions: ["冷淡", "微蹙眉"],
      eyeContact: "moderate",
      personalSpace: "distant",
      nervousHabits: ["摩挲指节", "轻敲印盒"],
      confidenceIndicators: ["步幅稳", "节奏掌控强"],
      culturalVariations: ["祭坛上礼节动作标准化、近乎机械"]
    },
    decisionMaking: {
      approach: "analytical",
      timeframe: "deliberate",
      informationGathering: "以书证为主，口供次之，情报来自茶局与内线",
      riskTolerance: 3,
      influences: ["上级意志","御史问责压力"],
      biases: ["权威偏误", "确认偏误"],
      decisionHistory: ["推动黑籍配额加缚", "多次拒绝临时断链请求"]
    },
    conflictResponse: {
      primaryStyle: "competing",
      escalationTriggers: ["公开质疑权威", "绕流程的行为"],
      deescalationMethods: ["提供替代流程窗口", "延期再议"],
      emotionalReactions: ["烦躁","强硬"],
      physicalReactions: ["偏头痛", "指节疼"],
      recoveryMethods: ["苦茶静坐", "抄碑半刻"],
      conflictHistory: ["与林岚在三环亭听证交锋两次"]
    },
    socialBehavior: {
      socialEnergy: "introverted",
      groupDynamics: "小团队中居主导，强调分工与责任链",
      socialRoles: ["流程设定者","风险把关人"],
      boundaryManagement: "公务与私交严格区隔",
      socialAnxieties: ["面对群众自发围观时紧张"],
      socialStrengths: ["稳定场面","控节奏"],
      networkingStyle: "官圈与商圈双循环",
      socialAdaptability: 6
    },
    workStyle: {
      productivity: "morning",
      environment: "quiet",
      organization: "highly_organized",
      taskManagement: "清单+时序依赖图",
      collaboration: "自上而下的指令式协作",
      innovation: "流程优化大于发明创造",
      stressManagement: "以结构化工作覆盖焦虑"
    },
    leadershipStyle: {
      type: "autocratic",
      strengths: ["明确标准","迅速收拢权责"],
      weaknesses: ["压抑创造力","易激化矛盾"],
      motivationMethods: ["奖惩分明","晋升通道绑定绩效"],
      delegationStyle: "按科室分派，严控回报节点",
      feedbackApproach: "书面批注+例会点名",
      decisionInclusivity: "低",
      crisisManagement: "先封控后复核"
    },
    learningStyle: {
      primary: "reading",
      preferences: ["条目化手册", "案例判例集"],
      strengths: ["记忆力强", "抽取规则能力强"],
      challenges: ["同理心欠缺导致沟通阻滞"],
      motivationFactors: ["上级肯定", "指标完成"],
      retentionMethods: ["抄写与背诵"],
      environments: ["档案室", "静室"],
      adaptability: 6
    }
  }
};
