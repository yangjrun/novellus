import { InterviewQuestion, InterviewSession, InterviewAnswer } from '@types/index';
import { StorageService, generateId } from '@utils/storage';

export class InterviewService {
  private storage: StorageService;
  private questionSets: Map<string, InterviewQuestion[]> = new Map();

  constructor() {
    this.storage = new StorageService('interviews');
    this.initializeQuestionSets();
  }

  private initializeQuestionSets(): void {
    // 基础认知面试问题
    this.questionSets.set('basic', [
      {
        id: 'basic_1',
        category: '基础认知',
        question: '请介绍一下你自己',
        type: 'text'
      },
      {
        id: 'basic_2',
        category: '基础认知',
        question: '你认为自己最大的优点是什么？',
        type: 'text'
      },
      {
        id: 'basic_3',
        category: '基础认知',
        question: '你最不喜欢自己的哪一点？',
        type: 'text'
      },
      {
        id: 'basic_4',
        category: '基础认知',
        question: '如果用三个词来描述自己，你会选择哪三个？',
        type: 'text'
      },
      {
        id: 'basic_5',
        category: '基础认知',
        question: '你觉得别人是怎么看你的？',
        type: 'text'
      },
      {
        id: 'basic_6',
        category: '基础认知',
        question: '你最自豪的一件事是什么？',
        type: 'text'
      },
      {
        id: 'basic_7',
        category: '基础认知',
        question: '你最后悔的一件事是什么？',
        type: 'text'
      }
    ]);

    // 价值观探索面试问题
    this.questionSets.set('values', [
      {
        id: 'values_1',
        category: '价值观探索',
        question: '什么对你来说最重要？',
        type: 'text'
      },
      {
        id: 'values_2',
        category: '价值观探索',
        question: '你绝对不会做的事情是什么？',
        type: 'text'
      },
      {
        id: 'values_3',
        category: '价值观探索',
        question: '你认为什么是正确的生活方式？',
        type: 'text'
      },
      {
        id: 'values_4',
        category: '价值观探索',
        question: '如果必须在家人和正义之间选择，你会怎么办？',
        type: 'text'
      },
      {
        id: 'values_5',
        category: '价值观探索',
        question: '你相信命运吗？为什么？',
        type: 'choice',
        choices: ['完全相信', '部分相信', '不太相信', '完全不信']
      },
      {
        id: 'values_6',
        category: '价值观探索',
        question: '金钱对你意味着什么？',
        type: 'text'
      },
      {
        id: 'values_7',
        category: '价值观探索',
        question: '你如何定义成功？',
        type: 'text'
      }
    ]);

    // 情感关系面试问题
    this.questionSets.set('emotions', [
      {
        id: 'emotions_1',
        category: '情感关系',
        question: '描述一下你最重要的一段关系',
        type: 'text'
      },
      {
        id: 'emotions_2',
        category: '情感关系',
        question: '你在恋爱关系中寻求什么？',
        type: 'text'
      },
      {
        id: 'emotions_3',
        category: '情感关系',
        question: '你如何处理冲突？',
        type: 'text'
      },
      {
        id: 'emotions_4',
        category: '情感关系',
        question: '什么会让你感到被背叛？',
        type: 'text'
      },
      {
        id: 'emotions_5',
        category: '情感关系',
        question: '你容易相信别人吗？',
        type: 'choice',
        choices: ['非常容易', '比较容易', '不太容易', '很难相信']
      },
      {
        id: 'emotions_6',
        category: '情感关系',
        question: '你如何表达爱意？',
        type: 'text'
      },
      {
        id: 'emotions_7',
        category: '情感关系',
        question: '什么会让你放弃一段关系？',
        type: 'text'
      }
    ]);

    // 恐惧与欲望面试问题
    this.questionSets.set('fears', [
      {
        id: 'fears_1',
        category: '恐惧与欲望',
        question: '你最害怕什么？',
        type: 'text'
      },
      {
        id: 'fears_2',
        category: '恐惧与欲望',
        question: '你最想要的是什么？',
        type: 'text'
      },
      {
        id: 'fears_3',
        category: '恐惧与欲望',
        question: '什么会让你晚上睡不着觉？',
        type: 'text'
      },
      {
        id: 'fears_4',
        category: '恐惧与欲望',
        question: '如果你有三个愿望，你会许什么愿？',
        type: 'text'
      },
      {
        id: 'fears_5',
        category: '恐惧与欲望',
        question: '你最不想失去的是什么？',
        type: 'text'
      },
      {
        id: 'fears_6',
        category: '恐惧与欲望',
        question: '什么情况下你会感到绝望？',
        type: 'text'
      },
      {
        id: 'fears_7',
        category: '恐惧与欲望',
        question: '你的人生目标是什么？',
        type: 'text'
      }
    ]);

    // 行为模式面试问题
    this.questionSets.set('behavior', [
      {
        id: 'behavior_1',
        category: '行为模式',
        question: '当你生气时，你通常会做什么？',
        type: 'text'
      },
      {
        id: 'behavior_2',
        category: '行为模式',
        question: '面对压力时，你如何应对？',
        type: 'text'
      },
      {
        id: 'behavior_3',
        category: '行为模式',
        question: '你如何做重要决定？',
        type: 'text'
      },
      {
        id: 'behavior_4',
        category: '行为模式',
        question: '在陌生环境中，你的第一反应是什么？',
        type: 'text'
      },
      {
        id: 'behavior_5',
        category: '行为模式',
        question: '你如何处理失败？',
        type: 'text'
      },
      {
        id: 'behavior_6',
        category: '行为模式',
        question: '当有人需要帮助时，你会怎么做？',
        type: 'text'
      },
      {
        id: 'behavior_7',
        category: '行为模式',
        question: '你如何庆祝成功？',
        type: 'text'
      }
    ]);

    // 过去经历面试问题
    this.questionSets.set('past', [
      {
        id: 'past_1',
        category: '过去经历',
        question: '说一说改变你人生轨迹的一件事',
        type: 'text'
      },
      {
        id: 'past_2',
        category: '过去经历',
        question: '你童年最深刻的记忆是什么？',
        type: 'text'
      },
      {
        id: 'past_3',
        category: '过去经历',
        question: '谁是对你影响最大的人？',
        type: 'text'
      },
      {
        id: 'past_4',
        category: '过去经历',
        question: '你经历过的最困难的时期是什么？',
        type: 'text'
      },
      {
        id: 'past_5',
        category: '过去经历',
        question: '你学到的最重要的教训是什么？',
        type: 'text'
      },
      {
        id: 'past_6',
        category: '过去经历',
        question: '有什么事情你希望能重新来过？',
        type: 'text'
      },
      {
        id: 'past_7',
        category: '过去经历',
        question: '你最想感谢的人是谁？',
        type: 'text'
      }
    ]);

    // 未来展望面试问题
    this.questionSets.set('future', [
      {
        id: 'future_1',
        category: '未来展望',
        question: '你希望五年后的自己是什么样子？',
        type: 'text'
      },
      {
        id: 'future_2',
        category: '未来展望',
        question: '你最想实现的梦想是什么？',
        type: 'text'
      },
      {
        id: 'future_3',
        category: '未来展望',
        question: '什么会阻止你实现目标？',
        type: 'text'
      },
      {
        id: 'future_4',
        category: '未来展望',
        question: '你对未来最大的担忧是什么？',
        type: 'text'
      },
      {
        id: 'future_5',
        category: '未来展望',
        question: '如果明天就是世界末日，你会做什么？',
        type: 'text'
      },
      {
        id: 'future_6',
        category: '未来展望',
        question: '你希望别人怎样记住你？',
        type: 'text'
      },
      {
        id: 'future_7',
        category: '未来展望',
        question: '你认为什么会让你的人生有意义？',
        type: 'text'
      }
    ]);

    // 情境应对面试问题
    this.questionSets.set('scenarios', [
      {
        id: 'scenarios_1',
        category: '情境应对',
        question: '你发现你最好的朋友背叛了你，你会怎么做？',
        type: 'text'
      },
      {
        id: 'scenarios_2',
        category: '情境应对',
        question: '你必须在两分钟内做出一个重要决定，你会怎么办？',
        type: 'text'
      },
      {
        id: 'scenarios_3',
        category: '情境应对',
        question: '你意外得到一大笔钱，你会如何处理？',
        type: 'text'
      },
      {
        id: 'scenarios_4',
        category: '情境应对',
        question: '你被误解并遭到众人指责，你会如何反应？',
        type: 'text'
      },
      {
        id: 'scenarios_5',
        category: '情境应对',
        question: '你必须向你讨厌的人求助，你会怎么做？',
        type: 'text'
      },
      {
        id: 'scenarios_6',
        category: '情境应对',
        question: '你发现了一个可能伤害他人的秘密，你会怎么办？',
        type: 'text'
      },
      {
        id: 'scenarios_7',
        category: '情境应对',
        question: '你面临职业生涯的重大选择，你会如何决定？',
        type: 'text'
      }
    ]);
  }

