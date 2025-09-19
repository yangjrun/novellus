// 裂世九域·法则链纪元 MongoDB数据库初始化脚本
// 支持复杂文档数据和非结构化内容存储

// 使用novellus数据库
use novellus;

// =============================================================================
// 角色管理集合
// =============================================================================

// 创建角色集合
db.createCollection("characters", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["novel_id", "name", "character_type"],
            properties: {
                novel_id: {
                    bsonType: "string",
                    description: "小说ID，关联PostgreSQL中的novels表"
                },
                name: {
                    bsonType: "string",
                    description: "角色名称"
                },
                character_type: {
                    enum: ["protagonist", "antagonist", "supporting", "background", "mentor", "love_interest"],
                    description: "角色类型"
                },
                basic_info: {
                    bsonType: "object",
                    properties: {
                        full_name: { bsonType: "string" },
                        aliases: { bsonType: "array" },
                        age: { bsonType: "int" },
                        gender: { bsonType: "string" },
                        race: { bsonType: "string" },
                        birthplace: { bsonType: "string" },
                        current_domain: { bsonType: "string" }
                    }
                },
                cultivation_info: {
                    bsonType: "object",
                    properties: {
                        current_stage: { bsonType: "string" },
                        cultivation_method: { bsonType: "string" },
                        law_chains: { bsonType: "array" },
                        chain_marks: { bsonType: "array" },
                        special_abilities: { bsonType: "array" },
                        cultivation_history: { bsonType: "array" }
                    }
                },
                personality: {
                    bsonType: "object",
                    properties: {
                        traits: { bsonType: "array" },
                        motivations: { bsonType: "array" },
                        fears: { bsonType: "array" },
                        goals: { bsonType: "array" },
                        moral_alignment: { bsonType: "string" },
                        personality_type: { bsonType: "string" }
                    }
                },
                appearance: {
                    bsonType: "object",
                    properties: {
                        height: { bsonType: "string" },
                        build: { bsonType: "string" },
                        hair_color: { bsonType: "string" },
                        eye_color: { bsonType: "string" },
                        distinctive_features: { bsonType: "array" },
                        clothing_style: { bsonType: "string" },
                        aura_description: { bsonType: "string" }
                    }
                },
                background: {
                    bsonType: "object",
                    properties: {
                        origin_story: { bsonType: "string" },
                        family_background: { bsonType: "object" },
                        education: { bsonType: "string" },
                        major_events: { bsonType: "array" },
                        relationships: { bsonType: "array" },
                        secrets: { bsonType: "array" }
                    }
                },
                relationships: {
                    bsonType: "array",
                    items: {
                        bsonType: "object",
                        properties: {
                            character_id: { bsonType: "string" },
                            relationship_type: { bsonType: "string" },
                            relationship_status: { bsonType: "string" },
                            description: { bsonType: "string" },
                            importance_level: { bsonType: "int" }
                        }
                    }
                },
                story_role: {
                    bsonType: "object",
                    properties: {
                        importance_level: { bsonType: "int" },
                        screen_time: { bsonType: "string" },
                        character_arc: { bsonType: "string" },
                        plot_functions: { bsonType: "array" },
                        symbolic_meaning: { bsonType: "string" }
                    }
                },
                dialogue_style: {
                    bsonType: "object",
                    properties: {
                        speech_patterns: { bsonType: "array" },
                        vocabulary_level: { bsonType: "string" },
                        accent_dialect: { bsonType: "string" },
                        common_phrases: { bsonType: "array" },
                        emotional_expressions: { bsonType: "object" }
                    }
                },
                status: {
                    enum: ["active", "inactive", "deceased", "missing", "transformed"],
                    description: "角色状态"
                },
                tags: { bsonType: "array" },
                created_at: { bsonType: "date" },
                updated_at: { bsonType: "date" }
            }
        }
    }
});

// =============================================================================
// 地点和场景集合
// =============================================================================

