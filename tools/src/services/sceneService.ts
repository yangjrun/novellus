import { Scene, SceneAtmosphere, SensoryDetails } from '../types/index';
import { storage } from '@utils/storage';

export class SceneService {
  private readonly storageKey = 'novellus-scenes';

  async getAllScenes(): Promise<Scene[]> {
    try {
      const scenes = await storage.getItem<Scene[]>(this.storageKey) || [];
      return scenes.map(this.deserializeScene);
    } catch (error) {
      console.error('获取场景列表失败:', error);
      return [];
    }
  }

  async getSceneById(id: string): Promise<Scene | null> {
    try {
      const scenes = await this.getAllScenes();
      return scenes.find(scene => scene.id === id) || null;
    } catch (error) {
      console.error('获取场景失败:', error);
      return null;
    }
  }

  async getScenesByProject(projectId: string): Promise<Scene[]> {
    try {
      const scenes = await this.getAllScenes();
      return scenes.filter(scene => scene.projectId === projectId);
    } catch (error) {
      console.error('获取项目场景失败:', error);
      return [];
    }
  }

  async saveScene(scene: Scene): Promise<void> {
    try {
      const scenes = await this.getAllScenes();
      const existingIndex = scenes.findIndex(s => s.id === scene.id);

      const serializedScene = this.serializeScene({
        ...scene,
        updatedAt: new Date()
      });

      if (existingIndex >= 0) {
        scenes[existingIndex] = serializedScene;
      } else {
        scenes.push(serializedScene);
      }

      await storage.setItem(this.storageKey, scenes);
    } catch (error) {
      console.error('保存场景失败:', error);
      throw error;
    }
  }

  async deleteScene(id: string): Promise<void> {
    try {
      const scenes = await this.getAllScenes();
      const filteredScenes = scenes
        .filter(scene => scene.id !== id)
        .map(this.serializeScene);

      await storage.setItem(this.storageKey, filteredScenes);
    } catch (error) {
      console.error('删除场景失败:', error);
      throw error;
    }
  }

  // 创建场景模板
  createSceneTemplate(projectId: string, type: 'action' | 'dialogue' | 'description' | 'emotional' | 'transition' = 'description'): Scene {
    const templates = this.getSceneTemplates();
    const template = templates[type];

    return {
      id: this.generateId(),
      projectId,
      title: '',
      description: '',
      locationId: '',
      timeOfDay: template.timeOfDay,
      weather: template.weather,
      atmosphere: { ...template.atmosphere },
      sensoryDetails: { ...template.sensoryDetails },
      characters: [],
      purpose: { ...template.purpose },
      pacing: template.pacing,
      emotionalTone: [...template.emotionalTone],
      conflict: '',
      outcome: '',
      notes: '',
      createdAt: new Date(),
      updatedAt: new Date()
    };
  }

