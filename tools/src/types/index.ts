// 基础类型定义
export interface Character {
  id: string;
  projectId: string;
  createdAt: Date;
  updatedAt: Date;

  // 基本信息
  basicInfo: {
    name: string;
    alias?: string[];
    age: number | string;
    gender: string;
    occupation: string;
    socialStatus: string;
  };

  // 外貌特征
  appearance: {
    height: string;
    weight: string;
    hairColor: string;
    eyeColor: string;
    skinTone: string;
    bodyType: string;
    specialMarks: string[];
    clothingStyle: string;
  };

  // 性格特质
  personality: {
    coreTraits: string[];
    values: string[];
    beliefs: string[];
    fears: string[];
    desires: string[];
    weaknesses: string[];
    strengths: string[];
  };

  // 背景故事
  background: {
    birthplace: string;
    family: string;
    childhood: string;
    education: string;
    importantEvents: string[];
    trauma: string[];
    achievements: string[];
  };

  // 能力技能
  abilities: {
    professionalSkills: string[];
    specialTalents: string[];
    languages: string[];
    learningAbility: string;
    socialSkills: string;
    practicalSkills: string[];
  };

  // 人际关系
  relationships: {
    family: Relationship[];
    friends: Relationship[];
    lovers: Relationship[];
    enemies: Relationship[];
    mentors: Relationship[];
    subordinates: Relationship[];
    socialCircle: string[];
  };

  // 生活状况
  lifestyle: {
    residence: string;
    economicStatus: string;
    dailyRoutine: string;
    hobbies: string[];
    foodPreferences: string[];
    entertainment: string[];
  };

  // 心理状态
  psychology: {
    mentalHealth: string;
    copingMechanisms: string[];
    emotionalPatterns: string[];
    trauma: string[];
    growthNeeds: string[];
  };

  // 故事功能
  storyRole: {
    characterType: 'protagonist' | 'antagonist' | 'supporting' | 'minor';
    characterArc: string;
    conflictRole: string;
    symbolism: string;
    readerConnection: string;
  };

  // 特殊设定
  specialSettings: {
    worldBuilding: string;
    culturalBackground: string;
    historicalContext: string;
    technologyLevel: string;
    magicAbilities?: string;
  };
}

export interface Relationship {
  characterId?: string;
  name: string;
  relationship: string;
  description: string;
  importance: 'high' | 'medium' | 'low';
}

// 面试工具类型
export interface InterviewQuestion {
  id: string;
  category: string;
  question: string;
  type: 'text' | 'choice' | 'scale';
  choices?: string[];
  followUp?: string[];
}

export interface InterviewSession {
  id: string;
  characterId: string;
  interviewType: string;
  questions: InterviewQuestion[];
  answers: InterviewAnswer[];
  startTime: Date;
  endTime?: Date;
  status: 'in_progress' | 'completed' | 'paused';
}

export interface InterviewAnswer {
  questionId: string;
  answer: string;
  timestamp: Date;
  notes?: string;
}

// 检查清单类型
export interface ChecklistItem {
  id: string;
  category: string;
  subcategory?: string;
  title: string;
  description: string;
  checked: boolean;
  priority: 'high' | 'medium' | 'low';
  notes?: string;
}

export interface ChecklistTemplate {
  id: string;
  name: string;
  description: string;
  categories: ChecklistCategory[];
}

export interface ChecklistCategory {
  id: string;
  name: string;
  description: string;
  items: ChecklistItem[];
}

