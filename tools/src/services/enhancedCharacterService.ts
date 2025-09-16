import { Character } from '../types/index';
import { storage } from '@utils/storage';

// 增强版角色服务，包含AI辅助功能
export class EnhancedCharacterService {
  private readonly storageKey = 'novellus-enhanced-characters';

  async getAllCharacters(): Promise<Character[]> {
    try {
      const characters = await storage.getItem<Character[]>(this.storageKey) || [];
      return characters.map(this.deserializeCharacter);
    } catch (error) {
      console.error('获取角色列表失败:', error);
      return [];
    }
  }

  async getCharacterById(id: string): Promise<Character | null> {
    try {
      const characters = await this.getAllCharacters();
      return characters.find(character => character.id === id) || null;
    } catch (error) {
      console.error('获取角色失败:', error);
      return null;
    }
  }

  async saveCharacter(character: Character): Promise<void> {
    try {
      const characters = await this.getAllCharacters();
      const existingIndex = characters.findIndex(c => c.id === character.id);

      const serializedCharacter = this.serializeCharacter({
        ...character,
        updatedAt: new Date()
      });

      if (existingIndex >= 0) {
        characters[existingIndex] = serializedCharacter;
      } else {
        characters.push(serializedCharacter);
      }

      await storage.setItem(this.storageKey, characters);
    } catch (error) {
      console.error('保存角色失败:', error);
      throw error;
    }
  }

  async deleteCharacter(id: string): Promise<void> {
    try {
      const characters = await this.getAllCharacters();
      const filteredCharacters = characters
        .filter(character => character.id !== id)
        .map(this.serializeCharacter);

      await storage.setItem(this.storageKey, filteredCharacters);
    } catch (error) {
      console.error('删除角色失败:', error);
      throw error;
    }
  }

  // 创建角色模板
  createCharacterTemplate(projectId: string, type: Character['storyRole']['characterType'] = 'protagonist'): Character {
    const templates = this.getCharacterTemplates();
    const template = templates[type];

    return {
      id: this.generateId(),
      projectId,
      createdAt: new Date(),
      updatedAt: new Date(),
      ...template
    };
  }