  // 获取可用的面试类型
  getAvailableInterviewTypes(): Array<{ id: string; name: string; description: string; questionCount: number }> {
    return [
      {
        id: 'basic',
        name: '基础认知面试',
        description: '了解角色的基本自我认知',
        questionCount: this.questionSets.get('basic')?.length || 0
      },
      {
        id: 'values',
        name: '价值观探索面试',
        description: '挖掘角色的核心价值观和信念',
        questionCount: this.questionSets.get('values')?.length || 0
      },
      {
        id: 'emotions',
        name: '情感关系面试',
        description: '了解角色的情感需求和人际关系模式',
        questionCount: this.questionSets.get('emotions')?.length || 0
      },
      {
        id: 'fears',
        name: '恐惧与欲望面试',
        description: '探索角色的深层动机和恐惧',
        questionCount: this.questionSets.get('fears')?.length || 0
      },
      {
        id: 'behavior',
        name: '行为模式面试',
        description: '了解角色在不同情况下的行为反应',
        questionCount: this.questionSets.get('behavior')?.length || 0
      },
      {
        id: 'past',
        name: '过去经历面试',
        description: '了解塑造角色的重要经历',
        questionCount: this.questionSets.get('past')?.length || 0
      },
      {
        id: 'future',
        name: '未来展望面试',
        description: '了解角色的期望和计划',
        questionCount: this.questionSets.get('future')?.length || 0
      },
      {
        id: 'scenarios',
        name: '情境应对面试',
        description: '测试角色在特定情境下的反应',
        questionCount: this.questionSets.get('scenarios')?.length || 0
      }
    ];
  }

