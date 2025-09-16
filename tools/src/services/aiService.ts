import { AIPrompt, AIResponse, AIParameter } from '../types/index';

// AI服务 - 基础AI集成框架
export class AIService {
  private readonly baseUrl = 'https://api.novellus.ai'; // 示例API地址
  private readonly apiKey = process.env.REACT_APP_AI_API_KEY || '';

  // 获取所有可用的AI提示模板
  getAvailablePrompts(): AIPrompt[] {
    return this.getPromptTemplates();
  }

  // 根据类别获取AI提示
  getPromptsByCategory(category: AIPrompt['category']): AIPrompt[] {
    return this.getPromptTemplates().filter(prompt => prompt.category === category);
  }

  // 执行AI生成
  async generateContent(promptId: string, parameters: Record<string, any>): Promise<AIResponse> {
    try {
      const prompt = this.getPromptTemplates().find(p => p.id === promptId);
      if (!prompt) {
        throw new Error(`找不到提示模板: ${promptId}`);
      }

      // 验证参数
      this.validateParameters(prompt, parameters);

      // 构建最终提示
      const finalPrompt = this.buildPrompt(prompt, parameters);

      // 模拟AI调用 (实际项目中应该调用真实的AI API)
      const result = await this.simulateAICall(finalPrompt, prompt.category);

      const response: AIResponse = {
        id: this.generateId(),
        promptId,
        input: parameters,
        output: result.content,
        confidence: result.confidence,
        suggestions: result.suggestions,
        timestamp: new Date()
      };

      return response;
    } catch (error) {
      console.error('AI生成失败:', error);
      throw error;
    }
  }

  // 批量生成内容
  async batchGenerate(requests: Array<{ promptId: string, parameters: Record<string, any> }>): Promise<AIResponse[]> {
    try {
      const responses = await Promise.all(
        requests.map(request => this.generateContent(request.promptId, request.parameters))
      );
      return responses;
    } catch (error) {
      console.error('批量AI生成失败:', error);
      throw error;
    }
  }

  // 优化和改进内容
  async improveContent(content: string, improvementType: 'grammar' | 'style' | 'clarity' | 'creativity'): Promise<string> {
    try {
      const prompt = this.getImprovementPrompt(improvementType);
      const parameters = { content, improvementType };

      const response = await this.generateContent(prompt.id, parameters);
      return response.output;
    } catch (error) {
      console.error('内容优化失败:', error);
      throw error;
    }
  }

  // 内容质量评估
  async evaluateContent(content: string, contentType: 'character' | 'plot' | 'scene' | 'dialogue'): Promise<{
    score: number;
    feedback: string[];
    suggestions: string[];
  }> {
    try {
      // 模拟AI评估
      const evaluation = await this.simulateContentEvaluation(content, contentType);
      return evaluation;
    } catch (error) {
      console.error('内容评估失败:', error);
      throw error;
    }
  }

