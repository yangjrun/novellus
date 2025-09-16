import React, { useState, useEffect } from 'react';
import { Character, Project } from '../types/index';
import { CharacterService } from '@services/characterService';
import { generateId } from '@utils/storage';
import './ProjectManager.css';

interface ProjectManagerProps {
  onToolSelect: (tool: 'character' | 'interview' | 'checklist' | 'diagnostic' | 'narrative' | 'world-builder' | 'scene-creator') => void;
  onCharacterSelect: (character: Character) => void;
  onProjectSelect: (projectId: string) => void;
}

export const ProjectManager: React.FC<ProjectManagerProps> = ({
  onToolSelect,
  onCharacterSelect,
  onProjectSelect
}) => {
  const [characterService] = useState(new CharacterService());
  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCharacters();
  }, []);

  const loadCharacters = async () => {
    try {
      const allCharacters = await characterService.getAllCharacters();
      setCharacters(allCharacters);
    } catch (error) {
      console.error('加载角色失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCharacter = () => {
    onToolSelect('character');
  };

  const handleEditCharacter = (character: Character) => {
    onCharacterSelect(character);
    onToolSelect('character');
  };

  const handleInterviewCharacter = (character: Character) => {
    onCharacterSelect(character);
    onToolSelect('interview');
  };

  const handleDeleteCharacter = async (characterId: string) => {
    if (window.confirm('确定要删除这个角色吗？此操作不可撤销。')) {
      try {
        await characterService.deleteCharacter(characterId);
        await loadCharacters();
      } catch (error) {
        console.error('删除角色失败:', error);
        alert('删除失败，请重试');
      }
    }
  };

  const handleCreateProject = () => {
    const projectId = generateId();
    onProjectSelect(projectId);
  };

  if (loading) {
    return (
      <div className="project-manager loading">
        <div className="loading-spinner"></div>
        <p>正在加载...</p>
      </div>
    );
  }

  return (
    <div className="project-manager">
      <div className="welcome-section">
        <h1>欢迎使用 Novellus 创作工具</h1>
        <p>专业的小说创作辅助工具，让你的创作更加高效和有序</p>
      </div>

      <div className="tools-grid">
        {/* Phase 1 增强工具 */}
        <div className="tool-category phase1-tools">
          <h2>🚀 Phase 1 增强工具</h2>
          <div className="tools-row">
            <div className="tool-card enhanced" onClick={() => {
              handleCreateProject();
              onToolSelect('narrative');
            }}>
              <div className="tool-icon">📚</div>
              <h3>叙事结构构建</h3>
              <p>选择经典故事结构，规划情节节点，可视化故事发展</p>
              <div className="tool-stats">
                <span className="new-badge">新功能</span>
                6种经典结构
              </div>
            </div>

            <div className="tool-card enhanced" onClick={() => {
              handleCreateProject();
              onToolSelect('character');
            }}>
              <div className="tool-icon">🎭</div>
              <h3>角色创建</h3>
              <p>统一角色创建器，支持快速、引导、专业三种模式</p>
              <div className="tool-stats">
                <span className="new-badge">新功能</span>
                AI智能建议
              </div>
            </div>
          </div>

          <div className="tools-row">
            <div className="tool-card enhanced" onClick={() => {
              handleCreateProject();
              onToolSelect('world-builder');
            }}>
              <div className="tool-icon">🌍</div>
              <h3>智能世界构建</h3>
              <p>创建完整的世界观，文化系统，地理环境和历史背景</p>
              <div className="tool-stats">
                <span className="new-badge">新功能</span>
                6种世界类型
              </div>
            </div>

            <div className="tool-card enhanced" onClick={() => {
              handleCreateProject();
              onToolSelect('scene-creator');
            }}>
              <div className="tool-icon">🎬</div>
              <h3>多维场景创作</h3>
              <p>感官场景构建器，氛围营造工具，多感官体验设计</p>
              <div className="tool-stats">
                <span className="new-badge">新功能</span>
                5种场景类型
              </div>
            </div>
          </div>
        </div>

        {/* 基础工具 */}
        <div className="tool-category">
          <h2>📝 基础创作工具</h2>
          <div className="tools-row">

            <div className="tool-card" onClick={() => onToolSelect('interview')}>
              <div className="tool-icon">💬</div>
              <h3>角色面试</h3>
              <p>通过深度面试了解角色内心，完善角色设定</p>
              <div className="tool-stats">
                8种面试类型
              </div>
            </div>
          </div>

          <div className="tools-row">
            <div className="tool-card" onClick={() => {
              handleCreateProject();
              onToolSelect('checklist');
            }}>
              <div className="tool-icon">✅</div>
              <h3>情节检查清单</h3>
              <p>系统化检查故事结构，确保情节完整性</p>
              <div className="tool-stats">
                3套专业模板
              </div>
            </div>

            <div className="tool-card" onClick={() => {
              handleCreateProject();
              onToolSelect('diagnostic');
            }}>
              <div className="tool-icon">🔍</div>
              <h3>故事诊断</h3>
              <p>快速发现故事问题，获得针对性改进建议</p>
              <div className="tool-stats">
                7类诊断测试
              </div>
            </div>
          </div>
        </div>
      </div>

      {characters.length > 0 && (
        <div className="characters-section">
          <h2>📚 我的角色</h2>
          <div className="characters-grid">
            {characters.map(character => (
              <div key={character.id} className="character-card">
                <div className="character-header">
                  <h3>{character.basicInfo.name || '未命名角色'}</h3>
                  <div className="character-type">
                    {character.storyRole.characterType === 'protagonist' && '主角'}
                    {character.storyRole.characterType === 'antagonist' && '反角'}
                    {character.storyRole.characterType === 'supporting' && '配角'}
                    {character.storyRole.characterType === 'minor' && '次要角色'}
                  </div>
                </div>

                <div className="character-info">
                  <div className="character-detail">
                    <span className="label">职业:</span>
                    <span>{character.basicInfo.occupation || '未设定'}</span>
                  </div>
                  <div className="character-detail">
                    <span className="label">年龄:</span>
                    <span>{character.basicInfo.age || '未设定'}</span>
                  </div>
                  <div className="character-detail">
                    <span className="label">特质:</span>
                    <span>{character.personality.coreTraits.slice(0, 2).join(', ') || '未设定'}</span>
                  </div>
                </div>

                <div className="character-actions">
                  <button
                    className="btn-edit"
                    onClick={() => handleEditCharacter(character)}
                  >
                    编辑
                  </button>
                  <button
                    className="btn-interview"
                    onClick={() => handleInterviewCharacter(character)}
                  >
                    面试
                  </button>
                  <button
                    className="btn-delete"
                    onClick={() => handleDeleteCharacter(character.id)}
                  >
                    删除
                  </button>
                </div>

                <div className="character-meta">
                  创建于 {new Date(character.createdAt).toLocaleDateString('zh-CN')}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="quick-start">
        <h2>🚀 快速开始</h2>
        <div className="quick-start-steps">
          <div className="step">
            <div className="step-number">1</div>
            <div className="step-content">
              <h3>创建角色</h3>
              <p>使用统一角色创建器开始你的创作之旅</p>
              <button onClick={handleCreateCharacter} className="step-btn">
                开始创建
              </button>
            </div>
          </div>

          <div className="step">
            <div className="step-number">2</div>
            <div className="step-content">
              <h3>深度面试</h3>
              <p>通过角色面试工具深入了解角色内心</p>
              <button
                onClick={() => onToolSelect('interview')}
                className="step-btn"
                disabled={characters.length === 0}
              >
                开始面试
              </button>
            </div>
          </div>

          <div className="step">
            <div className="step-number">3</div>
            <div className="step-content">
              <h3>检查情节</h3>
              <p>使用检查清单确保故事结构完整</p>
              <button
                onClick={() => {
                  handleCreateProject();
                  onToolSelect('checklist');
                }}
                className="step-btn"
              >
                开始检查
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="features-highlight">
        <h2>✨ 核心特性</h2>
        <div className="features-grid">
          <div className="feature-item">
            <div className="feature-icon">💾</div>
            <h3>本地存储</h3>
            <p>所有数据保存在本地，保护你的创作隐私</p>
          </div>
          <div className="feature-item">
            <div className="feature-icon">📤</div>
            <h3>多格式导出</h3>
            <p>支持导出为 JSON、PDF、Word 等多种格式</p>
          </div>
          <div className="feature-item">
            <div className="feature-icon">🔧</div>
            <h3>模块化设计</h3>
            <p>每个工具独立运行，可根据需要灵活使用</p>
          </div>
          <div className="feature-item">
            <div className="feature-icon">📱</div>
            <h3>响应式界面</h3>
            <p>完美适配桌面和移动设备</p>
          </div>
        </div>
      </div>
    </div>
  );
};