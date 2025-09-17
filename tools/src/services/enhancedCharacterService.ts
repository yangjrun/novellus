import { Character } from "../types/index";
import { storage } from "@utils/storage";

// 增强版角色服务，包含AI辅助功能
export class EnhancedCharacterService {
  private readonly storageKey = "novellus-enhanced-characters";

  async getAllCharacters(): Promise<Character[]> {
    try {
      const characters =
        (await storage.getItem<Character[]>(this.storageKey)) || [];
      return characters.map(this.deserializeCharacter);
    } catch (error) {
      console.error("获取角色列表失败:", error);
      return [];
    }
  }

  async getCharacterById(id: string): Promise<Character | null> {
    try {
      const characters = await this.getAllCharacters();
      return characters.find((character) => character.id === id) || null;
    } catch (error) {
      console.error("获取角色失败:", error);
      return null;
    }
  }

  async saveCharacter(character: Character): Promise<void> {
    try {
      const characters = await this.getAllCharacters();
      const existingIndex = characters.findIndex((c) => c.id === character.id);

      const serializedCharacter = this.serializeCharacter({
        ...character,
        updatedAt: new Date(),
      });

      if (existingIndex >= 0) {
        characters[existingIndex] = serializedCharacter;
      } else {
        characters.push(serializedCharacter);
      }

      await storage.setItem(this.storageKey, characters);
    } catch (error) {
      console.error("保存角色失败:", error);
      throw error;
    }
  }

  async deleteCharacter(id: string): Promise<void> {
    try {
      const characters = await this.getAllCharacters();
      const filteredCharacters = characters
        .filter((character) => character.id !== id)
        .map(this.serializeCharacter);

      await storage.setItem(this.storageKey, filteredCharacters);
    } catch (error) {
      console.error("删除角色失败:", error);
      throw error;
    }
  }

  // 创建角色模板
  createCharacterTemplate(
    projectId: string,
    type: Character["storyRole"]["characterType"] = "protagonist"
  ): Character {
    const templates = this.getCharacterTemplates();
    const template = templates[type];

    return {
      id: this.generateId(),
      projectId,
      createdAt: new Date(),
      updatedAt: new Date(),
      ...template,
    };
  }

