// 裂世九域·法则链纪元 - MongoDB文化框架集合架构 (优化版本)
// 支持复杂文化数据、语义关系、向量搜索和知识图谱构建
// 优化后版本：增强数据处理能力和高级分析功能

// 1. 文化详细内容集合
db.createCollection("cultural_details", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["novelId", "domainType", "rawContent"],
            properties: {
                _id: { bsonType: "objectId" },
                novelId: { bsonType: "string", description: "小说ID" },
                domainType: {
                    bsonType: "string",
                    enum: ["人域", "天域", "荒域", "冥域", "魔域", "虚域", "海域", "源域", "永恒域"],
                    description: "所属域"
                },

                // 原始内容
                rawContent: { bsonType: "string", description: "原始文本内容" },
                processedContent: { bsonType: "object", description: "处理后的结构化内容" },

                // 解析结果
                parsedSections: {
                    bsonType: "array",
                    items: {
                        bsonType: "object",
                        properties: {
                            dimension: { bsonType: "string" },
                            title: { bsonType: "string" },
                            content: { bsonType: "string" },
                            keyElements: { bsonType: "array", items: { bsonType: "string" } },
                            extractedEntities: { bsonType: "array" },
                            tags: { bsonType: "array", items: { bsonType: "string" } }
                        }
                    }
                },

                // 元数据
                processingMetadata: {
                    bsonType: "object",
                    properties: {
                        version: { bsonType: "string" },
                        processingDate: { bsonType: "date" },
                        parserVersion: { bsonType: "string" },
                        qualityScore: { bsonType: "double" },
                        completeness: { bsonType: "double" }
                    }
                },

                // 时间戳
                createdAt: { bsonType: "date" },
                updatedAt: { bsonType: "date" }
            }
        }
    }
});

// 2. 剧情钩子详细集合
db.createCollection("plot_hooks_detailed", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["novelId", "domainType", "hookContent"],
            properties: {
                _id: { bsonType: "objectId" },
                novelId: { bsonType: "string" },
                domainType: {
                    bsonType: "string",
                    enum: ["人域", "天域", "荒域", "冥域", "魔域", "虚域", "海域", "源域"]
                },

                // 钩子内容
                hookContent: {
                    bsonType: "object",
                    properties: {
                        title: { bsonType: "string" },
                        description: { bsonType: "string" },
                        fullText: { bsonType: "string" },
                        structuredData: { bsonType: "object" }
                    }
                },

                // 分析数据
                analysis: {
                    bsonType: "object",
                    properties: {
                        themes: { bsonType: "array", items: { bsonType: "string" } },
                        characters: { bsonType: "array" },
                        locations: { bsonType: "array" },
                        conflicts: { bsonType: "array" },
                        opportunities: { bsonType: "array" }
                    }
                },

                // 关联信息
                connections: {
                    bsonType: "object",
                    properties: {
                        relatedEntities: { bsonType: "array" },
                        crossDomainLinks: { bsonType: "array" },
                        culturalReferences: { bsonType: "array" }
                    }
                },

                createdAt: { bsonType: "date" },
                updatedAt: { bsonType: "date" }
            }
        }
    }
});

// 3. 概念词典详细集合
db.createCollection("concepts_dictionary", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["novelId", "term", "definition"],
            properties: {
                _id: { bsonType: "objectId" },
                novelId: { bsonType: "string" },

                // 概念信息
                term: { bsonType: "string", description: "术语名称" },
                definition: { bsonType: "string", description: "定义" },
                category: { bsonType: "string", description: "分类" },
                domainType: {
                    bsonType: "string",
                    enum: ["人域", "天域", "荒域", "冥域", "魔域", "虚域", "海域", "源域"]
                },

                // 详细信息
                detailedInfo: {
                    bsonType: "object",
                    properties: {
                        etymology: { bsonType: "string" },
                        culturalContext: { bsonType: "string" },
                        historicalBackground: { bsonType: "string" },
                        variations: { bsonType: "array" }
                    }
                },

                // 使用信息
                usage: {
                    bsonType: "object",
                    properties: {
                        frequency: { bsonType: "int" },
                        contexts: { bsonType: "array" },
                        examples: { bsonType: "array" },
                        relatedTerms: { bsonType: "array" }
                    }
                },

                // 分析数据
                analysis: {
                    bsonType: "object",
                    properties: {
                        importance: { bsonType: "int" },
                        complexity: { bsonType: "int" },
                        storyRelevance: { bsonType: "double" },
                        culturalSignificance: { bsonType: "double" }
                    }
                },

                createdAt: { bsonType: "date" },
                updatedAt: { bsonType: "date" }
            }
        }
    }
});

