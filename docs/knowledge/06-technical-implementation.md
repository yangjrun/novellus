# 基础创作工具技术实现方案

## 总体架构

### 技术栈选择
- **前端**: React/Vue.js + TypeScript
- **后端**: Node.js/Python FastAPI
- **数据库**: MongoDB/PostgreSQL
- **文件存储**: 本地文件系统/云存储
- **导出功能**: PDF.js/jsPDF, Excel.js

### 系统架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端界面      │    │   API网关       │    │   核心服务      │
│   React/Vue     │◄──►│   Express/Koa   │◄──►│   业务逻辑      │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   本地存储      │    │   用户认证      │    │   数据库        │
│   LocalStorage  │    │   JWT/Session   │    │   MongoDB/PG    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 1. 角色工作表实现

### 数据模型
```typescript
interface Character {
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

interface Relationship {
  characterId?: string;
  name: string;
  relationship: string;
  description: string;
  importance: 'high' | 'medium' | 'low';
}
```

### 核心功能实现

#### 1. 表单组件
```typescript
// CharacterForm.tsx
import React, { useState, useEffect } from 'react';

interface CharacterFormProps {
  character?: Character;
  onSave: (character: Character) => void;
  onCancel: () => void;
}

export const CharacterForm: React.FC<CharacterFormProps> = ({
  character,
  onSave,
  onCancel
}) => {
  const [formData, setFormData] = useState<Character>(
    character || getDefaultCharacter()
  );

  const [currentSection, setCurrentSection] = useState('basicInfo');

  const sections = [
    { key: 'basicInfo', label: '基本信息' },
    { key: 'appearance', label: '外貌特征' },
    { key: 'personality', label: '性格特质' },
    { key: 'background', label: '背景故事' },
    { key: 'abilities', label: '能力技能' },
    { key: 'relationships', label: '人际关系' },
    { key: 'lifestyle', label: '生活状况' },
    { key: 'psychology', label: '心理状态' },
    { key: 'storyRole', label: '故事功能' },
    { key: 'specialSettings', label: '特殊设定' }
  ];

  const handleSectionChange = (section: string) => {
    setCurrentSection(section);
  };

  const handleFieldChange = (section: string, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };

  const handleSave = () => {
    // 验证必填字段
    if (!formData.basicInfo.name) {
      alert('角色姓名不能为空');
      return;
    }

    onSave({
      ...formData,
      updatedAt: new Date()
    });
  };

  return (
    <div className="character-form">
      <div className="form-nav">
        {sections.map(section => (
          <button
            key={section.key}
            className={currentSection === section.key ? 'active' : ''}
            onClick={() => handleSectionChange(section.key)}
          >
            {section.label}
          </button>
        ))}
      </div>

      <div className="form-content">
        {currentSection === 'basicInfo' && (
          <BasicInfoForm
            data={formData.basicInfo}
            onChange={(field, value) => handleFieldChange('basicInfo', field, value)}
          />
        )}

        {currentSection === 'appearance' && (
          <AppearanceForm
            data={formData.appearance}
            onChange={(field, value) => handleFieldChange('appearance', field, value)}
          />
        )}

        {/* 其他表单组件... */}
      </div>

      <div className="form-actions">
        <button onClick={handleCancel}>取消</button>
        <button onClick={handleSave} className="primary">保存</button>
      </div>
    </div>
  );
};
```