  // 获取角色模板库
  private getCharacterTemplates() {
    return {
      protagonist: {
        basicInfo: {
          name: "",
          alias: [],
          age: "",
          gender: "",
          occupation: "",
          socialStatus: "",
        },
        appearance: {
          height: "",
          weight: "",
          hairColor: "",
          eyeColor: "",
          skinTone: "",
          bodyType: "",
          specialMarks: [],
          clothingStyle: "",
        },
        personality: {
          coreTraits: ["勇敢", "决心坚定"],
          values: ["正义", "保护弱者"],
          beliefs: ["善有善报"],
          fears: ["失去所爱的人"],
          desires: ["实现目标", "成长"],
          weaknesses: ["过于冲动"],
          strengths: ["坚持不懈", "富有同情心"],
        },
        background: {
          birthplace: "",
          family: "",
          childhood: "",
          education: "",
          importantEvents: [],
          trauma: [],
          achievements: [],
        },
        abilities: {
          professionalSkills: [],
          specialTalents: [],
          languages: [],
          learningAbility: "",
          socialSkills: "",
          practicalSkills: [],
        },
        relationships: {
          family: [],
          friends: [],
          lovers: [],
          enemies: [],
          mentors: [],
          subordinates: [],
          socialCircle: [],
        },
        lifestyle: {
          residence: "",
          economicStatus: "",
          dailyRoutine: "",
          hobbies: [],
          foodPreferences: [],
          entertainment: [],
        },
        psychology: {
          mentalHealth: "稳定",
          mentalHealthStatus: "good",
          copingMechanisms: [],
          emotionalPatterns: [],
          trauma: [],
          growthNeeds: [],
          cognitivePatterns: [],
          stressResponses: [],
          emotionalIntelligence: {
            selfAwareness: 5,
            selfRegulation: 5,
            motivation: 5,
            empathy: 5,
            socialSkills: 5,
            strengths: [],
            weaknesses: [],
          },
          psychologicalDefenses: [],
          mentalHealthHistory: [],
        },
        storyRole: {
          characterType: "protagonist" as const,
          characterArc: "成长型弧线",
          conflictRole: "推动故事发展",
          symbolism: "",
          readerConnection: "认同感",
        },
        specialSettings: {
          worldBuilding: "",
          culturalBackground: "",
          historicalContext: "",
          technologyLevel: "",
          magicAbilities: "",
          culturalIdentity: {
            primaryCulture: "",
            subcultures: [],
            culturalValues: [],
            culturalConflicts: [],
            assimilationLevel: 5,
            culturalPride: 5,
            traditionalPractices: [],
            modernAdaptations: [],
          },
          religiousBeliefs: {
            religion: "",
            denomination: "",
            devotionLevel: 5,
            practices: [],
            beliefs: [],
            doubts: [],
            spiritualExperiences: [],
            religionInLife: "moderate",
          },
          languageProfile: {
            nativeLanguage: "",
            fluentLanguages: [],
            learningLanguages: [],
            accents: [],
            dialectVariations: [],
            speechPatterns: [],
            languageBarriers: [],
            communicationPreferences: [],
          },
          behaviorPatterns: [],
          rolePlayingNotes: [],
        },
        characterArc: {
          currentStage: "",
          developmentGoals: [],
          growthMilestones: [],
          personalityChanges: [],
          skillProgression: [],
          relationshipEvolution: [],
          internalConflicts: [],
          externalChallenges: [],
        },
        behaviorProfile: {
          communicationStyle: {
            primaryStyle: "direct",
            verbalCharacteristics: [],
            nonverbalCharacteristics: [],
            listeningStyle: "active",
            feedbackStyle: "",
            conflictCommunication: "",
            culturalInfluences: [],
          },
          bodyLanguage: {
            posture: "",
            gestures: [],
            facialExpressions: [],
            eyeContact: "moderate",
            personalSpace: "normal",
            nervousHabits: [],
            confidenceIndicators: [],
            culturalVariations: [],
          },
          decisionMaking: {
            approach: "analytical",
            timeframe: "moderate",
            informationGathering: "",
            riskTolerance: 5,
            influences: [],
            biases: [],
            decisionHistory: [],
          },
          conflictResponse: {
            primaryStyle: "collaborating",
            escalationTriggers: [],
            deescalationMethods: [],
            emotionalReactions: [],
            physicalReactions: [],
            recoveryMethods: [],
            conflictHistory: [],
          },
          socialBehavior: {
            socialEnergy: "ambivert",
            groupDynamics: "",
            socialRoles: [],
            boundaryManagement: "",
            socialAnxieties: [],
            socialStrengths: [],
            networkingStyle: "",
            socialAdaptability: 5,
          },
          workStyle: {
            productivity: "morning",
            environment: "quiet",
            organization: "moderately_organized",
            taskManagement: "",
            collaboration: "",
            innovation: "",
            stressManagement: "",
          },
          learningStyle: {
            primary: "visual",
            preferences: [],
            strengths: [],
            challenges: [],
            motivationFactors: [],
            retentionMethods: [],
            environments: [],
            adaptability: 5,
          },
        },
      },
      antagonist: {
        basicInfo: {
          name: "",
          alias: [],
          age: "",
          gender: "",
          occupation: "",
          socialStatus: "",
        },
        appearance: {
          height: "",
          weight: "",
          hairColor: "",
          eyeColor: "",
          skinTone: "",
          bodyType: "",
          specialMarks: [],
          clothingStyle: "",
        },
        personality: {
          coreTraits: ["野心勃勃", "冷酷"],
          values: ["权力", "控制"],
          beliefs: ["强者为王"],
          fears: ["失去权力", "被击败"],
          desires: ["统治", "征服"],
          weaknesses: ["傲慢", "低估对手"],
          strengths: ["策略思维", "意志坚强"],
        },
        background: {
          birthplace: "",
          family: "",
          childhood: "",
          education: "",
          importantEvents: [],
          trauma: [],
          achievements: [],
        },
        abilities: {
          professionalSkills: [],
          specialTalents: [],
          languages: [],
          learningAbility: "",
          socialSkills: "",
          practicalSkills: [],
        },
        relationships: {
          family: [],
          friends: [],
          lovers: [],
          enemies: [],
          mentors: [],
          subordinates: [],
          socialCircle: [],
        },
        lifestyle: {
          residence: "",
          economicStatus: "",
          dailyRoutine: "",
          hobbies: [],
          foodPreferences: [],
          entertainment: [],
        },
        psychology: {
          mentalHealth: "功能性",
          mentalHealthStatus: "good" as const,
          copingMechanisms: [],
          emotionalPatterns: [],
          trauma: [],
          growthNeeds: [],
          cognitivePatterns: [],
          stressResponses: [],
          emotionalIntelligence: {
            selfAwareness: 5,
            selfRegulation: 5,
            motivation: 5,
            empathy: 5,
            socialSkills: 5,
            strengths: [],
            weaknesses: [],
          },
          psychologicalDefenses: [],
          mentalHealthHistory: [],
        },
        storyRole: {
          characterType: "antagonist" as const,
          characterArc: "堕落或固定弧线",
          conflictRole: "制造冲突",
          symbolism: "",
          readerConnection: "恐惧或理解",
        },
        specialSettings: {
          worldBuilding: "",
          culturalBackground: "",
          historicalContext: "",
          technologyLevel: "",
          magicAbilities: "",
          culturalIdentity: {
            primaryCulture: "",
            subcultures: [],
            culturalValues: [],
            culturalConflicts: [],
            assimilationLevel: 5,
            culturalPride: 5,
            traditionalPractices: [],
            modernAdaptations: [],
          },
          religiousBeliefs: {
            religion: "",
            denomination: "",
            devotionLevel: 5,
            practices: [],
            beliefs: [],
            doubts: [],
            spiritualExperiences: [],
            religionInLife: "moderate",
          },
          languageProfile: {
            nativeLanguage: "",
            fluentLanguages: [],
            learningLanguages: [],
            accents: [],
            dialectVariations: [],
            speechPatterns: [],
            languageBarriers: [],
            communicationPreferences: [],
          },
          behaviorPatterns: [],
          rolePlayingNotes: [],
        },
        characterArc: {
          currentStage: "",
          developmentGoals: [],
          growthMilestones: [],
          personalityChanges: [],
          skillProgression: [],
          relationshipEvolution: [],
          internalConflicts: [],
          externalChallenges: [],
        },
        behaviorProfile: {
          communicationStyle: {
            primaryStyle: "direct",
            verbalCharacteristics: [],
            nonverbalCharacteristics: [],
            listeningStyle: "active",
            feedbackStyle: "",
            conflictCommunication: "",
            culturalInfluences: [],
          },
          bodyLanguage: {
            posture: "",
            gestures: [],
            facialExpressions: [],
            eyeContact: "moderate",
            personalSpace: "normal",
            nervousHabits: [],
            confidenceIndicators: [],
            culturalVariations: [],
          },
          decisionMaking: {
            approach: "analytical",
            timeframe: "moderate",
            informationGathering: "",
            riskTolerance: 5,
            influences: [],
            biases: [],
            decisionHistory: [],
          },
          conflictResponse: {
            primaryStyle: "collaborating",
            escalationTriggers: [],
            deescalationMethods: [],
            emotionalReactions: [],
            physicalReactions: [],
            recoveryMethods: [],
            conflictHistory: [],
          },
          socialBehavior: {
            socialEnergy: "ambivert",
            groupDynamics: "",
            socialRoles: [],
            boundaryManagement: "",
            socialAnxieties: [],
            socialStrengths: [],
            networkingStyle: "",
            socialAdaptability: 5,
          },
          workStyle: {
            productivity: "morning",
            environment: "quiet",
            organization: "moderately_organized",
            taskManagement: "",
            collaboration: "",
            innovation: "",
            stressManagement: "",
          },
          learningStyle: {
            primary: "visual",
            preferences: [],
            strengths: [],
            challenges: [],
            motivationFactors: [],
            retentionMethods: [],
            environments: [],
            adaptability: 5,
          },
        },
      },
      supporting: {
        basicInfo: {
          name: "",
          alias: [],
          age: "",
          gender: "",
          occupation: "",
          socialStatus: "",
        },
        appearance: {
          height: "",
          weight: "",
          hairColor: "",
          eyeColor: "",
          skinTone: "",
          bodyType: "",
          specialMarks: [],
          clothingStyle: "",
        },
        personality: {
          coreTraits: ["忠诚", "可靠"],
          values: ["友谊", "支持"],
          beliefs: ["团队合作"],
          fears: ["让朋友失望"],
          desires: ["帮助他人", "被认可"],
          weaknesses: ["过度依赖他人"],
          strengths: ["值得信赖", "善解人意"],
        },
        background: {
          birthplace: "",
          family: "",
          childhood: "",
          education: "",
          importantEvents: [],
          trauma: [],
          achievements: [],
        },
        abilities: {
          professionalSkills: [],
          specialTalents: [],
          languages: [],
          learningAbility: "",
          socialSkills: "",
          practicalSkills: [],
        },
        relationships: {
          family: [],
          friends: [],
          lovers: [],
          enemies: [],
          mentors: [],
          subordinates: [],
          socialCircle: [],
        },
        lifestyle: {
          residence: "",
          economicStatus: "",
          dailyRoutine: "",
          hobbies: [],
          foodPreferences: [],
          entertainment: [],
        },
        psychology: {
          mentalHealth: "稳定",
          mentalHealthStatus: "good",
          copingMechanisms: [],
          emotionalPatterns: [],
          trauma: [],
          growthNeeds: [],
          cognitivePatterns: [],
          stressResponses: [],
          emotionalIntelligence: {
            selfAwareness: 5,
            selfRegulation: 5,
            motivation: 5,
            empathy: 5,
            socialSkills: 5,
            strengths: [],
            weaknesses: [],
          },
          psychologicalDefenses: [],
          mentalHealthHistory: [],
        },
        storyRole: {
          characterType: "supporting" as const,
          characterArc: "支持主角成长",
          conflictRole: "协助解决冲突",
          symbolism: "",
          readerConnection: "喜爱",
        },
        specialSettings: {
          worldBuilding: "",
          culturalBackground: "",
          historicalContext: "",
          technologyLevel: "",
          magicAbilities: "",
          culturalIdentity: {
            primaryCulture: "",
            subcultures: [],
            culturalValues: [],
            culturalConflicts: [],
            assimilationLevel: 5,
            culturalPride: 5,
            traditionalPractices: [],
            modernAdaptations: [],
          },
          religiousBeliefs: {
            religion: "",
            denomination: "",
            devotionLevel: 5,
            practices: [],
            beliefs: [],
            doubts: [],
            spiritualExperiences: [],
            religionInLife: "moderate",
          },
          languageProfile: {
            nativeLanguage: "",
            fluentLanguages: [],
            learningLanguages: [],
            accents: [],
            dialectVariations: [],
            speechPatterns: [],
            languageBarriers: [],
            communicationPreferences: [],
          },
          behaviorPatterns: [],
          rolePlayingNotes: [],
        },
        characterArc: {
          currentStage: "",
          developmentGoals: [],
          growthMilestones: [],
          personalityChanges: [],
          skillProgression: [],
          relationshipEvolution: [],
          internalConflicts: [],
          externalChallenges: [],
        },
        behaviorProfile: {
          communicationStyle: {
            primaryStyle: "direct",
            verbalCharacteristics: [],
            nonverbalCharacteristics: [],
            listeningStyle: "active",
            feedbackStyle: "",
            conflictCommunication: "",
            culturalInfluences: [],
          },
          bodyLanguage: {
            posture: "",
            gestures: [],
            facialExpressions: [],
            eyeContact: "moderate",
            personalSpace: "normal",
            nervousHabits: [],
            confidenceIndicators: [],
            culturalVariations: [],
          },
          decisionMaking: {
            approach: "analytical",
            timeframe: "moderate",
            informationGathering: "",
            riskTolerance: 5,
            influences: [],
            biases: [],
            decisionHistory: [],
          },
          conflictResponse: {
            primaryStyle: "collaborating",
            escalationTriggers: [],
            deescalationMethods: [],
            emotionalReactions: [],
            physicalReactions: [],
            recoveryMethods: [],
            conflictHistory: [],
          },
          socialBehavior: {
            socialEnergy: "ambivert",
            groupDynamics: "",
            socialRoles: [],
            boundaryManagement: "",
            socialAnxieties: [],
            socialStrengths: [],
            networkingStyle: "",
            socialAdaptability: 5,
          },
          workStyle: {
            productivity: "morning",
            environment: "quiet",
            organization: "moderately_organized",
            taskManagement: "",
            collaboration: "",
            innovation: "",
            stressManagement: "",
          },
          learningStyle: {
            primary: "visual",
            preferences: [],
            strengths: [],
            challenges: [],
            motivationFactors: [],
            retentionMethods: [],
            environments: [],
            adaptability: 5,
          },
        },
      },
      minor: {
        basicInfo: {
          name: "",
          alias: [],
          age: "",
          gender: "",
          occupation: "",
          socialStatus: "",
        },
        appearance: {
          height: "",
          weight: "",
          hairColor: "",
          eyeColor: "",
          skinTone: "",
          bodyType: "",
          specialMarks: [],
          clothingStyle: "",
        },
        personality: {
          coreTraits: [],
          values: [],
          beliefs: [],
          fears: [],
          desires: [],
          weaknesses: [],
          strengths: [],
        },
        background: {
          birthplace: "",
          family: "",
          childhood: "",
          education: "",
          importantEvents: [],
          trauma: [],
          achievements: [],
        },
        abilities: {
          professionalSkills: [],
          specialTalents: [],
          languages: [],
          learningAbility: "",
          socialSkills: "",
          practicalSkills: [],
        },
        relationships: {
          family: [],
          friends: [],
          lovers: [],
          enemies: [],
          mentors: [],
          subordinates: [],
          socialCircle: [],
        },
        lifestyle: {
          residence: "",
          economicStatus: "",
          dailyRoutine: "",
          hobbies: [],
          foodPreferences: [],
          entertainment: [],
        },
        psychology: {
          mentalHealth: "",
          copingMechanisms: [],
          emotionalPatterns: [],
          trauma: [],
          growthNeeds: [],
        },
        storyRole: {
          characterType: "minor" as const,
          characterArc: "功能性角色",
          conflictRole: "推动情节",
          symbolism: "",
          readerConnection: "中性",
        },
        specialSettings: {
          worldBuilding: "",
          culturalBackground: "",
          historicalContext: "",
          technologyLevel: "",
          magicAbilities: "",
          culturalIdentity: {
            primaryCulture: "",
            subcultures: [],
            culturalValues: [],
            culturalConflicts: [],
            assimilationLevel: 5,
            culturalPride: 5,
            traditionalPractices: [],
            modernAdaptations: [],
          },
          religiousBeliefs: {
            religion: "",
            denomination: "",
            devotionLevel: 5,
            practices: [],
            beliefs: [],
            doubts: [],
            spiritualExperiences: [],
            religionInLife: "moderate",
          },
          languageProfile: {
            nativeLanguage: "",
            fluentLanguages: [],
            learningLanguages: [],
            accents: [],
            dialectVariations: [],
            speechPatterns: [],
            languageBarriers: [],
            communicationPreferences: [],
          },
          behaviorPatterns: [],
          rolePlayingNotes: [],
        },
        characterArc: {
          currentStage: "",
          developmentGoals: [],
          growthMilestones: [],
          personalityChanges: [],
          skillProgression: [],
          relationshipEvolution: [],
          internalConflicts: [],
          externalChallenges: [],
        },
        behaviorProfile: {
          communicationStyle: {
            primaryStyle: "direct",
            verbalCharacteristics: [],
            nonverbalCharacteristics: [],
            listeningStyle: "active",
            feedbackStyle: "",
            conflictCommunication: "",
            culturalInfluences: [],
          },
          bodyLanguage: {
            posture: "",
            gestures: [],
            facialExpressions: [],
            eyeContact: "moderate",
            personalSpace: "normal",
            nervousHabits: [],
            confidenceIndicators: [],
            culturalVariations: [],
          },
          decisionMaking: {
            approach: "analytical",
            timeframe: "moderate",
            informationGathering: "",
            riskTolerance: 5,
            influences: [],
            biases: [],
            decisionHistory: [],
          },
          conflictResponse: {
            primaryStyle: "collaborating",
            escalationTriggers: [],
            deescalationMethods: [],
            emotionalReactions: [],
            physicalReactions: [],
            recoveryMethods: [],
            conflictHistory: [],
          },
          socialBehavior: {
            socialEnergy: "ambivert",
            groupDynamics: "",
            socialRoles: [],
            boundaryManagement: "",
            socialAnxieties: [],
            socialStrengths: [],
            networkingStyle: "",
            socialAdaptability: 5,
          },
          workStyle: {
            productivity: "morning",
            environment: "quiet",
            organization: "moderately_organized",
            taskManagement: "",
            collaboration: "",
            innovation: "",
            stressManagement: "",
          },
          learningStyle: {
            primary: "visual",
            preferences: [],
            strengths: [],
            challenges: [],
            motivationFactors: [],
            retentionMethods: [],
            environments: [],
            adaptability: 5,
          },
        },
      },
    };
  }

