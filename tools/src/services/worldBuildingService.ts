import { WorldBuilding, Culture, Location, HistoricalEvent, WorldSystem } from '../types/index';
import { storage } from '@utils/storage';

export class WorldBuildingService {
  private readonly storageKey = 'novellus-worlds';

  async getAllWorlds(): Promise<WorldBuilding[]> {
    try {
      const worlds = await storage.getItem<WorldBuilding[]>(this.storageKey) || [];
      return worlds.map(this.deserializeWorld);
    } catch (error) {
      console.error('获取世界列表失败:', error);
      return [];
    }
  }

  async getWorldById(id: string): Promise<WorldBuilding | null> {
    try {
      const worlds = await this.getAllWorlds();
      return worlds.find(world => world.id === id) || null;
    } catch (error) {
      console.error('获取世界失败:', error);
      return null;
    }
  }

  async getWorldsByProject(projectId: string): Promise<WorldBuilding[]> {
    try {
      const worlds = await this.getAllWorlds();
      return worlds.filter(world => world.projectId === projectId);
    } catch (error) {
      console.error('获取项目世界失败:', error);
      return [];
    }
  }

  async saveWorld(world: WorldBuilding): Promise<void> {
    try {
      const worlds = await this.getAllWorlds();
      const existingIndex = worlds.findIndex(w => w.id === world.id);

      const serializedWorld = this.serializeWorld({
        ...world,
        updatedAt: new Date()
      });

      if (existingIndex >= 0) {
        worlds[existingIndex] = serializedWorld;
      } else {
        worlds.push(serializedWorld);
      }

      await storage.setItem(this.storageKey, worlds);
    } catch (error) {
      console.error('保存世界失败:', error);
      throw error;
    }
  }

  async deleteWorld(id: string): Promise<void> {
    try {
      const worlds = await this.getAllWorlds();
      const filteredWorlds = worlds
        .filter(world => world.id !== id)
        .map(this.serializeWorld);

      await storage.setItem(this.storageKey, filteredWorlds);
    } catch (error) {
      console.error('删除世界失败:', error);
      throw error;
    }
  }

  // 创建世界模板
  createWorldTemplate(projectId: string, type: WorldBuilding['type'] = 'fantasy'): WorldBuilding {
    const templates = this.getWorldTemplates();
    const template = templates[type];

    return {
      id: this.generateId(),
      projectId,
      name: '',
      type,
      settings: template.settings,
      cultures: [],
      locations: [],
      history: [],
      systems: template.systems,
      createdAt: new Date(),
      updatedAt: new Date()
    };
  }

