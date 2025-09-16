import React, { useState, useEffect } from 'react';
import { Character } from '../types/index';
import { EnhancedCharacterService } from '@services/enhancedCharacterService';
import {
  Box,
  VStack,
  HStack,
  Flex,
  Card,
  Container,
  Heading,
  Text,
  Input,
  Textarea,
  NativeSelect,
  Button,
  Field,
  SimpleGrid,
  Tag,
  Badge,
  Stack,
  Progress,
  Spinner,
  Alert
} from '@chakra-ui/react';

interface EnhancedCharacterCreatorProps {
  projectId: string;
  character?: Character;
  onSave: (character: Character) => void;
  onCancel: () => void;
}

export const EnhancedCharacterCreator: React.FC<EnhancedCharacterCreatorProps> = ({
  projectId,
  character,
  onSave,
  onCancel
}) => {
  const [characterService] = useState(new EnhancedCharacterService());
  const [currentCharacter, setCurrentCharacter] = useState<Character>(
    character || characterService.createCharacterTemplate(projectId)
  );
  const [currentStep, setCurrentStep] = useState(0);
  const [consistencyCheck, setConsistencyCheck] = useState<{ issues: string[], score: number } | null>(null);
  const [loading, setLoading] = useState(false);

  const steps = [
    { id: 'basic', title: '基本信息', icon: '👤' },
    { id: 'appearance', title: '外貌特征', icon: '✨' },
    { id: 'personality', title: '性格特质', icon: '🧠' },
    { id: 'background', title: '背景故事', icon: '📖' },
    { id: 'abilities', title: '能力技能', icon: '⚡' },
    { id: 'relationships', title: '人际关系', icon: '👥' },
    { id: 'lifestyle', title: '生活状况', icon: '🏠' },
    { id: 'psychology', title: '心理状态', icon: '💭' },
    { id: 'story-role', title: '故事功能', icon: '🎭' },
    { id: 'special', title: '特殊设定', icon: '🌟' }
  ];

  useEffect(() => {
    // 定期进行一致性检查
    const check = characterService.checkCharacterConsistency(currentCharacter);
    setConsistencyCheck(check);
  }, [currentCharacter, characterService]);

  const handleFieldChange = (section: keyof Character, field: string, value: any) => {
    setCurrentCharacter(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };

  const handleArrayFieldChange = (section: keyof Character, field: string, index: number, value: string) => {
    setCurrentCharacter(prev => {
      const sectionData = prev[section] as any;
      const array = [...(sectionData[field] || [])];
      array[index] = value;
      return {
        ...prev,
        [section]: {
          ...sectionData,
          [field]: array
        }
      };
    });
  };

  const addArrayItem = (section: keyof Character, field: string, defaultValue: any = '') => {
    setCurrentCharacter(prev => {
      const sectionData = prev[section] as any;
      const array = [...(sectionData[field] || []), defaultValue];
      return {
        ...prev,
        [section]: {
          ...sectionData,
          [field]: array
        }
      };
    });
  };

  const removeArrayItem = (section: keyof Character, field: string, index: number) => {
    setCurrentCharacter(prev => {
      const sectionData = prev[section] as any;
      const array = [...(sectionData[field] || [])];
      array.splice(index, 1);
      return {
        ...prev,
        [section]: {
          ...sectionData,
          [field]: array
        }
      };
    });
  };

  const getSuggestions = (category: string): string[] => {
    return characterService.generateCharacterSuggestions(currentCharacter, category);
  };

  const applySuggestion = (section: keyof Character, field: string, suggestion: string) => {
    const sectionData = currentCharacter[section] as any;
    const currentArray = sectionData[field] || [];
    if (!currentArray.includes(suggestion)) {
      setCurrentCharacter(prev => ({
        ...prev,
        [section]: {
          ...prev[section],
          [field]: [...currentArray, suggestion]
        }
      }));
    }
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      await characterService.saveCharacter(currentCharacter);
      onSave(currentCharacter);
    } catch (error) {
      console.error('保存角色失败:', error);
      alert('保存失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const renderBasicInfo = () => (
    <VStack spacing={6} align="stretch" maxW="800px">
      <Heading size="lg" color="blue.600" display="flex" alignItems="center" gap={2}>
        👤 基本信息
      </Heading>

      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} mb={8}>
        <FormField label="姓名" required>
          <Input
            value={currentCharacter.basicInfo.name}
            onChange={(e) => handleFieldChange('basicInfo', 'name', e.target.value)}
            placeholder="角色的正式姓名"
          />
        </FormField>

        <FormField label="年龄">
          <Input
            value={currentCharacter.basicInfo.age}
            onChange={(e) => handleFieldChange('basicInfo', 'age', e.target.value)}
            placeholder="例：25岁 / 青年 / 不详"
          />
        </FormField>

        <FormField label="性别">
          <NativeSelect.Root>
            <NativeSelect.Field
              value={currentCharacter.basicInfo.gender}
              onChange={(e) => handleFieldChange('basicInfo', 'gender', e.target.value)}
              placeholder="选择性别"
            >
              <option value="">选择性别</option>
              <option value="男">男</option>
              <option value="女">女</option>
              <option value="非二元">非二元</option>
              <option value="不详">不详</option>
            </NativeSelect.Field>
            <NativeSelect.Indicator />
          </NativeSelect.Root>
        </FormField>

        <FormField label="职业">
          <Input
            value={currentCharacter.basicInfo.occupation}
            onChange={(e) => handleFieldChange('basicInfo', 'occupation', e.target.value)}
            placeholder="角色的主要职业或身份"
          />
        </FormField>

        <FormField label="社会地位">
          <Input
            value={currentCharacter.basicInfo.socialStatus}
            onChange={(e) => handleFieldChange('basicInfo', 'socialStatus', e.target.value)}
            placeholder="例：平民、贵族、流浪者"
          />
        </FormField>
      </SimpleGrid>

      <FormField label="别名/外号">
        <ArrayInput
          values={currentCharacter.basicInfo.alias || []}
          onChange={(values) => handleFieldChange('basicInfo', 'alias', values)}
          placeholder="添加别名或外号"
        />
      </FormField>
    </VStack>
  );

  const renderAppearance = () => (
    <VStack spacing={6} align="stretch" maxW="800px">
      <Heading size="lg" color="blue.600" display="flex" alignItems="center" gap={2}>
        ✨ 外貌特征
      </Heading>

      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} mb={8}>
        <FormField label="身高">
          <Input
            value={currentCharacter.appearance.height}
            onChange={(e) => handleFieldChange('appearance', 'height', e.target.value)}
            placeholder="例：180cm / 高大 / 中等"
          />
        </FormField>

        <FormField label="体重">
          <Input
            value={currentCharacter.appearance.weight}
            onChange={(e) => handleFieldChange('appearance', 'weight', e.target.value)}
            placeholder="例：70kg / 偏瘦 / 健壮"
          />
        </FormField>

        <FormField label="发色">
          <Input
            value={currentCharacter.appearance.hairColor}
            onChange={(e) => handleFieldChange('appearance', 'hairColor', e.target.value)}
            placeholder="例：黑色、金色、银白"
          />
        </FormField>

        <FormField label="眼色">
          <Input
            value={currentCharacter.appearance.eyeColor}
            onChange={(e) => handleFieldChange('appearance', 'eyeColor', e.target.value)}
            placeholder="例：棕色、蓝色、绿色"
          />
        </FormField>

        <FormField label="肤色">
          <Input
            value={currentCharacter.appearance.skinTone}
            onChange={(e) => handleFieldChange('appearance', 'skinTone', e.target.value)}
            placeholder="例：白皙、古铜、黝黑"
          />
        </FormField>

        <FormField label="体型">
          <Input
            value={currentCharacter.appearance.bodyType}
            onChange={(e) => handleFieldChange('appearance', 'bodyType', e.target.value)}
            placeholder="例：瘦削、健壮、丰满"
          />
        </FormField>

        <FormField label="着装风格">
          <Input
            value={currentCharacter.appearance.clothingStyle}
            onChange={(e) => handleFieldChange('appearance', 'clothingStyle', e.target.value)}
            placeholder="例：简约、华丽、实用"
          />
        </FormField>
      </SimpleGrid>

      <FormField label="特殊标记">
        <ArrayInput
          values={currentCharacter.appearance.specialMarks}
          onChange={(values) => handleFieldChange('appearance', 'specialMarks', values)}
          placeholder="添加疤痕、纹身、胎记等"
        />
      </FormField>
    </VStack>
  );

  const renderPersonality = () => (
    <VStack spacing={6} align="stretch" maxW="800px">
      <Heading size="lg" color="blue.600" display="flex" alignItems="center" gap={2}>
        🧠 性格特质
      </Heading>

      <VStack spacing={6} align="stretch">
        <SuggestionField
          label="核心特质"
          values={currentCharacter.personality.coreTraits}
          suggestions={getSuggestions('coreTraits')}
          onAdd={(value) => applySuggestion('personality', 'coreTraits', value)}
          onChange={(values) => handleFieldChange('personality', 'coreTraits', values)}
          placeholder="添加性格特质"
        />

        <SuggestionField
          label="价值观"
          values={currentCharacter.personality.values}
          suggestions={getSuggestions('values')}
          onAdd={(value) => applySuggestion('personality', 'values', value)}
          onChange={(values) => handleFieldChange('personality', 'values', values)}
          placeholder="添加核心价值观"
        />

        <FormField label="信念">
          <ArrayInput
            values={currentCharacter.personality.beliefs}
            onChange={(values) => handleFieldChange('personality', 'beliefs', values)}
            placeholder="添加信念或世界观"
          />
        </FormField>

        <SuggestionField
          label="恐惧"
          values={currentCharacter.personality.fears}
          suggestions={getSuggestions('fears')}
          onAdd={(value) => applySuggestion('personality', 'fears', value)}
          onChange={(values) => handleFieldChange('personality', 'fears', values)}
          placeholder="添加恐惧"
        />

        <FormField label="欲望/目标">
          <ArrayInput
            values={currentCharacter.personality.desires}
            onChange={(values) => handleFieldChange('personality', 'desires', values)}
            placeholder="添加欲望或目标"
          />
        </FormField>

        <FormField label="弱点">
          <ArrayInput
            values={currentCharacter.personality.weaknesses}
            onChange={(values) => handleFieldChange('personality', 'weaknesses', values)}
            placeholder="添加性格弱点"
          />
        </FormField>

        <FormField label="优点">
          <ArrayInput
            values={currentCharacter.personality.strengths}
            onChange={(values) => handleFieldChange('personality', 'strengths', values)}
            placeholder="添加性格优点"
          />
        </FormField>
      </VStack>
    </VStack>
  );

  const renderStoryRole = () => (
    <VStack spacing={6} align="stretch" maxW="800px">
      <Heading size="lg" color="blue.600" display="flex" alignItems="center" gap={2}>
        🎭 故事功能
      </Heading>

      <VStack spacing={6} align="stretch">
        <FormField label="角色类型" required>
          <NativeSelect.Root>
            <NativeSelect.Field
              value={currentCharacter.storyRole.characterType}
              onChange={(e) => handleFieldChange('storyRole', 'characterType', e.target.value)}
            >
              <option value="protagonist">主角</option>
              <option value="antagonist">反角</option>
              <option value="supporting">配角</option>
              <option value="minor">次要角色</option>
            </NativeSelect.Field>
            <NativeSelect.Indicator />
          </NativeSelect.Root>
        </FormField>

        <FormField label="角色弧线">
          <Input
            value={currentCharacter.storyRole.characterArc}
            onChange={(e) => handleFieldChange('storyRole', 'characterArc', e.target.value)}
            placeholder="例：成长型、堕落型、平坦型"
          />
        </FormField>

        <FormField label="冲突作用">
          <Textarea
            value={currentCharacter.storyRole.conflictRole}
            onChange={(e) => handleFieldChange('storyRole', 'conflictRole', e.target.value)}
            placeholder="描述角色在故事冲突中的作用"
            rows={3}
            resize="vertical"
          />
        </FormField>

        <FormField label="象征意义">
          <Textarea
            value={currentCharacter.storyRole.symbolism}
            onChange={(e) => handleFieldChange('storyRole', 'symbolism', e.target.value)}
            placeholder="角色象征的主题或概念"
            rows={2}
            resize="vertical"
          />
        </FormField>

        <FormField label="读者连接">
          <Input
            value={currentCharacter.storyRole.readerConnection}
            onChange={(e) => handleFieldChange('storyRole', 'readerConnection', e.target.value)}
            placeholder="例：认同、同情、敬畏、恐惧"
          />
        </FormField>
      </VStack>
    </VStack>
  );

  const renderCurrentStep = () => {
    switch (steps[currentStep].id) {
      case 'basic': return renderBasicInfo();
      case 'appearance': return renderAppearance();
      case 'personality': return renderPersonality();
      case 'story-role': return renderStoryRole();
      default: return (
        <VStack spacing={6} align="center" justify="center" minH="400px">
          <Text fontSize="6xl">🚧</Text>
          <Heading size="lg" color="fg.muted">开发中...</Heading>
          <Text color="fg.muted" textAlign="center" maxW="md">
            该功能模块正在开发中，敬请期待。您可以切换到其他已完成的功能模块继续编辑角色信息。
          </Text>
        </VStack>
      );
    }
  };

  return (
    <Container maxW="7xl" p={0}>
      <Card.Root variant="elevated" overflow="hidden">
        <Card.Header bg="gradient-to-br" from="blue.500" to="purple.600" color="white" p={{ base: 6, md: 8 }}>
          <Flex
            justify="space-between"
            align="flex-start"
            gap={6}
            direction={{ base: "column", md: "row" }}
          >
            <Box flex="1">
              <Heading size={{ base: "lg", md: "xl" }} mb={4}>
                {character ? '编辑角色' : '创建新角色'}
                {currentCharacter.basicInfo.name && `: ${currentCharacter.basicInfo.name}`}
              </Heading>

              {consistencyCheck && (
                <Box
                  mt={4}
                  p={3}
                  bg="whiteAlpha.100"
                  backdropFilter="blur(10px)"
                  borderRadius="md"
                  borderLeft="4px solid"
                  borderColor={
                    consistencyCheck.score < 70 ? 'red.400' :
                    consistencyCheck.score < 90 ? 'yellow.400' :
                    'green.400'
                  }
                >
                  <Text fontWeight="bold" fontSize="lg" mb={2}>
                    一致性评分: {consistencyCheck.score}/100
                  </Text>
                  {consistencyCheck.issues.length > 0 && (
                    <VStack align="flex-start" gap={1}>
                      {consistencyCheck.issues.map((issue, index) => (
                        <Text key={index} fontSize="sm" opacity={0.9}>
                          ⚠️ {issue}
                        </Text>
                      ))}
                    </VStack>
                  )}
                </Box>
              )}
            </Box>

            <HStack gap={3} flexShrink={0} w={{ base: "full", md: "auto" }}>
              <Button
                variant="outline"
                colorScheme="whiteAlpha"
                onClick={onCancel}
                flex={{ base: 1, md: "none" }}
              >
                取消
              </Button>
              <Button
                onClick={handleSave}
                disabled={loading || !currentCharacter.basicInfo.name.trim()}
                colorScheme="white"
                variant="solid"
                loadingText="保存中..."
                loading={loading}
                flex={{ base: 1, md: "none" }}
              >
                保存角色
              </Button>
            </HStack>
          </Flex>
        </Card.Header>

        <Card.Body p={0}>
          <Flex minH="600px" direction={{ base: "column", lg: "row" }}>
            {/* Step Navigation Sidebar */}
            <Box
              w={{ base: "full", lg: "280px" }}
              bg="bg.subtle"
              borderRight={{ base: "none", lg: "1px solid" }}
              borderBottom={{ base: "1px solid", lg: "none" }}
              borderColor="border.muted"
              py={{ base: 4, lg: 6 }}
              px={{ base: 4, lg: 0 }}
              overflowY="auto"
              overflowX={{ base: "auto", lg: "visible" }}
            >
              <Stack
                direction={{ base: "row", lg: "column" }}
                spacing={0}
                align="stretch"
                overflowX={{ base: "auto", lg: "visible" }}
              >
                {steps.map((step, index) => (
                  <Button
                    key={step.id}
                    variant="ghost"
                    justifyContent="flex-start"
                    h="auto"
                    py={4}
                    px={{ base: 4, lg: 6 }}
                    borderRadius={0}
                    borderLeft={{ base: "none", lg: "3px solid transparent" }}
                    borderBottom={{ base: "3px solid transparent", lg: "none" }}
                    color={index === currentStep ? 'blue.600' : 'fg.muted'}
                    bg={index === currentStep ? 'blue.50' : 'transparent'}
                    borderLeftColor={{ base: "transparent", lg: index === currentStep ? 'blue.600' : 'transparent' }}
                    borderBottomColor={{ base: index === currentStep ? 'blue.600' : 'transparent', lg: "transparent" }}
                    fontWeight={index === currentStep ? 'semibold' : 'normal'}
                    minW={{ base: "auto", lg: "full" }}
                    flexShrink={{ base: 0, lg: "initial" }}
                    _hover={{
                      bg: index === currentStep ? 'blue.50' : 'bg.panel',
                      color: 'fg.default'
                    }}
                    onClick={() => setCurrentStep(index)}
                  >
                    <HStack spacing={3} w="full">
                      <Text fontSize="lg" position="relative">
                        {step.icon}
                        {index < currentStep && (
                          <Text
                            position="absolute"
                            bottom="-2px"
                            right="-2px"
                            fontSize="xs"
                            bg="green.500"
                            color="white"
                            borderRadius="full"
                            w="4"
                            h="4"
                            display="flex"
                            alignItems="center"
                            justifyContent="center"
                          >
                            ✓
                          </Text>
                        )}
                      </Text>
                      <Text fontSize="sm" textAlign="left" display={{ base: "none", md: "block" }}>
                        {step.title}
                      </Text>
                    </HStack>
                  </Button>
                ))}
              </Stack>
            </Box>

            {/* Step Content */}
            <Box
              flex="1"
              p={{ base: 4, md: 6, lg: 8 }}
              overflowY="auto"
              maxH={{ base: "none", lg: "600px" }}
            >
              {renderCurrentStep()}
            </Box>
          </Flex>

          {/* Step Actions Footer */}
          <Flex
            justify="space-between"
            align="center"
            direction={{ base: "column", sm: "row" }}
            gap={{ base: 4, sm: 0 }}
            px={{ base: 4, md: 6, lg: 8 }}
            py={6}
            bg="bg.subtle"
            borderTop="1px solid"
            borderColor="border.muted"
          >
            <Button
              variant="outline"
              onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
              disabled={currentStep === 0}
              w={{ base: "full", sm: "auto" }}
              order={{ base: 2, sm: 1 }}
            >
              上一步
            </Button>

            <Text
              fontSize="sm"
              color="fg.muted"
              fontWeight="medium"
              order={{ base: 1, sm: 2 }}
            >
              {currentStep + 1} / {steps.length}
            </Text>

            <Button
              variant="outline"
              onClick={() => setCurrentStep(Math.min(steps.length - 1, currentStep + 1))}
              disabled={currentStep === steps.length - 1}
              w={{ base: "full", sm: "auto" }}
              order={{ base: 3, sm: 3 }}
            >
              下一步
            </Button>
          </Flex>
        </Card.Body>
      </Card.Root>
    </Container>
  );
};

