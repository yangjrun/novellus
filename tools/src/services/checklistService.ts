import { ChecklistTemplate, ChecklistCategory, ChecklistItem, ProjectChecklist, ChecklistProgress } from '@types/index';
import { StorageService, generateId } from '@utils/storage';

export class ChecklistService {
  private storage: StorageService;
  private templates: Map<string, ChecklistTemplate> = new Map();

  constructor() {
    this.storage = new StorageService('checklists');
    this.initializeDefaultTemplates();
  }

  private initializeDefaultTemplates(): void {
    // 三幕结构检查模板
    const threeActTemplate: ChecklistTemplate = {
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
            },
            {
              id: 'world_building',
              category: 'act_one',
              title: '建立故事世界和背景',
              description: '世界观和背景设定是否清晰',
              checked: false,
              priority: 'high'
            },
            {
              id: 'central_conflict',
              category: 'act_one',
              title: '提出中心冲突',
              description: '故事的主要冲突是否明确提出',
              checked: false,
              priority: 'high'
            },
            {
              id: 'first_plot_point',
              category: 'act_one',
              title: '第一个转折点清晰',
              description: '推动故事进入第二幕的转折点是否明确',
              checked: false,
              priority: 'medium'
            }
          ]
        },
        {
          id: 'act_two',
          name: '第二幕（发展）',
          description: '冲突发展和角色成长',
          items: [
            {
              id: 'conflict_escalation',
              category: 'act_two',
              title: '冲突逐步升级',
              description: '故事冲突是否层层递进',
              checked: false,
              priority: 'high'
            },
            {
              id: 'increasing_obstacles',
              category: 'act_two',
              title: '角色面临增加的障碍',
              description: '角色遇到的困难是否逐渐增加',
              checked: false,
              priority: 'medium'
            },
            {
              id: 'midpoint_crisis',
              category: 'act_two',
              title: '中点危机或转折',
              description: '故事中点是否有重要的危机或转折',
              checked: false,
              priority: 'medium'
            },
            {
              id: 'character_decision',
              category: 'act_two',
              title: '角色做出重要决定',
              description: '角色是否做出推动剧情的关键决定',
              checked: false,
              priority: 'high'
            },
            {
              id: 'second_plot_point',
              category: 'act_two',
              title: '第二个转折点引向高潮',
              description: '推动故事进入高潮的转折点是否有力',
              checked: false,
              priority: 'high'
            }
          ]
        },
        {
          id: 'act_three',
          name: '第三幕（结局）',
          description: '高潮和结局',
          items: [
            {
              id: 'engaging_climax',
              category: 'act_three',
              title: '高潮场面引人入胜',
              description: '故事高潮是否紧张刺激',
              checked: false,
              priority: 'high'
            },
            {
              id: 'conflict_resolution',
              category: 'act_three',
              title: '主要冲突得到解决',
              description: '故事的主要冲突是否得到satisfactory解决',
              checked: false,
              priority: 'high'
            },
            {
              id: 'character_arc_completion',
              category: 'act_three',
              title: '角色弧光完成',
              description: '主要角色的成长轨迹是否完整',
              checked: false,
              priority: 'high'
            },
            {
              id: 'satisfying_ending',
              category: 'act_three',
              title: '结局令人满意',
              description: '故事结局是否让读者感到满意',
              checked: false,
              priority: 'high'
            },
            {
              id: 'loose_ends_tied',
              category: 'act_three',
              title: '所有重要线索得到处理',
              description: '重要的剧情线索是否都有交代',
              checked: false,
              priority: 'medium'
            }
          ]
        }
      ]
    };

    // 角色弧光检查模板
    const characterArcTemplate: ChecklistTemplate = {
      id: 'character_arc',
      name: '角色弧光检查',
      description: '检查主要角色的发展轨迹',
      categories: [
        {
          id: 'protagonist_development',
          name: '主角发展',
          description: '主角的成长和变化',
          items: [
            {
              id: 'clear_starting_state',
              category: 'protagonist_development',
              title: '起始状态明确',
              description: '主角在故事开始时的状态是否清晰',
              checked: false,
              priority: 'high'
            },
            {
              id: 'reasonable_motivation',
              category: 'protagonist_development',
              title: '变化动机合理',
              description: '主角改变的动机是否可信',
              checked: false,
              priority: 'high'
            },
            {
              id: 'believable_growth',
              category: 'protagonist_development',
              title: '成长过程可信',
              description: '主角的成长过程是否自然可信',
              checked: false,
              priority: 'high'
            },
            {
              id: 'satisfying_end_state',
              category: 'protagonist_development',
              title: '最终状态令人满意',
              description: '主角的最终状态是否令人满意',
              checked: false,
              priority: 'medium'
            },
            {
              id: 'internal_external_conflict',
              category: 'protagonist_development',
              title: '内在冲突与外在冲突呼应',
              description: '主角的内心斗争与外部冲突是否相互呼应',
              checked: false,
              priority: 'medium'
            }
          ]
        },
        {
          id: 'supporting_character_function',
          name: '配角功能',
          description: '配角的作用和发展',
          items: [
            {
              id: 'clear_purpose',
              category: 'supporting_character_function',
              title: '每个配角都有明确作用',
              description: '配角在故事中的作用是否明确',
              checked: false,
              priority: 'medium'
            },
            {
              id: 'plot_advancement',
              category: 'supporting_character_function',
              title: '配角推动情节发展',
              description: '配角是否有效推动故事前进',
              checked: false,
              priority: 'medium'
            },
            {
              id: 'mini_character_arcs',
              category: 'supporting_character_function',
              title: '配角有自己的小弧光',
              description: '重要配角是否有自己的发展轨迹',
              checked: false,
              priority: 'low'
            },
            {
              id: 'clear_relationships',
              category: 'supporting_character_function',
              title: '配角与主角关系清晰',
              description: '配角与主角的关系是否明确',
              checked: false,
              priority: 'medium'
            }
          ]
        }
      ]
    };

    // 质量检查模板
    const qualityCheckTemplate: ChecklistTemplate = {
      id: 'quality_check',
      name: '整体质量检查',
      description: '检查故事的整体质量和完整性',
      categories: [
        {
          id: 'plot_consistency',
          name: '情节一致性',
          description: '情节逻辑和一致性检查',
          items: [
            {
              id: 'logical_progression',
              category: 'plot_consistency',
              title: '情节发展逻辑',
              description: '故事情节发展是否合乎逻辑',
              checked: false,
              priority: 'high'
            },
            {
              id: 'timeline_consistency',
              category: 'plot_consistency',
              title: '时间线一致性',
              description: '故事时间线是否前后一致',
              checked: false,
              priority: 'high'
            },
            {
              id: 'cause_and_effect',
              category: 'plot_consistency',
              title: '因果关系清晰',
              description: '事件之间的因果关系是否清楚',
              checked: false,
              priority: 'high'
            },
            {
              id: 'foreshadowing_payoff',
              category: 'plot_consistency',
              title: '伏笔得到呼应',
              description: '前面的伏笔是否在后面得到呼应',
              checked: false,
              priority: 'medium'
            }
          ]
        },
        {
          id: 'character_consistency',
          name: '角色一致性',
          description: '角色行为和发展的一致性',
          items: [
            {
              id: 'behavior_consistency',
              category: 'character_consistency',
              title: '角色行为一致',
              description: '角色行为是否符合其性格设定',
              checked: false,
              priority: 'high'
            },
            {
              id: 'dialogue_consistency',
              category: 'character_consistency',
              title: '对话风格一致',
              description: '角色对话是否保持一致的风格',
              checked: false,
              priority: 'medium'
            },
            {
              id: 'motivation_clarity',
              category: 'character_consistency',
              title: '动机清晰合理',
              description: '角色的动机是否清晰合理',
              checked: false,
              priority: 'high'
            }
          ]
        },
        {
          id: 'pacing_and_structure',
          name: '节奏和结构',
          description: '故事节奏和结构检查',
          items: [
            {
              id: 'good_pacing',
              category: 'pacing_and_structure',
              title: '节奏恰当',
              description: '故事节奏是否恰到好处',
              checked: false,
              priority: 'medium'
            },
            {
              id: 'tension_variation',
              category: 'pacing_and_structure',
              title: '张力变化',
              description: '故事张力是否有适当的起伏',
              checked: false,
              priority: 'medium'
            },
            {
              id: 'scene_purpose',
              category: 'pacing_and_structure',
              title: '每个场景都有目的',
              description: '每个场景是否都推进故事或角色发展',
              checked: false,
              priority: 'medium'
            }
          ]
        }
      ]
    };

    this.templates.set('three_act_structure', threeActTemplate);
    this.templates.set('character_arc', characterArcTemplate);
    this.templates.set('quality_check', qualityCheckTemplate);
  }

  // 获取所有可用模板
  getAvailableTemplates(): ChecklistTemplate[] {
    return Array.from(this.templates.values());
  }

  // 根据ID获取模板
  getTemplate(templateId: string): ChecklistTemplate | null {
    return this.templates.get(templateId) || null;
  }

  // 为项目创建检查清单
  async createProjectChecklist(projectId: string, templateId: string): Promise<ProjectChecklist> {
    const template = this.getTemplate(templateId);
    if (!template) {
      throw new Error(`未找到模板: ${templateId}`);
    }

    const checklist: ProjectChecklist = {
      id: generateId(),
      projectId,
      templateId,
      name: template.name,
      description: template.description,
      createdAt: new Date(),
      updatedAt: new Date(),
      categories: template.categories.map(category => ({
        ...category,
        items: category.items.map(item => ({ ...item }))
      }))
    };

    await this.storage.set(checklist.id, checklist);
    return checklist;
  }

  // 获取项目的检查清单
  async getProjectChecklist(checklistId: string): Promise<ProjectChecklist | null> {
    return await this.storage.get<ProjectChecklist>(checklistId);
  }

  // 获取项目的所有检查清单
  async getProjectChecklists(projectId: string): Promise<ProjectChecklist[]> {
    const allChecklists = await this.storage.getAll<ProjectChecklist>();
    return allChecklists.filter(checklist => checklist.projectId === projectId);
  }

  // 更新检查项
  async updateChecklistItem(
    checklistId: string,
    itemId: string,
    updates: Partial<ChecklistItem>
  ): Promise<void> {
    const checklist = await this.getProjectChecklist(checklistId);
    if (!checklist) {
      throw new Error('检查清单不存在');
    }

    let itemFound = false;
    for (const category of checklist.categories) {
      const item = category.items.find(i => i.id === itemId);
      if (item) {
        Object.assign(item, updates);
        itemFound = true;
        break;
      }
    }

    if (!itemFound) {
      throw new Error('检查项不存在');
    }

    checklist.updatedAt = new Date();
    await this.storage.set(checklistId, checklist);
  }

  // 批量更新检查项
  async updateMultipleItems(
    checklistId: string,
    updates: Array<{ itemId: string; updates: Partial<ChecklistItem> }>
  ): Promise<void> {
    const checklist = await this.getProjectChecklist(checklistId);
    if (!checklist) {
      throw new Error('检查清单不存在');
    }

    for (const { itemId, updates: itemUpdates } of updates) {
      for (const category of checklist.categories) {
        const item = category.items.find(i => i.id === itemId);
        if (item) {
          Object.assign(item, itemUpdates);
          break;
        }
      }
    }

    checklist.updatedAt = new Date();
    await this.storage.set(checklistId, checklist);
  }

  // 获取检查清单进度
  getChecklistProgress(checklist: ProjectChecklist): ChecklistProgress {
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

  // 获取分类进度
  getCategoryProgress(category: ChecklistCategory): ChecklistProgress {
    const total = category.items.length;
    const completed = category.items.filter(item => item.checked).length;

    return {
      total,
      completed,
      percentage: total > 0 ? (completed / total) * 100 : 0
    };
  }

  // 按优先级获取未完成项目
  getIncompleteItemsByPriority(checklist: ProjectChecklist): {
    high: ChecklistItem[];
    medium: ChecklistItem[];
    low: ChecklistItem[];
  } {
    const incomplete = {
      high: [] as ChecklistItem[],
      medium: [] as ChecklistItem[],
      low: [] as ChecklistItem[]
    };

    for (const category of checklist.categories) {
      for (const item of category.items) {
        if (!item.checked) {
          incomplete[item.priority].push(item);
        }
      }
    }

    return incomplete;
  }

  // 获取已完成的高优先级项目数量
  getHighPriorityCompletionRate(checklist: ProjectChecklist): number {
    let totalHigh = 0;
    let completedHigh = 0;

    for (const category of checklist.categories) {
      for (const item of category.items) {
        if (item.priority === 'high') {
          totalHigh++;
          if (item.checked) completedHigh++;
        }
      }
    }

    return totalHigh > 0 ? (completedHigh / totalHigh) * 100 : 0;
  }

  // 删除检查清单
  async deleteChecklist(checklistId: string): Promise<boolean> {
    try {
      await this.storage.remove(checklistId);
      return true;
    } catch (error) {
      console.error('删除检查清单失败:', error);
      return false;
    }
  }

  // 复制检查清单
  async duplicateChecklist(checklistId: string): Promise<ProjectChecklist | null> {
    const original = await this.getProjectChecklist(checklistId);
    if (!original) return null;

    const duplicate: ProjectChecklist = {
      ...original,
      id: generateId(),
      name: `${original.name} (副本)`,
      createdAt: new Date(),
      updatedAt: new Date(),
      categories: original.categories.map(category => ({
        ...category,
        items: category.items.map(item => ({
          ...item,
          checked: false, // 重置检查状态
          notes: '' // 清空备注
        }))
      }))
    };

    await this.storage.set(duplicate.id, duplicate);
    return duplicate;
  }

  // 重置检查清单
  async resetChecklist(checklistId: string): Promise<void> {
    const checklist = await this.getProjectChecklist(checklistId);
    if (!checklist) {
      throw new Error('检查清单不存在');
    }

    for (const category of checklist.categories) {
      for (const item of category.items) {
        item.checked = false;
        item.notes = '';
      }
    }

    checklist.updatedAt = new Date();
    await this.storage.set(checklistId, checklist);
  }

  // 导出检查清单报告
  generateChecklistReport(checklist: ProjectChecklist): {
    summary: ChecklistProgress;
    categoryBreakdown: Array<{
      category: string;
      progress: ChecklistProgress;
      completedItems: ChecklistItem[];
      incompleteItems: ChecklistItem[];
    }>;
    priorityBreakdown: {
      high: ChecklistProgress;
      medium: ChecklistProgress;
      low: ChecklistProgress;
    };
    recommendations: string[];
  } {
    const summary = this.getChecklistProgress(checklist);
    const incomplete = this.getIncompleteItemsByPriority(checklist);

    const categoryBreakdown = checklist.categories.map(category => {
      const progress = this.getCategoryProgress(category);
      const completedItems = category.items.filter(item => item.checked);
      const incompleteItems = category.items.filter(item => !item.checked);

      return {
        category: category.name,
        progress,
        completedItems,
        incompleteItems
      };
    });

    // 计算优先级进度
    const priorityBreakdown = {
      high: this.calculatePriorityProgress(checklist, 'high'),
      medium: this.calculatePriorityProgress(checklist, 'medium'),
      low: this.calculatePriorityProgress(checklist, 'low')
    };

    // 生成建议
    const recommendations = this.generateRecommendations(checklist, incomplete);

    return {
      summary,
      categoryBreakdown,
      priorityBreakdown,
      recommendations
    };
  }

  private calculatePriorityProgress(checklist: ProjectChecklist, priority: 'high' | 'medium' | 'low'): ChecklistProgress {
    let total = 0;
    let completed = 0;

    for (const category of checklist.categories) {
      for (const item of category.items) {
        if (item.priority === priority) {
          total++;
          if (item.checked) completed++;
        }
      }
    }

    return {
      total,
      completed,
      percentage: total > 0 ? (completed / total) * 100 : 0
    };
  }

  private generateRecommendations(
    checklist: ProjectChecklist,
    incomplete: { high: ChecklistItem[]; medium: ChecklistItem[]; low: ChecklistItem[] }
  ): string[] {
    const recommendations: string[] = [];

    // 高优先级建议
    if (incomplete.high.length > 0) {
      recommendations.push(`首先关注 ${incomplete.high.length} 个高优先级问题`);

      if (incomplete.high.length > 5) {
        recommendations.push('高优先级问题较多，建议逐步解决');
      }
    }

    // 结构性建议
    const structureIssues = incomplete.high.filter(item =>
      item.category.includes('act_') || item.title.includes('结构') || item.title.includes('冲突')
    );

    if (structureIssues.length > 0) {
      recommendations.push('发现结构性问题，建议重新审视故事架构');
    }

    // 角色建议
    const characterIssues = incomplete.high.filter(item =>
      item.category.includes('character') || item.title.includes('角色')
    );

    if (characterIssues.length > 0) {
      recommendations.push('角色发展需要加强，建议深化角色塑造');
    }

    // 整体进度建议
    const progress = this.getChecklistProgress(checklist);
    if (progress.percentage < 50) {
      recommendations.push('故事还处于早期阶段，建议先完善基础结构');
    } else if (progress.percentage < 80) {
      recommendations.push('故事基本成型，建议重点关注细节完善');
    } else {
      recommendations.push('故事接近完成，建议进行全面润色');
    }

    return recommendations;
  }
}