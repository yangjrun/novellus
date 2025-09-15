import React, { useState, useEffect } from 'react';
import { InterviewSession, InterviewQuestion, InterviewAnswer } from '@types/index';
import { InterviewService } from '@services/interviewService';
import './InterviewInterface.css';

interface InterviewInterfaceProps {
  characterId: string;
  onComplete: (session: InterviewSession) => void;
  onCancel: () => void;
}

export const InterviewInterface: React.FC<InterviewInterfaceProps> = ({
  characterId,
  onComplete,
  onCancel
}) => {
  const [interviewService] = useState(new InterviewService());
  const [availableTypes, setAvailableTypes] = useState<Array<{ id: string; name: string; description: string; questionCount: number }>>([]);
  const [selectedType, setSelectedType] = useState<string>('');
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<InterviewQuestion | null>(null);
  const [answer, setAnswer] = useState('');
  const [notes, setNotes] = useState('');
  const [progress, setProgress] = useState({ total: 0, answered: 0, percentage: 0 });
  const [isStarted, setIsStarted] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const [showNotes, setShowNotes] = useState(false);

  useEffect(() => {
    loadAvailableTypes();
  }, []);

  const loadAvailableTypes = () => {
    const types = interviewService.getAvailableInterviewTypes();
    setAvailableTypes(types);
  };

  const startInterview = async () => {
    if (!selectedType) return;

    try {
      const newSession = await interviewService.startInterview(characterId, selectedType);
      setSession(newSession);
      setIsStarted(true);

      const nextQuestion = await interviewService.getNextQuestion(newSession.id);
      setCurrentQuestion(nextQuestion);

      updateProgress(newSession.id);
    } catch (error) {
      console.error('开始面试失败:', error);
      alert('开始面试失败，请重试');
    }
  };

  const updateProgress = async (sessionId: string) => {
    const progressData = await interviewService.getInterviewProgress(sessionId);
    setProgress(progressData);
  };

  const submitAnswer = async () => {
    if (!session || !currentQuestion || !answer.trim()) return;

    try {
      await interviewService.answerQuestion(session.id, currentQuestion.id, answer, notes);

      const nextQuestion = await interviewService.getNextQuestion(session.id);
      if (nextQuestion) {
        setCurrentQuestion(nextQuestion);
        setAnswer('');
        setNotes('');
        await updateProgress(session.id);
      } else {
        // 面试完成
        const completedSession = await interviewService.completeInterview(session.id);
        if (completedSession) {
          setSession(completedSession);
          setIsCompleted(true);
          onComplete(completedSession);
        }
      }
    } catch (error) {
      console.error('提交答案失败:', error);
      alert('提交答案失败，请重试');
    }
  };

  const pauseInterview = async () => {
    if (!session) return;

    try {
      await interviewService.pauseInterview(session.id);
      onCancel();
    } catch (error) {
      console.error('暂停面试失败:', error);
    }
  };

  const skipQuestion = async () => {
    if (!session || !currentQuestion) return;

    await submitAnswer(); // 以空答案提交
  };

  if (!isStarted) {
    return (
      <div className="interview-setup">
        <div className="setup-header">
          <h2>角色面试工具</h2>
          <p>通过面试深入了解角色的内心世界和行为模式</p>
        </div>

        <div className="interview-types">
          <h3>选择面试类型</h3>
          <div className="types-grid">
            {availableTypes.map(type => (
              <div
                key={type.id}
                className={`type-card ${selectedType === type.id ? 'selected' : ''}`}
                onClick={() => setSelectedType(type.id)}
              >
                <h4>{type.name}</h4>
                <p>{type.description}</p>
                <div className="question-count">{type.questionCount} 个问题</div>
              </div>
            ))}
          </div>
        </div>

        <div className="setup-actions">
          <button onClick={onCancel} className="cancel-btn">
            取消
          </button>
          <button
            onClick={startInterview}
            className="start-btn"
            disabled={!selectedType}
          >
            开始面试
          </button>
        </div>
      </div>
    );
  }

  if (isCompleted) {
    return (
      <div className="interview-completed">
        <div className="completion-header">
          <h2>面试完成</h2>
          <div className="completion-stats">
            <div className="stat">
              <span className="stat-value">{progress.answered}</span>
              <span className="stat-label">回答问题</span>
            </div>
            <div className="stat">
              <span className="stat-value">{Math.round(progress.percentage)}%</span>
              <span className="stat-label">完成度</span>
            </div>
          </div>
        </div>

        <div className="completion-message">
          <p>恭喜！你已经完成了 {availableTypes.find(t => t.id === selectedType)?.name}。</p>
          <p>通过这次面试，你对角色有了更深入的了解。</p>
        </div>

        <div className="completion-actions">
          <button onClick={onCancel} className="done-btn">
            完成
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="interview-interface">
      <div className="interview-header">
        <div className="header-info">
          <h2>{availableTypes.find(t => t.id === selectedType)?.name}</h2>
          <div className="progress-info">
            问题 {progress.answered + 1} / {progress.total}
          </div>
        </div>

        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${progress.percentage}%` }}
          ></div>
        </div>
      </div>

      {currentQuestion && (
        <div className="question-section">
          <div className="question-category">
            {currentQuestion.category}
          </div>

          <div className="question-content">
            <h3>{currentQuestion.question}</h3>

            {currentQuestion.type === 'choice' && currentQuestion.choices && (
              <div className="choice-options">
                {currentQuestion.choices.map((choice, index) => (
                  <label key={index} className="choice-option">
                    <input
                      type="radio"
                      name="choice"
                      value={choice}
                      checked={answer === choice}
                      onChange={(e) => setAnswer(e.target.value)}
                    />
                    <span>{choice}</span>
                  </label>
                ))}
              </div>
            )}

            {currentQuestion.type === 'text' && (
              <div className="text-answer">
                <textarea
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  placeholder="请以角色的身份回答这个问题..."
                  rows={6}
                />
              </div>
            )}

            {currentQuestion.type === 'scale' && (
              <div className="scale-input">
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={answer || '5'}
                  onChange={(e) => setAnswer(e.target.value)}
                />
                <div className="scale-labels">
                  <span>1 (完全不同意)</span>
                  <span>当前值: {answer || '5'}</span>
                  <span>10 (完全同意)</span>
                </div>
              </div>
            )}

            <div className="notes-section">
              <button
                className="notes-toggle"
                onClick={() => setShowNotes(!showNotes)}
              >
                {showNotes ? '隐藏' : '添加'}备注
              </button>

              {showNotes && (
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="添加关于这个回答的备注或思考..."
                  rows={3}
                  className="notes-input"
                />
              )}
            </div>
          </div>

          <div className="question-actions">
            <button onClick={pauseInterview} className="pause-btn">
              暂停面试
            </button>

            <button onClick={skipQuestion} className="skip-btn">
              跳过
            </button>

            <button
              onClick={submitAnswer}
              className="submit-btn"
              disabled={!answer.trim() && currentQuestion.type !== 'scale'}
            >
              {progress.answered + 1 === progress.total ? '完成面试' : '下一题'}
            </button>
          </div>
        </div>
      )}

      <div className="interview-tips">
        <h4>💡 面试提示</h4>
        <ul>
          <li>完全从角色的角度思考和回答</li>
          <li>保持答案与已知角色信息的一致性</li>
          <li>不满足于表面回答，深入思考"为什么"</li>
          <li>可以添加备注记录新发现的角色特质</li>
        </ul>
      </div>
    </div>
  );
};