  // 获取世界模板库
  private getWorldTemplates() {
    return {
      fantasy: {
        settings: {
          physics: {
            naturalLaws: ['重力', '时间流逝', '能量守恒'],
            magicSystem: {
              name: '魔法系统',
              type: 'hard' as const,
              source: '魔力',
              rules: ['魔力消耗', '咒语结构', '施法组件'],
              limitations: ['魔力有限', '施法时间', '技能要求'],
              practitioners: ['法师', '术士', '牧师'],
              socialImpact: '魔法影响社会结构和日常生活'
            },
            technology: {
              era: '中世纪',
              keyTechnologies: ['锻造', '农业', '建筑'],
              limitations: ['无火药', '无印刷术', '有限的机械'],
              socialImpact: ['手工业发达', '农业为主', '城堡防御'],
              progressionRate: '缓慢发展'
            },
            timeFlow: '标准时间流速'
          },
          geography: {
            continents: [
              {
                name: '主大陆',
                size: '大型',
                climate: ['温带', '亚热带'],
                features: ['山脉', '森林', '平原', '河流'],
                cultures: ['人类', '精灵', '矮人']
              }
            ],
            climate: '多样化气候',
            naturalResources: ['铁矿', '木材', '宝石', '草药'],
            environmentalChallenges: ['野兽威胁', '自然灾害', '魔法污染']
          },
          society: {
            governmentSystems: [
              {
                type: '封建制',
                description: '王国与领主的等级制度',
                powerStructure: '国王-公爵-伯爵-骑士',
                laws: ['贵族特权', '农奴制', '骑士法典']
              }
            ],
            economicSystems: [
              {
                type: '农业经济',
                currency: '金币',
                tradeRoutes: ['陆路商道', '河运'],
                keyIndustries: ['农业', '手工业', '魔法工艺'],
                classStructure: ['贵族', '商人', '农民', '奴隶']
              }
            ],
            socialStructures: [
              {
                type: '等级社会',
                hierarchy: ['王室', '贵族', '骑士', '平民', '农奴'],
                mobility: '有限流动',
                traditions: ['骑士精神', '荣誉决斗', '宫廷礼仪']
              }
            ],
            conflictSources: ['领土争夺', '资源竞争', '宗教分歧', '种族冲突']
          }
        },
        systems: [
          {
            type: 'magical' as const,
            name: '魔法学院',
            description: '培养和管理魔法师的机构',
            rules: ['入学考试', '等级制度', '法术注册'],
            participants: ['学生', '教师', '大法师'],
            conflicts: ['学派之争', '禁术研究', '政治介入']
          }
        ]
      },
      scifi: {
        settings: {
          physics: {
            naturalLaws: ['相对论', '量子力学', '热力学定律'],
            technology: {
              era: '未来',
              keyTechnologies: ['人工智能', '星际旅行', '基因工程', '纳米技术'],
              limitations: ['能源需求', '伦理约束', '技术复杂性'],
              socialImpact: ['自动化', '生命延长', '太空殖民'],
              progressionRate: '快速发展'
            },
            timeFlow: '可变时间流速'
          },
          geography: {
            continents: [
              {
                name: '地球',
                size: '行星',
                climate: ['人工调控'],
                features: ['巨型城市', '工业区', '保护区'],
                cultures: ['统一人类', 'AI实体', '基因改造人']
              }
            ],
            climate: '气候控制系统',
            naturalResources: ['稀有元素', '能源晶体', '合成材料'],
            environmentalChallenges: ['污染治理', '资源枯竭', '生态平衡']
          },
          society: {
            governmentSystems: [
              {
                type: '联邦制',
                description: '星际联邦政府',
                powerStructure: '议会-委员会-地方政府',
                laws: ['人权法', 'AI权利法', '星际法']
              }
            ],
            economicSystems: [
              {
                type: '后稀缺经济',
                currency: '能源单位',
                tradeRoutes: ['星际贸易', '量子传输'],
                keyIndustries: ['技术研发', '太空工业', '娱乐'],
                classStructure: ['科学家', '工程师', '艺术家', '服务者']
              }
            ],
            socialStructures: [
              {
                type: '功能社会',
                hierarchy: ['专家委员会', '技术人员', '普通公民'],
                mobility: '基于能力',
                traditions: ['科学精神', '探索文化', '技术崇拜']
              }
            ],
            conflictSources: ['资源竞争', '技术鸿沟', 'AI威胁', '殖民冲突']
          }
        },
        systems: [
          {
            type: 'technological' as const,
            name: '中央AI网络',
            description: '管理社会运行的人工智能系统',
            rules: ['算法治理', '数据保护', '人机界限'],
            participants: ['AI实体', '人类监督者', '系统维护者'],
            conflicts: ['AI自主性', '隐私问题', '系统故障']
          }
        ]
      },
      realistic: {
        settings: {
          physics: {
            naturalLaws: ['牛顿定律', '热力学', '电磁学'],
            technology: {
              era: '现代',
              keyTechnologies: ['互联网', '移动通信', '新能源'],
              limitations: ['物理定律', '经济成本', '环境影响'],
              socialImpact: ['全球化', '信息时代', '城市化'],
              progressionRate: '稳定发展'
            },
            timeFlow: '正常时间流速'
          },
          geography: {
            continents: [
              {
                name: '现实地球',
                size: '标准行星',
                climate: ['多样气候带'],
                features: ['七大洲', '海洋', '山脉', '河流'],
                cultures: ['多元文化', '民族国家']
              }
            ],
            climate: '自然气候系统',
            naturalResources: ['石油', '矿物', '淡水', '森林'],
            environmentalChallenges: ['气候变化', '环境污染', '资源枯竭']
          },
          society: {
            governmentSystems: [
              {
                type: '民主制',
                description: '现代民主国家',
                powerStructure: '立法-行政-司法',
                laws: ['宪法', '民法', '刑法']
              }
            ],
            economicSystems: [
              {
                type: '市场经济',
                currency: '法定货币',
                tradeRoutes: ['全球贸易', '电子商务'],
                keyIndustries: ['制造业', '服务业', '科技'],
                classStructure: ['上层', '中产', '工人', '贫困']
              }
            ],
            socialStructures: [
              {
                type: '阶层社会',
                hierarchy: ['精英', '中产阶级', '工人阶级'],
                mobility: '有限流动',
                traditions: ['个人主义', '竞争文化', '消费主义']
              }
            ],
            conflictSources: ['经济不平等', '政治分歧', '文化冲突', '资源争夺']
          }
        },
        systems: [
          {
            type: 'political' as const,
            name: '国际组织',
            description: '维护国际秩序的组织',
            rules: ['国际法', '外交程序', '制裁机制'],
            participants: ['成员国', '外交官', '国际官员'],
            conflicts: ['主权争议', '利益冲突', '价值分歧']
          }
        ]
      },
      historical: {
        settings: {
          physics: {
            naturalLaws: ['古代物理认知', '四元素理论'],
            technology: {
              era: '古代',
              keyTechnologies: ['青铜工艺', '农业技术', '建筑工程'],
              limitations: ['工具简陋', '能源有限', '知识匮乏'],
              socialImpact: ['农业文明', '手工业', '城邦制'],
              progressionRate: '极缓发展'
            },
            timeFlow: '历史时间流速'
          },
          geography: {
            continents: [
              {
                name: '古代世界',
                size: '已知世界',
                climate: ['地中海气候', '大陆性气候'],
                features: ['古代地形', '传说之地'],
                cultures: ['古代文明', '部落社会']
              }
            ],
            climate: '自然气候',
            naturalResources: ['金属矿藏', '石材', '木材', '香料'],
            environmentalChallenges: ['自然灾害', '疾病', '战争破坏']
          },
          society: {
            governmentSystems: [
              {
                type: '君主制',
                description: '古代王权',
                powerStructure: '君主-贵族-官僚',
                laws: ['王法', '习俗法', '宗教法']
              }
            ],
            economicSystems: [
              {
                type: '农业经济',
                currency: '金属货币',
                tradeRoutes: ['丝绸之路', '海上贸易'],
                keyIndustries: ['农业', '手工业', '贸易'],
                classStructure: ['王室', '贵族', '平民', '奴隶']
              }
            ],
            socialStructures: [
              {
                type: '传统社会',
                hierarchy: ['王权', '宗教', '军事', '商人'],
                mobility: '世袭制',
                traditions: ['祖先崇拜', '宗教仪式', '家族荣耀']
              }
            ],
            conflictSources: ['王朝更替', '外族入侵', '宗教冲突', '自然灾害']
          }
        },
        systems: [
          {
            type: 'religious' as const,
            name: '宗教体系',
            description: '古代宗教组织',
            rules: ['宗教律法', '祭祀制度', '教义传承'],
            participants: ['祭司', '信徒', '宗教学者'],
            conflicts: ['教派分歧', '世俗权力', '异端思想']
          }
        ]
      },
      'alternate-history': {
        settings: {
          physics: {
            naturalLaws: ['现实物理+变异因子'],
            technology: {
              era: '替代现代',
              keyTechnologies: ['蒸汽科技', '机械工艺', '替代能源'],
              limitations: ['技术分支', '资源限制', '社会接受度'],
              socialImpact: ['工业革命变异', '社会结构改变'],
              progressionRate: '分化发展'
            },
            timeFlow: '替代时间线'
          },
          geography: {
            continents: [
              {
                name: '替代地球',
                size: '变异地球',
                climate: ['气候差异'],
                features: ['地理变化', '新增地形'],
                cultures: ['替代文明', '分化发展']
              }
            ],
            climate: '变异气候系统',
            naturalResources: ['新型资源', '稀有材料', '能源变异'],
            environmentalChallenges: ['历史分歧影响', '技术副作用']
          },
          society: {
            governmentSystems: [
              {
                type: '替代政制',
                description: '历史分叉后的政府形式',
                powerStructure: '变异权力结构',
                laws: ['替代法律体系']
              }
            ],
            economicSystems: [
              {
                type: '替代经济',
                currency: '新型货币',
                tradeRoutes: ['变异贸易路线'],
                keyIndustries: ['替代工业', '新兴行业'],
                classStructure: ['替代社会阶层']
              }
            ],
            socialStructures: [
              {
                type: '分化社会',
                hierarchy: ['替代等级制度'],
                mobility: '不同流动性',
                traditions: ['新兴传统', '变异文化']
              }
            ],
            conflictSources: ['历史遗留', '分歧扩大', '新兴矛盾']
          }
        },
        systems: [
          {
            type: 'technological' as const,
            name: '替代科技树',
            description: '不同发展路径的技术体系',
            rules: ['技术逻辑', '发展限制', '应用规范'],
            participants: ['发明家', '工程师', '用户'],
            conflicts: ['技术竞争', '标准之争', '伦理问题']
          }
        ]
      },
      mixed: {
        settings: {
          physics: {
            naturalLaws: ['混合物理法则'],
            technology: {
              era: '多元时代',
              keyTechnologies: ['融合技术'],
              limitations: ['复杂性', '兼容性'],
              socialImpact: ['多元文明'],
              progressionRate: '不均衡发展'
            },
            timeFlow: '复杂时间流'
          },
          geography: {
            continents: [
              {
                name: '混合世界',
                size: '多样化',
                climate: ['复合气候'],
                features: ['多元地形'],
                cultures: ['融合文明']
              }
            ],
            climate: '多样化环境',
            naturalResources: ['复合资源'],
            environmentalChallenges: ['复杂挑战']
          },
          society: {
            governmentSystems: [
              {
                type: '混合政制',
                description: '多元政府形式',
                powerStructure: '复合结构',
                laws: ['综合法律']
              }
            ],
            economicSystems: [
              {
                type: '混合经济',
                currency: '多元货币',
                tradeRoutes: ['复合贸易'],
                keyIndustries: ['多元产业'],
                classStructure: ['复杂阶层']
              }
            ],
            socialStructures: [
              {
                type: '多元社会',
                hierarchy: ['灵活等级'],
                mobility: '多样流动',
                traditions: ['融合传统']
              }
            ],
            conflictSources: ['文明冲突', '价值分歧', '资源竞争']
          }
        },
        systems: [
          {
            type: 'mixed' as any,
            name: '混合系统',
            description: '多元化的社会系统',
            rules: ['灵活规则'],
            participants: ['多元参与者'],
            conflicts: ['复杂矛盾']
          }
        ]
      }
    };
  }

