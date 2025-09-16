import { useState, useEffect, useCallback } from 'react';
import {
  Box,
  VStack,
  HStack,
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
  Separator,
  Tag,
  Flex
} from '@chakra-ui/react';
import {
  PromptConfig,
  PromptTemplate,
  DynamicVariable,
  GeneratedPrompt,
  VariableOption
} from '../types/prompt';
import { PromptGeneratorFactory } from '../services/promptGenerator';
import { PromptCopyService } from '../services/promptCopyService';

interface PromptGeneratorProps {
  initialConfig?: Partial<PromptConfig>;
  onPromptGenerated?: (prompt: GeneratedPrompt) => void;
  projectContext?: any;
}

export const PromptGenerator: React.FC<PromptGeneratorProps> = ({
  initialConfig,
  onPromptGenerated,
  projectContext
}) => {
  const [config, setConfig] = useState<PromptConfig>({
    category: 'structure',
    difficulty: 'beginner',
    writingStyle: 'narrative',
    detailLevel: 'moderate',
    aiModel: 'claude',
    ...initialConfig,
    projectContext
  });

  const [template, setTemplate] = useState<PromptTemplate | null>(null);
  const [variables, setVariables] = useState<Record<string, any>>({});
  const [generatedPrompt, setGeneratedPrompt] = useState<string>('');
  const [copyStatus, setCopyStatus] = useState<'idle' | 'copying' | 'success' | 'error'>('idle');
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  const promptCopyService = new PromptCopyService();

  // 实时生成模板
  useEffect(() => {
    try {
      const generator = PromptGeneratorFactory.getGenerator(config.category);
      const newTemplate = generator.generateTemplate(config);
      setTemplate(newTemplate);

      // 重置变量值
      const defaultVariables: Record<string, any> = {};
      newTemplate.variables.forEach(variable => {
        if (variable.defaultValue !== undefined) {
          defaultVariables[variable.name] = variable.defaultValue;
        }
      });
      setVariables(defaultVariables);

      // 清除之前的错误
      setValidationErrors([]);
    } catch (error) {
      console.error('生成模板失败:', error);
      setTemplate(null);
    }
  }, [config]);

  // 处理配置变更
  const handleConfigChange = useCallback((newConfig: Partial<PromptConfig>) => {
    setConfig(prev => ({ ...prev, ...newConfig }));
  }, []);

  // 处理变量变更
  const handleVariableChange = useCallback((variableName: string, value: any) => {
    setVariables(prev => {
      const newVariables = { ...prev, [variableName]: value };

      // 处理变量依赖关系
      if (template) {
        template.variables.forEach(variable => {
          if (variable.dependencies) {
            variable.dependencies.forEach(dep => {
              if (dep.variable === variableName) {
                const shouldShow = checkDependencyCondition(dep, value);
                if (!shouldShow && newVariables[variable.name] !== undefined) {
                  delete newVariables[variable.name];
                }
              }
            });
          }
        });
      }

      return newVariables;
    });
  }, [template]);

  // 检查依赖条件
  const checkDependencyCondition = (dependency: any, value: any): boolean => {
    switch (dependency.condition) {
      case 'equals':
        return value === dependency.value;
      case 'not_equals':
        return value !== dependency.value;
      case 'contains':
        return Array.isArray(value) ? value.includes(dependency.value) : String(value).includes(dependency.value);
      default:
        return true;
    }
  };

  // 验证变量
  const validateVariables = (): boolean => {
    if (!template) return false;

    const errors: string[] = [];

    template.variables.forEach(variable => {
      const value = variables[variable.name];

      // 检查必填项
      if (variable.required && (value === undefined || value === '' || (Array.isArray(value) && value.length === 0))) {
        errors.push(`${variable.label}是必填项`);
      }

      // 检查验证规则
      if (variable.validation && value !== undefined && value !== '') {
        variable.validation.forEach(rule => {
          switch (rule.type) {
            case 'min_length':
              if (String(value).length < rule.value) {
                errors.push(rule.message);
              }
              break;
            case 'max_length':
              if (String(value).length > rule.value) {
                errors.push(rule.message);
              }
              break;
            case 'pattern':
              if (!new RegExp(rule.value).test(String(value))) {
                errors.push(rule.message);
              }
              break;
          }
        });
      }
    });

    setValidationErrors(errors);
    return errors.length === 0;
  };

  // 生成Prompt
  const handleGeneratePrompt = () => {
    if (!template || !validateVariables()) {
      return;
    }

    try {
      const prompt = generatePromptContent(template, variables);
      setGeneratedPrompt(prompt);

      if (onPromptGenerated) {
        const generatedPromptData: GeneratedPrompt = {
          id: `generated_${Date.now()}`,
          template,
          variables,
          generatedContent: prompt,
          metadata: {
            generatedAt: new Date(),
            estimatedTokens: template.metadata.estimatedTokens,
            aiModel: config.aiModel,
            userConfig: config
          }
        };
        onPromptGenerated(generatedPromptData);
      }
    } catch (error) {
      console.error('生成Prompt失败:', error);
    }
  };

  // 生成Prompt内容
  const generatePromptContent = (template: PromptTemplate, variables: Record<string, any>): string => {
    let content = '';

    // 按顺序添加各个部分
    const sortedSections = [...template.promptStructure.sections].sort((a, b) => a.order - b.order);

    sortedSections.forEach(section => {
      if (section.required || checkSectionConditions(section, variables)) {
        content += replaceVariables(section.content, variables) + '\n\n';
      }
    });

    // 添加条件性部分
    if (template.promptStructure.conditionalSections) {
      template.promptStructure.conditionalSections.forEach(conditionalSection => {
        if (checkConditionRule(conditionalSection.condition, variables)) {
          content += replaceVariables(conditionalSection.section.content, variables) + '\n\n';
        }
      });
    }

    // 添加动态指令
    if (template.promptStructure.dynamicInstructions) {
      template.promptStructure.dynamicInstructions.forEach(instruction => {
        if (checkConditionRule(instruction.condition, variables)) {
          content += replaceVariables(instruction.instruction, variables) + '\n\n';
        }
      });
    }

    return content.trim();
  };

  // 检查部分条件
  const checkSectionConditions = (section: any, variables: Record<string, any>): boolean => {
    if (!section.conditions) return true;

    return section.conditions.every((condition: any) =>
      checkConditionRule(condition, variables)
    );
  };

  // 检查条件规则
  const checkConditionRule = (condition: any, variables: Record<string, any>): boolean => {
    if (condition.variable) {
      const value = variables[condition.variable];
      if (condition.equals !== undefined) {
        return value === condition.equals;
      }
      if (condition.not_equals !== undefined) {
        return value !== condition.not_equals;
      }
      if (condition.contains !== undefined) {
        return Array.isArray(value) ? value.includes(condition.contains) : String(value).includes(condition.contains);
      }
    }

    if (condition.difficulty) {
      return config.difficulty === condition.difficulty;
    }

    if (condition.aiModel) {
      return config.aiModel === condition.aiModel;
    }

    return true;
  };

  // 替换变量
  const replaceVariables = (content: string, variables: Record<string, any>): string => {
    let result = content;

    Object.entries(variables).forEach(([key, value]) => {
      const placeholder = `{{${key}}}`;
      const replacement = Array.isArray(value) ? value.join(', ') : String(value);
      result = result.replace(new RegExp(placeholder, 'g'), replacement);
    });

    return result;
  };

  // 复制到剪贴板
  const handleCopy = async (format: 'plain' | 'markdown' | 'structured') => {
    if (!generatedPrompt) return;

    setCopyStatus('copying');
    try {
      const success = await promptCopyService.copyToClipboard(generatedPrompt, format);
      setCopyStatus(success ? 'success' : 'error');

      // 3秒后重置状态
      setTimeout(() => setCopyStatus('idle'), 3000);
    } catch (error) {
      setCopyStatus('error');
      setTimeout(() => setCopyStatus('idle'), 3000);
    }
  };

  // 检查变量是否应该显示
  const shouldShowVariable = (variable: DynamicVariable): boolean => {
    if (!variable.dependencies) return true;

    return variable.dependencies.every(dep => {
      const depValue = variables[dep.variable];
      const shouldShow = checkDependencyCondition(dep, depValue);
      return dep.action === 'show' ? shouldShow : !shouldShow;
    });
  };

  // 渲染变量输入组件
  const renderVariableInput = (variable: DynamicVariable) => {
    if (!shouldShowVariable(variable)) {
      return null;
    }

    const value = variables[variable.name] || '';

    switch (variable.type) {
      case 'text':
        return (
          <Input
            value={value}
            onChange={(e) => handleVariableChange(variable.name, e.target.value)}
            placeholder={variable.placeholder}
            size="md"
          />
        );

      case 'textarea':
        return (
          <Textarea
            value={value}
            onChange={(e) => handleVariableChange(variable.name, e.target.value)}
            placeholder={variable.placeholder}
            rows={3}
            resize="vertical"
          />
        );

      case 'select':
        const selectedOption = variable.options?.find(opt => opt.value === value);
        return (
          <VStack align="stretch" gap={2}>
            <NativeSelect.Root>
              <NativeSelect.Field
                value={value}
                onChange={(e) => handleVariableChange(variable.name, e.target.value)}
              >
                <option value="">请选择</option>
                {variable.options?.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </NativeSelect.Field>
            </NativeSelect.Root>
            {selectedOption?.description && (
              <Text
                fontSize="sm"
                color="fg.muted"
                bg="bg.subtle"
                p={2}
                borderRadius="md"
                borderLeft="3px solid"
                borderColor="blue.500"
              >
                {selectedOption.description}
              </Text>
            )}
          </VStack>
        );

      case 'multiselect':
        return (
          <VStack align="stretch" gap={2}>
            <HStack wrap="wrap" gap={2}>
              {Array.isArray(value) && value.map((item, index) => (
                <Tag.Root key={index} colorPalette="blue" variant="subtle">
                  <Tag.Label>{item}</Tag.Label>
                  <Tag.EndElement>
                    <Tag.CloseTrigger
                      onClick={() => {
                        const newValue = value.filter((_: any, i: number) => i !== index);
                        handleVariableChange(variable.name, newValue);
                      }}
                    />
                  </Tag.EndElement>
                </Tag.Root>
              ))}
            </HStack>
            <NativeSelect.Root>
              <NativeSelect.Field
                onChange={(e) => {
                  if (e.target.value) {
                    const currentValue = Array.isArray(value) ? value : [];
                    if (!currentValue.includes(e.target.value)) {
                      handleVariableChange(variable.name, [...currentValue, e.target.value]);
                    }
                    e.target.value = '';
                  }
                }}
              >
                <option value="">添加选项</option>
                {variable.options?.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </NativeSelect.Field>
            </NativeSelect.Root>
          </VStack>
        );

      case 'number':
        return (
          <Input
            type="number"
            value={value}
            onChange={(e) => handleVariableChange(variable.name, Number(e.target.value))}
            min={variable.min}
            max={variable.max}
            step={variable.step}
          />
        );

      case 'boolean':
        return (
          <HStack gap={4}>
            <label>
              <input
                type="radio"
                name={variable.name}
                checked={value === true}
                onChange={() => handleVariableChange(variable.name, true)}
              />
              <Text ml={2}>是</Text>
            </label>
            <label>
              <input
                type="radio"
                name={variable.name}
                checked={value === false}
                onChange={() => handleVariableChange(variable.name, false)}
              />
              <Text ml={2}>否</Text>
            </label>
          </HStack>
        );

      default:
        return <Text color="red.500">不支持的变量类型: {variable.type}</Text>;
    }
  };

  return (
    <Container maxW="6xl" py={6}>
      <VStack gap={6} align="stretch">
        {/* 配置选择区域 */}
        <Card.Root variant="outline">
          <Box p={6}>
            <Heading size="md" mb={4}>Prompt配置</Heading>

            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} gap={4}>
              <Field.Root>
                <Field.Label>创作阶段</Field.Label>
                <NativeSelect.Root>
                  <NativeSelect.Field
                    value={config.category}
                    onChange={(e) => handleConfigChange({ category: e.target.value as any })}
                  >
                    <option value="structure">结构规划</option>
                    <option value="character">角色创建</option>
                    <option value="world">世界构建</option>
                    <option value="scene">场景设计</option>
                    <option value="dialogue">对话创作</option>
                  </NativeSelect.Field>
                </NativeSelect.Root>
              </Field.Root>

              <Field.Root>
                <Field.Label>难度等级</Field.Label>
                <NativeSelect.Root>
                  <NativeSelect.Field
                    value={config.difficulty}
                    onChange={(e) => handleConfigChange({ difficulty: e.target.value as any })}
                  >
                    <option value="beginner">新手</option>
                    <option value="intermediate">中级</option>
                    <option value="advanced">高级</option>
                  </NativeSelect.Field>
                </NativeSelect.Root>
              </Field.Root>

              <Field.Root>
                <Field.Label>AI模型</Field.Label>
                <NativeSelect.Root>
                  <NativeSelect.Field
                    value={config.aiModel}
                    onChange={(e) => handleConfigChange({ aiModel: e.target.value as any })}
                  >
                    <option value="claude">Claude</option>
                    <option value="gpt">ChatGPT</option>
                    <option value="gemini">Gemini</option>
                    <option value="generic">通用</option>
                  </NativeSelect.Field>
                </NativeSelect.Root>
              </Field.Root>

              <Field.Root>
                <Field.Label>写作风格</Field.Label>
                <NativeSelect.Root>
                  <NativeSelect.Field
                    value={config.writingStyle}
                    onChange={(e) => handleConfigChange({ writingStyle: e.target.value as any })}
                  >
                    <option value="narrative">叙事性</option>
                    <option value="analytical">分析性</option>
                    <option value="creative">创意性</option>
                    <option value="technical">技术性</option>
                  </NativeSelect.Field>
                </NativeSelect.Root>
              </Field.Root>

              <Field.Root>
                <Field.Label>详细程度</Field.Label>
                <NativeSelect.Root>
                  <NativeSelect.Field
                    value={config.detailLevel}
                    onChange={(e) => handleConfigChange({ detailLevel: e.target.value as any })}
                  >
                    <option value="brief">简洁</option>
                    <option value="moderate">适中</option>
                    <option value="detailed">详细</option>
                    <option value="comprehensive">全面</option>
                  </NativeSelect.Field>
                </NativeSelect.Root>
              </Field.Root>
            </SimpleGrid>
          </Box>
        </Card.Root>

        {/* 模板预览 */}
        {template && (
          <Card.Root variant="elevated">
            <Box p={6}>
              <VStack gap={4} align="stretch">
                <HStack justify="space-between">
                  <VStack align="start" gap={1}>
                    <Heading size="md">{template.title}</Heading>
                    <Text color="gray.600">{template.description}</Text>
                  </VStack>
                  <VStack align="end" gap={1}>
                    <Badge colorPalette="blue">
                      {template.variables.length} 个变量
                    </Badge>
                    <Text fontSize="sm" color="gray.500">
                      📊 {template.metadata.estimatedTokens} tokens | ⏱️ {template.metadata.estimatedTime}
                    </Text>
                  </VStack>
                </HStack>
              </VStack>
            </Box>
          </Card.Root>
        )}

        {/* 变量填写区域 */}
        {template && (
          <Card.Root variant="outline">
            <Box p={6}>
              <Heading size="md" mb={4}>填写变量</Heading>

              {validationErrors.length > 0 && (
                <Alert.Root status="error" mb={4}>
                  <Alert.Indicator />
                  <Alert.Content>
                    <Alert.Title>请修正以下错误：</Alert.Title>
                    <Alert.Description>
                      {validationErrors.map((error, index) => (
                        <Text key={index}>• {error}</Text>
                      ))}
                    </Alert.Description>
                  </Alert.Content>
                </Alert.Root>
              )}

              <SimpleGrid columns={{ base: 1, md: 2 }} gap={6}>
                {template.variables.map(variable => (
                  <Field.Root key={variable.name}>
                    <Field.Label>
                      {variable.label}
                      {variable.required && <Text as="span" color="red.500" ml={1}>*</Text>}
                    </Field.Label>
                    {variable.description && (
                      <Field.HelperText mb={2}>{variable.description}</Field.HelperText>
                    )}
                    {renderVariableInput(variable)}
                  </Field.Root>
                ))}
              </SimpleGrid>

              <Button
                onClick={handleGeneratePrompt}
                colorPalette="blue"
                size="lg"
                mt={6}
                disabled={validationErrors.length > 0}
                w="full"
              >
                🎯 生成Prompt
              </Button>
            </Box>
          </Card.Root>
        )}

        {/* Prompt预览和复制区域 */}
        {generatedPrompt && (
          <Card.Root variant="elevated">
            <Box p={6}>
              <VStack gap={4} align="stretch">
                <HStack justify="space-between">
                  <Heading size="md">生成的Prompt</Heading>
                  <HStack gap={2}>
                    <Button
                      onClick={() => handleCopy('plain')}
                      variant="outline"
                      size="sm"
                      colorPalette={copyStatus === 'success' ? 'green' : 'blue'}
                    >
                      {copyStatus === 'copying' ? '复制中...' :
                       copyStatus === 'success' ? '✓ 已复制' : '📋 复制纯文本'}
                    </Button>
                    <Button
                      onClick={() => handleCopy('markdown')}
                      variant="outline"
                      size="sm"
                    >
                      📝 复制Markdown
                    </Button>
                    <Button
                      onClick={() => handleCopy('structured')}
                      variant="outline"
                      size="sm"
                    >
                      🔧 复制结构化
                    </Button>
                  </HStack>
                </HStack>

                <Card.Root variant="outline">
                  <Box p={4}>
                    <Text
                      fontSize="sm"
                      fontFamily="mono"
                      whiteSpace="pre-wrap"
                      bg="gray.50"
                      p={4}
                      borderRadius="md"
                      maxH="400px"
                      overflow="auto"
                      border="1px solid"
                      borderColor="gray.200"
                    >
                      {generatedPrompt}
                    </Text>
                  </Box>
                </Card.Root>

                {copyStatus === 'success' && (
                  <Alert.Root status="success">
                    <Alert.Indicator />
                    <Alert.Content>
                      <Alert.Description>
                        Prompt已复制到剪贴板，现在可以粘贴到AI工具中使用！
                      </Alert.Description>
                    </Alert.Content>
                  </Alert.Root>
                )}
              </VStack>
            </Box>
          </Card.Root>
        )}
      </VStack>
    </Container>
  );
};