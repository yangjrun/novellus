import { useState, useEffect } from 'react';
import { Character } from '../types/index';
import { CharacterService } from '@services/characterService';
import { EnhancedCharacterService } from '@services/enhancedCharacterService';
import { PromptGenerator } from './PromptGenerator';
import { PromptConfig, GeneratedPrompt } from '../types/prompt';
import {
  Box,
  VStack,
  HStack,
  Flex,
  Card,
  Container,
  Heading,
  Text,
  Button,
  Badge,
  Progress,
  Alert,
  Input,
  Textarea,
  NativeSelect,
  Field,
  SimpleGrid,
  Tabs,
  Separator,
  Tag
} from '@chakra-ui/react';

interface UnifiedCharacterCreatorProps {
  projectId?: string;
  character?: Character;
  onSave: (character: Character) => void;
  onCancel: () => void;
}

type CreationMode = 'professional';

export const UnifiedCharacterCreator: React.FC<UnifiedCharacterCreatorProps> = ({
  projectId,
  character,
  onSave,
  onCancel
}) => {
  const [mode, setMode] = useState<CreationMode>('professional');
  const [characterService] = useState(new CharacterService());
  const [enhancedService] = useState(new EnhancedCharacterService());
  const [currentCharacter, setCurrentCharacter] = useState<Character>(
    character || characterService.createDefaultCharacter()
  );
  const [currentStep, setCurrentStep] = useState(0);
  const [showPromptGenerator, setShowPromptGenerator] = useState(false);

  // 专业路径模式 - 完整套件协同使用，支持复杂角色体系
  const availableModes = ['professional'];

  const modeConfigs = {
    professional: {
      title: '专业角色创作套件',
      icon: '🎯',
      description: '完整10维度专业工具，支持复杂角色体系',
      sections: ['basicInfo', 'appearance', 'personality', 'background', 'abilities', 'relationships', 'lifestyle', 'psychology', 'storyRole', 'specialSettings']
    }
  };

  const handleCreateWithPrompt = () => {
    setShowPromptGenerator(true);
  };

  const handlePromptGenerated = (prompt: GeneratedPrompt) => {
    console.log('角色创作Prompt已生成:', prompt);
  };

  const handleBackToTraditional = () => {
    setShowPromptGenerator(false);
  };

  const renderModeSelector = () => (
    <Box py={6} borderBottom="1px" borderColor="gray.200">
      <Container maxW="4xl">
        <VStack gap={4}>
          <Heading size="lg" textAlign="center">
            {character ? '编辑角色' : '创建新角色'}
          </Heading>

          {!character && !showPromptGenerator && (
            <HStack gap={4} mb={4}>
              <Button
                colorPalette="blue"
                size="md"
                onClick={handleCreateWithPrompt}
              >
                🎯 AI辅助创作
              </Button>
              <Button
                variant="outline"
                size="md"
                onClick={() => {/* 继续传统流程 */}}
              >
                🔧 传统创建
              </Button>
            </HStack>
          )}

          {showPromptGenerator && (
            <HStack gap={2}>
              <Button
                variant="outline"
                size="sm"
                onClick={handleBackToTraditional}
              >
                🔧 传统创建
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={onCancel}
              >
                取消
              </Button>
            </HStack>
          )}

          <Card.Root
            variant="solid"
            colorPalette="blue"
            maxW="600px"
            mx="auto"
          >
            <Box textAlign="center" py={6} px={8}>
              <VStack gap={4}>
                <Text fontSize="4xl">🎯</Text>
                <Heading size="lg">
                  {showPromptGenerator ? 'AI辅助角色创作' : '专业角色创作套件'}
                </Heading>
                <Text color="blue.100" fontSize="lg" lineHeight="tall">
                  {showPromptGenerator
                    ? '生成专业的角色创作Prompt，获得AI辅助的深度角色设计'
                    : '基于12大知识模块构建的完整角色创作工具体系'
                  }
                </Text>
                {!showPromptGenerator && (
                  <Text color="blue.200" fontSize="md">
                    ✨ 完整套件协同使用，支持复杂角色体系<br/>
                    🧠 AI驱动的智能建议和对话生成<br/>
                    ⚔️ 冲突设计器和成长弧线规划<br/>
                    📊 多维度质量分析和一致性检查<br/>
                    🗣️ 角色面试工具和语音分析
                  </Text>
                )}
              </VStack>
            </Box>
          </Card.Root>
        </VStack>
      </Container>
    </Box>
  );

  const renderCreationContent = () => {
    if (showPromptGenerator) {
      const promptConfig: Partial<PromptConfig> = {
        category: 'character',
        difficulty: 'intermediate',
        writingStyle: 'creative',
        detailLevel: 'detailed',
        aiModel: 'claude',
        projectContext: projectId ? { id: projectId, name: 'Current Project' } : undefined
      };

      return (
        <PromptGenerator
          initialConfig={promptConfig}
          onPromptGenerated={handlePromptGenerated}
          projectContext={projectId ? { id: projectId, name: 'Current Project' } : undefined}
        />
      );
    }

    return (
      <ProfessionalCreationView
        character={currentCharacter}
        projectId={projectId}
        onChange={setCurrentCharacter}
        onSave={onSave}
        onCancel={onCancel}
      />
    );
  };

  return (
    <Box minH="100vh" bg="gray.50">
      {renderModeSelector()}
      <Container maxW="6xl" py={6}>
        {renderCreationContent()}
      </Container>
    </Box>
  );
};