// 表单字段组件
interface FormFieldProps {
  label: string;
  required?: boolean;
  children: React.ReactNode;
}

const FormField: React.FC<FormFieldProps> = ({ label, required, children }) => (
  <Field.Root required={required}>
    <Field.Label>
      {label}
      {required && <Field.RequiredIndicator />}
    </Field.Label>
    {children}
  </Field.Root>
);

// 数组输入组件
interface ArrayInputProps {
  values: string[];
  onChange: (values: string[]) => void;
  placeholder: string;
}

const ArrayInput: React.FC<ArrayInputProps> = ({ values, onChange, placeholder }) => {
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
    <VStack spacing={3} align="stretch">
      <HStack spacing={2}>
        <Input
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && addValue()}
          placeholder={placeholder}
          flex="1"
        />
        <Button onClick={addValue} colorScheme="blue" size="md" flexShrink={0}>
          添加
        </Button>
      </HStack>

      {values.length > 0 && (
        <Flex wrap="wrap" gap={2}>
          {values.map((value, index) => (
            <Tag.Root key={index} colorScheme="blue" variant="subtle">
              <Tag.Label>{value}</Tag.Label>
              <Tag.EndElement>
                <Tag.CloseTrigger onClick={() => removeValue(index)} />
              </Tag.EndElement>
            </Tag.Root>
          ))}
        </Flex>
      )}
    </VStack>
  );
};

