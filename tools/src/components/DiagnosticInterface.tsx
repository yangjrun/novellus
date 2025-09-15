import React, { useState, useEffect } from 'react';
import { DiagnosticResult, DiagnosticTest } from '@types/index';
import { DiagnosticService } from '@services/diagnosticService';
import { CharacterService } from '@services/characterService';
import './DiagnosticInterface.css';

interface DiagnosticInterfaceProps {
  projectId: string;
  onComplete: () => void;
}

export const DiagnosticInterface: React.FC<DiagnosticInterfaceProps> = ({
  projectId,
  onComplete
}) => {
  const [diagnosticService] = useState(new DiagnosticService());
  const [characterService] = useState(new CharacterService());
  const [availableTests, setAvailableTests] = useState<DiagnosticTest[]>([]);
  const [selectedTests, setSelectedTests] = useState<string[]>([]);
  const [results, setResults] = useState<DiagnosticResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [currentInput, setCurrentInput] = useState<Record<string, any>>({});

  useEffect(() => {
    loadAvailableTests();
  }, []);

  const loadAvailableTests = () => {
    const tests = diagnosticService.getAvailableTests();
    setAvailableTests(tests);
  };

  const handleTestSelection = (testId: string, selected: boolean) => {
    if (selected) {
      setSelectedTests(prev => [...prev, testId]);
    } else {
      setSelectedTests(prev => prev.filter(id => id !== testId));
    }
  };

  const collectProjectData = async () => {
    try {
      const characters = await characterService.getAllCharacters();
      const projectCharacters = characters.filter(c => c.projectId === projectId);

      return {
        characters: projectCharacters,
        summary: currentInput.summary || '',
        // 其他项目数据...
      };
    } catch (error) {
      console.error('收集项目数据失败:', error);
      return { characters: [], summary: '' };
    }
  };

  const runSelectedTests = async () => {
    if (selectedTests.length === 0) {
      alert('请至少选择一个测试');
      return;
    }

    setIsRunning(true);
    setResults([]);

    try {
      const projectData = await collectProjectData();
      const testResults = diagnosticService.runBatch(selectedTests, projectData);
      setResults(testResults);
    } catch (error) {
      console.error('诊断失败:', error);
      alert('诊断失败，请重试');
    } finally {
      setIsRunning(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'excellent': return '#48bb78';
      case 'good': return '#68d391';
      case 'warning': return '#ed8936';
      case 'critical': return '#f56565';
      default: return '#a0aec0';
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

  const groupTestsByCategory = (tests: DiagnosticTest[]) => {
    return tests.reduce((groups, test) => {
      const category = test.category;
      if (!groups[category]) {
        groups[category] = [];
      }
      groups[category].push(test);
      return groups;
    }, {} as Record<string, DiagnosticTest[]>);
  };

  const getCategoryName = (category: string) => {
    const names: Record<string, string> = {
      'structure': '结构检查',
      'character': '角色检查',
      'dialogue': '对话检查',
      'pacing': '节奏检查',
      'consistency': '一致性检查'
    };
    return names[category] || category;
  };

  return (
    <div className="diagnostic-interface">
      <div className="diagnostic-header">
        <h2>故事诊断工具</h2>
        <p>快速发现故事中的潜在问题，获得专业的改进建议</p>
      </div>

      {/* 输入数据区域 */}
      <div className="input-section">
        <h3>提供诊断数据</h3>
        <div className="input-group">
          <label>故事概述 *</label>
          <textarea
            value={currentInput.summary || ''}
            onChange={(e) => setCurrentInput(prev => ({ ...prev, summary: e.target.value }))}
            placeholder="请简要描述你的故事情节（用于故事核心测试）..."
            rows={4}
            className="story-summary-input"
          />
          <div className="input-help">
            用30秒到1分钟时间描述你的故事，包含主角、冲突、行动和结果
          </div>
        </div>
      </div>

      {/* 测试选择区域 */}
      <div className="test-selection">
        <h3>选择诊断测试</h3>
        <div className="test-categories">
          {Object.entries(groupTestsByCategory(availableTests)).map(([category, tests]) => (
            <div key={category} className="test-category">
              <h4>{getCategoryName(category)}</h4>
              <div className="tests-grid">
                {tests.map(test => (
                  <div key={test.id} className="test-card">
                    <label className="test-label">
                      <input
                        type="checkbox"
                        checked={selectedTests.includes(test.id)}
                        onChange={(e) => handleTestSelection(test.id, e.target.checked)}
                      />
                      <div className="test-info">
                        <h5>{test.name}</h5>
                        <p>{test.description}</p>
                        <div className="test-meta">
                          <span className="test-time">⏱️ {test.timeEstimate}分钟</span>
                        </div>
                      </div>
                    </label>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="test-actions">
          <button
            onClick={runSelectedTests}
            disabled={selectedTests.length === 0 || isRunning || !currentInput.summary?.trim()}
            className="run-tests-btn"
          >
            {isRunning ? (
              <>
                <div className="loading-spinner"></div>
                运行中...
              </>
            ) : (
              `运行选中的测试 (${selectedTests.length})`
            )}
          </button>
        </div>
      </div>

      {/* 诊断结果 */}
      {results.length > 0 && (
        <div className="diagnostic-results">
          <h3>诊断结果</h3>

          {/* 整体概览 */}
          <div className="results-overview">
            <div className="overview-stats">
              <div className="stat-item">
                <span className="stat-value">{results.length}</span>
                <span className="stat-label">已完成测试</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">
                  {Math.round(results.reduce((sum, r) => sum + r.score, 0) / results.length)}
                </span>
                <span className="stat-label">平均分数</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">
                  {results.reduce((sum, r) => sum + r.issues.length, 0)}
                </span>
                <span className="stat-label">发现问题</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">
                  {results.reduce((sum, r) => sum + r.suggestions.length, 0)}
                </span>
                <span className="stat-label">改进建议</span>
              </div>
            </div>
          </div>

          {/* 详细结果 */}
          <div className="results-details">
            {results.map(result => (
              <div key={result.testId} className="result-card">
                <div className="result-header">
                  <div className="result-title">
                    <h4>{availableTests.find(t => t.id === result.testId)?.name}</h4>
                    <div className="result-score">
                      <div
                        className="score-circle"
                        style={{ backgroundColor: getStatusColor(result.status) }}
                      >
                        {result.score}
                      </div>
                      <span className="status-text">{getStatusText(result.status)}</span>
                    </div>
                  </div>
                </div>

                {result.issues.length > 0 && (
                  <div className="issues-section">
                    <h5>发现的问题</h5>
                    <div className="issues-list">
                      {result.issues.map((issue, index) => (
                        <div key={index} className={`issue-item ${issue.type} severity-${issue.severity}`}>
                          <span className="issue-icon">
                            {issue.type === 'error' ? '❌' : issue.type === 'warning' ? '⚠️' : 'ℹ️'}
                          </span>
                          <div className="issue-content">
                            <span className="issue-message">{issue.message}</span>
                            {issue.location && (
                              <span className="issue-location">位置: {issue.location}</span>
                            )}
                          </div>
                          <span className={`severity-badge severity-${issue.severity}`}>
                            {issue.severity === 'high' && '高'}
                            {issue.severity === 'medium' && '中'}
                            {issue.severity === 'low' && '低'}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {result.suggestions.length > 0 && (
                  <div className="suggestions-section">
                    <h5>改进建议</h5>
                    <ul className="suggestions-list">
                      {result.suggestions.map((suggestion, index) => (
                        <li key={index}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="result-meta">
                  测试时间: {new Date(result.timestamp).toLocaleString('zh-CN')}
                </div>
              </div>
            ))}
          </div>

          <div className="results-actions">
            <button onClick={() => setResults([])} className="clear-results-btn">
              清除结果
            </button>
            <button onClick={onComplete} className="complete-btn">
              完成诊断
            </button>
          </div>
        </div>
      )}

      <div className="diagnostic-tips">
        <h4>💡 诊断提示</h4>
        <ul>
          <li>建议先进行结构检查，确保故事框架稳固</li>
          <li>角色检查能帮助发现角色塑造问题</li>
          <li>对话检查关注角色声音的独特性</li>
          <li>定期进行诊断，及时发现和解决问题</li>
        </ul>
      </div>
    </div>
  );
};