  // 获取AI提示模板库
  private getPromptTemplates(): AIPrompt[] {
    return [
      // 角色创作提示
      {
        id: 'character-background-generator',
        name: '角色背景生成器',
        description: '生成详细的角色背景故事',
        category: 'character',
        template: `请为以下角色生成一个详细的背景故事：

角色名称：{characterName}
角色类型：{characterType}
年龄：{age}
职业：{occupation}
性格特质：{coreTraits}
文化背景：{culturalBackground}

要求：
1. 包含童年经历
2. 重要的人生转折点
3. 影响性格形成的关键事件
4. 与其他角色的潜在关系
5. 适合故事世界观的背景设定

背景故事应该在300-500字之间，具有逻辑性和可信度。`,
        parameters: [
          { name: 'characterName', type: 'text', description: '角色姓名', required: true },
          { name: 'characterType', type: 'select', description: '角色类型', required: true, options: ['主角', '反角', '配角', '次要角色'] },
          { name: 'age', type: 'text', description: '年龄', required: false },
          { name: 'occupation', type: 'text', description: '职业', required: false },
          { name: 'coreTraits', type: 'text', description: '核心性格特质', required: false },
          { name: 'culturalBackground', type: 'text', description: '文化背景', required: false }
        ],
        examples: [
          {
            input: {
              characterName: '艾丽娅',
              characterType: '主角',
              age: '25',
              occupation: '法师学徒',
              coreTraits: '勇敢、固执、富有同情心',
              culturalBackground: '北方山地部族'
            },
            output: '艾丽娅出生在北方的雪峰部族，从小就展现出不凡的魔法天赋...',
            explanation: '生成了包含童年、成长、转折点的完整背景故事'
          }
        ]
      },
      {
        id: 'character-dialogue-generator',
        name: '角色对话生成器',
        description: '生成符合角色性格的对话',
        category: 'character',
        template: `请为以下角色生成对话，要求符合其性格特征：

角色信息：
- 姓名：{characterName}
- 性格：{personality}
- 说话风格：{speakingStyle}
- 当前情绪：{currentMood}
- 对话背景：{context}

对话主题：{dialogueTopic}

要求：
1. 对话要符合角色的性格和说话风格
2. 体现当前的情绪状态
3. 符合对话背景和情境
4. 自然流畅，避免生硬
5. 包含适当的动作描写

请生成3-5句对话。`,
        parameters: [
          { name: 'characterName', type: 'text', description: '角色姓名', required: true },
          { name: 'personality', type: 'text', description: '性格特征', required: true },
          { name: 'speakingStyle', type: 'text', description: '说话风格', required: false },
          { name: 'currentMood', type: 'text', description: '当前情绪', required: false },
          { name: 'context', type: 'text', description: '对话背景', required: true },
          { name: 'dialogueTopic', type: 'text', description: '对话主题', required: true }
        ],
        examples: []
      },

      // 世界构建提示
      {
        id: 'culture-generator',
        name: '文化生成器',
        description: '创建独特的文化背景',
        category: 'world',
        template: `请创建一个独特的文化，包含以下要素：

文化名称：{cultureName}
世界类型：{worldType}
地理环境：{geography}
主要价值观：{mainValues}

要求生成：
1. 核心价值观和信念系统
2. 社会结构和等级制度
3. 重要的传统和仪式
4. 艺术形式和表达方式
5. 语言特色和交流方式
6. 与其他文化的关系
7. 独特的文化符号和象征

内容应该详细且有内在逻辑，符合所设定的世界观。`,
        parameters: [
          { name: 'cultureName', type: 'text', description: '文化名称', required: true },
          { name: 'worldType', type: 'select', description: '世界类型', required: true, options: ['奇幻', '科幻', '现实', '历史', '架空历史'] },
          { name: 'geography', type: 'text', description: '地理环境', required: false },
          { name: 'mainValues', type: 'text', description: '主要价值观', required: false }
        ],
        examples: []
      },
      {
        id: 'magic-system-generator',
        name: '魔法系统生成器',
        description: '设计完整的魔法系统',
        category: 'world',
        template: `请设计一个魔法系统，包含以下规范：

魔法类型：{magicType}
能量来源：{energySource}
限制因素：{limitations}
社会影响：{socialImpact}

要求包含：
1. 魔法的基本原理和运作方式
2. 能量来源和消耗机制
3. 使用限制和代价
4. 学习和掌握的方法
5. 不同等级的魔法能力
6. 对社会结构的影响
7. 魔法物品和辅助工具
8. 与普通人的关系

系统应该逻辑自洽，有明确的规则和限制。`,
        parameters: [
          { name: 'magicType', type: 'select', description: '魔法类型', required: true, options: ['元素魔法', '心灵魔法', '符文魔法', '神术', '自然魔法', '血脉魔法'] },
          { name: 'energySource', type: 'text', description: '能量来源', required: false },
          { name: 'limitations', type: 'text', description: '限制因素', required: false },
          { name: 'socialImpact', type: 'text', description: '社会影响', required: false }
        ],
        examples: []
      },

      // 情节创作提示
      {
        id: 'plot-twist-generator',
        name: '情节转折生成器',
        description: '创造意外的情节转折',
        category: 'plot',
        template: `基于以下故事背景，生成一个意外的情节转折：

故事背景：{storyBackground}
当前情况：{currentSituation}
主要角色：{mainCharacters}
已有冲突：{existingConflicts}
转折类型：{twistType}

要求：
1. 转折要出人意料但符合逻辑
2. 与已有情节元素相关联
3. 推动故事发展
4. 增加戏剧张力
5. 为角色创造新的挑战
6. 埋下伏笔或揭示隐情

转折应该具体明确，包含实施的具体方式。`,
        parameters: [
          { name: 'storyBackground', type: 'text', description: '故事背景', required: true },
          { name: 'currentSituation', type: 'text', description: '当前情况', required: true },
          { name: 'mainCharacters', type: 'text', description: '主要角色', required: false },
          { name: 'existingConflicts', type: 'text', description: '已有冲突', required: false },
          { name: 'twistType', type: 'select', description: '转折类型', required: false, options: ['身份揭示', '背叛', '意外发现', '时间逆转', '虚假死亡', '隐藏动机'] }
        ],
        examples: []
      },

      // 场景创作提示
      {
        id: 'scene-atmosphere-enhancer',
        name: '场景氛围增强器',
        description: '丰富场景的氛围描写',
        category: 'scene',
        template: `请为以下场景增强氛围描写：

场景基本信息：
- 地点：{location}
- 时间：{timeOfDay}
- 天气：{weather}
- 氛围：{desiredMood}
- 角色状态：{characterState}

当前描写：{currentDescription}

要求增强：
1. 视觉细节（光线、色彩、形状）
2. 听觉细节（声音、音效、静默）
3. 嗅觉和触觉（气味、温度、质地）
4. 情感氛围（紧张、温馨、神秘等）
5. 象征意义（环境反映主题）

增强后的描写应该更加生动，能够让读者身临其境。`,
        parameters: [
          { name: 'location', type: 'text', description: '场景地点', required: true },
          { name: 'timeOfDay', type: 'select', description: '时间', required: false, options: ['黎明', '上午', '中午', '下午', '黄昏', '夜晚', '深夜'] },
          { name: 'weather', type: 'text', description: '天气', required: false },
          { name: 'desiredMood', type: 'text', description: '期望氛围', required: true },
          { name: 'characterState', type: 'text', description: '角色状态', required: false },
          { name: 'currentDescription', type: 'text', description: '当前描写', required: true }
        ],
        examples: []
      },

      // 通用改进提示
      {
        id: 'content-improver-grammar',
        name: '语法改进器',
        description: '改进文本的语法和表达',
        category: 'general',
        template: `请改进以下文本的语法和表达：

原文：{content}

改进要求：
1. 修正语法错误
2. 优化句式结构
3. 提升表达清晰度
4. 保持原意不变
5. 增强文本流畅性

请提供改进后的版本。`,
        parameters: [
          { name: 'content', type: 'text', description: '需要改进的内容', required: true },
          { name: 'improvementType', type: 'text', description: '改进类型', required: false }
        ],
        examples: []
      }
    ];
  }