  // 生成角色建议
  generateCharacterSuggestions(
    character: Partial<Character>,
    category: string
  ): string[] {
    const suggestions: Record<string, string[]> = {
      coreTraits: [
        "勇敢",
        "善良",
        "智慧",
        "冷静",
        "热情",
        "坚持",
        "幽默",
        "诚实",
        "冲动",
        "固执",
        "谨慎",
        "乐观",
        "悲观",
        "野心",
        "温和",
        "严厉",
        "创造性",
        "逻辑性",
        "直觉性",
        "分析性",
        "感性",
        "理性",
      ],
      values: [
        "正义",
        "自由",
        "忠诚",
        "诚实",
        "勇气",
        "智慧",
        "慈悲",
        "尊重",
        "责任",
        "家庭",
        "友谊",
        "爱情",
        "成就",
        "安全",
        "冒险",
        "传统",
        "变革",
        "独立",
        "合作",
        "竞争",
        "平等",
        "秩序",
      ],
      fears: [
        "死亡",
        "失败",
        "拒绝",
        "孤独",
        "背叛",
        "失控",
        "痛苦",
        "羞耻",
        "被遗忘",
        "失去所爱",
        "暴露弱点",
        "重复错误",
        "失去身份",
        "社会排斥",
        "经济困难",
        "健康问题",
        "未知",
        "改变",
        "承诺",
        "冲突",
      ],
      hobbies: [
        "阅读",
        "写作",
        "绘画",
        "音乐",
        "运动",
        "旅行",
        "摄影",
        "收藏",
        "园艺",
        "烹饪",
        "手工",
        "游戏",
        "舞蹈",
        "瑜伽",
        "冥想",
        "学习",
        "社交",
        "志愿服务",
        "观星",
        "钓鱼",
        "徒步",
        "骑行",
      ],
      professionalSkills: [
        "领导力",
        "沟通",
        "分析",
        "创造力",
        "解决问题",
        "时间管理",
        "团队合作",
        "谈判",
        "技术能力",
        "语言能力",
        "项目管理",
        "财务管理",
        "营销",
        "销售",
        "教学",
        "研究",
        "设计",
        "编程",
        "医疗",
        "法律",
        "工程",
        "艺术",
      ],
    };

    return suggestions[category] || [];
  }

