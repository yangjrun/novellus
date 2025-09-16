import {
  PromptConfig,
  PromptTemplate,
  DynamicVariable,
  PromptStructure,
  PromptSection,
  TemplateMetadata,
  ValidationResult,
  IPromptTemplateGenerator,
  VariableOption,
  ConditionalSection,
  DynamicInstruction
} from '../types/prompt';
import { projectDataService } from './projectDataService';

// Prompt模板生成器基类
export abstract class BasePromptGenerator implements IPromptTemplateGenerator {
  protected category: string;

  constructor(category: string) {
    this.category = category;
  }

  abstract generateTemplate(config: PromptConfig): PromptTemplate;

  validateConfig(config: PromptConfig): ValidationResult {
    const errors = [];
    const warnings = [];

    if (!config.category) {
      errors.push({ field: 'category', message: '必须选择创作阶段', code: 'REQUIRED' });
    }

    if (!config.difficulty) {
      errors.push({ field: 'difficulty', message: '必须选择难度等级', code: 'REQUIRED' });
    }

    if (!config.aiModel) {
      warnings.push({
        field: 'aiModel',
        message: '未选择AI模型，将使用通用格式',
        suggestion: '选择特定AI模型可获得更好的优化效果'
      });
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }

  getDefaultConfig(): PromptConfig {
    return {
      category: 'structure',
      difficulty: 'beginner',
      writingStyle: 'narrative',
      detailLevel: 'moderate',
      aiModel: 'generic'
    };
  }

  getSupportedCategories(): string[] {
    return ['structure', 'character', 'world', 'scene', 'dialogue', 'assessment'];
  }

  // 通用工具方法
  protected generateId(): string {
    return `${this.category}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  protected getBaseRoleDefinition(aiModel: string, category: string): string {
    const roleDefinitions = {
      claude: {
        structure: '作为一名专业的叙事结构专家和创意写作导师，你具有深厚的文学理论功底和丰富的创作指导经验。',
        character: '作为一名专业的角色设计师和心理学专家，你精通角色塑造理论和人物发展规律。',
        world: '作为一名专业的世界构建师和文化研究专家，你擅长创造复杂而逻辑一致的虚构世界。',
        scene: '作为一名专业的场景设计师和感官写作专家，你精通环境描述和氛围营造技巧。',
        dialogue: '作为一名专业的对话写作专家和语言学家，你擅长创作自然流畅且富有个性的对话。'
      },
      gpt: {
        structure: '你是一个专业的故事结构设计师，精通各种叙事技巧和创作理论。',
        character: '你是一个专业的角色创建专家，擅长设计复杂而真实的角色。',
        world: '你是一个专业的世界构建专家，擅长设计详细的虚构世界。',
        scene: '你是一个专业的场景描述专家，擅长创作生动的环境描述。',
        dialogue: '你是一个专业的对话写作专家，擅长创作自然的角色对话。'
      },
      gemini: {
        structure: '作为创作导师，你将运用专业知识帮助用户构建优秀的故事结构。',
        character: '作为角色设计顾问，你将帮助用户创造深度的角色形象。',
        world: '作为世界构建顾问，你将协助用户设计引人入胜的虚构世界。',
        scene: '作为场景创作顾问，你将指导用户描绘生动的场景画面。',
        dialogue: '作为对话创作顾问，你将帮助用户写出精彩的角色对话。'
      },
      generic: {
        structure: '作为专业的故事结构顾问，请提供专业的创作建议。',
        character: '作为专业的角色设计顾问，请提供专业的角色创作建议。',
        world: '作为专业的世界构建顾问，请提供专业的世界设定建议。',
        scene: '作为专业的场景设计顾问，请提供专业的场景创作建议。',
        dialogue: '作为专业的对话创作顾问，请提供专业的对话写作建议。'
      }
    };

    return roleDefinitions[aiModel]?.[category] || roleDefinitions.generic[category];
  }

  protected getOutputFormat(detailLevel: string): string {
    const formats = {
      brief: '请提供简洁明了的建议，重点突出核心要素。',
      moderate: '请提供结构清晰的详细建议，包含具体的指导和示例。',
      detailed: '请提供全面深入的分析和建议，包含理论依据和多种方案。',
      comprehensive: '请提供详尽的专业分析，包含理论背景、多种方案比较、具体实施步骤和注意事项。'
    };

    return formats[detailLevel] || formats.moderate;
  }

  protected estimateTokens(sections: PromptSection[], variables: DynamicVariable[]): number {
    let baseTokens = 0;

    sections.forEach(section => {
      baseTokens += Math.ceil(section.content.length / 4); // 大致估算
    });

    variables.forEach(variable => {
      baseTokens += 20; // 每个变量的平均token估算
    });

    return baseTokens;
  }

  protected generateMetadata(config: PromptConfig, sections: PromptSection[], variables: DynamicVariable[]): TemplateMetadata {
    const estimatedTokens = this.estimateTokens(sections, variables);

    return {
      estimatedTokens,
      estimatedTime: this.estimateTime(estimatedTokens),
      difficulty: config.difficulty,
      tags: this.generateTags(config),
      compatibility: {
        aiModels: [config.aiModel],
        languages: ['zh-CN']
      },
      usage: {
        count: 0,
        lastUsed: new Date()
      }
    };
  }

  protected estimateTime(tokens: number): string {
    if (tokens < 100) return '1-2分钟';
    if (tokens < 300) return '3-5分钟';
    if (tokens < 600) return '5-10分钟';
    return '10分钟以上';
  }

  private generateTags(config: PromptConfig): string[] {
    const tags = [config.category, config.difficulty, config.writingStyle];

    if (config.projectContext?.genre) {
      tags.push(config.projectContext.genre);
    }

    return tags;
  }
}

// 结构规划Prompt生成器
export class StructurePromptGenerator extends BasePromptGenerator {
  constructor() {
    super('structure');
  }

  generateTemplate(config: PromptConfig): PromptTemplate {
    const variables = this.generateVariables(config);
    const promptStructure = this.buildPromptStructure(config, variables);

    return {
      id: this.generateId(),
      title: this.generateTitle(config),
      description: this.generateDescription(config),
      category: this.category,
      variables,
      promptStructure,
      metadata: this.generateMetadata(config, promptStructure.sections, variables),
      createdAt: new Date(),
      version: '1.0'
    };
  }

  private generateVariables(config: PromptConfig): DynamicVariable[] {
    const baseVariables: DynamicVariable[] = [
      {
        name: 'structureType',
        type: 'select',
        label: '叙事结构类型',
        description: '选择故事的叙事结构框架',
        required: true,
        options: this.getStructureTypeOptions(config.difficulty),
        dependencies: []
      },
      {
        name: 'storyType',
        type: 'select',
        label: '故事类型',
        description: '选择故事的主要类型和风格',
        required: true,
        options: this.getStoryTypeOptions(config.difficulty),
        dependencies: []
      },
      {
        name: 'culturalBackground',
        type: 'select',
        label: '文化背景',
        description: '故事的文化和地域背景',
        required: true,
        options: this.getCulturalOptions()
      },
      {
        name: 'targetAudience',
        type: 'select',
        label: '目标受众',
        description: '作品的主要读者群体特征',
        required: true,
        options: this.getTargetAudienceOptions(config.difficulty)
      }
    ];

    // 根据难度添加额外变量
    if (config.difficulty === 'intermediate' || config.difficulty === 'advanced') {
      baseVariables.push({
        name: 'theme',
        type: 'textarea',
        label: '核心主题',
        description: '故事要探讨的核心主题和深层含义',
        required: false,
        placeholder: '例：成长与责任、正义与复仇、爱与牺牲...'
      });
    }

    if (config.difficulty === 'advanced') {
      baseVariables.push({
        name: 'narrativeComplexity',
        type: 'select',
        label: '叙事复杂度',
        description: '选择叙事结构的复杂程度',
        required: false,
        options: [
          { value: 'linear', label: '线性叙事' },
          { value: 'non_linear', label: '非线性叙事' },
          { value: 'multi_timeline', label: '多时间线' },
          { value: 'experimental', label: '实验性结构' }
        ]
      });
    }

    // 从前置数据提取变量
    if (config.previousStageData) {
      baseVariables.push(...this.extractContextualVariables(config.previousStageData));
    }

    return baseVariables;
  }

  private getStructureTypeOptions(difficulty: string): VariableOption[] {
    const basicStructures = [
      { value: 'three_act', label: '三幕结构', description: '经典的开始-发展-结局结构' },
      { value: 'heros_journey', label: '英雄之旅', description: '坎贝尔的经典英雄历程模式' },
      { value: 'five_act', label: '五幕结构', description: '莎士比亚式的戏剧结构' },
      { value: 'seven_point', label: '七点故事结构', description: '丹·威尔斯的故事结构模式' },
      { value: 'freytag', label: '弗莱塔格金字塔', description: '经典的戏剧冲突发展模式' },
      { value: 'save_the_cat', label: '拯救猫咪结构', description: '布莱克·斯奈德的剧本结构' }
    ];

    const advancedStructures = [
      { value: 'nonlinear', label: '非线性叙事', description: '打破时间顺序的复杂叙事' },
      { value: 'parallel', label: '平行叙事', description: '多条故事线并行发展' },
      { value: 'nested', label: '嵌套结构', description: '故事中的故事，多层叙事' },
      { value: 'circular', label: '环形结构', description: '首尾呼应的循环叙事' },
      { value: 'frame', label: '框架叙事', description: '外层故事包含内层故事' },
      { value: 'experimental', label: '实验性结构', description: '创新的叙事结构形式' }
    ];

    return difficulty === 'advanced' ? [...basicStructures, ...advancedStructures] : basicStructures;
  }

  private getStoryTypeOptions(difficulty: string): VariableOption[] {
    const basicTypes = [
      { value: 'romance', label: '言情/爱情', description: '以情感关系为核心的故事' },
      { value: 'adventure', label: '冒险', description: '充满挑战和探索的故事' },
      { value: 'mystery', label: '悬疑推理', description: '以解谜为主线的故事' },
      { value: 'fantasy', label: '奇幻', description: '包含魔法或超自然元素的故事' },
      { value: 'scifi', label: '科幻', description: '基于科学技术的未来或另类世界故事' },
      { value: 'historical', label: '历史', description: '以历史背景为基础的故事' }
    ];

    const advancedTypes = [
      { value: 'literary_fiction', label: '纯文学', description: '注重艺术性和深度的文学作品' },
      { value: 'experimental', label: '实验性叙事', description: '打破传统结构的创新作品' },
      { value: 'metafiction', label: '元小说', description: '自我指涉的后现代叙事' },
      { value: 'magical_realism', label: '魔幻现实主义', description: '现实与超现实元素融合的作品' }
    ];

    return difficulty === 'advanced' ? [...basicTypes, ...advancedTypes] : basicTypes;
  }

  private getCulturalOptions(): VariableOption[] {
    return [
      { value: 'eastern', label: '东方文化', description: '中华文化、日本文化、韩国文化等' },
      { value: 'western', label: '西方文化', description: '欧美文化传统' },
      { value: 'arabic', label: '阿拉伯文化', description: '中东和阿拉伯文化' },
      { value: 'african', label: '非洲文化', description: '非洲各地区传统文化' },
      { value: 'latin', label: '拉丁文化', description: '拉丁美洲文化' },
      { value: 'mixed', label: '多元文化', description: '融合多种文化元素' },
      { value: 'fictional', label: '虚构文化', description: '完全原创的文化设定' }
    ];
  }

  private getTargetAudienceOptions(difficulty: string): VariableOption[] {
    const basicAudiences = [
      { value: 'casual_readers', label: '休闲读者', description: '寻求轻松娱乐，偏好情节导向的故事' },
      { value: 'emotional_seekers', label: '情感共鸣者', description: '希望通过阅读获得情感体验和内心触动' },
      { value: 'knowledge_seekers', label: '知识探求者', description: '通过故事学习和思考，偏好有深度的内容' },
      { value: 'escapism_readers', label: '逃避现实者', description: '希望暂时脱离现实，沉浸在虚构世界中' },
      { value: 'inspiration_seekers', label: '励志追求者', description: '寻求正能量和人生启发的读者' },
      { value: 'genre_enthusiasts', label: '类型爱好者', description: '特定类型（如科幻、奇幻、悬疑）的忠实读者' }
    ];

    const intermediateAudiences = [
      { value: 'urban_professionals', label: '都市职场人群', description: '忙碌的白领，需要高效阅读体验' },
      { value: 'life_reflectors', label: '人生思考者', description: '正处于人生转折期，寻求价值观探索' },
      { value: 'cultural_explorers', label: '文化探索者', description: '对不同文化和社会议题感兴趣' },
      { value: 'artistic_appreciators', label: '艺术鉴赏者', description: '注重文学性和艺术表达的读者' },
      { value: 'social_critics', label: '社会观察者', description: '关注社会问题，喜欢批判性思考' },
      { value: 'identity_explorers', label: '身份认同者', description: '探索自我身份和归属感的读者群体' }
    ];

    const advancedAudiences = [
      { value: 'intellectual_elite', label: '知识精英', description: '高学历、深度思考能力强的读者群体' },
      { value: 'philosophical_minds', label: '哲学思辨者', description: '喜欢抽象思考和哲学探讨的读者' },
      { value: 'cross_cultural_thinkers', label: '跨文化思考者', description: '具有国际视野，理解多元文化的读者' },
      { value: 'avant_garde_readers', label: '先锋艺术受众', description: '接受实验性和前卫表达形式的读者' },
      { value: 'trauma_healers', label: '创伤疗愈群体', description: '通过阅读处理心理创伤和成长的读者' },
      { value: 'system_challengers', label: '制度反思者', description: '质疑现有体系，寻求变革的批判性读者' },
      { value: 'spiritual_seekers', label: '精神探寻者', description: '追求超越物质层面的精神满足的读者' }
    ];

    switch (difficulty) {
      case 'beginner':
        return basicAudiences;
      case 'intermediate':
        return [...basicAudiences, ...intermediateAudiences];
      case 'advanced':
        return [...basicAudiences, ...intermediateAudiences, ...advancedAudiences];
      default:
        return basicAudiences;
    }
  }

  private extractContextualVariables(previousData: Record<string, any>): DynamicVariable[] {
    const variables: DynamicVariable[] = [];

    // 从项目上下文提取信息
    if (previousData.projectInfo) {
      const project = previousData.projectInfo;
      if (project.existingCharacters) {
        variables.push({
          name: 'existingElements',
          type: 'textarea',
          label: '现有故事元素',
          description: '项目中已有的角色、设定等元素',
          required: false,
          defaultValue: `现有角色：${project.existingCharacters.map((c: any) => c.name).join(', ')}`
        });
      }
    }

    return variables;
  }

  private buildPromptStructure(config: PromptConfig, variables: DynamicVariable[]): PromptStructure {
    const sections: PromptSection[] = [
      {
        name: 'role_definition',
        order: 1,
        content: this.getBaseRoleDefinition(config.aiModel, this.category),
        required: true
      },
      {
        name: 'context_input',
        order: 2,
        content: this.generateContextSection(variables),
        required: true
      },
      {
        name: 'task_instructions',
        order: 3,
        content: this.getTaskInstructions(config),
        required: true
      },
      {
        name: 'output_format',
        order: 4,
        content: this.getOutputFormat(config.detailLevel),
        required: true
      }
    ];

    const conditionalSections: ConditionalSection[] = [
      {
        condition: { variable: 'storyType', equals: 'fantasy' },
        section: {
          name: 'fantasy_specific',
          order: 3.5,
          content: '请特别关注魔法系统的逻辑一致性和世界观的完整性。确保魔法规则明确且贯穿整个故事结构。',
          required: false
        }
      },
      {
        condition: { variable: 'storyType', equals: 'mystery' },
        section: {
          name: 'mystery_specific',
          order: 3.5,
          content: '请确保谜题设计合理，线索布局恰当，推理逻辑清晰。避免出现无法解释的情节漏洞。',
          required: false
        }
      }
    ];

    const dynamicInstructions: DynamicInstruction[] = [
      {
        condition: { difficulty: 'advanced' },
        instruction: '请提供详细的理论分析和多种结构方案对比，包括每种方案的优劣势分析。',
        position: 'after',
        targetSection: 'task_instructions'
      },
      {
        condition: { aiModel: 'claude' },
        instruction: '请结合具体的文学理论和叙事学原理进行分析。',
        position: 'after',
        targetSection: 'task_instructions'
      }
    ];

    return {
      sections,
      conditionalSections,
      dynamicInstructions
    };
  }

  private generateContextSection(variables: DynamicVariable[]): string {
    const variableRefs = variables.map(v => `- ${v.label}：{{${v.name}}}`).join('\n');
    return `请基于以下信息设计故事结构：\n\n${variableRefs}\n\n`;
  }

  private getTaskInstructions(config: PromptConfig): string {
    const baseInstructions = `请基于选择的{{structureType}}框架为此故事设计完整的叙事结构，包括：

1. 针对{{structureType}}的具体实施方案
2. 关键情节节点规划（根据{{structureType}}的特点安排5-7个主要节点）
3. 每个节点的功能说明和建议内容
4. 整体节奏控制建议
5. {{structureType}}结构的特殊技巧和注意事项`;

    if (config.difficulty === 'advanced') {
      return baseInstructions + `
6. 深层主题的结构化表达方式
7. 叙事视角和时间线的创新运用
8. 读者期待的管理和颠覆策略`;
    }

    return baseInstructions;
  }

  private generateTitle(config: PromptConfig): string {
    const titles = {
      beginner: '故事结构设计助手',
      intermediate: '专业故事结构规划器',
      advanced: '高级叙事结构分析师'
    };

    return titles[config.difficulty] || titles.beginner;
  }

  private generateDescription(config: PromptConfig): string {
    return `基于${config.difficulty}级别和${config.writingStyle}风格，为${config.aiModel}模型优化的故事结构设计Prompt`;
  }
}

// 角色创建Prompt生成器
export class CharacterPromptGenerator extends BasePromptGenerator {
  constructor() {
    super('character');
  }

  generateTemplate(config: PromptConfig): PromptTemplate {
    const variables = this.generateVariables(config);
    const promptStructure = this.buildPromptStructure(config, variables);

    return {
      id: this.generateId(),
      title: this.generateTitle(config),
      description: this.generateDescription(config),
      category: this.category,
      variables,
      promptStructure,
      metadata: this.generateMetadata(config, promptStructure.sections, variables),
      createdAt: new Date(),
      version: '1.0'
    };
  }

  private generateVariables(config: PromptConfig): DynamicVariable[] {
    const baseVariables: DynamicVariable[] = [
      {
        name: 'characterType',
        type: 'select',
        label: '角色类型',
        description: '角色在故事中的主要功能',
        required: true,
        options: [
          { value: 'protagonist', label: '主角', enablesVariables: ['heroicQualities'] },
          { value: 'antagonist', label: '反角', enablesVariables: ['conflictMotivation'] },
          { value: 'supporting', label: '配角', enablesVariables: ['supportFunction'] },
          { value: 'minor', label: '次要角色' }
        ]
      },
      {
        name: 'characterComplexity',
        type: 'select',
        label: '角色复杂度',
        description: '角色的心理和性格复杂程度',
        required: true,
        options: [
          { value: 'simple', label: '简单型', description: '明确的性格特征，较少内在冲突' },
          { value: 'moderate', label: '适中型', description: '有一定复杂性和成长空间' },
          { value: 'complex', label: '复杂型', description: '多面性格，深层心理冲突' },
          { value: 'contradictory', label: '矛盾型', description: '充满内在矛盾的复杂角色' }
        ]
      }
    ];

    // 条件变量
    baseVariables.push(
      {
        name: 'heroicQualities',
        type: 'multiselect',
        label: '英雄特质',
        description: '主角应具备的核心品质',
        required: false,
        options: [
          { value: 'courage', label: '勇气' },
          { value: 'determination', label: '决心' },
          { value: 'compassion', label: '同情心' },
          { value: 'wisdom', label: '智慧' },
          { value: 'leadership', label: '领导力' },
          { value: 'sacrifice', label: '牺牲精神' }
        ],
        dependencies: [
          { variable: 'characterType', condition: 'equals', value: 'protagonist', action: 'show' }
        ]
      },
      {
        name: 'conflictMotivation',
        type: 'textarea',
        label: '冲突动机',
        description: '反角的核心动机和目标',
        required: false,
        placeholder: '描述反角的深层动机、价值观冲突或创伤背景...',
        dependencies: [
          { variable: 'characterType', condition: 'equals', value: 'antagonist', action: 'show' }
        ]
      },
      {
        name: 'supportFunction',
        type: 'select',
        label: '支持功能',
        description: '配角在故事中的具体作用',
        required: false,
        options: [
          { value: 'mentor', label: '导师型', description: '提供指导和智慧' },
          { value: 'ally', label: '盟友型', description: '协助主角完成任务' },
          { value: 'love_interest', label: '情感支柱', description: '提供情感支持和动力' },
          { value: 'comic_relief', label: '调剂型', description: '缓解紧张气氛' },
          { value: 'catalyst', label: '催化剂', description: '推动情节发展' }
        ],
        dependencies: [
          { variable: 'characterType', condition: 'equals', value: 'supporting', action: 'show' }
        ]
      }
    );

    // 从前置数据提取变量
    if (config.previousStageData?.structure) {
      baseVariables.push(...this.extractFromStructure(config.previousStageData.structure));
    }

    return baseVariables;
  }

  private extractFromStructure(structureData: any): DynamicVariable[] {
    const extractedVariables: DynamicVariable[] = [];

    if (structureData.theme) {
      extractedVariables.push({
        name: 'themeAlignment',
        type: 'textarea',
        label: '与主题的关联',
        description: `如何体现故事主题：${structureData.theme}`,
        required: true,
        defaultValue: `这个角色将通过...来体现"${structureData.theme}"这一主题`,
        placeholder: '描述角色如何通过行为、选择或成长来体现故事主题...'
      });
    }

    if (structureData.plotPoints) {
      extractedVariables.push({
        name: 'plotFunction',
        type: 'select',
        label: '在关键情节中的作用',
        description: '角色在故事关键节点的具体功能',
        required: true,
        options: structureData.plotPoints.map((point: any) => ({
          value: point.id,
          label: `${point.name}阶段的作用`,
          description: point.description
        }))
      });
    }

    if (structureData.storyType) {
      // 根据故事类型调整角色特征
      const typeSpecificVariables = this.getTypeSpecificVariables(structureData.storyType);
      extractedVariables.push(...typeSpecificVariables);
    }

    return extractedVariables;
  }

  private getTypeSpecificVariables(storyType: string): DynamicVariable[] {
    const typeVariables: Record<string, DynamicVariable[]> = {
      fantasy: [
        {
          name: 'magicalAbilities',
          type: 'textarea',
          label: '魔法能力',
          description: '角色的魔法或超自然能力',
          required: false,
          placeholder: '描述角色的魔法能力、限制和成长潜力...'
        }
      ],
      mystery: [
        {
          name: 'investigativeSkills',
          type: 'multiselect',
          label: '调查技能',
          description: '角色的推理和调查能力',
          required: false,
          options: [
            { value: 'observation', label: '观察力' },
            { value: 'deduction', label: '推理能力' },
            { value: 'psychology', label: '心理分析' },
            { value: 'forensics', label: '物证分析' }
          ]
        }
      ],
      romance: [
        {
          name: 'romanticTraits',
          type: 'multiselect',
          label: '浪漫特质',
          description: '在情感关系中的表现特征',
          required: false,
          options: [
            { value: 'passionate', label: '热情' },
            { value: 'tender', label: '温柔' },
            { value: 'protective', label: '保护欲' },
            { value: 'vulnerable', label: '脆弱性' }
          ]
        }
      ]
    };

    return typeVariables[storyType] || [];
  }

  private buildPromptStructure(config: PromptConfig, variables: DynamicVariable[]): PromptStructure {
    const sections: PromptSection[] = [
      {
        name: 'role_definition',
        order: 1,
        content: this.getBaseRoleDefinition(config.aiModel, this.category),
        required: true
      },
      {
        name: 'context_input',
        order: 2,
        content: this.generateContextSection(variables),
        required: true
      },
      {
        name: 'character_requirements',
        order: 3,
        content: this.getCharacterRequirements(config),
        required: true
      },
      {
        name: 'output_format',
        order: 4,
        content: this.getOutputFormat(config.detailLevel),
        required: true
      }
    ];

    return { sections };
  }

  private generateContextSection(variables: DynamicVariable[]): string {
    const variableRefs = variables.map(v => `- ${v.label}：{{${v.name}}}`).join('\n');
    return `请基于以下要求创建角色：\n\n${variableRefs}\n\n`;
  }

  private getCharacterRequirements(config: PromptConfig): string {
    const baseRequirements = `请为这个角色设计：

1. 基本信息（姓名、年龄、职业、社会地位）
2. 外貌特征（突出个性的外貌描述）
3. 性格特质（3-5个核心特质，包含正面和负面）
4. 价值观体系（最重要的2-3个价值观）
5. 恐惧与欲望（内在驱动力）
6. 背景故事（关键的成长经历）
7. 语言风格（说话特点和口头禅）
8. 与其他角色的关系设定`;

    if (config.difficulty === 'advanced') {
      return baseRequirements + `
9. 深层心理分析（潜意识冲突和防御机制）
10. 角色弧线设计（从开始到结束的转变）
11. 象征意义（角色在主题层面的作用）
12. 读者情感连接点（如何引发读者共鸣）`;
    }

    return baseRequirements;
  }

  private generateTitle(config: PromptConfig): string {
    const titles = {
      beginner: '角色创建助手',
      intermediate: '深度角色塑造师',
      advanced: '复杂角色心理分析师'
    };

    return titles[config.difficulty] || titles.beginner;
  }

  private generateDescription(config: PromptConfig): string {
    return `基于${config.difficulty}级别，创建具有丰富内在世界的立体角色`;
  }
}

// 场景Prompt生成器
export class ScenePromptGenerator extends BasePromptGenerator {
  constructor() {
    super('scene');
  }

  generateTemplate(config: PromptConfig): PromptTemplate {
    const variables = this.generateVariables(config);

    const template: PromptTemplate = {
      id: `scene_${Date.now()}`,
      category: 'scene',
      title: this.generateTitle(config),
      description: this.generateDescription(config),
      version: '1.0',
      variables,
      promptStructure: {
        sections: [
          {
            name: 'system_prompt',
            order: 1,
            content: this.getSystemPrompt(config),
            required: true
          },
          {
            name: 'context_input',
            order: 2,
            content: this.generateContextSection(variables),
            required: true
          },
          {
            name: 'task_instructions',
            order: 3,
            content: this.getTaskInstructions(config, variables),
            required: true
          },
          {
            name: 'output_format',
            order: 4,
            content: this.getOutputFormat(config.detailLevel),
            required: true
          }
        ]
      },
      createdAt: new Date(),
      metadata: this.generateSceneMetadata(config, [
        {
          name: 'system_prompt',
          order: 1,
          content: this.getSystemPrompt(config),
          required: true
        },
        {
          name: 'context_input',
          order: 2,
          content: this.generateContextSection(variables),
          required: true
        },
        {
          name: 'task_instructions',
          order: 3,
          content: this.getTaskInstructions(config, variables),
          required: true
        },
        {
          name: 'output_format',
          order: 4,
          content: this.getOutputFormat(config.detailLevel),
          required: true
        }
      ], variables)
    };

    return template;
  }

  private generateVariables(config: PromptConfig): DynamicVariable[] {
    const baseVariables: DynamicVariable[] = [
      {
        name: 'sceneType',
        type: 'select',
        label: '场景类型',
        description: '选择要创建的场景类型',
        required: true,
        options: [
          { value: 'action', label: '动作场景', description: '高能量的行动和冲突场景' },
          { value: 'dialogue', label: '对话场景', description: '角色间的深度交流场景' },
          { value: 'description', label: '描写场景', description: '重点展现环境和氛围' },
          { value: 'emotional', label: '情感场景', description: '探索角色内心世界' },
          { value: 'transition', label: '过渡场景', description: '连接不同情节段落' }
        ],
        dependencies: []
      },
      {
        name: 'location',
        type: 'text',
        label: '场景地点',
        description: '场景发生的具体位置',
        required: true,
        placeholder: '例：古老的图书馆、繁华的市集、神秘的森林...'
      },
      {
        name: 'timeOfDay',
        type: 'select',
        label: '时间段',
        description: '场景发生的时间',
        required: true,
        options: [
          { value: 'dawn', label: '黎明' },
          { value: 'morning', label: '上午' },
          { value: 'noon', label: '中午' },
          { value: 'afternoon', label: '下午' },
          { value: 'dusk', label: '黄昏' },
          { value: 'night', label: '夜晚' },
          { value: 'midnight', label: '深夜' }
        ]
      },
      {
        name: 'atmosphere',
        type: 'select',
        label: '主要氛围',
        description: '场景的整体情感基调',
        required: true,
        options: [
          { value: 'tense', label: '紧张' },
          { value: 'peaceful', label: '宁静' },
          { value: 'mysterious', label: '神秘' },
          { value: 'romantic', label: '浪漫' },
          { value: 'dangerous', label: '危险' },
          { value: 'melancholic', label: '忧郁' },
          { value: 'joyful', label: '欢快' },
          { value: 'dramatic', label: '戏剧性' }
        ]
      },
      {
        name: 'characters',
        type: 'textarea',
        label: '参与角色',
        description: '场景中出现的主要角色及其状态',
        required: true,
        placeholder: '描述参与此场景的角色，包括他们的情绪状态和动机...'
      }
    ];

    // 根据难度添加额外变量
    if (config.difficulty === 'intermediate' || config.difficulty === 'advanced') {
      baseVariables.push({
        name: 'sensoryDetails',
        type: 'textarea',
        label: '感官细节要求',
        description: '指定需要重点描写的感官体验',
        required: false,
        placeholder: '例：重点描写听觉和嗅觉、营造视觉冲击、突出触觉感受...'
      });

      baseVariables.push({
        name: 'pacing',
        type: 'select',
        label: '节奏控制',
        description: '场景的叙述节奏',
        required: false,
        options: [
          { value: 'slow', label: '慢节奏 - 细腻描述' },
          { value: 'medium', label: '中等节奏 - 平衡发展' },
          { value: 'fast', label: '快节奏 - 紧凑推进' },
          { value: 'variable', label: '变化节奏 - 张弛有度' }
        ]
      });
    }

    if (config.difficulty === 'advanced') {
      baseVariables.push({
        name: 'symbolism',
        type: 'textarea',
        label: '象征意义',
        description: '场景需要承载的象征意义或隐喻',
        required: false,
        placeholder: '例：用天气变化暗示情感转折、通过环境对比体现内心冲突...'
      });

      baseVariables.push({
        name: 'narrativeFunction',
        type: 'select',
        label: '叙事功能',
        description: '此场景在整个故事中的作用',
        required: false,
        options: [
          { value: 'exposition', label: '背景铺垫' },
          { value: 'conflict', label: '冲突爆发' },
          { value: 'climax', label: '高潮展现' },
          { value: 'resolution', label: '问题解决' },
          { value: 'character_development', label: '角色发展' },
          { value: 'theme_exploration', label: '主题探索' }
        ]
      });
    }

    // 从前置数据提取变量
    if (config.previousStageData) {
      baseVariables.push(...this.extractContextualVariables(config.previousStageData));
    }

    return baseVariables;
  }

  private getSystemPrompt(config: PromptConfig): string {
    const modelSpecific = this.getBaseRoleDefinition(config.aiModel, this.category);

    return `${modelSpecific}

你是一位专业的创意写作指导师，擅长创建富有感官体验和情感深度的故事场景。你的任务是帮助用户创建一个多维度的场景描述，该场景应该：

1. 具有强烈的视觉画面感
2. 包含丰富的感官细节
3. 营造恰当的情感氛围
4. 推动故事情节发展
5. 体现角色的内在状态

请基于用户提供的信息，创建一个具体、生动、有层次的场景描述。`;
  }

  private getTaskInstructions(config: PromptConfig, variables: DynamicVariable[]): string {
    const difficultyInstructions = {
      beginner: `
请创建一个基础的场景描述，包含：
- 清晰的环境设定
- 基本的感官描述
- 角色的基本行为和对话
- 简单的情感氛围`,

      intermediate: `
请创建一个中等复杂度的场景，包含：
- 详细的环境描述和氛围营造
- 多层次的感官体验（视觉、听觉、嗅觉等）
- 角色的内心活动和外在表现
- 场景与情节的有机结合
- 适当的节奏控制`,

      advanced: `
请创建一个高级场景，包含：
- 深层的象征意义和隐喻
- 复杂的情感层次和心理描写
- 精妙的细节设计和伏笔铺设
- 多维度的感官体验融合
- 与整体叙事结构的呼应
- 独特的叙述视角和技巧`
    };

    return `## 创作任务

基于以下信息创建场景：

{{sceneType}} | {{location}} | {{timeOfDay}} | {{atmosphere}}

**参与角色：**
{{characters}}

${variables.find(v => v.name === 'sensoryDetails') ? '**感官重点：**\n{{sensoryDetails}}\n' : ''}
${variables.find(v => v.name === 'pacing') ? '**节奏要求：**\n{{pacing}}\n' : ''}
${variables.find(v => v.name === 'symbolism') ? '**象征意义：**\n{{symbolism}}\n' : ''}
${variables.find(v => v.name === 'narrativeFunction') ? '**叙事功能：**\n{{narrativeFunction}}\n' : ''}

${difficultyInstructions[config.difficulty]}`;
  }

  protected getOutputFormat(detailLevel: string): string {
    const formats = {
      brief: `
## 输出格式

请按以下结构输出场景：

**场景标题：**
[给场景起一个吸引人的标题]

**环境描述：**
[2-3段描述场景环境和氛围]

**角色行为：**
[描述角色在此场景中的行为和对话]

**情感基调：**
[1段总结场景的情感氛围和意义]`,

      detailed: `
## 输出格式

请按以下结构输出详细场景：

**场景标题：**
[给场景起一个吸引人的标题]

**开场设定：**
[1-2段建立场景的时间、地点、天气等基础信息]

**环境描述：**
[3-4段详细描述环境，包含多种感官体验]

**角色呈现：**
[2-3段描述角色的外在表现和内心活动]

**情节推进：**
[2-3段展现场景中发生的具体事件]

**收尾过渡：**
[1-2段为下一个场景或情节做铺垫]

**创作要点：**
[列出3-5个该场景的写作亮点]`,

      comprehensive: `
## 输出格式

请按以下结构输出完整场景分析：

**场景概览：**
- 场景标题：[吸引人的标题]
- 时空设定：[具体的时间地点]
- 核心冲突：[场景的主要矛盾]
- 叙事功能：[在故事中的作用]

**多维描述：**

*视觉层面：*
[详细的视觉描述，包含色彩、光影、构图]

*听觉层面：*
[声音环境的营造和变化]

*嗅觉触觉：*
[气味和触觉的细节描写]

*情感氛围：*
[情绪基调和心理环境]

**角色塑造：**
- 外在表现：[动作、表情、对话]
- 内心活动：[思考、情感、动机]
- 角色关系：[人物间的互动动态]

**叙事技巧：**
- 视角选择：[叙述视角和理由]
- 节奏控制：[快慢变化的安排]
- 象征手法：[隐喻和象征的运用]

**扩展建议：**
[后续发展的可能性和写作建议]`
    };

    return formats[detailLevel] || formats.detailed;
  }

  private extractContextualVariables(previousData: Record<string, any>): DynamicVariable[] {
    const variables: DynamicVariable[] = [];

    // 从项目上下文提取信息
    if (previousData.projectInfo) {
      const project = previousData.projectInfo;
      if (project.worldSettings) {
        variables.push({
          name: 'worldContext',
          type: 'text',
          label: '世界背景',
          description: '基于已创建的世界设定',
          required: false,
          defaultValue: project.worldSettings.name || ''
        });
      }

      if (project.existingCharacters) {
        variables.push({
          name: 'availableCharacters',
          type: 'multiselect',
          label: '可用角色',
          description: '选择参与此场景的现有角色',
          required: false,
          options: project.existingCharacters.map((char: any) => ({
            value: char.id,
            label: char.name,
            description: char.role || ''
          }))
        });
      }
    }

    return variables;
  }

  private generateContextSection(variables: DynamicVariable[]): string {
    return `## 创作背景

${variables.map(v => `**${v.label}：** {{${v.name}}}`).join('\n')}`;
  }

  private generateSceneMetadata(config: PromptConfig, sections: PromptSection[], variables: DynamicVariable[]): TemplateMetadata {
    const estimatedTokens = this.estimateTokens(sections, variables);

    return {
      estimatedTokens,
      estimatedTime: this.estimateTime(estimatedTokens),
      difficulty: config.difficulty,
      tags: ['场景创作', '多维描述', '感官体验', '情感氛围'],
      compatibility: {
        aiModels: [config.aiModel || 'generic'],
        languages: ['zh-CN']
      },
      usage: {
        count: 0,
        lastUsed: new Date()
      }
    };
  }

  private generateTitle(config: PromptConfig): string {
    const difficultyLabels = {
      beginner: '基础',
      intermediate: '中级',
      advanced: '高级'
    };

    return `${difficultyLabels[config.difficulty]}多维场景创作`;
  }

  private generateDescription(config: PromptConfig): string {
    return `基于${config.difficulty}级别，创建富有感官体验和情感深度的故事场景`;
  }
}

// Prompt生成器工厂
export class PromptGeneratorFactory {
  private static generators: Map<string, BasePromptGenerator> = new Map();

  static getGenerator(category: string): BasePromptGenerator {
    if (!this.generators.has(category)) {
      switch (category) {
        case 'structure':
          this.generators.set(category, new StructurePromptGenerator());
          break;
        case 'character':
          this.generators.set(category, new CharacterPromptGenerator());
          break;
        case 'scene':
          this.generators.set(category, new ScenePromptGenerator());
          break;
        // TODO: 添加其他生成器
        default:
          throw new Error(`不支持的类别: ${category}`);
      }
    }

    return this.generators.get(category)!;
  }

  static getSupportedCategories(): string[] {
    return ['structure', 'character', 'world', 'scene', 'dialogue'];
  }
}