  // 获取角色模板库
  private getCharacterTemplates() {
    return {
      protagonist: {
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
          coreTraits: ['勇敢', '决心坚定'],
          values: ['正义', '保护弱者'],
          beliefs: ['善有善报'],
          fears: ['失去所爱的人'],
          desires: ['实现目标', '成长'],
          weaknesses: ['过于冲动'],
          strengths: ['坚持不懈', '富有同情心']
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
          mentalHealth: '稳定',
          copingMechanisms: [],
          emotionalPatterns: [],
          trauma: [],
          growthNeeds: []
        },
        storyRole: {
          characterType: 'protagonist' as const,
          characterArc: '成长型弧线',
          conflictRole: '推动故事发展',
          symbolism: '',
          readerConnection: '认同感'
        },
        specialSettings: {
          worldBuilding: '',
          culturalBackground: '',
          historicalContext: '',
          technologyLevel: '',
          magicAbilities: ''
        }
      },
      antagonist: {
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
          coreTraits: ['野心勃勃', '冷酷'],
          values: ['权力', '控制'],
          beliefs: ['强者为王'],
          fears: ['失去权力', '被击败'],
          desires: ['统治', '征服'],
          weaknesses: ['傲慢', '低估对手'],
          strengths: ['策略思维', '意志坚强']
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
          mentalHealth: '功能性',
          copingMechanisms: [],
          emotionalPatterns: [],
          trauma: [],
          growthNeeds: []
        },
        storyRole: {
          characterType: 'antagonist' as const,
          characterArc: '堕落或固定弧线',
          conflictRole: '制造冲突',
          symbolism: '',
          readerConnection: '恐惧或理解'
        },
        specialSettings: {
          worldBuilding: '',
          culturalBackground: '',
          historicalContext: '',
          technologyLevel: '',
          magicAbilities: ''
        }
      },
      supporting: {
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
          coreTraits: ['忠诚', '可靠'],
          values: ['友谊', '支持'],
          beliefs: ['团队合作'],
          fears: ['让朋友失望'],
          desires: ['帮助他人', '被认可'],
          weaknesses: ['过度依赖他人'],
          strengths: ['值得信赖', '善解人意']
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
          mentalHealth: '稳定',
          copingMechanisms: [],
          emotionalPatterns: [],
          trauma: [],
          growthNeeds: []
        },
        storyRole: {
          characterType: 'supporting' as const,
          characterArc: '支持主角成长',
          conflictRole: '协助解决冲突',
          symbolism: '',
          readerConnection: '喜爱'
        },
        specialSettings: {
          worldBuilding: '',
          culturalBackground: '',
          historicalContext: '',
          technologyLevel: '',
          magicAbilities: ''
        }
      },
      minor: {
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
          copingMechanisms: [],
          emotionalPatterns: [],
          trauma: [],
          growthNeeds: []
        },
        storyRole: {
          characterType: 'minor' as const,
          characterArc: '功能性角色',
          conflictRole: '推动情节',
          symbolism: '',
          readerConnection: '中性'
        },
        specialSettings: {
          worldBuilding: '',
          culturalBackground: '',
          historicalContext: '',
          technologyLevel: '',
          magicAbilities: ''
        }
      }
    };
  }

  // 生成角色建议
  generateCharacterSuggestions(character: Partial<Character>, category: string): string[] {
    const suggestions: Record<string, string[]> = {
      coreTraits: [
        '勇敢', '善良', '智慧', '冷静', '热情', '坚持', '幽默', '诚实',
        '冲动', '固执', '谨慎', '乐观', '悲观', '野心', '温和', '严厉',
        '创造性', '逻辑性', '直觉性', '分析性', '感性', '理性'
      ],
      values: [
        '正义', '自由', '忠诚', '诚实', '勇气', '智慧', '慈悲', '尊重',
        '责任', '家庭', '友谊', '爱情', '成就', '安全', '冒险', '传统',
        '变革', '独立', '合作', '竞争', '平等', '秩序'
      ],
      fears: [
        '死亡', '失败', '拒绝', '孤独', '背叛', '失控', '痛苦', '羞耻',
        '被遗忘', '失去所爱', '暴露弱点', '重复错误', '失去身份', '社会排斥',
        '经济困难', '健康问题', '未知', '改变', '承诺', '冲突'
      ],
      hobbies: [
        '阅读', '写作', '绘画', '音乐', '运动', '旅行', '摄影', '收藏',
        '园艺', '烹饪', '手工', '游戏', '舞蹈', '瑜伽', '冥想', '学习',
        '社交', '志愿服务', '观星', '钓鱼', '徒步', '骑行'
      ],
      professionalSkills: [
        '领导力', '沟通', '分析', '创造力', '解决问题', '时间管理', '团队合作', '谈判',
        '技术能力', '语言能力', '项目管理', '财务管理', '营销', '销售', '教学', '研究',
        '设计', '编程', '医疗', '法律', '工程', '艺术'
      ]
    };

    return suggestions[category] || [];
  }

  // 角色一致性检查
  checkCharacterConsistency(character: Character): { issues: string[], score: number } {
    const issues: string[] = [];
    let score = 100;

    // 基本信息完整性检查
    if (!character.basicInfo.name.trim()) {
      issues.push('角色缺少姓名');
      score -= 10;
    }

    // 性格特质一致性检查
    const conflictingTraits = this.findConflictingTraits(character.personality.coreTraits);
    if (conflictingTraits.length > 0) {
      issues.push(`发现冲突的性格特质: ${conflictingTraits.join(', ')}`);
      score -= conflictingTraits.length * 5;
    }

    // 价值观与行为一致性
    if (character.personality.values.length === 0) {
      issues.push('角色缺少明确的价值观');
      score -= 5;
    }

    // 恐惧与欲望平衡
    if (character.personality.fears.length === 0) {
      issues.push('角色缺少恐惧，可能显得不够真实');
      score -= 5;
    }

    if (character.personality.desires.length === 0) {
      issues.push('角色缺少欲望和动机');
      score -= 10;
    }

    // 背景故事完整性
    if (!character.background.childhood.trim() && !character.background.importantEvents.length) {
      issues.push('角色背景故事不够详细');
      score -= 5;
    }

    // 角色弧线合理性
    if (!character.storyRole.characterArc.trim()) {
      issues.push('角色缺少明确的成长弧线');
      score -= 10;
    }

    return { issues, score: Math.max(0, score) };
  }

  // 检查冲突的性格特质
  private findConflictingTraits(traits: string[]): string[] {
    const conflicts: Record<string, string[]> = {
      '冲动': ['谨慎', '冷静'],
      '谨慎': ['冲动', '鲁莽'],
      '乐观': ['悲观', '绝望'],
      '悲观': ['乐观', '积极'],
      '内向': ['外向', '社交'],
      '外向': ['内向', '孤僻']
    };

    const conflicting: string[] = [];
    traits.forEach(trait => {
      if (conflicts[trait]) {
        const found = traits.filter(t => conflicts[trait].includes(t));
        conflicting.push(...found.map(f => `${trait} vs ${f}`));
      }
    });

    return [...new Set(conflicting)];
  }

  // 生成角色关系建议
  generateRelationshipSuggestions(character: Character, type: 'family' | 'friends' | 'enemies' | 'mentors'): string[] {
    const suggestions: Record<string, string[]> = {
      family: [
        '慈爱的父母', '严厉的父母', '缺席的父母', '兄弟姐妹', '祖父母',
        '叔伯阿姨', '表兄弟姐妹', '继父母', '养父母', '监护人'
      ],
      friends: [
        '童年玩伴', '同学好友', '工作伙伴', '志同道合者', '互补性朋友',
        '导师型朋友', '保护型朋友', '挑战型朋友', '安慰型朋友', '冒险伙伴'
      ],
      enemies: [
        '竞争对手', '前朋友', '价值观冲突者', '嫉妒者', '受害者',
        '权力斗争者', '理念对立者', '个人恩怨', '系统性敌人', '意外敌人'
      ],
      mentors: [
        '智慧长者', '专业导师', '人生教练', '精神导师', '技能师傅',
        '反面教材', '严师', '慈师', '挑战型导师', '启发型导师'
      ]
    };

    return suggestions[type] || [];
  }

  // 生成角色背景故事片段
  generateBackgroundStory(character: Character, eventType: 'childhood' | 'trauma' | 'achievement'): string[] {
    const templates: Record<string, string[]> = {
      childhood: [
        '在一个小镇长大，童年时光充满了...',
        '幼年时经历了家庭变故...',
        '从小就表现出了非凡的...',
        '童年时期的一次意外事件改变了...',
        '在严格的家庭环境中成长...'
      ],
      trauma: [
        '目睹了重要人物的离世...',
        '经历了一次重大失败...',
        '遭受了背叛...',
        '失去了珍贵的东西...',
        '面临了生死考验...'
      ],
      achievement: [
        '在年轻时就获得了重要的认可...',
        '克服了巨大的困难实现了目标...',
        '帮助他人度过了危机...',
        '在关键时刻做出了正确的选择...',
        '通过努力改变了自己的命运...'
      ]
    };

    return templates[eventType] || [];
  }

  private serializeCharacter(character: Character): any {
    return {
      ...character,
      createdAt: character.createdAt.toISOString(),
      updatedAt: character.updatedAt.toISOString()
    };
  }

  private deserializeCharacter(data: any): Character {
    return {
      ...data,
      createdAt: new Date(data.createdAt),
      updatedAt: new Date(data.updatedAt)
    };
  }

  private generateId(): string {
    return `character_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}