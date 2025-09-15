import React, { useState } from 'react';
import { Character, InterviewSession, ProjectChecklist } from '@types/index';
import { CharacterForm } from '@components/CharacterForm';
import { InterviewInterface } from '@components/InterviewInterface';
import { ChecklistInterface } from '@components/ChecklistInterface';
import { DiagnosticInterface } from '@components/DiagnosticInterface';
import { ProjectManager } from '@components/ProjectManager';
import './App.css';

type ActiveTool = 'home' | 'character' | 'interview' | 'checklist' | 'diagnostic';

interface AppState {
  activeTool: ActiveTool;
  currentCharacter?: Character;
  currentProject?: string;
}

function App() {
  const [state, setState] = useState<AppState>({
    activeTool: 'home'
  });

  const handleToolSwitch = (tool: ActiveTool) => {
    setState(prev => ({ ...prev, activeTool: tool }));
  };

  const handleCharacterSave = (character: Character) => {
    setState(prev => ({ ...prev, activeTool: 'home' }));
  };

  const handleInterviewComplete = (session: InterviewSession) => {
    setState(prev => ({ ...prev, activeTool: 'home' }));
  };

  const handleCancel = () => {
    setState(prev => ({ ...prev, activeTool: 'home' }));
  };

  const renderActiveTool = () => {
    switch (state.activeTool) {
      case 'character':
        return (
          <CharacterForm
            character={state.currentCharacter}
            onSave={handleCharacterSave}
            onCancel={handleCancel}
          />
        );

      case 'interview':
        if (!state.currentCharacter?.id) {
          return (
            <div className="error-message">
              <h3>需要先选择角色</h3>
              <p>请先创建或选择一个角色进行面试</p>
              <button onClick={() => handleToolSwitch('home')}>返回首页</button>
            </div>
          );
        }
        return (
          <InterviewInterface
            characterId={state.currentCharacter.id}
            onComplete={handleInterviewComplete}
            onCancel={handleCancel}
          />
        );

      case 'checklist':
        if (!state.currentProject) {
          return (
            <div className="error-message">
              <h3>需要先选择项目</h3>
              <p>请先创建或选择一个项目使用检查清单</p>
              <button onClick={() => handleToolSwitch('home')}>返回首页</button>
            </div>
          );
        }
        return (
          <ChecklistInterface
            projectId={state.currentProject}
            onComplete={handleCancel}
            onCancel={handleCancel}
          />
        );

      case 'diagnostic':
        if (!state.currentProject) {
          return (
            <div className="error-message">
              <h3>需要先选择项目</h3>
              <p>请先创建或选择一个项目使用诊断工具</p>
              <button onClick={() => handleToolSwitch('home')}>返回首页</button>
            </div>
          );
        }
        return (
          <DiagnosticInterface
            projectId={state.currentProject}
            onComplete={handleCancel}
          />
        );

      default:
        return (
          <ProjectManager
            onToolSelect={handleToolSwitch}
            onCharacterSelect={(character) => setState(prev => ({ ...prev, currentCharacter: character }))}
            onProjectSelect={(projectId) => setState(prev => ({ ...prev, currentProject: projectId }))}
          />
        );
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1 onClick={() => handleToolSwitch('home')} className="app-title">
            📚 Novellus 创作工具
          </h1>

          <nav className="main-nav">
            <button
              className={state.activeTool === 'home' ? 'active' : ''}
              onClick={() => handleToolSwitch('home')}
            >
              🏠 首页
            </button>
            <button
              className={state.activeTool === 'character' ? 'active' : ''}
              onClick={() => handleToolSwitch('character')}
            >
              👤 角色工作表
            </button>
            <button
              className={state.activeTool === 'interview' ? 'active' : ''}
              onClick={() => handleToolSwitch('interview')}
            >
              💬 角色面试
            </button>
            <button
              className={state.activeTool === 'checklist' ? 'active' : ''}
              onClick={() => handleToolSwitch('checklist')}
            >
              ✅ 情节检查
            </button>
            <button
              className={state.activeTool === 'diagnostic' ? 'active' : ''}
              onClick={() => handleToolSwitch('diagnostic')}
            >
              🔍 故事诊断
            </button>
          </nav>
        </div>
      </header>

      <main className="app-main">
        {renderActiveTool()}
      </main>

      <footer className="app-footer">
        <p>&copy; 2024 Novellus 创作工具 - 让创作更专业</p>
      </footer>
    </div>
  );
}

export default App;