// 专业角色创建视图组件 - 完整套件协同使用，支持复杂角色体系
interface ProfessionalCreationViewProps {
  character: Character;
  projectId?: string;
  onChange: (character: Character) => void;
  onSave: (character: Character) => void;
  onCancel: () => void;
}

const ProfessionalCreationView: React.FC<ProfessionalCreationViewProps> = ({
  character,
  projectId,
  onChange,
  onSave,
  onCancel
}) => {
  const [enhancedService] = useState(new EnhancedCharacterService());
  const [activeTab, setActiveTab] = useState('basicInfo');
  const [consistencyCheck, setConsistencyCheck] = useState<{ issues: string[], score: number } | null>(null);
  const [aiSuggestions, setAiSuggestions] = useState<Record<string, string[]>>({});
  const [showAIAssist, setShowAIAssist] = useState(false);

  // 专业工具套件的标签页
  const tabs = [
    { id: 'basicInfo', label: '基本信息', icon: '👤', description: '角色身份基础' },
    { id: 'appearance', label: '外貌特征', icon: '✨', description: '视觉形象塑造' },
    { id: 'personality', label: '性格特质', icon: '🧠', description: '深层心理分析' },
    { id: 'background', label: '背景故事', icon: '📖', description: '成长历程构建' },
    { id: 'abilities', label: '能力技能', icon: '⚡', description: '实力体系定义' },
    { id: 'relationships', label: '人际关系', icon: '👥', description: '社交网络编织' },
    { id: 'lifestyle', label: '生活状况', icon: '🏠', description: '日常生活描绘' },
    { id: 'psychology', label: '心理状态', icon: '💭', description: '内心世界探索' },
    { id: 'storyRole', label: '故事功能', icon: '🎭', description: '叙事作用明确' },
    { id: 'dialogue', label: '对话生成', icon: '💬', description: 'AI辅助对话创作' },
    { id: 'conflicts', label: '冲突设计', icon: '⚔️', description: '冲突矛盾编织' },
    { id: 'analysis', label: '质量分析', icon: '📊', description: '角色一致性检查' }
  ];

  // 使用增强服务进行一致性检查
  useEffect(() => {
    const check = enhancedService.checkCharacterConsistency(character);
    setConsistencyCheck(check);

    // 获取AI建议
    const suggestions = {
      personality: enhancedService.generateCharacterSuggestions(character, 'personality'),
      background: enhancedService.generateCharacterSuggestions(character, 'background'),
      abilities: enhancedService.generateCharacterSuggestions(character, 'abilities')
    };
    setAiSuggestions(suggestions);
  }, [character, enhancedService]);

  const handleFieldChange = (section: keyof Character, field: string, value: any) => {
    const updatedCharacter = {
      ...character,
      [section]: {
        ...character[section],
        [field]: value
      }
    };
    onChange(updatedCharacter);
  };

  const handleArrayFieldChange = (section: keyof Character, field: string, value: string) => {
    const arrayValue = value.split(',').map(item => item.trim()).filter(item => item);
    handleFieldChange(section, field, arrayValue);
  };

  // 应用AI建议
  const applySuggestion = (section: keyof Character, field: string, suggestion: string) => {
    const sectionData = character[section] as any;
    const currentArray = sectionData[field] || [];
    if (!currentArray.includes(suggestion)) {
      handleFieldChange(section, field, [...currentArray, suggestion]);
    }
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'basicInfo':
        return (
          <VStack gap={6} align="stretch">
            <Box>
              <Heading size="md" mb={2}>基本信息</Heading>
              <Text color="gray.600" fontSize="sm">建立角色的核心身份信息，这是所有其他属性的基础</Text>
            </Box>

            <SimpleGrid columns={{ base: 1, md: 2 }} gap={6}>
              <Field.Root>
                <Field.Label>姓名 *</Field.Label>
                <Input
                  value={character.basicInfo.name}
                  onChange={(e) => handleFieldChange('basicInfo', 'name', e.target.value)}
                  placeholder="角色的正式姓名"
                  size="lg"
                />
                <Field.HelperText>一个好名字能体现角色的文化背景和家庭出身</Field.HelperText>
              </Field.Root>

              <Field.Root>
                <Field.Label>别名/外号</Field.Label>
                <Input
                  value={character.basicInfo.alias?.join(', ') || ''}
                  onChange={(e) => handleArrayFieldChange('basicInfo', 'alias', e.target.value)}
                  placeholder="绰号, 化名, 代号"
                />
              </Field.Root>

              <Field.Root>
                <Field.Label>年龄</Field.Label>
                <Input
                  value={character.basicInfo.age}
                  onChange={(e) => handleFieldChange('basicInfo', 'age', e.target.value)}
                  placeholder="25岁 / 青年 / 中年 / 不详"
                />
              </Field.Root>

              <Field.Root>
                <Field.Label>性别</Field.Label>
                <NativeSelect.Root>
                  <NativeSelect.Field
                    value={character.basicInfo.gender}
                    onChange={(e) => handleFieldChange('basicInfo', 'gender', e.target.value)}
                  >
                    <option value="">请选择</option>
                    <option value="男">男</option>
                    <option value="女">女</option>
                    <option value="非二元">非二元</option>
                    <option value="不详">不详</option>
                  </NativeSelect.Field>
                </NativeSelect.Root>
              </Field.Root>

              <Field.Root>
                <Field.Label>职业</Field.Label>
                <Input
                  value={character.basicInfo.occupation}
                  onChange={(e) => handleFieldChange('basicInfo', 'occupation', e.target.value)}
                  placeholder="角色的主要职业或身份"
                />
              </Field.Root>

              <Field.Root>
                <Field.Label>社会地位</Field.Label>
                <Input
                  value={character.basicInfo.socialStatus}
                  onChange={(e) => handleFieldChange('basicInfo', 'socialStatus', e.target.value)}
                  placeholder="例：贵族、平民、流浪者、学者"
                />
              </Field.Root>
            </SimpleGrid>
          </VStack>
        );

      case 'dialogue':
        return (
          <VStack gap={6} align="stretch">
            <Box>
              <Heading size="md" mb={2}>对话生成器</Heading>
              <Text color="gray.600" fontSize="sm">基于角色性格生成符合其特点的对话内容</Text>
            </Box>

            <Alert.Root status="info">
              <Alert.Indicator />
              <Alert.Content>
                <Alert.Title>AI对话生成</Alert.Title>
                <Alert.Description>
                  此功能将根据角色的性格特质、价值观和背景生成符合其说话风格的对话
                </Alert.Description>
              </Alert.Content>
            </Alert.Root>

            <VStack gap={4} align="stretch">
              <Field.Root>
                <Field.Label>语言风格特征</Field.Label>
                <Textarea
                  placeholder="例：简洁直接、文雅含蓄、粗犷豪放、学究气息..."
                  rows={3}
                />
                <Field.HelperText>描述角色的说话方式和语言习惯</Field.HelperText>
              </Field.Root>

              <Field.Root>
                <Field.Label>常用口头禅</Field.Label>
                <Input placeholder="例：不是吧、没问题、这样啊" />
              </Field.Root>

              <Field.Root>
                <Field.Label>情绪表达模式</Field.Label>
                <Textarea
                  placeholder="描述角色在不同情绪下的表达方式..."
                  rows={3}
                />
              </Field.Root>

              <Button colorPalette="blue" onClick={() => {/* TODO: 实现对话生成逻辑 */}}>
                🤖 生成示例对话
              </Button>
            </VStack>
          </VStack>
        );

      case 'conflicts':
        return (
          <VStack gap={6} align="stretch">
            <Box>
              <Heading size="md" mb={2}>冲突设计器</Heading>
              <Text color="gray.600" fontSize="sm">设计角色间的冲突和矛盾，推动故事发展</Text>
            </Box>

            <VStack gap={6} align="stretch">
              <Field.Root>
                <Field.Label>内在冲突</Field.Label>
                <Textarea
                  placeholder="角色内心的矛盾和挣扎，如价值观冲突、欲望与道德的对立..."
                  rows={4}
                />
              </Field.Root>

              <Field.Root>
                <Field.Label>人际冲突</Field.Label>
                <Textarea
                  placeholder="与其他角色的冲突，包括利益冲突、情感纠葛、立场对立..."
                  rows={4}
                />
              </Field.Root>

              <Field.Root>
                <Field.Label>环境冲突</Field.Label>
                <Textarea
                  placeholder="角色与环境、制度、社会的冲突..."
                  rows={3}
                />
              </Field.Root>

              <SimpleGrid columns={{ base: 1, md: 2 }} gap={4}>
                <Field.Root>
                  <Field.Label>冲突升级路径</Field.Label>
                  <Textarea
                    placeholder="冲突如何逐步升级和发展..."
                    rows={3}
                  />
                </Field.Root>

                <Field.Root>
                  <Field.Label>解决方案</Field.Label>
                  <Textarea
                    placeholder="可能的冲突解决方向..."
                    rows={3}
                  />
                </Field.Root>
              </SimpleGrid>
            </VStack>
          </VStack>
        );

      case 'analysis':
        return (
          <VStack gap={6} align="stretch">
            <Box>
              <Heading size="md" mb={2}>角色质量分析</Heading>
              <Text color="gray.600" fontSize="sm">全方位评估角色的完整性和一致性</Text>
            </Box>

            {consistencyCheck && (
              <Card.Root variant="outline" borderColor={consistencyCheck.score < 70 ? 'red.200' : consistencyCheck.score < 90 ? 'yellow.200' : 'green.200'}>
                <Box p={4}>
                  <HStack justify="space-between" mb={4}>
                    <Text fontWeight="bold" fontSize="lg">
                      一致性评分
                    </Text>
                    <Badge
                      colorPalette={consistencyCheck.score < 70 ? 'red' : consistencyCheck.score < 90 ? 'yellow' : 'green'}
                      size="lg"
                    >
                      {consistencyCheck.score}/100
                    </Badge>
                  </HStack>

                  <Progress.Root value={consistencyCheck.score} colorPalette={consistencyCheck.score < 70 ? 'red' : consistencyCheck.score < 90 ? 'yellow' : 'green'} mb={4}>
                    <Progress.Track>
                      <Progress.Range />
                    </Progress.Track>
                  </Progress.Root>

                  {consistencyCheck.issues.length > 0 && (
                    <VStack align="stretch" gap={2}>
                      <Text fontWeight="medium">需要改进的方面：</Text>
                      {consistencyCheck.issues.map((issue, index) => (
                        <Text key={index} fontSize="sm" color="red.600">
                          ⚠️ {issue}
                        </Text>
                      ))}
                    </VStack>
                  )}
                </Box>
              </Card.Root>
            )}

            <SimpleGrid columns={{ base: 1, md: 2 }} gap={6}>
              <Card.Root variant="outline">
                <Box p={4}>
                  <Text fontWeight="medium" mb={2}>完整性检查</Text>
                  <VStack align="stretch" gap={2}>
                    <HStack justify="space-between">
                      <Text fontSize="sm">基本信息</Text>
                      <Badge colorPalette={character.basicInfo.name ? 'green' : 'red'}>
                        {character.basicInfo.name ? '✓' : '✗'}
                      </Badge>
                    </HStack>
                    <HStack justify="space-between">
                      <Text fontSize="sm">性格特质</Text>
                      <Badge colorPalette={character.personality.coreTraits.length > 0 ? 'green' : 'red'}>
                        {character.personality.coreTraits.length > 0 ? '✓' : '✗'}
                      </Badge>
                    </HStack>
                    <HStack justify="space-between">
                      <Text fontSize="sm">背景故事</Text>
                      <Badge colorPalette={character.background.family ? 'green' : 'red'}>
                        {character.background.family ? '✓' : '✗'}
                      </Badge>
                    </HStack>
                  </VStack>
                </Box>
              </Card.Root>

              <Card.Root variant="outline">
                <Box p={4}>
                  <Text fontWeight="medium" mb={2}>可信度评估</Text>
                  <VStack align="stretch" gap={2}>
                    <Text fontSize="sm">性格一致性: 良好</Text>
                    <Text fontSize="sm">背景合理性: 待完善</Text>
                    <Text fontSize="sm">能力平衡性: 良好</Text>
                  </VStack>
                </Box>
              </Card.Root>
            </SimpleGrid>

            <Button colorPalette="blue" onClick={() => {/* TODO: 生成详细分析报告 */}}>
              📋 生成详细分析报告
            </Button>
          </VStack>
        );

      // 保留原有的基础标签页内容
      case 'personality':
        return (
          <VStack gap={6} align="stretch">
            <Box>
              <Heading size="md" mb={2}>性格特质</Heading>
              <Text color="gray.600" fontSize="sm">深入探索角色的心理层面和性格特征</Text>
            </Box>

            <VStack gap={6} align="stretch">
              <SuggestionField
                label="核心特质"
                values={character.personality.coreTraits}
                suggestions={aiSuggestions.personality || []}
                onAdd={(value) => applySuggestion('personality', 'coreTraits', value)}
                onChange={(values) => handleFieldChange('personality', 'coreTraits', values)}
                placeholder="添加性格特质"
                description="定义角色最突出的3-5个性格特征"
              />

              <SimpleGrid columns={{ base: 1, md: 2 }} gap={6}>
                <Field.Root>
                  <Field.Label>价值观</Field.Label>
                  <Textarea
                    value={character.personality.values.join(', ')}
                    onChange={(e) => handleArrayFieldChange('personality', 'values', e.target.value)}
                    placeholder="正义, 自由, 家庭, 诚实, 成功"
                    rows={3}
                  />
                  <Field.HelperText>角色最重要的价值观念</Field.HelperText>
                </Field.Root>

                <Field.Root>
                  <Field.Label>信念体系</Field.Label>
                  <Textarea
                    value={character.personality.beliefs.join(', ')}
                    onChange={(e) => handleArrayFieldChange('personality', 'beliefs', e.target.value)}
                    placeholder="努力就会有回报, 人性本善"
                    rows={3}
                  />
                </Field.Root>

                <Field.Root>
                  <Field.Label>恐惧</Field.Label>
                  <Textarea
                    value={character.personality.fears.join(', ')}
                    onChange={(e) => handleArrayFieldChange('personality', 'fears', e.target.value)}
                    placeholder="失去亲人, 被背叛, 失败"
                    rows={3}
                  />
                </Field.Root>

                <Field.Root>
                  <Field.Label>渴望</Field.Label>
                  <Textarea
                    value={character.personality.desires.join(', ')}
                    onChange={(e) => handleArrayFieldChange('personality', 'desires', e.target.value)}
                    placeholder="成功, 被认可, 自由, 安全感"
                    rows={3}
                  />
                </Field.Root>
              </SimpleGrid>
            </VStack>
          </VStack>
        );

      case 'storyRole':
        return (
          <VStack gap={6} align="stretch">
            <Box>
              <Heading size="md" mb={2}>故事功能</Heading>
              <Text color="gray.600" fontSize="sm">明确角色在故事中的作用和意义</Text>
            </Box>

            <VStack gap={6} align="stretch">
              <SimpleGrid columns={{ base: 1, md: 2 }} gap={6}>
                <Field.Root>
                  <Field.Label>角色类型</Field.Label>
                  <NativeSelect.Root>
                    <NativeSelect.Field
                      value={character.storyRole.characterType}
                      onChange={(e) => handleFieldChange('storyRole', 'characterType', e.target.value)}
                    >
                      <option value="">请选择</option>
                      <option value="protagonist">主角</option>
                      <option value="antagonist">反角</option>
                      <option value="supporting">配角</option>
                      <option value="minor">次要角色</option>
                    </NativeSelect.Field>
                  </NativeSelect.Root>
                </Field.Root>

                <Field.Root>
                  <Field.Label>角色弧线类型</Field.Label>
                  <Input
                    value={character.storyRole.characterArc}
                    onChange={(e) => handleFieldChange('storyRole', 'characterArc', e.target.value)}
                    placeholder="例：成长型、堕落型、平坦型"
                  />
                </Field.Root>
              </SimpleGrid>

              <Field.Root>
                <Field.Label>冲突作用</Field.Label>
                <Textarea
                  value={character.storyRole.conflictRole}
                  onChange={(e) => handleFieldChange('storyRole', 'conflictRole', e.target.value)}
                  placeholder="描述角色在故事冲突中扮演的具体作用..."
                  rows={3}
                />
              </Field.Root>

              <Field.Root>
                <Field.Label>象征意义</Field.Label>
                <Textarea
                  value={character.storyRole.symbolism}
                  onChange={(e) => handleFieldChange('storyRole', 'symbolism', e.target.value)}
                  placeholder="角色象征的主题、概念或价值观..."
                  rows={3}
                />
              </Field.Root>

              <Field.Root>
                <Field.Label>读者连接点</Field.Label>
                <Input
                  value={character.storyRole.readerConnection}
                  onChange={(e) => handleFieldChange('storyRole', 'readerConnection', e.target.value)}
                  placeholder="例：认同、同情、敬畏、恐惧"
                />
                <Field.HelperText>角色与读者建立情感连接的方式</Field.HelperText>
              </Field.Root>
            </VStack>
          </VStack>
        );

      default:
        return (
          <VStack gap={4} align="stretch">
            <Heading size="md">{tabs.find(t => t.id === activeTab)?.label} - 开发中</Heading>
            <Text color="gray.600">
              此功能模块正在开发中，敬请期待完整的专业创作工具体验。
            </Text>
          </VStack>
        );
    }
  };

  // 计算完成度
  const calculateProgress = () => {
    let totalFields = 0;
    let completedFields = 0;

    // 基本信息权重
    if (character.basicInfo.name) completedFields += 2;
    totalFields += 2;
    if (character.basicInfo.age) completedFields++;
    totalFields++;
    if (character.basicInfo.occupation) completedFields++;
    totalFields++;

    // 性格特质权重
    if (character.personality.coreTraits.length > 0) completedFields += 2;
    totalFields += 2;
    if (character.personality.values.length > 0) completedFields++;
    totalFields++;

    // 其他维度
    if (character.appearance.height) completedFields++;
    totalFields++;
    if (character.background.family) completedFields++;
    totalFields++;

    return Math.round((completedFields / totalFields) * 100);
  };

  const completionPercentage = calculateProgress();

  return (
    <Box>
      <VStack gap={6}>
        {/* 顶部状态栏 */}
        <Card.Root w="full" maxW="7xl" variant="elevated">
          <Box p={6}>
            <Flex justify="space-between" align="center" direction={{ base: "column", md: "row" }} gap={4}>
              <Box>
                <HStack gap={3} mb={2}>
                  <Text fontSize="2xl">🎯</Text>
                  <Heading size="lg">专业角色创作套件</Heading>
                  {character.basicInfo.name && (
                    <Badge colorPalette="blue" size="lg">
                      {character.basicInfo.name}
                    </Badge>
                  )}
                </HStack>
                <Text color="gray.600">
                  基于12大知识模块的完整角色创作工具体系
                </Text>
              </Box>

              <VStack align="end" gap={2}>
                <HStack gap={4}>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowAIAssist(!showAIAssist)}
                  >
                    🤖 AI助手 {showAIAssist ? '(开启)' : '(关闭)'}
                  </Button>
                  <Text fontSize="sm" color="gray.600">
                    完成度：{completionPercentage}%
                  </Text>
                </HStack>
                <Progress.Root value={completionPercentage} colorPalette="blue" w="300px" size="lg">
                  <Progress.Track>
                    <Progress.Range />
                  </Progress.Track>
                </Progress.Root>
              </VStack>
            </Flex>
          </Box>
        </Card.Root>

        {/* 一致性检查提醒 */}
        {consistencyCheck && consistencyCheck.score < 80 && (
          <Alert.Root status="warning" w="full" maxW="7xl">
            <Alert.Indicator />
            <Alert.Content>
              <Alert.Title>角色一致性提醒</Alert.Title>
              <Alert.Description>
                当前角色一致性评分为 {consistencyCheck.score}/100，建议完善以下方面以提高角色的可信度。
              </Alert.Description>
            </Alert.Content>
          </Alert.Root>
        )}

        {/* 专业工具导航 */}
        <Tabs.Root value={activeTab} onValueChange={(e) => setActiveTab(e.value)} w="full" maxW="7xl">
          <Box overflowX="auto">
            <Tabs.List minW="max-content">
              {tabs.map((tab) => (
                <Tabs.Trigger key={tab.id} value={tab.id} px={4} py={3}>
                  <VStack gap={1} minW="80px">
                    <Text fontSize="lg">{tab.icon}</Text>
                    <Text fontSize="xs" textAlign="center" lineHeight="tight">
                      {tab.label}
                    </Text>
                  </VStack>
                </Tabs.Trigger>
              ))}
            </Tabs.List>
          </Box>

          <Tabs.Content value={activeTab} py={6}>
            <Card.Root variant="elevated">
              <Box p={8}>
                {renderTabContent()}
              </Box>
            </Card.Root>
          </Tabs.Content>
        </Tabs.Root>

        {/* 底部操作区 */}
        <Card.Root w="full" maxW="7xl">
          <Box p={4}>
            <Flex justify="space-between" align="center" direction={{ base: "column", sm: "row" }} gap={4}>
              <HStack gap={4}>
                <Button variant="outline" onClick={onCancel}>
                  取消
                </Button>
                <Button onClick={() => {/* TODO: 导出角色数据 */}} variant="outline">
                  📄 导出
                </Button>
                <Button
                  onClick={() => {
                    // 切换到角色面试工具
                    if (window.parent && window.parent.postMessage) {
                      window.parent.postMessage({ action: 'switchTool', tool: 'interview', character }, '*');
                    }
                  }}
                  variant="outline"
                >
                  🗣️ 角色面试
                </Button>
              </HStack>

              <Button
                onClick={() => onSave(character)}
                colorPalette="blue"
                size="lg"
                disabled={!character.basicInfo.name.trim()}
              >
                💾 保存角色
              </Button>
            </Flex>
          </Box>
        </Card.Root>
      </VStack>
    </Box>
  );
};