  // 开始面试
  async startInterview(characterId: string, interviewType: string): Promise<InterviewSession> {
    const questions = this.questionSets.get(interviewType);
    if (!questions) {
      throw new Error(`未找到面试类型: ${interviewType}`);
    }

    const session: InterviewSession = {
      id: generateId(),
      characterId,
      interviewType,
      questions: [...questions],
      answers: [],
      startTime: new Date(),
      status: 'in_progress'
    };

    await this.storage.set(session.id, session);
    return session;
  }

  // 回答问题
  async answerQuestion(sessionId: string, questionId: string, answer: string, notes?: string): Promise<void> {
    const session = await this.storage.get<InterviewSession>(sessionId);
    if (!session) {
      throw new Error('面试会话不存在');
    }

    const answerRecord: InterviewAnswer = {
      questionId,
      answer,
      timestamp: new Date(),
      notes
    };

    session.answers.push(answerRecord);
    await this.storage.set(sessionId, session);
  }

  // 获取下一个问题
  async getNextQuestion(sessionId: string): Promise<InterviewQuestion | null> {
    const session = await this.storage.get<InterviewSession>(sessionId);
    if (!session) return null;

    const answeredQuestionIds = new Set(session.answers.map(a => a.questionId));
    return session.questions.find(q => !answeredQuestionIds.has(q.id)) || null;
  }

