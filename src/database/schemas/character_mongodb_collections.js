// =============================================================================
// MongoDB 角色管理集合结构定义
// 支持复杂角色数据的文档存储和版本管理
// =============================================================================

// =============================================================================
// 1. 角色档案集合 (character_profiles)
// =============================================================================

/**
 * 角色档案集合结构定义
 * 存储完整的角色设定数据，支持版本化管理
 */
const characterProfilesSchema = {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["character_unique_id", "character_name", "novel_id", "domain_code", "version"],
      properties: {
        // 基础标识信息
        character_unique_id: {
          bsonType: "string",
          description: "角色唯一标识，格式: lieshi-jiuyu-linlan-001"
        },
        character_name: {
          bsonType: "string",
          description: "角色姓名，跨域不变"
        },
        novel_id: {
          bsonType: "int",
          description: "所属小说ID"
        },
        novel_code: {
          bsonType: "string",
          description: "小说代码标识"
        },

        // 版本管理信息
        domain_code: {
          bsonType: "string",
          description: "当前所在域代码，如 ren_yu, tian_yu"
        },
        version: {
          bsonType: "string",
          pattern: "^[0-9]+\\.[0-9]+$",
          description: "版本号，格式 1.0"
        },
        previous_version: {
          bsonType: ["null", "object"],
          description: "前一版本引用信息"
        },

        // 基础信息 (简单结构)
        basic_info: {
          bsonType: "object",
          properties: {
            name: { bsonType: "string" },
            alias: { bsonType: "array", items: { bsonType: "string" } },
            age: { bsonType: "int" },
            gender: { bsonType: "string" },
            occupation: { bsonType: "string" },
            social_status: { bsonType: "string" }
          }
        },

        // 外貌特征
        appearance: {
          bsonType: "object",
          properties: {
            height: { bsonType: "string" },
            weight: { bsonType: "string" },
            hair_color: { bsonType: "string" },
            eye_color: { bsonType: "string" },
            skin_tone: { bsonType: "string" },
            body_type: { bsonType: "string" },
            special_marks: { bsonType: "array" },
            clothing_style: { bsonType: "string" }
          }
        },

        // 性格特质 (复杂嵌套结构)
        personality: {
          bsonType: "object",
          properties: {
            core_traits: { bsonType: "array" },
            values: { bsonType: "array" },
            beliefs: { bsonType: "array" },
            fears: { bsonType: "array" },
            desires: { bsonType: "array" },
            weaknesses: { bsonType: "array" },
            strengths: { bsonType: "array" }
          }
        },

        // 背景故事
        background: {
          bsonType: "object",
          properties: {
            birthplace: { bsonType: "string" },
            family: { bsonType: "string" },
            childhood: { bsonType: "string" },
            education: { bsonType: "string" },
            important_events: { bsonType: "array" },
            trauma: { bsonType: "array" },
            achievements: { bsonType: "array" }
          }
        },

        // 能力技能
        abilities: {
          bsonType: "object",
          properties: {
            professional_skills: { bsonType: "array" },
            special_talents: { bsonType: "array" },
            languages: { bsonType: "array" },
            learning_ability: { bsonType: "string" },
            social_skills: { bsonType: "string" },
            practical_skills: { bsonType: "array" }
          }
        },

        // 人际关系 (引用关系，详细数据在 PostgreSQL)
        relationships: {
          bsonType: "object",
          properties: {
            family: { bsonType: "array" },
            friends: { bsonType: "array" },
            lovers: { bsonType: "array" },
            enemies: { bsonType: "array" },
            mentors: { bsonType: "array" },
            subordinates: { bsonType: "array" },
            social_circle: { bsonType: "array" }
          }
        },

        // 生活状况
        lifestyle: {
          bsonType: "object",
          properties: {
            residence: { bsonType: "string" },
            economic_status: { bsonType: "string" },
            daily_routine: { bsonType: "string" },
            hobbies: { bsonType: "array" },
            food_preferences: { bsonType: "array" },
            entertainment: { bsonType: "array" }
          }
        },

        // 心理状态 (极其复杂的结构)
        psychology: {
          bsonType: "object",
          properties: {
            mental_health: { bsonType: "string" },
            mental_health_status: { bsonType: "string" },
            coping_mechanisms: { bsonType: "array" },
            emotional_patterns: { bsonType: "array" },
            trauma: { bsonType: "array" },
            growth_needs: { bsonType: "array" },
            cognitive_patterns: { bsonType: "array" },
            stress_responses: { bsonType: "array" },
            emotional_intelligence: { bsonType: "object" },
            psychological_defenses: { bsonType: "array" },
            mental_health_history: { bsonType: "array" }
          }
        },

        // 角色成长轨迹 (动态数据)
        character_arc: {
          bsonType: "object",
          properties: {
            current_stage: { bsonType: "string" },
            development_goals: { bsonType: "array" },
            growth_milestones: { bsonType: "array" },
            personality_changes: { bsonType: "array" },
            skill_progression: { bsonType: "array" },
            relationship_evolution: { bsonType: "array" },
            internal_conflicts: { bsonType: "array" },
            external_challenges: { bsonType: "array" }
          }
        },

        // 行为模式 (交互系统)
        behavior_profile: {
          bsonType: "object",
          properties: {
            communication_style: { bsonType: "object" },
            body_language: { bsonType: "object" },
            decision_making: { bsonType: "object" },
            conflict_response: { bsonType: "object" },
            social_behavior: { bsonType: "object" },
            work_style: { bsonType: "object" },
            leadership_style: { bsonType: "object" },
            learning_style: { bsonType: "object" }
          }
        },

        // 跨域变化记录
        domain_transitions: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              from_domain: { bsonType: "string" },
              to_domain: { bsonType: "string" },
              transition_date: { bsonType: "date" },
              major_changes: { bsonType: "array" },
              adaptation_notes: { bsonType: "string" }
            }
          }
        },

        // 元数据
        metadata: {
          bsonType: "object",
          properties: {
            created_at: { bsonType: "date" },
            updated_at: { bsonType: "date" },
            created_by: { bsonType: "string" },
            last_modified_by: { bsonType: "string" },
            tags: { bsonType: "array" },
            notes: { bsonType: "string" },
            role_playing_notes: { bsonType: "array" }
          }
        },

        // 状态标记
        is_current_version: {
          bsonType: "bool",
          description: "是否为当前版本"
        },
        is_archived: {
          bsonType: "bool",
          description: "是否已归档"
        }
      }
    }
  }
};