// 4. 跨域分析结果集合
db.createCollection("cross_domain_analysis", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["novelId", "analysisType"],
            properties: {
                _id: { bsonType: "objectId" },
                novelId: { bsonType: "string" },

                // 分析类型
                analysisType: {
                    bsonType: "string",
                    enum: ["conflict_analysis", "cultural_exchange", "power_dynamics", "economic_relations", "religious_conflicts"]
                },

                // 分析范围
                scope: {
                    bsonType: "object",
                    properties: {
                        domains: { bsonType: "array" },
                        dimensions: { bsonType: "array" },
                        timeRange: { bsonType: "object" }
                    }
                },

                // 分析结果
                results: {
                    bsonType: "object",
                    properties: {
                        summary: { bsonType: "string" },
                        keyFindings: { bsonType: "array" },
                        conflictPoints: { bsonType: "array" },
                        opportunities: { bsonType: "array" },
                        recommendations: { bsonType: "array" }
                    }
                },

                // 数据详情
                data: {
                    bsonType: "object",
                    properties: {
                        relationshipMatrix: { bsonType: "object" },
                        influenceMap: { bsonType: "object" },
                        timelineData: { bsonType: "array" },
                        statisticalSummary: { bsonType: "object" }
                    }
                },

                // 元数据
                metadata: {
                    bsonType: "object",
                    properties: {
                        analysisVersion: { bsonType: "string" },
                        confidence: { bsonType: "double" },
                        completeness: { bsonType: "double" },
                        lastUpdated: { bsonType: "date" }
                    }
                },

                createdAt: { bsonType: "date" },
                updatedAt: { bsonType: "date" }
            }
        }
    }
});

// 5. 数据处理日志集合
db.createCollection("processing_logs", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["novelId", "processType", "status"],
            properties: {
                _id: { bsonType: "objectId" },
                novelId: { bsonType: "string" },

                // 处理信息
                processType: {
                    bsonType: "string",
                    enum: ["text_parsing", "entity_extraction", "relation_analysis", "quality_check", "data_import"]
                },
                status: {
                    bsonType: "string",
                    enum: ["started", "in_progress", "completed", "failed", "partial"]
                },

                // 处理详情
                processDetails: {
                    bsonType: "object",
                    properties: {
                        inputSize: { bsonType: "int" },
                        outputSize: { bsonType: "int" },
                        processingTime: { bsonType: "double" },
                        errorCount: { bsonType: "int" },
                        warningCount: { bsonType: "int" }
                    }
                },

                // 结果统计
                statistics: {
                    bsonType: "object",
                    properties: {
                        entitiesExtracted: { bsonType: "int" },
                        relationsFound: { bsonType: "int" },
                        conceptsIdentified: { bsonType: "int" },
                        qualityScore: { bsonType: "double" }
                    }
                },

                // 错误和警告
                issues: {
                    bsonType: "array",
                    items: {
                        bsonType: "object",
                        properties: {
                            type: { bsonType: "string" },
                            severity: { bsonType: "string" },
                            message: { bsonType: "string" },
                            context: { bsonType: "string" }
                        }
                    }
                },

                createdAt: { bsonType: "date" },
                updatedAt: { bsonType: "date" }
            }
        }
    }
});

