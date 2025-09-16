import localforage from 'localforage';

// 配置本地存储
const storage = localforage.createInstance({
  name: 'NovellsCreationTools',
  storeName: 'data',
  version: 1.0,
  description: 'Novellus创作工具数据存储'
});

export class StorageService {
  private prefix: string;

  constructor(prefix: string) {
    this.prefix = prefix;
  }

  private getKey(key: string): string {
    return `${this.prefix}_${key}`;
  }

  async set<T>(key: string, value: T): Promise<void> {
    await storage.setItem(this.getKey(key), value);
  }

  async get<T>(key: string): Promise<T | null> {
    return await storage.getItem(this.getKey(key));
  }

  async remove(key: string): Promise<void> {
    await storage.removeItem(this.getKey(key));
  }

  async getAll<T>(): Promise<T[]> {
    const keys = await storage.keys();
    const prefixedKeys = keys.filter(key => key.startsWith(this.prefix));
    const values = await Promise.all(
      prefixedKeys.map(key => storage.getItem(key))
    );
    return values.filter(value => value !== null) as T[];
  }

  async clear(): Promise<void> {
    const keys = await storage.keys();
    const prefixedKeys = keys.filter(key => key.startsWith(this.prefix));
    await Promise.all(prefixedKeys.map(key => storage.removeItem(key)));
  }

  async export(): Promise<string> {
    const keys = await storage.keys();
    const prefixedKeys = keys.filter(key => key.startsWith(this.prefix));
    const data: Record<string, any> = {};

    for (const key of prefixedKeys) {
      const value = await storage.getItem(key);
      data[key] = value;
    }

    return JSON.stringify({
      prefix: this.prefix,
      data,
      exportDate: new Date().toISOString(),
      version: '1.0.0'
    }, null, 2);
  }

  async import(jsonData: string): Promise<void> {
    const parsed = JSON.parse(jsonData);

    if (!parsed.prefix || !parsed.data) {
      throw new Error('无效的备份数据格式');
    }

    // 清除现有数据
    await this.clear();

    // 导入新数据
    for (const [key, value] of Object.entries(parsed.data)) {
      await storage.setItem(key, value);
    }
  }
}

// 工具函数
export const generateId = (): string => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
};

export const formatDate = (date: Date): string => {
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
};

export const deepClone = <T>(obj: T): T => {
  return JSON.parse(JSON.stringify(obj));
};

// 导出storage实例供直接使用
export { storage };