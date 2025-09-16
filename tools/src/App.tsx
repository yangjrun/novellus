import React, { useState } from 'react';
import {
  Box,
  Flex,
  Button,
  Heading,
  Text,
  Alert,
  Container,
  HStack,
  VStack,
  Badge,
  Menu,
  Portal,
  useBreakpointValue
} from '@chakra-ui/react';
import { Character, InterviewSession } from './types/index';
import { CharacterForm } from '@components/CharacterForm';
import { InterviewInterface } from '@components/InterviewInterface';
import { ChecklistInterface } from '@components/ChecklistInterface';
import { DiagnosticInterface } from '@components/DiagnosticInterface';
import { ProjectManager } from '@components/ProjectManager';
import { NarrativeStructureComponent } from '@components/NarrativeStructure';
import { EnhancedCharacterCreator } from '@components/EnhancedCharacterCreator';
import { WorldBuilder } from '@components/WorldBuilder';
import { SceneCreator } from '@components/SceneCreator';

type ActiveTool = 'home' | 'character' | 'interview' | 'checklist' | 'diagnostic' | 'narrative' | 'enhanced-character' | 'world-builder' | 'scene-creator';

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

  const handleCharacterSave = (_character: Character) => {
    setState(prev => ({ ...prev, activeTool: 'home' }));
  };

  const handleInterviewComplete = (_session: InterviewSession) => {
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

      case 'enhanced-character':
        if (!state.currentProject) {
          return (
            <Alert.Root status="warning" maxW="md" mx="auto" mt={20}>
              <Alert.Indicator />
              <Alert.Content>
                <Alert.Title>需要先选择项目</Alert.Title>
                <Alert.Description>
                  请先创建或选择一个项目使用增强版角色创作器
                </Alert.Description>
              </Alert.Content>
              <Button
                size="sm"
                colorPalette="blue"
                onClick={() => handleToolSwitch('home')}
                ml={4}
              >
                返回首页
              </Button>
            </Alert.Root>
          );
        }
        return (
          <EnhancedCharacterCreator
            projectId={state.currentProject}
            character={state.currentCharacter}
            onSave={handleCharacterSave}
            onCancel={handleCancel}
          />
        );

      case 'interview':
        if (!state.currentCharacter?.id) {
          return (
            <Alert.Root status="warning" maxW="md" mx="auto" mt={20}>
              <Alert.Indicator />
              <Alert.Content>
                <Alert.Title>需要先选择角色</Alert.Title>
                <Alert.Description>
                  请先创建或选择一个角色进行面试
                </Alert.Description>
              </Alert.Content>
              <Button
                size="sm"
                colorPalette="blue"
                onClick={() => handleToolSwitch('home')}
                ml={4}
              >
                返回首页
              </Button>
            </Alert.Root>
          );
        }
        return (
          <InterviewInterface
            characterId={state.currentCharacter.id}
            onComplete={handleInterviewComplete}
            onCancel={handleCancel}
          />
        );

      case 'narrative':
        if (!state.currentProject) {
          return (
            <Alert.Root status="warning" maxW="md" mx="auto" mt={20}>
              <Alert.Indicator />
              <Alert.Content>
                <Alert.Title>需要先选择项目</Alert.Title>
                <Alert.Description>
                  请先创建或选择一个项目使用叙事结构工具
                </Alert.Description>
              </Alert.Content>
              <Button
                size="sm"
                colorPalette="blue"
                onClick={() => handleToolSwitch('home')}
                ml={4}
              >
                返回首页
              </Button>
            </Alert.Root>
          );
        }
        return (
          <NarrativeStructureComponent
            projectId={state.currentProject}
            onComplete={handleCancel}
            onCancel={handleCancel}
          />
        );

      case 'world-builder':
        if (!state.currentProject) {
          return (
            <Alert.Root status="warning" maxW="md" mx="auto" mt={20}>
              <Alert.Indicator />
              <Alert.Content>
                <Alert.Title>需要先选择项目</Alert.Title>
                <Alert.Description>
                  请先创建或选择一个项目使用世界构建工具
                </Alert.Description>
              </Alert.Content>
              <Button
                size="sm"
                colorPalette="blue"
                onClick={() => handleToolSwitch('home')}
                ml={4}
              >
                返回首页
              </Button>
            </Alert.Root>
          );
        }
        return (
          <WorldBuilder
            projectId={state.currentProject}
            onComplete={handleCancel}
            onCancel={handleCancel}
          />
        );

      case 'scene-creator':
        if (!state.currentProject) {
          return (
            <Alert.Root status="warning" maxW="md" mx="auto" mt={20}>
              <Alert.Indicator />
              <Alert.Content>
                <Alert.Title>需要先选择项目</Alert.Title>
                <Alert.Description>
                  请先创建或选择一个项目使用场景创作工具
                </Alert.Description>
              </Alert.Content>
              <Button
                size="sm"
                colorPalette="blue"
                onClick={() => handleToolSwitch('home')}
                ml={4}
              >
                返回首页
              </Button>
            </Alert.Root>
          );
        }
        return (
          <SceneCreator
            projectId={state.currentProject}
            onComplete={handleCancel}
            onCancel={handleCancel}
          />
        );

      case 'checklist':
        if (!state.currentProject) {
          return (
            <Alert.Root status="warning" maxW="md" mx="auto" mt={20}>
              <Alert.Indicator />
              <Alert.Content>
                <Alert.Title>需要先选择项目</Alert.Title>
                <Alert.Description>
                  请先创建或选择一个项目使用检查清单
                </Alert.Description>
              </Alert.Content>
              <Button
                size="sm"
                colorPalette="blue"
                onClick={() => handleToolSwitch('home')}
                ml={4}
              >
                返回首页
              </Button>
            </Alert.Root>
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
            <Alert.Root status="warning" maxW="md" mx="auto" mt={20}>
              <Alert.Indicator />
              <Alert.Content>
                <Alert.Title>需要先选择项目</Alert.Title>
                <Alert.Description>
                  请先创建或选择一个项目使用诊断工具
                </Alert.Description>
              </Alert.Content>
              <Button
                size="sm"
                colorPalette="blue"
                onClick={() => handleToolSwitch('home')}
                ml={4}
              >
                返回首页
              </Button>
            </Alert.Root>
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

  const isMobile = useBreakpointValue({ base: true, md: false });

  return (
    <Box minH="100vh" bg="gray.50" display="flex" flexDirection="column">
      <Box
        as="header"
        bg="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        color="white"
        boxShadow="0 2px 20px rgba(0, 0, 0, 0.1)"
        position="sticky"
        top={0}
        zIndex={100}
      >
        <Container maxW="8xl" p={0}>
          <Flex
            justify="space-between"
            align="center"
            px={5}
            py={isMobile ? 4 : 0}
            h={isMobile ? "auto" : "70px"}
            gap={5}
            direction={isMobile ? "column" : "row"}
          >
            <Heading
              size={isMobile ? "lg" : "xl"}
              cursor="pointer"
              transition="opacity 0.2s"
              userSelect="none"
              flexShrink={0}
              onClick={() => handleToolSwitch('home')}
              _hover={{ opacity: 0.9 }}
            >
              📚 Novellus 创作工具
            </Heading>

            <HStack
              as="nav"
              gap={2}
              flexWrap="wrap"
              minW={0}
              justify={isMobile ? "center" : "flex-end"}
            >
              <Button
                size="sm"
                variant={state.activeTool === 'home' ? 'solid' : 'ghost'}
                colorPalette={state.activeTool === 'home' ? 'white' : 'gray'}
                bg={state.activeTool === 'home' ? 'white' : 'rgba(255, 255, 255, 0.1)'}
                color={state.activeTool === 'home' ? 'blue.600' : 'white'}
                backdropFilter="blur(10px)"
                borderRadius="full"
                fontSize="xs"
                fontWeight="medium"
                px={3}
                py={2}
                onClick={() => handleToolSwitch('home')}
                _hover={{
                  bg: state.activeTool === 'home' ? 'white' : 'rgba(255, 255, 255, 0.2)',
                  transform: 'translateY(-1px)'
                }}
              >
                🏠 首页
              </Button>

              {/* Enhanced Tools and Basic Tools */}
              {!isMobile ? (
                <HStack gap={3}>
                  <Menu.Root>
                    <Menu.Trigger asChild>
                      <Button
                        size="sm"
                        variant="ghost"
                        bg="rgba(255, 255, 255, 0.1)"
                        color="white"
                        backdropFilter="blur(10px)"
                        borderRadius="full"
                        fontSize="xs"
                        fontWeight="medium"
                        px={4}
                        py={2}
                        rightIcon="▼"
                        _hover={{
                          bg: 'rgba(255, 255, 255, 0.2)',
                          transform: 'translateY(-1px)'
                        }}
                      >
                        🚀 增强工具
                      </Button>
                    </Menu.Trigger>
                    <Portal>
                      <Menu.Positioner>
                        <Menu.Content
                          bg="white"
                          borderRadius="xl"
                          boxShadow="xl"
                          p={2}
                          minW="220px"
                        >
                          <Menu.ItemGroup>
                            <Menu.ItemGroupLabel px={4} py={2} fontSize="xs" fontWeight="bold" color="gray.500">
                              🚀 Phase 1 增强工具
                            </Menu.ItemGroupLabel>
                            <Menu.Item
                              value="narrative"
                              bg={state.activeTool === 'narrative' ? 'blue.50' : 'transparent'}
                              color={state.activeTool === 'narrative' ? 'blue.600' : 'gray.700'}
                              borderRadius="lg"
                              py={3}
                              px={4}
                              fontSize="sm"
                              fontWeight="medium"
                              _hover={{ bg: 'blue.50', color: 'blue.600' }}
                              onClick={() => handleToolSwitch('narrative')}
                            >
                              📚 叙事结构
                            </Menu.Item>
                            <Menu.Item
                              value="enhanced-character"
                              bg={state.activeTool === 'enhanced-character' ? 'blue.50' : 'transparent'}
                              color={state.activeTool === 'enhanced-character' ? 'blue.600' : 'gray.700'}
                              borderRadius="lg"
                              py={3}
                              px={4}
                              fontSize="sm"
                              fontWeight="medium"
                              _hover={{ bg: 'blue.50', color: 'blue.600' }}
                              onClick={() => handleToolSwitch('enhanced-character')}
                            >
                              🎭 深度角色
                            </Menu.Item>
                            <Menu.Item
                              value="world-builder"
                              bg={state.activeTool === 'world-builder' ? 'blue.50' : 'transparent'}
                              color={state.activeTool === 'world-builder' ? 'blue.600' : 'gray.700'}
                              borderRadius="lg"
                              py={3}
                              px={4}
                              fontSize="sm"
                              fontWeight="medium"
                              _hover={{ bg: 'blue.50', color: 'blue.600' }}
                              onClick={() => handleToolSwitch('world-builder')}
                            >
                              🌍 智能世界
                            </Menu.Item>
                            <Menu.Item
                              value="scene-creator"
                              bg={state.activeTool === 'scene-creator' ? 'blue.50' : 'transparent'}
                              color={state.activeTool === 'scene-creator' ? 'blue.600' : 'gray.700'}
                              borderRadius="lg"
                              py={3}
                              px={4}
                              fontSize="sm"
                              fontWeight="medium"
                              _hover={{ bg: 'blue.50', color: 'blue.600' }}
                              onClick={() => handleToolSwitch('scene-creator')}
                            >
                              🎬 多维场景
                            </Menu.Item>
                          </Menu.ItemGroup>
                        </Menu.Content>
                      </Menu.Positioner>
                    </Portal>
                  </Menu.Root>

                  <Menu.Root>
                    <Menu.Trigger asChild>
                      <Button
                        size="sm"
                        variant="ghost"
                        bg="rgba(255, 255, 255, 0.1)"
                        color="white"
                        backdropFilter="blur(10px)"
                        borderRadius="full"
                        fontSize="xs"
                        fontWeight="medium"
                        px={4}
                        py={2}
                        rightIcon="▼"
                        _hover={{
                          bg: 'rgba(255, 255, 255, 0.2)',
                          transform: 'translateY(-1px)'
                        }}
                      >
                        📝 基础工具
                      </Button>
                    </Menu.Trigger>
                    <Portal>
                      <Menu.Positioner>
                        <Menu.Content
                          bg="white"
                          borderRadius="xl"
                          boxShadow="xl"
                          p={2}
                          minW="200px"
                        >
                          <Menu.Item
                            value="character"
                            bg={state.activeTool === 'character' ? 'blue.50' : 'transparent'}
                            color={state.activeTool === 'character' ? 'blue.600' : 'gray.700'}
                            borderRadius="lg"
                            py={3}
                            px={4}
                            fontSize="sm"
                            fontWeight="medium"
                            _hover={{ bg: 'blue.50', color: 'blue.600' }}
                            onClick={() => handleToolSwitch('character')}
                          >
                            👤 角色工作表
                          </Menu.Item>
                          <Menu.Item
                            value="interview"
                            bg={state.activeTool === 'interview' ? 'blue.50' : 'transparent'}
                            color={state.activeTool === 'interview' ? 'blue.600' : 'gray.700'}
                            borderRadius="lg"
                            py={3}
                            px={4}
                            fontSize="sm"
                            fontWeight="medium"
                            _hover={{ bg: 'blue.50', color: 'blue.600' }}
                            onClick={() => handleToolSwitch('interview')}
                          >
                            💬 角色面试
                          </Menu.Item>
                          <Menu.Item
                            value="checklist"
                            bg={state.activeTool === 'checklist' ? 'blue.50' : 'transparent'}
                            color={state.activeTool === 'checklist' ? 'blue.600' : 'gray.700'}
                            borderRadius="lg"
                            py={3}
                            px={4}
                            fontSize="sm"
                            fontWeight="medium"
                            _hover={{ bg: 'blue.50', color: 'blue.600' }}
                            onClick={() => handleToolSwitch('checklist')}
                          >
                            ✅ 情节检查
                          </Menu.Item>
                          <Menu.Item
                            value="diagnostic"
                            bg={state.activeTool === 'diagnostic' ? 'blue.50' : 'transparent'}
                            color={state.activeTool === 'diagnostic' ? 'blue.600' : 'gray.700'}
                            borderRadius="lg"
                            py={3}
                            px={4}
                            fontSize="sm"
                            fontWeight="medium"
                            _hover={{ bg: 'blue.50', color: 'blue.600' }}
                            onClick={() => handleToolSwitch('diagnostic')}
                          >
                            🔍 故事诊断
                          </Menu.Item>
                        </Menu.Content>
                      </Menu.Positioner>
                    </Portal>
                  </Menu.Root>
                </HStack>
              ) : (
                /* Mobile: Compact menu for all tools */
                <Menu.Root>
                  <Menu.Trigger asChild>
                    <Button
                      size="sm"
                      variant="ghost"
                      bg="rgba(255, 255, 255, 0.1)"
                      color="white"
                      backdropFilter="blur(10px)"
                      borderRadius="full"
                      fontSize="xs"
                      fontWeight="medium"
                      px={4}
                      py={2}
                      rightIcon="▼"
                      _hover={{
                        bg: 'rgba(255, 255, 255, 0.2)',
                        transform: 'translateY(-1px)'
                      }}
                    >
                      🛠️ 创作工具
                    </Button>
                  </Menu.Trigger>
                  <Portal>
                    <Menu.Positioner>
                      <Menu.Content
                        bg="white"
                        borderRadius="xl"
                        boxShadow="xl"
                        p={2}
                        minW="220px"
                        maxH="80vh"
                        overflowY="auto"
                      >
                        <Menu.ItemGroup>
                          <Menu.ItemGroupLabel px={4} py={2} fontSize="xs" fontWeight="bold" color="gray.500">
                            🎨 创作工具
                          </Menu.ItemGroupLabel>
                          <Menu.Item
                            value="narrative"
                            bg={state.activeTool === 'narrative' ? 'blue.50' : 'transparent'}
                            color={state.activeTool === 'narrative' ? 'blue.600' : 'gray.700'}
                            borderRadius="lg"
                            py={3}
                            px={4}
                            fontSize="sm"
                            fontWeight="medium"
                            _hover={{ bg: 'blue.50', color: 'blue.600' }}
                            onClick={() => handleToolSwitch('narrative')}
                          >
                            📚 叙事结构
                          </Menu.Item>
                          <Menu.Item
                            value="enhanced-character"
                            bg={state.activeTool === 'enhanced-character' ? 'blue.50' : 'transparent'}
                            color={state.activeTool === 'enhanced-character' ? 'blue.600' : 'gray.700'}
                            borderRadius="lg"
                            py={3}
                            px={4}
                            fontSize="sm"
                            fontWeight="medium"
                            _hover={{ bg: 'blue.50', color: 'blue.600' }}
                            onClick={() => handleToolSwitch('enhanced-character')}
                          >
                            🎭 角色创建
                          </Menu.Item>
                          <Menu.Item
                            value="world-builder"
                            bg={state.activeTool === 'world-builder' ? 'blue.50' : 'transparent'}
                            color={state.activeTool === 'world-builder' ? 'blue.600' : 'gray.700'}
                            borderRadius="lg"
                            py={3}
                            px={4}
                            fontSize="sm"
                            fontWeight="medium"
                            _hover={{ bg: 'blue.50', color: 'blue.600' }}
                            onClick={() => handleToolSwitch('world-builder')}
                          >
                            🌍 世界构建
                          </Menu.Item>
                          <Menu.Item
                            value="scene-creator"
                            bg={state.activeTool === 'scene-creator' ? 'blue.50' : 'transparent'}
                            color={state.activeTool === 'scene-creator' ? 'blue.600' : 'gray.700'}
                            borderRadius="lg"
                            py={3}
                            px={4}
                            fontSize="sm"
                            fontWeight="medium"
                            _hover={{ bg: 'blue.50', color: 'blue.600' }}
                            onClick={() => handleToolSwitch('scene-creator')}
                          >
                            🎬 场景创建
                          </Menu.Item>
                        </Menu.ItemGroup>
                        <Menu.Separator />
                        <Menu.ItemGroup>
                          <Menu.ItemGroupLabel px={4} py={2} fontSize="xs" fontWeight="bold" color="gray.500">
                            📝 基础工具
                          </Menu.ItemGroupLabel>
                          <Menu.Item
                            value="character"
                            bg={state.activeTool === 'character' ? 'blue.50' : 'transparent'}
                            color={state.activeTool === 'character' ? 'blue.600' : 'gray.700'}
                            borderRadius="lg"
                            py={3}
                            px={4}
                            fontSize="sm"
                            fontWeight="medium"
                            _hover={{ bg: 'blue.50', color: 'blue.600' }}
                            onClick={() => handleToolSwitch('character')}
                          >
                            👤 角色工作表
                          </Menu.Item>
                          <Menu.Item
                            value="interview"
                            bg={state.activeTool === 'interview' ? 'blue.50' : 'transparent'}
                            color={state.activeTool === 'interview' ? 'blue.600' : 'gray.700'}
                            borderRadius="lg"
                            py={3}
                            px={4}
                            fontSize="sm"
                            fontWeight="medium"
                            _hover={{ bg: 'blue.50', color: 'blue.600' }}
                            onClick={() => handleToolSwitch('interview')}
                          >
                            💬 角色面试
                          </Menu.Item>
                          <Menu.Item
                            value="checklist"
                            bg={state.activeTool === 'checklist' ? 'blue.50' : 'transparent'}
                            color={state.activeTool === 'checklist' ? 'blue.600' : 'gray.700'}
                            borderRadius="lg"
                            py={3}
                            px={4}
                            fontSize="sm"
                            fontWeight="medium"
                            _hover={{ bg: 'blue.50', color: 'blue.600' }}
                            onClick={() => handleToolSwitch('checklist')}
                          >
                            ✅ 情节检查
                          </Menu.Item>
                          <Menu.Item
                            value="diagnostic"
                            bg={state.activeTool === 'diagnostic' ? 'blue.50' : 'transparent'}
                            color={state.activeTool === 'diagnostic' ? 'blue.600' : 'gray.700'}
                            borderRadius="lg"
                            py={3}
                            px={4}
                            fontSize="sm"
                            fontWeight="medium"
                            _hover={{ bg: 'blue.50', color: 'blue.600' }}
                            onClick={() => handleToolSwitch('diagnostic')}
                          >
                            🔍 故事诊断
                          </Menu.Item>
                        </Menu.ItemGroup>
                      </Menu.Content>
                    </Menu.Positioner>
                  </Portal>
                </Menu.Root>
              )}
            </HStack>
          </Flex>
        </Container>
      </Box>

      <Container
        as="main"
        maxW="6xl"
        flex={1}
        py={5}
        px={5}
      >
        {renderActiveTool()}
      </Container>

      <Box
        as="footer"
        bg="gray.800"
        color="gray.300"
        textAlign="center"
        py={5}
        mt="auto"
      >
        <Text fontSize="sm" opacity={0.8}>
          &copy; 2024 Novellus 创作工具 - 让创作更专业
        </Text>
      </Box>
    </Box>
  );
}

export default App;