#### 2. 数据持久化
```typescript
// characterService.ts
export class CharacterService {
  private storageKey = 'novellus_characters';

  async saveCharacter(character: Character): Promise<Character> {
    const characters = this.getAllCharacters();

    if (character.id) {
      // 更新现有角色
      const index = characters.findIndex(c => c.id === character.id);
      if (index !== -1) {
        characters[index] = character;
      }
    } else {
      // 创建新角色
      character.id = this.generateId();
      character.createdAt = new Date();
      characters.push(character);
    }

    this.saveToStorage(characters);
    return character;
  }

  getAllCharacters(): Character[] {
    const data = localStorage.getItem(this.storageKey);
    return data ? JSON.parse(data) : [];
  }

  getCharacterById(id: string): Character | null {
    const characters = this.getAllCharacters();
    return characters.find(c => c.id === id) || null;
  }

  deleteCharacter(id: string): boolean {
    const characters = this.getAllCharacters();
    const filteredCharacters = characters.filter(c => c.id !== id);
    this.saveToStorage(filteredCharacters);
    return true;
  }

  private saveToStorage(characters: Character[]): void {
    localStorage.setItem(this.storageKey, JSON.stringify(characters));
  }

  private generateId(): string {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  }

  // 导出功能
  exportCharacter(character: Character, format: 'json' | 'pdf' | 'docx'): void {
    switch (format) {
      case 'json':
        this.exportAsJSON(character);
        break;
      case 'pdf':
        this.exportAsPDF(character);
        break;
      case 'docx':
        this.exportAsDocx(character);
        break;
    }
  }

  private exportAsJSON(character: Character): void {
    const dataStr = JSON.stringify(character, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `${character.basicInfo.name}_character.json`;
    link.click();

    URL.revokeObjectURL(url);
  }

  private exportAsPDF(character: Character): void {
    // 使用 jsPDF 生成 PDF
    // 实现略...
  }
}
```

## 2. 角色面试工具实现

### 面试管理器
```typescript
// interviewManager.ts
interface InterviewQuestion {
  id: string;
  category: string;
  question: string;
  type: 'text' | 'choice' | 'scale';
  choices?: string[];
  followUp?: string[];
}

interface InterviewSession {
  id: string;
  characterId: string;
  interviewType: string;
  questions: InterviewQuestion[];
  answers: InterviewAnswer[];
  startTime: Date;
  endTime?: Date;
  status: 'in_progress' | 'completed' | 'paused';
}

interface InterviewAnswer {
  questionId: string;
  answer: string;
  timestamp: Date;
  notes?: string;
}

export class InterviewManager {
  private sessions: Map<string, InterviewSession> = new Map();

  startInterview(characterId: string, interviewType: string): InterviewSession {
    const questions = this.getQuestionsForType(interviewType);

    const session: InterviewSession = {
      id: this.generateSessionId(),
      characterId,
      interviewType,
      questions,
      answers: [],
      startTime: new Date(),
      status: 'in_progress'
    };

    this.sessions.set(session.id, session);
    return session;
  }

  answerQuestion(sessionId: string, questionId: string, answer: string): void {
    const session = this.sessions.get(sessionId);
    if (!session) return;

    const answerRecord: InterviewAnswer = {
      questionId,
      answer,
      timestamp: new Date()
    };

    session.answers.push(answerRecord);

    // 保存到本地存储
    this.saveSession(session);
  }

  getNextQuestion(sessionId: string): InterviewQuestion | null {
    const session = this.sessions.get(sessionId);
    if (!session) return null;

    const answeredQuestionIds = new Set(session.answers.map(a => a.questionId));
    return session.questions.find(q => !answeredQuestionIds.has(q.id)) || null;
  }

  completeInterview(sessionId: string): InterviewSession | null {
    const session = this.sessions.get(sessionId);
    if (!session) return null;

    session.status = 'completed';
    session.endTime = new Date();

    this.saveSession(session);
    return session;
  }

  private getQuestionsForType(type: string): InterviewQuestion[] {
    // 根据面试类型返回相应的问题集
    const questionSets = {
      'basic': [
        {
          id: 'basic_1',
          category: '基础认知',
          question: '请介绍一下你自己',
          type: 'text' as const
        },
        {
          id: 'basic_2',
          category: '基础认知',
          question: '你认为自己最大的优点是什么？',
          type: 'text' as const
        }
        // 更多问题...
      ],
      'values': [
        {
          id: 'values_1',
          category: '价值观探索',
          question: '什么对你来说最重要？',
          type: 'text' as const
        }
        // 更多问题...
      ]
      // 其他类型...
    };

    return questionSets[type] || [];
  }
}
```

