import { NarrativeStructure, PlotPoint, TimelineEvent } from '../types/index';
import { storage } from '@utils/storage';

export class NarrativeService {
  private readonly storageKey = 'novellus-narratives';

  async getAllNarratives(): Promise<NarrativeStructure[]> {
    try {
      const narratives = await storage.getItem<NarrativeStructure[]>(this.storageKey) || [];
      return narratives.map(this.deserializeNarrative);
    } catch (error) {
      console.error('获取叙事结构失败:', error);
      return [];
    }
  }

  async getNarrativeById(id: string): Promise<NarrativeStructure | null> {
    try {
      const narratives = await this.getAllNarratives();
      return narratives.find(narrative => narrative.id === id) || null;
    } catch (error) {
      console.error('获取叙事结构失败:', error);
      return null;
    }
  }

  async getNarrativesByProject(projectId: string): Promise<NarrativeStructure[]> {
    try {
      const narratives = await this.getAllNarratives();
      return narratives.filter(narrative => narrative.projectId === projectId);
    } catch (error) {
      console.error('获取项目叙事结构失败:', error);
      return [];
    }
  }

  async saveNarrative(narrative: NarrativeStructure): Promise<void> {
    try {
      const narratives = await this.getAllNarratives();
      const existingIndex = narratives.findIndex(n => n.id === narrative.id);

      const serializedNarrative = this.serializeNarrative({
        ...narrative,
        updatedAt: new Date()
      });

      if (existingIndex >= 0) {
        narratives[existingIndex] = serializedNarrative;
      } else {
        narratives.push(serializedNarrative);
      }

      await storage.setItem(this.storageKey, narratives);
    } catch (error) {
      console.error('保存叙事结构失败:', error);
      throw error;
    }
  }

  async deleteNarrative(id: string): Promise<void> {
    try {
      const narratives = await this.getAllNarratives();
      const filteredNarratives = narratives
        .filter(narrative => narrative.id !== id)
        .map(this.serializeNarrative);

      await storage.setItem(this.storageKey, filteredNarratives);
    } catch (error) {
      console.error('删除叙事结构失败:', error);
      throw error;
    }
  }

  // 创建叙事结构模板
  createNarrativeTemplate(
    projectId: string,
    type: NarrativeStructure['type'],
    culturalTradition: NarrativeStructure['culturalTradition'] = 'western'
  ): NarrativeStructure {
    const templates = this.getStructureTemplates();
    const template = templates[type] || templates['three-act'];

    return {
      id: this.generateId(),
      projectId,
      name: template.name,
      type,
      culturalTradition,
      description: template.description,
      plotPoints: template.plotPoints.map(point => ({
        ...point,
        id: this.generateId(),
        completed: false,
        notes: '',
        relatedCharacters: [],
        relatedScenes: []
      })),
      timelineEvents: [],
      createdAt: new Date(),
      updatedAt: new Date()
    };
  }

