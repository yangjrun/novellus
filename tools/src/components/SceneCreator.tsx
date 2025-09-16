import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  VStack,
  HStack,
  Card,
  Button,
  Heading,
  Text,
  Input,
  Textarea,
  NativeSelect,
  Field,
  Slider,
  IconButton,
  SimpleGrid,
  Tag,
  Spinner,
  Center,
  Badge
} from '@chakra-ui/react';
import { Scene } from '../types/index';
import { SceneService } from '@services/sceneService';
import { PromptGenerator } from './PromptGenerator';

interface SceneCreatorProps {
  projectId: string;
  onComplete: () => void;
  onCancel: () => void;
}

export const SceneCreator: React.FC<SceneCreatorProps> = ({
  projectId,
  onComplete,
  onCancel
}) => {
  const [sceneService] = useState(new SceneService());
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [currentScene, setCurrentScene] = useState<Scene | null>(null);
  const [loading, setLoading] = useState(true);
  const [showPromptGenerator, setShowPromptGenerator] = useState(false);

  useEffect(() => {
    loadScenes();
  }, []);

  const loadScenes = async () => {
    try {
      const scenesList = await sceneService.getScenesByProject(projectId);
      setScenes(scenesList);
    } catch (error) {
      console.error('加载场景失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateScene = (type: 'action' | 'dialogue' | 'description' | 'emotional' | 'transition') => {
    const newScene = sceneService.createSceneTemplate(projectId, type);
    setCurrentScene(newScene);
  };

  const handleCreateWithPrompt = () => {
    setShowPromptGenerator(true);
  };

  const handleSaveScene = async () => {
    if (!currentScene) return;

    try {
      await sceneService.saveScene(currentScene);
      await loadScenes();
      setCurrentScene(null);
    } catch (error) {
      console.error('保存场景失败:', error);
      alert('保存失败，请重试');
    }
  };

  if (loading) {
    return (
      <Container maxW="container.xl" py={8}>
        <Center h="400px">
          <VStack gap={4}>
            <Spinner size="xl" colorPalette="blue" />
            <Text color="fg.muted">正在加载场景创作工具...</Text>
          </VStack>
        </Center>
      </Container>
    );
  }

  if (showPromptGenerator) {
    return (
      <PromptGenerator
        category="scene"
        projectId={projectId}
        onBack={() => setShowPromptGenerator(false)}
        onComplete={() => {
          setShowPromptGenerator(false);
          onComplete();
        }}
      />
    );
  }

  if (currentScene) {
    return (
      <SceneEditor
        scene={currentScene}
        onChange={setCurrentScene}
        onSave={handleSaveScene}
        onCancel={() => setCurrentScene(null)}
      />
    );
  }

  return (
    <Container maxW="container.xl" py={8}>
      <VStack gap={8} align="stretch">
        {/* Header Section */}
        <Box>
          <HStack justify="space-between" align="flex-start" mb={4}>
            <VStack align="flex-start" gap={2}>
              <Heading size="2xl" color="fg">🎬 多维场景创作工具</Heading>
              <Text color="fg.muted" fontSize="lg">创建富有感官体验和情感深度的故事场景</Text>
            </VStack>
            <Button onClick={onCancel} variant="outline" size="md">
              返回
            </Button>
          </HStack>
        </Box>

        {/* Scene Types Section */}
        <Box>
          <HStack justify="space-between" align="center" mb={6}>
            <Heading size="lg">选择场景类型</Heading>
            <Button
              colorPalette="blue"
              variant="outline"
              onClick={handleCreateWithPrompt}
              size="md"
            >
              🤖 AI辅助创作
            </Button>
          </HStack>
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} gap={6}>
            {[
              { type: 'action', name: '动作场景', icon: '⚔️', desc: '高能量的行动和冲突场景' },
              { type: 'dialogue', name: '对话场景', icon: '💬', desc: '角色间的深度交流场景' },
              { type: 'description', name: '描写场景', icon: '🖼️', desc: '重点展现环境和氛围' },
              { type: 'emotional', name: '情感场景', icon: '💖', desc: '探索角色内心世界' },
              { type: 'transition', name: '过渡场景', icon: '🌉', desc: '连接不同情节段落' }
            ].map(sceneType => (
              <Card.Root
                key={sceneType.type}
                variant="outline"
                cursor="pointer"
                transition="all 0.2s"
                _hover={{ transform: "translateY(-2px)", shadow: "lg" }}
                onClick={() => handleCreateScene(sceneType.type as any)}
              >
                <Card.Body p={6}>
                  <VStack gap={3}>
                    <Text fontSize="3xl">{sceneType.icon}</Text>
                    <Heading size="md" textAlign="center">{sceneType.name}</Heading>
                    <Text color="fg.muted" textAlign="center" fontSize="sm">{sceneType.desc}</Text>
                  </VStack>
                </Card.Body>
              </Card.Root>
            ))}
          </SimpleGrid>
        </Box>

        {/* Existing Scenes Section */}
        <Box>
          <Heading size="lg" mb={6}>已创建的场景</Heading>
          {scenes.length === 0 ? (
            <Card.Root variant="subtle">
              <Card.Body py={12}>
                <Center>
                  <VStack gap={6}>
                    <Text fontSize="4xl">🎭</Text>
                    <Text color="fg.muted" textAlign="center">
                      还没有创建任何场景。选择创作方式开始吧！
                    </Text>
                    <HStack gap={4}>
                      <Button
                        colorPalette="blue"
                        onClick={handleCreateWithPrompt}
                        size="lg"
                      >
                        🤖 AI辅助创作
                      </Button>
                      <Text color="fg.muted">或</Text>
                      <Text color="fg.muted">选择上方场景类型进行传统创作</Text>
                    </HStack>
                  </VStack>
                </Center>
              </Card.Body>
            </Card.Root>
          ) : (
            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} gap={6}>
              {scenes.map(scene => (
                <Card.Root
                  key={scene.id}
                  variant="outline"
                  cursor="pointer"
                  transition="all 0.2s"
                  _hover={{ shadow: "md" }}
                  onClick={() => setCurrentScene(scene)}
                >
                  <Card.Body p={4}>
                    <VStack align="stretch" gap={3}>
                      <Heading size="sm" noOfLines={2}>
                        {scene.title || '未命名场景'}
                      </Heading>
                      <Text color="fg.muted" fontSize="sm" noOfLines={3}>
                        {scene.description.substring(0, 100)}...
                      </Text>
                      <HStack justify="space-between" fontSize="xs" color="fg.muted">
                        <HStack>
                          <Text>📍</Text>
                          <Text>{scene.locationId || '未设定地点'}</Text>
                        </HStack>
                        <HStack>
                          <Text>⏰</Text>
                          <Text>{scene.timeOfDay}</Text>
                        </HStack>
                      </HStack>
                    </VStack>
                  </Card.Body>
                </Card.Root>
              ))}
            </SimpleGrid>
          )}
        </Box>
      </VStack>
    </Container>
  );
};