### 面试界面组件
```typescript
// InterviewInterface.tsx
export const InterviewInterface: React.FC<{
  characterId: string;
  interviewType: string;
}> = ({ characterId, interviewType }) => {
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<InterviewQuestion | null>(null);
  const [answer, setAnswer] = useState('');
  const [progress, setProgress] = useState(0);

  const interviewManager = new InterviewManager();

  useEffect(() => {
    const newSession = interviewManager.startInterview(characterId, interviewType);
    setSession(newSession);
    setCurrentQuestion(interviewManager.getNextQuestion(newSession.id));
  }, [characterId, interviewType]);

  const handleAnswerSubmit = () => {
    if (!session || !currentQuestion || !answer.trim()) return;

    interviewManager.answerQuestion(session.id, currentQuestion.id, answer);

    const nextQuestion = interviewManager.getNextQuestion(session.id);
    if (nextQuestion) {
      setCurrentQuestion(nextQuestion);
      setAnswer('');
      updateProgress();
    } else {
      // 面试完成
      interviewManager.completeInterview(session.id);
      // 跳转到结果页面
    }
  };

  const updateProgress = () => {
    if (!session) return;
    const answered = session.answers.length;
    const total = session.questions.length;
    setProgress((answered / total) * 100);
  };

  return (
    <div className="interview-interface">
      <div className="interview-header">
        <h2>{interviewType}面试</h2>
        <div className="progress-bar">
          <div className="progress" style={{ width: `${progress}%` }}></div>
        </div>
      </div>

      {currentQuestion && (
        <div className="question-section">
          <div className="question-category">{currentQuestion.category}</div>
          <div className="question-text">{currentQuestion.question}</div>

          <div className="answer-section">
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="以角色的身份回答这个问题..."
              rows={6}
            />

            <div className="answer-actions">
              <button onClick={handleAnswerSubmit} disabled={!answer.trim()}>
                提交答案
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
```

## 3. 情节检查清单实现

### 检查清单数据结构
```typescript
// plotChecklist.ts
interface ChecklistItem {
  id: string;
  category: string;
  subcategory?: string;
  title: string;
  description: string;
  checked: boolean;
  priority: 'high' | 'medium' | 'low';
  notes?: string;
}

interface ChecklistTemplate {
  id: string;
  name: string;
  description: string;
  categories: ChecklistCategory[];
}

interface ChecklistCategory {
  id: string;
  name: string;
  description: string;
  items: ChecklistItem[];
}

export class PlotChecklistManager {
  private templates: ChecklistTemplate[] = [];

  constructor() {
    this.initializeDefaultTemplates();
  }

  private initializeDefaultTemplates(): void {
    this.templates = [
      {
        id: 'three_act_structure',
        name: '三幕结构检查',
        description: '检查故事是否遵循经典三幕结构',
        categories: [
          {
            id: 'act_one',
            name: '第一幕（建立）',
            description: '故事开始，建立世界观和角色',
            items: [
              {
                id: 'opening_hook',
                category: 'act_one',
                title: '开场吸引读者注意',
                description: '故事开头是否能立即抓住读者的兴趣',
                checked: false,
                priority: 'high'
              },
              {
                id: 'character_introduction',
                category: 'act_one',
                title: '介绍主要角色',
                description: '主要角色是否得到恰当介绍',
                checked: false,
                priority: 'high'
              }
              // 更多检查项...
            ]
          }
          // 其他分类...
        ]
      }
      // 其他模板...
    ];
  }

  getTemplate(templateId: string): ChecklistTemplate | null {
    return this.templates.find(t => t.id === templateId) || null;
  }

  createProjectChecklist(projectId: string, templateId: string): ProjectChecklist {
    const template = this.getTemplate(templateId);
    if (!template) throw new Error('Template not found');

    const checklist: ProjectChecklist = {
      id: this.generateId(),
      projectId,
      templateId,
      name: template.name,
      createdAt: new Date(),
      updatedAt: new Date(),
      categories: template.categories.map(category => ({
        ...category,
        items: category.items.map(item => ({ ...item }))
      }))
    };

    this.saveProjectChecklist(checklist);
    return checklist;
  }

  updateChecklistItem(
    checklistId: string,
    itemId: string,
    updates: Partial<ChecklistItem>
  ): void {
    const checklist = this.getProjectChecklist(checklistId);
    if (!checklist) return;

    for (const category of checklist.categories) {
      const item = category.items.find(i => i.id === itemId);
      if (item) {
        Object.assign(item, updates);
        checklist.updatedAt = new Date();
        this.saveProjectChecklist(checklist);
        break;
      }
    }
  }

  getChecklistProgress(checklistId: string): ChecklistProgress {
    const checklist = this.getProjectChecklist(checklistId);
    if (!checklist) return { total: 0, completed: 0, percentage: 0 };

    let total = 0;
    let completed = 0;

    for (const category of checklist.categories) {
      for (const item of category.items) {
        total++;
        if (item.checked) completed++;
      }
    }

    return {
      total,
      completed,
      percentage: total > 0 ? (completed / total) * 100 : 0
    };
  }
}

interface ProjectChecklist extends ChecklistTemplate {
  projectId: string;
  createdAt: Date;
  updatedAt: Date;
}

interface ChecklistProgress {
  total: number;
  completed: number;
  percentage: number;
}
```

