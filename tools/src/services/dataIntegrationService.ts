import { Character, NarrativeStructure, WorldBuilding, Scene } from '../types/index';
import { CharacterService } from '@services/characterService';
import { EnhancedCharacterService } from '@services/enhancedCharacterService';
import { NarrativeService } from '@services/narrativeService';
import { WorldBuildingService } from '@services/worldBuildingService';
import { SceneService } from '@services/sceneService';

// 数据集成服务 - 跨工具数据共享和同步
export class DataIntegrationService {
  private characterService: CharacterService;
  private enhancedCharacterService: EnhancedCharacterService;
  private narrativeService: NarrativeService;
  private worldService: WorldBuildingService;
  private sceneService: SceneService;

  constructor() {
    this.characterService = new CharacterService();
    this.enhancedCharacterService = new EnhancedCharacterService();
    this.narrativeService = new NarrativeService();
    this.worldService = new WorldBuildingService();
    this.sceneService = new SceneService();
  }

  // 获取项目的完整数据概览
  async getProjectOverview(projectId: string): Promise<ProjectOverview> {
    try {
      const [characters, narratives, worlds, scenes] = await Promise.all([
        this.enhancedCharacterService.getAllCharacters(),
        this.narrativeService.getNarrativesByProject(projectId),
        this.worldService.getWorldsByProject(projectId),
        this.sceneService.getScenesByProject(projectId)
      ]);

      const projectCharacters = characters.filter(c => c.projectId === projectId);

      return {
        projectId,
        characters: projectCharacters,
        narratives,
        worlds,
        scenes,
        statistics: this.calculateProjectStatistics(projectCharacters, narratives, worlds, scenes),
        connections: this.analyzeDataConnections(projectCharacters, narratives, worlds, scenes),
        lastUpdated: new Date()
      };
    } catch (error) {
      console.error('获取项目概览失败:', error);
      throw error;
    }
  }

