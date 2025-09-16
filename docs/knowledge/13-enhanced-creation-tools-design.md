# 增强版基础创作工具设计

## 概述
基于12大知识模块构建的完整基础创作工具体系，从单一工具扩展为全方位创作支持平台，涵盖从创意构思到成品输出的全创作流程。

## 🛠️ **完整工具体系架构**

### 核心设计原则
1. **模块化设计**: 每个工具独立运行，可组合使用
2. **数据互通**: 工具间信息共享和智能关联
3. **渐进式使用**: 从简单到复杂的使用路径
4. **智能辅助**: AI驱动的创作建议和优化

---

## 📚 **12大模块对应的基础创作工具**

### 1. 叙事结构构建工具 (Narrative Structure Builder)

#### 1.1 故事结构选择器
**功能**：根据故事类型和文化背景选择适合的叙事结构
```typescript
interface StructureSelector {
  storyType: 'fantasy' | 'romance' | 'mystery' | 'scifi' | 'realistic';
  culturalBackground: 'western' | 'eastern' | 'african' | 'arabic' | 'mixed';
  recommendedStructures: NarrativeStructure[];
  customizationOptions: StructureCustomization[];
}
```

**核心功能**：
- **结构模板库**: 三幕式、英雄之旅、起承转合、非线性等
- **文化适配器**: 不同文化背景的叙事传统
- **结构可视化**: 结构图表和时间轴展示
- **进度跟踪**: 创作进度与结构节点对应

#### 1.2 情节节点规划器
**功能**：规划和管理关键情节节点
- 开场钩子设计
- 转折点规划
- 高潮设计
- 结局类型选择

### 2. 深度角色创作套件 (Advanced Character Creation Suite)

#### 2.1 角色档案生成器 (扩展现有工具)
**新增功能**：
- **心理档案生成**: 基于心理学理论的性格分析
- **角色关系图谱**: 可视化人物关系网络
- **角色声音分析**: 语言风格和说话习惯定义
- **角色成长轨迹**: 完整的角色弧线规划

#### 2.2 角色对话生成器
**功能**：为不同角色生成符合其性格的对话
```typescript
interface DialogueGenerator {
  characterId: string;
  context: SceneContext;
  emotionalState: EmotionalState;
  generateDialogue: (prompt: string) => string[];
  styleConsistency: boolean;
}
```

#### 2.3 角色冲突设计器
**功能**：设计角色间的冲突和矛盾
- 价值观冲突生成
- 利益冲突分析
- 情感纠葛设计
- 冲突升级路径

### 3. 智能世界构建平台 (Intelligent Worldbuilding Platform)

#### 3.1 世界设定生成器 (扩展现有工具)
**新增功能**：
- **文化生成器**: 自动生成独特文化背景
- **历史事件编织器**: 构建完整历史时间线
- **经济系统设计器**: 货币、贸易、资源分布
- **语言创造工具**: 简化的人工语言构建

#### 3.2 世界一致性检查器
**功能**：检查世界设定的逻辑一致性
- 物理法则验证
- 社会制度合理性检查
- 文化内在逻辑验证
- 科技发展合理性分析

### 4. 多维场景创作工具 (Multi-dimensional Scene Creator)

#### 4.1 感官场景构建器 (扩展现有工具)
**新增功能**：
- **氛围情绪调色板**: 不同情绪对应的环境设置
- **感官细节生成器**: 五感描写的智能建议
- **场景功能分析器**: 分析场景在故事中的作用
- **环境互动设计器**: 环境与角色/情节的互动关系

#### 4.2 场景转换管理器
**功能**：管理场景间的转换和连接
- 转场技巧库
- 时空跳跃处理
- 场景节奏控制
- 读者注意力管理

### 5. 对话创作增强器 (Dialogue Enhancement Suite)

#### 5.1 对话质量分析器
**功能**：分析和优化对话质量
```typescript
interface DialogueAnalyzer {
  analyzeNaturalness: (dialogue: string) => QualityScore;
  checkCharacterConsistency: (dialogue: string, characterId: string) => boolean;
  analyzePacing: (dialogue: string) => PacingAnalysis;
  suggestImprovements: (dialogue: string) => Suggestion[];
}
```

#### 5.2 潜台词设计工具
**功能**：帮助创作具有深层含义的对话
- 隐含意思分析
- 情感潜流设计
- 冲突暗示技巧
- 伏笔对话构建

### 6. 文学技法应用器 (Literary Techniques Applicator)

#### 6.1 修辞手法库
**功能**：提供各类修辞手法的使用指导
- 比喻生成器
- 象征元素库
- 对比技巧指导
- 重复结构设计

#### 6.2 叙事视角切换器
**功能**：管理不同叙事视角的使用
- 视角一致性检查
- 视角转换建议
- 信息披露控制
- 读者同理心管理

### 7. 类型化创作助手 (Genre-specific Creation Assistant)

#### 7.1 类型规范检查器
**功能**：检查是否符合特定类型的创作规范
```typescript
interface GenreChecker {
  genre: 'fantasy' | 'mystery' | 'romance' | 'scifi' | 'thriller';
  checkConventions: (story: Story) => ComplianceReport;
  suggestImprovements: (story: Story) => GenreAdvice[];
  readerExpectations: ExpectationGuide;
}
```