  // 获取场景模板库
  private getSceneTemplates() {
    return {
      action: {
        timeOfDay: '日间',
        weather: '晴朗',
        atmosphere: {
          mood: '紧张',
          tension: 8,
          energy: 9,
          intimacy: 3,
          danger: 8,
          mystery: 4
        },
        sensoryDetails: {
          visual: ['快速移动', '尘土飞扬', '光影交错'],
          auditory: ['金属碰撞声', '急促脚步', '重重喘息'],
          olfactory: ['汗水味', '血腥味'],
          tactile: ['心跳加速', '肌肉紧绷', '冷汗'],
          gustatory: ['口干舌燥', '铁锈味'],
          emotional: ['肾上腺素飙升', '专注', '恐惧']
        },
        purpose: {
          storyFunction: 'conflict' as const,
          characterDevelopment: ['展现勇气', '测试能力'],
          plotAdvancement: '推动情节高潮',
          worldBuilding: '展示世界的危险性',
          themeExploration: '探讨勇气与恐惧'
        },
        pacing: 'fast' as const,
        emotionalTone: ['紧张', '刺激', '危险']
      },
      dialogue: {
        timeOfDay: '晚间',
        weather: '平静',
        atmosphere: {
          mood: '亲密',
          tension: 4,
          energy: 5,
          intimacy: 8,
          danger: 2,
          mystery: 3
        },
        sensoryDetails: {
          visual: ['柔和灯光', '面部表情', '手势动作'],
          auditory: ['声音细节', '语调变化', '沉默'],
          olfactory: ['咖啡香味', '淡淡香水'],
          tactile: ['温暖', '紧握的手'],
          gustatory: ['茶的苦涩', '甜点的香甜'],
          emotional: ['温暖', '信任', '理解']
        },
        purpose: {
          storyFunction: 'development' as const,
          characterDevelopment: ['深化关系', '揭示内心'],
          plotAdvancement: '推进情感线',
          worldBuilding: '展示文化背景',
          themeExploration: '探讨人际关系'
        },
        pacing: 'slow' as const,
        emotionalTone: ['温馨', '深入', '真诚']
      },
      description: {
        timeOfDay: '黄昏',
        weather: '多云',
        atmosphere: {
          mood: '神秘',
          tension: 5,
          energy: 4,
          intimacy: 4,
          danger: 3,
          mystery: 7
        },
        sensoryDetails: {
          visual: ['夕阳西下', '长长阴影', '古老建筑'],
          auditory: ['风声', '远处钟声', '脚步回声'],
          olfactory: ['古老书香', '潮湿石头'],
          tactile: ['凉爽微风', '粗糙石墙'],
          gustatory: ['空气中的尘埃'],
          emotional: ['怀旧', '好奇', '敬畏']
        },
        purpose: {
          storyFunction: 'setup' as const,
          characterDevelopment: ['建立氛围'],
          plotAdvancement: '设置背景',
          worldBuilding: '展示环境细节',
          themeExploration: '营造主题氛围'
        },
        pacing: 'medium' as const,
        emotionalTone: ['宁静', '神秘', '美丽']
      },
      emotional: {
        timeOfDay: '深夜',
        weather: '暴雨',
        atmosphere: {
          mood: '忧郁',
          tension: 7,
          energy: 3,
          intimacy: 9,
          danger: 4,
          mystery: 5
        },
        sensoryDetails: {
          visual: ['雨水模糊', '昏暗灯光', '泪水'],
          auditory: ['雨声', '抽泣声', '雷声'],
          olfactory: ['雨后泥土', '咸味眼泪'],
          tactile: ['冰冷雨滴', '颤抖身体', '湿润'],
          gustatory: ['苦涩泪水'],
          emotional: ['悲伤', '痛苦', '绝望', '释放']
        },
        purpose: {
          storyFunction: 'development' as const,
          characterDevelopment: ['情感爆发', '内心成长'],
          plotAdvancement: '情感转折点',
          worldBuilding: '反映内心状态',
          themeExploration: '探讨人性深度'
        },
        pacing: 'slow' as const,
        emotionalTone: ['悲伤', '深刻', '感人']
      },
      transition: {
        timeOfDay: '清晨',
        weather: '微风',
        atmosphere: {
          mood: '过渡',
          tension: 3,
          energy: 6,
          intimacy: 4,
          danger: 2,
          mystery: 3
        },
        sensoryDetails: {
          visual: ['晨光', '新的开始', '道路'],
          auditory: ['鸟鸣声', '脚步声'],
          olfactory: ['清新空气', '花香'],
          tactile: ['温暖阳光', '轻快步伐'],
          gustatory: ['清晨的甘甜'],
          emotional: ['希望', '期待', '变化']
        },
        purpose: {
          storyFunction: 'transition' as const,
          characterDevelopment: ['状态转换'],
          plotAdvancement: '连接情节段落',
          worldBuilding: '展示时间流逝',
          themeExploration: '暗示变化主题'
        },
        pacing: 'medium' as const,
        emotionalTone: ['平缓', '过渡', '希望']
      }
    };
  }