  // 角色一致性检查
  checkCharacterConsistency(character: Character): {
    issues: string[];
    score: number;
  } {
    const issues: string[] = [];
    let score = 100;

    // 基本信息完整性检查
    if (!character.basicInfo.name.trim()) {
      issues.push("角色缺少姓名");
      score -= 10;
    }

    // 性格特质一致性检查
    const conflictingTraits = this.findConflictingTraits(
      character.personality.coreTraits
    );
    if (conflictingTraits.length > 0) {
      issues.push(`发现冲突的性格特质: ${conflictingTraits.join(", ")}`);
      score -= conflictingTraits.length * 5;
    }

    // 价值观与行为一致性
    if (character.personality.values.length === 0) {
      issues.push("角色缺少明确的价值观");
      score -= 5;
    }

    // 恐惧与欲望平衡
    if (character.personality.fears.length === 0) {
      issues.push("角色缺少恐惧，可能显得不够真实");
      score -= 5;
    }

    if (character.personality.desires.length === 0) {
      issues.push("角色缺少欲望和动机");
      score -= 10;
    }

    // 背景故事完整性
    if (
      !character.background.childhood.trim() &&
      !character.background.importantEvents.length
    ) {
      issues.push("角色背景故事不够详细");
      score -= 5;
    }

    // 角色弧线合理性
    if (!character.storyRole.characterArc.trim()) {
      issues.push("角色缺少明确的成长弧线");
      score -= 10;
    }

    return { issues, score: Math.max(0, score) };
  }

  // 检查冲突的性格特质
  private findConflictingTraits(traits: string[]): string[] {
    const conflicts: Record<string, string[]> = {
      冲动: ["谨慎", "冷静"],
      谨慎: ["冲动", "鲁莽"],
      乐观: ["悲观", "绝望"],
      悲观: ["乐观", "积极"],
      内向: ["外向", "社交"],
      外向: ["内向", "孤僻"],
    };

    const conflicting: string[] = [];
    traits.forEach((trait) => {
      if (conflicts[trait]) {
        const found = traits.filter((t) => conflicts[trait].includes(t));
        conflicting.push(...found.map((f) => `${trait} vs ${f}`));
      }
    });

    return [...new Set(conflicting)];
  }