#### 7.2 类型元素生成器
**功能**：为特定类型生成相应元素
- 奇幻：魔法系统、种族设定、法宝设计
- 科幻：科技概念、未来社会、太空设定
- 悬疑：谜题设计、线索布局、推理逻辑
- 言情：情感节点、浪漫场景、冲突设计

### 8. 情节冲突编织器 (Plot Conflict Weaver)

#### 8.1 冲突层次管理器
**功能**：管理多层次的故事冲突
- 主线冲突设计
- 支线冲突编织
- 内外冲突平衡
- 冲突解决策略

#### 8.2 悬念张力控制器
**功能**：控制故事的悬念和张力
- 悬念密度分析
- 张力曲线可视化
- 信息释放节奏
- 读者期待管理

### 9. 创作流程管理器 (Writing Process Manager)

#### 9.1 创作状态跟踪器
**功能**：跟踪和分析创作状态
```typescript
interface WritingTracker {
  dailyWordCount: number;
  creativeFlow: FlowState;
  blockagePoints: BlockageAnalysis[];
  productivityTrends: ProductivityData;
  motivationLevel: MotivationMetrics;
}
```

#### 9.2 写作习惯优化器
**功能**：优化个人写作习惯和流程
- 最佳写作时间分析
- 创作环境优化建议
- 写作节奏调整
- 灵感捕捉系统

### 10. 跨文化内容顾问 (Cross-cultural Content Advisor)

#### 10.1 文化敏感性检查器
**功能**：检查内容的文化适宜性
- 刻板印象检测
- 文化误用警告
- 敏感内容标识
- 多元化建议

#### 10.2 文化元素融合器
**功能**：帮助融合不同文化元素
- 文化背景库
- 融合可行性分析
- 冲突点预警
- 和谐融合建议

### 11. 数字创作优化器 (Digital Creation Optimizer)

#### 11.1 多平台适配器
**功能**：优化不同平台的内容表现
```typescript
interface PlatformOptimizer {
  platform: 'web_novel' | 'print_book' | 'audiobook' | 'interactive';
  optimizeForPlatform: (content: Content) => OptimizedContent;
  formatGuidelines: PlatformGuidelines;
  engagementTips: EngagementStrategy[];
}
```

#### 11.2 读者互动分析器
**功能**：分析和利用读者反馈
- 评论情感分析
- 热点话题识别
- 读者偏好追踪
- 内容调整建议

### 12. 综合质量评估中心 (Comprehensive Quality Assessment Center)

#### 12.1 多维度质量分析器
**功能**：从多个维度评估创作质量
```typescript
interface QualityAssessment {
  storyCore: CoreQuality;        // 故事内核质量
  structure: StructuralQuality; // 结构完整性
  characters: CharacterQuality; // 角色塑造质量
  language: LanguageQuality;    // 语言表达质量
  genre: GenreQuality;         // 类型符合度
  cultural: CulturalQuality;   // 文化适宜性
  overall: OverallScore;       // 综合评分
}
```

#### 12.2 智能优化建议器
**功能**：提供针对性的优化建议
- 问题诊断报告
- 优先级排序
- 具体改进方案
- 成效追踪系统

---

## 🔗 **工具间协作机制**

### 数据流设计：Prompt系统架构
```
创意输入 → 结构规划 → 角色创建 → 世界构建 → 场景设计 → 对话创作 → 质量评估 → 优化建议
    ↓           ↓         ↓         ↓         ↓         ↓         ↓         ↓
结构Prompt ← 角色Prompt ← 世界Prompt ← 场景Prompt ← 对话Prompt ← 评估Prompt ← 优化Prompt ← 成品Prompt
    ↓           ↓         ↓         ↓         ↓         ↓         ↓         ↓
  [复制]     [复制]     [复制]     [复制]     [复制]     [复制]     [复制]     [复制]
    ↓           ↓         ↓         ↓         ↓         ↓         ↓         ↓
 AI创作工具 ← ChatGPT ← Claude ← Gemini ← 其他AI工具 ← 本地AI ← API调用 ← 第三方服务
```

### Prompt系统核心设计

#### 数据结构定义
```typescript
interface PromptSystem {
  id: string;
  category: 'structure' | 'character' | 'world' | 'scene' | 'dialogue' | 'assessment';
  title: string;
  description: string;
  prompt: string;
  variables: PromptVariable[];
  metadata: PromptMetadata;
  version: string;
  createdAt: Date;
  updatedAt: Date;
}

interface PromptVariable {
  name: string;
  type: 'text' | 'select' | 'multiline' | 'number';
  label: string;
  defaultValue?: string;
  options?: string[]; // for select type
  required: boolean;
  placeholder?: string;
}

interface PromptMetadata {
  aiModel: 'claude' | 'gpt' | 'gemini' | 'generic';
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedTokens: number;
  tags: string[];
  usage: PromptUsage;
}

interface PromptUsage {
  count: number;
  lastUsed: Date;
  rating: number;
  feedback: string[];
}
```