  // 感官细节建议
  getSensoryDetailSuggestions(category: keyof SensoryDetails): string[] {
    const suggestions: Record<keyof SensoryDetails, string[]> = {
      visual: [
        '明亮的阳光', '昏暗的灯光', '长长的阴影', '色彩斑斓', '黑白对比',
        '模糊不清', '清晰锐利', '反光表面', '纹理细节', '空间深度',
        '动作流畅', '静止画面', '远近景观', '细节特写', '全景视野'
      ],
      auditory: [
        '轻柔音乐', '嘈杂声音', '寂静无声', '回声效果', '节奏感强',
        '高低音调', '突然声响', '持续噪音', '自然声音', '人工声音',
        '和谐音色', '刺耳声音', '熟悉声音', '陌生声音', '情感色彩'
      ],
      olfactory: [
        '花香味', '食物香味', '烟雾味', '海洋味', '森林味',
        '化学味', '腐败味', '清新味', '甜腻味', '刺鼻味',
        '熟悉味道', '陌生味道', '混合气味', '淡淡香味', '浓郁气味'
      ],
      tactile: [
        '柔软触感', '粗糙表面', '冰冷温度', '温暖感觉', '潮湿环境',
        '干燥感觉', '光滑质地', '黏腻感觉', '尖锐边缘', '圆润曲线',
        '重量感', '轻飘感', '振动感', '压力感', '舒适感'
      ],
      gustatory: [
        '甜味', '苦味', '酸味', '咸味', '鲜味',
        '辛辣味', '清淡味', '浓郁味', '回甘', '余味',
        '熟悉味道', '陌生味道', '复合味道', '纯净味道', '变化味道'
      ],
      emotional: [
        '快乐', '悲伤', '愤怒', '恐惧', '惊讶',
        '厌恶', '期待', '信任', '怀疑', '嫉妒',
        '羞耻', '骄傲', '感激', '怨恨', '宽恕',
        '希望', '绝望', '平静', '焦虑', '兴奋'
      ]
    };

    return suggestions[category] || [];
  }

  // 氛围营造建议
  getAtmosphereSuggestions(moodType: string): SceneAtmosphere {
    const atmospherePresets: Record<string, SceneAtmosphere> = {
      '紧张': { mood: '紧张', tension: 8, energy: 7, intimacy: 3, danger: 7, mystery: 5 },
      '浪漫': { mood: '浪漫', tension: 3, energy: 4, intimacy: 9, danger: 1, mystery: 4 },
      '神秘': { mood: '神秘', tension: 6, energy: 5, intimacy: 4, danger: 5, mystery: 9 },
      '战斗': { mood: '战斗', tension: 9, energy: 10, intimacy: 2, danger: 9, mystery: 3 },
      '宁静': { mood: '宁静', tension: 2, energy: 3, intimacy: 6, danger: 1, mystery: 2 },
      '恐怖': { mood: '恐怖', tension: 9, energy: 6, intimacy: 3, danger: 8, mystery: 8 },
      '欢乐': { mood: '欢乐', tension: 2, energy: 8, intimacy: 7, danger: 1, mystery: 2 },
      '悲伤': { mood: '悲伤', tension: 5, energy: 2, intimacy: 8, danger: 2, mystery: 4 },
      '冒险': { mood: '冒险', tension: 6, energy: 8, intimacy: 4, danger: 6, mystery: 6 },
      '思考': { mood: '思考', tension: 3, energy: 2, intimacy: 5, danger: 1, mystery: 5 }
    };

    return atmospherePresets[moodType] || atmospherePresets['宁静'];
  }

  // 场景功能分析
  analyzeScenePurpose(scene: Scene): string[] {
    const analysis: string[] = [];

    // 分析故事功能
    switch (scene.purpose.storyFunction) {
      case 'setup':
        analysis.push('这是一个设置场景，用于建立故事背景和氛围');
        break;
      case 'conflict':
        analysis.push('这是一个冲突场景，推动故事的主要矛盾');
        break;
      case 'development':
        analysis.push('这是一个发展场景，深化角色和情节');
        break;
      case 'climax':
        analysis.push('这是一个高潮场景，是故事的关键转折点');
        break;
      case 'resolution':
        analysis.push('这是一个解决场景，处理故事的结局');
        break;
      case 'transition':
        analysis.push('这是一个过渡场景，连接不同的故事段落');
        break;
    }

    // 分析节奏
    if (scene.pacing === 'fast') {
      analysis.push('快节奏场景，适合动作和紧张情节');
    } else if (scene.pacing === 'slow') {
      analysis.push('慢节奏场景，适合情感交流和深入描写');
    } else {
      analysis.push('中等节奏场景，平衡动作和情感');
    }

    // 分析氛围
    if (scene.atmosphere.tension >= 7) {
      analysis.push('高张力场景，能够牢牢抓住读者注意力');
    }

    if (scene.atmosphere.intimacy >= 7) {
      analysis.push('高亲密度场景，适合角色情感交流');
    }

    if (scene.atmosphere.danger >= 7) {
      analysis.push('高危险场景，能够创造悬念和紧张感');
    }

    if (scene.atmosphere.mystery >= 7) {
      analysis.push('高神秘感场景，引发读者好奇心');
    }

    // 分析感官丰富度
    const sensoryCount = Object.values(scene.sensoryDetails).reduce((total, details) => total + details.length, 0);
    if (sensoryCount >= 15) {
      analysis.push('感官细节丰富，能够创造沉浸式体验');
    } else if (sensoryCount < 5) {
      analysis.push('感官细节较少，建议添加更多感官描写');
    }

    return analysis;
  }

