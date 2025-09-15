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

// 导出类型
export type ExportFormat = 'json' | 'pdf' | 'docx' | 'csv';

export interface ExportOptions {
  format: ExportFormat;
  includeNotes?: boolean;
  includeMetadata?: boolean;
  template?: string;
}