#### 复制功能接口
```typescript
interface PromptCopyService {
  copyToClipboard: (promptId: string, variables: Record<string, any>) => Promise<boolean>;
  generatePrompt: (promptId: string, variables: Record<string, any>) => string;
  exportPrompt: (promptId: string, format: 'text' | 'json' | 'markdown') => string;
  sharePrompt: (promptId: string) => Promise<string>; // returns share URL
}
```

### 智能关联系统
- **Prompt生成**: 基于前置阶段数据自动生成下一阶段Prompt
- **变量注入**: 已有信息自动填充到Prompt变量
- **模板推荐**: 基于使用情况推荐相关Prompt模板
- **一致性保持**: 跨阶段的Prompt内容一致性检查

---

## 🎯 **使用场景和工作流程**

### 动态Prompt模板生成系统

#### Prompt模板生成器
```typescript
interface PromptTemplateGenerator {
  // 基于用户选择生成模板
  generateTemplate: (config: PromptConfig) => PromptTemplate;

  // 模板配置
  config: {
    category: 'structure' | 'character' | 'world' | 'scene' | 'dialogue';
    userPreferences: UserPreferences;
    contextData: ContextData;
    outputFormat: 'detailed' | 'concise' | 'creative' | 'professional';
  };
}

interface PromptConfig {
  // 基础配置
  category: string;
  subcategory?: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';

  // 用户偏好
  writingStyle: 'narrative' | 'analytical' | 'creative' | 'technical';
  detailLevel: 'brief' | 'moderate' | 'detailed' | 'comprehensive';
  aiModel: 'claude' | 'gpt' | 'gemini' | 'generic';

  // 上下文数据
  previousStageData?: Record<string, any>;
  projectContext?: ProjectContext;
  userGoals?: string[];
}

interface PromptTemplate {
  id: string;
  title: string;
  description: string;
  variables: DynamicVariable[];
  promptStructure: PromptStructure;
  metadata: TemplateMetadata;
}

interface DynamicVariable {
  name: string;
  type: 'text' | 'select' | 'multiselect' | 'textarea' | 'number' | 'boolean';
  label: string;
  description?: string;
  required: boolean;
  defaultValue?: any;
  options?: VariableOption[];
  validation?: ValidationRule[];
  dependencies?: VariableDependency[];
}

interface VariableOption {
  value: string;
  label: string;
  description?: string;
  enablesVariables?: string[];
  disablesVariables?: string[];
}

interface PromptStructure {
  sections: PromptSection[];
  conditionalSections?: ConditionalSection[];
  dynamicInstructions?: DynamicInstruction[];
}

interface PromptSection {
  name: string;
  order: number;
  content: string;
  required: boolean;
  conditions?: ConditionRule[];
}
```

#### 动态模板生成实例

##### 1. 结构规划模板生成器
```typescript
class StructurePromptGenerator {
  generateTemplate(config: PromptConfig): PromptTemplate {
    const { difficulty, writingStyle, aiModel, previousStageData } = config;

    // 根据难度和风格动态调整变量
    const variables: DynamicVariable[] = [
      {
        name: 'storyType',
        type: 'select',
        label: '故事类型',
        required: true,
        options: this.getStoryTypeOptions(difficulty),
        dependencies: [
          {
            variable: 'structureComplexity',
            condition: 'equals',
            value: 'fantasy',
            action: 'show'
          }
        ]
      },
      {
        name: 'culturalBackground',
        type: 'select',
        label: '文化背景',
        required: true,
        options: this.getCulturalOptions(writingStyle)
      },
      // 根据AI模型调整提示复杂度
      ...(aiModel === 'claude' ? this.getAdvancedVariables() : this.getBasicVariables()),
      // 如果有前置数据，自动填充相关变量
      ...(previousStageData ? this.getContextualVariables(previousStageData) : [])
    ];

    const promptStructure = this.buildPromptStructure(config, variables);

    return {
      id: `structure_${Date.now()}`,
      title: this.generateTitle(config),
      description: this.generateDescription(config),
      variables,
      promptStructure,
      metadata: this.generateMetadata(config)
    };
  }

  private buildPromptStructure(config: PromptConfig, variables: DynamicVariable[]): PromptStructure {
    const basePrompt = this.getBasePrompt(config.aiModel);
    const specificInstructions = this.getSpecificInstructions(config);
    const outputFormat = this.getOutputFormat(config.detailLevel);

    return {
      sections: [
        {
          name: 'role_definition',
          order: 1,
          content: basePrompt.roleDefinition,
          required: true
        },
        {
          name: 'context_input',
          order: 2,
          content: this.generateContextSection(variables),
          required: true
        },
        {
          name: 'specific_instructions',
          order: 3,
          content: specificInstructions,
          required: true
        },
        {
          name: 'output_format',
          order: 4,
          content: outputFormat,
          required: true
        }
      ],
      conditionalSections: [
        {
          condition: { variable: 'storyType', equals: 'fantasy' },
          section: {
            name: 'fantasy_specific',
            order: 3.5,
            content: '请特别关注魔法系统和世界观的逻辑一致性。',
            required: false
          }
        }
      ],
      dynamicInstructions: [
        {
          condition: { difficulty: 'advanced' },
          instruction: '请提供详细的理论分析和多种方案对比。'
        }
      ]
    };
  }

  private getBasePrompt(aiModel: string): { roleDefinition: string } {
    const roleDefinitions = {
      claude: '作为一名专业的叙事结构专家和创意写作导师，你具有深厚的文学理论功底和丰富的创作指导经验。',
      gpt: '你是一个专业的故事结构设计师，精通各种叙事技巧和创作理论。',
      gemini: '作为创作导师，你将运用专业知识帮助用户构建优秀的故事结构。',
      generic: '作为专业的故事结构顾问，请提供专业的创作建议。'
    };

    return {
      roleDefinition: roleDefinitions[aiModel] || roleDefinitions.generic
    };
  }

  private getStoryTypeOptions(difficulty: string): VariableOption[] {
    const basicTypes = [
      { value: 'romance', label: '言情/爱情', description: '以情感关系为核心的故事' },
      { value: 'adventure', label: '冒险', description: '充满挑战和探索的故事' },
      { value: 'mystery', label: '悬疑推理', description: '以解谜为主线的故事' }
    ];

    const advancedTypes = [
      { value: 'literary_fiction', label: '纯文学', description: '注重艺术性和深度的文学作品' },
      { value: 'experimental', label: '实验性叙事', description: '打破传统结构的创新作品' },
      { value: 'metafiction', label: '元小说', description: '自我指涉的后现代叙事' }
    ];

    return difficulty === 'advanced' ? [...basicTypes, ...advancedTypes] : basicTypes;
  }

  private generateContextSection(variables: DynamicVariable[]): string {
    const variableRefs = variables.map(v => `- ${v.label}：{{${v.name}}}`).join('\n');

    return `请基于以下信息设计故事结构：\n\n${variableRefs}\n\n`;
  }
}
```

