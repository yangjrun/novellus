import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  VStack,
  HStack,
  Card,
  Heading,
  Text,
  Button,
  Badge,
  Separator,
  SimpleGrid,
  Progress,
  Alert
} from '@chakra-ui/react';
import { projectDataService, ProjectAnalysisData } from '../services/projectDataService';

interface ProjectDataViewerProps {
  onBack: () => void;
}

export const ProjectDataViewer: React.FC<ProjectDataViewerProps> = ({ onBack }) => {
  const [analysisData, setAnalysisData] = useState<ProjectAnalysisData[]>([]);
  const [selectedData, setSelectedData] = useState<ProjectAnalysisData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalysisData();
  }, []);

  const loadAnalysisData = () => {
    try {
      const data = projectDataService.getAllAnalysisData();
      setAnalysisData(data);
      setLoading(false);
    } catch (error) {
      console.error('加载项目数据失败:', error);
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('zh-CN');
  };

  if (loading) {
    return (
      <Container maxW="container.xl" py={8}>
        <VStack gap={4}>
          <Progress size="sm" colorPalette="blue" />
          <Text>正在加载项目数据...</Text>
        </VStack>
      </Container>
    );
  }

  if (selectedData) {
    return (
      <Container maxW="container.xl" py={8}>
        <VStack gap={6} align="stretch">
          {/* Header */}
          <HStack justify="space-between" align="center">
            <VStack align="flex-start" gap={2}>
              <Heading size="2xl">{selectedData.title}</Heading>
              <HStack gap={2}>
                <Badge colorPalette="blue">{selectedData.category}</Badge>
                <Badge colorPalette="green">{selectedData.difficulty}</Badge>
                <Badge colorPalette="purple">{selectedData.targetAudience}</Badge>
              </HStack>
            </VStack>
            <Button onClick={() => setSelectedData(null)} variant="outline">
              返回列表
            </Button>
          </HStack>

          {/* Core Framework */}
          {selectedData.analysisContent?.coreFramework && (
            <Card.Root>
              <Card.Header>
                <Card.Title>{selectedData.analysisContent.coreFramework.title}</Card.Title>
                <Card.Description>{selectedData.analysisContent.coreFramework.description}</Card.Description>
              </Card.Header>
              <Card.Body>
                <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} gap={4}>
                  {selectedData.analysisContent.coreFramework.stageFlow?.map((stage: any, index: number) => (
                    <Card.Root key={index} variant="outline" size="sm">
                      <Card.Body>
                        <VStack align="stretch" gap={2}>
                          <Text fontWeight="bold" color="blue.600">{stage.percentage}</Text>
                          <Text fontSize="sm" fontWeight="medium">{stage.stage}</Text>
                          <Text fontSize="xs" color="fg.muted">{stage.character}</Text>
                        </VStack>
                      </Card.Body>
                    </Card.Root>
                  ))}
                </SimpleGrid>
              </Card.Body>
            </Card.Root>
          )}

          {/* Key Nodes */}
          {selectedData.analysisContent?.keyNodes && (
            <Card.Root>
              <Card.Header>
                <Card.Title>{selectedData.analysisContent.keyNodes.title}</Card.Title>
              </Card.Header>
              <Card.Body>
                <VStack gap={4} align="stretch">
                  {selectedData.analysisContent.keyNodes.nodes?.map((node: any, index: number) => (
                    <Card.Root key={index} variant="subtle">
                      <Card.Body>
                        <VStack align="stretch" gap={3}>
                          <HStack justify="space-between">
                            <Heading size="md">{node.title}</Heading>
                            <Badge colorPalette="orange">{node.percentage}</Badge>
                          </HStack>

                          <Box>
                            <Text fontSize="sm" fontWeight="medium" mb={2}>叙事功能：</Text>
                            <VStack align="stretch" gap={1}>
                              {node.narrativeFunctions?.map((func: string, i: number) => (
                                <Text key={i} fontSize="sm" color="fg.muted">• {func}</Text>
                              ))}
                            </VStack>
                          </Box>

                          <Box>
                            <Text fontSize="sm" fontWeight="medium" mb={2}>结构特点：</Text>
                            <VStack align="stretch" gap={1}>
                              {node.structuralFeatures?.map((feature: string, i: number) => (
                                <Text key={i} fontSize="sm" color="fg.muted">• {feature}</Text>
                              ))}
                            </VStack>
                          </Box>
                        </VStack>
                      </Card.Body>
                    </Card.Root>
                  ))}
                </VStack>
              </Card.Body>
            </Card.Root>
          )}

          {/* Application Notes */}
          {selectedData.applicationNotes && (
            <Card.Root>
              <Card.Header>
                <Card.Title>应用指导</Card.Title>
                <Card.Description>各创作环节的具体指导建议</Card.Description>
              </Card.Header>
              <Card.Body>
                <SimpleGrid columns={{ base: 1, md: 3 }} gap={6}>
                  <Box>
                    <Heading size="sm" mb={3} color="blue.600">角色创建</Heading>
                    <VStack align="stretch" gap={2}>
                      {selectedData.applicationNotes.characterCreation?.map((note: string, i: number) => (
                        <Text key={i} fontSize="sm">• {note}</Text>
                      ))}
                    </VStack>
                  </Box>

                  <Box>
                    <Heading size="sm" mb={3} color="green.600">世界构建</Heading>
                    <VStack align="stretch" gap={2}>
                      {selectedData.applicationNotes.worldBuilding?.map((note: string, i: number) => (
                        <Text key={i} fontSize="sm">• {note}</Text>
                      ))}
                    </VStack>
                  </Box>

                  <Box>
                    <Heading size="sm" mb={3} color="purple.600">场景设计</Heading>
                    <VStack align="stretch" gap={2}>
                      {selectedData.applicationNotes.sceneDesign?.map((note: string, i: number) => (
                        <Text key={i} fontSize="sm">• {note}</Text>
                      ))}
                    </VStack>
                  </Box>
                </SimpleGrid>
              </Card.Body>
            </Card.Root>
          )}

          {/* Metadata */}
          <Card.Root variant="subtle">
            <Card.Body>
              <SimpleGrid columns={{ base: 1, md: 2 }} gap={4}>
                <VStack align="stretch" gap={2}>
                  <Text fontSize="sm"><strong>创建时间：</strong> {formatDate(selectedData.createdAt)}</Text>
                  <Text fontSize="sm"><strong>AI模型：</strong> {selectedData.metadata.aiModel}</Text>
                  <Text fontSize="sm"><strong>复杂度：</strong> {selectedData.metadata.complexity}</Text>
                </VStack>
                <VStack align="stretch" gap={2}>
                  <Text fontSize="sm"><strong>预计阅读：</strong> {selectedData.metadata.estimatedReadingTime}</Text>
                  <Text fontSize="sm"><strong>生成工具：</strong> {selectedData.metadata.generatedBy}</Text>
                  <Box>
                    <Text fontSize="sm" mb={2}><strong>标签：</strong></Text>
                    <HStack wrap="wrap" gap={1}>
                      {selectedData.metadata.tags?.map((tag: string, i: number) => (
                        <Badge key={i} size="sm" variant="subtle">{tag}</Badge>
                      ))}
                    </HStack>
                  </Box>
                </VStack>
              </SimpleGrid>
            </Card.Body>
          </Card.Root>
        </VStack>
      </Container>
    );
  }

  return (
    <Container maxW="container.xl" py={8}>
      <VStack gap={6} align="stretch">
        {/* Header */}
        <HStack justify="space-between" align="center">
          <VStack align="flex-start" gap={2}>
            <Heading size="2xl">📊 项目数据库</Heading>
            <Text color="fg.muted">查看已保存的分析结果和创作指导</Text>
          </VStack>
          <Button onClick={onBack} variant="outline">
            返回
          </Button>
        </HStack>

        {/* Analysis List */}
        {analysisData.length === 0 ? (
          <Alert.Root status="info">
            <Alert.Indicator />
            <Alert.Title>暂无保存的项目数据</Alert.Title>
            <Alert.Description>
              使用各种AI辅助创作工具生成分析结果后，会自动保存到这里供后续参考。
            </Alert.Description>
          </Alert.Root>
        ) : (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} gap={6}>
            {analysisData.map((data) => (
              <Card.Root
                key={data.id}
                cursor="pointer"
                transition="all 0.2s"
                _hover={{ transform: "translateY(-2px)", shadow: "lg" }}
                onClick={() => setSelectedData(data)}
              >
                <Card.Body>
                  <VStack align="stretch" gap={3}>
                    <HStack justify="space-between">
                      <Badge colorPalette="blue" size="sm">{data.category}</Badge>
                      <Badge colorPalette="green" size="sm">{data.difficulty}</Badge>
                    </HStack>

                    <Heading size="md" noOfLines={2}>{data.title}</Heading>

                    <Text fontSize="sm" color="fg.muted" noOfLines={3}>
                      目标受众: {data.targetAudience} |
                      {data.structureType && ` 结构: ${data.structureType} |`}
                      文化背景: {data.culturalBackground}
                    </Text>

                    <HStack justify="space-between" fontSize="xs" color="fg.muted">
                      <Text>{formatDate(data.createdAt)}</Text>
                      <Text>{data.metadata.estimatedReadingTime}</Text>
                    </HStack>
                  </VStack>
                </Card.Body>
              </Card.Root>
            ))}
          </SimpleGrid>
        )}
      </VStack>
    </Container>
  );
};