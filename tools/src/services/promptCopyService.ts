import {
  GeneratedPrompt,
  PromptHistory,
  IPromptCopyService,
  IPromptHistoryService,
  PromptTemplate
} from '../types/prompt';

// Prompt复制服务
export class PromptCopyService implements IPromptCopyService {
  async copyToClipboard(content: string, format: 'plain' | 'markdown' | 'structured'): Promise<boolean> {
    try {
      let formattedContent = content;

      switch (format) {
        case 'markdown':
          formattedContent = this.formatAsMarkdown(content);
          break;
        case 'structured':
          formattedContent = this.formatAsStructured(content);
          break;
        default:
          formattedContent = content;
      }

      // 检查浏览器是否支持Clipboard API
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(formattedContent);
      } else {
        // 回退到传统方法
        this.fallbackCopyToClipboard(formattedContent);
      }

      // 显示成功提示
      this.showToast('Prompt已复制到剪贴板', 'success');

      // 记录使用统计
      this.trackUsage('copy', format);

      return true;
    } catch (error) {
      console.error('复制失败:', error);
      this.showToast('复制失败，请手动选择文本', 'error');
      return false;
    }
  }

  generatePrompt(template: PromptTemplate, variables: Record<string, any>): string {
    let content = '';

    // 按顺序组装各个部分
    const sortedSections = [...template.promptStructure.sections].sort((a, b) => a.order - b.order);

    sortedSections.forEach(section => {
      content += this.replaceVariables(section.content, variables) + '\n\n';
    });

    // 添加条件性部分
    if (template.promptStructure.conditionalSections) {
      template.promptStructure.conditionalSections.forEach(conditionalSection => {
        // 这里需要根据条件判断是否添加
        content += this.replaceVariables(conditionalSection.section.content, variables) + '\n\n';
      });
    }

    return content.trim();
  }

  exportPrompt(prompt: GeneratedPrompt, format: 'txt' | 'md' | 'json'): void {
    let content: string;
    let filename: string;
    let mimeType: string;

    switch (format) {
      case 'md':
        content = this.formatAsMarkdown(prompt.generatedContent);
        filename = `prompt_${prompt.template.category}_${Date.now()}.md`;
        mimeType = 'text/markdown';
        break;
      case 'json':
        content = JSON.stringify(prompt, null, 2);
        filename = `prompt_${prompt.template.category}_${Date.now()}.json`;
        mimeType = 'application/json';
        break;
      default:
        content = prompt.generatedContent;
        filename = `prompt_${prompt.template.category}_${Date.now()}.txt`;
        mimeType = 'text/plain';
    }

    this.downloadFile(content, filename, mimeType);
  }

  async sharePrompt(promptId: string): Promise<string> {
    try {
      // 实际项目中这里应该调用后端API生成分享链接
      const shareUrl = `${window.location.origin}/shared/prompt/${promptId}`;

      // 复制分享链接到剪贴板
      await navigator.clipboard.writeText(shareUrl);
      this.showToast('分享链接已复制到剪贴板', 'success');

      return shareUrl;
    } catch (error) {
      console.error('生成分享链接失败:', error);
      throw new Error('生成分享链接失败');
    }
  }

  formatAsMarkdown(content: string): string {
    const timestamp = new Date().toLocaleString();
    return `# AI创作Prompt

生成时间: ${timestamp}

\`\`\`
${content}
\`\`\`

---
*由 [Novellus 创作工具](https://novellus.ai) 生成*`;
  }

  formatAsStructured(content: string): string {
    const timestamp = new Date().toLocaleString();
    return `/**
 * Novellus AI创作Prompt
 * 生成时间: ${timestamp}
 * 工具版本: v1.0
 */

${content}

/**
 * 使用说明:
 * 1. 将此Prompt复制到AI工具中（如ChatGPT、Claude、Gemini等）
 * 2. 根据需要调整具体参数
 * 3. 获得AI生成的高质量创作内容
 *
 * 推荐AI工具:
 * - Claude: 适合深度分析和文学创作
 * - ChatGPT: 适合结构化内容和实用建议
 * - Gemini: 适合创意性内容和多样化观点
 */`;
  }

  private replaceVariables(content: string, variables: Record<string, any>): string {
    let result = content;

    Object.entries(variables).forEach(([key, value]) => {
      const placeholder = `{{${key}}}`;
      let replacement = '';

      if (Array.isArray(value)) {
        replacement = value.join(', ');
      } else if (typeof value === 'boolean') {
        replacement = value ? '是' : '否';
      } else {
        replacement = String(value || '');
      }

      result = result.replace(new RegExp(placeholder.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), replacement);
    });

    return result;
  }

  private fallbackCopyToClipboard(text: string): void {
    // 创建临时textarea元素
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
      document.execCommand('copy');
    } catch (error) {
      console.error('回退复制方法失败:', error);
      throw error;
    } finally {
      document.body.removeChild(textArea);
    }
  }

  private downloadFile(content: string, filename: string, mimeType: string): void {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  private showToast(message: string, type: 'success' | 'error' | 'info'): void {
    // 这里可以集成具体的Toast库或自定义实现
    console.log(`[${type.toUpperCase()}] ${message}`);

    // 简单的原生实现
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
      color: white;
      padding: 12px 20px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 500;
      z-index: 10000;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      animation: slideInRight 0.3s ease-out;
    `;

    document.body.appendChild(toast);

    // 3秒后自动移除
    setTimeout(() => {
      toast.style.animation = 'slideOutRight 0.3s ease-in';
      setTimeout(() => {
        if (document.body.contains(toast)) {
          document.body.removeChild(toast);
        }
      }, 300);
    }, 3000);
  }

  private trackUsage(action: string, format: string): void {
    // 记录使用统计
    const usage = {
      action,
      format,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    };

    try {
      const usageHistory = JSON.parse(localStorage.getItem('novellus-prompt-usage') || '[]');
      usageHistory.push(usage);

      // 保持最新的100条记录
      if (usageHistory.length > 100) {
        usageHistory.splice(0, usageHistory.length - 100);
      }

      localStorage.setItem('novellus-prompt-usage', JSON.stringify(usageHistory));
    } catch (error) {
      console.warn('记录使用统计失败:', error);
    }
  }
}

// Prompt历史管理服务
export class PromptHistoryService implements IPromptHistoryService {
  private readonly storageKey = 'novellus-prompt-history';
  private readonly maxHistorySize = 100;

  async saveToHistory(prompt: GeneratedPrompt): Promise<void> {
    try {
      const history = await this.getHistory();
      const historyItem: PromptHistory = {
        id: `history_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        template: prompt.template,
        variables: prompt.variables,
        generatedContent: prompt.generatedContent,
        createdAt: new Date(),
        usageCount: 1,
        tags: [prompt.template.category, prompt.metadata.userConfig.difficulty],
        projectId: prompt.metadata.userConfig.projectContext?.id
      };

      // 添加到历史记录开头
      history.unshift(historyItem);

      // 保持历史记录数量限制
      if (history.length > this.maxHistorySize) {
        history.splice(this.maxHistorySize);
      }

      await this.setHistory(history);
    } catch (error) {
      console.error('保存到历史记录失败:', error);
      throw error;
    }
  }

  async getHistory(): Promise<PromptHistory[]> {
    try {
      const stored = localStorage.getItem(this.storageKey);
      if (!stored) return [];

      const parsed = JSON.parse(stored);
      return parsed.map((item: any) => ({
        ...item,
        createdAt: new Date(item.createdAt),
        template: {
          ...item.template,
          createdAt: new Date(item.template.createdAt)
        }
      }));
    } catch (error) {
      console.error('读取历史记录失败:', error);
      return [];
    }
  }

  async searchHistory(query: string, category?: string): Promise<PromptHistory[]> {
    try {
      const history = await this.getHistory();
      const lowercaseQuery = query.toLowerCase();

      return history.filter(item => {
        // 搜索匹配
        const matchesQuery = !query ||
          item.template.title.toLowerCase().includes(lowercaseQuery) ||
          item.template.description.toLowerCase().includes(lowercaseQuery) ||
          item.generatedContent.toLowerCase().includes(lowercaseQuery) ||
          item.tags.some(tag => tag.toLowerCase().includes(lowercaseQuery));

        // 分类匹配
        const matchesCategory = !category || item.template.category === category;

        return matchesQuery && matchesCategory;
      });
    } catch (error) {
      console.error('搜索历史记录失败:', error);
      return [];
    }
  }

  async deleteFromHistory(id: string): Promise<void> {
    try {
      const history = await this.getHistory();
      const filteredHistory = history.filter(item => item.id !== id);
      await this.setHistory(filteredHistory);
    } catch (error) {
      console.error('删除历史记录失败:', error);
      throw error;
    }
  }

  async ratePrompt(id: string, rating: number): Promise<void> {
    try {
      const history = await this.getHistory();
      const item = history.find(h => h.id === id);

      if (item) {
        item.rating = Math.max(1, Math.min(5, rating)); // 限制在1-5之间
        await this.setHistory(history);
      }
    } catch (error) {
      console.error('评分失败:', error);
      throw error;
    }
  }

  async addTags(id: string, tags: string[]): Promise<void> {
    try {
      const history = await this.getHistory();
      const item = history.find(h => h.id === id);

      if (item) {
        // 合并标签并去重
        const newTags = [...new Set([...item.tags, ...tags])];
        item.tags = newTags;
        await this.setHistory(history);
      }
    } catch (error) {
      console.error('添加标签失败:', error);
      throw error;
    }
  }

  async incrementUsage(id: string): Promise<void> {
    try {
      const history = await this.getHistory();
      const item = history.find(h => h.id === id);

      if (item) {
        item.usageCount++;
        await this.setHistory(history);
      }
    } catch (error) {
      console.error('更新使用次数失败:', error);
      throw error;
    }
  }

  async getStats(): Promise<{
    totalPrompts: number;
    categoryStats: Record<string, number>;
    usageStats: Record<string, number>;
    recentActivity: PromptHistory[];
  }> {
    try {
      const history = await this.getHistory();

      const categoryStats: Record<string, number> = {};
      const usageStats: Record<string, number> = {};

      history.forEach(item => {
        // 分类统计
        categoryStats[item.template.category] = (categoryStats[item.template.category] || 0) + 1;

        // 使用次数统计
        const usageRange = this.getUsageRange(item.usageCount);
        usageStats[usageRange] = (usageStats[usageRange] || 0) + 1;
      });

      // 最近活动（最新10条）
      const recentActivity = history.slice(0, 10);

      return {
        totalPrompts: history.length,
        categoryStats,
        usageStats,
        recentActivity
      };
    } catch (error) {
      console.error('获取统计数据失败:', error);
      return {
        totalPrompts: 0,
        categoryStats: {},
        usageStats: {},
        recentActivity: []
      };
    }
  }

  private async setHistory(history: PromptHistory[]): Promise<void> {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(history));
    } catch (error) {
      console.error('保存历史记录失败:', error);
      throw error;
    }
  }

  private getUsageRange(count: number): string {
    if (count === 1) return '使用1次';
    if (count <= 5) return '使用2-5次';
    if (count <= 10) return '使用6-10次';
    return '使用10次以上';
  }
}

// 全局实例
export const promptCopyService = new PromptCopyService();
export const promptHistoryService = new PromptHistoryService();