##### 2. 角色创建模板生成器
```typescript
class CharacterPromptGenerator {
  generateTemplate(config: PromptConfig): PromptTemplate {
    const { difficulty, previousStageData } = config;

    // 如果有结构规划数据，自动生成相关变量
    const structureBasedVariables = this.extractFromStructure(previousStageData?.structure);

    const variables: DynamicVariable[] = [
      {
        name: 'characterType',
        type: 'select',
        label: '角色类型',
        required: true,
        options: [
          { value: 'protagonist', label: '主角', enablesVariables: ['heroicQualities'] },
          { value: 'antagonist', label: '反角', enablesVariables: ['conflictMotivation'] },
          { value: 'supporting', label: '配角', enablesVariables: ['supportFunction'] }
        ]
      },
      // 动态变量：基于故事结构自动生成
      ...structureBasedVariables,
      // 条件变量：基于角色类型显示
      {
        name: 'heroicQualities',
        type: 'multiselect',
        label: '英雄特质',
        required: false,
        options: this.getHeroicQualities(),
        dependencies: [
          { variable: 'characterType', condition: 'equals', value: 'protagonist', action: 'show' }
        ]
      }
    ];

    return {
      id: `character_${Date.now()}`,
      title: '动态角色创建助手',
      description: '基于故事需求和用户偏好生成角色创建Prompt',
      variables,
      promptStructure: this.buildCharacterPromptStructure(config, variables),
      metadata: this.generateMetadata(config)
    };
  }

  private extractFromStructure(structureData?: any): DynamicVariable[] {
    if (!structureData) return [];

    const extractedVariables: DynamicVariable[] = [];

    // 从故事结构中提取主题
    if (structureData.theme) {
      extractedVariables.push({
        name: 'themeAlignment',
        type: 'textarea',
        label: '与主题的关联',
        description: `如何体现故事主题：${structureData.theme}`,
        required: true,
        defaultValue: `这个角色将通过...来体现"${structureData.theme}"这一主题`
      });
    }

    // 从结构节点提取角色需求
    if (structureData.plotPoints) {
      extractedVariables.push({
        name: 'plotFunction',
        type: 'select',
        label: '在关键情节中的作用',
        required: true,
        options: structureData.plotPoints.map((point: any) => ({
          value: point.id,
          label: `${point.name}阶段的作用`,
          description: point.description
        }))
      });
    }

    return extractedVariables;
  }
}
```