  // 计算项目统计信息
  private calculateProjectStatistics(
    characters: Character[],
    narratives: NarrativeStructure[],
    worlds: WorldBuilding[],
    scenes: Scene[]
  ): ProjectStatistics {
    const totalPlotPoints = narratives.reduce((sum, n) => sum + n.plotPoints.length, 0);
    const completedPlotPoints = narratives.reduce((sum, n) =>
      sum + n.plotPoints.filter(p => p.completed).length, 0
    );

    const totalCultures = worlds.reduce((sum, w) => sum + w.cultures.length, 0);
    const totalLocations = worlds.reduce((sum, w) => sum + w.locations.length, 0);

    const characterTypes = characters.reduce((acc, c) => {
      acc[c.storyRole.characterType] = (acc[c.storyRole.characterType] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const sceneTypes = scenes.reduce((acc, s) => {
      acc[s.purpose.storyFunction] = (acc[s.purpose.storyFunction] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      characters: {
        total: characters.length,
        byType: characterTypes,
        avgCompleteness: this.calculateCharacterCompleteness(characters)
      },
      narratives: {
        total: narratives.length,
        plotPointsTotal: totalPlotPoints,
        plotPointsCompleted: completedPlotPoints,
        completionRate: totalPlotPoints > 0 ? Math.round((completedPlotPoints / totalPlotPoints) * 100) : 0
      },
      worlds: {
        total: worlds.length,
        culturesTotal: totalCultures,
        locationsTotal: totalLocations,
        avgConsistency: this.calculateWorldConsistency(worlds)
      },
      scenes: {
        total: scenes.length,
        byFunction: sceneTypes,
        avgQuality: this.calculateSceneQuality(scenes)
      }
    };
  }

  // 分析数据连接关系
  private analyzeDataConnections(
    characters: Character[],
    narratives: NarrativeStructure[],
    worlds: WorldBuilding[],
    scenes: Scene[]
  ): DataConnections {
    const connections: DataConnections = {
      characterToPlot: [],
      characterToWorld: [],
      characterToScene: [],
      plotToWorld: [],
      plotToScene: [],
      worldToScene: [],
      orphanedData: {
        characters: [],
        plotPoints: [],
        locations: [],
        scenes: []
      }
    };

    // 角色到情节点的连接
    narratives.forEach(narrative => {
      narrative.plotPoints.forEach(plotPoint => {
        plotPoint.relatedCharacters.forEach(characterId => {
          const character = characters.find(c => c.id === characterId);
          if (character) {
            connections.characterToPlot.push({
              characterId: character.id,
              characterName: character.basicInfo.name,
              plotPointId: plotPoint.id,
              plotPointName: plotPoint.name,
              narrativeId: narrative.id
            });
          }
        });
      });
    });

    // 角色到世界的连接
    characters.forEach(character => {
      const matchingWorld = worlds.find(world =>
        world.cultures.some(culture =>
          culture.name.toLowerCase().includes(character.specialSettings.culturalBackground.toLowerCase()) ||
          character.specialSettings.culturalBackground.toLowerCase().includes(culture.name.toLowerCase())
        )
      );

      if (matchingWorld) {
        connections.characterToWorld.push({
          characterId: character.id,
          characterName: character.basicInfo.name,
          worldId: matchingWorld.id,
          worldName: matchingWorld.name,
          connectionType: 'cultural'
        });
      }
    });

    // 角色到场景的连接
    scenes.forEach(scene => {
      scene.characters.forEach(sceneChar => {
        const character = characters.find(c => c.id === sceneChar.characterId);
        if (character) {
          connections.characterToScene.push({
            characterId: character.id,
            characterName: character.basicInfo.name,
            sceneId: scene.id,
            sceneTitle: scene.title,
            role: sceneChar.role
          });
        }
      });
    });

    // 情节到场景的连接
    narratives.forEach(narrative => {
      narrative.plotPoints.forEach(plotPoint => {
        const relatedScenes = scenes.filter(scene =>
          plotPoint.relatedScenes.includes(scene.id)
        );

        relatedScenes.forEach(scene => {
          connections.plotToScene.push({
            plotPointId: plotPoint.id,
            plotPointName: plotPoint.name,
            sceneId: scene.id,
            sceneTitle: scene.title,
            narrativeId: narrative.id
          });
        });
      });
    });

    // 世界到场景的连接
    scenes.forEach(scene => {
      const matchingWorld = worlds.find(world =>
        world.locations.some(location => location.id === scene.locationId)
      );

      if (matchingWorld) {
        const location = matchingWorld.locations.find(l => l.id === scene.locationId);
        connections.worldToScene.push({
          worldId: matchingWorld.id,
          worldName: matchingWorld.name,
          sceneId: scene.id,
          sceneTitle: scene.title,
          locationId: scene.locationId,
          locationName: location?.name || ''
        });
      }
    });

    // 查找孤立数据
    connections.orphanedData.characters = characters.filter(character =>
      !connections.characterToPlot.some(c => c.characterId === character.id) &&
      !connections.characterToScene.some(c => c.characterId === character.id)
    ).map(c => ({ id: c.id, name: c.basicInfo.name }));

    connections.orphanedData.scenes = scenes.filter(scene =>
      scene.characters.length === 0 &&
      !connections.plotToScene.some(p => p.sceneId === scene.id)
    ).map(s => ({ id: s.id, name: s.title }));

    return connections;
  }

  // 数据同步和关联建议
  async generateSyncSuggestions(projectId: string): Promise<SyncSuggestion[]> {
    const overview = await this.getProjectOverview(projectId);
    const suggestions: SyncSuggestion[] = [];

    // 检查角色是否关联到情节
    overview.characters.forEach(character => {
      const hasPlotConnection = overview.connections.characterToPlot.some(
        c => c.characterId === character.id
      );

      if (!hasPlotConnection && character.storyRole.characterType !== 'minor') {
        suggestions.push({
          type: 'missing-connection',
          priority: 'high',
          title: `角色"${character.basicInfo.name}"未关联到任何情节点`,
          description: '重要角色应该参与到故事的关键情节中',
          action: 'link-character-to-plot',
          targetId: character.id,
          targetType: 'character'
        });
      }
    });

    // 检查世界设定是否被场景使用
    overview.worlds.forEach(world => {
      const hasSceneConnection = overview.connections.worldToScene.some(
        w => w.worldId === world.id
      );

      if (!hasSceneConnection) {
        suggestions.push({
          type: 'unused-asset',
          priority: 'medium',
          title: `世界"${world.name}"未被任何场景使用`,
          description: '创建的世界设定应该在故事场景中体现',
          action: 'create-scene-for-world',
          targetId: world.id,
          targetType: 'world'
        });
      }
    });

    // 检查情节点是否有对应场景
    overview.narratives.forEach(narrative => {
      narrative.plotPoints.forEach(plotPoint => {
        const hasSceneConnection = overview.connections.plotToScene.some(
          p => p.plotPointId === plotPoint.id
        );

        if (!hasSceneConnection && plotPoint.type !== 'custom') {
          suggestions.push({
            type: 'missing-scene',
            priority: 'high',
            title: `情节点"${plotPoint.name}"缺少对应场景`,
            description: '重要的情节点应该有具体的场景来展现',
            action: 'create-scene-for-plot',
            targetId: plotPoint.id,
            targetType: 'plot-point'
          });
        }
      });
    });

    // 检查角色背景与世界设定的一致性
    overview.characters.forEach(character => {
      if (character.specialSettings.culturalBackground) {
        const hasWorldConnection = overview.connections.characterToWorld.some(
          c => c.characterId === character.id
        );

        if (!hasWorldConnection) {
          suggestions.push({
            type: 'inconsistency',
            priority: 'medium',
            title: `角色"${character.basicInfo.name}"的文化背景未在世界设定中体现`,
            description: '角色的文化背景应该与世界设定中的文化保持一致',
            action: 'sync-character-culture',
            targetId: character.id,
            targetType: 'character'
          });
        }
      }
    });

    return suggestions.sort((a, b) => {
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    });
  }

  // 自动关联数据
  async autoLinkData(projectId: string, linkType: string, sourceId: string, targetId: string): Promise<void> {
    try {
      switch (linkType) {
        case 'character-to-plot':
          await this.linkCharacterToPlot(sourceId, targetId);
          break;
        case 'character-to-scene':
          await this.linkCharacterToScene(sourceId, targetId);
          break;
        case 'plot-to-scene':
          await this.linkPlotToScene(sourceId, targetId);
          break;
        case 'world-to-scene':
          await this.linkWorldToScene(sourceId, targetId);
          break;
        default:
          throw new Error(`不支持的关联类型: ${linkType}`);
      }
    } catch (error) {
      console.error('自动关联数据失败:', error);
      throw error;
    }
  }

  // 具体的关联方法
  private async linkCharacterToPlot(characterId: string, plotPointId: string): Promise<void> {
    const narratives = await this.narrativeService.getAllNarratives();
    const narrative = narratives.find(n =>
      n.plotPoints.some(p => p.id === plotPointId)
    );

    if (narrative) {
      const plotPoint = narrative.plotPoints.find(p => p.id === plotPointId);
      if (plotPoint && !plotPoint.relatedCharacters.includes(characterId)) {
        plotPoint.relatedCharacters.push(characterId);
        await this.narrativeService.saveNarrative(narrative);
      }
    }
  }

  private async linkCharacterToScene(characterId: string, sceneId: string): Promise<void> {
    const scene = await this.sceneService.getSceneById(sceneId);
    const character = await this.enhancedCharacterService.getCharacterById(characterId);

    if (scene && character) {
      const existingCharacter = scene.characters.find(c => c.characterId === characterId);
      if (!existingCharacter) {
        scene.characters.push({
          characterId,
          role: character.storyRole.characterType === 'protagonist' ? 'protagonist' : 'supporting',
          emotionalState: '',
          motivation: '',
          goals: [],
          obstacles: []
        });
        await this.sceneService.saveScene(scene);
      }
    }
  }

  private async linkPlotToScene(plotPointId: string, sceneId: string): Promise<void> {
    const narratives = await this.narrativeService.getAllNarratives();
    const narrative = narratives.find(n =>
      n.plotPoints.some(p => p.id === plotPointId)
    );

    if (narrative) {
      const plotPoint = narrative.plotPoints.find(p => p.id === plotPointId);
      if (plotPoint && !plotPoint.relatedScenes.includes(sceneId)) {
        plotPoint.relatedScenes.push(sceneId);
        await this.narrativeService.saveNarrative(narrative);
      }
    }
  }

  private async linkWorldToScene(worldId: string, sceneId: string): Promise<void> {
    const world = await this.worldService.getWorldById(worldId);
    const scene = await this.sceneService.getSceneById(sceneId);

    if (world && scene && world.locations.length > 0) {
      // 如果场景还没有指定地点，使用世界中的第一个地点
      if (!scene.locationId) {
        scene.locationId = world.locations[0].id;
        await this.sceneService.saveScene(scene);
      }
    }
  }

  // 辅助计算方法
  private calculateCharacterCompleteness(characters: Character[]): number {
    if (characters.length === 0) return 0;

    const totalScore = characters.reduce((sum, character) => {
      let score = 0;
      const fields = [
        character.basicInfo.name,
        character.basicInfo.age,
        character.basicInfo.occupation,
        character.personality.coreTraits.length > 0,
        character.background.childhood,
        character.abilities.professionalSkills.length > 0,
        character.storyRole.characterArc
      ];

      score = fields.filter(field => field && field !== '').length;
      return sum + (score / fields.length) * 100;
    }, 0);

    return Math.round(totalScore / characters.length);
  }

  private calculateWorldConsistency(worlds: WorldBuilding[]): number {
    if (worlds.length === 0) return 0;

    const totalScore = worlds.reduce((sum, world) => {
      const consistency = this.worldService.checkWorldConsistency(world);
      return sum + consistency.score;
    }, 0);

    return Math.round(totalScore / worlds.length);
  }

  private calculateSceneQuality(scenes: Scene[]): number {
    if (scenes.length === 0) return 0;

    const totalScore = scenes.reduce((sum, scene) => {
      const quality = this.sceneService.evaluateSceneQuality(scene);
      return sum + quality.score;
    }, 0);

    return Math.round(totalScore / scenes.length);
  }
}

// 类型定义
export interface ProjectOverview {
  projectId: string;
  characters: Character[];
  narratives: NarrativeStructure[];
  worlds: WorldBuilding[];
  scenes: Scene[];
  statistics: ProjectStatistics;
  connections: DataConnections;
  lastUpdated: Date;
}

export interface ProjectStatistics {
  characters: {
    total: number;
    byType: Record<string, number>;
    avgCompleteness: number;
  };
  narratives: {
    total: number;
    plotPointsTotal: number;
    plotPointsCompleted: number;
    completionRate: number;
  };
  worlds: {
    total: number;
    culturesTotal: number;
    locationsTotal: number;
    avgConsistency: number;
  };
  scenes: {
    total: number;
    byFunction: Record<string, number>;
    avgQuality: number;
  };
}

export interface DataConnections {
  characterToPlot: Array<{
    characterId: string;
    characterName: string;
    plotPointId: string;
    plotPointName: string;
    narrativeId: string;
  }>;
  characterToWorld: Array<{
    characterId: string;
    characterName: string;
    worldId: string;
    worldName: string;
    connectionType: string;
  }>;
  characterToScene: Array<{
    characterId: string;
    characterName: string;
    sceneId: string;
    sceneTitle: string;
    role: string;
  }>;
  plotToWorld: Array<{
    plotPointId: string;
    plotPointName: string;
    worldId: string;
    worldName: string;
    narrativeId: string;
  }>;
  plotToScene: Array<{
    plotPointId: string;
    plotPointName: string;
    sceneId: string;
    sceneTitle: string;
    narrativeId: string;
  }>;
  worldToScene: Array<{
    worldId: string;
    worldName: string;
    sceneId: string;
    sceneTitle: string;
    locationId: string;
    locationName: string;
  }>;
  orphanedData: {
    characters: Array<{ id: string; name: string }>;
    plotPoints: Array<{ id: string; name: string }>;
    locations: Array<{ id: string; name: string }>;
    scenes: Array<{ id: string; name: string }>;
  };
}

export interface SyncSuggestion {
  type: 'missing-connection' | 'unused-asset' | 'missing-scene' | 'inconsistency';
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  action: string;
  targetId: string;
  targetType: 'character' | 'plot-point' | 'world' | 'scene';
}