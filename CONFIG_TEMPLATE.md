# AI小说生成器配置模板示例

本文档为用户提供配置AI小说生成器的详细指导，包括如何填写前端UI界面的各项参数。

## 1. 环境变量配置

首先，在项目根目录下创建 `.env` 文件，并填入相应的API密钥：

```env
# OpenAI API密钥（用于大模型和向量模型）
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# DeepSeek API密钥
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Gemini API密钥
GEMINI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 智谱AI API密钥
ZHIPUAI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Gitee AI API密钥
GITEE_AI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# SiliconFlow API密钥
SILICONFLOW_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Embedding API密钥（如果使用OpenAI的向量模型）
OPENAI_EMBEDDING_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 2. 大模型配置（LLM配置）

在"大模型设置"标签页中配置：

### 2.1 接口格式选择
- **OpenAI**: OpenAI官方接口格式
- **Azure OpenAI**: 微软Azure OpenAI服务
- **Ollama**: 本地运行的大模型
- **DeepSeek**: DeepSeek官方接口
- **Gemini**: Google Gemini接口
- **ML Studio**: LM Studio本地服务
- **智谱**: 智谱AI接口
- **SiliconFlow**: 硅基流动接口

### 2.2 常见配置示例

#### OpenAI配置
- **基础URL**: `https://api.openai.com/v1`
- **模型名称**: `gpt-4o-mini` 或 `gpt-4`

#### DeepSeek配置
- **基础URL**: `https://api.deepseek.com/v1`
- **模型名称**: `deepseek-chat`

#### 智谱配置
- **基础URL**: `https://open.bigmodel.cn/api/paas/v4`
- **模型名称**: `glm-4.5-air`

#### SiliconFlow配置
- **基础URL**: `https://api.siliconflow.cn/v1`
- **模型名称**: `Qwen/Qwen3-7B-Instruct`

#### Ollama本地配置
- **基础URL**: `http://localhost:11434/v1`
- **模型名称**: `llama3`

## 3. 向量模型配置（Embedding配置）

在"向量模型设置"标签页中配置：

### 3.1 接口格式选择
- **OpenAI**: OpenAI官方向量接口
- **Azure OpenAI**: 微软Azure OpenAI向量服务
- **Ollama**: 本地运行的向量模型
- **DeepSeek**: DeepSeek向量接口
- **Gemini**: Google Gemini向量接口
- **ML Studio**: LM Studio本地向量服务
- **SiliconFlow**: 硅基流动向量服务（免费）
- **智谱**: 智谱AI向量接口
- **Gitee AI**: Gitee AI向量接口（免费）

### 3.2 免费向量模型配置示例

#### Ollama配置（完全免费，本地运行）
- **基础URL**: `http://localhost:11434/api`
- **模型名称**: `nomic-embed-text`

#### SiliconFlow配置（免费在线服务）
- **基础URL**: `https://api.siliconflow.cn/v1/embeddings`
- **模型名称**: `BAAI/bge-m3`

#### Gitee AI配置（免费在线服务）
- **基础URL**: `https://ai.gitee.com/v1`
- **模型名称**: `bge-m3`

### 3.3 付费向量模型配置示例

#### OpenAI配置
- **基础URL**: `https://api.openai.com/v1`
- **模型名称**: `text-embedding-ada-002`

#### 智谱配置
- **基础URL**: `https://open.bigmodel.cn/api/paas/v4`
- **模型名称**: `embedding-2`

## 4. 模型选择配置

在"模型选择"标签页中，为不同步骤选择合适的模型：

### 4.1 推荐配置方案

#### 方案一：高性价比方案（适合预算有限的用户）
- **生成架构所用大模型**: DeepSeek（性价比高）
- **生成大目录所用大模型**: DeepSeek
- **生成草稿所用大模型**: DeepSeek
- **定稿章节所用大模型**: 智谱GLM-4.5（质量较好）
- **一致性审校所用大模型**: DeepSeek