// 6. 文化实体详细集合
db.createCollection("cultural_entities_detailed", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["novelId", "entityName", "entityType"],
            properties: {
                _id: { bsonType: "objectId" },
                novelId: { bsonType: "string" },
                entityId: { bsonType: "string", description: "PostgreSQL中的实体ID" },

                // 基本信息
                entityName: { bsonType: "string" },
                entityType: {
                    bsonType: "string",
                    enum: ["组织机构", "重要概念", "文化物品", "仪式活动", "身份制度", "货币体系", "技术工艺", "信仰体系", "习俗传统"]
                },

                // 详细描述
                detailedDescription: {
                    bsonType: "object",
                    properties: {
                        fullDescription: { bsonType: "string" },
                        physicalDescription: { bsonType: "string" },
                        functionalDescription: { bsonType: "string" },
                        culturalSignificance: { bsonType: "string" }
                    }
                },

                // 历史和演化
                history: {
                    bsonType: "object",
                    properties: {
                        origin: { bsonType: "string" },
                        evolution: { bsonType: "array" },
                        keyEvents: { bsonType: "array" },
                        currentState: { bsonType: "string" }
                    }
                },

                // 关联网络
                relationships: {
                    bsonType: "object",
                    properties: {
                        directConnections: { bsonType: "array" },
                        indirectInfluences: { bsonType: "array" },
                        conflictingEntities: { bsonType: "array" },
                        supportingEntities: { bsonType: "array" }
                    }
                },

                // 分析数据
                analysis: {
                    bsonType: "object",
                    properties: {
                        importanceScore: { bsonType: "double" },
                        influenceRadius: { bsonType: "double" },
                        storyPotential: { bsonType: "double" },
                        conflictPotential: { bsonType: "double" }
                    }
                },

                createdAt: { bsonType: "date" },
                updatedAt: { bsonType: "date" }
            }
        }
    }
});

// 创建索引
// 文化详细内容索引
db.cultural_details.createIndex({ "novelId": 1, "domainType": 1 });
db.cultural_details.createIndex({ "processingMetadata.processingDate": -1 });
db.cultural_details.createIndex({ "$**": "text" }, { name: "full_text_search" });

// 剧情钩子详细索引
db.plot_hooks_detailed.createIndex({ "novelId": 1, "domainType": 1 });
db.plot_hooks_detailed.createIndex({ "analysis.themes": 1 });
db.plot_hooks_detailed.createIndex({ "hookContent.title": "text", "hookContent.description": "text" });

// 概念词典索引
db.concepts_dictionary.createIndex({ "novelId": 1, "term": 1 }, { unique: true });
db.concepts_dictionary.createIndex({ "category": 1, "domainType": 1 });
db.concepts_dictionary.createIndex({ "usage.frequency": -1 });
db.concepts_dictionary.createIndex({ "term": "text", "definition": "text" });

// 跨域分析索引
db.cross_domain_analysis.createIndex({ "novelId": 1, "analysisType": 1 });
db.cross_domain_analysis.createIndex({ "scope.domains": 1 });
db.cross_domain_analysis.createIndex({ "metadata.lastUpdated": -1 });

// 处理日志索引
db.processing_logs.createIndex({ "novelId": 1, "processType": 1 });
db.processing_logs.createIndex({ "status": 1, "createdAt": -1 });
db.processing_logs.createIndex({ "processDetails.processingTime": -1 });

// 文化实体详细索引
db.cultural_entities_detailed.createIndex({ "novelId": 1, "entityId": 1 }, { unique: true });
db.cultural_entities_detailed.createIndex({ "entityType": 1 });
db.cultural_entities_detailed.createIndex({ "analysis.importanceScore": -1 });
db.cultural_entities_detailed.createIndex({ "entityName": "text", "detailedDescription.fullDescription": "text" });

// 插入初始配置文档
db.system_config.insertOne({
    configType: "cultural_framework",
    version: "1.0.0",
    settings: {
        parsingOptions: {
            enableEntityExtraction: true,
            enableRelationAnalysis: true,
            enableQualityCheck: true,
            maxProcessingTime: 300
        },
        qualityThresholds: {
            minimumCompleteness: 0.8,
            minimumConfidence: 0.7,
            maxErrorRate: 0.1
        },
        analysisSettings: {
            enableCrossDomainAnalysis: true,
            enableConflictDetection: true,
            enableInfluenceMapping: true,
            updateFrequency: "daily"
        }
    },
    createdAt: new Date(),
    updatedAt: new Date()
});