// 场景编辑器组件
interface SceneEditorProps {
  scene: Scene;
  onChange: (scene: Scene) => void;
  onSave: () => void;
  onCancel: () => void;
}

const SceneEditor: React.FC<SceneEditorProps> = ({ scene, onChange, onSave, onCancel }) => {
  const updateField = (field: keyof Scene, value: any) => {
    onChange({ ...scene, [field]: value });
  };

  const updateNestedField = (parent: keyof Scene, field: string, value: any) => {
    onChange({
      ...scene,
      [parent]: {
        ...(scene[parent] as any),
        [field]: value
      }
    });
  };

  return (
    <Container maxW="container.xl" py={8}>
      <VStack gap={8} align="stretch">
        {/* Header Section */}
        <HStack justify="space-between" align="center">
          <Heading size="2xl" color="fg">编辑场景</Heading>
          <HStack gap={3}>
            <Button onClick={onCancel} variant="outline" size="md">
              取消
            </Button>
            <Button onClick={onSave} colorPalette="blue" size="md">
              保存场景
            </Button>
          </HStack>
        </HStack>

        {/* Basic Information Section */}
        <Card.Root>
          <Card.Header>
            <Card.Title>基本信息</Card.Title>
          </Card.Header>
          <Card.Body>
            <VStack gap={6} align="stretch">
              <Field.Root>
                <Field.Label>场景标题</Field.Label>
                <Input
                  value={scene.title}
                  onChange={(e) => updateField('title', e.target.value)}
                  placeholder="输入场景标题"
                  size="lg"
                />
              </Field.Root>

              <Field.Root>
                <Field.Label>场景描述</Field.Label>
                <Textarea
                  value={scene.description}
                  onChange={(e) => updateField('description', e.target.value)}
                  placeholder="描述这个场景的内容和情景..."
                  rows={4}
                  resize="vertical"
                />
              </Field.Root>

              <SimpleGrid columns={{ base: 1, md: 3 }} gap={4}>
                <Field.Root>
                  <Field.Label>时间段</Field.Label>
                  <NativeSelect.Root value={scene.timeOfDay} onChange={(e) => updateField('timeOfDay', e.target.value)}>
                    <NativeSelect.Field>
                      <option value="">选择时间</option>
                      <option value="黎明">黎明</option>
                      <option value="上午">上午</option>
                      <option value="中午">中午</option>
                      <option value="下午">下午</option>
                      <option value="黄昏">黄昏</option>
                      <option value="夜晚">夜晚</option>
                      <option value="深夜">深夜</option>
                    </NativeSelect.Field>
                    <NativeSelect.Indicator />
                  </NativeSelect.Root>
                </Field.Root>

                <Field.Root>
                  <Field.Label>天气状况</Field.Label>
                  <Input
                    value={scene.weather}
                    onChange={(e) => updateField('weather', e.target.value)}
                    placeholder="如：晴朗、雨天、多云"
                  />
                </Field.Root>

                <Field.Root>
                  <Field.Label>节奏</Field.Label>
                  <NativeSelect.Root value={scene.pacing} onChange={(e) => updateField('pacing', e.target.value)}>
                    <NativeSelect.Field>
                      <option value="slow">慢节奏</option>
                      <option value="medium">中等节奏</option>
                      <option value="fast">快节奏</option>
                    </NativeSelect.Field>
                    <NativeSelect.Indicator />
                  </NativeSelect.Root>
                </Field.Root>
              </SimpleGrid>
            </VStack>
          </Card.Body>
        </Card.Root>

        {/* Atmosphere Settings Section */}
        <Card.Root>
          <Card.Header>
            <Card.Title>氛围设置</Card.Title>
            <Card.Description>调整各项氛围参数来营造想要的场景感觉</Card.Description>
          </Card.Header>
          <Card.Body>
            <VStack gap={6} align="stretch">
              {[
                { key: 'tension', label: '紧张度', max: 10, colorPalette: 'red' },
                { key: 'energy', label: '能量', max: 10, colorPalette: 'orange' },
                { key: 'intimacy', label: '亲密度', max: 10, colorPalette: 'pink' },
                { key: 'danger', label: '危险度', max: 10, colorPalette: 'red' },
                { key: 'mystery', label: '神秘感', max: 10, colorPalette: 'purple' }
              ].map(slider => (
                <Box key={slider.key}>
                  <Slider.Root
                    value={[(scene.atmosphere as any)[slider.key]]}
                    onValueChange={({ value }) => updateNestedField('atmosphere', slider.key, value[0])}
                    min={1}
                    max={slider.max}
                    step={1}
                    colorPalette={slider.colorPalette as any}
                  >
                    <HStack justify="space-between">
                      <Slider.Label>{slider.label}</Slider.Label>
                      <Slider.ValueText />
                    </HStack>
                    <Slider.Control>
                      <Slider.Track>
                        <Slider.Range />
                      </Slider.Track>
                      <Slider.Thumbs />
                    </Slider.Control>
                  </Slider.Root>
                </Box>
              ))}
            </VStack>
          </Card.Body>
        </Card.Root>

        {/* Sensory Details Section */}
        <Card.Root>
          <Card.Header>
            <Card.Title>感官细节</Card.Title>
            <Card.Description>为场景添加丰富的感官体验细节</Card.Description>
          </Card.Header>
          <Card.Body>
            <VStack gap={8} align="stretch">
              {Object.entries(scene.sensoryDetails).map(([senseType, details]) => (
                <Box key={senseType}>
                  <Heading size="md" mb={4} color="fg">
                    {getSenseLabel(senseType)}
                  </Heading>
                  <VStack gap={3} align="stretch">
                    {details.map((detail, index) => (
                      <HStack key={index} gap={3}>
                        <Input
                          flex="1"
                          value={detail}
                          onChange={(e) => {
                            const newDetails = [...details];
                            newDetails[index] = e.target.value;
                            updateNestedField('sensoryDetails', senseType, newDetails);
                          }}
                          placeholder={`输入${getSenseLabel(senseType)}细节`}
                        />
                        <IconButton
                          aria-label="删除细节"
                          size="md"
                          variant="outline"
                          colorPalette="red"
                          onClick={() => {
                            const newDetails = details.filter((_, i) => i !== index);
                            updateNestedField('sensoryDetails', senseType, newDetails);
                          }}
                        >
                          ×
                        </IconButton>
                      </HStack>
                    ))}
                    <Button
                      variant="outline"
                      colorPalette="blue"
                      size="sm"
                      onClick={() => {
                        const newDetails = [...details, ''];
                        updateNestedField('sensoryDetails', senseType, newDetails);
                      }}
                      alignSelf="flex-start"
                    >
                      + 添加{getSenseLabel(senseType)}细节
                    </Button>
                  </VStack>
                </Box>
              ))}
            </VStack>
          </Card.Body>
        </Card.Root>
      </VStack>
    </Container>
  );
};

function getSenseLabel(senseType: string): string {
  const labels: Record<string, string> = {
    visual: '视觉',
    auditory: '听觉',
    olfactory: '嗅觉',
    tactile: '触觉',
    gustatory: '味觉',
    emotional: '情感'
  };
  return labels[senseType] || senseType;
}