  // 获取改进提示
  private getImprovementPrompt(type: string): AIPrompt {
    const prompts = this.getPromptTemplates();
    return prompts.find(p => p.id === `content-improver-${type}`) || prompts.find(p => p.id === 'content-improver-grammar')!;
  }

  // 验证参数
  private validateParameters(prompt: AIPrompt, parameters: Record<string, any>): void {
    for (const param of prompt.parameters) {
      if (param.required && (!parameters[param.name] || parameters[param.name] === '')) {
        throw new Error(`缺少必需参数: ${param.name}`);
      }

      if (param.type === 'select' && param.options && parameters[param.name]) {
        if (!param.options.includes(parameters[param.name])) {
          throw new Error(`参数 ${param.name} 的值不在允许范围内`);
        }
      }
    }
  }

  // 构建最终提示
  private buildPrompt(prompt: AIPrompt, parameters: Record<string, any>): string {
    let finalPrompt = prompt.template;

    // 替换参数占位符
    for (const [key, value] of Object.entries(parameters)) {
      const placeholder = `{${key}}`;
      finalPrompt = finalPrompt.replace(new RegExp(placeholder, 'g'), value || '');
    }

    return finalPrompt;
  }

  // 模拟AI调用（实际项目中应该调用真实API）
  private async simulateAICall(prompt: string, category: string): Promise<{
    content: string;
    confidence: number;
    suggestions: string[];
  }> {
    // 模拟API延迟
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));

    // 根据类别生成不同类型的模拟内容
    const simulatedContent = this.generateSimulatedContent(category, prompt);

    return {
      content: simulatedContent,
      confidence: Math.round(80 + Math.random() * 20), // 80-100
      suggestions: this.generateSuggestions(category)
    };
  }

  // 生成模拟内容
  private generateSimulatedContent(category: string, prompt: string): string {
    const templates: Record<string, string[]> = {
      character: [
        '这个角色有着复杂的背景故事，从小就展现出与众不同的特质...',
        '在成长过程中，这个角色经历了重要的人生转折...',
        '他/她的性格特征深深地影响着故事的发展...'
      ],
      world: [
        '这个世界拥有独特的文化传统和价值体系...',
        '其地理环境和历史背景塑造了居民的生活方式...',
        '各种势力和组织在这个世界中相互影响...'
      ],
      plot: [
        '故事在这一点出现了意想不到的转折...',
        '新的冲突为角色带来了前所未有的挑战...',
        '这个情节发展为后续故事埋下了重要伏笔...'
      ],
      scene: [
        '夕阳西下，金色的光芒洒在古老的石径上...',
        '空气中弥漫着神秘的香味，远处传来悠扬的钟声...',
        '角色们在这个特殊的环境中感受到了前所未有的氛围...'
      ],
      general: [
        '经过改进的内容更加清晰明了...',
        '优化后的表达更符合语言规范...',
        '改进后的文本具有更好的可读性...'
      ]
    };

    const categoryTemplates = templates[category] || templates.general;
    const randomTemplate = categoryTemplates[Math.floor(Math.random() * categoryTemplates.length)];

    // 根据提示内容长度生成不同长度的回复
    const baseLength = prompt.length > 500 ? 300 : 150;
    const additionalContent = Math.floor(Math.random() * 200);

    return randomTemplate + '这里是根据您的具体要求生成的详细内容，包含了丰富的细节和创意元素，能够为您的创作提供有价值的参考和启发。' + '内容的详细程度会根据您提供的参数进行调整，确保生成的内容既符合您的期望，又具有创新性和实用性。'.repeat(Math.floor(additionalContent / 100));
  }

  // 生成建议
  private generateSuggestions(category: string): string[] {
    const suggestions: Record<string, string[]> = {
      character: [
        '考虑添加更多的性格冲突元素',
        '可以进一步探索角色的内心动机',
        '建议增加与其他角色的关系细节'
      ],
      world: [
        '可以添加更多的文化细节',
        '考虑设计独特的社会制度',
        '建议完善世界的历史背景'
      ],
      plot: [
        '可以增加更多的铺垫和伏笔',
        '考虑加强冲突的层次感',
        '建议优化情节的节奏控制'
      ],
      scene: [
        '可以丰富感官描写',
        '考虑增加环境与情感的呼应',
        '建议添加更多的象征元素'
      ],
      general: [
        '可以进一步优化语言表达',
        '考虑增强内容的逻辑性',
        '建议完善细节描写'
      ]
    };

    return suggestions[category] || suggestions.general;
  }

  // 模拟内容评估
  private async simulateContentEvaluation(content: string, contentType: string): Promise<{
    score: number;
    feedback: string[];
    suggestions: string[];
  }> {
    // 模拟API延迟
    await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 1200));

    const baseScore = 70 + Math.random() * 25; // 70-95
    const score = Math.round(baseScore);

    const feedback: string[] = [];
    const suggestions: string[] = [];

    // 根据内容长度和类型生成反馈
    if (content.length < 50) {
      feedback.push('内容较短，建议增加更多细节');
      suggestions.push('扩展现有内容，添加更多描述');
    } else if (content.length > 1000) {
      feedback.push('内容详细，结构良好');
      suggestions.push('可以考虑精简部分重复内容');
    } else {
      feedback.push('内容长度适中，信息量丰富');
    }

    // 根据内容类型添加具体反馈
    switch (contentType) {
      case 'character':
        feedback.push('角色设定具有一定的深度');
        suggestions.push('可以进一步探索角色的内心世界');
        break;
      case 'plot':
        feedback.push('情节发展具有逻辑性');
        suggestions.push('考虑增加更多的转折和悬念');
        break;
      case 'scene':
        feedback.push('场景描写生动具体');
        suggestions.push('可以增强氛围营造');
        break;
      case 'dialogue':
        feedback.push('对话自然流畅');
        suggestions.push('可以增加更多的潜台词');
        break;
    }

    return { score, feedback, suggestions };
  }

  private generateId(): string {
    return `ai_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// AI助手类 - 提供便捷的AI功能访问
export class AIAssistant {
  private aiService: AIService;

  constructor() {
    this.aiService = new AIService();
  }

  // 角色创作助手
  async generateCharacterBackground(character: any): Promise<string> {
    const response = await this.aiService.generateContent('character-background-generator', {
      characterName: character.basicInfo?.name || '未命名角色',
      characterType: this.getCharacterTypeLabel(character.storyRole?.characterType),
      age: character.basicInfo?.age || '',
      occupation: character.basicInfo?.occupation || '',
      coreTraits: character.personality?.coreTraits?.join(', ') || '',
      culturalBackground: character.specialSettings?.culturalBackground || ''
    });

    return response.output;
  }

  async generateCharacterDialogue(character: any, context: string, topic: string): Promise<string> {
    const response = await this.aiService.generateContent('character-dialogue-generator', {
      characterName: character.basicInfo?.name || '角色',
      personality: character.personality?.coreTraits?.join(', ') || '未定义',
      speakingStyle: this.inferSpeakingStyle(character),
      currentMood: '正常',
      context,
      dialogueTopic: topic
    });

    return response.output;
  }

  // 世界构建助手
  async generateCulture(cultureName: string, worldType: string, geography: string = ''): Promise<string> {
    const response = await this.aiService.generateContent('culture-generator', {
      cultureName,
      worldType,
      geography,
      mainValues: ''
    });

    return response.output;
  }

  async generateMagicSystem(magicType: string, energySource: string = ''): Promise<string> {
    const response = await this.aiService.generateContent('magic-system-generator', {
      magicType,
      energySource,
      limitations: '',
      socialImpact: ''
    });

    return response.output;
  }

  // 情节创作助手
  async generatePlotTwist(storyBackground: string, currentSituation: string): Promise<string> {
    const response = await this.aiService.generateContent('plot-twist-generator', {
      storyBackground,
      currentSituation,
      mainCharacters: '',
      existingConflicts: '',
      twistType: ''
    });

    return response.output;
  }

  // 场景创作助手
  async enhanceSceneAtmosphere(scene: any): Promise<string> {
    const response = await this.aiService.generateContent('scene-atmosphere-enhancer', {
      location: scene.locationId || '未指定地点',
      timeOfDay: scene.timeOfDay || '',
      weather: scene.weather || '',
      desiredMood: scene.atmosphere?.mood || '中性',
      characterState: '',
      currentDescription: scene.description || ''
    });

    return response.output;
  }

  // 内容改进助手
  async improveContent(content: string, type: 'grammar' | 'style' | 'clarity' | 'creativity' = 'grammar'): Promise<string> {
    return this.aiService.improveContent(content, type);
  }

  // 内容评估助手
  async evaluateContent(content: string, type: 'character' | 'plot' | 'scene' | 'dialogue'): Promise<{
    score: number;
    feedback: string[];
    suggestions: string[];
  }> {
    return this.aiService.evaluateContent(content, type);
  }

  // 辅助方法
  private getCharacterTypeLabel(type: string): string {
    const labels: Record<string, string> = {
      protagonist: '主角',
      antagonist: '反角',
      supporting: '配角',
      minor: '次要角色'
    };
    return labels[type] || '角色';
  }

  private inferSpeakingStyle(character: any): string {
    const traits = character.personality?.coreTraits || [];

    if (traits.includes('冷静') || traits.includes('理性')) {
      return '冷静理性，措辞精确';
    } else if (traits.includes('热情') || traits.includes('外向')) {
      return '热情洋溢，用词丰富';
    } else if (traits.includes('谨慎') || traits.includes('内向')) {
      return '谨慎含蓄，言简意赅';
    } else {
      return '自然随意，符合身份';
    }
  }
}