##### 3. 模板选择界面
```tsx
const DynamicPromptSelector: React.FC = () => {
  const [config, setConfig] = useState<PromptConfig>({
    category: 'structure',
    difficulty: 'beginner',
    writingStyle: 'narrative',
    detailLevel: 'moderate',
    aiModel: 'claude'
  });

  const [generatedTemplate, setGeneratedTemplate] = useState<PromptTemplate | null>(null);

  const handleConfigChange = (newConfig: Partial<PromptConfig>) => {
    const updatedConfig = { ...config, ...newConfig };
    setConfig(updatedConfig);

    // 实时生成新模板
    const generator = getPromptGenerator(updatedConfig.category);
    const template = generator.generateTemplate(updatedConfig);
    setGeneratedTemplate(template);
  };

  return (
    <VStack gap={6} align="stretch">
      {/* 配置选择区域 */}
      <Card.Root variant="outline">
        <Box p={6}>
          <Heading size="md" mb={4}>Prompt配置</Heading>

          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} gap={4}>
            <Field.Root>
              <Field.Label>创作阶段</Field.Label>
              <NativeSelect.Root>
                <NativeSelect.Field
                  value={config.category}
                  onChange={(e) => handleConfigChange({ category: e.target.value as any })}
                >
                  <option value="structure">结构规划</option>
                  <option value="character">角色创建</option>
                  <option value="world">世界构建</option>
                  <option value="scene">场景设计</option>
                  <option value="dialogue">对话创作</option>
                </NativeSelect.Field>
              </NativeSelect.Root>
            </Field.Root>

            <Field.Root>
              <Field.Label>难度等级</Field.Label>
              <NativeSelect.Root>
                <NativeSelect.Field
                  value={config.difficulty}
                  onChange={(e) => handleConfigChange({ difficulty: e.target.value as any })}
                >
                  <option value="beginner">新手</option>
                  <option value="intermediate">中级</option>
                  <option value="advanced">高级</option>
                </NativeSelect.Field>
              </NativeSelect.Root>
            </Field.Root>

            <Field.Root>
              <Field.Label>AI模型</Field.Label>
              <NativeSelect.Root>
                <NativeSelect.Field
                  value={config.aiModel}
                  onChange={(e) => handleConfigChange({ aiModel: e.target.value as any })}
                >
                  <option value="claude">Claude</option>
                  <option value="gpt">ChatGPT</option>
                  <option value="gemini">Gemini</option>
                  <option value="generic">通用</option>
                </NativeSelect.Field>
              </NativeSelect.Root>
            </Field.Root>

            <Field.Root>
              <Field.Label>写作风格</Field.Label>
              <NativeSelect.Root>
                <NativeSelect.Field
                  value={config.writingStyle}
                  onChange={(e) => handleConfigChange({ writingStyle: e.target.value as any })}
                >
                  <option value="narrative">叙事性</option>
                  <option value="analytical">分析性</option>
                  <option value="creative">创意性</option>
                  <option value="technical">技术性</option>
                </NativeSelect.Field>
              </NativeSelect.Root>
            </Field.Root>

            <Field.Root>
              <Field.Label>详细程度</Field.Label>
              <NativeSelect.Root>
                <NativeSelect.Field
                  value={config.detailLevel}
                  onChange={(e) => handleConfigChange({ detailLevel: e.target.value as any })}
                >
                  <option value="brief">简洁</option>
                  <option value="moderate">适中</option>
                  <option value="detailed">详细</option>
                  <option value="comprehensive">全面</option>
                </NativeSelect.Field>
              </NativeSelect.Root>
            </Field.Root>
          </SimpleGrid>
        </Box>
      </Card.Root>

      {/* 实时生成的模板预览 */}
      {generatedTemplate && (
        <Card.Root variant="elevated">
          <Box p={6}>
            <VStack gap={4} align="stretch">
              <HStack justify="space-between">
                <VStack align="start" gap={1}>
                  <Heading size="md">{generatedTemplate.title}</Heading>
                  <Text color="gray.600">{generatedTemplate.description}</Text>
                </VStack>
                <Badge colorPalette="blue">
                  {generatedTemplate.variables.length} 个变量
                </Badge>
              </HStack>

              <Text fontSize="sm" color="gray.500">
                📊 预估Token数: {generatedTemplate.metadata.estimatedTokens} |
                ⏱️ 预估时间: {generatedTemplate.metadata.estimatedTime}
              </Text>

              <Button
                onClick={() => proceedWithTemplate(generatedTemplate)}
                colorPalette="blue"
                size="lg"
              >
                使用此模板 →
              </Button>
            </VStack>
          </Box>
        </Card.Root>
      )}
    </VStack>
  );
};
```

#### 2. 角色创建Prompt模板
```
标题：深度角色塑造助手
变量：
- 角色类型：{{characterType}}
- 故事背景：{{storyContext}}
- 角色功能：{{characterRole}}
- 现有角色：{{existingCharacters}}

Prompt内容：
作为一名专业的角色设计师，请帮我创建一个{{characterType}}角色。

背景信息：
- 故事背景：{{storyContext}}
- 角色在故事中的功能：{{characterRole}}
- 已有角色：{{existingCharacters}}

请为这个角色设计：
1. 基本信息（姓名、年龄、职业、社会地位）
2. 外貌特征（突出个性的外貌描述）
3. 性格特质（3-5个核心特质，包含正面和负面）
4. 价值观体系（最重要的2-3个价值观）
5. 恐惧与欲望（内在驱动力）
6. 背景故事（关键的成长经历）
7. 语言风格（说话特点和口头禅）
8. 与其他角色的关系设定

请确保角色具有复杂性和真实感，避免过于完美或单一。
```

#### 3. 世界构建Prompt模板
```
标题：世界设定构建助手
变量：
- 世界类型：{{worldType}}
- 时代背景：{{timeSettings}}
- 角色需求：{{characterNeeds}}
- 故事需求：{{storyNeeds}}

Prompt内容：
作为一名专业的世界构建师，请帮我设计一个{{worldType}}类型的故事世界。

基础设定：
- 世界类型：{{worldType}}
- 时代背景：{{timeSettings}}
- 需要配合的角色：{{characterNeeds}}
- 故事情节需求：{{storyNeeds}}

请详细设计：
1. 地理环境（地形、气候、重要地点）
2. 社会制度（政治体系、社会阶层、法律制度）
3. 文化背景（宗教信仰、价值观念、传统习俗）
4. 经济体系（货币制度、贸易方式、资源分布）
5. 科技/魔法水平（能力体系、限制规则）
6. 历史背景（重要历史事件、文明发展）
7. 语言文字（命名规则、方言特色）
8. 日常生活（饮食、居住、娱乐方式）

请确保世界设定的内在逻辑一致，并能很好地支撑故事情节的发展。
```