  // 场景质量评估
  evaluateSceneQuality(scene: Scene): { score: number, feedback: string[] } {
    let score = 100;
    const feedback: string[] = [];

    // 基本信息检查
    if (!scene.title.trim()) {
      feedback.push('场景缺少标题');
      score -= 10;
    }

    if (!scene.description.trim()) {
      feedback.push('场景缺少描述');
      score -= 15;
    }

    // 感官细节检查
    const sensoryCount = Object.values(scene.sensoryDetails).reduce((total, details) => total + details.length, 0);
    if (sensoryCount === 0) {
      feedback.push('缺少感官细节描写');
      score -= 20;
    } else if (sensoryCount < 5) {
      feedback.push('感官细节较少，建议丰富感官描写');
      score -= 10;
    }

    // 氛围一致性检查
    if (scene.emotionalTone.includes('快乐') && scene.atmosphere.mood === '悲伤') {
      feedback.push('情感基调与氛围不一致');
      score -= 15;
    }

    // 节奏与内容匹配
    if (scene.pacing === 'fast' && scene.purpose.storyFunction === 'development' && scene.atmosphere.energy < 5) {
      feedback.push('快节奏设定与场景功能不匹配');
      score -= 10;
    }

    // 角色参与度
    if (scene.characters.length === 0) {
      feedback.push('场景中没有角色参与');
      score -= 15;
    }

    // 冲突存在性
    if (!scene.conflict.trim() && scene.purpose.storyFunction === 'conflict') {
      feedback.push('冲突场景缺少具体冲突描述');
      score -= 10;
    }

    // 结果明确性
    if (!scene.outcome.trim() && ['conflict', 'climax'].includes(scene.purpose.storyFunction)) {
      feedback.push('重要场景缺少明确结果');
      score -= 10;
    }

    return { score: Math.max(0, score), feedback };
  }

  // 生成场景转换建议
  generateTransitionSuggestions(fromScene: Scene, toScene: Scene): string[] {
    const suggestions: string[] = [];

    // 时间过渡
    if (fromScene.timeOfDay !== toScene.timeOfDay) {
      suggestions.push(`考虑添加时间过渡描写，从${fromScene.timeOfDay}到${toScene.timeOfDay}`);
    }

    // 地点过渡
    if (fromScene.locationId !== toScene.locationId) {
      suggestions.push('需要描写地点转换，可以使用移动场景或淡出淡入');
    }

    // 情绪过渡
    const fromMood = fromScene.atmosphere.mood;
    const toMood = toScene.atmosphere.mood;
    if (fromMood !== toMood) {
      suggestions.push(`情绪从${fromMood}转向${toMood}，注意情感过渡的自然性`);
    }

    // 节奏过渡
    if (fromScene.pacing !== toScene.pacing) {
      const paceMap = { fast: '快', medium: '中', slow: '慢' };
      suggestions.push(`节奏从${paceMap[fromScene.pacing]}转向${paceMap[toScene.pacing]}，需要适当的缓冲`);
    }

    // 张力过渡
    const tensionDiff = toScene.atmosphere.tension - fromScene.atmosphere.tension;
    if (Math.abs(tensionDiff) >= 3) {
      if (tensionDiff > 0) {
        suggestions.push('张力急剧上升，考虑使用铺垫和预示');
      } else {
        suggestions.push('张力快速下降，注意释放的合理性');
      }
    }

    return suggestions;
  }

  private serializeScene(scene: Scene): any {
    return {
      ...scene,
      createdAt: scene.createdAt.toISOString(),
      updatedAt: scene.updatedAt.toISOString()
    };
  }

  private deserializeScene(data: any): Scene {
    return {
      ...data,
      createdAt: new Date(data.createdAt),
      updatedAt: new Date(data.updatedAt)
    };
  }

  private generateId(): string {
    return `scene_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}