  // 生成文化
  generateCulture(worldType: WorldBuilding['type'], cultureName: string): Culture {
    const cultureTemplates = this.getCultureTemplates();
    const template = cultureTemplates[worldType] || cultureTemplates.fantasy;

    return {
      id: this.generateId(),
      name: cultureName,
      description: '',
      values: [...template.values],
      beliefs: [...template.beliefs],
      traditions: [...template.traditions],
      language: { ...template.language },
      artForms: [...template.artForms],
      socialNorms: [...template.socialNorms],
      conflicts: [],
      influences: []
    };
  }

  // 获取文化模板
  private getCultureTemplates() {
    return {
      fantasy: {
        values: ['荣誉', '勇气', '智慧', '魔法'],
        beliefs: ['诸神存在', '魔法力量', '命运注定'],
        traditions: ['吟游诗人', '魔法仪式', '骑士册封'],
        language: {
          name: '通用语',
          family: '魔法语系',
          writingSystem: '符文文字',
          characteristics: ['魔法词汇', '仪式用语'],
          speakers: 1000000
        },
        artForms: ['魔法工艺', '史诗诗歌', '战争舞蹈'],
        socialNorms: ['魔法师地位', '荣誉决斗', '行会制度']
      },
      scifi: {
        values: ['科学', '进步', '探索', '效率'],
        beliefs: ['技术万能', '理性主义', '进化论'],
        traditions: ['太空仪式', '技术传承', '数据记录'],
        language: {
          name: '标准语',
          family: '人工语系',
          writingSystem: '数字编码',
          characteristics: ['技术术语', '精确表达'],
          speakers: 10000000
        },
        artForms: ['全息艺术', '量子音乐', '虚拟雕塑'],
        socialNorms: ['效率优先', '数据隐私', '技术等级']
      },
      realistic: {
        values: ['自由', '平等', '正义', '个人主义'],
        beliefs: ['人权', '民主', '法治'],
        traditions: ['选举制度', '节日庆典', '家庭聚会'],
        language: {
          name: '现代语言',
          family: '自然语系',
          writingSystem: '拉丁字母',
          characteristics: ['日常用语', '专业术语'],
          speakers: 5000000
        },
        artForms: ['电影', '音乐', '文学', '绘画'],
        socialNorms: ['个人空间', '社交礼仪', '工作伦理']
      }
    };
  }