// 建议字段组件
interface SuggestionFieldProps extends ArrayInputProps {
  label: string;
  suggestions: string[];
  onAdd: (value: string) => void;
}

const SuggestionField: React.FC<SuggestionFieldProps> = ({
  label,
  values,
  suggestions,
  onAdd,
  onChange,
  placeholder
}) => {
  return (
    <FormField label={label}>
      <VStack spacing={4} align="stretch">
        <ArrayInput values={values} onChange={onChange} placeholder={placeholder} />

        <Box
          p={4}
          bg="bg.subtle"
          borderRadius="md"
          border="1px solid"
          borderColor="border.muted"
        >
          <Text fontSize="sm" color="fg.muted" mb={2} fontWeight="medium">
            建议：
          </Text>
          <Flex wrap="wrap" gap={2}>
            {suggestions.filter(s => !values.includes(s)).slice(0, 10).map((suggestion, index) => (
              <Button
                key={index}
                size="xs"
                variant="outline"
                borderRadius="full"
                fontSize="xs"
                color="fg.muted"
                borderColor="border.muted"
                _hover={{
                  bg: 'blue.50',
                  color: 'blue.600',
                  borderColor: 'blue.200'
                }}
                onClick={() => onAdd(suggestion)}
              >
                + {suggestion}
              </Button>
            ))}
          </Flex>
        </Box>
      </VStack>
    </FormField>
  );
};