  // 生成角色关系建议
  generateRelationshipSuggestions(
    character: Character,
    type: "family" | "friends" | "enemies" | "mentors"
  ): string[] {
    const suggestions: Record<string, string[]> = {
      family: [
        "慈爱的父母",
        "严厉的父母",
        "缺席的父母",
        "兄弟姐妹",
        "祖父母",
        "叔伯阿姨",
        "表兄弟姐妹",
        "继父母",
        "养父母",
        "监护人",
      ],
      friends: [
        "童年玩伴",
        "同学好友",
        "工作伙伴",
        "志同道合者",
        "互补性朋友",
        "导师型朋友",
        "保护型朋友",
        "挑战型朋友",
        "安慰型朋友",
        "冒险伙伴",
      ],
      enemies: [
        "竞争对手",
        "前朋友",
        "价值观冲突者",
        "嫉妒者",
        "受害者",
        "权力斗争者",
        "理念对立者",
        "个人恩怨",
        "系统性敌人",
        "意外敌人",
      ],
      mentors: [
        "智慧长者",
        "专业导师",
        "人生教练",
        "精神导师",
        "技能师傅",
        "反面教材",
        "严师",
        "慈师",
        "挑战型导师",
        "启发型导师",
      ],
    };

    return suggestions[type] || [];
  }

  // 生成角色对话样例
  generateCharacterDialogue(
    character: Character,
    context: "casual" | "angry" | "sad" | "excited" | "formal"
  ): string[] {
    const personality = character.personality.coreTraits;
    const dialogues: string[] = [];

    // 基于性格特质生成对话风格
    if (personality.includes("幽默")) {
      dialogues.push("哈，这可真是个有趣的局面。");
      dialogues.push("你知道吗，这让我想起了一个笑话...");
    }

    if (personality.includes("严肃")) {
      dialogues.push("我们需要认真对待这个问题。");
      dialogues.push("这不是开玩笑的时候。");
    }

    if (personality.includes("温和")) {
      dialogues.push("或许我们可以换个角度看这件事。");
      dialogues.push("我理解你的感受，但是...");
    }

    if (personality.includes("冲动")) {
      dialogues.push("我受够了！现在就行动！");
      dialogues.push("别废话了，直接去做！");
    }

    // 基于价值观调整语言风格
    if (character.personality.values.includes("正义")) {
      dialogues.push("这样做是对的。");
      dialogues.push("我们必须站在正确的一边。");
    }

    return dialogues.length > 0
      ? dialogues
      : ["嗯，我需要想想这个问题。", "这确实值得考虑。"];
  }

  // 分析角色语言特征
  analyzeCharacterVoice(character: Character): {
    style: string;
    vocabulary: string[];
    mannerisms: string[];
    emotionalRange: string[];
  } {
    const traits = character.personality.coreTraits;
    const occupation = character.basicInfo.occupation;
    const education = character.background.education;

    let style = "中性";
    const vocabulary: string[] = [];
    const mannerisms: string[] = [];
    const emotionalRange: string[] = [];

    // 基于性格特质分析语言风格
    if (traits.includes("幽默")) {
      style = "幽默风趣";
      mannerisms.push("经常开玩笑", "使用双关语");
      vocabulary.push("俏皮话", "比喻", "讽刺");
    }

    if (traits.includes("严肃")) {
      style = "严谨正式";
      mannerisms.push("用词准确", "逻辑清晰");
      vocabulary.push("专业术语", "正式用语");
    }

    if (traits.includes("文雅")) {
      style = "文雅含蓄";
      mannerisms.push("措辞委婉", "引经据典");
      vocabulary.push("成语", "诗词", "典故");
    }

    // 基于职业调整语言特征
    if (occupation.includes("教师") || occupation.includes("学者")) {
      vocabulary.push("教育术语", "学术词汇");
      mannerisms.push("喜欢解释", "举例说明");
    }

    if (occupation.includes("军人") || occupation.includes("警察")) {
      vocabulary.push("命令式语言", "简短有力");
      mannerisms.push("直接了当", "重视纪律");
    }

    // 情感表达范围
    if (traits.includes("感性")) {
      emotionalRange.push("情感丰富", "表达直接", "感情外露");
    } else if (traits.includes("理性")) {
      emotionalRange.push("情感克制", "逻辑优先", "冷静客观");
    }

    return {
      style,
      vocabulary,
      mannerisms,
      emotionalRange,
    };
  }

  // 设计角色冲突关系
  designCharacterConflicts(
    character: Character,
    otherCharacters: Character[]
  ): {
    internalConflicts: string[];
    interpersonalConflicts: Array<{
      withCharacter: string;
      conflictType: string;
      description: string;
      intensity: "low" | "medium" | "high";
    }>;
    environmentalConflicts: string[];
  } {
    const internalConflicts: string[] = [];
    const interpersonalConflicts: Array<{
      withCharacter: string;
      conflictType: string;
      description: string;
      intensity: "low" | "medium" | "high";
    }> = [];
    const environmentalConflicts: string[] = [];

    // 分析内在冲突
    const traits = character.personality.coreTraits;
    const values = character.personality.values;
    const fears = character.personality.fears;
    const desires = character.personality.desires;

    // 价值观冲突
    if (values.includes("自由") && values.includes("责任")) {
      internalConflicts.push("自由与责任的两难抉择");
    }
    if (values.includes("正义") && values.includes("家庭")) {
      internalConflicts.push("正义感与家庭利益的冲突");
    }

    // 恐惧与欲望的冲突
    if (fears.includes("失败") && desires.includes("成功")) {
      internalConflicts.push("对失败的恐惧阻碍了对成功的追求");
    }
    if (fears.includes("孤独") && desires.includes("独立")) {
      internalConflicts.push("渴望独立但害怕孤独");
    }

    // 分析与其他角色的冲突
    otherCharacters.forEach((other) => {
      const conflictPotential = this.analyzeConflictPotential(character, other);
      if (conflictPotential.hasConflict) {
        interpersonalConflicts.push({
          withCharacter: other.basicInfo.name || "未知角色",
          conflictType: conflictPotential.type,
          description: conflictPotential.description,
          intensity: conflictPotential.intensity,
        });
      }
    });

    // 环境冲突
    const occupation = character.basicInfo.occupation;
    const socialStatus = character.basicInfo.socialStatus;

    if (values.includes("平等") && socialStatus.includes("贵族")) {
      environmentalConflicts.push("平等理念与贵族身份的矛盾");
    }
    if (values.includes("和平") && occupation.includes("军人")) {
      environmentalConflicts.push("和平主义与军人职责的冲突");
    }

    return {
      internalConflicts,
      interpersonalConflicts,
      environmentalConflicts,
    };
  }