// 插入示例数据 - 为裂世九域·法则链纪元
db.cultural_details.insertOne({
    novelId: "e1fd1aa4-bde2-4c76-8cee-334e54fa47d1",
    domainType: "人域",
    rawContent: "人域文化框架示例内容...",
    processedContent: {
        sections: [
            {
                dimension: "权力与法律",
                content: "天命王朝统治体系...",
                entities: ["天命王朝", "链籍三等制"]
            }
        ]
    },
    processingMetadata: {
        version: "1.0.0",
        processingDate: new Date(),
        parserVersion: "1.0.0",
        qualityScore: 0.85,
        completeness: 0.9
    },
    createdAt: new Date(),
    updatedAt: new Date()
});

// 7. 文化向量嵌入集合 - 支持语义搜索和相似性分析
db.createCollection("cultural_embeddings", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["novelId", "contentId", "embedding"],
            properties: {
                _id: { bsonType: "objectId" },
                novelId: { bsonType: "string" },
                contentId: { bsonType: "string", description: "关联的内容ID" },
                contentType: {
                    bsonType: "string",
                    enum: ["entity", "framework", "relation", "text_segment"],
                    description: "内容类型"
                },

                // 向量数据
                embedding: {
                    bsonType: "array",
                    items: { bsonType: "double" },
                    description: "文本嵌入向量"
                },
                dimension: { bsonType: "int", description: "向量维度" },

                // 模型信息
                modelInfo: {
                    bsonType: "object",
                    properties: {
                        modelName: { bsonType: "string" },
                        version: { bsonType: "string" },
                        language: { bsonType: "string", default: "zh-CN" }
                    }
                },

                // 文本元数据
                textMetadata: {
                    bsonType: "object",
                    properties: {
                        originalText: { bsonType: "string" },
                        textLength: { bsonType: "int" },
                        semanticTags: { bsonType: "array", items: { bsonType: "string" } }
                    }
                },

                createdAt: { bsonType: "date" },
                updatedAt: { bsonType: "date" }
            }
        }
    }
});

// 8. 知识图谱存储集合 - 支持图形化分析和可视化
db.createCollection("knowledge_graph", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["novelId", "graphData"],
            properties: {
                _id: { bsonType: "objectId" },
                novelId: { bsonType: "string" },
                graphVersion: { bsonType: "string", description: "图谱版本" },

                // 图谱数据
                graphData: {
                    bsonType: "object",
                    properties: {
                        nodes: {
                            bsonType: "array",
                            items: {
                                bsonType: "object",
                                properties: {
                                    id: { bsonType: "string" },
                                    label: { bsonType: "string" },
                                    type: { bsonType: "string" },
                                    domain: { bsonType: "string" },
                                    properties: { bsonType: "object" },
                                    coordinates: {
                                        bsonType: "object",
                                        properties: {
                                            x: { bsonType: "double" },
                                            y: { bsonType: "double" },
                                            z: { bsonType: "double" }
                                        }
                                    }
                                }
                            }
                        },
                        edges: {
                            bsonType: "array",
                            items: {
                                bsonType: "object",
                                properties: {
                                    id: { bsonType: "string" },
                                    source: { bsonType: "string" },
                                    target: { bsonType: "string" },
                                    type: { bsonType: "string" },
                                    weight: { bsonType: "double" },
                                    properties: { bsonType: "object" }
                                }
                            }
                        }
                    }
                },

                // 图谱统计
                statistics: {
                    bsonType: "object",
                    properties: {
                        nodeCount: { bsonType: "int" },
                        edgeCount: { bsonType: "int" },
                        density: { bsonType: "double" },
                        clusteringCoefficient: { bsonType: "double" },
                        averagePathLength: { bsonType: "double" },
                        centralityMeasures: { bsonType: "object" }
                    }
                },

                // 生成配置
                generationConfig: {
                    bsonType: "object",
                    properties: {
                        algorithm: { bsonType: "string" },
                        parameters: { bsonType: "object" },
                        layoutEngine: { bsonType: "string" },
                        filterCriteria: { bsonType: "object" }
                    }
                },

                createdAt: { bsonType: "date" },
                updatedAt: { bsonType: "date" }
            }
        }
    }
});