// 创建地点集合
db.createCollection("locations", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["novel_id", "name", "location_type"],
            properties: {
                novel_id: { bsonType: "string" },
                name: { bsonType: "string" },
                location_type: {
                    enum: ["domain", "city", "sect", "palace", "mountain", "forest", "ruin", "battlefield", "cultivation_ground", "secret_realm"],
                    description: "地点类型"
                },
                domain_affiliation: { bsonType: "string" },
                geographical_info: {
                    bsonType: "object",
                    properties: {
                        coordinates: { bsonType: "object" },
                        size: { bsonType: "string" },
                        terrain: { bsonType: "string" },
                        climate: { bsonType: "string" },
                        natural_resources: { bsonType: "array" },
                        dangers: { bsonType: "array" }
                    }
                },
                political_info: {
                    bsonType: "object",
                    properties: {
                        ruling_organization: { bsonType: "string" },
                        population: { bsonType: "int" },
                        governance_system: { bsonType: "string" },
                        laws_and_customs: { bsonType: "array" },
                        diplomatic_relations: { bsonType: "array" }
                    }
                },
                cultivation_aspects: {
                    bsonType: "object",
                    properties: {
                        spiritual_energy_density: { bsonType: "int" },
                        law_chain_affinities: { bsonType: "array" },
                        cultivation_bonuses: { bsonType: "array" },
                        restrictions: { bsonType: "array" },
                        special_phenomena: { bsonType: "array" }
                    }
                },
                physical_description: {
                    bsonType: "object",
                    properties: {
                        architecture: { bsonType: "string" },
                        landmarks: { bsonType: "array" },
                        atmosphere: { bsonType: "string" },
                        sensory_details: { bsonType: "object" },
                        notable_features: { bsonType: "array" }
                    }
                },
                history: {
                    bsonType: "object",
                    properties: {
                        founding_story: { bsonType: "string" },
                        major_events: { bsonType: "array" },
                        previous_rulers: { bsonType: "array" },
                        legendary_figures: { bsonType: "array" },
                        mysterious_aspects: { bsonType: "array" }
                    }
                },
                connected_locations: {
                    bsonType: "array",
                    items: {
                        bsonType: "object",
                        properties: {
                            location_id: { bsonType: "string" },
                            connection_type: { bsonType: "string" },
                            travel_method: { bsonType: "string" },
                            travel_time: { bsonType: "string" },
                            difficulty: { bsonType: "string" }
                        }
                    }
                },
                story_significance: {
                    bsonType: "object",
                    properties: {
                        plot_importance: { bsonType: "int" },
                        symbolic_meaning: { bsonType: "string" },
                        character_connections: { bsonType: "array" },
                        planned_scenes: { bsonType: "array" }
                    }
                },
                status: {
                    enum: ["active", "destroyed", "abandoned", "hidden", "transformed"],
                    description: "地点状态"
                },
                tags: { bsonType: "array" },
                created_at: { bsonType: "date" },
                updated_at: { bsonType: "date" }
            }
        }
    }
});

// =============================================================================
// 物品和法宝集合
// =============================================================================

// 创建物品集合
db.createCollection("items", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["novel_id", "name", "item_type"],
            properties: {
                novel_id: { bsonType: "string" },
                name: { bsonType: "string" },
                item_type: {
                    enum: ["weapon", "armor", "pill", "cultivation_manual", "treasure", "artifact", "material", "consumable"],
                    description: "物品类型"
                },
                rarity: {
                    enum: ["common", "uncommon", "rare", "epic", "legendary", "mythical", "divine"],
                    description: "稀有度"
                },
                basic_info: {
                    bsonType: "object",
                    properties: {
                        grade: { bsonType: "string" },
                        origin: { bsonType: "string" },
                        creator: { bsonType: "string" },
                        age: { bsonType: "string" },
                        value: { bsonType: "object" }
                    }
                },
                physical_properties: {
                    bsonType: "object",
                    properties: {
                        appearance: { bsonType: "string" },
                        material: { bsonType: "string" },
                        weight: { bsonType: "string" },
                        size: { bsonType: "string" },
                        durability: { bsonType: "int" },
                        special_markings: { bsonType: "array" }
                    }
                },
                abilities: {
                    bsonType: "object",
                    properties: {
                        passive_effects: { bsonType: "array" },
                        active_abilities: { bsonType: "array" },
                        special_techniques: { bsonType: "array" },
                        cultivation_bonuses: { bsonType: "array" },
                        restrictions: { bsonType: "array" }
                    }
                },
                law_chain_connections: {
                    bsonType: "array",
                    items: {
                        bsonType: "object",
                        properties: {
                            chain_name: { bsonType: "string" },
                            resonance_level: { bsonType: "int" },
                            enhancement_type: { bsonType: "string" }
                        }
                    }
                },
                requirements: {
                    bsonType: "object",
                    properties: {
                        cultivation_stage: { bsonType: "string" },
                        spiritual_power: { bsonType: "int" },
                        bloodline: { bsonType: "string" },
                        special_conditions: { bsonType: "array" }
                    }
                },
                history: {
                    bsonType: "object",
                    properties: {
                        creation_story: { bsonType: "string" },
                        previous_owners: { bsonType: "array" },
                        legendary_deeds: { bsonType: "array" },
                        curses_blessings: { bsonType: "array" }
                    }
                },
                current_status: {
                    bsonType: "object",
                    properties: {
                        location: { bsonType: "string" },
                        owner: { bsonType: "string" },
                        condition: { bsonType: "string" },
                        accessibility: { bsonType: "string" }
                    }
                },
                story_role: {
                    bsonType: "object",
                    properties: {
                        plot_importance: { bsonType: "int" },
                        symbolic_significance: { bsonType: "string" },
                        character_connections: { bsonType: "array" },
                        planned_usage: { bsonType: "array" }
                    }
                },
                tags: { bsonType: "array" },
                created_at: { bsonType: "date" },
                updated_at: { bsonType: "date" }
            }
        }
    }
});