  // 获取结构模板库
  private getStructureTemplates() {
    return {
      'three-act': {
        name: '三幕式结构',
        description: '经典的西方叙事结构，包含建立-对抗-解决三个主要部分',
        plotPoints: [
          {
            name: '开场钩子',
            description: '吸引读者注意力的开场事件',
            position: 1,
            type: 'inciting-incident' as const
          },
          {
            name: '煽动事件',
            description: '推动故事开始的关键事件',
            position: 10,
            type: 'inciting-incident' as const
          },
          {
            name: '第一转折点',
            description: '故事从建立转向对抗',
            position: 25,
            type: 'plot-point-1' as const
          },
          {
            name: '中点',
            description: '故事的重要转折点',
            position: 50,
            type: 'midpoint' as const
          },
          {
            name: '第二转折点',
            description: '故事从对抗转向解决',
            position: 75,
            type: 'plot-point-2' as const
          },
          {
            name: '高潮',
            description: '故事的最高点和主要冲突的解决',
            position: 90,
            type: 'climax' as const
          },
          {
            name: '结局',
            description: '故事的收尾和后续影响',
            position: 100,
            type: 'resolution' as const
          }
        ]
      },
      'heros-journey': {
        name: '英雄之旅',
        description: '约瑟夫·坎贝尔的单一神话结构模式',
        plotPoints: [
          {
            name: '日常世界',
            description: '英雄在冒险开始前的正常生活',
            position: 5,
            type: 'custom' as const
          },
          {
            name: '冒险召唤',
            description: '英雄收到开始冒险的召唤',
            position: 10,
            type: 'inciting-incident' as const
          },
          {
            name: '拒绝召唤',
            description: '英雄最初拒绝或犹豫',
            position: 15,
            type: 'custom' as const
          },
          {
            name: '遇见导师',
            description: '英雄遇到智慧的导师或获得帮助',
            position: 20,
            type: 'custom' as const
          },
          {
            name: '越过第一道门槛',
            description: '英雄离开日常世界，进入特殊世界',
            position: 25,
            type: 'plot-point-1' as const
          },
          {
            name: '试炼、盟友与敌人',
            description: '英雄在特殊世界中面临各种挑战',
            position: 40,
            type: 'custom' as const
          },
          {
            name: '进入最深的洞穴',
            description: '英雄准备面对最大的恐惧',
            position: 55,
            type: 'midpoint' as const
          },
          {
            name: '磨难',
            description: '英雄面临最大的危机',
            position: 70,
            type: 'custom' as const
          },
          {
            name: '获得奖赏',
            description: '英雄克服危机，获得奖赏',
            position: 75,
            type: 'plot-point-2' as const
          },
          {
            name: '回归之路',
            description: '英雄开始返回日常世界',
            position: 85,
            type: 'custom' as const
          },
          {
            name: '复活',
            description: '英雄经历最后的考验和转变',
            position: 92,
            type: 'climax' as const
          },
          {
            name: '携宝而归',
            description: '英雄回到日常世界，分享所得',
            position: 100,
            type: 'resolution' as const
          }
        ]
      },
      'kishotenketsu': {
        name: '起承转合',
        description: '东亚传统的四段式叙事结构',
        plotPoints: [
          {
            name: '起',
            description: '故事的开始，介绍背景和人物',
            position: 25,
            type: 'custom' as const
          },
          {
            name: '承',
            description: '承接开头，发展情节',
            position: 50,
            type: 'custom' as const
          },
          {
            name: '转',
            description: '转折点，出现意想不到的发展',
            position: 75,
            type: 'midpoint' as const
          },
          {
            name: '合',
            description: '结合前面的情节，得出结论',
            position: 100,
            type: 'resolution' as const
          }
        ]
      },
      'seven-point': {
        name: '七点故事结构',
        description: '丹·威尔斯的七点故事结构',
        plotPoints: [
          {
            name: '钩子',
            description: '开场吸引读者的元素',
            position: 1,
            type: 'custom' as const
          },
          {
            name: '情节转折1',
            description: '故事开始的重大变化',
            position: 25,
            type: 'plot-point-1' as const
          },
          {
            name: '夹点1',
            description: '施加压力的事件',
            position: 37.5,
            type: 'custom' as const
          },
          {
            name: '中点',
            description: '故事的转折中心',
            position: 50,
            type: 'midpoint' as const
          },
          {
            name: '夹点2',
            description: '进一步施压的事件',
            position: 62.5,
            type: 'custom' as const
          },
          {
            name: '情节转折2',
            description: '最后阶段的重大变化',
            position: 75,
            type: 'plot-point-2' as const
          },
          {
            name: '结局',
            description: '故事的最终结果',
            position: 100,
            type: 'resolution' as const
          }
        ]
      },
      'freytag': {
        name: '弗莱塔格金字塔',
        description: '德国戏剧理论家弗莱塔格的五段式结构',
        plotPoints: [
          {
            name: '开端',
            description: '故事背景和人物介绍',
            position: 10,
            type: 'custom' as const
          },
          {
            name: '上升动作',
            description: '冲突逐渐加剧',
            position: 30,
            type: 'plot-point-1' as const
          },
          {
            name: '高潮',
            description: '冲突达到顶点',
            position: 50,
            type: 'climax' as const
          },
          {
            name: '下降动作',
            description: '冲突开始解决',
            position: 70,
            type: 'plot-point-2' as const
          },
          {
            name: '结局',
            description: '故事的最终解决',
            position: 100,
            type: 'resolution' as const
          }
        ]
      },
      'custom': {
        name: '自定义结构',
        description: '根据需要自定义的故事结构',
        plotPoints: [
          {
            name: '开始',
            description: '故事的开始',
            position: 10,
            type: 'custom' as const
          },
          {
            name: '发展',
            description: '故事的发展',
            position: 50,
            type: 'custom' as const
          },
          {
            name: '结束',
            description: '故事的结束',
            position: 100,
            type: 'resolution' as const
          }
        ]
      }
    };
  }