// 创建角色档案集合的函数
function createCharacterProfilesCollection(db) {
  // 创建集合
  db.createCollection("character_profiles", characterProfilesSchema);

  // 创建索引
  db.character_profiles.createIndex(
    { "character_unique_id": 1, "domain_code": 1, "version": 1 },
    { unique: true, name: "idx_character_domain_version" }
  );

  db.character_profiles.createIndex(
    { "novel_id": 1, "character_unique_id": 1 },
    { name: "idx_novel_character" }
  );

  db.character_profiles.createIndex(
    { "character_unique_id": 1, "is_current_version": 1 },
    { name: "idx_character_current" }
  );

  db.character_profiles.createIndex(
    { "domain_code": 1, "is_current_version": 1 },
    { name: "idx_domain_current" }
  );

  db.character_profiles.createIndex(
    { "metadata.created_at": -1 },
    { name: "idx_created_date" }
  );

  // 文本搜索索引
  db.character_profiles.createIndex(
    {
      "character_name": "text",
      "basic_info.occupation": "text",
      "background.birthplace": "text",
      "metadata.tags": "text"
    },
    { name: "idx_character_text_search" }
  );

  // 复合查询索引
  db.character_profiles.createIndex(
    { "novel_id": 1, "domain_code": 1, "is_current_version": 1 },
    { name: "idx_novel_domain_current" }
  );
}

// =============================================================================
// 2. 角色关系详情集合 (character_relationship_details)
// =============================================================================

