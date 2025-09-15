import { DiagnosticTest, DiagnosticResult, DiagnosticIssue, Character } from '@types/index';

export class DiagnosticService {
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

    // 角色一致性测试
    this.registerTest({
      id: 'character_consistency',
      name: '角色一致性测试',
      description: '检查角色行为是否一致',
      category: 'character',
      timeEstimate: 3,
      execute: this.executeCharacterConsistencyTest
    });

    // 对话质量测试
    this.registerTest({
      id: 'dialogue_quality',
      name: '对话质量测试',
      description: '检查对话的有效性和独特性',
      category: 'dialogue',
      timeEstimate: 4,
      execute: this.executeDialogueQualityTest
    });

    // 情节逻辑测试
    this.registerTest({
      id: 'plot_logic',
      name: '情节逻辑测试',
      description: '检查情节发展的逻辑性',
      category: 'structure',
      timeEstimate: 6,
      execute: this.executePlotLogicTest
    });
  }

  registerTest(test: DiagnosticTest): void {
    this.tests.set(test.id, test);
  }

  runTest(testId: string, input: any): DiagnosticResult {
    const test = this.tests.get(testId);
    if (!test) {
      throw new Error(`测试 ${testId} 不存在`);
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

    if (!summary || summary.trim().length === 0) {
      return {
        testId: 'story_core',
        score: 0,
        status: 'critical',
        issues: [{
          type: 'error',
          message: '缺少故事概述',
          severity: 'high'
        }],
        suggestions: ['请提供故事概述'],
        timestamp: new Date()
      };
    }

    // 检查长度
    if (summary.length < 50) {
      issues.push({
        type: 'warning',
        message: '故事概述过于简短',
        severity: 'medium'
      });
      suggestions.push('尝试用更多细节描述故事核心');
      score -= 20;
    }

    if (summary.length > 500) {
      issues.push({
        type: 'warning',
        message: '故事概述过于冗长',
        severity: 'low'
      });
      suggestions.push('尝试简化核心概念，突出重点');
      score -= 10;
    }

    // 检查关键元素
    const hasCharacter = /主角|角色|人物|他|她/.test(summary);
    const hasConflict = /冲突|问题|挑战|困难|危机|阻碍/.test(summary);
    const hasGoal = /目标|目的|想要|追求|希望|梦想/.test(summary);
    const hasAction = /行动|做|去|战斗|努力|尝试/.test(summary);

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
      suggestions.push('明确描述故事的主要冲突或问题');
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

    if (!hasAction) {
      issues.push({
        type: 'warning',
        message: '缺少行动描述',
        severity: 'medium'
      });
      suggestions.push('描述角色为实现目标采取的行动');
      score -= 15;
    }

    // 检查完整性
    if (hasCharacter && hasConflict && hasGoal && hasAction) {
      suggestions.push('故事核心要素完整，继续完善细节');
    }

    const status = score >= 80 ? 'excellent' :
                   score >= 60 ? 'good' :
                   score >= 40 ? 'warning' : 'critical';

    return {
      testId: 'story_core',
      score: Math.max(0, score),
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

    // 检查每个角色的独特性
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

      if (!character.background.importantEvents.length) {
        issues.push({
          type: 'warning',
          message: `角色 ${character.basicInfo.name} 缺少重要经历`,
          severity: 'medium'
        });
        score -= 10;
      }

      if (!character.personality.fears.length) {
        issues.push({
          type: 'info',
          message: `角色 ${character.basicInfo.name} 缺少恐惧设定`,
          severity: 'low'
        });
        score -= 5;
      }

      if (!character.personality.desires.length) {
        issues.push({
          type: 'info',
          message: `角色 ${character.basicInfo.name} 缺少欲望设定`,
          severity: 'low'
        });
        score -= 5;
      }
    }

    // 检查角色间的差异化
    if (characters.length > 1) {
      const allTraits = characters.flatMap(c => c.personality.coreTraits);
      const uniqueTraits = new Set(allTraits);

      if (uniqueTraits.size < allTraits.length * 0.7) {
        issues.push({
          type: 'warning',
          message: '角色特质重复过多，缺乏差异化',
          severity: 'medium'
        });
        suggestions.push('为每个角色设计更独特的性格特质');
        score -= 20;
      }
    }

    // 生成建议
    if (issues.length === 0) {
      suggestions.push('角色设计良好，继续保持这种独特性');
    } else {
      suggestions.push('为每个角色添加更多独特的特质和背景');
      if (characters.some(c => c.personality.coreTraits.length < 3)) {
        suggestions.push('确保每个角色至少有3个核心性格特质');
      }
      if (characters.some(c => !c.background.importantEvents.length)) {
        suggestions.push('为角色添加塑造性格的重要经历');
      }
    }

    const status = score >= 80 ? 'excellent' :
                   score >= 60 ? 'good' :
                   score >= 40 ? 'warning' : 'critical';

    return {
      testId: 'character_uniqueness',
      score: Math.max(0, score),
      status,
      issues,
      suggestions,
      timestamp: new Date()
    };
  };

  private executeCharacterConsistencyTest = (input: { characters: Character[] }): DiagnosticResult => {
    const { characters } = input;
    const issues: DiagnosticIssue[] = [];
    const suggestions: string[] = [];
    let score = 100;

    if (characters.length === 0) {
      return {
        testId: 'character_consistency',
        score: 0,
        status: 'critical',
        issues: [{ type: 'error', message: '没有角色数据', severity: 'high' }],
        suggestions: ['请先创建角色'],
        timestamp: new Date()
      };
    }

    for (const character of characters) {
      // 检查基本信息完整性
      if (!character.basicInfo.name) {
        issues.push({
          type: 'error',
          message: '角色缺少姓名',
          severity: 'high'
        });
        score -= 25;
      }

      // 检查性格与背景的一致性
      if (character.personality.coreTraits.length > 0 &&
          character.background.importantEvents.length === 0) {
        issues.push({
          type: 'warning',
          message: `角色 ${character.basicInfo.name} 有性格特质但缺少支撑的背景经历`,
          severity: 'medium'
        });
        score -= 15;
      }

      // 检查恐惧与欲望的平衡
      const fearsCount = character.personality.fears.length;
      const desiresCount = character.personality.desires.length;

      if (fearsCount === 0 && desiresCount === 0) {
        issues.push({
          type: 'warning',
          message: `角色 ${character.basicInfo.name} 缺少内在动机设定`,
          severity: 'medium'
        });
        score -= 10;
      }

      // 检查角色类型与特质的匹配
      if (character.storyRole.characterType === 'protagonist' &&
          character.personality.weaknesses.length === 0) {
        issues.push({
          type: 'info',
          message: `主角 ${character.basicInfo.name} 缺少弱点设定`,
          severity: 'low'
        });
        score -= 5;
      }
    }

    // 生成建议
    if (issues.length === 0) {
      suggestions.push('角色设定一致性良好');
    } else {
      suggestions.push('确保角色的性格、背景和动机相互支撑');
      suggestions.push('为每个角色设定明确的内在冲突');
    }

    const status = score >= 80 ? 'excellent' :
                   score >= 60 ? 'good' :
                   score >= 40 ? 'warning' : 'critical';

    return {
      testId: 'character_consistency',
      score: Math.max(0, score),
      status,
      issues,
      suggestions,
      timestamp: new Date()
    };
  };

  private executeDialogueQualityTest = (input: any): DiagnosticResult => {
    // 由于没有实际对话数据，这里提供模拟测试
    const issues: DiagnosticIssue[] = [];
    const suggestions: string[] = [];
    let score = 75; // 默认中等分数

    // 模拟一些通用的对话问题
    issues.push({
      type: 'info',
      message: '建议确保每个角色有独特的说话方式',
      severity: 'low'
    });

    suggestions.push('为每个角色设计独特的语言风格');
    suggestions.push('确保对话推进情节或揭示角色性格');
    suggestions.push('避免信息倾倒式的对话');

    return {
      testId: 'dialogue_quality',
      score,
      status: 'good',
      issues,
      suggestions,
      timestamp: new Date()
    };
  };

  private executePlotLogicTest = (input: { summary: string }): DiagnosticResult => {
    const { summary } = input;
    const issues: DiagnosticIssue[] = [];
    const suggestions: string[] = [];
    let score = 100;

    if (!summary || summary.trim().length === 0) {
      return {
        testId: 'plot_logic',
        score: 0,
        status: 'critical',
        issues: [{
          type: 'error',
          message: '缺少情节描述',
          severity: 'high'
        }],
        suggestions: ['请提供详细的情节描述'],
        timestamp: new Date()
      };
    }

    // 检查因果关系
    const hasCause = /因为|由于|所以|导致|引起/.test(summary);
    if (!hasCause) {
      issues.push({
        type: 'warning',
        message: '缺少明确的因果关系描述',
        severity: 'medium'
      });
      suggestions.push('明确事件之间的因果关系');
      score -= 20;
    }

    // 检查时间逻辑
    const hasTimeMarkers = /然后|接着|后来|最后|最终|之前|之后/.test(summary);
    if (!hasTimeMarkers) {
      issues.push({
        type: 'info',
        message: '缺少时间顺序标记',
        severity: 'low'
      });
      suggestions.push('使用时间标记词明确事件顺序');
      score -= 10;
    }

    // 检查转折点
    const hasTurningPoint = /但是|然而|突然|意外|转折/.test(summary);
    if (!hasTurningPoint) {
      issues.push({
        type: 'info',
        message: '可能缺少情节转折',
        severity: 'low'
      });
      suggestions.push('考虑添加情节转折增加故事张力');
      score -= 10;
    }

    if (issues.length === 0) {
      suggestions.push('情节逻辑清晰，继续保持');
    }

    const status = score >= 80 ? 'excellent' :
                   score >= 60 ? 'good' :
                   score >= 40 ? 'warning' : 'critical';

    return {
      testId: 'plot_logic',
      score: Math.max(0, score),
      status,
      issues,
      suggestions,
      timestamp: new Date()
    };
  };
}