export interface ProjectChecklist extends ChecklistTemplate {
  projectId: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface ChecklistProgress {
  total: number;
  completed: number;
  percentage: number;
}

// 诊断工具类型
export interface DiagnosticTest {
  id: string;
  name: string;
  description: string;
  category: string;
  timeEstimate: number; // 分钟
  execute: (input: any) => DiagnosticResult;
}

export interface DiagnosticResult {
  testId: string;
  score: number; // 0-100
  status: 'excellent' | 'good' | 'warning' | 'critical';
  issues: DiagnosticIssue[];
  suggestions: string[];
  timestamp: Date;
}

export interface DiagnosticIssue {
  type: 'error' | 'warning' | 'info';
  message: string;
  location?: string;
  severity: 'high' | 'medium' | 'low';
}

// 项目类型
export interface Project {
  id: string;
  name: string;
  description: string;
  genre: string;
  createdAt: Date;
  updatedAt: Date;
}

// === Phase 1 新增功能类型定义 ===

// 叙事结构工具类型
export interface NarrativeStructure {
  id: string;
  projectId: string;
  name: string;
  type: 'three-act' | 'heros-journey' | 'kishotenketsu' | 'seven-point' | 'freytag' | 'custom';
  culturalTradition: 'western' | 'eastern' | 'african' | 'arabic' | 'indigenous' | 'mixed';
  description: string;
  plotPoints: PlotPoint[];
  timelineEvents: TimelineEvent[];
  createdAt: Date;
  updatedAt: Date;
}

export interface PlotPoint {
  id: string;
  name: string;
  description: string;
  position: number; // 0-100 percentage of story
  type: 'inciting-incident' | 'plot-point-1' | 'midpoint' | 'plot-point-2' | 'climax' | 'resolution' | 'custom';
  completed: boolean;
  notes: string;
  relatedCharacters: string[];
  relatedScenes: string[];
}

export interface TimelineEvent {
  id: string;
  title: string;
  description: string;
  timestamp: number; // story timestamp
  chapter?: number;
  scene?: number;
  importance: 'critical' | 'major' | 'minor';
  tags: string[];
}

// 世界构建工具类型
export interface WorldBuilding {
  id: string;
  projectId: string;
  name: string;
  type: 'fantasy' | 'scifi' | 'realistic' | 'historical' | 'alternate-history' | 'mixed';
  settings: WorldSettings;
  cultures: Culture[];
  locations: Location[];
  history: HistoricalEvent[];
  systems: WorldSystem[];
  createdAt: Date;
  updatedAt: Date;
}

export interface WorldSettings {
  physics: {
    naturalLaws: string[];
    magicSystem?: MagicSystem;
    technology: TechnologyLevel;
    timeFlow: string;
  };
  geography: {
    continents: Continent[];
    climate: string;
    naturalResources: string[];
    environmentalChallenges: string[];
  };
  society: {
    governmentSystems: GovernmentSystem[];
    economicSystems: EconomicSystem[];
    socialStructures: SocialStructure[];
    conflictSources: string[];
  };
}

export interface Culture {
  id: string;
  name: string;
  description: string;
  values: string[];
  beliefs: string[];
  traditions: string[];
  language: LanguageInfo;
  artForms: string[];
  socialNorms: string[];
  conflicts: string[];
  influences: string[];
}

export interface Location {
  id: string;
  name: string;
  type: 'city' | 'town' | 'village' | 'landmark' | 'region' | 'building' | 'natural';
  description: string;
  geography: string;
  climate: string;
  population?: number;
  culture: string;
  economy: string;
  significance: string;
  connectedLocations: string[];
  scenes: string[];
}

export interface MagicSystem {
  name: string;
  type: 'hard' | 'soft' | 'hybrid';
  source: string;
  rules: string[];
  limitations: string[];
  practitioners: string[];
  socialImpact: string;
}

export interface TechnologyLevel {
  era: string;
  keyTechnologies: string[];
  limitations: string[];
  socialImpact: string[];
  progressionRate: string;
}

// 场景创作工具类型
export interface Scene {
  id: string;
  projectId: string;
  title: string;
  description: string;
  locationId: string;
  timeOfDay: string;
  weather: string;
  atmosphere: SceneAtmosphere;
  sensoryDetails: SensoryDetails;
  characters: SceneCharacter[];
  purpose: ScenePurpose;
  pacing: 'fast' | 'medium' | 'slow';
  emotionalTone: string[];
  conflict: string;
  outcome: string;
  notes: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface SceneAtmosphere {
  mood: string;
  tension: number; // 1-10
  energy: number; // 1-10
  intimacy: number; // 1-10
  danger: number; // 1-10
  mystery: number; // 1-10
}

export interface SensoryDetails {
  visual: string[];
  auditory: string[];
  olfactory: string[];
  tactile: string[];
  gustatory: string[];
  emotional: string[];
}

export interface SceneCharacter {
  characterId: string;
  role: 'protagonist' | 'antagonist' | 'supporting' | 'background';
  emotionalState: string;
  motivation: string;
  goals: string[];
  obstacles: string[];
}

export interface ScenePurpose {
  storyFunction: 'setup' | 'conflict' | 'development' | 'climax' | 'resolution' | 'transition';
  characterDevelopment: string[];
  plotAdvancement: string;
  worldBuilding: string;
  themeExploration: string;
}

// AI集成类型
export interface AIPrompt {
  id: string;
  name: string;
  description: string;
  category: 'character' | 'world' | 'plot' | 'scene' | 'dialogue' | 'general';
  template: string;
  parameters: AIParameter[];
  examples: AIExample[];
}

export interface AIParameter {
  name: string;
  type: 'text' | 'number' | 'boolean' | 'select' | 'multiselect';
  description: string;
  required: boolean;
  defaultValue?: any;
  options?: string[];
}

export interface AIExample {
  input: Record<string, any>;
  output: string;
  explanation: string;
}

export interface AIResponse {
  id: string;
  promptId: string;
  input: Record<string, any>;
  output: string;
  confidence: number; // 0-100
  suggestions: string[];
  timestamp: Date;
}

// 通用辅助类型
export interface GovernmentSystem {
  type: string;
  description: string;
  powerStructure: string;
  laws: string[];
}

export interface EconomicSystem {
  type: string;
  currency: string;
  tradeRoutes: string[];
  keyIndustries: string[];
  classStructure: string[];
}

export interface SocialStructure {
  type: string;
  hierarchy: string[];
  mobility: string;
  traditions: string[];
}

export interface Continent {
  name: string;
  size: string;
  climate: string[];
  features: string[];
  cultures: string[];
}

export interface HistoricalEvent {
  id: string;
  name: string;
  date: string;
  description: string;
  participants: string[];
  consequences: string[];
  significance: string;
}

export interface WorldSystem {
  type: 'political' | 'economic' | 'religious' | 'educational' | 'military' | 'magical' | 'technological';
  name: string;
  description: string;
  rules: string[];
  participants: string[];
  conflicts: string[];
}

export interface LanguageInfo {
  name: string;
  family: string;
  writingSystem: string;
  characteristics: string[];
  speakers: number;
}

// 导出类型
export type ExportFormat = 'json' | 'pdf' | 'docx' | 'csv';

export interface ExportOptions {
  format: ExportFormat;
  includeNotes?: boolean;
  includeMetadata?: boolean;
  template?: string;
}