  // 分析两个角色间的冲突潜力
  private analyzeConflictPotential(
    char1: Character,
    char2: Character
  ): {
    hasConflict: boolean;
    type: string;
    description: string;
    intensity: "low" | "medium" | "high";
  } {
    // 价值观冲突
    const values1 = char1.personality.values;
    const values2 = char2.personality.values;

    const opposingValues: Record<string, string[]> = {
      自由: ["秩序", "控制", "传统"],
      正义: ["利益", "权力", "效率"],
      和平: ["荣誉", "复仇", "征服"],
      个人主义: ["集体主义", "团队", "家庭"],
    };

    for (const value1 of values1) {
      for (const value2 of values2) {
        if (opposingValues[value1]?.includes(value2)) {
          return {
            hasConflict: true,
            type: "价值观冲突",
            description: `${value1} vs ${value2} 的理念对立`,
            intensity: "high",
          };
        }
      }
    }

    // 角色类型冲突
    if (
      char1.storyRole.characterType === "protagonist" &&
      char2.storyRole.characterType === "antagonist"
    ) {
      return {
        hasConflict: true,
        type: "立场对立",
        description: "主角与反角的根本对立",
        intensity: "high",
      };
    }

    // 性格冲突
    const traits1 = char1.personality.coreTraits;
    const traits2 = char2.personality.coreTraits;

    const conflictingTraits: Record<string, string[]> = {
      冲动: ["谨慎", "保守"],
      理性: ["感性", "直觉"],
      独立: ["依赖", "合作"],
    };

    for (const trait1 of traits1) {
      for (const trait2 of traits2) {
        if (conflictingTraits[trait1]?.includes(trait2)) {
          return {
            hasConflict: true,
            type: "性格冲突",
            description: `${trait1} vs ${trait2} 的性格不合`,
            intensity: "medium",
          };
        }
      }
    }

    return {
      hasConflict: false,
      type: "",
      description: "",
      intensity: "low",
    };
  }

  // 生成角色成长弧线建议
  generateCharacterArcSuggestions(character: Character): {
    arcType: string;
    keyMilestones: string[];
    challenges: string[];
    transformation: string;
  } {
    const characterType = character.storyRole.characterType;
    const traits = character.personality.coreTraits;
    const fears = character.personality.fears;
    const desires = character.personality.desires;
    const weaknesses = character.personality.weaknesses;

    let arcType = "平坦弧线";
    const keyMilestones: string[] = [];
    const challenges: string[] = [];
    let transformation = "角色保持初始状态";

    // 基于角色类型确定弧线类型
    if (characterType === "protagonist") {
      if (weaknesses.length > 0) {
        arcType = "成长弧线";
        transformation = `从 ${weaknesses[0]} 成长为更强的自己`;

        keyMilestones.push("初始状态：存在明显缺陷");
        keyMilestones.push("触发事件：面临重大挑战");
        keyMilestones.push("中点：尝试改变但遭遇挫折");
        keyMilestones.push("危机：缺陷导致的最大冲突");
        keyMilestones.push("高潮：克服缺陷，获得成长");

        challenges.push(`克服 ${weaknesses[0]} 的弱点`);
        if (fears.length > 0) {
          challenges.push(`面对 ${fears[0]} 的恐惧`);
        }
      }
    } else if (characterType === "antagonist") {
      if (traits.includes("野心") || traits.includes("权力欲")) {
        arcType = "堕落弧线";
        transformation = "从相对正常堕落为完全的反派";

        keyMilestones.push("初始：具有某些正面特质");
        keyMilestones.push("诱惑：权力或利益的诱惑");
        keyMilestones.push("妥协：第一次道德妥协");
        keyMilestones.push("沉沦：逐渐失去道德底线");
        keyMilestones.push("堕落：完全转变为反派");
      }
    }

    // 基于欲望添加挑战
    desires.forEach((desire) => {
      challenges.push(`追求 ${desire} 的过程中面临的阻碍`);
    });

    return {
      arcType,
      keyMilestones,
      challenges,
      transformation,
    };
  }

  // 生成角色背景故事片段
  generateBackgroundStory(
    character: Character,
    eventType: "childhood" | "trauma" | "achievement"
  ): string[] {
    const templates: Record<string, string[]> = {
      childhood: [
        "在一个小镇长大，童年时光充满了...",
        "幼年时经历了家庭变故...",
        "从小就表现出了非凡的...",
        "童年时期的一次意外事件改变了...",
        "在严格的家庭环境中成长...",
      ],
      trauma: [
        "目睹了重要人物的离世...",
        "经历了一次重大失败...",
        "遭受了背叛...",
        "失去了珍贵的东西...",
        "面临了生死考验...",
      ],
      achievement: [
        "在年轻时就获得了重要的认可...",
        "克服了巨大的困难实现了目标...",
        "帮助他人度过了危机...",
        "在关键时刻做出了正确的选择...",
        "通过努力改变了自己的命运...",
      ],
    };

    return templates[eventType] || [];
  }

  private serializeCharacter(character: Character): any {
    return {
      ...character,
      createdAt: character.createdAt.toISOString(),
      updatedAt: character.updatedAt.toISOString(),
    };
  }

  private deserializeCharacter(data: any): Character {
    return {
      ...data,
      createdAt: new Date(data.createdAt),
      updatedAt: new Date(data.updatedAt),
    };
  }

  // 角色质量评估
  assessCharacterQuality(character: Character): {
    overall: number;
    dimensions: {
      completeness: number;
      consistency: number;
      depth: number;
      believability: number;
      uniqueness: number;
    };
    recommendations: string[];
  } {
    const dimensions = {
      completeness: this.assessCompleteness(character),
      consistency: this.assessConsistency(character),
      depth: this.assessDepth(character),
      believability: this.assessBelievability(character),
      uniqueness: this.assessUniqueness(character),
    };

    const overall = Math.round(
      (dimensions.completeness +
        dimensions.consistency +
        dimensions.depth +
        dimensions.believability +
        dimensions.uniqueness) /
        5
    );

    const recommendations: string[] = [];

    if (dimensions.completeness < 70) {
      recommendations.push("建议完善基本信息和背景故事");
    }
    if (dimensions.consistency < 70) {
      recommendations.push("检查性格特质和行为的一致性");
    }
    if (dimensions.depth < 70) {
      recommendations.push("深化角色的内心世界和动机");
    }
    if (dimensions.believability < 70) {
      recommendations.push("增加真实感，避免过于完美或极端");
    }
    if (dimensions.uniqueness < 70) {
      recommendations.push("强化角色的独特性和个人特色");
    }

    return {
      overall,
      dimensions,
      recommendations,
    };
  }

