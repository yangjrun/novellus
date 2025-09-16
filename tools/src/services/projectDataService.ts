import narrativeStructureAnalysis from '../data/projects/narrative-structure-analysis.json';

// 项目数据接口定义
export interface ProjectAnalysisData {
  id: string;
  title: string;
  category: string;
  type: string;
  targetAudience: string;
  structureType?: string;
  culturalBackground: string;
  difficulty: string;
  createdAt: string;
  analysisContent: any;
  applicationNotes: {
    characterCreation: string[];
    worldBuilding: string[];
    sceneDesign: string[];
  };
  metadata: {
    sourcePrompt: string;
    generatedBy: string;
    aiModel: string;
    estimatedReadingTime: string;
    complexity: string;
    tags: string[];
  };
}

// 项目数据服务类
export class ProjectDataService {
  private static instance: ProjectDataService;
  private projectData: Map<string, ProjectAnalysisData> = new Map();

  private constructor() {
    this.loadStaticData();
  }

  static getInstance(): ProjectDataService {
    if (!ProjectDataService.instance) {
      ProjectDataService.instance = new ProjectDataService();
    }
    return ProjectDataService.instance;
  }

  // 加载静态数据
  private loadStaticData(): void {
    // 加载叙事结构分析数据
    this.projectData.set(narrativeStructureAnalysis.id, narrativeStructureAnalysis as ProjectAnalysisData);
  }

  // 获取特定类型的分析数据
  getAnalysisByCategory(category: string): ProjectAnalysisData[] {
    return Array.from(this.projectData.values())
      .filter(data => data.category === category);
  }

  // 获取特定分析数据
  getAnalysisById(id: string): ProjectAnalysisData | undefined {
    return this.projectData.get(id);
  }

  // 获取叙事结构分析（便捷方法）
  getNarrativeStructureAnalysis(): ProjectAnalysisData | undefined {
    return this.getAnalysisById('narrative_structure_hero_journey_web_novel');
  }

  // 获取角色创建的参考数据
  getCharacterCreationGuidelines(): string[] {
    const narrativeData = this.getNarrativeStructureAnalysis();
    if (!narrativeData) return [];

    return [
      ...narrativeData.applicationNotes.characterCreation,
      // 从叙事结构中提取角色发展阶段
      ...narrativeData.analysisContent.coreFramework.stageFlow.map((stage: any) =>
        `${stage.percentage}: ${stage.character} - ${stage.stage}`
      )
    ];
  }

  // 获取世界构建的参考数据
  getWorldBuildingGuidelines(): string[] {
    const narrativeData = this.getNarrativeStructureAnalysis();
    if (!narrativeData) return [];

    return [
      ...narrativeData.applicationNotes.worldBuilding,
      // 从主题分析中提取世界观要素
      ...narrativeData.analysisContent.themeAnalysis.implantationTechniques.techniques
        .filter((tech: any) => tech.type === '符号系统')
        .flatMap((tech: any) => tech.examples.map((example: string) => `符号系统需求: ${example}`))
    ];
  }

  // 获取场景设计的参考数据
  getSceneDesignGuidelines(): string[] {
    const narrativeData = this.getNarrativeStructureAnalysis();
    if (!narrativeData) return [];

    return [
      ...narrativeData.applicationNotes.sceneDesign,
      // 从关键节点中提取场景要求
      ...narrativeData.analysisContent.keyNodes.nodes.map((node: any) =>
        `${node.percentage} ${node.title}: ${node.narrativeFunctions[0]}`
      )
    ];
  }

  // 获取当前项目的叙事节点信息
  getNarrativeNodes(): Array<{
    id: string;
    title: string;
    percentage: string;
    functions: string[];
    features: string[];
  }> {
    const narrativeData = this.getNarrativeStructureAnalysis();
    if (!narrativeData) return [];

    return narrativeData.analysisContent.keyNodes.nodes.map((node: any) => ({
      id: node.id,
      title: node.title,
      percentage: node.percentage,
      functions: node.narrativeFunctions,
      features: node.structuralFeatures
    }));
  }

  // 获取主题层次信息
  getThemeLayers(): Array<{
    level: string;
    theme: string;
    purpose: string;
  }> {
    const narrativeData = this.getNarrativeStructureAnalysis();
    if (!narrativeData) return [];

    return narrativeData.analysisContent.themeAnalysis.themeProgression.layers;
  }

  // 保存新的分析数据
  saveAnalysisData(data: ProjectAnalysisData): void {
    this.projectData.set(data.id, data);
    // 这里可以添加持久化逻辑，比如保存到 localStorage 或发送到后端
    this.saveToLocalStorage(data);
  }

  // 保存到本地存储
  private saveToLocalStorage(data: ProjectAnalysisData): void {
    try {
      const existingData = localStorage.getItem('novellus-project-data');
      const projectData = existingData ? JSON.parse(existingData) : {};
      projectData[data.id] = data;
      localStorage.setItem('novellus-project-data', JSON.stringify(projectData));
    } catch (error) {
      console.error('保存项目数据到本地存储失败:', error);
    }
  }

  // 从本地存储加载数据
  loadFromLocalStorage(): void {
    try {
      const existingData = localStorage.getItem('novellus-project-data');
      if (existingData) {
        const projectData = JSON.parse(existingData);
        Object.values(projectData).forEach((data: any) => {
          this.projectData.set(data.id, data);
        });
      }
    } catch (error) {
      console.error('从本地存储加载项目数据失败:', error);
    }
  }

  // 获取所有分析数据
  getAllAnalysisData(): ProjectAnalysisData[] {
    return Array.from(this.projectData.values());
  }

  // 根据标签搜索分析数据
  searchByTags(tags: string[]): ProjectAnalysisData[] {
    return Array.from(this.projectData.values())
      .filter(data => tags.some(tag => data.metadata.tags.includes(tag)));
  }
}

// 导出单例实例
export const projectDataService = ProjectDataService.getInstance();