// =============================================================================
// 事件和情节集合
// =============================================================================

// 创建事件集合
db.createCollection("events", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["novel_id", "name", "event_type"],
            properties: {
                novel_id: { bsonType: "string" },
                name: { bsonType: "string" },
                event_type: {
                    enum: ["battle", "cultivation_breakthrough", "political_intrigue", "discovery", "betrayal", "alliance", "romance", "tragedy", "mystery"],
                    description: "事件类型"
                },
                timeline_info: {
                    bsonType: "object",
                    properties: {
                        chronological_order: { bsonType: "int" },
                        duration: { bsonType: "string" },
                        time_period: { bsonType: "string" },
                        parallel_events: { bsonType: "array" }
                    }
                },
                participants: {
                    bsonType: "array",
                    items: {
                        bsonType: "object",
                        properties: {
                            character_id: { bsonType: "string" },
                            role: { bsonType: "string" },
                            importance: { bsonType: "int" },
                            outcome: { bsonType: "string" }
                        }
                    }
                },
                location_info: {
                    bsonType: "object",
                    properties: {
                        primary_location: { bsonType: "string" },
                        secondary_locations: { bsonType: "array" },
                        environmental_factors: { bsonType: "array" }
                    }
                },
                description: {
                    bsonType: "object",
                    properties: {
                        summary: { bsonType: "string" },
                        detailed_account: { bsonType: "string" },
                        key_moments: { bsonType: "array" },
                        emotional_beats: { bsonType: "array" }
                    }
                },
                consequences: {
                    bsonType: "object",
                    properties: {
                        immediate_effects: { bsonType: "array" },
                        long_term_impacts: { bsonType: "array" },
                        character_changes: { bsonType: "array" },
                        world_changes: { bsonType: "array" }
                    }
                },
                plot_connections: {
                    bsonType: "object",
                    properties: {
                        triggers: { bsonType: "array" },
                        leads_to: { bsonType: "array" },
                        foreshadowing: { bsonType: "array" },
                        callbacks: { bsonType: "array" }
                    }
                },
                themes: {
                    bsonType: "array",
                    description: "事件体现的主题"
                },
                status: {
                    enum: ["planned", "in_progress", "completed", "revised", "cancelled"],
                    description: "事件状态"
                },
                tags: { bsonType: "array" },
                created_at: { bsonType: "date" },
                updated_at: { bsonType: "date" }
            }
        }
    }
});

// =============================================================================
// 知识库集合
// =============================================================================

// 创建知识库集合
db.createCollection("knowledge_base", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["novel_id", "title", "category"],
            properties: {
                novel_id: { bsonType: "string" },
                title: { bsonType: "string" },
                category: {
                    enum: ["world_history", "cultivation_theory", "politics", "geography", "culture", "language", "mythology", "technology", "economics"],
                    description: "知识分类"
                },
                content: {
                    bsonType: "object",
                    properties: {
                        summary: { bsonType: "string" },
                        detailed_info: { bsonType: "string" },
                        examples: { bsonType: "array" },
                        references: { bsonType: "array" },
                        contradictions: { bsonType: "array" }
                    }
                },
                related_entities: {
                    bsonType: "array",
                    items: {
                        bsonType: "object",
                        properties: {
                            entity_type: { bsonType: "string" },
                            entity_id: { bsonType: "string" },
                            relationship: { bsonType: "string" }
                        }
                    }
                },
                sources: {
                    bsonType: "array",
                    description: "信息来源"
                },
                reliability: {
                    bsonType: "int",
                    minimum: 1,
                    maximum: 10,
                    description: "信息可靠度(1-10)"
                },
                tags: { bsonType: "array" },
                created_at: { bsonType: "date" },
                updated_at: { bsonType: "date" }
            }
        }
    }
});