#### 方案二：高质量方案（适合对质量要求较高的用户）
- **生成架构所用大模型**: GPT-4或GLM-4.5
- **生成大目录所用大模型**: GPT-4或GLM-4.5
- **生成草稿所用大模型**: DeepSeek（平衡成本）
- **定稿章节所用大模型**: GPT-4或GLM-4.5
- **一致性审校所用大模型**: DeepSeek

#### 方案三：完全免费方案（适合测试使用）
- **生成架构所用大模型**: Ollama本地模型
- **生成大目录所用大模型**: Ollama本地模型
- **生成草稿所用大模型**: Ollama本地模型
- **定稿章节所用大模型**: Ollama本地模型
- **一致性审校所用大模型**: Ollama本地模型

## 5. 小说参数配置

在"小说参数"标签页中填写小说的基本信息：

### 5.1 基本参数
- **主题**: 小说的核心主题
- **类型**: 小说类型（玄幻、科幻、都市等）
- **章节数**: 计划生成的章节数量
- **每章字数**: 每章的大致字数
- **保存路径**: 小说文件的保存位置
- **内容指导**: 对小说内容的具体要求
- **核心人物**: 小说中的主要角色
- **关键道具**: 小说中的重要物品
- **空间坐标**: 故事发生的主要地点
- **时间压力**: 故事中的时间限制或紧迫感

### 5.2 参数填写示例

#### 示例一：玄幻小说
- **主题**: 一个现代青年穿越到修仙世界，通过自己的智慧和努力最终成为一代仙帝的故事
- **类型**: 玄幻
- **章节数**: 120
- **每章字数**: 4000
- **保存路径**: ./novel_output/仙帝之路
- **内容指导**: 重点描写修炼过程中的奇遇和战斗场面，人物性格要鲜明，情节要有起伏
- **核心人物**: 主角李凡（现代青年）、师父青云子（仙门长老）、反派血魔宗宗主
- **关键道具**: 九转金丹（提升修为）、诛仙剑（神兵利器）、天机图（藏宝图）
- **空间坐标**: 青云山脉（修仙圣地）、血魔域（邪恶之地）、天界（最终目标）
- **时间压力**: 千年内必须突破到仙帝境界，否则将被天道惩罚

#### 示例二：科幻小说
- **主题**: 人类在火星建立殖民地后，发现古老文明遗迹并揭开宇宙秘密的故事
- **类型**: 科幻
- **章节数**: 80
- **每章字数**: 5000
- **保存路径**: ./novel_output/火星遗迹
- **内容指导**: 注重科学细节和逻辑性，描写高科技设备和外星文明
- **核心人物**: 主角陈博士（考古学家）、AI助手ARIA、火星总督
- **关键道具**: 量子探测器、古代星图、能量核心
- **空间坐标**: 火星新北京城、古代遗迹区、地球总部
- **时间压力**: 太阳风暴将在30天内摧毁火星殖民地

#### 示例三：都市小说
- **主题**: 年轻人创业失败后，通过直播带货重新站起来的励志故事
- **类型**: 都市
- **章节数**: 60
- **每章字数**: 3000
- **保存路径**: ./novel_output/直播人生
- **内容指导**: 贴近现实生活，描写商业竞争和人际关系
- **核心人物**: 主角张小明（创业者）、合伙人李娜、竞争对手王总
- **关键道具**: 手机直播设备、爆款产品、商业合同
- **空间坐标**: 创业园区、直播间、商业中心
- **时间压力**: 必须在三个月内还清债务，否则将失去所有

## 6. 使用建议

1. **免费选项**: 
   - 对于向量模型，推荐使用SiliconFlow或Gitee AI，它们提供免费额度
   - 对于大模型，可以使用Ollama在本地运行免费模型

2. **配置测试**:
   - 在填写完配置后，点击"测试配置"按钮验证配置是否正确
   - 确保API密钥正确且有足够额度

3. **模型选择**:
   - 根据不同步骤的需求选择合适的模型，平衡质量和成本

4. **保存配置**:
   - 配置完成后记得点击"保存"按钮，配置将持久化到文件中

通过以上配置，您就可以开始使用AI小说生成器创作您的小说了！