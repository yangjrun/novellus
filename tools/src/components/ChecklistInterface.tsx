import React, { useState, useEffect } from 'react';
import { ProjectChecklist, ChecklistProgress, ChecklistTemplate } from '../types/index';
import { ChecklistService } from '@services/checklistService';
import './ChecklistInterface.css';

interface ChecklistInterfaceProps {
  projectId: string;
  onComplete: () => void;
  onCancel: () => void;
}

export const ChecklistInterface: React.FC<ChecklistInterfaceProps> = ({
  projectId,
  onComplete,
  onCancel
}) => {
  const [checklistService] = useState(new ChecklistService());
  const [availableTemplates, setAvailableTemplates] = useState<ChecklistTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [checklist, setChecklist] = useState<ProjectChecklist | null>(null);
  const [activeCategory, setActiveCategory] = useState<string>('');
  const [progress, setProgress] = useState<ChecklistProgress>({ total: 0, completed: 0, percentage: 0 });
  const [isSetup, setIsSetup] = useState(true);
  const [showNotes, setShowNotes] = useState<Record<string, boolean>>({});

  useEffect(() => {
    loadAvailableTemplates();
  }, []);

  const loadAvailableTemplates = () => {
    const templates = checklistService.getAvailableTemplates();
    setAvailableTemplates(templates);
  };

  const createChecklist = async () => {
    if (!selectedTemplate) return;

    try {
      const newChecklist = await checklistService.createProjectChecklist(projectId, selectedTemplate);
      setChecklist(newChecklist);
      setProgress(checklistService.getChecklistProgress(newChecklist));

      if (newChecklist.categories.length > 0) {
        setActiveCategory(newChecklist.categories[0].id);
      }

      setIsSetup(false);
    } catch (error) {
      console.error('创建检查清单失败:', error);
      alert('创建检查清单失败，请重试');
    }
  };

  const handleItemCheck = async (itemId: string, checked: boolean) => {
    if (!checklist) return;

    try {
      await checklistService.updateChecklistItem(checklist.id, itemId, { checked });

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
      setProgress(checklistService.getChecklistProgress(updatedChecklist));
    } catch (error) {
      console.error('更新检查项失败:', error);
    }
  };

  const handleItemNotes = async (itemId: string, notes: string) => {
    if (!checklist) return;

    try {
      await checklistService.updateChecklistItem(checklist.id, itemId, { notes });

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
    } catch (error) {
      console.error('更新备注失败:', error);
    }
  };

  const toggleNotes = (itemId: string) => {
    setShowNotes(prev => ({
      ...prev,
      [itemId]: !prev[itemId]
    }));
  };

  const generateReport = () => {
    if (!checklist) return;

    const report = checklistService.generateChecklistReport(checklist);

    // 简单的报告展示
    let reportText = `检查清单报告\n\n`;
    reportText += `总体进度: ${report.summary.completed}/${report.summary.total} (${Math.round(report.summary.percentage)}%)\n\n`;

    reportText += `分类详情:\n`;
    report.categoryBreakdown.forEach(category => {
      reportText += `- ${category.category}: ${category.progress.completed}/${category.progress.total}\n`;
    });

    reportText += `\n建议:\n`;
    report.recommendations.forEach(rec => {
      reportText += `- ${rec}\n`;
    });

    alert(reportText);
  };

  if (isSetup) {
    return (
      <div className="checklist-setup">
        <div className="setup-header">
          <h2>情节检查清单</h2>
          <p>选择合适的检查模板，系统化验证你的故事结构</p>
        </div>

        <div className="template-selection">
          <h3>选择检查模板</h3>
          <div className="templates-grid">
            {availableTemplates.map(template => (
              <div
                key={template.id}
                className={`template-card ${selectedTemplate === template.id ? 'selected' : ''}`}
                onClick={() => setSelectedTemplate(template.id)}
              >
                <h4>{template.name}</h4>
                <p>{template.description}</p>
                <div className="template-stats">
                  {template.categories.length} 个分类，
                  {template.categories.reduce((sum, cat) => sum + cat.items.length, 0)} 个检查项
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="setup-actions">
          <button onClick={onCancel} className="cancel-btn">
            取消
          </button>
          <button
            onClick={createChecklist}
            className="create-btn"
            disabled={!selectedTemplate}
          >
            创建检查清单
          </button>
        </div>
      </div>
    );
  }

  if (!checklist) {
    return (
      <div className="checklist-loading">
        <div className="loading-spinner"></div>
        <p>正在加载检查清单...</p>
      </div>
    );
  }

  return (
    <div className="checklist-interface">
      <div className="checklist-header">
        <div className="header-info">
          <h2>{checklist.name}</h2>
          <p>{checklist.description}</p>
        </div>

        <div className="progress-section">
          <div className="progress-stats">
            <span className="progress-text">
              {progress.completed}/{progress.total} ({Math.round(progress.percentage)}%)
            </span>
          </div>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${progress.percentage}%` }}
            ></div>
          </div>
        </div>

        <div className="header-actions">
          <button onClick={generateReport} className="report-btn">
            生成报告
          </button>
          <button onClick={onComplete} className="complete-btn">
            完成
          </button>
        </div>
      </div>

      <div className="checklist-content">
        <div className="category-nav">
          {checklist.categories.map(category => {
            const categoryProgress = checklistService.getCategoryProgress(category);
            return (
              <button
                key={category.id}
                className={`category-btn ${activeCategory === category.id ? 'active' : ''}`}
                onClick={() => setActiveCategory(category.id)}
              >
                <span className="category-name">{category.name}</span>
                <span className="category-progress">
                  {categoryProgress.completed}/{categoryProgress.total}
                </span>
                <div className="category-progress-bar">
                  <div
                    className="category-progress-fill"
                    style={{ width: `${categoryProgress.percentage}%` }}
                  ></div>
                </div>
              </button>
            );
          })}
        </div>

        <div className="category-content">
          {checklist.categories
            .filter(category => category.id === activeCategory)
            .map(category => (
              <div key={category.id} className="category-section">
                <div className="category-header">
                  <h3>{category.name}</h3>
                  <p>{category.description}</p>
                </div>

                <div className="checklist-items">
                  {category.items.map(item => (
                    <div key={item.id} className={`checklist-item priority-${item.priority}`}>
                      <div className="item-header">
                        <label className="checkbox-label">
                          <input
                            type="checkbox"
                            checked={item.checked}
                            onChange={(e) => handleItemCheck(item.id, e.target.checked)}
                          />
                          <span className="checkmark"></span>
                          <div className="item-content">
                            <span className="item-title">{item.title}</span>
                            <span className={`priority-badge priority-${item.priority}`}>
                              {item.priority === 'high' && '高优先级'}
                              {item.priority === 'medium' && '中优先级'}
                              {item.priority === 'low' && '低优先级'}
                            </span>
                          </div>
                        </label>

                        <button
                          className="notes-toggle"
                          onClick={() => toggleNotes(item.id)}
                          title="添加备注"
                        >
                          📝
                        </button>
                      </div>

                      <p className="item-description">{item.description}</p>

                      {showNotes[item.id] && (
                        <div className="notes-section">
                          <textarea
                            value={item.notes || ''}
                            onChange={(e) => handleItemNotes(item.id, e.target.value)}
                            placeholder="添加备注或修改建议..."
                            rows={3}
                            className="notes-input"
                          />
                        </div>
                      )}

                      {item.notes && !showNotes[item.id] && (
                        <div className="existing-notes">
                          <strong>备注：</strong> {item.notes}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
        </div>
      </div>

      <div className="checklist-tips">
        <h4>💡 使用提示</h4>
        <ul>
          <li>按优先级依次检查，高优先级项目最重要</li>
          <li>可以添加备注记录发现的问题和修改建议</li>
          <li>定期生成报告查看整体进度和改进建议</li>
          <li>不同分类关注故事的不同方面，建议全面检查</li>
        </ul>
      </div>
    </div>
  );
};