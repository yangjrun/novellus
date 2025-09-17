const renyu_character_18: Character = {
  id: "char-renyu-lucheng-018",
  projectId: "proj-liashi-jiuyu",
  createdAt: new Date("2025-09-17T00:00:00Z"),
  updatedAt: new Date("2025-09-17T00:00:00Z"),

  // 基本信息
  basicInfo: {
    name: "陆澄",
    alias: ["小澄", "光字生"],
    age: 20,
    gender: "male",
    occupation: "九环书院附校青年 / 链算所实习 / 三环亭可视化讲解员",
    socialStatus: "良籍·书院附校生（链算所挂名学徒）"
  },

  // 外貌特征
  appearance: {
    height: "176cm",
    weight: "60kg",
    hairColor: "乌黑（碎发）",
    eyeColor: "深褐",
    skinTone: "偏白",
    bodyType: "清瘦·久坐型",
    specialMarks: ["右眼下淡痣", "指腹常有墨迹与蜡印残渍", "长时施术后眼角细红纹"],
    clothingStyle: "浅灰学袍+束袖，外披短斗篷；腰挂小型影封盒与光字板"
  },

  // 性格特质
  personality: {
    coreTraits: ["理性", "腼腆", "好奇", "较真"],
    values: ["可复核", "公开透明", "弱者可理解"],
    beliefs: ["复杂问题需要‘看得见’才有共识"],
    fears: ["可视化被篡改用于操控舆情", "在大场合失手出错"],
    desires: ["让‘证据可视化’成为三环亭标配流程", "完成一本《给普通人的链算图解》"],
    weaknesses: ["社交场紧张", "过度打磨导致拖延"],
    strengths: ["抽象转译可视化", "数据洁癖与交叉验证", "耐心讲解"]
  },

  // 背景故事
  background: {
    birthplace: "九埠市书院街（人域）",
    family: "父为木匠，母为针线匠；家境清寒但重学",
    childhood: "常在报馆边驻足抄要点，靠抄写赚纸钱；对‘图’有天然敏感",
    education: "九环书院附校链算方向；在链算所做可视化与镜账辅助",
    importantEvents: [
      "16岁：用自制光字板把一场口角视觉化，促成和解",
      "18岁：入链算所为志愿助理，参与‘镜账’图解实验",
      "19岁：在三环亭首创‘证据时间线光幕’，当场降低对骂",
      "20岁：与裴青笺、白荟合作，将‘事实墙+光字时间线’联动"
    ],
    trauma: [
      "一次公开讲解被人故意打断、投掷杂物，留下上台恐惧",
      "封关期看见人群踩踏影像，长期自责‘可视化不够早’"
    ],
    achievements: [
      "《光字二十式》小册（证据可视化手法）",
      "‘三点一线’证据时间线模板（人/时/物）",
      "镜账可视化组件（与白简、贺砚舟共制）"
    ]
  },

  // 能力技能
  abilities: {
    professionalSkills: [
      "证据可视化建模（时间线/关系图/地形图）",
      "镜账对照与数据清洗",
      "公众讲解与流程演示",
      "影封与在场联动的显示控制"
    ],
    specialTalents: [
      "一眼抓关键变量并转为‘三步图’",
      "空间方位感强，能在现场快速画出安全动线"
    ],
    languages: ["通域语", "人域乡言", "天域官音（学术/礼仪口）"],
    learningAbility: "阅读-实验-教学三连，迁移与复盘能力强",
    socialSkills: "书面表达强，口头在小场景更自如；能让普通人听懂术语",
    practicalSkills: [
      "光字·投演（把证据转为可视光幕）",
      "镜谱·映证（把镜账片段嵌入画面）",
      "地形·白线（在广场投射‘生命走廊’）"
    ]
  },

  // 人际关系
  relationships: {
    family: [
      { name: "陆父", relationship: "父子", description: "木匠，为其做便携光字板木框", importance: "medium" },
      { name: "陆母", relationship: "母子", description: "针线匠，缝制耐用工具袋", importance: "low" }
    ],
    friends: [
      { name: "裴青笺", relationship: "合作/朋友", description: "事实墙联动的固定搭档", importance: "high" },
      { name: "白荟", relationship: "业务同盟", description: "公开交割可视化协作", importance: "high" }
    ],
    lovers: [],
    enemies: [
      { name: "何舫", relationship: "制度博弈", description: "反感其把账目‘亮在光里’削弱话语权", importance: "medium" }
    ],
    mentors: [
      { name: "白简", relationship: "导师", description: "把复杂条款转为白话与图解的引路人", importance: "high" },
      { name: "温砚", relationship: "礼学引导", description: "‘预审礼+可视化’的礼序框定", importance: "medium" }
    ],
    subordinates: [
      { name: "链算所实习同学两名", relationship: "组长-组员", description: "负责数据清洗与投影设备", importance: "low" }
    ],
    socialCircle: ["书院学友", "链算所助理", "三环亭志愿者", "中立仓见证队"]
  },

  // 生活状况
  lifestyle: {
    residence: "书院街合租小阁楼（步行至三环亭）",
    economicStatus: "清贫但稳定（助学金+小稿费）",
    dailyRoutine: "清晨练手绘→午前数据清洗→午后现场勘画→傍晚演示调试→夜里复盘与写图解",
    hobbies: ["手绘图解", "收集旧地形图", "做纸质模型"],
    foodPreferences: ["清淡热汤", "面食", "豆干"],
    entertainment: ["书场听公案", "与学友做推演小剧场"]
  },

  // 心理状态 (增强版)
  psychology: {
    mentalHealth: "轻社交焦虑伴演示前紧张；总体稳定",
    mentalHealthStatus: "good",
    copingMechanisms: [
      { type: "healthy", strategy: "演示前三次走场+预置问题卡", triggers: ["公开讲解","大场冲突"], effectiveness: 8, frequency: "frequent" },
      { type: "adaptive", strategy: "以技术细节转移注意", triggers: ["被起哄","质疑"], effectiveness: 6, frequency: "occasional" }
    ],
    emotionalPatterns: [
      { emotion: "紧张→专注", triggers: ["上台前30秒","哨声与人群噪音"], intensity: 6, duration: "brief", expression: "深呼吸+目视白线", impact: "进入讲解节奏" }
    ],
    trauma: [
      { type: "adolescent", event: "公开讲解被投掷物砸中", age: 17, severity: "moderate", status: "healing", triggers: ["嘘声","杂物砸地声"], effects: ["手抖","心跳加快"], copingMethods: ["与护运队演练入场保护", "先投白线再讲话"] }
    ],
    growthNeeds: ["县署备案‘证据可视化标准’", "稳定设备与经费支持"],
    cognitivePatterns: [
      { type: "belief", description: "图胜千言，但图必须对应原证", situations: ["听证","纠纷"], impact: "positive", awareness: "conscious" },
      { type: "bias", description: "偏好图表而忽视口才", situations: ["辩论"], impact: "mixed", awareness: "conscious" }
    ],
    stressResponses: [
      {
        stressor: "封关期/押解穿场+人群起哄",
        physicalResponse: ["眼压上升","太阳穴胀痛"],
        emotionalResponse: ["焦灼→冷静"],
        behavioralResponse: ["先投‘生命走廊’与时间线", "请求见证双签"],
        cognitiveResponse: ["把叙述转为坐标点与箭头"],
        timeframe: "事件当场"
      }
    ],
    emotionalIntelligence: {
      selfAwareness: 6, selfRegulation: 7, motivation: 8, empathy: 7, socialSkills: 6,
      strengths: ["把复杂讲清楚"], weaknesses: ["开场慢热","被动交流"]
    },
    psychologicalDefenses: ["理智化", "转译（把情绪转换为图）"],
    mentalHealthHistory: [
      { date: new Date("2025-07-05"), status: "good", notes: "完成‘三点一线’模板v2，三环亭采用" }
    ]
  },

  // 故事功能
  storyRole: {
    characterType: "supporting",
    characterArc: "书斋学生 → 现场可视化讲解员 → 证据制度化推动者",
    conflictRole: "‘事实墙—时间线—镜账’三联的技术枢纽",
    symbolism: "光字板=把真相照亮；白线=安全的可见边界",
    readerConnection: "社恐但靠谱的年轻技术派：笨拙又有用"
  },

  // 特殊设定 (增强版)
  specialSettings: {
    worldBuilding: "裂世九域·法则链纪元",
    culturalBackground: "人域-书院/链算文化（与三环亭/中立仓/报馆耦合）",
    historicalContext: "裂世后时代",
    technologyLevel: "链工学-中（投影/影封/镜账联动）",
    magicAbilities:
      "法则链：主[光] 副[因果]；契合度:2；禁忌:[以可视化误导事实, 以光幕煽动群情]；代表术式:[光字·投演(把证据转为图像), 镜谱·映证(把镜账碎片嵌入画面), 推演·回廊(以因果箭头展示前后果)]; 代价: 长时施术诱发偏头痛、眼压升高与短暂残影",
    culturalIdentity: {
      primaryCulture: "人域-书院文化",
      subcultures: ["链算所实习圈","三环亭志愿者","中立仓见证协作"],
      culturalValues: ["求真","可证","可复用"],
      culturalConflicts: ["与票行‘黑箱’冲突", "与官署‘面子图表’冲突"],
      assimilationLevel: 6,
      culturalPride: 6,
      traditionalPractices: ["讲解前‘点灯礼’（点亮光字板）"],
      modernAdaptations: ["模板化图解与开源清单"]
    },
    religiousBeliefs: {
      religion: "天命信仰（理性-明证派）",
      denomination: "书院私祠",
      devotionLevel: 2,
      practices: ["讲解前默数三息"],
      beliefs: ["光能照见秩序，但秩序须能检验"],
      doubts: ["繁礼耽误执行"],
      spiritualExperiences: ["夜半对着墙练‘光字’，像有一道线把思路拉直"],
      religionInLife: "minimal"
    },
    languageProfile: {
      nativeLanguage: "通域语",
      fluentLanguages: ["人域乡言","天域官音（学术/礼仪口）"],
      learningLanguages: [],
      accents: ["书院清音（停顿分明）"],
      dialectVariations: [],
      speechPatterns: [
        { characteristic: "图先于话", examples: ["我们先看这条线", "这里是分叉点", "箭头代表‘若…则…’"], frequency: "often", context: ["讲解","听证"], origin: "链算所训练" }
      ],
      languageBarriers: ["即兴辩难弱"],
      communicationPreferences: ["投影+白话+实例"]
    },
    behaviorPatterns: [
      { category: "professional", behavior: "固定使用‘三点一线’模板自检", frequency: "daily", triggers: ["制作光幕前"], context: ["书院/三环亭"], development: "错误率下降" },
      { category: "professional", behavior: "演示前三次走场并布‘白线’", frequency: "situational", triggers: ["大场讲解"], context: ["广场/厅堂"], development: "秩序提升" },
      { category: "personal", behavior: "睡前手绘一页图解", frequency: "daily", triggers: ["复盘"], context: ["合租阁楼"], development: "知识沉淀" }
    ],
    rolePlayingNotes: [
      "Domain: 人域",
      "KeyLocations: 九环书院附校 / 三环亭 / 链算所 / 中立仓",
      "F*: F5/F6/F12/F17/F19",
      "口头禅: '先把图画出来' '看这条线'"
    ]
  },

  // 角色成长轨迹 (新增)
  characterArc: {
    currentStage: "③ 试炼与盟友（技术枢纽）",
    developmentGoals: [
      {
        id: "lc-g1",
        category: "professional",
        goal: "把‘证据可视化标准’写成三环亭流程附件并通过备案",
        motivation: "让普通人也能一眼看懂真相",
        timeline: "两个月",
        obstacles: ["设备与经费", "既得利益阻挠", "个人演示焦虑"],
        progress: 35,
        priority: "high"
      }
    ],
    growthMilestones: [
      {
        id: "lc-m1",
        title: "首次县级标准化‘光字时间线’听证",
        description: "三环亭大案用统一模板展示证据，观众理解度显著提升",
        significance: "技术→制度的跨越",
        prerequisites: ["模板评审通过","设备调试完毕"],
        relatedGoals: ["lc-g1"],
        status: "planned"
      }
    ],
    personalityChanges: [
      {
        id: "lc-p1",
        trait: "舞台胆量",
        oldValue: "怯场",
        newValue: "小紧张可控",
        trigger: "与护运队协作完成一次高压演示",
        timeline: "一月",
        significance: "moderate",
        stability: "developing"
      }
    ],
    skillProgression: [
      {
        skill: "推演·回廊（因果箭头）",
        category: "artistic",
        currentLevel: 5,
        targetLevel: 7,
        learningMethod: "与白简共修案例库+与贺砚舟联通在场印",
        timeframe: "两月",
        obstacles: ["偏头痛","数据缺口"],
        mentors: ["白简","贺砚舟"]
      }
    ],
    relationshipEvolution: [
      {
        relationshipId: "rel-peiqingjian-bridge",
        personName: "裴青笺",
        evolutionType: "strengthening",
        previousState: "素材互助",
        currentState: "制度合作者（事实墙+光幕联动）",
        triggers: ["大案演示成功"],
        timeline: "持续",
        significance: "公众理解路径成型"
      }
    ],
    internalConflicts: [
      {
        id: "lc-ic1",
        title: "准确 vs. 易懂",
        description: "过度简化会不会误导？",
        conflictingValues: ["科学严谨","公众可读"],
        emotionalImpact: "反复打磨而拖延",
        manifestations: ["不断改图", "迟迟不发布"],
        resolutionAttempts: ["双版本图（学术/大众）", "引入第三方复核"],
        status: "active"
      }
    ],
    externalChallenges: [
      {
        id: "lc-ec1",
        title: "舆情扭曲与黑箱阻挠",
        description: "光幕被指‘导向性’、设备被卡",
        source: "society",
        difficulty: 6,
        timeframe: "两个月",
        resources: ["报馆平台","中立仓见证","书院背书"],
        strategies: ["开源模板与样例库", "全程在场印与影封"],
        status: "upcoming"
      }
    ]
  },

  // 互动行为模式 (新增)
  behaviorProfile: {
    communicationStyle: {
      primaryStyle: "indirect",
      verbalCharacteristics: ["图先于话", "比喻简短", "结论配证据"],
      nonverbalCharacteristics: ["指图而非指人", "呼吸节拍稳定"],
      listeningStyle: "active",
      feedbackStyle: "三点式（哪里不懂/为什么/怎么做）",
      conflictCommunication: "请在场→投时间线→逐点回应",
      culturalInfluences: ["书院讲解风", "三环亭程序语境"]
    },
    bodyLanguage: {
      posture: "站位略后但稳定",
      gestures: ["两指并拢划线", "掌心向下示稳"],
      facialExpressions: ["专注", "开场略紧张后放松"],
      eyeContact: "moderate",
      personalSpace: "normal",
      nervousHabits: ["捻光字板边角", "清嗓"],
      confidenceIndicators: ["语速渐稳", "停顿恰当"],
      culturalVariations: ["对长者放慢语速，对孩童蹲下示图"]
    },
    decisionMaking: {
      approach: "analytical",
      timeframe: "moderate",
      informationGathering: "多源交叉+镜账对照",
      riskTolerance: 3,
      influences: ["可复核", "公众可读", "安全"],
      biases: ["偏好图胜言"],
      decisionHistory: ["三场听证可视化成功", "一次延迟发布避免误导"]
    },
    conflictResponse: {
      primaryStyle: "collaborating",
      escalationTriggers: ["扣帽子/打断演示", "设备被掐断"],
      deescalationMethods: ["切到离线白板", "请见证双签继续"],
      emotionalReactions: ["短暂结巴后回稳"],
      physicalReactions: ["指尖发冷", "太阳穴跳痛"],
      recoveryMethods: ["闭眼三息", "热毛巾敷眼"],
      conflictHistory: ["一次起哄后以‘白线+图示’重整秩序"]
    },
    socialBehavior: {
      socialEnergy: "introverted",
      groupDynamics: "当‘翻译器’，把复杂转通俗",
      socialRoles: ["讲解员","模板维护者"],
      boundaryManagement: "坚持‘图不离证’红线",
      socialAnxieties: ["即兴辩论"],
      socialStrengths: ["清晰表达", "耐心答疑"],
      networkingStyle: "书院-链算所-三环亭-中立仓四角",
      socialAdaptability: 7
    },
    workStyle: {
      productivity: "evening",
      environment: "quiet",
      organization: "highly_organized",
      taskManagement: "模板库+版本控制+清单化复核",
      collaboration: "与记者/见证/护运跨职协作",
      innovation: "标准化可视化模板与开源图解",
      stressManagement: "数息法+热敷眼"
    },
    leadershipStyle: {
      type: "situational",
      strengths: ["以清晰带队", "工具化赋能"],
      weaknesses: ["临场话术不足"],
      motivationMethods: ["署名与模板入库", "公开致谢"],
      delegationStyle: "按模块分工（清洗/绘制/演示）",
      feedbackApproach: "版本对比+复盘单",
      decisionInclusivity: "中",
      crisisManagement: "先画安全线→再画证据线→后说判断"
    },
    learningStyle: {
      primary: "visual",
      preferences: ["图解/沙盘/示例"],
      strengths: ["抽象化与再表达"],
      challenges: ["纯口头辩论"],
      motivationFactors: ["让大众理解", "减少误解"],
      retentionMethods: ["每日一图", "案例卡片"],
      environments: ["书院小室","三环亭","中立仓会议角"],
      adaptability: 8
    }
  }
};