#### 4. 场景设计Prompt模板
```
标题：沉浸式场景创作助手
变量：
- 场景功能：{{sceneFunction}}
- 情绪氛围：{{mood}}
- 参与角色：{{characters}}
- 世界设定：{{worldContext}}

Prompt内容：
作为一名专业的场景设计师，请帮我创作一个{{sceneFunction}}功能的场景。

场景要求：
- 场景功能：{{sceneFunction}}
- 目标情绪氛围：{{mood}}
- 参与的角色：{{characters}}
- 世界设定背景：{{worldContext}}

请设计包含：
1. 环境描述（地点、时间、天气、光线）
2. 感官细节（视觉、听觉、嗅觉、触觉、味觉）
3. 氛围营造（情绪基调、紧张程度、节奏感）
4. 角色状态（情绪状态、行为表现、互动方式）
5. 环境互动（角色与环境的互动关系）
6. 象征元素（环境中的象征意义）
7. 转场设计（如何自然地进入和离开场景）
8. 读者感受（预期的读者情感反应）

请确保场景描述生动具体，能够有效推动情节发展并深化角色刻画。
```

#### 5. 对话创作Prompt模板
```
标题：角色对话生成助手
变量：
- 对话角色：{{speakers}}
- 场景情境：{{sceneContext}}
- 对话目的：{{dialoguePurpose}}
- 情感基调：{{emotionalTone}}

Prompt内容：
作为一名专业的对话写作专家，请为以下角色创作对话。

对话设定：
- 参与对话的角色：{{speakers}}
- 场景情境：{{sceneContext}}
- 对话的主要目的：{{dialoguePurpose}}
- 情感基调：{{emotionalTone}}

请创作包含：
1. 符合角色性格的对话内容
2. 自然的语言节奏和停顿
3. 潜台词和言外之意
4. 情感变化的层次
5. 冲突或张力的体现
6. 信息传递的巧妙处理
7. 动作和表情的穿插描述
8. 对话的起承转合

请确保：
- 每个角色的语言风格保持一致
- 对话推动情节发展
- 包含适当的情感冲突
- 避免单纯的信息堆砌
```

### 新手作家工作流（基于Prompt系统）
1. **结构规划** → 生成故事结构Prompt → 复制到AI工具 → 获得结构框架
2. **角色创建** → 生成角色塑造Prompt → 复制到AI工具 → 获得角色档案
3. **世界构建** → 生成世界设定Prompt → 复制到AI工具 → 获得世界背景
4. **场景设计** → 生成场景创作Prompt → 复制到AI工具 → 获得场景描述
5. **对话创作** → 生成对话写作Prompt → 复制到AI工具 → 获得对话内容

### 经验作家工作流
1. **快速搭建** → 使用类型化助手快速建立框架
2. **深度优化** → 使用专业工具精细化调整
3. **文化校验** → 使用跨文化顾问确保适宜性
4. **多平台优化** → 使用数字优化器适配不同平台

### AI协作创作工作流
1. **AI生成初稿** → 使用各类生成器产出基础内容
2. **人工精修** → 使用分析器和优化器精细调整
3. **质量把控** → 使用评估中心确保质量标准
4. **持续迭代** → 基于反馈持续优化改进

---

## 📊 **技术实现优先级**

### Phase 1 - 核心工具 (0-3个月)
- 叙事结构构建工具
- 增强角色创作套件
- 智能世界构建平台
- 多维场景创作工具

### Phase 2 - 专业工具 (3-6个月)
- 对话创作增强器
- 文学技法应用器
- 类型化创作助手
- 情节冲突编织器

### Phase 3 - 高级功能 (6-12个月)
- 创作流程管理器
- 跨文化内容顾问
- 数字创作优化器
- 综合质量评估中心

---

## 🔧 **Prompt管理系统实现**

### 一键复制功能设计
```typescript
interface PromptCopyComponent {
  // 复制按钮组件
  render: () => JSX.Element;

  // 复制功能实现
  handleCopy: (promptData: GeneratedPrompt) => Promise<void>;

  // 复制状态管理
  copyStatus: 'idle' | 'copying' | 'success' | 'error';

  // 复制格式选项
  copyFormats: {
    plain: string;      // 纯文本格式
    markdown: string;   // Markdown格式
    structured: string; // 结构化格式
  };
}

// 生成的Prompt数据结构
interface GeneratedPrompt {
  id: string;
  template: PromptSystem;
  variables: Record<string, any>;
  generatedContent: string;
  metadata: {
    generatedAt: Date;
    estimatedTokens: number;
    aiModel: string;
  };
}
```