// =============================================================================
// 创建索引
// =============================================================================

// 角色集合索引
db.characters.createIndex({ "novel_id": 1, "name": 1 }, { unique: true });
db.characters.createIndex({ "novel_id": 1, "character_type": 1 });
db.characters.createIndex({ "cultivation_info.current_stage": 1 });
db.characters.createIndex({ "status": 1 });
db.characters.createIndex({ "tags": 1 });
db.characters.createIndex({ "name": "text", "basic_info.full_name": "text" });

// 地点集合索引
db.locations.createIndex({ "novel_id": 1, "name": 1 }, { unique: true });
db.locations.createIndex({ "novel_id": 1, "location_type": 1 });
db.locations.createIndex({ "domain_affiliation": 1 });
db.locations.createIndex({ "status": 1 });
db.locations.createIndex({ "tags": 1 });
db.locations.createIndex({ "name": "text", "physical_description.atmosphere": "text" });

// 物品集合索引
db.items.createIndex({ "novel_id": 1, "name": 1 }, { unique: true });
db.items.createIndex({ "novel_id": 1, "item_type": 1 });
db.items.createIndex({ "rarity": 1 });
db.items.createIndex({ "current_status.owner": 1 });
db.items.createIndex({ "tags": 1 });
db.items.createIndex({ "name": "text", "physical_properties.appearance": "text" });

// 事件集合索引
db.events.createIndex({ "novel_id": 1, "name": 1 });
db.events.createIndex({ "novel_id": 1, "event_type": 1 });
db.events.createIndex({ "timeline_info.chronological_order": 1 });
db.events.createIndex({ "participants.character_id": 1 });
db.events.createIndex({ "status": 1 });
db.events.createIndex({ "tags": 1 });
db.events.createIndex({ "name": "text", "description.summary": "text" });

// 知识库集合索引
db.knowledge_base.createIndex({ "novel_id": 1, "title": 1 }, { unique: true });
db.knowledge_base.createIndex({ "novel_id": 1, "category": 1 });
db.knowledge_base.createIndex({ "reliability": 1 });
db.knowledge_base.createIndex({ "tags": 1 });
db.knowledge_base.createIndex({ "title": "text", "content.summary": "text" });

// =============================================================================
// 初始化预设数据
// =============================================================================

// 插入裂世九域的基本设定（示例数据）
db.knowledge_base.insertMany([
    {
        novel_id: "default",
        title: "九域修炼体系总览",
        category: "cultivation_theory",
        content: {
            summary: "裂世九域的修炼体系以法则链为核心，分为七个主要阶段",
            detailed_info: "修炼阶段：凡身 → 开脉 → 归源 → 封侯 → 破界 → 帝境 → 裂世者。每个阶段都有其独特的力量特征和突破要求。",
            examples: [
                "凡身期：淬炼肉身，为开脉做准备",
                "开脉期：打通经脉，感知法则链",
                "归源期：深度理解法则本质",
                "封侯期：掌控区域法则",
                "破界期：突破域界限制",
                "帝境期：建立自身法则领域",
                "裂世者：能够撕裂现实规则"
            ]
        },
        related_entities: [],
        sources: ["世界观设定文档"],
        reliability: 10,
        tags: ["修炼", "法则链", "体系"],
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        novel_id: "default",
        title: "九大域基本情况",
        category: "geography",
        content: {
            summary: "裂世九域包含九个不同特色的域界，每个域都有独特的法则特性",
            detailed_info: "人域、天域、灵域、魔域、仙域、神域、虚域、混沌域、永恒域，每个域都有其独特的生态系统、修炼环境和统治结构。"
        },
        related_entities: [],
        sources: ["世界观设定文档"],
        reliability: 10,
        tags: ["九域", "地理", "世界观"],
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        novel_id: "default",
        title: "四大权力组织",
        category: "politics",
        content: {
            summary: "天命王朝、法则宗门、祭司议会、裂世反叛军四大势力主导政治格局",
            detailed_info: "每个组织都有其独特的理念、组织架构和势力范围，形成复杂的政治关系网。"
        },
        related_entities: [],
        sources: ["世界观设定文档"],
        reliability: 10,
        tags: ["政治", "组织", "权力"],
        created_at: new Date(),
        updated_at: new Date()
    }
]);

print("MongoDB数据库初始化完成！");
print("已创建集合：characters, locations, items, events, knowledge_base");
print("已创建索引以优化查询性能");
print("已插入基础世界观数据");