### 检查清单界面
```typescript
// ChecklistInterface.tsx
export const ChecklistInterface: React.FC<{
  projectId: string;
  templateId: string;
}> = ({ projectId, templateId }) => {
  const [checklist, setChecklist] = useState<ProjectChecklist | null>(null);
  const [progress, setProgress] = useState<ChecklistProgress>({ total: 0, completed: 0, percentage: 0 });
  const [activeCategory, setActiveCategory] = useState<string>('');

  const checklistManager = new PlotChecklistManager();

  useEffect(() => {
    // 加载或创建检查清单
    let existingChecklist = checklistManager.getProjectChecklist(projectId, templateId);
    if (!existingChecklist) {
      existingChecklist = checklistManager.createProjectChecklist(projectId, templateId);
    }

    setChecklist(existingChecklist);
    setProgress(checklistManager.getChecklistProgress(existingChecklist.id));

    if (existingChecklist.categories.length > 0) {
      setActiveCategory(existingChecklist.categories[0].id);
    }
  }, [projectId, templateId]);

  const handleItemCheck = (itemId: string, checked: boolean) => {
    if (!checklist) return;

    checklistManager.updateChecklistItem(checklist.id, itemId, { checked });

    // 更新本地状态
    const updatedChecklist = { ...checklist };
    for (const category of updatedChecklist.categories) {
      const item = category.items.find(i => i.id === itemId);
      if (item) {
        item.checked = checked;
        break;
      }
    }

    setChecklist(updatedChecklist);
    setProgress(checklistManager.getChecklistProgress(checklist.id));
  };

  const handleItemNotes = (itemId: string, notes: string) => {
    if (!checklist) return;

    checklistManager.updateChecklistItem(checklist.id, itemId, { notes });

    // 更新本地状态
    const updatedChecklist = { ...checklist };
    for (const category of updatedChecklist.categories) {
      const item = category.items.find(i => i.id === itemId);
      if (item) {
        item.notes = notes;
        break;
      }
    }

    setChecklist(updatedChecklist);
  };

  return (
    <div className="checklist-interface">
      <div className="checklist-header">
        <h2>{checklist?.name}</h2>
        <div className="progress-indicator">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${progress.percentage}%` }}
            ></div>
          </div>
          <span className="progress-text">
            {progress.completed}/{progress.total} ({Math.round(progress.percentage)}%)
          </span>
        </div>
      </div>

      <div className="checklist-content">
        <div className="category-nav">
          {checklist?.categories.map(category => (
            <button
              key={category.id}
              className={activeCategory === category.id ? 'active' : ''}
              onClick={() => setActiveCategory(category.id)}
            >
              {category.name}
            </button>
          ))}
        </div>

        <div className="category-content">
          {checklist?.categories
            .filter(category => category.id === activeCategory)
            .map(category => (
              <div key={category.id} className="category">
                <h3>{category.name}</h3>
                <p className="category-description">{category.description}</p>

                <div className="checklist-items">
                  {category.items.map(item => (
                    <ChecklistItemComponent
                      key={item.id}
                      item={item}
                      onCheck={(checked) => handleItemCheck(item.id, checked)}
                      onNotesChange={(notes) => handleItemNotes(item.id, notes)}
                    />
                  ))}
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
};

// ChecklistItemComponent.tsx
const ChecklistItemComponent: React.FC<{
  item: ChecklistItem;
  onCheck: (checked: boolean) => void;
  onNotesChange: (notes: string) => void;
}> = ({ item, onCheck, onNotesChange }) => {
  const [showNotes, setShowNotes] = useState(false);
  const [notes, setNotes] = useState(item.notes || '');

  const handleNotesSubmit = () => {
    onNotesChange(notes);
    setShowNotes(false);
  };

  return (
    <div className={`checklist-item priority-${item.priority}`}>
      <div className="item-header">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={item.checked}
            onChange={(e) => onCheck(e.target.checked)}
          />
          <span className="checkmark"></span>
          <span className="item-title">{item.title}</span>
        </label>

        <button
          className="notes-button"
          onClick={() => setShowNotes(!showNotes)}
          title="添加备注"
        >
          📝
        </button>
      </div>

      <p className="item-description">{item.description}</p>

      {showNotes && (
        <div className="notes-section">
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="添加备注或修改建议..."
            rows={3}
          />
          <div className="notes-actions">
            <button onClick={handleNotesSubmit}>保存</button>
            <button onClick={() => setShowNotes(false)}>取消</button>
          </div>
        </div>
      )}

      {item.notes && !showNotes && (
        <div className="existing-notes">
          <strong>备注：</strong> {item.notes}
        </div>
      )}
    </div>
  );
};
```

## 4. 简单诊断工具实现

### 诊断引擎
```typescript
// diagnosticEngine.ts
interface DiagnosticTest {
  id: string;
  name: string;
  description: string;
  category: string;
  timeEstimate: number; // 分钟
  execute: (input: any) => DiagnosticResult;
}

interface DiagnosticResult {
  testId: string;
  score: number; // 0-100
  status: 'excellent' | 'good' | 'warning' | 'critical';
  issues: DiagnosticIssue[];
  suggestions: string[];
  timestamp: Date;
}

interface DiagnosticIssue {
  type: 'error' | 'warning' | 'info';
  message: string;
  location?: string;
  severity: 'high' | 'medium' | 'low';
}

export class DiagnosticEngine {
  private tests: Map<string, DiagnosticTest> = new Map();

  constructor() {
    this.registerDefaultTests();
  }

  private registerDefaultTests(): void {
    // 故事核心诊断
    this.registerTest({
      id: 'story_core',
      name: '故事核心测试',
      description: '检验故事核心是否清晰',
      category: 'structure',
      timeEstimate: 2,
      execute: this.executeStoryCoreTest
    });

    // 角色独特性测试
    this.registerTest({
      id: 'character_uniqueness',
      name: '角色独特性测试',
      description: '检查角色是否具有独特性',
      category: 'character',
      timeEstimate: 5,
      execute: this.executeCharacterUniquenessTest
    });

    // 更多测试...
  }

  registerTest(test: DiagnosticTest): void {
    this.tests.set(test.id, test);
  }

  runTest(testId: string, input: any): DiagnosticResult {
    const test = this.tests.get(testId);
    if (!test) {
      throw new Error(`Test ${testId} not found`);
    }

    try {
      return test.execute(input);
    } catch (error) {
      return {
        testId,
        score: 0,
        status: 'critical',
        issues: [{
          type: 'error',
          message: `测试执行失败: ${error.message}`,
          severity: 'high'
        }],
        suggestions: ['请检查输入数据格式'],
        timestamp: new Date()
      };
    }
  }

  runBatch(testIds: string[], input: any): DiagnosticResult[] {
    return testIds.map(testId => this.runTest(testId, input));
  }

  getAvailableTests(category?: string): DiagnosticTest[] {
    const tests = Array.from(this.tests.values());
    return category ? tests.filter(t => t.category === category) : tests;
  }

  // 具体测试实现
  private executeStoryCoreTest = (input: { summary: string }): DiagnosticResult => {
    const { summary } = input;
    const issues: DiagnosticIssue[] = [];
    const suggestions: string[] = [];
    let score = 100;

    // 检查长度
    if (summary.length < 50) {
      issues.push({
        type: 'warning',
        message: '故事概述过于简短',
        severity: 'medium'
      });
      suggestions.push('尝试用更多细节描述故事');
      score -= 20;
    }

    if (summary.length > 500) {
      issues.push({
        type: 'warning',
        message: '故事概述过于冗长',
        severity: 'low'
      });
      suggestions.push('尝试简化核心概念');
      score -= 10;
    }

    // 检查关键元素
    const hasCharacter = /主角|角色|人物/.test(summary);
    const hasConflict = /冲突|问题|挑战|困难/.test(summary);
    const hasGoal = /目标|目的|想要|追求/.test(summary);

    if (!hasCharacter) {
      issues.push({
        type: 'error',
        message: '缺少明确的主角描述',
        severity: 'high'
      });
      suggestions.push('明确描述故事的主要角色');
      score -= 30;
    }

    if (!hasConflict) {
      issues.push({
        type: 'error',
        message: '缺少明确的冲突描述',
        severity: 'high'
      });
      suggestions.push('明确描述故事的主要冲突');
      score -= 30;
    }

    if (!hasGoal) {
      issues.push({
        type: 'warning',
        message: '缺少明确的目标描述',
        severity: 'medium'
      });
      suggestions.push('明确描述角色的目标或动机');
      score -= 20;
    }

    const status = score >= 80 ? 'excellent' :
                   score >= 60 ? 'good' :
                   score >= 40 ? 'warning' : 'critical';

    return {
      testId: 'story_core',
      score,
      status,
      issues,
      suggestions,
      timestamp: new Date()
    };
  };

  private executeCharacterUniquenessTest = (input: { characters: Character[] }): DiagnosticResult => {
    const { characters } = input;
    const issues: DiagnosticIssue[] = [];
    const suggestions: string[] = [];
    let score = 100;

    if (characters.length === 0) {
      return {
        testId: 'character_uniqueness',
        score: 0,
        status: 'critical',
        issues: [{ type: 'error', message: '没有角色数据', severity: 'high' }],
        suggestions: ['请先创建角色'],
        timestamp: new Date()
      };
    }

    // 检查角色独特性
    for (const character of characters) {
      const traits = character.personality.coreTraits;

      if (traits.length < 3) {
        issues.push({
          type: 'warning',
          message: `角色 ${character.basicInfo.name} 的核心特质过少`,
          severity: 'medium'
        });
        score -= 15;
      }

      // 检查是否有具体的背景故事
      if (!character.background.importantEvents.length) {
        issues.push({
          type: 'warning',
          message: `角色 ${character.basicInfo.name} 缺少重要经历`,
          severity: 'medium'
        });
        score -= 10;
      }
    }

    // 检查角色间的差异
    if (characters.length > 1) {
      // 简单的相似度检查
      // 实际实现会更复杂
    }

    if (issues.length === 0) {
      suggestions.push('角色设计良好，保持这种独特性');
    } else {
      suggestions.push('为每个角色添加更多独特的特质和背景');
    }

    const status = score >= 80 ? 'excellent' :
                   score >= 60 ? 'good' :
                   score >= 40 ? 'warning' : 'critical';

    return {
      testId: 'character_uniqueness',
      score,
      status,
      issues,
      suggestions,
      timestamp: new Date()
    };
  };
}
```

### 诊断界面
```typescript
// DiagnosticInterface.tsx
export const DiagnosticInterface: React.FC<{
  projectId: string;
}> = ({ projectId }) => {
  const [engine] = useState(new DiagnosticEngine());
  const [availableTests, setAvailableTests] = useState<DiagnosticTest[]>([]);
  const [selectedTests, setSelectedTests] = useState<string[]>([]);
  const [results, setResults] = useState<DiagnosticResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    setAvailableTests(engine.getAvailableTests());
  }, [engine]);

  const handleTestSelection = (testId: string, selected: boolean) => {
    if (selected) {
      setSelectedTests(prev => [...prev, testId]);
    } else {
      setSelectedTests(prev => prev.filter(id => id !== testId));
    }
  };

  const runSelectedTests = async () => {
    setIsRunning(true);
    setResults([]);

    try {
      // 收集必要的数据
      const projectData = await collectProjectData(projectId);

      // 运行选中的测试
      const testResults = engine.runBatch(selectedTests, projectData);
      setResults(testResults);
    } catch (error) {
      console.error('诊断失败:', error);
    } finally {
      setIsRunning(false);
    }
  };

  const collectProjectData = async (projectId: string) => {
    // 收集项目相关数据
    const characterService = new CharacterService();
    const characters = characterService.getAllCharacters()
      .filter(c => c.projectId === projectId);

    // 其他数据收集...

    return {
      characters,
      // 其他数据...
    };
  };

  return (
    <div className="diagnostic-interface">
      <div className="diagnostic-header">
        <h2>故事诊断工具</h2>
        <p>选择要运行的诊断测试，快速发现故事中的潜在问题</p>
      </div>

      <div className="test-selection">
        <h3>可用测试</h3>
        <div className="test-categories">
          {Object.entries(groupTestsByCategory(availableTests)).map(([category, tests]) => (
            <div key={category} className="test-category">
              <h4>{getCategoryName(category)}</h4>
              {tests.map(test => (
                <TestSelectionItem
                  key={test.id}
                  test={test}
                  selected={selectedTests.includes(test.id)}
                  onSelectionChange={(selected) => handleTestSelection(test.id, selected)}
                />
              ))}
            </div>
          ))}
        </div>

        <div className="test-actions">
          <button
            onClick={runSelectedTests}
            disabled={selectedTests.length === 0 || isRunning}
            className="run-tests-button"
          >
            {isRunning ? '运行中...' : `运行选中的测试 (${selectedTests.length})`}
          </button>
        </div>
      </div>

      {results.length > 0 && (
        <div className="diagnostic-results">
          <h3>诊断结果</h3>
          {results.map(result => (
            <DiagnosticResultCard key={result.testId} result={result} />
          ))}

          <div className="overall-summary">
            <OverallSummary results={results} />
          </div>
        </div>
      )}
    </div>
  );
};