  // 生成地点
  generateLocation(worldType: WorldBuilding['type'], locationType: Location['type']): Location {
    const locationTemplates = this.getLocationTemplates();
    const template = locationTemplates[locationType];

    return {
      id: this.generateId(),
      name: '',
      type: locationType,
      description: template.description,
      geography: template.geography,
      climate: template.climate,
      culture: '',
      economy: template.economy,
      significance: '',
      connectedLocations: [],
      scenes: []
    };
  }

  // 获取地点模板
  private getLocationTemplates() {
    return {
      city: {
        description: '繁华的城市中心',
        geography: '平原或河畔',
        climate: '温和适宜',
        economy: '商业贸易中心'
      },
      town: {
        description: '宁静的小镇',
        geography: '丘陵或河谷',
        climate: '季节性变化',
        economy: '农业和手工业'
      },
      village: {
        description: '偏远的村庄',
        geography: '乡村田野',
        climate: '自然环境',
        economy: '农业为主'
      },
      landmark: {
        description: '重要的标志性建筑',
        geography: '特殊地形',
        climate: '地域性气候',
        economy: '旅游或宗教'
      },
      region: {
        description: '广阔的地理区域',
        geography: '多样化地形',
        climate: '区域性气候',
        economy: '综合经济'
      },
      building: {
        description: '特殊的建筑物',
        geography: '人工结构',
        climate: '室内环境',
        economy: '功能性经济'
      },
      natural: {
        description: '自然景观',
        geography: '天然地形',
        climate: '自然气候',
        economy: '资源开采'
      }
    };
  }