/**
 * 角色关系详情集合
 * 存储复杂的人际关系数据和关系演进历史
 */
const characterRelationshipDetailsSchema = {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["novel_id", "source_character_id", "target_character_id", "relationship_type"],
      properties: {
        novel_id: { bsonType: "int" },
        source_character_id: { bsonType: "string" },
        target_character_id: { bsonType: "string" },
        relationship_type: { bsonType: "string" },

        // 关系详情
        relationship_details: {
          bsonType: "object",
          properties: {
            description: { bsonType: "string" },
            importance: { bsonType: "string" },
            emotional_intensity: { bsonType: "int" },
            trust_level: { bsonType: "int" },
            influence_degree: { bsonType: "int" }
          }
        },

        // 域特定信息
        domain_context: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              domain_code: { bsonType: "string" },
              relationship_manifestation: { bsonType: "string" },
              social_recognition: { bsonType: "string" },
              interaction_frequency: { bsonType: "string" }
            }
          }
        },

        // 关系历史
        evolution_history: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              date: { bsonType: "date" },
              change_type: { bsonType: "string" },
              description: { bsonType: "string" },
              trigger_event: { bsonType: "string" },
              domain_code: { bsonType: "string" }
            }
          }
        },

        metadata: {
          bsonType: "object",
          properties: {
            created_at: { bsonType: "date" },
            updated_at: { bsonType: "date" },
            is_bidirectional: { bsonType: "bool" },
            is_active: { bsonType: "bool" }
          }
        }
      }
    }
  }
};

function createCharacterRelationshipDetailsCollection(db) {
  db.createCollection("character_relationship_details", characterRelationshipDetailsSchema);

  // 创建索引
  db.character_relationship_details.createIndex(
    { "source_character_id": 1, "target_character_id": 1 },
    { name: "idx_relationship_pair" }
  );

  db.character_relationship_details.createIndex(
    { "novel_id": 1, "relationship_type": 1 },
    { name: "idx_novel_relationship_type" }
  );

  db.character_relationship_details.createIndex(
    { "domain_context.domain_code": 1 },
    { name: "idx_relationship_domain" }
  );
}

// =============================================================================
// 3. 角色发展轨迹集合 (character_development_tracks)
// =============================================================================

/**
 * 角色发展轨迹集合
 * 追踪角色的成长历程和发展变化
 */
const characterDevelopmentTracksSchema = {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["character_unique_id", "novel_id", "track_type"],
      properties: {
        character_unique_id: { bsonType: "string" },
        novel_id: { bsonType: "int" },
        track_type: {
          bsonType: "string",
          enum: ["skill", "personality", "relationship", "goal", "milestone"]
        },

        // 轨迹数据
        development_data: {
          bsonType: "object",
          properties: {
            track_name: { bsonType: "string" },
            start_state: { bsonType: "object" },
            current_state: { bsonType: "object" },
            target_state: { bsonType: "object" },
            progress_percentage: { bsonType: "int" }
          }
        },

        // 发展历史
        development_history: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              timestamp: { bsonType: "date" },
              domain_code: { bsonType: "string" },
              change_description: { bsonType: "string" },
              trigger_event: { bsonType: "string" },
              impact_assessment: { bsonType: "object" }
            }
          }
        },

        metadata: {
          bsonType: "object",
          properties: {
            created_at: { bsonType: "date" },
            updated_at: { bsonType: "date" },
            is_active: { bsonType: "bool" },
            priority_level: { bsonType: "int" }
          }
        }
      }
    }
  }
};

function createCharacterDevelopmentTracksCollection(db) {
  db.createCollection("character_development_tracks", characterDevelopmentTracksSchema);

  db.character_development_tracks.createIndex(
    { "character_unique_id": 1, "track_type": 1 },
    { name: "idx_character_track_type" }
  );

  db.character_development_tracks.createIndex(
    { "novel_id": 1, "track_type": 1, "metadata.is_active": 1 },
    { name: "idx_novel_active_tracks" }
  );
}

// =============================================================================
// 4. 角色心理状态历史集合 (character_psychological_history)
// =============================================================================

