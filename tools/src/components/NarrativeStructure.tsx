import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Flex,
  Heading,
  Text,
  Button,
  Spinner,
  Grid,
  SimpleGrid,
  Badge,
  Checkbox,
  Textarea,
  AbsoluteCenter,
  ProgressCircle,
  Center,
  Stack,
  RadioCard
} from '@chakra-ui/react';
import { NarrativeStructure, PlotPoint } from '../types/index';
import { NarrativeService } from '@services/narrativeService';
import { PromptGenerator } from './PromptGenerator';
import { PromptConfig, GeneratedPrompt } from '../types/prompt';

interface NarrativeStructureProps {
  projectId: string;
  onComplete: () => void;
  onCancel: () => void;
}

export const NarrativeStructureComponent: React.FC<NarrativeStructureProps> = ({
  projectId,
  onComplete,
  onCancel
}) => {
  const [narrativeService] = useState(new NarrativeService());
  const [narratives, setNarratives] = useState<NarrativeStructure[]>([]);
  const [currentNarrative, setCurrentNarrative] = useState<NarrativeStructure | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [loading, setLoading] = useState(true);
  const [showPromptGenerator, setShowPromptGenerator] = useState(false);

  useEffect(() => {
    loadNarratives();
  }, []);

  const loadNarratives = async () => {
    try {
      const narrativesList = await narrativeService.getNarrativesByProject(projectId);
      setNarratives(narrativesList);
      if (narrativesList.length > 0) {
        setCurrentNarrative(narrativesList[0]);
      }
    } catch (error) {
      console.error('加载叙事结构失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateNarrative = async (
    type: NarrativeStructure['type'],
    culturalTradition: NarrativeStructure['culturalTradition']
  ) => {
    try {
      const newNarrative = narrativeService.createNarrativeTemplate(projectId, type, culturalTradition);
      await narrativeService.saveNarrative(newNarrative);
      await loadNarratives();
      setCurrentNarrative(newNarrative);
      setIsCreating(false);
    } catch (error) {
      console.error('创建叙事结构失败:', error);
      alert('创建失败，请重试');
    }
  };

  const handleCreateWithPrompt = () => {
    setShowPromptGenerator(true);
  };

  const handlePromptGenerated = (prompt: GeneratedPrompt) => {
    // Prompt生成完成后可以选择：
    // 1. 返回传统创建流程
    // 2. 保存Prompt到历史记录
    // 3. 直接完成创建流程
    console.log('叙事结构Prompt已生成:', prompt);
  };

  const handleBackToTraditional = () => {
    setShowPromptGenerator(false);
    setIsCreating(true);
  };

  const handlePlotPointToggle = async (plotPointId: string) => {
    if (!currentNarrative) return;

    try {
      const plotPoint = currentNarrative.plotPoints.find(p => p.id === plotPointId);
      if (plotPoint) {
        await narrativeService.updatePlotPoint(
          currentNarrative.id,
          plotPointId,
          { completed: !plotPoint.completed }
        );
        await loadNarratives();
        // 更新当前叙事结构
        const updated = await narrativeService.getNarrativeById(currentNarrative.id);
        if (updated) setCurrentNarrative(updated);
      }
    } catch (error) {
      console.error('更新情节点失败:', error);
    }
  };

  const handlePlotPointUpdate = async (plotPointId: string, updates: Partial<PlotPoint>) => {
    if (!currentNarrative) return;

    try {
      await narrativeService.updatePlotPoint(currentNarrative.id, plotPointId, updates);
      const updated = await narrativeService.getNarrativeById(currentNarrative.id);
      if (updated) setCurrentNarrative(updated);
    } catch (error) {
      console.error('更新情节点失败:', error);
    }
  };

  const getStructureTypeLabel = (type: NarrativeStructure['type']) => {
    const labels = {
      'three-act': '三幕式',
      'heros-journey': '英雄之旅',
      'kishotenketsu': '起承转合',
      'seven-point': '七点结构',
      'freytag': '弗莱塔格金字塔',
      'custom': '自定义'
    };
    return labels[type] || type;
  };

  const getCulturalTraditionLabel = (tradition: NarrativeStructure['culturalTradition']) => {
    const labels = {
      western: '西方',
      eastern: '东方',
      african: '非洲',
      arabic: '阿拉伯',
      indigenous: '原住民',
      mixed: '混合'
    };
    return labels[tradition] || tradition;
  };

  if (loading) {
    return (
      <Center minH="400px">
        <VStack gap={4}>
          <Spinner size="lg" color="blue.500" />
          <Text color="fg.muted">正在加载叙事结构...</Text>
        </VStack>
      </Center>
    );
  }

  // 显示Prompt生成器
  if (showPromptGenerator) {
    const promptConfig: Partial<PromptConfig> = {
      category: 'structure',
      difficulty: 'intermediate',
      writingStyle: 'narrative',
      detailLevel: 'detailed',
      aiModel: 'claude',
      projectContext: { id: projectId, name: 'Current Project' }
    };

    return (
      <Box>
        <VStack gap={4} mb={6} align="stretch">
          <HStack justify="space-between">
            <Heading size="lg">📚 叙事结构 - AI辅助创作</Heading>
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
            使用AI生成专业的故事结构设计Prompt，帮助您构建引人入胜的叙事框架
          </Text>
        </VStack>

        <PromptGenerator
          initialConfig={promptConfig}
          onPromptGenerated={handlePromptGenerated}
          projectContext={{ id: projectId, name: 'Current Project' }}
        />
      </Box>
    );
  }

  if (isCreating) {
    return <NarrativeCreator onCreate={handleCreateNarrative} onCancel={() => setIsCreating(false)} />;
  }

  if (!currentNarrative) {
    return (
      <Center minH="400px">
        <VStack gap={6} textAlign="center">
          <Heading size="lg">📚 叙事结构构建工具</Heading>
          <Text color="fg.muted" maxW="md">
            还没有创建任何叙事结构。选择一个方式开始创建！
          </Text>
          <HStack gap={4}>
            <Button
              colorPalette="blue"
              size="lg"
              onClick={handleCreateWithPrompt}
            >
              🎯 AI辅助创作
            </Button>
            <Button
              variant="outline"
              size="lg"
              onClick={() => setIsCreating(true)}
            >
              🔧 传统创建
            </Button>
          </HStack>
          <Text fontSize="sm" color="gray.500">
            推荐使用AI辅助创作，生成专业的创作Prompt
          </Text>
        </VStack>
      </Center>
    );
  }

  const progress = narrativeService.getProgress(currentNarrative);

  return (
    <Box maxW="1200px" mx="auto" p={5}>
      <Box
        bg="bg.panel"
        borderRadius="xl"
        border="1px"
        borderColor="border.muted"
        p={5}
        mb={8}
      >
        <Flex
          direction={{ base: "column", lg: "row" }}
          justify="space-between"
          align="flex-start"
          gap={6}
        >
          <Flex gap={8} flex={1} direction={{ base: "column", md: "row" }}>
            <VStack align="start" flex={1}>
              <Heading size="lg" color="fg">
                {currentNarrative.name}
              </Heading>
              <HStack gap={4} mb={2}>
                <Badge
                  colorPalette="blue"
                  variant="subtle"
                  borderRadius="full"
                  px={3}
                  py={1}
                  fontSize="xs"
                >
                  {getStructureTypeLabel(currentNarrative.type)}
                </Badge>
                <Badge
                  colorPalette="purple"
                  variant="subtle"
                  borderRadius="full"
                  px={3}
                  py={1}
                  fontSize="xs"
                >
                  {getCulturalTraditionLabel(currentNarrative.culturalTradition)}传统
                </Badge>
              </HStack>
              <Text color="fg.muted" lineHeight={1.6}>
                {currentNarrative.description}
              </Text>
            </VStack>

            <VStack align="center" gap={4}>
              <ProgressCircle.Root value={progress.percentage} size="lg">
                <ProgressCircle.Circle>
                  <ProgressCircle.Track stroke="border.muted" />
                  <ProgressCircle.Range stroke="blue.solid" strokeLinecap="round" />
                </ProgressCircle.Circle>
                <AbsoluteCenter>
                  <Text fontSize="lg" fontWeight="semibold" color="blue.solid">
                    {progress.percentage}%
                  </Text>
                </AbsoluteCenter>
              </ProgressCircle.Root>
              <Text fontSize="sm" color="fg.muted" textAlign="center">
                已完成 {progress.completed}/{progress.total} 个情节点
              </Text>
            </VStack>
          </Flex>

          <VStack gap={3} align="stretch">
            <Button
              variant="outline"
              onClick={() => setIsCreating(true)}
            >
              新建结构
            </Button>
            <Button
              variant="outline"
              onClick={onCancel}
            >
              返回
            </Button>
          </VStack>
        </Flex>
      </Box>

      <VStack gap={8} align="stretch">
        <Box
          bg="bg.panel"
          borderRadius="xl"
          border="1px"
          borderColor="border.muted"
          p={5}
        >
          <Heading size="md" mb={5} color="fg">
            📊 结构可视化
          </Heading>
          <Box
            position="relative"
            h="120px"
            bg="bg.muted"
            borderRadius="md"
            overflow="hidden"
          >
            {currentNarrative.plotPoints.map((plotPoint, index) => (
              <Box
                key={plotPoint.id}
                position="absolute"
                top={0}
                left={`${plotPoint.position}%`}
                transform="translateX(-50%)"
                w="2px"
                h="full"
                role="group"
              >
                <Box position="relative" h="full">
                  <Box
                    position="absolute"
                    top="50%"
                    left="50%"
                    transform="translate(-50%, -50%)"
                    w="12px"
                    h="12px"
                    borderRadius="full"
                    bg={plotPoint.completed ? "green.solid" : "border.muted"}
                    border="2px"
                    borderColor="bg.panel"
                    zIndex={2}
                    transition="all 0.3s"
                  />
                  <Box
                    position="absolute"
                    top={0}
                    left="50%"
                    transform="translateX(-50%)"
                    w="2px"
                    h="full"
                    bg={plotPoint.completed ? "green.solid" : "border.muted"}
                    opacity={plotPoint.completed ? 0.8 : 0.5}
                  />
                </Box>
                <Box
                  position="absolute"
                  top="full"
                  left="50%"
                  transform="translateX(-50%)"
                  minW="120px"
                  maxW="200px"
                  p={3}
                  bg="bg.panel"
                  border="1px"
                  borderColor="border.muted"
                  borderRadius="md"
                  textAlign="center"
                  opacity={0}
                  pointerEvents="none"
                  transition="all 0.3s"
                  mt={2}
                  boxShadow="lg"
                  zIndex={3}
                  _groupHover={{ opacity: 1, pointerEvents: "auto" }}
                >
                  <Flex justify="space-between" align="center" mb={1}>
                    <Text fontSize="xs" fontWeight="semibold" color="fg">
                      {plotPoint.name}
                    </Text>
                    <Text fontSize="2xs" color="fg.muted">
                      {plotPoint.position}%
                    </Text>
                  </Flex>
                  <Text fontSize="2xs" color="fg.muted" lineHeight="1.3">
                    {plotPoint.description}
                  </Text>
                </Box>
              </Box>
            ))}
          </Box>
        </Box>

        <Box>
          <Heading size="md" mb={5} color="fg">
            📝 情节节点规划
          </Heading>
          <SimpleGrid columns={{ base: 1, lg: 2 }} gap={5}>
            {currentNarrative.plotPoints.map((plotPoint) => (
              <PlotPointCard
                key={plotPoint.id}
                plotPoint={plotPoint}
                onToggle={() => handlePlotPointToggle(plotPoint.id)}
                onUpdate={(updates) => handlePlotPointUpdate(plotPoint.id, updates)}
              />
            ))}
          </SimpleGrid>
        </Box>

        {currentNarrative.timelineEvents.length > 0 && (
          <Box
            bg="bg.panel"
            border="1px"
            borderColor="border.muted"
            borderRadius="xl"
            p={5}
          >
            <Heading size="md" mb={5} color="fg">
              ⏰ 时间线事件
            </Heading>
            <VStack gap={4} align="stretch">
              {currentNarrative.timelineEvents.map((event) => {
                const getBorderColor = (importance: string) => {
                  switch (importance) {
                    case 'critical': return 'red.solid';
                    case 'major': return 'orange.solid';
                    case 'minor': return 'blue.solid';
                    default: return 'border.muted';
                  }
                };

                return (
                  <Box
                    key={event.id}
                    p={4}
                    borderRadius="md"
                    borderLeftWidth="4px"
                    borderLeftColor={getBorderColor(event.importance)}
                    bg="bg.muted"
                  >
                    <Flex justify="space-between" align="center" mb={2}>
                      <Heading size="sm" color="fg">
                        {event.title}
                      </Heading>
                      <Text fontSize="xs" color="fg.muted" fontWeight="medium">
                        Ch.{event.chapter || '?'}
                      </Text>
                    </Flex>
                    <Text color="fg.muted" fontSize="sm" lineHeight={1.5} mb={2}>
                      {event.description}
                    </Text>
                    <Flex gap={2} flexWrap="wrap">
                      {event.tags.map((tag, index) => (
                        <Badge
                          key={index}
                          colorPalette="blue"
                          variant="subtle"
                          borderRadius="full"
                          fontSize="2xs"
                          fontWeight="medium"
                        >
                          {tag}
                        </Badge>
                      ))}
                    </Flex>
                  </Box>
                );
              })}
            </VStack>
          </Box>
        )}
      </VStack>
    </Box>
  );
};

// 情节点卡片组件
interface PlotPointCardProps {
  plotPoint: PlotPoint;
  onToggle: () => void;
  onUpdate: (updates: Partial<PlotPoint>) => void;
}

const PlotPointCard: React.FC<PlotPointCardProps> = ({ plotPoint, onToggle, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [notes, setNotes] = useState(plotPoint.notes);

  const handleNotesUpdate = () => {
    onUpdate({ notes });
    setIsEditing(false);
  };

  const getTypeLabel = (type: PlotPoint['type']) => {
    const labels = {
      'inciting-incident': '煽动事件',
      'plot-point-1': '第一转折点',
      'midpoint': '中点',
      'plot-point-2': '第二转折点',
      'climax': '高潮',
      'resolution': '结局',
      'custom': '自定义'
    };
    return labels[type] || type;
  };

  return (
    <Box
      bg={plotPoint.completed ? "green.subtle" : "bg.panel"}
      border="1px"
      borderColor={plotPoint.completed ? "green.solid" : "border.muted"}
      borderRadius="xl"
      p={5}
      transition="all 0.3s"
      _hover={{
        borderColor: plotPoint.completed ? "green.solid" : "blue.solid",
        boxShadow: "md"
      }}
    >
      <Flex justify="space-between" align="flex-start" mb={4}>
        <VStack align="start" flex={1}>
          <Heading size="sm" color="fg" mb={2}>
            {plotPoint.name}
          </Heading>
          <HStack gap={2} mb={2}>
            <Badge
              colorPalette="blue"
              variant="subtle"
              borderRadius="full"
              fontSize="2xs"
              fontWeight="medium"
            >
              {getTypeLabel(plotPoint.type)}
            </Badge>
            <Badge
              colorPalette="purple"
              variant="subtle"
              borderRadius="full"
              fontSize="2xs"
              fontWeight="medium"
            >
              {plotPoint.position}%
            </Badge>
          </HStack>
        </VStack>
        <Checkbox.Root
          checked={plotPoint.completed}
          onCheckedChange={onToggle}
          colorPalette="green"
          size="md"
        >
          <Checkbox.HiddenInput />
          <Checkbox.Control />
        </Checkbox.Root>
      </Flex>

      <VStack align="stretch" gap={3}>
        <Text color="fg.muted" lineHeight={1.6}>
          {plotPoint.description}
        </Text>

        {plotPoint.relatedCharacters.length > 0 && (
          <Text fontSize="sm" color="fg.muted">
            <Text as="span" fontWeight="semibold" color="fg">
              相关角色:
            </Text>{' '}
            {plotPoint.relatedCharacters.join(', ')}
          </Text>
        )}

        {plotPoint.relatedScenes.length > 0 && (
          <Text fontSize="sm" color="fg.muted">
            <Text as="span" fontWeight="semibold" color="fg">
              相关场景:
            </Text>{' '}
            {plotPoint.relatedScenes.join(', ')}
          </Text>
        )}

        <Box pt={3} borderTop="1px" borderTopColor="border.muted">
          <Flex justify="space-between" align="center" mb={2}>
            <Text fontWeight="semibold" color="fg" fontSize="sm">
              备注:
            </Text>
            <Button
              variant="ghost"
              size="xs"
              colorPalette="blue"
              onClick={() => setIsEditing(!isEditing)}
            >
              {isEditing ? '取消' : '编辑'}
            </Button>
          </Flex>

          {isEditing ? (
            <VStack align="stretch" gap={3}>
              <Textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="添加关于此情节点的备注..."
                rows={3}
                resize="vertical"
                bg="bg"
                borderColor="border.muted"
              />
              <Flex justify="flex-end">
                <Button
                  size="sm"
                  colorPalette="blue"
                  onClick={handleNotesUpdate}
                >
                  保存
                </Button>
              </Flex>
            </VStack>
          ) : (
            <Text
              fontSize="sm"
              color="fg.muted"
              fontStyle={plotPoint.notes ? "normal" : "italic"}
            >
              {plotPoint.notes || '暂无备注...'}
            </Text>
          )}
        </Box>
      </VStack>
    </Box>
  );
};

// 创建叙事结构组件
interface NarrativeCreatorProps {
  onCreate: (type: NarrativeStructure['type'], cultural: NarrativeStructure['culturalTradition']) => void;
  onCancel: () => void;
}

const NarrativeCreator: React.FC<NarrativeCreatorProps> = ({ onCreate, onCancel }) => {
  const [selectedType, setSelectedType] = useState<NarrativeStructure['type']>('three-act');
  const [selectedCultural, setSelectedCultural] = useState<NarrativeStructure['culturalTradition']>('western');

  const structureTypes = [
    { value: 'three-act', label: '三幕式结构', desc: '经典的西方叙事结构，适合大多数故事类型' },
    { value: 'heros-journey', label: '英雄之旅', desc: '约瑟夫·坎贝尔的单一神话模式，适合冒险和成长故事' },
    { value: 'kishotenketsu', label: '起承转合', desc: '东亚传统四段式结构，注重意境和转折' },
    { value: 'seven-point', label: '七点结构', desc: '丹·威尔斯的现代故事结构，注重钩子和节奏' },
    { value: 'freytag', label: '弗莱塔格金字塔', desc: '经典戏剧结构，适合戏剧性强的故事' },
    { value: 'custom', label: '自定义结构', desc: '根据你的具体需求定制故事结构' }
  ];

  const culturalTraditions = [
    { value: 'western', label: '西方传统', desc: '注重个人主义和线性发展' },
    { value: 'eastern', label: '东方传统', desc: '注重和谐、循环和内在成长' },
    { value: 'african', label: '非洲传统', desc: '注重社群智慧和口述传统' },
    { value: 'arabic', label: '阿拉伯传统', desc: '注重诗意表达和道德教化' },
    { value: 'indigenous', label: '原住民传统', desc: '注重自然联系和精神层面' },
    { value: 'mixed', label: '混合传统', desc: '融合多种文化传统的优点' }
  ];

  return (
    <Box maxW="900px" mx="auto" p={5}>
      <VStack gap={8} align="stretch">
        <Box textAlign="center">
          <Heading size="lg" mb={3} color="fg">
            🎭 创建新的叙事结构
          </Heading>
          <Text color="fg.muted">
            选择最适合你的故事的结构类型和文化传统
          </Text>
        </Box>

        <VStack gap={6} align="stretch">
          <Box>
            <Heading size="md" mb={4} color="fg">
              选择结构类型
            </Heading>
            <RadioCard.Root
              value={selectedType}
              onValueChange={(e) => setSelectedType(e.value as NarrativeStructure['type'])}
            >
              <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} gap={4}>
                {structureTypes.map((type) => (
                  <RadioCard.Item
                    key={type.value}
                    value={type.value}
                    p={5}
                    borderRadius="xl"
                    cursor="pointer"
                    transition="all 0.3s"
                    _hover={{ borderColor: "blue.solid", boxShadow: "md" }}
                    _checked={{
                      borderColor: "blue.solid",
                      bg: "blue.subtle"
                    }}
                  >
                    <RadioCard.ItemHiddenInput />
                    <RadioCard.ItemControl>
                      <RadioCard.ItemContent>
                        <VStack align="start" gap={2}>
                          <RadioCard.ItemText>
                            <Heading size="sm" color="fg">
                              {type.label}
                            </Heading>
                          </RadioCard.ItemText>
                          <RadioCard.ItemDescription>
                            <Text fontSize="sm" color="fg.muted" lineHeight={1.5}>
                              {type.desc}
                            </Text>
                          </RadioCard.ItemDescription>
                        </VStack>
                      </RadioCard.ItemContent>
                      <RadioCard.ItemIndicator />
                    </RadioCard.ItemControl>
                  </RadioCard.Item>
                ))}
              </SimpleGrid>
            </RadioCard.Root>
          </Box>

          <Box>
            <Heading size="md" mb={4} color="fg">
              选择文化传统
            </Heading>
            <RadioCard.Root
              value={selectedCultural}
              onValueChange={(e) => setSelectedCultural(e.value as NarrativeStructure['culturalTradition'])}
            >
              <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} gap={4}>
                {culturalTraditions.map((cultural) => (
                  <RadioCard.Item
                    key={cultural.value}
                    value={cultural.value}
                    p={5}
                    borderRadius="xl"
                    cursor="pointer"
                    transition="all 0.3s"
                    _hover={{ borderColor: "purple.solid", boxShadow: "md" }}
                    _checked={{
                      borderColor: "purple.solid",
                      bg: "purple.subtle"
                    }}
                  >
                    <RadioCard.ItemHiddenInput />
                    <RadioCard.ItemControl>
                      <RadioCard.ItemContent>
                        <VStack align="start" gap={2}>
                          <RadioCard.ItemText>
                            <Heading size="sm" color="fg">
                              {cultural.label}
                            </Heading>
                          </RadioCard.ItemText>
                          <RadioCard.ItemDescription>
                            <Text fontSize="sm" color="fg.muted" lineHeight={1.5}>
                              {cultural.desc}
                            </Text>
                          </RadioCard.ItemDescription>
                        </VStack>
                      </RadioCard.ItemContent>
                      <RadioCard.ItemIndicator />
                    </RadioCard.ItemControl>
                  </RadioCard.Item>
                ))}
              </SimpleGrid>
            </RadioCard.Root>
          </Box>
        </VStack>

        <Flex justify="space-between" gap={4} direction={{ base: "column", sm: "row" }}>
          <Button variant="outline" onClick={onCancel} flex={{ base: 1, sm: "none" }}>
            取消
          </Button>
          <Button
            colorPalette="blue"
            onClick={() => onCreate(selectedType, selectedCultural)}
            flex={{ base: 1, sm: "none" }}
          >
            创建结构
          </Button>
        </Flex>
      </VStack>
    </Box>
  );
};