  private assessCompleteness(character: Character): number {
    let score = 0;
    let maxScore = 0;

    // 基本信息 (20分)
    maxScore += 20;
    if (character.basicInfo.name) score += 5;
    if (character.basicInfo.age) score += 3;
    if (character.basicInfo.occupation) score += 4;
    if (character.basicInfo.gender) score += 3;
    if (character.basicInfo.socialStatus) score += 3;
    if (character.basicInfo.alias && character.basicInfo.alias.length > 0)
      score += 2;

    // 性格特质 (25分)
    maxScore += 25;
    if (character.personality.coreTraits.length >= 3) score += 8;
    if (character.personality.values.length >= 2) score += 6;
    if (character.personality.fears.length >= 1) score += 4;
    if (character.personality.desires.length >= 1) score += 4;
    if (character.personality.beliefs.length >= 1) score += 3;

    // 背景故事 (20分)
    maxScore += 20;
    if (character.background.birthplace) score += 3;
    if (character.background.family) score += 5;
    if (character.background.childhood) score += 5;
    if (character.background.education) score += 3;
    if (character.background.importantEvents.length >= 1) score += 4;

    // 外貌描述 (15分)
    maxScore += 15;
    if (character.appearance.height) score += 3;
    if (character.appearance.hairColor) score += 3;
    if (character.appearance.eyeColor) score += 3;
    if (character.appearance.clothingStyle) score += 3;
    if (character.appearance.specialMarks.length > 0) score += 3;

    // 故事功能 (20分)
    maxScore += 20;
    if (character.storyRole.characterType) score += 5;
    if (character.storyRole.characterArc) score += 5;
    if (character.storyRole.conflictRole) score += 5;
    if (character.storyRole.readerConnection) score += 5;

    return Math.round((score / maxScore) * 100);
  }

  private assessConsistency(character: Character): number {
    // 使用现有的一致性检查逻辑
    const check = this.checkCharacterConsistency(character);
    return check.score;
  }

  private assessDepth(character: Character): number {
    let score = 0;

    // 心理深度
    if (character.personality.fears.length >= 2) score += 20;
    if (character.personality.desires.length >= 2) score += 20;
    if (character.personality.weaknesses.length >= 1) score += 15;
    if (character.personality.strengths.length >= 1) score += 15;

    // 背景复杂性
    if (character.background.trauma.length >= 1) score += 10;
    if (character.background.achievements.length >= 1) score += 10;
    if (character.background.importantEvents.length >= 2) score += 10;

    return Math.min(score, 100);
  }

  private assessBelievability(character: Character): number {
    let score = 100;

    // 检查是否过于完美
    if (character.personality.weaknesses.length === 0) score -= 20;
    if (character.personality.fears.length === 0) score -= 15;
    if (
      character.background.trauma.length === 0 &&
      character.background.importantEvents.length === 0
    )
      score -= 15;

    // 检查极端特质
    const extremeTraits = ["完美", "无敌", "全能", "无所不知"];
    const hasExtremeTraits = character.personality.coreTraits.some((trait) =>
      extremeTraits.some((extreme) => trait.includes(extreme))
    );
    if (hasExtremeTraits) score -= 25;

    return Math.max(score, 0);
  }

  private assessUniqueness(character: Character): number {
    let score = 50; // 基础分

    // 独特的背景元素
    if (
      character.background.birthplace &&
      !["北京", "上海", "普通小镇"].includes(character.background.birthplace)
    ) {
      score += 10;
    }

    // 特殊标记或特征
    if (character.appearance.specialMarks.length > 0) score += 15;

    // 不寻常的职业
    const commonOccupations = ["学生", "教师", "医生", "警察", "工程师"];
    if (
      character.basicInfo.occupation &&
      !commonOccupations.includes(character.basicInfo.occupation)
    ) {
      score += 10;
    }

    // 独特的性格组合
    const rareTraits = ["神秘", "古怪", "天才", "预言", "直觉超强"];
    const hasRareTraits = character.personality.coreTraits.some((trait) =>
      rareTraits.some((rare) => trait.includes(rare))
    );
    if (hasRareTraits) score += 15;

    return Math.min(score, 100);
  }

  // 角色面试问题生成器
  generateInterviewQuestions(
    character: Character,
    category:
      | "basic"
      | "values"
      | "emotions"
      | "relationships"
      | "behavior"
      | "past"
      | "future"
      | "situational"
  ): string[] {
    const questionSets: Record<string, string[]> = {
      basic: [
        "请介绍一下你自己",
        "你认为自己最大的优点是什么？",
        "你最不喜欢自己的哪一点？",
        "如果用三个词来描述自己，你会选择哪三个？",
        "你觉得别人是怎么看你的？",
        "你最自豪的一件事是什么？",
        "你最后悔的一件事是什么？",
      ],
      values: [
        "什么对你来说最重要？",
        "你绝对不会做的事情是什么？",
        "你认为什么是正确的生活方式？",
        "如果必须在家人和正义之间选择，你会怎么办？",
        "你相信命运吗？为什么？",
        "金钱对你意味着什么？",
        "你如何定义成功？",
      ],
      emotions: [
        "你最害怕什么？",
        "你最想要的是什么？",
        "什么会让你晚上睡不着觉？",
        "如果你有三个愿望，你会许什么愿？",
        "你最不想失去的是什么？",
        "什么情况下你会感到绝望？",
        "你的人生目标是什么？",
      ],
      relationships: [
        "描述一下你最重要的一段关系",
        "你在恋爱关系中寻求什么？",
        "你如何处理冲突？",
        "什么会让你感到被背叛？",
        "你容易相信别人吗？",
        "你如何表达爱意？",
        "什么会让你放弃一段关系？",
      ],
      behavior: [
        "当你生气时，你通常会做什么？",
        "面对压力时，你如何应对？",
        "你如何做重要决定？",
        "在陌生环境中，你的第一反应是什么？",
        "你如何处理失败？",
        "当有人需要帮助时，你会怎么做？",
        "你如何庆祝成功？",
      ],
      past: [
        "说一说改变你人生轨迹的一件事",
        "你童年最深刻的记忆是什么？",
        "谁是对你影响最大的人？",
        "你经历过的最困难的时期是什么？",
        "你学到的最重要的教训是什么？",
        "有什么事情你希望能重新来过？",
        "你最想感谢的人是谁？",
      ],
      future: [
        "你希望五年后的自己是什么样子？",
        "你最想实现的梦想是什么？",
        "什么会阻止你实现目标？",
        "你对未来最大的担忧是什么？",
        "如果明天就是世界末日，你会做什么？",
        "你希望别人怎样记住你？",
        "你认为什么会让你的人生有意义？",
      ],
      situational: [
        "如果你发现你最好的朋友背叛了你，你会怎么做？",
        "如果你必须在两分钟内做出一个重要决定，你会如何决策？",
        "如果你意外得到一大笔钱，你会怎么处理？",
        "如果你被误解并遭到众人指责，你会如何应对？",
        "如果你必须向你讨厌的人求助，你会怎么做？",
        "如果你发现了一个可能伤害他人的秘密，你会怎么办？",
        "如果你面临职业生涯的重大选择，你会考虑哪些因素？",
      ],
    };

    return questionSets[category] || [];
  }