  // 生成历史事件
  generateHistoricalEvent(eventType: 'war' | 'disaster' | 'discovery' | 'political' | 'cultural'): HistoricalEvent {
    const eventTemplates = this.getEventTemplates();
    const template = eventTemplates[eventType];

    return {
      id: this.generateId(),
      name: '',
      date: '',
      description: '',
      participants: [],
      consequences: [...template.consequences],
      significance: template.significance
    };
  }

  // 获取事件模板
  private getEventTemplates() {
    return {
      war: {
        consequences: ['领土变更', '政权更替', '人口损失', '技术发展'],
        significance: '改变政治格局'
      },
      disaster: {
        consequences: ['环境破坏', '人口迁移', '社会重组', '技术适应'],
        significance: '推动社会变革'
      },
      discovery: {
        consequences: ['知识进步', '技术革新', '社会影响', '文化交流'],
        significance: '促进文明发展'
      },
      political: {
        consequences: ['制度变化', '权力转移', '法律改革', '社会稳定'],
        significance: '影响治理结构'
      },
      cultural: {
        consequences: ['价值观念', '艺术发展', '宗教变化', '语言演变'],
        significance: '塑造文明特征'
      }
    };
  }

  // 世界一致性检查
  checkWorldConsistency(world: WorldBuilding): { issues: string[], score: number } {
    const issues: string[] = [];
    let score = 100;

    // 基本信息检查
    if (!world.name.trim()) {
      issues.push('世界缺少名称');
      score -= 10;
    }

    // 物理法则一致性
    if (world.type === 'fantasy' && !world.settings.physics.magicSystem) {
      issues.push('奇幻世界缺少魔法系统');
      score -= 15;
    }

    if (world.type === 'scifi' && world.settings.physics.technology.era === '古代') {
      issues.push('科幻世界的技术时代设定不符');
      score -= 10;
    }

    // 文化多样性检查
    if (world.cultures.length === 0) {
      issues.push('世界缺少文化设定');
      score -= 15;
    }

    // 地理与文化关联性
    const geographyCount = world.settings.geography.continents.length;
    const cultureCount = world.cultures.length;
    if (geographyCount > 0 && cultureCount > 0 && Math.abs(geographyCount - cultureCount) > 2) {
      issues.push('地理区域与文化数量不协调');
      score -= 5;
    }

    // 历史连贯性
    if (world.history.length > 1) {
      const sortedEvents = world.history.sort((a, b) =>
        parseInt(a.date) - parseInt(b.date)
      );

      for (let i = 1; i < sortedEvents.length; i++) {
        const prev = sortedEvents[i - 1];
        const curr = sortedEvents[i];

        // 检查事件逻辑连贯性
        if (prev.consequences.some(c => c.includes('毁灭')) &&
            curr.description.includes('繁荣')) {
          issues.push(`历史事件逻辑冲突: ${prev.name} -> ${curr.name}`);
          score -= 5;
        }
      }
    }

    // 系统功能性检查
    world.systems.forEach(system => {
      if (system.participants.length === 0) {
        issues.push(`系统"${system.name}"缺少参与者`);
        score -= 3;
      }

      if (system.rules.length === 0) {
        issues.push(`系统"${system.name}"缺少运行规则`);
        score -= 3;
      }
    });

    return { issues, score: Math.max(0, score) };
  }

  private serializeWorld(world: WorldBuilding): any {
    return {
      ...world,
      createdAt: world.createdAt.toISOString(),
      updatedAt: world.updatedAt.toISOString()
    };
  }

  private deserializeWorld(data: any): WorldBuilding {
    return {
      ...data,
      createdAt: new Date(data.createdAt),
      updatedAt: new Date(data.updatedAt)
    };
  }

  private generateId(): string {
    return `world_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}