// 9. 批量导入任务集合 - 支持大规模数据导入和处理监控
db.createCollection("import_tasks", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["novelId", "taskType", "status"],
            properties: {
                _id: { bsonType: "objectId" },
                novelId: { bsonType: "string" },
                taskName: { bsonType: "string" },

                // 任务信息
                taskType: {
                    bsonType: "string",
                    enum: ["full_import", "incremental_update", "validation", "reprocessing"],
                    description: "任务类型"
                },
                status: {
                    bsonType: "string",
                    enum: ["pending", "running", "completed", "failed", "cancelled"],
                    description: "任务状态"
                },

                // 进度信息
                progress: {
                    bsonType: "object",
                    properties: {
                        totalRecords: { bsonType: "int" },
                        processedRecords: { bsonType: "int" },
                        successfulRecords: { bsonType: "int" },
                        failedRecords: { bsonType: "int" },
                        progressPercentage: { bsonType: "double" }
                    }
                },

                // 配置信息
                configuration: {
                    bsonType: "object",
                    properties: {
                        sourceFile: { bsonType: "string" },
                        importOptions: { bsonType: "object" },
                        validationRules: { bsonType: "object" },
                        processingOptions: { bsonType: "object" }
                    }
                },

                // 结果信息
                results: {
                    bsonType: "object",
                    properties: {
                        summary: { bsonType: "string" },
                        errors: { bsonType: "array" },
                        warnings: { bsonType: "array" },
                        statisticsSummary: { bsonType: "object" }
                    }
                },

                // 时间信息
                startedAt: { bsonType: "date" },
                completedAt: { bsonType: "date" },
                createdAt: { bsonType: "date" },
                updatedAt: { bsonType: "date" }
            }
        }
    }
});

// 扩展索引创建

// 文化向量嵌入索引
db.cultural_embeddings.createIndex({ "novelId": 1, "contentType": 1 });
db.cultural_embeddings.createIndex({ "contentId": 1 }, { unique: true });
db.cultural_embeddings.createIndex({ "modelInfo.modelName": 1, "modelInfo.version": 1 });
db.cultural_embeddings.createIndex({ "dimension": 1 });

// 知识图谱索引
db.knowledge_graph.createIndex({ "novelId": 1, "graphVersion": 1 }, { unique: true });
db.knowledge_graph.createIndex({ "statistics.nodeCount": -1 });
db.knowledge_graph.createIndex({ "createdAt": -1 });

// 批量导入任务索引
db.import_tasks.createIndex({ "novelId": 1, "status": 1 });
db.import_tasks.createIndex({ "taskType": 1, "createdAt": -1 });
db.import_tasks.createIndex({ "status": 1, "startedAt": -1 });

// 添加复合索引优化查询性能
db.cultural_details.createIndex({ "novelId": 1, "domainType": 1, "processingMetadata.processingDate": -1 });
db.cultural_entities_detailed.createIndex({ "novelId": 1, "entityType": 1, "analysis.importanceScore": -1 });
db.processing_logs.createIndex({ "novelId": 1, "processType": 1, "status": 1, "createdAt": -1 });

// 创建聚合管道优化复杂查询
db.createView("cultural_summary_view", "cultural_details", [
    {
        $group: {
            _id: {
                novelId: "$novelId",
                domainType: "$domainType"
            },
            totalContent: { $sum: 1 },
            averageQuality: { $avg: "$processingMetadata.qualityScore" },
            averageCompleteness: { $avg: "$processingMetadata.completeness" },
            lastUpdated: { $max: "$updatedAt" }
        }
    },
    {
        $project: {
            novelId: "$_id.novelId",
            domainType: "$_id.domainType",
            totalContent: 1,
            averageQuality: { $round: ["$averageQuality", 3] },
            averageCompleteness: { $round: ["$averageCompleteness", 3] },
            lastUpdated: 1,
            _id: 0
        }
    }
]);