  private generateId(): string {
    return `character_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // 生成综合角色Prompt
  generateComprehensivePrompt(character: Character): string {
    const sections: string[] = [];

    // 基本信息
    if (character.basicInfo.name) {
      sections.push(`# 角色基本信息
**姓名**: ${character.basicInfo.name}
**年龄**: ${character.basicInfo.age}
**性别**: ${character.basicInfo.gender}
**职业**: ${character.basicInfo.occupation}
**社会地位**: ${character.basicInfo.socialStatus}`);
    }

    // 性格特质
    if (character.personality.coreTraits.length > 0) {
      sections.push(`# 性格特质
**核心特质**: ${character.personality.coreTraits.join(", ")}
**价值观**: ${character.personality.values.join(", ")}
**恐惧**: ${character.personality.fears.join(", ")}
**渴望**: ${character.personality.desires.join(", ")}
**优势**: ${character.personality.strengths.join(", ")}
**弱点**: ${character.personality.weaknesses.join(", ")}`);
    }

    // 背景故事
    if (character.background.family || character.background.childhood) {
      sections.push(`# 背景故事
**出生地**: ${character.background.birthplace}
**家庭背景**: ${character.background.family}
**成长经历**: ${character.background.childhood}
**教育背景**: ${character.background.education}
**重要事件**: ${character.background.importantEvents.join(", ")}`);
    }

    // 心理档案（增强版）
    if (character.psychology.mentalHealthStatus) {
      sections.push(`# 心理档案
**心理健康状态**: ${character.psychology.mentalHealthStatus}
**情商水平**:
  - 自我认知: ${character.psychology.emotionalIntelligence.selfAwareness}/10
  - 情绪控制: ${character.psychology.emotionalIntelligence.selfRegulation}/10
  - 同理心: ${character.psychology.emotionalIntelligence.empathy}/10
**心理防御机制**: ${character.psychology.psychologicalDefenses.join(", ")}
**成长需求**: ${character.psychology.growthNeeds.join(", ")}`);
    }

    // 文化身份
    if (character.specialSettings.culturalIdentity.primaryCulture) {
      sections.push(`# 文化身份
**主要文化背景**: ${character.specialSettings.culturalIdentity.primaryCulture}
**文化认同程度**: ${character.specialSettings.culturalIdentity.culturalPride}/10
**传统习俗**: ${character.specialSettings.culturalIdentity.traditionalPractices.join(
        ", "
      )}
**宗教信仰**: ${character.specialSettings.religiousBeliefs.religion}
**虔诚程度**: ${character.specialSettings.religiousBeliefs.devotionLevel}/10
**母语**: ${character.specialSettings.languageProfile.nativeLanguage}
**流利语言**: ${character.specialSettings.languageProfile.fluentLanguages.join(
        ", "
      )}`);
    }

    // 行为模式
    sections.push(`# 行为模式
**沟通风格**: ${character.behaviorProfile.communicationStyle.primaryStyle}
**决策风格**: ${character.behaviorProfile.decisionMaking.approach}
**社交倾向**: ${character.behaviorProfile.socialBehavior.socialEnergy}
**冲突处理**: ${character.behaviorProfile.conflictResponse.primaryStyle}
**工作时段**: ${character.behaviorProfile.workStyle.productivity}
**环境偏好**: ${character.behaviorProfile.workStyle.environment}
**学习风格**: ${character.behaviorProfile.learningStyle.primary}`);

    // 角色成长
    if (character.characterArc.currentStage) {
      sections.push(`# 角色成长轨迹
**当前发展阶段**: ${character.characterArc.currentStage}
**发展目标数量**: ${character.characterArc.developmentGoals.length}
**成长里程碑数量**: ${character.characterArc.growthMilestones.length}
**内在冲突数量**: ${character.characterArc.internalConflicts.length}`);
    }

    // 故事功能
    if (character.storyRole.characterType) {
      sections.push(`# 故事功能
**角色类型**: ${character.storyRole.characterType}
**角色弧线**: ${character.storyRole.characterArc}
**冲突作用**: ${character.storyRole.conflictRole}
**象征意义**: ${character.storyRole.symbolism}
**读者连接**: ${character.storyRole.readerConnection}`);
    }

    // AI创作指导
    sections.push(`# AI创作指导

## 角色塑造要点
1. **性格一致性**: 确保角色在不同情境下的反应符合其核心特质
2. **成长轨迹**: 关注角色的内心变化和外在行为的演进
3. **文化背景**: 体现角色的文化身份对其价值观和行为的影响
4. **心理深度**: 展现角色的情感复杂性和内在冲突

## 对话创作建议
- 根据沟通风格调整语言特色：${
      character.behaviorProfile.communicationStyle.primaryStyle
    }
- 体现文化背景：${character.specialSettings.culturalIdentity.primaryCulture}
- 反映性格特质：${character.personality.coreTraits.slice(0, 3).join(", ")}

## 情节发展建议
- 设计与角色恐惧相关的挑战：${character.personality.fears
      .slice(0, 2)
      .join(", ")}
- 利用角色渴望推动情节：${character.personality.desires.slice(0, 2).join(", ")}
- 考虑角色的决策风格：${character.behaviorProfile.decisionMaking.approach}

## 写作提醒
- 角色当前处于：${character.characterArc.currentStage || "待定发展阶段"}
- 重点展现：${character.storyRole.symbolism || "角色的象征意义"}
- 读者情感连接：${character.storyRole.readerConnection || "建立认同感"}`);

    return sections.filter((section) => section.trim()).join("\n\n");
  }
}