  // 获取面试进度
  async getInterviewProgress(sessionId: string): Promise<{
    total: number;
    answered: number;
    percentage: number;
  }> {
    const session = await this.storage.get<InterviewSession>(sessionId);
    if (!session) {
      return { total: 0, answered: 0, percentage: 0 };
    }

    const total = session.questions.length;
    const answered = session.answers.length;
    const percentage = total > 0 ? (answered / total) * 100 : 0;

    return { total, answered, percentage };
  }

  // 完成面试
  async completeInterview(sessionId: string): Promise<InterviewSession | null> {
    const session = await this.storage.get<InterviewSession>(sessionId);
    if (!session) return null;

    session.status = 'completed';
    session.endTime = new Date();

    await this.storage.set(sessionId, session);
    return session;
  }

  // 暂停面试
  async pauseInterview(sessionId: string): Promise<void> {
    const session = await this.storage.get<InterviewSession>(sessionId);
    if (!session) return;

    session.status = 'paused';
    await this.storage.set(sessionId, session);
  }

  // 恢复面试
  async resumeInterview(sessionId: string): Promise<void> {
    const session = await this.storage.get<InterviewSession>(sessionId);
    if (!session) return;

    session.status = 'in_progress';
    await this.storage.set(sessionId, session);
  }

  // 获取角色的所有面试会话
  async getCharacterInterviews(characterId: string): Promise<InterviewSession[]> {
    const allSessions = await this.storage.getAll<InterviewSession>();
    return allSessions.filter(session => session.characterId === characterId);
  }

  // 获取面试会话
  async getInterviewSession(sessionId: string): Promise<InterviewSession | null> {
    return await this.storage.get<InterviewSession>(sessionId);
  }

  // 删除面试会话
  async deleteInterview(sessionId: string): Promise<boolean> {
    try {
      await this.storage.remove(sessionId);
      return true;
    } catch (error) {
      console.error('删除面试会话失败:', error);
      return false;
    }
  }

  // 生成面试报告
  async generateInterviewReport(sessionId: string): Promise<{
    characterId: string;
    interviewType: string;
    startTime: Date;
    endTime?: Date;
    totalQuestions: number;
    answeredQuestions: number;
    completionRate: number;
    keyInsights: string[];
    answers: InterviewAnswer[];
  } | null> {
    const session = await this.storage.get<InterviewSession>(sessionId);
    if (!session) return null;

    const keyInsights = this.extractKeyInsights(session);

    return {
      characterId: session.characterId,
      interviewType: session.interviewType,
      startTime: session.startTime,
      endTime: session.endTime,
      totalQuestions: session.questions.length,
      answeredQuestions: session.answers.length,
      completionRate: (session.answers.length / session.questions.length) * 100,
      keyInsights,
      answers: session.answers
    };
  }

  private extractKeyInsights(session: InterviewSession): string[] {
    const insights: string[] = [];

    // 分析回答长度
    const avgAnswerLength = session.answers.reduce((sum, answer) => sum + answer.answer.length, 0) / session.answers.length;
    if (avgAnswerLength > 100) {
      insights.push('角色表达详细，善于阐述观点');
    } else if (avgAnswerLength < 30) {
      insights.push('角色表达简洁，可能较为内向');
    }

    // 分析情感词汇
    const emotionalWords = ['害怕', '恐惧', '担心', '焦虑', '开心', '快乐', '兴奋', '愤怒', '生气', '悲伤'];
    const emotionCount = session.answers.reduce((count, answer) => {
      return count + emotionalWords.filter(word => answer.answer.includes(word)).length;
    }, 0);

    if (emotionCount > session.answers.length * 0.3) {
      insights.push('角色情感丰富，感情表达直接');
    }

    // 分析价值观关键词
    const valueWords = ['正义', '公平', '自由', '家庭', '朋友', '成功', '金钱', '权力'];
    const valueCount = session.answers.reduce((count, answer) => {
      return count + valueWords.filter(word => answer.answer.includes(word)).length;
    }, 0);

    if (valueCount > 0) {
      insights.push('角色有明确的价值观体系');
    }

    return insights;
  }
}