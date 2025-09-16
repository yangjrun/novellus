// 动态Prompt模板生成系统的核心类型定义

export interface PromptConfig {
  // 基础配置
  category: 'structure' | 'character' | 'world' | 'scene' | 'dialogue' | 'assessment';
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

export interface ProjectContext {
  id: string;
  name: string;
  genre: string;
  theme?: string;
  targetAudience?: string;
  culturalBackground?: string;
}

export interface PromptTemplate {
  id: string;
  title: string;
  description: string;
  category: string;
  variables: DynamicVariable[];
  promptStructure: PromptStructure;
  metadata: TemplateMetadata;
  createdAt: Date;
  version: string;
}

export interface DynamicVariable {
  name: string;
  type: 'text' | 'select' | 'multiselect' | 'textarea' | 'number' | 'boolean' | 'slider';
  label: string;
  description?: string;
  required: boolean;
  defaultValue?: any;
  options?: VariableOption[];
  validation?: ValidationRule[];
  dependencies?: VariableDependency[];
  placeholder?: string;
  min?: number;
  max?: number;
  step?: number;
}

export interface VariableOption {
  value: string;
  label: string;
  description?: string;
  enablesVariables?: string[];
  disablesVariables?: string[];
  modifiesPrompt?: PromptModification[];
}

export interface VariableDependency {
  variable: string;
  condition: 'equals' | 'not_equals' | 'contains' | 'not_contains' | 'greater_than' | 'less_than';
  value: any;
  action: 'show' | 'hide' | 'enable' | 'disable' | 'require' | 'optional';
}

export interface ValidationRule {
  type: 'required' | 'min_length' | 'max_length' | 'pattern' | 'custom';
  value?: any;
  message: string;
  validator?: (value: any) => boolean;
}

export interface PromptStructure {
  sections: PromptSection[];
  conditionalSections?: ConditionalSection[];
  dynamicInstructions?: DynamicInstruction[];
}

export interface PromptSection {
  name: string;
  order: number;
  content: string;
  required: boolean;
  conditions?: ConditionRule[];
}

export interface ConditionalSection {
  condition: ConditionRule;
  section: PromptSection;
}

export interface DynamicInstruction {
  condition: ConditionRule;
  instruction: string;
  position?: 'before' | 'after' | 'replace';
  targetSection?: string;
}

export interface ConditionRule {
  variable?: string;
  difficulty?: string;
  aiModel?: string;
  equals?: any;
  not_equals?: any;
  contains?: any;
  operator?: 'and' | 'or';
  conditions?: ConditionRule[];
}

export interface PromptModification {
  type: 'add_section' | 'remove_section' | 'modify_section' | 'add_instruction';
  target?: string;
  content?: string;
  position?: number;
}

export interface TemplateMetadata {
  estimatedTokens: number;
  estimatedTime: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  tags: string[];
  compatibility: {
    aiModels: string[];
    languages: string[];
  };
  usage: PromptUsage;
  rating?: number;
  feedback?: string[];
}

export interface PromptUsage {
  count: number;
  lastUsed: Date;
  successRate?: number;
  averageRating?: number;
}

export interface GeneratedPrompt {
  id: string;
  template: PromptTemplate;
  variables: Record<string, any>;
  generatedContent: string;
  metadata: {
    generatedAt: Date;
    estimatedTokens: number;
    aiModel: string;
    userConfig: PromptConfig;
  };
}

export interface PromptHistory {
  id: string;
  template: PromptTemplate;
  variables: Record<string, any>;
  generatedContent: string;
  createdAt: Date;
  usageCount: number;
  rating?: number;
  tags: string[];
  projectId?: string;
}

// Prompt模板生成器接口
export interface IPromptTemplateGenerator {
  generateTemplate(config: PromptConfig): PromptTemplate;
  validateConfig(config: PromptConfig): ValidationResult;
  getDefaultConfig(): PromptConfig;
  getSupportedCategories(): string[];
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export interface ValidationWarning {
  field: string;
  message: string;
  suggestion?: string;
}

// Prompt复制和管理服务接口
export interface IPromptCopyService {
  copyToClipboard(content: string, format: 'plain' | 'markdown' | 'structured'): Promise<boolean>;
  generatePrompt(template: PromptTemplate, variables: Record<string, any>): string;
  exportPrompt(prompt: GeneratedPrompt, format: 'txt' | 'md' | 'json'): void;
  sharePrompt(promptId: string): Promise<string>;
  formatAsMarkdown(content: string): string;
  formatAsStructured(content: string): string;
}

export interface IPromptHistoryService {
  saveToHistory(prompt: GeneratedPrompt): Promise<void>;
  getHistory(): Promise<PromptHistory[]>;
  searchHistory(query: string, category?: string): Promise<PromptHistory[]>;
  deleteFromHistory(id: string): Promise<void>;
  ratePrompt(id: string, rating: number): Promise<void>;
  addTags(id: string, tags: string[]): Promise<void>;
}

// 事件类型
export interface PromptGenerationEvent {
  type: 'template_generated' | 'prompt_generated' | 'prompt_copied' | 'prompt_exported';
  data: any;
  timestamp: Date;
}

export type PromptEventHandler = (event: PromptGenerationEvent) => void;