### Prompt管理界面
```tsx
// Prompt生成和管理组件
const PromptManagerComponent: React.FC = () => {
  const [selectedTemplate, setSelectedTemplate] = useState<PromptSystem | null>(null);
  const [variables, setVariables] = useState<Record<string, any>>({});
  const [generatedPrompt, setGeneratedPrompt] = useState<string>('');
  const [copyStatus, setCopyStatus] = useState<'idle' | 'copying' | 'success' | 'error'>('idle');

  return (
    <Card.Root>
      <Box p={6}>
        {/* 模板选择区域 */}
        <VStack gap={4} align="stretch">
          <Heading size="md">Prompt模板库</Heading>

          {/* 分类标签 */}
          <HStack gap={2}>
            {['structure', 'character', 'world', 'scene', 'dialogue'].map(category => (
              <Button key={category} variant="outline" size="sm">
                {getCategoryLabel(category)}
              </Button>
            ))}
          </HStack>

          {/* 模板列表 */}
          <SimpleGrid columns={{base: 1, md: 2, lg: 3}} gap={4}>
            {templates.map(template => (
              <Card.Root
                key={template.id}
                variant="outline"
                cursor="pointer"
                onClick={() => setSelectedTemplate(template)}
              >
                <Box p={4}>
                  <VStack align="start" gap={2}>
                    <HStack justify="space-between" w="full">
                      <Badge colorPalette="blue">{template.category}</Badge>
                      <Text fontSize="xs" color="gray.500">
                        {template.metadata.estimatedTokens} tokens
                      </Text>
                    </HStack>
                    <Text fontWeight="medium">{template.title}</Text>
                    <Text fontSize="sm" color="gray.600" noOfLines={2}>
                      {template.description}
                    </Text>
                  </VStack>
                </Box>
              </Card.Root>
            ))}
          </SimpleGrid>
        </VStack>

        {/* 变量填写区域 */}
        {selectedTemplate && (
          <VStack gap={4} align="stretch" mt={6}>
            <Separator />
            <Heading size="md">填写变量</Heading>

            <SimpleGrid columns={{base: 1, md: 2}} gap={4}>
              {selectedTemplate.variables.map(variable => (
                <Field.Root key={variable.name}>
                  <Field.Label>
                    {variable.label}
                    {variable.required && <Text color="red.500">*</Text>}
                  </Field.Label>

                  {variable.type === 'text' && (
                    <Input
                      value={variables[variable.name] || ''}
                      onChange={(e) => setVariables(prev => ({
                        ...prev,
                        [variable.name]: e.target.value
                      }))}
                      placeholder={variable.placeholder}
                    />
                  )}

                  {variable.type === 'multiline' && (
                    <Textarea
                      value={variables[variable.name] || ''}
                      onChange={(e) => setVariables(prev => ({
                        ...prev,
                        [variable.name]: e.target.value
                      }))}
                      placeholder={variable.placeholder}
                      rows={3}
                    />
                  )}

                  {variable.type === 'select' && (
                    <NativeSelect.Root>
                      <NativeSelect.Field
                        value={variables[variable.name] || ''}
                        onChange={(e) => setVariables(prev => ({
                          ...prev,
                          [variable.name]: e.target.value
                        }))}
                      >
                        <option value="">请选择</option>
                        {variable.options?.map(option => (
                          <option key={option} value={option}>{option}</option>
                        ))}
                      </NativeSelect.Field>
                    </NativeSelect.Root>
                  )}
                </Field.Root>
              ))}
            </SimpleGrid>

            {/* 生成按钮 */}
            <Button
              onClick={handleGeneratePrompt}
              colorPalette="blue"
              size="lg"
              disabled={!isVariablesValid()}
            >
              🎯 生成Prompt
            </Button>
          </VStack>
        )}

        {/* Prompt预览和复制区域 */}
        {generatedPrompt && (
          <VStack gap={4} align="stretch" mt={6}>
            <Separator />
            <HStack justify="space-between">
              <Heading size="md">生成的Prompt</Heading>
              <HStack gap={2}>
                <Button
                  onClick={() => handleCopy('plain')}
                  variant="outline"
                  size="sm"
                  colorPalette={copyStatus === 'success' ? 'green' : 'blue'}
                >
                  {copyStatus === 'copying' ? '复制中...' :
                   copyStatus === 'success' ? '✓ 已复制' : '📋 复制纯文本'}
                </Button>
                <Button
                  onClick={() => handleCopy('markdown')}
                  variant="outline"
                  size="sm"
                >
                  📝 复制Markdown
                </Button>
                <Button
                  onClick={() => handleExport()}
                  variant="outline"
                  size="sm"
                >
                  📤 导出
                </Button>
              </HStack>
            </HStack>

            <Card.Root variant="outline">
              <Box p={4}>
                <Text
                  fontSize="sm"
                  fontFamily="mono"
                  whiteSpace="pre-wrap"
                  bg="gray.50"
                  p={4}
                  borderRadius="md"
                  maxH="400px"
                  overflow="auto"
                >
                  {generatedPrompt}
                </Text>
              </Box>
            </Card.Root>

            {/* 快速操作 */}
            <HStack gap={4} justify="center">
              <Button
                onClick={() => openInNewWindow(generatedPrompt)}
                variant="outline"
                leftIcon="🚀"
              >
                在新窗口打开
              </Button>
              <Button
                onClick={() => saveToHistory(generatedPrompt)}
                variant="outline"
                leftIcon="💾"
              >
                保存到历史
              </Button>
              <Button
                onClick={() => sharePrompt(generatedPrompt)}
                variant="outline"
                leftIcon="🔗"
              >
                分享链接
              </Button>
            </HStack>
          </VStack>
        )}
      </Box>
    </Card.Root>
  );
};
```