  // 添加情节点
  async addPlotPoint(narrativeId: string, plotPoint: Omit<PlotPoint, 'id'>): Promise<void> {
    const narrative = await this.getNarrativeById(narrativeId);
    if (!narrative) throw new Error('找不到指定的叙事结构');

    const newPlotPoint: PlotPoint = {
      ...plotPoint,
      id: this.generateId()
    };

    narrative.plotPoints.push(newPlotPoint);
    narrative.plotPoints.sort((a, b) => a.position - b.position);

    await this.saveNarrative(narrative);
  }

  // 更新情节点
  async updatePlotPoint(narrativeId: string, plotPointId: string, updates: Partial<PlotPoint>): Promise<void> {
    const narrative = await this.getNarrativeById(narrativeId);
    if (!narrative) throw new Error('找不到指定的叙事结构');

    const plotPoint = narrative.plotPoints.find(p => p.id === plotPointId);
    if (!plotPoint) throw new Error('找不到指定的情节点');

    Object.assign(plotPoint, updates);
    await this.saveNarrative(narrative);
  }

  // 删除情节点
  async deletePlotPoint(narrativeId: string, plotPointId: string): Promise<void> {
    const narrative = await this.getNarrativeById(narrativeId);
    if (!narrative) throw new Error('找不到指定的叙事结构');

    narrative.plotPoints = narrative.plotPoints.filter(p => p.id !== plotPointId);
    await this.saveNarrative(narrative);
  }

  // 添加时间线事件
  async addTimelineEvent(narrativeId: string, event: Omit<TimelineEvent, 'id'>): Promise<void> {
    const narrative = await this.getNarrativeById(narrativeId);
    if (!narrative) throw new Error('找不到指定的叙事结构');

    const newEvent: TimelineEvent = {
      ...event,
      id: this.generateId()
    };

    narrative.timelineEvents.push(newEvent);
    narrative.timelineEvents.sort((a, b) => a.timestamp - b.timestamp);

    await this.saveNarrative(narrative);
  }

  // 计算进度
  getProgress(narrative: NarrativeStructure): { completed: number; total: number; percentage: number } {
    const total = narrative.plotPoints.length;
    const completed = narrative.plotPoints.filter(p => p.completed).length;
    return {
      completed,
      total,
      percentage: total > 0 ? Math.round((completed / total) * 100) : 0
    };
  }

  private serializeNarrative(narrative: NarrativeStructure): any {
    return {
      ...narrative,
      createdAt: narrative.createdAt.toISOString(),
      updatedAt: narrative.updatedAt.toISOString()
    };
  }

  private deserializeNarrative(data: any): NarrativeStructure {
    return {
      ...data,
      createdAt: new Date(data.createdAt),
      updatedAt: new Date(data.updatedAt)
    };
  }

  private generateId(): string {
    return `narrative_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}