/**
 * 角色心理状态历史集合
 * 详细记录角色的心理变化和心理健康状况
 */
const characterPsychologicalHistorySchema = {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["character_unique_id", "novel_id", "record_date"],
      properties: {
        character_unique_id: { bsonType: "string" },
        novel_id: { bsonType: "int" },
        domain_code: { bsonType: "string" },
        record_date: { bsonType: "date" },

        // 心理状态快照
        psychological_snapshot: {
          bsonType: "object",
          properties: {
            mental_health_status: { bsonType: "string" },
            stress_level: { bsonType: "int" },
            emotional_stability: { bsonType: "int" },
            coping_effectiveness: { bsonType: "int" }
          }
        },

        // 具体事件记录
        psychological_events: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              event_type: { bsonType: "string" },
              trigger: { bsonType: "string" },
              response: { bsonType: "string" },
              impact: { bsonType: "string" },
              recovery_method: { bsonType: "string" }
            }
          }
        },

        // 治疗或康复记录
        intervention_records: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              intervention_type: { bsonType: "string" },
              description: { bsonType: "string" },
              effectiveness: { bsonType: "int" },
              duration: { bsonType: "string" }
            }
          }
        },

        metadata: {
          bsonType: "object",
          properties: {
            recorded_by: { bsonType: "string" },
            notes: { bsonType: "string" },
            confidence_level: { bsonType: "int" }
          }
        }
      }
    }
  }
};

function createCharacterPsychologicalHistoryCollection(db) {
  db.createCollection("character_psychological_history", characterPsychologicalHistorySchema);

  db.character_psychological_history.createIndex(
    { "character_unique_id": 1, "record_date": -1 },
    { name: "idx_character_psych_timeline" }
  );

  db.character_psychological_history.createIndex(
    { "novel_id": 1, "domain_code": 1 },
    { name: "idx_novel_domain_psych" }
  );
}

// =============================================================================
// 5. 初始化所有集合的函数
// =============================================================================

function initializeCharacterCollections(db) {
  console.log("开始初始化角色管理 MongoDB 集合...");

  try {
    // 创建所有集合
    createCharacterProfilesCollection(db);
    console.log("✓ 角色档案集合创建完成");

    createCharacterRelationshipDetailsCollection(db);
    console.log("✓ 角色关系详情集合创建完成");

    createCharacterDevelopmentTracksCollection(db);
    console.log("✓ 角色发展轨迹集合创建完成");

    createCharacterPsychologicalHistoryCollection(db);
    console.log("✓ 角色心理状态历史集合创建完成");

    console.log("所有角色管理集合初始化完成！");

  } catch (error) {
    console.error("初始化角色管理集合时出错：", error);
    throw error;
  }
}

// =============================================================================
// 6. 示例文档结构（供参考）
// =============================================================================

const exampleCharacterProfile = {
  character_unique_id: "lieshi-jiuyu-linlan-001",
  character_name: "林岚",
  novel_id: 1,
  novel_code: "lieshi-jiuyu",
  domain_code: "ren_yu",
  version: "1.0",
  previous_version: null,

  basic_info: {
    name: "林岚",
    alias: ["小岚", "半环"],
    age: 18,
    gender: "female",
    occupation: "外堂童生（水工学徒/抄写）",
    social_status: "灰籍"
  },

  // ... 其他所有字段 ...

  metadata: {
    created_at: new Date(),
    updated_at: new Date(),
    created_by: "system",
    tags: ["主角", "人域", "水工"],
    role_playing_notes: [
      "Domain: 人域",
      "KeyLocations: 枢链城 / 环印关镇",
      "口头禅: '先把账本拿来' '条款先读清'"
    ]
  },

  is_current_version: true,
  is_archived: false
};

// 导出初始化函数
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    initializeCharacterCollections,
    createCharacterProfilesCollection,
    createCharacterRelationshipDetailsCollection,
    createCharacterDevelopmentTracksCollection,
    createCharacterPsychologicalHistoryCollection,
    exampleCharacterProfile
  };
}