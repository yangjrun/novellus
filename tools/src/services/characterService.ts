import { Character, ExportFormat } from '../types/index';
import { StorageService, generateId } from '@utils/storage';
import { saveAs } from 'file-saver';

export class CharacterService {
  private storage: StorageService;

  constructor() {
    this.storage = new StorageService('characters');
  }

  // 创建默认角色对象
  createDefaultCharacter(): Character {
    return {
      id: generateId(),
      projectId: '',
      createdAt: new Date(),
      updatedAt: new Date(),
      basicInfo: {
        name: '',
        alias: [],
        age: '',
        gender: '',
        occupation: '',
        socialStatus: ''
      },
      appearance: {
        height: '',
        weight: '',
        hairColor: '',
        eyeColor: '',
        skinTone: '',
        bodyType: '',
        specialMarks: [],
        clothingStyle: ''
      },
      personality: {
        coreTraits: [],
        values: [],
        beliefs: [],
        fears: [],
        desires: [],
        weaknesses: [],
        strengths: []
      },
      background: {
        birthplace: '',
        family: '',
        childhood: '',
        education: '',
        importantEvents: [],
        trauma: [],
        achievements: []
      },
      abilities: {
        professionalSkills: [],
        specialTalents: [],
        languages: [],
        learningAbility: '',
        socialSkills: '',
        practicalSkills: []
      },
      relationships: {
        family: [],
        friends: [],
        lovers: [],
        enemies: [],
        mentors: [],
        subordinates: [],
        socialCircle: []
      },
      lifestyle: {
        residence: '',
        economicStatus: '',
        dailyRoutine: '',
        hobbies: [],
        foodPreferences: [],
        entertainment: []
      },
      psychology: {
        mentalHealth: '',
        mentalHealthStatus: 'good',
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
          weaknesses: []
        },
        psychologicalDefenses: [],
        mentalHealthHistory: []
      },
      storyRole: {
        characterType: 'supporting',
        characterArc: '',
        conflictRole: '',
        symbolism: '',
        readerConnection: ''
      },
      specialSettings: {
        worldBuilding: '',
        culturalBackground: '',
        historicalContext: '',
        technologyLevel: '',
        magicAbilities: '',
        culturalIdentity: {
          primaryCulture: '',
          subcultures: [],
          culturalValues: [],
          culturalConflicts: [],
          assimilationLevel: 5,
          culturalPride: 5,
          traditionalPractices: [],
          modernAdaptations: []
        },
        religiousBeliefs: {
          religion: '',
          denomination: '',
          devotionLevel: 5,
          practices: [],
          beliefs: [],
          doubts: [],
          spiritualExperiences: [],
          religionInLife: 'moderate'
        },
        languageProfile: {
          nativeLanguage: '',
          fluentLanguages: [],
          learningLanguages: [],
          accents: [],
          dialectVariations: [],
          speechPatterns: [],
          languageBarriers: [],
          communicationPreferences: []
        },
        behaviorPatterns: [],
        rolePlayingNotes: []
      },
      characterArc: {
        currentStage: '',
        developmentGoals: [],
        growthMilestones: [],
        personalityChanges: [],
        skillProgression: [],
        relationshipEvolution: [],
        internalConflicts: [],
        externalChallenges: []
      },
      behaviorProfile: {
        communicationStyle: {
          primaryStyle: 'direct',
          verbalCharacteristics: [],
          nonverbalCharacteristics: [],
          listeningStyle: 'active',
          feedbackStyle: '',
          conflictCommunication: '',
          culturalInfluences: []
        },
        bodyLanguage: {
          posture: '',
          gestures: [],
          facialExpressions: [],
          eyeContact: 'moderate',
          personalSpace: 'normal',
          nervousHabits: [],
          confidenceIndicators: [],
          culturalVariations: []
        },
        decisionMaking: {
          approach: 'analytical',
          timeframe: 'moderate',
          informationGathering: '',
          riskTolerance: 5,
          influences: [],
          biases: [],
          decisionHistory: []
        },
        conflictResponse: {
          primaryStyle: 'collaborating',
          escalationTriggers: [],
          deescalationMethods: [],
          emotionalReactions: [],
          physicalReactions: [],
          recoveryMethods: [],
          conflictHistory: []
        },
        socialBehavior: {
          socialEnergy: 'ambivert',
          groupDynamics: '',
          socialRoles: [],
          boundaryManagement: '',
          socialAnxieties: [],
          socialStrengths: [],
          networkingStyle: '',
          socialAdaptability: 5
        },
        workStyle: {
          productivity: 'morning',
          environment: 'quiet',
          organization: 'moderately_organized',
          taskManagement: '',
          collaboration: '',
          innovation: '',
          stressManagement: ''
        },
        learningStyle: {
          primary: 'visual',
          preferences: [],
          strengths: [],
          challenges: [],
          motivationFactors: [],
          retentionMethods: [],
          environments: [],
          adaptability: 5
        }
      }
    };
  }

  // 保存角色
  async saveCharacter(character: Character): Promise<Character> {
    const now = new Date();

    if (!character.id) {
      character.id = generateId();
      character.createdAt = now;
    }

    character.updatedAt = now;

    await this.storage.set(character.id, character);
    return character;
  }

  // 获取所有角色
  async getAllCharacters(): Promise<Character[]> {
    return await this.storage.getAll<Character>();
  }

  // 根据ID获取角色
  async getCharacterById(id: string): Promise<Character | null> {
    return await this.storage.get<Character>(id);
  }

  // 根据项目ID获取角色
  async getCharactersByProject(projectId: string): Promise<Character[]> {
    const allCharacters = await this.getAllCharacters();
    return allCharacters.filter(character => character.projectId === projectId);
  }

  // 删除角色
  async deleteCharacter(id: string): Promise<boolean> {
    try {
      await this.storage.remove(id);
      return true;
    } catch (error) {
      console.error('删除角色失败:', error);
      return false;
    }
  }

  // 复制角色
  async duplicateCharacter(id: string): Promise<Character | null> {
    const original = await this.getCharacterById(id);
    if (!original) return null;

    const duplicate: Character = {
      ...original,
      id: generateId(),
      basicInfo: {
        ...original.basicInfo,
        name: `${original.basicInfo.name} (副本)`
      },
      createdAt: new Date(),
      updatedAt: new Date()
    };

    return await this.saveCharacter(duplicate);
  }

  // 导出角色
  async exportCharacter(id: string, format: ExportFormat): Promise<void> {
    const character = await this.getCharacterById(id);
    if (!character) {
      throw new Error('角色不存在');
    }

    switch (format) {
      case 'json':
        await this.exportAsJSON(character);
        break;
      case 'pdf':
        await this.exportAsPDF(character);
        break;
      case 'docx':
        await this.exportAsDocx(character);
        break;
      default:
        throw new Error(`不支持的导出格式: ${format}`);
    }
  }

  // 导出为JSON
  private async exportAsJSON(character: Character): Promise<void> {
    const dataStr = JSON.stringify(character, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    saveAs(blob, `${character.basicInfo.name || 'character'}_${character.id}.json`);
  }

  // 导出为PDF
  private async exportAsPDF(character: Character): Promise<void> {
    // 使用动态导入来减少初始包大小
    const { jsPDF } = await import('jspdf');
    const doc = new jsPDF();

    // 设置中文字体支持
    doc.setFont('helvetica');

    let yPosition = 20;
    const lineHeight = 10;
    const pageHeight = doc.internal.pageSize.height;

    const addText = (text: string, fontSize = 12) => {
      doc.setFontSize(fontSize);
      if (yPosition > pageHeight - 20) {
        doc.addPage();
        yPosition = 20;
      }
      doc.text(text, 20, yPosition);
      yPosition += lineHeight;
    };

    // 标题
    addText(`角色档案: ${character.basicInfo.name}`, 16);
    yPosition += 5;

    // 基本信息
    addText('基本信息', 14);
    addText(`姓名: ${character.basicInfo.name}`);
    addText(`年龄: ${character.basicInfo.age}`);
    addText(`性别: ${character.basicInfo.gender}`);
    addText(`职业: ${character.basicInfo.occupation}`);
    yPosition += 5;

    // 性格特质
    addText('性格特质', 14);
    addText(`核心特质: ${character.personality.coreTraits.join(', ')}`);
    addText(`价值观: ${character.personality.values.join(', ')}`);
    addText(`恐惧: ${character.personality.fears.join(', ')}`);
    yPosition += 5;

    // 背景故事
    addText('背景故事', 14);
    addText(`出生地: ${character.background.birthplace}`);
    addText(`教育背景: ${character.background.education}`);

    // 保存PDF
    doc.save(`${character.basicInfo.name || 'character'}_${character.id}.pdf`);
  }

  // 导出为Word文档
  private async exportAsDocx(character: Character): Promise<void> {
    // 这里可以使用docx库来生成Word文档
    // 为了简化，我们先生成一个简单的文本格式
    let content = `角色档案: ${character.basicInfo.name}\n\n`;

    content += `基本信息:\n`;
    content += `姓名: ${character.basicInfo.name}\n`;
    content += `年龄: ${character.basicInfo.age}\n`;
    content += `性别: ${character.basicInfo.gender}\n`;
    content += `职业: ${character.basicInfo.occupation}\n\n`;

    content += `性格特质:\n`;
    content += `核心特质: ${character.personality.coreTraits.join(', ')}\n`;
    content += `价值观: ${character.personality.values.join(', ')}\n`;
    content += `恐惧: ${character.personality.fears.join(', ')}\n\n`;

    // 更多内容...

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    saveAs(blob, `${character.basicInfo.name || 'character'}_${character.id}.txt`);
  }

  // 搜索角色
  async searchCharacters(query: string): Promise<Character[]> {
    const allCharacters = await this.getAllCharacters();
    const lowercaseQuery = query.toLowerCase();

    return allCharacters.filter(character => {
      return (
        character.basicInfo.name.toLowerCase().includes(lowercaseQuery) ||
        character.basicInfo.occupation.toLowerCase().includes(lowercaseQuery) ||
        character.personality.coreTraits.some(trait =>
          trait.toLowerCase().includes(lowercaseQuery)
        ) ||
        character.background.birthplace.toLowerCase().includes(lowercaseQuery)
      );
    });
  }

  // 获取统计信息
  async getStatistics(): Promise<{
    total: number;
    byType: Record<string, number>;
    byProject: Record<string, number>;
  }> {
    const allCharacters = await this.getAllCharacters();

    const byType: Record<string, number> = {};
    const byProject: Record<string, number> = {};

    allCharacters.forEach(character => {
      // 按角色类型统计
      const type = character.storyRole.characterType;
      byType[type] = (byType[type] || 0) + 1;

      // 按项目统计
      const projectId = character.projectId || 'unassigned';
      byProject[projectId] = (byProject[projectId] || 0) + 1;
    });

    return {
      total: allCharacters.length,
      byType,
      byProject
    };
  }

  // 数据验证
  validateCharacter(character: Character): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    // 必填字段检查
    if (!character.basicInfo.name.trim()) {
      errors.push('角色姓名不能为空');
    }

    // 字段长度检查
    if (character.basicInfo.name.length > 50) {
      errors.push('角色姓名不能超过50个字符');
    }

    // 数组字段检查
    if (character.personality.coreTraits.length === 0) {
      errors.push('至少需要设置一个核心性格特质');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }
}