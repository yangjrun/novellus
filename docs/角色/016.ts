const renyu_character_16: Character = {
  id: "char-renyu-xugui-016",
  projectId: "proj-liashi-jiuyu",
  createdAt: new Date("2025-09-17T00:00:00Z"),
  updatedAt: new Date("2025-09-17T00:00:00Z"),

  // 基本信息
  basicInfo: {
    name: "许桂",
    alias: ["桂姐", "分发官"],
    age: 38,
    gender: "female",
    occupation: "妇女互助队头 / 互助仓分发官（白泥系乡社联队）",
    socialStatus: "良籍·乡社职事（选任）"
  },

  // 外貌特征
  appearance: {
    height: "166cm",
    weight: "55kg",
    hairColor: "乌黑（高髻，常束头巾）",
    eyeColor: "深褐",
    skinTone: "麦色",
    bodyType: "结实·耐劳型",
    specialMarks: ["左前臂缝合旧疤（汛夜救援所致）", "指腹厚茧", "颈侧有淡绿色叶脉胎记"],
    clothingStyle: "粗布窄袖+防水围裙，肩挎分发牌与口袋清单，雨天披油布蓑衣"
  },

  // 性格特质
  personality: {
    coreTraits: ["干练", "共情", "原则清晰", "韧性强"],
    values: ["人命优先", "公开公平", "弱者优先序"],
    beliefs: ["秩序来自被看见的规则", "救急不问来处"],
    fears: ["分发现场踩踏与二次伤害", "被票粮绑架以换配合"],
    desires: ["把‘三线分发’写进县内应急常规", "建成乡社妇幼护站网络"],
    weaknesses: ["对官样冗词不耐", "对拖延零容忍易起冲突"],
    strengths: ["现场组织", "人群疏导", "情绪安抚与小儿急救"]
  },

  // 背景故事
  background: {
    birthplace: "白泥村（人域·南环水网）",
    family: "夫赵渔常年在外跑渔工，一女一子在乡学；与婆母同住",
    childhood: "出身圩丁之家，自幼随父母巡圩帮工，练就强体力与秩序感",
    education: "乡学基础；后随温砚与白简学‘预审礼’与‘白话条款’；急救短训一季",
    importantEvents: [
      "20岁：汛夜入水系竹排救出三人，受圩里嘉奖",
      "27岁：发起‘妇女互助队’，建立孕幼与老弱优先序",
      "33岁：试行‘三线分发’（孕幼线/老弱线/壮劳线）化解一次粮队挤压",
      "37岁：联合乡祠把‘事实墙·分发榜’上墙公开"
    ],
    trauma: ["早年一位抱婴妇在拥挤中跌倒受伤，自责多年", "封关挤兑夜目睹推搡导致骨折"],
    achievements: [
      "三线分发流程卡（含撤退通道）",
      "‘静息五息’安抚口令推行至三村",
      "妇幼护站样表（清单化需求登记）"
    ]
  },

  // 能力技能
  abilities: {
    professionalSkills: [
      "应急分发与队列组织",
      "人群疏导与安全线设置",
      "妇幼关怀与基础急救",
      "物资登记与公开榜制作"
    ],
    specialTalents: [
      "人群温度感（能迅速定位情绪焦点）",
      "以三个手势完成转弯/停步/让道的统一"
    ],
    languages: ["人域乡言", "通域语", "天域官音（事务口）"],
    learningAbility: "场景—清单化极强；以‘一句口令+一个动作’固化流程",
    socialSkills: "强现场影响力；能把对立人群带回秩序",
    practicalSkills: [
      "队形·编织（以绳桩与手势编出人流通道）",
      "静息·五息（群体安抚口令）",
      "止血包扎/固定/婴幼儿抱持法",
      "事实墙·分发榜快速制作"
    ]
  },

  // 人际关系
  relationships: {
    family: [
      { name: "赵渔", relationship: "夫妻", description: "外出渔工，淡季回乡支援分发", importance: "medium" },
      { name: "婆母许氏", relationship: "婆媳", description: "照看孙辈，协助登记", importance: "medium" },
      { name: "赵小芹/赵小河", relationship: "母女/母子", description: "在乡学，常参与张贴分发榜", importance: "low" }
    ],
    friends: [
      { name: "梁守圩", relationship: "同盟", description: "里正，分发与巡圩配套的搭档", importance: "high" },
      { name: "白简", relationship: "顾问", description: "把分发规则写成白话条款", importance: "high" }
    ],
    lovers: [],
    enemies: [
      { name: "沈合", relationship: "对立", description: "多次以‘产量优先’挤占通道，冲突频发", importance: "high" },
      { name: "何舫", relationship: "利益冲突", description: "反对以票粮绑定‘配合度’，被其公开驳斥", importance: "medium" }
    ],
    mentors: [
      { name: "温砚", relationship: "礼学导师", description: "以‘预审礼’加持分发现场的合法性", importance: "high" }
    ],
    subordinates: [
      { name: "妇女互助队", relationship: "队头-队员", description: "十五人轮值，熟练三线分发与静息五息", importance: "high" }
    ],
    socialCircle: ["乡祠礼生", "义庄与医徒", "书场志愿者", "中立仓守仓人"]
  },

  // 生活状况
  lifestyle: {
    residence: "白泥村圩内砖屋（靠近互助仓与乡祠）",
    economicStatus: "朴素稳定（公职贴补+自家小田）",
    dailyRoutine: "清晨点队→核对分发清单→上午看场→午后探访弱户→傍晚复盘上榜→夜里训练手势口令",
    hobbies: ["编竹牌与绳标", "收集各地排队手势图", "教孩子吹口哨口令"],
    foodPreferences: ["热汤粥", "野菜饼", "盐渍小鱼"],
    entertainment: ["庙会看戏", "在书场听白话合同课"]
  },

  // 心理状态 (增强版)
  psychology: {
    mentalHealth: "高功能；在大规模分发前后出现短暂疲惫与失眠",
    mentalHealthStatus: "good",
    copingMechanisms: [
      { type: "healthy", strategy: "演练‘三线分发’与撤退通道", triggers: ["汛前","封关期"], effectiveness: 9, frequency: "frequent" },
      { type: "adaptive", strategy: "以‘静息五息’自我调节", triggers: ["场面失控迹象"], effectiveness: 7, frequency: "occasional" }
    ],
    emotionalPatterns: [
      { emotion: "焦虑→镇定", triggers: ["拥挤", "哭喊"], intensity: 6, duration: "brief", expression: "口令短促、手势明确", impact: "迅速恢复秩序" }
    ],
    trauma: [
      { type: "adult", event: "分发踩踏致伤", age: 24, severity: "severe", status: "healing", triggers: ["尖叫声","密集脚步声"], effects: ["手心出汗","短时呼吸急促"], copingMethods: ["分区/留白线", "静息五息带队"] }
    ],
    growthNeeds: ["县署备案‘三线分发+撤退权’标准", "常备物资与志愿队训练经费"],
    cognitivePatterns: [
      { type: "belief", description: "弱者优先序是秩序起点", situations: ["分发/撤离"], impact: "positive", awareness: "conscious" },
      { type: "assumption", description: "口令>说理（在现场）", situations: ["危机管控"], impact: "mixed", awareness: "conscious" }
    ],
    stressResponses: [
      {
        stressor: "大批人潮+舆情起哄",
        physicalResponse: ["肩背僵硬","喉部紧张"],
        emotionalResponse: ["急躁后迅速收束"],
        behavioralResponse: ["划白线/增手势位","请求第三方见证"],
        cognitiveResponse: ["聚焦核心三步：分区—让道—撤退"],
        timeframe: "事件全程"
      }
    ],
    emotionalIntelligence: {
      selfAwareness: 7, selfRegulation: 8, motivation: 8, empathy: 8, socialSkills: 7,
      strengths: ["情绪安抚","秩序恢复"], weaknesses: ["对拖延零容忍，言辞偏硬"]
    },
    psychologicalDefenses: ["理智化", "升华（把痛转流程）"],
    mentalHealthHistory: [
      { date: new Date("2025-06-20"), status: "good", notes: "完成两场万人次分发零踩踏，流程被邻村采纳" }
    ]
  },

  // 故事功能
  storyRole: {
    characterType: "supporting",
    characterArc: "民间组织者 → 关键秩序节点 → 制度化共创者",
    conflictRole: "分发与撤离的执行枢纽/把‘人命优先’落到地面的铁手与温手",
    symbolism: "叶脉胎记=滋养与连结；绳桩与白线=秩序的可见边界",
    readerConnection: "看得见、靠得住的‘现场女队头’：快、稳、心软但不乱"
  },

  // 特殊设定 (增强版)
  specialSettings: {
    worldBuilding: "裂世九域·法则链纪元",
    culturalBackground: "人域-乡社/互助文化（与乡祠/行会/中立仓耦合）",
    historicalContext: "裂世后时代",
    technologyLevel: "链工学-中（场务工具化）",
    magicAbilities:
      "法则链：主[木] 副[水]；契合度:3；禁忌:[以粮施压换服从, 以线锁困异议者]；代表术式:[队形·编织(以木链意象引导队列成带), 芽脉·安抚(微调群情阈值), 水息·稳心(同步呼吸口令)]; 代价: 过用后喉部沙哑、脱水与短时‘同理疲劳’",
    culturalIdentity: {
      primaryCulture: "人域-乡社文化",
      subcultures: ["妇女互助队","义庄/医徒网络","书场志愿者"],
      culturalValues: ["守望相助","公开公平","弱者优先"],
      culturalConflicts: ["与票行‘配额换粮’冲突","与官署‘效率压人’冲突"],
      assimilationLevel: 8,
      culturalPride: 7,
      traditionalPractices: ["汛前‘分线礼’", "分发后谢圩小礼"],
      modernAdaptations: ["分发榜上墙与镜像存证", "白线可卷携带式标志套件"]
    },
    religiousBeliefs: {
      religion: "源祖/河祠并修（务实派）",
      denomination: "乡祠",
      devotionLevel: 4,
      practices: ["开汛小礼", "谢圩献羹"],
      beliefs: ["滋养与秩序相依"],
      doubts: ["繁礼不救急"],
      spiritualExperiences: ["在最乱的场面里听见‘水息’的节拍，作为口令节奏来源"],
      religionInLife: "important"
    },
    languageProfile: {
      nativeLanguage: "人域乡言",
      fluentLanguages: ["通域语","天域官音（事务口）"],
      learningLanguages: [],
      accents: ["乡音清脆、口令分明"],
      dialectVariations: [],
      speechPatterns: [
        {
          characteristic: "三口令一动作",
          examples: ["孕幼靠里", "老弱跟线", "壮劳让道——走"],
          frequency: "often",
          context: ["分发","撤离"],
          origin: "互助队训练"
        }
      ],
      languageBarriers: ["长篇礼仪腔"],
      communicationPreferences: ["口令+手势+白线图"]
    },
    behaviorPatterns: [
      { category: "professional", behavior: "分发前五分钟演练‘三线分发’", frequency: "situational", triggers: ["大规模分发前"], context: ["互助仓/广场"], development: "事故率显著下降" },
      { category: "professional", behavior: "事实墙公示清单与时窗", frequency: "daily", triggers: ["封关期","汛期"], context: ["乡祠/互助仓"], development: "提高信任度" },
      { category: "personal", behavior: "夜间带队做‘静息五息’复盘", frequency: "weekly", triggers: ["大场后"], context: ["乡祠"], development: "缓解同理疲劳" }
    ],
    rolePlayingNotes: [
      "Domain: 人域",
      "KeyLocations: 白泥村互助仓 / 乡祠广场 / 圩堤 / 三环亭（公示点）",
      "F*: F1/F3/F4/F10/F14/F18/F19/F20",
      "口头禅: '弱者先行' '白线之内，人人见’"
    ]
  },

  // 角色成长轨迹 (新增)
  characterArc: {
    currentStage: "③ 试炼与盟友（现场执行中枢）→ ④ 深渊（分发+押解叠加危机）",
    developmentGoals: [
      {
        id: "xg-g1",
        category: "social",
        goal: "将‘三线分发+撤退权+事实墙公示’写入县级应急标准并备案",
        motivation: "把经验变成救命的规程",
        timeline: "三个月",
        obstacles: ["官署效率导向","票行配额干预","设备经费不足"],
        progress: 40,
        priority: "high"
      }
    ],
    growthMilestones: [
      {
        id: "xg-m1",
        title: "首场县级‘标准化分发’落地",
        description: "在三环亭旁完成万人次分发零踩踏",
        significance: "树立可复制样本",
        prerequisites: ["手势训练100%", "白线套件齐备"],
        relatedGoals: ["xg-g1"],
        status: "planned"
      }
    ],
    personalityChanges: [
      {
        id: "xg-p1",
        trait: "对权力交涉方式",
        oldValue: "正面硬顶",
        newValue: "以程序与见证绕开硬碰",
        trigger: "一次传唤与白简点拨",
        timeline: "一月",
        significance: "moderate",
        stability: "developing"
      }
    ],
    skillProgression: [
      {
        skill: "队形·编织（大场版）",
        category: "professional",
        currentLevel: 6,
        targetLevel: 8,
        learningMethod: "与护运队/乡祠联训+沙盘演练",
        timeframe: "两月",
        obstacles: ["人员轮值疲劳","物资短缺"],
        mentors: ["梁守圩","鲁三","温砚"]
      }
    ],
    relationshipEvolution: [
      {
        relationshipId: "rel-liangshouwei-synergy",
        personName: "梁守圩",
        evolutionType: "strengthening",
        previousState: "协作",
        currentState: "制度合作者",
        triggers: ["村规上墙+分发标准化"],
        timeline: "持续",
        significance: "乡社执行力大幅提升"
      }
    ],
    internalConflicts: [
      {
        id: "xg-ic1",
        title: "公平 vs. 速度",
        description: "严格核对与快速通过的取舍",
        conflictingValues: ["公平","效率"],
        emotionalImpact: "自责与焦虑交替",
        manifestations: ["夜里复盘清单", "次日加练手势"],
        resolutionAttempts: ["分区复核", "事后抽检公示"],
        status: "active"
      }
    ],
    externalChallenges: [
      {
        id: "xg-ec1",
        title: "押解与分发同场冲突",
        description: "官署押解穿越分发线造成拥堵与恐慌",
        source: "society",
        difficulty: 8,
        timeframe: "汛季核心周",
        resources: ["白线套件","静息口令","护运队协同","乡祠见证"],
        strategies: ["划‘生命走廊’与‘押解绕行’", "事实墙即时公示", "中立仓暂存"],
        status: "upcoming"
      }
    ]
  },

  // 互动行为模式 (新增)
  behaviorProfile: {
    communicationStyle: {
      primaryStyle: "assertive",
      verbalCharacteristics: ["口令短句", "结论先行", "弱者优先序明确"],
      nonverbalCharacteristics: ["手势清晰", "指地划线"],
      listeningStyle: "active",
      feedbackStyle: "三点式（分区/让道/撤退）",
      conflictCommunication: "请见证→划白线→分批通过",
      culturalInfluences: ["乡社口令文化","互助队训练"]
    },
    bodyLanguage: {
      posture: "站位靠前而稳",
      gestures: ["掌心向下示‘稳’", "两指并拢示‘进/停’", "手背朝外示‘让道’"],
      facialExpressions: ["冷静", "偶显坚硬"],
      eyeContact: "moderate",
      personalSpace: "normal",
      nervousHabits: ["拇指摩挲绳标", "清嗓"],
      confidenceIndicators: ["步伐有节奏", "语速稳定"],
      culturalVariations: ["对长者放慢语速，对孩童蹲下交流"]
    },
    decisionMaking: {
      approach: "analytical",
      timeframe: "quick",
      informationGathering: "人流密度/出口宽度/弱者比例三指标",
      riskTolerance: 4,
      influences: ["人命优先","公开公平"],
      biases: ["对拖延零容忍"],
      decisionHistory: ["三线分发成功落地", "两次紧急撤退零伤亡"]
    },
    conflictResponse: {
      primaryStyle: "collaborating",
      escalationTriggers: ["强闯优先序", "押解穿线"],
      deescalationMethods: ["白线重划", "请祠司/护运见证"],
      emotionalReactions: ["短怒后收束"],
      physicalReactions: ["喉紧","背僵"],
      recoveryMethods: ["静息五息", "热姜汤"],
      conflictHistory: ["多起冲突转为有序通过"]
    },
    socialBehavior: {
      socialEnergy: "ambivert",
      groupDynamics: "现场核心，能快速分工",
      socialRoles: ["分发官","疏导者","安抚者"],
      boundaryManagement: "亲友也按序，边界清晰",
      socialAnxieties: ["在官场长篇演说"],
      socialStrengths: ["把混乱变秩序", "让弱者被看见"],
      networkingStyle: "乡社-护运-祠司-志愿者四角网络",
      socialAdaptability: 8
    },
    workStyle: {
      productivity: "morning",
      environment: "bustling",
      organization: "highly_organized",
      taskManagement: "清单+标志套件+上墙公示",
      collaboration: "与里正/护运/祠司密切协同",
      innovation: "把手势与白线工具化",
      stressManagement: "分段休息+口令呼吸"
    },
    leadershipStyle: {
      type: "servant",
      strengths: ["以身作则", "照顾弱者", "把原则变流程"],
      weaknesses: ["言辞偏硬", "对拖延不耐"],
      motivationMethods: ["公示表扬", "轮班优先选择权"],
      delegationStyle: "按熟练度与心态分配岗位",
      feedbackApproach: "事后三点复盘卡",
      decisionInclusivity: "中高",
      crisisManagement: "先划生命走廊→再分区→后清账"
    },
    learningStyle: {
      primary: "kinesthetic",
      preferences: ["现场演练","图示学习"],
      strengths: ["动作记忆","人群感知"],
      challenges: ["冗长文书"],
      motivationFactors: ["护人命","护乡社"],
      retentionMethods: ["口令卡","白线图"],
      environments: ["乡祠广场","互助仓","三环亭小间"],
      adaptability: 8
    }
  }
};
