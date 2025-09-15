import React, { useState, useEffect } from 'react';
import { Character } from '@types/index';
import { CharacterService } from '@services/characterService';
import './CharacterForm.css';

interface CharacterFormProps {
  character?: Character;
  onSave: (character: Character) => void;
  onCancel: () => void;
}

const SECTIONS = [
  { key: 'basicInfo', label: '基本信息', icon: '👤' },
  { key: 'appearance', label: '外貌特征', icon: '👀' },
  { key: 'personality', label: '性格特质', icon: '💭' },
  { key: 'background', label: '背景故事', icon: '📚' },
  { key: 'abilities', label: '能力技能', icon: '⚡' },
  { key: 'relationships', label: '人际关系', icon: '👥' },
  { key: 'lifestyle', label: '生活状况', icon: '🏠' },
  { key: 'psychology', label: '心理状态', icon: '🧠' },
  { key: 'storyRole', label: '故事功能', icon: '📖' },
  { key: 'specialSettings', label: '特殊设定', icon: '🌟' }
];

export const CharacterForm: React.FC<CharacterFormProps> = ({
  character,
  onSave,
  onCancel
}) => {
  const [characterService] = useState(new CharacterService());
  const [formData, setFormData] = useState<Character>(
    character || characterService.createDefaultCharacter()
  );
  const [currentSection, setCurrentSection] = useState('basicInfo');
  const [errors, setErrors] = useState<string[]>([]);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (character) {
      setFormData(character);
    }
  }, [character]);

  const handleSectionChange = (section: string) => {
    setCurrentSection(section);
    setErrors([]); // 清除错误信息
  };

  const handleFieldChange = (section: string, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [section]: {
        ...prev[section as keyof Character],
        [field]: value
      }
    }));
  };

  const handleArrayFieldChange = (section: string, field: string, index: number, value: string) => {
    setFormData(prev => {
      const sectionData = prev[section as keyof Character] as any;
      const newArray = [...sectionData[field]];
      newArray[index] = value;

      return {
        ...prev,
        [section]: {
          ...sectionData,
          [field]: newArray
        }
      };
    });
  };

  const addArrayItem = (section: string, field: string) => {
    setFormData(prev => {
      const sectionData = prev[section as keyof Character] as any;
      const newArray = [...sectionData[field], ''];

      return {
        ...prev,
        [section]: {
          ...sectionData,
          [field]: newArray
        }
      };
    });
  };

  const removeArrayItem = (section: string, field: string, index: number) => {
    setFormData(prev => {
      const sectionData = prev[section as keyof Character] as any;
      const newArray = sectionData[field].filter((_: any, i: number) => i !== index);

      return {
        ...prev,
        [section]: {
          ...sectionData,
          [field]: newArray
        }
      };
    });
  };

  const handleSave = async () => {
    const validation = characterService.validateCharacter(formData);

    if (!validation.isValid) {
      setErrors(validation.errors);
      return;
    }

    setIsSaving(true);
    setErrors([]);

    try {
      const savedCharacter = await characterService.saveCharacter(formData);
      onSave(savedCharacter);
    } catch (error) {
      setErrors(['保存失败，请重试']);
      console.error('保存角色失败:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const renderBasicInfo = () => (
    <div className="form-section">
      <h3>基本信息</h3>
      <div className="form-grid">
        <div className="form-group">
          <label>姓名 *</label>
          <input
            type="text"
            value={formData.basicInfo.name}
            onChange={(e) => handleFieldChange('basicInfo', 'name', e.target.value)}
            placeholder="角色姓名"
          />
        </div>

        <div className="form-group">
          <label>年龄</label>
          <input
            type="text"
            value={formData.basicInfo.age}
            onChange={(e) => handleFieldChange('basicInfo', 'age', e.target.value)}
            placeholder="例：25岁 / 青年 / 中年"
          />
        </div>

        <div className="form-group">
          <label>性别</label>
          <select
            value={formData.basicInfo.gender}
            onChange={(e) => handleFieldChange('basicInfo', 'gender', e.target.value)}
          >
            <option value="">请选择</option>
            <option value="男">男</option>
            <option value="女">女</option>
            <option value="其他">其他</option>
          </select>
        </div>

        <div className="form-group">
          <label>职业</label>
          <input
            type="text"
            value={formData.basicInfo.occupation}
            onChange={(e) => handleFieldChange('basicInfo', 'occupation', e.target.value)}
            placeholder="角色的职业或身份"
          />
        </div>

        <div className="form-group">
          <label>社会地位</label>
          <input
            type="text"
            value={formData.basicInfo.socialStatus}
            onChange={(e) => handleFieldChange('basicInfo', 'socialStatus', e.target.value)}
            placeholder="在社会中的地位等级"
          />
        </div>
      </div>

      <div className="form-group">
        <label>别名/昵称</label>
        <div className="array-input">
          {formData.basicInfo.alias?.map((alias, index) => (
            <div key={index} className="array-item">
              <input
                type="text"
                value={alias}
                onChange={(e) => handleArrayFieldChange('basicInfo', 'alias', index, e.target.value)}
                placeholder="别名或昵称"
              />
              <button
                type="button"
                onClick={() => removeArrayItem('basicInfo', 'alias', index)}
                className="remove-btn"
              >
                ×
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={() => addArrayItem('basicInfo', 'alias')}
            className="add-btn"
          >
            + 添加别名
          </button>
        </div>
      </div>
    </div>
  );

  const renderPersonality = () => (
    <div className="form-section">
      <h3>性格特质</h3>

      <div className="form-group">
        <label>核心性格特质 *</label>
        <div className="array-input">
          {formData.personality.coreTraits.map((trait, index) => (
            <div key={index} className="array-item">
              <input
                type="text"
                value={trait}
                onChange={(e) => handleArrayFieldChange('personality', 'coreTraits', index, e.target.value)}
                placeholder="例：勇敢、善良、固执"
              />
              <button
                type="button"
                onClick={() => removeArrayItem('personality', 'coreTraits', index)}
                className="remove-btn"
              >
                ×
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={() => addArrayItem('personality', 'coreTraits')}
            className="add-btn"
          >
            + 添加特质
          </button>
        </div>
      </div>

      <div className="form-group">
        <label>价值观</label>
        <div className="array-input">
          {formData.personality.values.map((value, index) => (
            <div key={index} className="array-item">
              <input
                type="text"
                value={value}
                onChange={(e) => handleArrayFieldChange('personality', 'values', index, e.target.value)}
                placeholder="重要的价值观念"
              />
              <button
                type="button"
                onClick={() => removeArrayItem('personality', 'values', index)}
                className="remove-btn"
              >
                ×
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={() => addArrayItem('personality', 'values')}
            className="add-btn"
          >
            + 添加价值观
          </button>
        </div>
      </div>

      <div className="form-group">
        <label>恐惧</label>
        <div className="array-input">
          {formData.personality.fears.map((fear, index) => (
            <div key={index} className="array-item">
              <input
                type="text"
                value={fear}
                onChange={(e) => handleArrayFieldChange('personality', 'fears', index, e.target.value)}
                placeholder="最害怕的事物"
              />
              <button
                type="button"
                onClick={() => removeArrayItem('personality', 'fears', index)}
                className="remove-btn"
              >
                ×
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={() => addArrayItem('personality', 'fears')}
            className="add-btn"
          >
            + 添加恐惧
          </button>
        </div>
      </div>

      <div className="form-group">
        <label>欲望</label>
        <div className="array-input">
          {formData.personality.desires.map((desire, index) => (
            <div key={index} className="array-item">
              <input
                type="text"
                value={desire}
                onChange={(e) => handleArrayFieldChange('personality', 'desires', index, e.target.value)}
                placeholder="最渴望得到的东西"
              />
              <button
                type="button"
                onClick={() => removeArrayItem('personality', 'desires', index)}
                className="remove-btn"
              >
                ×
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={() => addArrayItem('personality', 'desires')}
            className="add-btn"
          >
            + 添加欲望
          </button>
        </div>
      </div>
    </div>
  );

  const renderStoryRole = () => (
    <div className="form-section">
      <h3>故事功能</h3>

      <div className="form-group">
        <label>角色类型</label>
        <select
          value={formData.storyRole.characterType}
          onChange={(e) => handleFieldChange('storyRole', 'characterType', e.target.value)}
        >
          <option value="protagonist">主角</option>
          <option value="antagonist">反角</option>
          <option value="supporting">配角</option>
          <option value="minor">次要角色</option>
        </select>
      </div>

      <div className="form-group">
        <label>角色弧光</label>
        <textarea
          value={formData.storyRole.characterArc}
          onChange={(e) => handleFieldChange('storyRole', 'characterArc', e.target.value)}
          placeholder="在故事中的成长变化轨迹"
          rows={3}
        />
      </div>

      <div className="form-group">
        <label>冲突作用</label>
        <textarea
          value={formData.storyRole.conflictRole}
          onChange={(e) => handleFieldChange('storyRole', 'conflictRole', e.target.value)}
          placeholder="在冲突中扮演的角色"
          rows={3}
        />
      </div>

      <div className="form-group">
        <label>象征意义</label>
        <textarea
          value={formData.storyRole.symbolism}
          onChange={(e) => handleFieldChange('storyRole', 'symbolism', e.target.value)}
          placeholder="角色代表的主题或象征"
          rows={3}
        />
      </div>

      <div className="form-group">
        <label>读者连接点</label>
        <textarea
          value={formData.storyRole.readerConnection}
          onChange={(e) => handleFieldChange('storyRole', 'readerConnection', e.target.value)}
          placeholder="与读者建立情感连接的要素"
          rows={3}
        />
      </div>
    </div>
  );

  const renderAppearance = () => (
    <div className="form-section">
      <h3>外貌特征</h3>
      <div className="form-grid">
        <div className="form-group">
          <label>身高</label>
          <input
            type="text"
            value={formData.appearance.height}
            onChange={(e) => handleFieldChange('appearance', 'height', e.target.value)}
            placeholder="例：175cm / 中等身高"
          />
        </div>

        <div className="form-group">
          <label>体重</label>
          <input
            type="text"
            value={formData.appearance.weight}
            onChange={(e) => handleFieldChange('appearance', 'weight', e.target.value)}
            placeholder="例：65kg / 偏瘦"
          />
        </div>

        <div className="form-group">
          <label>发色</label>
          <input
            type="text"
            value={formData.appearance.hairColor}
            onChange={(e) => handleFieldChange('appearance', 'hairColor', e.target.value)}
            placeholder="例：黑色 / 金棕色"
          />
        </div>

        <div className="form-group">
          <label>眼色</label>
          <input
            type="text"
            value={formData.appearance.eyeColor}
            onChange={(e) => handleFieldChange('appearance', 'eyeColor', e.target.value)}
            placeholder="例：深棕色 / 蓝色"
          />
        </div>

        <div className="form-group">
          <label>肤色</label>
          <input
            type="text"
            value={formData.appearance.skinTone}
            onChange={(e) => handleFieldChange('appearance', 'skinTone', e.target.value)}
            placeholder="例：小麦色 / 白皙"
          />
        </div>

        <div className="form-group">
          <label>体型</label>
          <select
            value={formData.appearance.bodyType}
            onChange={(e) => handleFieldChange('appearance', 'bodyType', e.target.value)}
          >
            <option value="">请选择</option>
            <option value="瘦削">瘦削</option>
            <option value="苗条">苗条</option>
            <option value="匀称">匀称</option>
            <option value="健壮">健壮</option>
            <option value="丰满">丰满</option>
            <option value="魁梧">魁梧</option>
          </select>
        </div>
      </div>

      <div className="form-group">
        <label>特殊标记</label>
        <div className="array-input">
          {formData.appearance.specialMarks.map((mark, index) => (
            <div key={index} className="array-item">
              <input
                type="text"
                value={mark}
                onChange={(e) => handleArrayFieldChange('appearance', 'specialMarks', index, e.target.value)}
                placeholder="例：左臂有疤痕 / 右手腕纹身"
              />
              <button
                type="button"
                onClick={() => removeArrayItem('appearance', 'specialMarks', index)}
                className="remove-btn"
              >
                ×
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={() => addArrayItem('appearance', 'specialMarks')}
            className="add-btn"
          >
            + 添加特殊标记
          </button>
        </div>
      </div>

      <div className="form-group">
        <label>着装风格</label>
        <textarea
          value={formData.appearance.clothingStyle}
          onChange={(e) => handleFieldChange('appearance', 'clothingStyle', e.target.value)}
          placeholder="描述角色的穿衣风格和偏好..."
          rows={3}
        />
      </div>
    </div>
  );

  const renderBackground = () => (
    <div className="form-section">
      <h3>背景故事</h3>
      <div className="form-grid">
        <div className="form-group">
          <label>出生地</label>
          <input
            type="text"
            value={formData.background.birthplace}
            onChange={(e) => handleFieldChange('background', 'birthplace', e.target.value)}
            placeholder="角色的出生地点"
          />
        </div>

        <div className="form-group">
          <label>教育背景</label>
          <input
            type="text"
            value={formData.background.education}
            onChange={(e) => handleFieldChange('background', 'education', e.target.value)}
            placeholder="受教育程度和经历"
          />
        </div>
      </div>

      <div className="form-group">
        <label>家庭背景</label>
        <textarea
          value={formData.background.family}
          onChange={(e) => handleFieldChange('background', 'family', e.target.value)}
          placeholder="描述家庭构成、关系和影响..."
          rows={3}
        />
      </div>

      <div className="form-group">
        <label>成长经历</label>
        <textarea
          value={formData.background.childhood}
          onChange={(e) => handleFieldChange('background', 'childhood', e.target.value)}
          placeholder="描述重要的成长阶段和经历..."
          rows={3}
        />
      </div>

      <div className="form-group">
        <label>重要事件</label>
        <div className="array-input">
          {formData.background.importantEvents.map((event, index) => (
            <div key={index} className="array-item">
              <input
                type="text"
                value={event}
                onChange={(e) => handleArrayFieldChange('background', 'importantEvents', index, e.target.value)}
                placeholder="描述塑造性格的关键事件"
              />
              <button
                type="button"
                onClick={() => removeArrayItem('background', 'importantEvents', index)}
                className="remove-btn"
              >
                ×
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={() => addArrayItem('background', 'importantEvents')}
            className="add-btn"
          >
            + 添加重要事件
          </button>
        </div>
      </div>

      <div className="form-group">
        <label>创伤经历</label>
        <div className="array-input">
          {formData.background.trauma.map((trauma, index) => (
            <div key={index} className="array-item">
              <input
                type="text"
                value={trauma}
                onChange={(e) => handleArrayFieldChange('background', 'trauma', index, e.target.value)}
                placeholder="负面或痛苦的经历"
              />
              <button
                type="button"
                onClick={() => removeArrayItem('background', 'trauma', index)}
                className="remove-btn"
              >
                ×
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={() => addArrayItem('background', 'trauma')}
            className="add-btn"
          >
            + 添加创伤经历
          </button>
        </div>
      </div>

      <div className="form-group">
        <label>成就</label>
        <div className="array-input">
          {formData.background.achievements.map((achievement, index) => (
            <div key={index} className="array-item">
              <input
                type="text"
                value={achievement}
                onChange={(e) => handleArrayFieldChange('background', 'achievements', index, e.target.value)}
                placeholder="重要的成就或里程碑"
              />
              <button
                type="button"
                onClick={() => removeArrayItem('background', 'achievements', index)}
                className="remove-btn"
              >
                ×
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={() => addArrayItem('background', 'achievements')}
            className="add-btn"
          >
            + 添加成就
          </button>
        </div>
      </div>
    </div>
  );

  const renderRelationships = () => (
    <div className="form-section">
      <h3>人际关系</h3>

      <div className="relationship-category">
        <h4>家人</h4>
        <div className="relationship-list">
          {formData.relationships.family.map((rel, index) => (
            <div key={index} className="relationship-item">
              <div className="relationship-fields">
                <input
                  type="text"
                  value={rel.name}
                  onChange={(e) => {
                    const newFamily = [...formData.relationships.family];
                    newFamily[index] = { ...rel, name: e.target.value };
                    handleFieldChange('relationships', 'family', newFamily);
                  }}
                  placeholder="姓名"
                />
                <input
                  type="text"
                  value={rel.relationship}
                  onChange={(e) => {
                    const newFamily = [...formData.relationships.family];
                    newFamily[index] = { ...rel, relationship: e.target.value };
                    handleFieldChange('relationships', 'family', newFamily);
                  }}
                  placeholder="关系（如：父亲、母亲）"
                />
                <select
                  value={rel.importance}
                  onChange={(e) => {
                    const newFamily = [...formData.relationships.family];
                    newFamily[index] = { ...rel, importance: e.target.value as 'high' | 'medium' | 'low' };
                    handleFieldChange('relationships', 'family', newFamily);
                  }}
                >
                  <option value="high">重要</option>
                  <option value="medium">一般</option>
                  <option value="low">不重要</option>
                </select>
                <button
                  type="button"
                  onClick={() => {
                    const newFamily = formData.relationships.family.filter((_, i) => i !== index);
                    handleFieldChange('relationships', 'family', newFamily);
                  }}
                  className="remove-btn"
                >
                  ×
                </button>
              </div>
              <textarea
                value={rel.description}
                onChange={(e) => {
                  const newFamily = [...formData.relationships.family];
                  newFamily[index] = { ...rel, description: e.target.value };
                  handleFieldChange('relationships', 'family', newFamily);
                }}
                placeholder="描述关系详情..."
                rows={2}
              />
            </div>
          ))}
          <button
            type="button"
            onClick={() => {
              const newRel = { name: '', relationship: '', description: '', importance: 'medium' as const };
              handleFieldChange('relationships', 'family', [...formData.relationships.family, newRel]);
            }}
            className="add-btn"
          >
            + 添加家人
          </button>
        </div>
      </div>

      <div className="relationship-category">
        <h4>朋友</h4>
        <div className="relationship-list">
          {formData.relationships.friends.map((rel, index) => (
            <div key={index} className="relationship-item">
              <div className="relationship-fields">
                <input
                  type="text"
                  value={rel.name}
                  onChange={(e) => {
                    const newFriends = [...formData.relationships.friends];
                    newFriends[index] = { ...rel, name: e.target.value };
                    handleFieldChange('relationships', 'friends', newFriends);
                  }}
                  placeholder="姓名"
                />
                <input
                  type="text"
                  value={rel.relationship}
                  onChange={(e) => {
                    const newFriends = [...formData.relationships.friends];
                    newFriends[index] = { ...rel, relationship: e.target.value };
                    handleFieldChange('relationships', 'friends', newFriends);
                  }}
                  placeholder="关系类型（如：挚友、同学）"
                />
                <select
                  value={rel.importance}
                  onChange={(e) => {
                    const newFriends = [...formData.relationships.friends];
                    newFriends[index] = { ...rel, importance: e.target.value as 'high' | 'medium' | 'low' };
                    handleFieldChange('relationships', 'friends', newFriends);
                  }}
                >
                  <option value="high">重要</option>
                  <option value="medium">一般</option>
                  <option value="low">不重要</option>
                </select>
                <button
                  type="button"
                  onClick={() => {
                    const newFriends = formData.relationships.friends.filter((_, i) => i !== index);
                    handleFieldChange('relationships', 'friends', newFriends);
                  }}
                  className="remove-btn"
                >
                  ×
                </button>
              </div>
              <textarea
                value={rel.description}
                onChange={(e) => {
                  const newFriends = [...formData.relationships.friends];
                  newFriends[index] = { ...rel, description: e.target.value };
                  handleFieldChange('relationships', 'friends', newFriends);
                }}
                placeholder="描述友谊详情..."
                rows={2}
              />
            </div>
          ))}
          <button
            type="button"
            onClick={() => {
              const newRel = { name: '', relationship: '', description: '', importance: 'medium' as const };
              handleFieldChange('relationships', 'friends', [...formData.relationships.friends, newRel]);
            }}
            className="add-btn"
          >
            + 添加朋友
          </button>
        </div>
      </div>

      <div className="form-group">
        <label>社交圈</label>
        <div className="array-input">
          {formData.relationships.socialCircle.map((circle, index) => (
            <div key={index} className="array-item">
              <input
                type="text"
                value={circle}
                onChange={(e) => handleArrayFieldChange('relationships', 'socialCircle', index, e.target.value)}
                placeholder="所属的社交群体"
              />
              <button
                type="button"
                onClick={() => removeArrayItem('relationships', 'socialCircle', index)}
                className="remove-btn"
              >
                ×
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={() => addArrayItem('relationships', 'socialCircle')}
            className="add-btn"
          >
            + 添加社交圈
          </button>
        </div>
      </div>
    </div>
  );

  const renderLifestyle = () => (
    <div className="form-section">
      <h3>生活状况</h3>
      <div className="form-grid">
        <div className="form-group">
          <label>居住地</label>
          <input
            type="text"
            value={formData.lifestyle.residence}
            onChange={(e) => handleFieldChange('lifestyle', 'residence', e.target.value)}
            placeholder="当前居住地点"
          />
        </div>

        <div className="form-group">
          <label>经济状况</label>
          <select
            value={formData.lifestyle.economicStatus}
            onChange={(e) => handleFieldChange('lifestyle', 'economicStatus', e.target.value)}
          >
            <option value="">请选择</option>
            <option value="贫困">贫困</option>
            <option value="温饱">温饱</option>
            <option value="小康">小康</option>
            <option value="富裕">富裕</option>
            <option value="豪富">豪富</option>
          </select>
        </div>
      </div>

      <div className="form-group">
        <label>日常习惯</label>
        <textarea
          value={formData.lifestyle.dailyRoutine}
          onChange={(e) => handleFieldChange('lifestyle', 'dailyRoutine', e.target.value)}
          placeholder="描述生活作息和日常习惯..."
          rows={3}
        />
      </div>

      <div className="form-group">
        <label>兴趣爱好</label>
        <div className="array-input">
          {formData.lifestyle.hobbies.map((hobby, index) => (
            <div key={index} className="array-item">
              <input
                type="text"
                value={hobby}
                onChange={(e) => handleArrayFieldChange('lifestyle', 'hobbies', index, e.target.value)}
                placeholder="个人兴趣和爱好"
              />
              <button
                type="button"
                onClick={() => removeArrayItem('lifestyle', 'hobbies', index)}
                className="remove-btn"
              >
                ×
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={() => addArrayItem('lifestyle', 'hobbies')}
            className="add-btn"
          >
            + 添加爱好
          </button>
        </div>
      </div>

      <div className="form-group">
        <label>饮食偏好</label>
        <div className="array-input">
          {formData.lifestyle.foodPreferences.map((food, index) => (
            <div key={index} className="array-item">
              <input
                type="text"
                value={food}
                onChange={(e) => handleArrayFieldChange('lifestyle', 'foodPreferences', index, e.target.value)}
                placeholder="喜欢或讨厌的食物"
              />
              <button
                type="button"
                onClick={() => removeArrayItem('lifestyle', 'foodPreferences', index)}
                className="remove-btn"
              >
                ×
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={() => addArrayItem('lifestyle', 'foodPreferences')}
            className="add-btn"
          >
            + 添加饮食偏好
          </button>
        </div>
      </div>

      <div className="form-group">
        <label>娱乐方式</label>
        <div className="array-input">
          {formData.lifestyle.entertainment.map((ent, index) => (
            <div key={index} className="array-item">
              <input
                type="text"
                value={ent}
                onChange={(e) => handleArrayFieldChange('lifestyle', 'entertainment', index, e.target.value)}
                placeholder="休闲娱乐活动"
              />
              <button
                type="button"
                onClick={() => removeArrayItem('lifestyle', 'entertainment', index)}
                className="remove-btn"
              >
                ×
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={() => addArrayItem('lifestyle', 'entertainment')}
            className="add-btn"
          >
            + 添加娱乐方式
          </button>
        </div>
      </div>
    </div>
  );

  const renderPsychology = () => (
    <div className="form-section">
      <h3>心理状态</h3>

      <div className="form-group">
        <label>心理健康</label>
        <select
          value={formData.psychology.mentalHealth}
          onChange={(e) => handleFieldChange('psychology', 'mentalHealth', e.target.value)}
        >
          <option value="">请选择</option>
          <option value="非常健康">非常健康</option>
          <option value="基本健康">基本健康</option>
          <option value="轻微问题">轻微问题</option>
          <option value="明显问题">明显问题</option>
          <option value="严重问题">严重问题</option>
        </select>
      </div>

      <div className="form-group">
        <label>应对机制</label>
        <div className="array-input">
          {formData.psychology.copingMechanisms.map((mechanism, index) => (
            <div key={index} className="array-item">
              <input
                type="text"
                value={mechanism}
                onChange={(e) => handleArrayFieldChange('psychology', 'copingMechanisms', index, e.target.value)}
                placeholder="处理压力的方式"
              />
              <button
                type="button"
                onClick={() => removeArrayItem('psychology', 'copingMechanisms', index)}
                className="remove-btn"
              >
                ×
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={() => addArrayItem('psychology', 'copingMechanisms')}
            className="add-btn"
          >
            + 添加应对机制
          </button>
        </div>
      </div>

      <div className="form-group">
        <label>情绪模式</label>
        <div className="array-input">
          {formData.psychology.emotionalPatterns.map((pattern, index) => (
            <div key={index} className="array-item">
              <input
                type="text"
                value={pattern}
                onChange={(e) => handleArrayFieldChange('psychology', 'emotionalPatterns', index, e.target.value)}
                placeholder="常见的情绪反应模式"
              />
              <button
                type="button"
                onClick={() => removeArrayItem('psychology', 'emotionalPatterns', index)}
                className="remove-btn"
              >
                ×
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={() => addArrayItem('psychology', 'emotionalPatterns')}
            className="add-btn"
          >
            + 添加情绪模式
          </button>
        </div>
      </div>

      <div className="form-group">
        <label>心理创伤</label>
        <div className="array-input">
          {formData.psychology.trauma.map((trauma, index) => (
            <div key={index} className="array-item">
              <input
                type="text"
                value={trauma}
                onChange={(e) => handleArrayFieldChange('psychology', 'trauma', index, e.target.value)}
                placeholder="未愈合的心理伤痛"
              />
              <button
                type="button"
                onClick={() => removeArrayItem('psychology', 'trauma', index)}
                className="remove-btn"
              >
                ×
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={() => addArrayItem('psychology', 'trauma')}
            className="add-btn"
          >
            + 添加心理创伤
          </button>
        </div>
      </div>

      <div className="form-group">
        <label>成长需求</label>
        <div className="array-input">
          {formData.psychology.growthNeeds.map((need, index) => (
            <div key={index} className="array-item">
              <input
                type="text"
                value={need}
                onChange={(e) => handleArrayFieldChange('psychology', 'growthNeeds', index, e.target.value)}
                placeholder="心理成长的需要"
              />
              <button
                type="button"
                onClick={() => removeArrayItem('psychology', 'growthNeeds', index)}
                className="remove-btn"
              >
                ×
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={() => addArrayItem('psychology', 'growthNeeds')}
            className="add-btn"
          >
            + 添加成长需求
          </button>
        </div>
      </div>
    </div>
  );

  const renderCurrentSection = () => {
    switch (currentSection) {
      case 'basicInfo':
        return renderBasicInfo();
      case 'appearance':
        return renderAppearance();
      case 'personality':
        return renderPersonality();
      case 'background':
        return renderBackground();
      case 'relationships':
        return renderRelationships();
      case 'lifestyle':
        return renderLifestyle();
      case 'psychology':
        return renderPsychology();
      case 'storyRole':
        return renderStoryRole();
      // 其他分类暂时显示占位符
      default:
        return <div>此部分正在开发中...</div>;
    }
  };

  return (
    <div className="character-form">
      <div className="form-header">
        <h2>{character ? '编辑角色' : '创建新角色'}</h2>
        {formData.basicInfo.name && (
          <span className="character-name">{formData.basicInfo.name}</span>
        )}
      </div>

      {errors.length > 0 && (
        <div className="error-messages">
          {errors.map((error, index) => (
            <div key={index} className="error-message">
              {error}
            </div>
          ))}
        </div>
      )}

      <div className="form-layout">
        <div className="form-nav">
          {SECTIONS.map(section => (
            <button
              key={section.key}
              className={`nav-item ${currentSection === section.key ? 'active' : ''}`}
              onClick={() => handleSectionChange(section.key)}
            >
              <span className="nav-icon">{section.icon}</span>
              <span className="nav-label">{section.label}</span>
            </button>
          ))}
        </div>

        <div className="form-content">
          {renderCurrentSection()}
        </div>
      </div>

      <div className="form-actions">
        <button onClick={onCancel} className="cancel-btn" disabled={isSaving}>
          取消
        </button>
        <button onClick={handleSave} className="save-btn" disabled={isSaving}>
          {isSaving ? '保存中...' : '保存'}
        </button>
      </div>
    </div>
  );
};