// DiagnosticResultCard.tsx
const DiagnosticResultCard: React.FC<{ result: DiagnosticResult }> = ({ result }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'excellent': return '#4CAF50';
      case 'good': return '#8BC34A';
      case 'warning': return '#FF9800';
      case 'critical': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'excellent': return '优秀';
      case 'good': return '良好';
      case 'warning': return '需要注意';
      case 'critical': return '需要改进';
      default: return '未知';
    }
  };

  return (
    <div className="diagnostic-result-card">
      <div className="result-header">
        <h4>{getTestName(result.testId)}</h4>
        <div className="score-indicator">
          <div
            className="score-circle"
            style={{ backgroundColor: getStatusColor(result.status) }}
          >
            {result.score}
          </div>
          <span className="status-text">{getStatusText(result.status)}</span>
        </div>
      </div>

      {result.issues.length > 0 && (
        <div className="issues-section">
          <h5>发现的问题</h5>
          {result.issues.map((issue, index) => (
            <div key={index} className={`issue-item ${issue.type} ${issue.severity}`}>
              <span className="issue-icon">
                {issue.type === 'error' ? '❌' : issue.type === 'warning' ? '⚠️' : 'ℹ️'}
              </span>
              <span className="issue-message">{issue.message}</span>
            </div>
          ))}
        </div>
      )}

      {result.suggestions.length > 0 && (
        <div className="suggestions-section">
          <h5>改进建议</h5>
          <ul>
            {result.suggestions.map((suggestion, index) => (
              <li key={index}>{suggestion}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
```

## 部署和维护

### 构建脚本
```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "jest",
    "lint": "eslint src --ext .ts,.tsx",
    "type-check": "tsc --noEmit"
  }
}
```

### 数据备份和恢复
```typescript
// backupService.ts
export class BackupService {
  async exportAllData(): Promise<string> {
    const data = {
      characters: new CharacterService().getAllCharacters(),
      checklists: new PlotChecklistManager().getAllChecklists(),
      interviews: new InterviewManager().getAllSessions(),
      // 其他数据...
      exportDate: new Date().toISOString(),
      version: '1.0.0'
    };

    return JSON.stringify(data, null, 2);
  }

  async importData(jsonData: string): Promise<void> {
    const data = JSON.parse(jsonData);

    // 验证数据格式
    this.validateImportData(data);

    // 导入各类数据
    if (data.characters) {
      const characterService = new CharacterService();
      for (const character of data.characters) {
        await characterService.saveCharacter(character);
      }
    }

    // 导入其他数据...
  }

  private validateImportData(data: any): void {
    if (!data.version || !data.exportDate) {
      throw new Error('无效的备份文件格式');
    }

    // 更多验证...
  }
}
```

这个技术实现方案提供了一个完整的基础创作工具系统架构，包括数据模型、核心功能、用户界面和系统维护等各个方面。每个工具都设计为模块化和可扩展的，可以根据实际需求进行调整和优化。