### 复制功能核心实现
```typescript
class PromptCopyService {
  // 复制到剪贴板
  async copyToClipboard(content: string, format: 'plain' | 'markdown' | 'structured'): Promise<boolean> {
    try {
      let formattedContent = content;

      switch (format) {
        case 'markdown':
          formattedContent = this.formatAsMarkdown(content);
          break;
        case 'structured':
          formattedContent = this.formatAsStructured(content);
          break;
        default:
          formattedContent = content;
      }

      await navigator.clipboard.writeText(formattedContent);

      // 显示复制成功提示
      this.showToast('Prompt已复制到剪贴板', 'success');

      // 记录使用统计
      this.trackUsage('copy', format);

      return true;
    } catch (error) {
      console.error('复制失败:', error);
      this.showToast('复制失败，请手动选择文本', 'error');
      return false;
    }
  }

  // 格式化为Markdown
  private formatAsMarkdown(content: string): string {
    return `# AI创作Prompt\n\n\`\`\`\n${content}\n\`\`\`\n\n---\n*由Novellus创作工具生成*`;
  }

  // 格式化为结构化格式
  private formatAsStructured(content: string): string {
    const timestamp = new Date().toLocaleString();
    return `/**
 * Novellus AI创作Prompt
 * 生成时间: ${timestamp}
 * 工具版本: v1.0
 */

${content}

/* 使用说明:
 * 1. 将此Prompt复制到AI工具中
 * 2. 根据需要调整具体参数
 * 3. 获得AI生成的创作内容
 */`;
  }

  // 导出功能
  exportPrompt(prompt: GeneratedPrompt, format: 'txt' | 'md' | 'json'): void {
    let content: string;
    let filename: string;
    let mimeType: string;

    switch (format) {
      case 'md':
        content = this.formatAsMarkdown(prompt.generatedContent);
        filename = `prompt_${prompt.template.category}_${Date.now()}.md`;
        mimeType = 'text/markdown';
        break;
      case 'json':
        content = JSON.stringify(prompt, null, 2);
        filename = `prompt_${prompt.template.category}_${Date.now()}.json`;
        mimeType = 'application/json';
        break;
      default:
        content = prompt.generatedContent;
        filename = `prompt_${prompt.template.category}_${Date.now()}.txt`;
        mimeType = 'text/plain';
    }

    this.downloadFile(content, filename, mimeType);
  }

  // 下载文件
  private downloadFile(content: string, filename: string, mimeType: string): void {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }
}
```

### Prompt历史管理
```typescript
interface PromptHistory {
  id: string;
  template: PromptSystem;
  variables: Record<string, any>;
  generatedContent: string;
  createdAt: Date;
  usageCount: number;
  rating?: number;
  tags: string[];
}

class PromptHistoryService {
  private readonly storageKey = 'novellus-prompt-history';

  // 保存到历史
  async saveToHistory(prompt: GeneratedPrompt): Promise<void> {
    const history = await this.getHistory();
    const historyItem: PromptHistory = {
      id: `history_${Date.now()}`,
      template: prompt.template,
      variables: prompt.variables,
      generatedContent: prompt.generatedContent,
      createdAt: new Date(),
      usageCount: 1,
      tags: []
    };

    history.unshift(historyItem);

    // 保持历史记录数量限制
    if (history.length > 100) {
      history.splice(100);
    }

    await this.setHistory(history);
  }

  // 获取历史记录
  async getHistory(): Promise<PromptHistory[]> {
    try {
      const stored = localStorage.getItem(this.storageKey);
      if (!stored) return [];
      return JSON.parse(stored).map((item: any) => ({
        ...item,
        createdAt: new Date(item.createdAt)
      }));
    } catch (error) {
      console.error('读取历史记录失败:', error);
      return [];
    }
  }

  // 搜索历史记录
  async searchHistory(query: string, category?: string): Promise<PromptHistory[]> {
    const history = await this.getHistory();
    return history.filter(item => {
      const matchesQuery = !query ||
        item.template.title.toLowerCase().includes(query.toLowerCase()) ||
        item.generatedContent.toLowerCase().includes(query.toLowerCase());

      const matchesCategory = !category || item.template.category === category;

      return matchesQuery && matchesCategory;
    });
  }
}
```

## 💡 **创新特色**

### 1. **Prompt原生设计**
- 所有创作阶段都输出专业Prompt
- 一键复制到各种AI工具
- 支持多种格式和平台适配

### 2. **智能变量系统**
- 动态变量注入和验证
- 前置阶段数据自动填充
- 智能推荐和错误检查

### 3. **全格式支持**
- 纯文本、Markdown、结构化格式
- 适配ChatGPT、Claude、Gemini等
- 支持API调用和批量处理

### 4. **历史管理**
- 完整的Prompt使用历史
- 搜索、分类、评分功能
- 复用和优化建议

---

*文档版本: v1.0*
*创建时间: 2025-09-16*
*最后更新: 2025-09-16*