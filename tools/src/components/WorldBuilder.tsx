import React, { useState, useEffect } from 'react';
import {
  Container,
  VStack,
  HStack,
  Box,
  Card,
  Button,
  Input,
  Textarea,
  Field,
  Heading,
  Text,
  Badge,
  Tabs,
  SimpleGrid,
  Spinner,
  IconButton,
  NativeSelect,
  Tag,
  Separator,
  Stack,
  Group,
  Show
} from '@chakra-ui/react';
import { WorldBuilding, Culture, Location } from '../types/index';
import { WorldBuildingService } from '@services/worldBuildingService';
import { PromptGenerator } from './PromptGenerator';
import { PromptConfig, GeneratedPrompt } from '../types/prompt';

interface WorldBuilderProps {
  projectId: string;
  onComplete: () => void;
  onCancel: () => void;
}

export const WorldBuilder: React.FC<WorldBuilderProps> = ({
  projectId,
  onComplete,
  onCancel
}) => {
  const [worldService] = useState(new WorldBuildingService());
  const [worlds, setWorlds] = useState<WorldBuilding[]>([]);
  const [currentWorld, setCurrentWorld] = useState<WorldBuilding | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'cultures' | 'locations' | 'history' | 'systems'>('overview');
  const [isCreating, setIsCreating] = useState(false);
  const [consistencyCheck, setConsistencyCheck] = useState<{ issues: string[], score: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [showPromptGenerator, setShowPromptGenerator] = useState(false);

  useEffect(() => {
    loadWorlds();
  }, []);

  useEffect(() => {
    if (currentWorld) {
      const check = worldService.checkWorldConsistency(currentWorld);
      setConsistencyCheck(check);
    }
  }, [currentWorld, worldService]);

  const loadWorlds = async () => {
    try {
      const worldsList = await worldService.getWorldsByProject(projectId);
      setWorlds(worldsList);
      if (worldsList.length > 0) {
        setCurrentWorld(worldsList[0]);
      }
    } catch (error) {
      console.error('加载世界失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWorld = async (type: WorldBuilding['type']) => {
    try {
      const newWorld = worldService.createWorldTemplate(projectId, type);
      newWorld.name = `新的${getWorldTypeLabel(type)}世界`;
      await worldService.saveWorld(newWorld);
      await loadWorlds();
      setCurrentWorld(newWorld);
      setIsCreating(false);
    } catch (error) {
      console.error('创建世界失败:', error);
      alert('创建失败，请重试');
    }
  };

  const handleCreateWithPrompt = () => {
    setShowPromptGenerator(true);
  };

  const handlePromptGenerated = (prompt: GeneratedPrompt) => {
    console.log('世界构建Prompt已生成:', prompt);
  };

  const handleBackToTraditional = () => {
    setShowPromptGenerator(false);
    setIsCreating(true);
  };

  const handleSaveWorld = async () => {
    if (!currentWorld) return;

    try {
      await worldService.saveWorld(currentWorld);
      await loadWorlds();
    } catch (error) {
      console.error('保存世界失败:', error);
      alert('保存失败，请重试');
    }
  };

  const handleWorldChange = (field: string, value: any) => {
    if (!currentWorld) return;

    setCurrentWorld(prev => ({
      ...prev!,
      [field]: value
    }));
  };

  const addCulture = () => {
    if (!currentWorld) return;

    const newCulture = worldService.generateCulture(currentWorld.type, '新文化');
    setCurrentWorld(prev => ({
      ...prev!,
      cultures: [...prev!.cultures, newCulture]
    }));
  };

  const updateCulture = (index: number, culture: Culture) => {
    if (!currentWorld) return;

    const newCultures = [...currentWorld.cultures];
    newCultures[index] = culture;
    setCurrentWorld(prev => ({
      ...prev!,
      cultures: newCultures
    }));
  };

  const removeCulture = (index: number) => {
    if (!currentWorld) return;

    const newCultures = [...currentWorld.cultures];
    newCultures.splice(index, 1);
    setCurrentWorld(prev => ({
      ...prev!,
      cultures: newCultures
    }));
  };

  const addLocation = (type: Location['type']) => {
    if (!currentWorld) return;

    const newLocation = worldService.generateLocation(currentWorld.type, type);
    newLocation.name = `新的${getLocationTypeLabel(type)}`;
    setCurrentWorld(prev => ({
      ...prev!,
      locations: [...prev!.locations, newLocation]
    }));
  };

  const getWorldTypeLabel = (type: WorldBuilding['type']) => {
    const labels = {
      fantasy: '奇幻',
      scifi: '科幻',
      realistic: '现实',
      historical: '历史',
      'alternate-history': '架空历史',
      mixed: '混合'
    };
    return labels[type] || type;
  };

  const getLocationTypeLabel = (type: Location['type']) => {
    const labels = {
      city: '城市',
      town: '城镇',
      village: '村庄',
      landmark: '地标',
      region: '区域',
      building: '建筑',
      natural: '自然景观'
    };
    return labels[type] || type;
  };

  if (loading) {
    return (
      <Container maxW="6xl" py={8}>
        <VStack spacing={4}>
          <Spinner size="xl" colorPalette="blue" />
          <Text>正在加载世界构建器...</Text>
        </VStack>
      </Container>
    );
  }

  // 显示Prompt生成器
  if (showPromptGenerator) {
    const promptConfig: Partial<PromptConfig> = {
      category: 'world',
      difficulty: 'intermediate',
      writingStyle: 'creative',
      detailLevel: 'comprehensive',
      aiModel: 'claude',
      projectContext: { id: projectId, name: 'Current Project' }
    };

    return (
      <Container maxW="6xl" py={6}>
        <VStack gap={4} mb={6} align="stretch">
          <HStack justify="space-between">
            <Heading size="lg">🌍 世界构建 - AI辅助创作</Heading>
            <HStack gap={2}>
              <Button
                variant="outline"
                onClick={handleBackToTraditional}
              >
                🔧 传统创建
              </Button>
              <Button
                variant="outline"
                onClick={onCancel}
              >
                取消
              </Button>
            </HStack>
          </HStack>

          <Text color="gray.600">
            使用AI生成专业的世界构建Prompt，帮助您创造逻辑一致、引人入胜的虚构世界
          </Text>
        </VStack>

        <PromptGenerator
          initialConfig={promptConfig}
          onPromptGenerated={handlePromptGenerated}
          projectContext={{ id: projectId, name: 'Current Project' }}
        />
      </Container>
    );
  }

  if (isCreating) {
    return <WorldTypeSelector onSelect={handleCreateWorld} onCancel={() => setIsCreating(false)} />;
  }

  if (!currentWorld) {
    return (
      <Container maxW="6xl" py={8}>
        <VStack spacing={6} textAlign="center">
          <Box>
            <Heading size="2xl" mb={4}>🌍 智能世界构建平台</Heading>
            <Text fontSize="lg" color="fg.muted">
              还没有创建任何世界。选择一种方式开始构建你的独特世界！
            </Text>
          </Box>
          <HStack gap={4}>
            <Button
              size="lg"
              colorPalette="blue"
              onClick={handleCreateWithPrompt}
            >
              🎯 AI辅助创作
            </Button>
            <Button
              size="lg"
              variant="outline"
              onClick={() => setIsCreating(true)}
            >
              🔧 传统创建
            </Button>
          </HStack>
          <Text fontSize="sm" color="gray.500">
            推荐使用AI辅助创作，生成专业的世界构建Prompt
          </Text>
        </VStack>
      </Container>
    );
  }

  return (
    <Container maxW="8xl" py={6}>
      <VStack spacing={6} align="stretch">
        {/* Header Section */}
        <Card.Root>
          <Card.Body>
            <VStack spacing={4} align="stretch">
              <HStack justify="space-between" wrap="wrap">
                <VStack align="start" spacing={2}>
                  <Field.Root>
                    <Input
                      value={currentWorld.name}
                      onChange={(e) => handleWorldChange('name', e.target.value)}
                      placeholder="世界名称"
                      fontSize="2xl"
                      fontWeight="bold"
                      variant="subtle"
                      size="lg"
                    />
                  </Field.Root>

                  <HStack spacing={3}>
                    <Badge colorPalette="blue" variant="subtle">
                      {getWorldTypeLabel(currentWorld.type)}
                    </Badge>
                    <Text fontSize="sm" color="fg.muted">
                      创建于 {currentWorld.createdAt.toLocaleDateString('zh-CN')}
                    </Text>
                  </HStack>

                  {consistencyCheck && (
                    <Badge
                      colorPalette={consistencyCheck.score < 70 ? 'red' : consistencyCheck.score < 90 ? 'orange' : 'green'}
                      variant="surface"
                    >
                      世界一致性: {consistencyCheck.score}/100
                      {consistencyCheck.issues.length > 0 && (
                        <Text as="span" ml={2}>
                          ({consistencyCheck.issues.length} 个问题)
                        </Text>
                      )}
                    </Badge>
                  )}
                </VStack>

                <HStack spacing={3}>
                  <Button onClick={() => setIsCreating(true)} variant="outline">
                    新建世界
                  </Button>
                  <Button onClick={handleSaveWorld} colorPalette="blue">
                    保存世界
                  </Button>
                  <Button onClick={onCancel} variant="ghost">
                    返回
                  </Button>
                </HStack>
              </HStack>
            </VStack>
          </Card.Body>
        </Card.Root>

        {/* Tabs Navigation and Content */}
        <Tabs.Root value={activeTab} onValueChange={(details) => setActiveTab(details.value as any)}>
          <Tabs.List>
            <Tabs.Trigger value="overview">
              🌍 概览
            </Tabs.Trigger>
            <Tabs.Trigger value="cultures">
              🏛️ 文化
            </Tabs.Trigger>
            <Tabs.Trigger value="locations">
              🗺️ 地点
            </Tabs.Trigger>
            <Tabs.Trigger value="history">
              📜 历史
            </Tabs.Trigger>
            <Tabs.Trigger value="systems">
              ⚙️ 系统
            </Tabs.Trigger>
          </Tabs.List>

          <Tabs.Content value="overview">
            <OverviewTab world={currentWorld} onChange={handleWorldChange} />
          </Tabs.Content>

          <Tabs.Content value="cultures">
            <CulturesTab
              cultures={currentWorld.cultures}
              onAdd={addCulture}
              onUpdate={updateCulture}
              onRemove={removeCulture}
            />
          </Tabs.Content>

          <Tabs.Content value="locations">
            <LocationsTab
              locations={currentWorld.locations}
              onAdd={addLocation}
              cultures={currentWorld.cultures}
            />
          </Tabs.Content>

          <Tabs.Content value="history">
            <HistoryTab world={currentWorld} onChange={handleWorldChange} />
          </Tabs.Content>

          <Tabs.Content value="systems">
            <SystemsTab world={currentWorld} onChange={handleWorldChange} />
          </Tabs.Content>
        </Tabs.Root>

        {/* Consistency Issues Panel */}
        {consistencyCheck && consistencyCheck.issues.length > 0 && (
          <Card.Root colorPalette="orange" variant="subtle">
            <Card.Header>
              <Card.Title>🔍 一致性检查</Card.Title>
            </Card.Header>
            <Card.Body>
              <VStack align="start" spacing={2}>
                {consistencyCheck.issues.map((issue, index) => (
                  <HStack key={index} spacing={2}>
                    <Text>⚠️</Text>
                    <Text fontSize="sm">{issue}</Text>
                  </HStack>
                ))}
              </VStack>
            </Card.Body>
          </Card.Root>
        )}
      </VStack>
    </Container>
  );
};

// 世界类型选择器
interface WorldTypeSelectorProps {
  onSelect: (type: WorldBuilding['type']) => void;
  onCancel: () => void;
}

const WorldTypeSelector: React.FC<WorldTypeSelectorProps> = ({ onSelect, onCancel }) => {
  const worldTypes = [
    {
      type: 'fantasy' as const,
      name: '奇幻世界',
      description: '魔法、神话生物和超自然力量的世界',
      icon: '🧙‍♂️',
      features: ['魔法系统', '神话生物', '古代文明', '超自然力量']
    },
    {
      type: 'scifi' as const,
      name: '科幻世界',
      description: '先进科技和未来文明的世界',
      icon: '🚀',
      features: ['高科技', '太空旅行', '人工智能', '未来社会']
    },
    {
      type: 'realistic' as const,
      name: '现实世界',
      description: '基于真实世界的故事背景',
      icon: '🌎',
      features: ['现代社会', '真实地理', '当代文化', '现实法则']
    },
    {
      type: 'historical' as const,
      name: '历史世界',
      description: '特定历史时期的世界',
      icon: '🏛️',
      features: ['历史背景', '古代文明', '传统文化', '历史事件']
    },
    {
      type: 'alternate-history' as const,
      name: '架空历史',
      description: '历史发展不同分支的世界',
      icon: '⏳',
      features: ['历史分歧', '替代发展', '假设情景', '变异文明']
    },
    {
      type: 'mixed' as const,
      name: '混合世界',
      description: '融合多种元素的复合世界',
      icon: '🌟',
      features: ['多元素融合', '创新设定', '独特规则', '自由创作']
    }
  ];

  return (
    <Container maxW="6xl" py={8}>
      <VStack spacing={6}>
        <VStack spacing={2} textAlign="center">
          <Heading size="2xl">🎭 选择世界类型</Heading>
          <Text color="fg.muted">选择最适合你的故事的世界类型</Text>
        </VStack>

        <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
          {worldTypes.map(type => (
            <Card.Root
              key={type.type}
              cursor="pointer"
              _hover={{ transform: 'translateY(-2px)' }}
              transition="all 0.2s"
              onClick={() => onSelect(type.type)}
            >
              <Card.Body>
                <VStack spacing={3}>
                  <Text fontSize="3xl">{type.icon}</Text>
                  <Heading size="md">{type.name}</Heading>
                  <Text color="fg.muted" textAlign="center">
                    {type.description}
                  </Text>
                  <HStack wrap="wrap" justify="center">
                    {type.features.map((feature, index) => (
                      <Tag.Root key={index} size="sm" colorPalette="blue">
                        <Tag.Label>{feature}</Tag.Label>
                      </Tag.Root>
                    ))}
                  </HStack>
                </VStack>
              </Card.Body>
            </Card.Root>
          ))}
        </SimpleGrid>

        <Button onClick={onCancel} variant="ghost">
          取消
        </Button>
      </VStack>
    </Container>
  );
};

// 概览标签页
interface OverviewTabProps {
  world: WorldBuilding;
  onChange: (field: string, value: any) => void;
}

const OverviewTab: React.FC<OverviewTabProps> = ({ world, onChange }) => {
  return (
    <VStack spacing={6} align="stretch">
      {/* Basic Settings Section */}
      <Card.Root>
        <Card.Header>
          <Card.Title>🌍 基本设定</Card.Title>
        </Card.Header>
        <Card.Body>
          <Field.Root>
            <Field.Label>世界描述</Field.Label>
            <Textarea
              value={world.settings.geography.climate}
              onChange={(e) => onChange('settings', {
                ...world.settings,
                geography: { ...world.settings.geography, climate: e.target.value }
              })}
              placeholder="描述这个世界的总体特征..."
              rows={4}
            />
          </Field.Root>
        </Card.Body>
      </Card.Root>

      {/* Physics Laws Section */}
      <Card.Root>
        <Card.Header>
          <Card.Title>⚡ 物理法则</Card.Title>
        </Card.Header>
        <Card.Body>
          <SimpleGrid columns={{ base: 1, lg: 2, xl: 3 }} spacing={4}>
            <Card.Root variant="subtle">
              <Card.Header>
                <Card.Title size="md">🔬 自然法则</Card.Title>
              </Card.Header>
              <Card.Body>
                <VStack spacing={3} align="stretch">
                  {world.settings.physics.naturalLaws.map((law, index) => (
                    <HStack key={index} spacing={2}>
                      <Input
                        value={law}
                        onChange={(e) => {
                          const newLaws = [...world.settings.physics.naturalLaws];
                          newLaws[index] = e.target.value;
                          onChange('settings', {
                            ...world.settings,
                            physics: { ...world.settings.physics, naturalLaws: newLaws }
                          });
                        }}
                        flex={1}
                      />
                      <IconButton
                        onClick={() => {
                          const newLaws = world.settings.physics.naturalLaws.filter((_, i) => i !== index);
                          onChange('settings', {
                            ...world.settings,
                            physics: { ...world.settings.physics, naturalLaws: newLaws }
                          });
                        }}
                        variant="ghost"
                        colorPalette="red"
                        size="sm"
                      >
                        ×
                      </IconButton>
                    </HStack>
                  ))}
                  <Button
                    onClick={() => {
                      const newLaws = [...world.settings.physics.naturalLaws, '新法则'];
                      onChange('settings', {
                        ...world.settings,
                        physics: { ...world.settings.physics, naturalLaws: newLaws }
                      });
                    }}
                    variant="outline"
                    size="sm"
                  >
                    + 添加法则
                  </Button>
                </VStack>
              </Card.Body>
            </Card.Root>

            {world.settings.physics.magicSystem && (
              <Card.Root variant="subtle">
                <Card.Header>
                  <Card.Title size="md">✨ 魔法系统</Card.Title>
                </Card.Header>
                <Card.Body>
                  <VStack spacing={4}>
                    <Field.Root>
                      <Field.Label>魔法名称</Field.Label>
                      <Input
                        value={world.settings.physics.magicSystem.name}
                        onChange={(e) => onChange('settings', {
                          ...world.settings,
                          physics: {
                            ...world.settings.physics,
                            magicSystem: { ...world.settings.physics.magicSystem!, name: e.target.value }
                          }
                        })}
                      />
                    </Field.Root>
                    <Field.Root>
                      <Field.Label>魔法类型</Field.Label>
                      <NativeSelect.Root>
                        <NativeSelect.Field
                          value={world.settings.physics.magicSystem.type}
                          onChange={(e) => onChange('settings', {
                            ...world.settings,
                            physics: {
                              ...world.settings.physics,
                              magicSystem: { ...world.settings.physics.magicSystem!, type: e.currentTarget.value as any }
                            }
                          })}
                        >
                          <option value="hard">硬魔法</option>
                          <option value="soft">软魔法</option>
                          <option value="hybrid">混合型</option>
                        </NativeSelect.Field>
                        <NativeSelect.Indicator />
                      </NativeSelect.Root>
                    </Field.Root>
                  </VStack>
                </Card.Body>
              </Card.Root>
            )}

            <Card.Root variant="subtle">
              <Card.Header>
                <Card.Title size="md">🔧 技术水平</Card.Title>
              </Card.Header>
              <Card.Body>
                <Field.Root>
                  <Field.Label>时代</Field.Label>
                  <Input
                    value={world.settings.physics.technology.era}
                    onChange={(e) => onChange('settings', {
                      ...world.settings,
                      physics: {
                        ...world.settings.physics,
                        technology: { ...world.settings.physics.technology, era: e.target.value }
                      }
                    })}
                  />
                </Field.Root>
              </Card.Body>
            </Card.Root>
          </SimpleGrid>
        </Card.Body>
      </Card.Root>

      {/* Geography Section */}
      <Card.Root>
        <Card.Header>
          <Card.Title>🗺️ 地理环境</Card.Title>
        </Card.Header>
        <Card.Body>
          <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={4}>
            <Card.Root variant="subtle">
              <Card.Header>
                <Card.Title size="md">🌍 大陆</Card.Title>
              </Card.Header>
              <Card.Body>
                <VStack spacing={3}>
                  {world.settings.geography.continents.map((continent, index) => (
                    <Input
                      key={index}
                      value={continent.name}
                      onChange={(e) => {
                        const newContinents = [...world.settings.geography.continents];
                        newContinents[index] = { ...continent, name: e.target.value };
                        onChange('settings', {
                          ...world.settings,
                          geography: { ...world.settings.geography, continents: newContinents }
                        });
                      }}
                      placeholder="大陆名称"
                    />
                  ))}
                </VStack>
              </Card.Body>
            </Card.Root>

            <Card.Root variant="subtle">
              <Card.Header>
                <Card.Title size="md">🌿 自然资源</Card.Title>
              </Card.Header>
              <Card.Body>
                <HStack wrap="wrap" spacing={2}>
                  {world.settings.geography.naturalResources.map((resource, index) => (
                    <Tag.Root
                      key={index}
                      colorPalette="green"
                    >
                      <Tag.Label>{resource}</Tag.Label>
                      <Tag.EndElement>
                        <Tag.CloseTrigger onClick={() => {
                          const newResources = world.settings.geography.naturalResources.filter((_, i) => i !== index);
                          onChange('settings', {
                            ...world.settings,
                            geography: { ...world.settings.geography, naturalResources: newResources }
                          });
                        }} />
                      </Tag.EndElement>
                    </Tag.Root>
                  ))}
                </HStack>
              </Card.Body>
            </Card.Root>
          </SimpleGrid>
        </Card.Body>
      </Card.Root>
    </VStack>
  );
};

// 文化标签页
interface CulturesTabProps {
  cultures: Culture[];
  onAdd: () => void;
  onUpdate: (index: number, culture: Culture) => void;
  onRemove: (index: number) => void;
}

const CulturesTab: React.FC<CulturesTabProps> = ({ cultures, onAdd, onUpdate, onRemove }) => {
  return (
    <VStack spacing={6} align="stretch">
      <HStack justify="space-between">
        <Heading size="lg">🏛️ 文化系统</Heading>
        <Button onClick={onAdd} colorPalette="blue">
          + 创建新文化
        </Button>
      </HStack>

      {cultures.length > 0 ? (
        <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={4}>
          {cultures.map((culture, index) => (
            <CultureCard
              key={culture.id}
              culture={culture}
              onUpdate={(updated) => onUpdate(index, updated)}
              onRemove={() => onRemove(index)}
            />
          ))}
        </SimpleGrid>
      ) : (
        <Card.Root>
          <Card.Body py={8}>
            <VStack spacing={2}>
              <Text color="fg.muted" textAlign="center">
                还没有创建任何文化。开始创建你世界中的第一个文化吧！
              </Text>
              <Button onClick={onAdd} variant="outline">
                创建第一个文化
              </Button>
            </VStack>
          </Card.Body>
        </Card.Root>
      )}
    </VStack>
  );
};

// 文化卡片
interface CultureCardProps {
  culture: Culture;
  onUpdate: (culture: Culture) => void;
  onRemove: () => void;
}

const CultureCard: React.FC<CultureCardProps> = ({ culture, onUpdate, onRemove }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const updateField = (field: keyof Culture, value: any) => {
    onUpdate({ ...culture, [field]: value });
  };

  return (
    <Card.Root>
      <Card.Header>
        <HStack justify="space-between">
          <Field.Root flex={1}>
            <Input
              value={culture.name}
              onChange={(e) => updateField('name', e.target.value)}
              placeholder="文化名称"
              fontWeight="semibold"
              variant="subtle"
            />
          </Field.Root>
          <HStack spacing={2}>
            <Button
              onClick={() => setIsExpanded(!isExpanded)}
              variant="ghost"
              size="sm"
            >
              {isExpanded ? '收起' : '展开'}
            </Button>
            <IconButton
              onClick={onRemove}
              variant="ghost"
              colorPalette="red"
              size="sm"
            >
              ×
            </IconButton>
          </HStack>
        </HStack>
      </Card.Header>

      <Card.Body>
        <VStack spacing={4} align="stretch">
          <Field.Root>
            <Textarea
              value={culture.description}
              onChange={(e) => updateField('description', e.target.value)}
              placeholder="描述这个文化的特征..."
              rows={2}
            />
          </Field.Root>

          {isExpanded && (
            <VStack spacing={4} align="stretch">
              <ArrayField
                label="价值观"
                values={culture.values}
                onChange={(values) => updateField('values', values)}
                placeholder="添加价值观"
              />

              <ArrayField
                label="信念"
                values={culture.beliefs}
                onChange={(values) => updateField('beliefs', values)}
                placeholder="添加信念"
              />

              <ArrayField
                label="传统"
                values={culture.traditions}
                onChange={(values) => updateField('traditions', values)}
                placeholder="添加传统"
              />

              <Box>
                <Heading size="sm" mb={3}>语言</Heading>
                <SimpleGrid columns={2} spacing={3}>
                  <Field.Root>
                    <Field.Label>语言名称</Field.Label>
                    <Input
                      value={culture.language.name}
                      onChange={(e) => updateField('language', { ...culture.language, name: e.target.value })}
                      placeholder="语言名称"
                    />
                  </Field.Root>
                  <Field.Root>
                    <Field.Label>语系</Field.Label>
                    <Input
                      value={culture.language.family}
                      onChange={(e) => updateField('language', { ...culture.language, family: e.target.value })}
                      placeholder="语系"
                    />
                  </Field.Root>
                </SimpleGrid>
              </Box>
            </VStack>
          )}
        </VStack>
      </Card.Body>
    </Card.Root>
  );
};

// 地点标签页
interface LocationsTabProps {
  locations: Location[];
  onAdd: (type: Location['type']) => void;
  cultures: Culture[];
}

const LocationsTab: React.FC<LocationsTabProps> = ({ locations, onAdd, cultures }) => {
  const locationTypes: { type: Location['type'], label: string, icon: string }[] = [
    { type: 'city', label: '城市', icon: '🏙️' },
    { type: 'town', label: '城镇', icon: '🏘️' },
    { type: 'village', label: '村庄', icon: '🏡' },
    { type: 'landmark', label: '地标', icon: '🗿' },
    { type: 'region', label: '区域', icon: '🗺️' },
    { type: 'building', label: '建筑', icon: '🏛️' },
    { type: 'natural', label: '自然景观', icon: '🌲' }
  ];

  return (
    <VStack spacing={6} align="stretch">
      <VStack spacing={4} align="stretch">
        <Heading size="lg">🗺️ 地点系统</Heading>
        <HStack wrap="wrap" spacing={2}>
          {locationTypes.map(type => (
            <Button
              key={type.type}
              onClick={() => onAdd(type.type)}
              variant="outline"
              size="sm"
              title={`添加${type.label}`}
            >
              {type.icon} {type.label}
            </Button>
          ))}
        </HStack>
      </VStack>

      {locations.length > 0 ? (
        <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={4}>
          {locations.map((location, index) => (
            <LocationCard key={location.id} location={location} cultures={cultures} />
          ))}
        </SimpleGrid>
      ) : (
        <Card.Root>
          <Card.Body py={8}>
            <VStack spacing={4}>
              <Text color="fg.muted" textAlign="center">
                还没有创建任何地点。开始创建你世界中的第一个地点吧！
              </Text>
              <HStack wrap="wrap" spacing={2} justify="center">
                {locationTypes.slice(0, 3).map(type => (
                  <Button
                    key={type.type}
                    onClick={() => onAdd(type.type)}
                    variant="outline"
                    size="sm"
                  >
                    {type.icon} 创建{type.label}
                  </Button>
                ))}
              </HStack>
            </VStack>
          </Card.Body>
        </Card.Root>
      )}
    </VStack>
  );
};

// 地点卡片
interface LocationCardProps {
  location: Location;
  cultures: Culture[];
}

const LocationCard: React.FC<LocationCardProps> = ({ location, cultures }) => {
  const getLocationIcon = (type: Location['type']) => {
    const icons = {
      city: '🏙️',
      town: '🏘️',
      village: '🏡',
      landmark: '🗿',
      region: '🗺️',
      building: '🏛️',
      natural: '🌲'
    };
    return icons[type] || '📍';
  };

  return (
    <Card.Root>
      <Card.Header>
        <HStack spacing={3}>
          <Text fontSize="2xl">{getLocationIcon(location.type)}</Text>
          <Field.Root flex={1}>
            <Input
              value={location.name}
              placeholder="地点名称"
              fontWeight="semibold"
              variant="subtle"
            />
          </Field.Root>
        </HStack>
      </Card.Header>

      <Card.Body>
        <VStack spacing={4} align="stretch">
          <Field.Root>
            <Field.Label>描述</Field.Label>
            <Textarea
              value={location.description}
              placeholder="描述这个地点..."
              rows={3}
            />
          </Field.Root>

          <SimpleGrid columns={1} spacing={3}>
            <Field.Root>
              <Field.Label>地理环境</Field.Label>
              <Input value={location.geography} placeholder="地理特征" />
            </Field.Root>

            <Field.Root>
              <Field.Label>气候</Field.Label>
              <Input value={location.climate} placeholder="气候条件" />
            </Field.Root>

            <Field.Root>
              <Field.Label>经济</Field.Label>
              <Input value={location.economy} placeholder="经济状况" />
            </Field.Root>
          </SimpleGrid>
        </VStack>
      </Card.Body>
    </Card.Root>
  );
};

// 历史标签页
const HistoryTab: React.FC<{ world: WorldBuilding, onChange: (field: string, value: any) => void }> = () => {
  return (
    <Card.Root>
      <Card.Header>
        <Card.Title>📜 历史事件</Card.Title>
      </Card.Header>
      <Card.Body>
        <Text color="fg.muted">历史功能开发中...</Text>
      </Card.Body>
    </Card.Root>
  );
};

// 系统标签页
const SystemsTab: React.FC<{ world: WorldBuilding, onChange: (field: string, value: any) => void }> = () => {
  return (
    <Card.Root>
      <Card.Header>
        <Card.Title>⚙️ 世界系统</Card.Title>
      </Card.Header>
      <Card.Body>
        <Text color="fg.muted">系统功能开发中...</Text>
      </Card.Body>
    </Card.Root>
  );
};

// 数组字段组件
interface ArrayFieldProps {
  label: string;
  values: string[];
  onChange: (values: string[]) => void;
  placeholder: string;
}

const ArrayField: React.FC<ArrayFieldProps> = ({ label, values, onChange, placeholder }) => {
  const [inputValue, setInputValue] = useState('');

  const addValue = () => {
    if (inputValue.trim() && !values.includes(inputValue.trim())) {
      onChange([...values, inputValue.trim()]);
      setInputValue('');
    }
  };

  const removeValue = (index: number) => {
    const newValues = values.filter((_, i) => i !== index);
    onChange(newValues);
  };

  return (
    <Field.Root>
      <Field.Label>{label}</Field.Label>
      <VStack spacing={3} align="stretch">
        <HStack spacing={2}>
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && addValue()}
            placeholder={placeholder}
            flex={1}
          />
          <Button onClick={addValue} variant="outline" size="sm">
            添加
          </Button>
        </HStack>

        {values.length > 0 && (
          <HStack wrap="wrap" spacing={2}>
            {values.map((value, index) => (
              <Tag.Root
                key={index}
                colorPalette="blue"
              >
                <Tag.Label>{value}</Tag.Label>
                <Tag.EndElement>
                  <Tag.CloseTrigger onClick={() => removeValue(index)} />
                </Tag.EndElement>
              </Tag.Root>
            ))}
          </HStack>
        )}
      </VStack>
    </Field.Root>
  );
};