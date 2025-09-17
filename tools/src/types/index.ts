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

  // 心理状态 (增强版)
  psychology: {
    mentalHealth: string;
    mentalHealthStatus: 'excellent' | 'good' | 'fair' | 'poor' | 'critical';
    copingMechanisms: CopingMechanism[];
    emotionalPatterns: EmotionalPattern[];
    trauma: TraumaEntry[];
    growthNeeds: string[];
    cognitivePatterns: CognitivePattern[];
    stressResponses: StressResponse[];
    emotionalIntelligence: EmotionalIntelligence;
    psychologicalDefenses: string[];
    mentalHealthHistory: MentalHealthRecord[];
  };

  // 故事功能
  storyRole: {
    characterType: 'protagonist' | 'antagonist' | 'supporting' | 'minor';
    characterArc: string;
    conflictRole: string;
    symbolism: string;
    readerConnection: string;
  };

  // 特殊设定 (增强版)
  specialSettings: {
    worldBuilding: string;
    culturalBackground: string;
    historicalContext: string;
    technologyLevel: string;
    magicAbilities?: string;
    culturalIdentity: CulturalIdentity;
    religiousBeliefs: ReligiousBeliefs;
    languageProfile: LanguageProfile;
    behaviorPatterns: BehaviorPattern[];
    rolePlayingNotes: string[];
  };

  // 角色成长轨迹 (新增)
  characterArc: {
    currentStage: string;
    developmentGoals: DevelopmentGoal[];
    growthMilestones: GrowthMilestone[];
    personalityChanges: PersonalityChange[];
    skillProgression: SkillProgression[];
    relationshipEvolution: RelationshipEvolution[];
    internalConflicts: InternalConflict[];
    externalChallenges: ExternalChallenge[];
  };

  // 互动行为模式 (新增)
  behaviorProfile: {
    communicationStyle: CommunicationStyle;
    bodyLanguage: BodyLanguage;
    decisionMaking: DecisionMakingStyle;
    conflictResponse: ConflictResponse;
    socialBehavior: SocialBehavior;
    workStyle: WorkStyle;
    leadershipStyle?: LeadershipStyle;
    learningStyle: LearningStyle;
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

// === 增强版角色创作系统新增类型定义 ===

// 心理状态相关类型
export interface CopingMechanism {
  type: 'healthy' | 'unhealthy' | 'adaptive' | 'maladaptive';
  strategy: string;
  triggers: string[];
  effectiveness: number; // 1-10
  frequency: 'rare' | 'occasional' | 'frequent' | 'constant';
}

export interface EmotionalPattern {
  emotion: string;
  triggers: string[];
  intensity: number; // 1-10
  duration: 'brief' | 'moderate' | 'extended' | 'persistent';
  expression: string;
  impact: string;
}

export interface TraumaEntry {
  type: 'childhood' | 'adolescent' | 'adult' | 'recent';
  event: string;
  age: number;
  severity: 'mild' | 'moderate' | 'severe' | 'critical';
  status: 'unresolved' | 'healing' | 'resolved' | 'integrated';
  triggers: string[];
  effects: string[];
  copingMethods: string[];
}

export interface CognitivePattern {
  type: 'bias' | 'heuristic' | 'belief' | 'assumption';
  description: string;
  situations: string[];
  impact: 'positive' | 'negative' | 'neutral' | 'mixed';
  awareness: 'unconscious' | 'subconscious' | 'conscious';
}

export interface StressResponse {
  stressor: string;
  physicalResponse: string[];
  emotionalResponse: string[];
  behavioralResponse: string[];
  cognitiveResponse: string[];
  timeframe: string;
}

export interface EmotionalIntelligence {
  selfAwareness: number; // 1-10
  selfRegulation: number; // 1-10
  motivation: number; // 1-10
  empathy: number; // 1-10
  socialSkills: number; // 1-10
  strengths: string[];
  weaknesses: string[];
}

export interface MentalHealthRecord {
  date: Date;
  status: 'excellent' | 'good' | 'fair' | 'poor' | 'critical';
  notes: string;
  triggers?: string[];
  improvements?: string[];
}

// 文化身份相关类型
export interface CulturalIdentity {
  primaryCulture: string;
  subcultures: string[];
  culturalValues: string[];
  culturalConflicts: string[];
  assimilationLevel: number; // 1-10
  culturalPride: number; // 1-10
  traditionalPractices: string[];
  modernAdaptations: string[];
}

export interface ReligiousBeliefs {
  religion?: string;
  denomination?: string;
  devotionLevel: number; // 1-10
  practices: string[];
  beliefs: string[];
  doubts: string[];
  spiritualExperiences: string[];
  religionInLife: 'central' | 'important' | 'moderate' | 'minimal' | 'absent';
}

export interface LanguageProfile {
  nativeLanguage: string;
  fluentLanguages: string[];
  learningLanguages: string[];
  accents: string[];
  dialectVariations: string[];
  speechPatterns: SpeechPattern[];
  languageBarriers: string[];
  communicationPreferences: string[];
}

export interface SpeechPattern {
  characteristic: string;
  examples: string[];
  frequency: 'always' | 'often' | 'sometimes' | 'rarely';
  context: string[];
  origin: string;
}

export interface BehaviorPattern {
  category: 'social' | 'personal' | 'professional' | 'intimate';
  behavior: string;
  frequency: 'daily' | 'weekly' | 'monthly' | 'situational';
  triggers: string[];
  context: string[];
  development: string;
}

// 角色成长相关类型
export interface DevelopmentGoal {
  id: string;
  category: 'personal' | 'professional' | 'social' | 'spiritual' | 'physical';
  goal: string;
  motivation: string;
  timeline: string;
  obstacles: string[];
  progress: number; // 0-100
  priority: 'high' | 'medium' | 'low';
}

export interface GrowthMilestone {
  id: string;
  title: string;
  description: string;
  targetDate?: Date;
  completedDate?: Date;
  significance: string;
  prerequisites: string[];
  relatedGoals: string[];
  status: 'planned' | 'in_progress' | 'achieved' | 'missed';
}

export interface PersonalityChange {
  id: string;
  trait: string;
  oldValue: string;
  newValue: string;
  trigger: string;
  timeline: string;
  significance: 'minor' | 'moderate' | 'major' | 'transformative';
  stability: 'temporary' | 'developing' | 'stable' | 'permanent';
}

export interface SkillProgression {
  skill: string;
  category: 'professional' | 'personal' | 'artistic' | 'physical' | 'social';
  currentLevel: number; // 1-10
  targetLevel: number; // 1-10
  learningMethod: string;
  timeframe: string;
  obstacles: string[];
  mentors: string[];
}

export interface RelationshipEvolution {
  relationshipId: string;
  personName: string;
  evolutionType: 'strengthening' | 'weakening' | 'changing' | 'ending' | 'beginning';
  previousState: string;
  currentState: string;
  triggers: string[];
  timeline: string;
  significance: string;
}

export interface InternalConflict {
  id: string;
  title: string;
  description: string;
  conflictingValues: string[];
  emotionalImpact: string;
  manifestations: string[];
  resolutionAttempts: string[];
  status: 'unaware' | 'emerging' | 'active' | 'resolving' | 'resolved';
}

export interface ExternalChallenge {
  id: string;
  title: string;
  description: string;
  source: 'environmental' | 'social' | 'professional' | 'family' | 'society';
  difficulty: number; // 1-10
  timeframe: string;
  resources: string[];
  strategies: string[];
  status: 'upcoming' | 'current' | 'overcoming' | 'overcome' | 'failed';
}

// 行为模式相关类型
export interface CommunicationStyle {
  primaryStyle: 'direct' | 'indirect' | 'assertive' | 'passive' | 'aggressive' | 'passive-aggressive';
  verbalCharacteristics: string[];
  nonverbalCharacteristics: string[];
  listeningStyle: 'active' | 'selective' | 'distracted' | 'judgmental';
  feedbackStyle: string;
  conflictCommunication: string;
  culturalInfluences: string[];
}

export interface BodyLanguage {
  posture: string;
  gestures: string[];
  facialExpressions: string[];
  eyeContact: 'frequent' | 'moderate' | 'minimal' | 'avoiding';
  personalSpace: 'close' | 'normal' | 'distant' | 'variable';
  nervousHabits: string[];
  confidenceIndicators: string[];
  culturalVariations: string[];
}

export interface DecisionMakingStyle {
  approach: 'analytical' | 'intuitive' | 'spontaneous' | 'cautious' | 'collaborative';
  timeframe: 'impulsive' | 'quick' | 'moderate' | 'deliberate' | 'procrastinating';
  informationGathering: string;
  riskTolerance: number; // 1-10
  influences: string[];
  biases: string[];
  decisionHistory: string[];
}

export interface ConflictResponse {
  primaryStyle: 'competing' | 'accommodating' | 'avoiding' | 'compromising' | 'collaborating';
  escalationTriggers: string[];
  deescalationMethods: string[];
  emotionalReactions: string[];
  physicalReactions: string[];
  recoveryMethods: string[];
  conflictHistory: string[];
}

export interface SocialBehavior {
  socialEnergy: 'introverted' | 'extroverted' | 'ambivert';
  groupDynamics: string;
  socialRoles: string[];
  boundaryManagement: string;
  socialAnxieties: string[];
  socialStrengths: string[];
  networkingStyle: string;
  socialAdaptability: number; // 1-10
}

export interface WorkStyle {
  productivity: 'morning' | 'afternoon' | 'evening' | 'night' | 'variable';
  environment: 'quiet' | 'bustling' | 'collaborative' | 'isolated';
  organization: 'highly_organized' | 'moderately_organized' | 'flexible' | 'chaotic';
  taskManagement: string;
  collaboration: string;
  innovation: string;
  stressManagement: string;
}

export interface LeadershipStyle {
  type: 'autocratic' | 'democratic' | 'laissez_faire' | 'transformational' | 'servant' | 'situational';
  strengths: string[];
  weaknesses: string[];
  motivationMethods: string[];
  delegationStyle: string;
  feedbackApproach: string;
  decisionInclusivity: string;
  crisisManagement: string;
}

export interface LearningStyle {
  primary: 'visual' | 'auditory' | 'kinesthetic' | 'reading' | 'multimodal';
  preferences: string[];
  strengths: string[];
  challenges: string[];
  motivationFactors: string[];
  retentionMethods: string[];
  environments: string[];
  adaptability: number; // 1-10
}