// 创建全文搜索索引优化
db.cultural_details.createIndex({
    "rawContent": "text",
    "processedContent": "text",
    "parsedSections.content": "text"
}, {
    name: "cultural_content_text_search",
    default_language: "none"
});

db.cultural_entities_detailed.createIndex({
    "entityName": "text",
    "detailedDescription.fullDescription": "text",
    "detailedDescription.culturalSignificance": "text"
}, {
    name: "cultural_entities_text_search",
    default_language: "none"
});

// 插入扩展配置
db.system_config.insertOne({
    configType: "advanced_cultural_framework",
    version: "2.0.0",
    settings: {
        embeddingSettings: {
            enableVectorSearch: true,
            modelName: "text-embedding-3-small",
            dimension: 1536,
            batchSize: 100,
            updateFrequency: "daily"
        },
        graphSettings: {
            enableKnowledgeGraph: true,
            maxNodes: 10000,
            maxEdges: 50000,
            layoutAlgorithm: "force-directed",
            clusteringEnabled: true
        },
        importSettings: {
            maxFileSize: 100, // MB
            supportedFormats: ["txt", "md", "json", "csv"],
            parallelProcessing: true,
            maxConcurrentTasks: 5
        },
        analysisSettings: {
            enableSemanticAnalysis: true,
            enableRelationInference: true,
            enableConflictDetection: true,
            enableTrendAnalysis: true,
            confidenceThreshold: 0.7
        }
    },
    createdAt: new Date(),
    updatedAt: new Date()
});

// 更新示例数据以包含新字段
db.cultural_details.updateOne(
    { novelId: "e1fd1aa4-bde2-4c76-8cee-334e54fa47d1" },
    {
        $set: {
            processedContent: {
                sections: [
                    {
                        dimension: "权力与法律",
                        content: "天命王朝统治体系以法则链为核心，建立了严密的等级制度...",
                        entities: ["天命王朝", "链籍三等制", "法则议会"],
                        semanticTags: ["政治制度", "等级制度", "法则体系"],
                        confidenceScore: 0.92
                    },
                    {
                        dimension: "经济与技术",
                        content: "人域的经济体系以链票为主要货币，技术发展依赖法则链的力量...",
                        entities: ["链票", "法则技术", "贸易公会"],
                        semanticTags: ["货币系统", "技术发展", "贸易体系"],
                        confidenceScore: 0.88
                    }
                ],
                extractedRelations: [
                    {
                        source: "天命王朝",
                        target: "链籍三等制",
                        type: "控制",
                        strength: 0.95
                    },
                    {
                        source: "链票",
                        target: "贸易公会",
                        type: "关联",
                        strength: 0.87
                    }
                ]
            },
            processingMetadata: {
                version: "2.0.0",
                processingDate: new Date(),
                parserVersion: "2.0.0",
                qualityScore: 0.91,
                completeness: 0.94,
                entitiesExtracted: 6,
                relationsFound: 2,
                semanticAnalysisEnabled: true
            }
        }
    }
);

print("MongoDB文化框架集合架构创建完成！");
print("========================================");
print("优化后功能特性：");
print("✓ 9个专用集合，支持复杂文化数据存储");
print("✓ 向量嵌入支持，启用语义搜索功能");
print("✓ 知识图谱存储，支持图形化分析");
print("✓ 批量导入任务管理，支持大规模数据处理");
print("✓ 完整的验证规则确保数据质量");
print("✓ 优化的索引结构支持高性能查询");
print("✓ 全文搜索支持中文内容检索");
print("✓ 聚合视图提供快速统计分析");
print("✓ 扩展配置支持高级分析功能");
print("========================================");