// 增强的建议字段组件
interface SuggestionFieldProps {
  label: string;
  values: string[];
  suggestions: string[];
  onAdd: (value: string) => void;
  onChange: (values: string[]) => void;
  placeholder: string;
  description?: string;
}

const SuggestionField: React.FC<SuggestionFieldProps> = ({
  label,
  values,
  suggestions,
  onAdd,
  onChange,
  placeholder,
  description
}) => {
  const [inputValue, setInputValue] = useState('');

  const addValue = () => {
    if (inputValue.trim() && !values.includes(inputValue.trim())) {
      onChange([...values, inputValue.trim()]);
      setInputValue('');
    }
  };

  const removeValue = (index: number) => {
    const newValues = [...values];
    newValues.splice(index, 1);
    onChange(newValues);
  };

  return (
    <Field.Root>
      <Field.Label>{label}</Field.Label>
      {description && <Field.HelperText mb={2}>{description}</Field.HelperText>}

      <VStack spacing={4} align="stretch">
        {/* 输入区域 */}
        <HStack spacing={2}>
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && addValue()}
            placeholder={placeholder}
            flex="1"
          />
          <Button onClick={addValue} colorPalette="blue" size="md">
            添加
          </Button>
        </HStack>

        {/* 已添加的值 */}
        {values.length > 0 && (
          <Flex wrap="wrap" gap={2}>
            {values.map((value, index) => (
              <Tag.Root key={index} colorPalette="blue" variant="subtle">
                <Tag.Label>{value}</Tag.Label>
                <Tag.EndElement>
                  <Tag.CloseTrigger onClick={() => removeValue(index)} />
                </Tag.EndElement>
              </Tag.Root>
            ))}
          </Flex>
        )}

        {/* AI建议 */}
        {suggestions.length > 0 && (
          <Box
            p={3}
            bg="gray.50"
            borderRadius="md"
            border="1px solid"
            borderColor="gray.200"
          >
            <Text fontSize="sm" color="gray.600" mb={2} fontWeight="medium">
              🤖 AI建议：
            </Text>
            <Flex wrap="wrap" gap={2}>
              {suggestions.filter(s => !values.includes(s)).slice(0, 8).map((suggestion, index) => (
                <Button
                  key={index}
                  size="xs"
                  variant="outline"
                  borderRadius="full"
                  fontSize="xs"
                  onClick={() => onAdd(suggestion)}
                >
                  + {suggestion}
                </Button>
              ))}
            </Flex>
          </Box>
        )}
      </VStack>
    </Field.Root>
  );
};