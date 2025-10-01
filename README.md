# 📖 自动小说生成工具

>- 当前没有什么精力维护该项目，本身该项目并无任何收益，以及临近毕业，有很多内容要忙，如果后面有时间的话，再考虑基于更新的技术去重构吧。——2025/9/24

<div align="center">
  
✨ **核心功能** ✨

| 功能模块          | 关键能力                          |
|-------------------|----------------------------------|
| 🎨 小说设定工坊    | 世界观架构 / 角色设定 / 剧情蓝图   |
| 📖 智能章节生成    | 多阶段生成保障剧情连贯性           |
| 🧠 状态追踪系统    | 角色发展轨迹 / 伏笔管理系统         |
| 🔍 语义检索引擎    | 基于向量的长程上下文一致性维护      |
| 📚 知识库集成      | 支持本地文档参考         |
| ✅ 自动审校机制    | 检测剧情矛盾与逻辑冲突          |
| 🖥 可视化工作台    | 全流程GUI操作，配置/生成/审校一体化 |

</div>

> 一款基于大语言模型的多功能小说生成器，助您高效创作逻辑严谨、设定统一的长篇故事

---

## 📑 目录导航
1. [环境准备](#-环境准备)  
2. [项目架构](#-项目架构)  
3. [配置指南](#⚙️-配置指南)  
4. [运行说明](#🚀-运行说明)  
5. [使用教程](#📘-使用教程)  
6. [疑难解答](#❓-疑难解答)  

---

## 🛠 环境准备
确保满足以下运行条件：
- **Python 3.11+** 运行环境（推荐3.11-3.12之间）
- **pip** 包管理工具 或 **uv** 包管理工具
- 有效API密钥：
  - 云端服务：OpenAI / DeepSeek / 智谱 / SiliconFlow 等
  - 本地服务：Ollama 等兼容 OpenAI 的接口

---

## 📥 安装说明
1. **下载项目**  
   - 通过 [GitHub](https://github.com) 下载项目 ZIP 文件，或使用以下命令克隆本项目：
     ```bash
     git clone https://github.com/YILING0013/AI_NovelGenerator
     ```

2. **安装编译工具（可选）**  
   - 如果对某些包无法正常安装，访问 [Visual Studio Build Tools](https://visualstudio.microsoft.com/zh-hans/visual-cpp-build-tools/) 下载并安装C++编译工具，用于构建部分模块包；
   - 安装时，默认只包含 MSBuild 工具，需手动勾选左上角列表栏中的 **C++ 桌面开发** 选项。

3. **配置环境变量**  
   - 复制 [.env.example](file://d:\AI_NovelGenerator\.env.example) 文件为 `.env`：
     ```bash
     cp .env.example .env
     ```
   - 编辑 `.env` 文件，填入您的API密钥和其他配置

4. **安装依赖并运行**  
   ### 使用 pip 安装（传统方式）
   - 打开终端，进入项目源文件目录：
     ```bash
     cd AI_NovelGenerator
     ```
   - 安装项目依赖：
     ```bash
     pip install -r requirements.txt
     ```
   - 安装完成后，运行主程序：
     ```bash
     python main.py
     ```

   ### 使用 uv 安装（推荐方式）
   - 确保已安装 [uv](https://github.com/astral-sh/uv) 包管理器
   - 打开终端，进入项目源文件目录：
     ```bash
     cd AI_NovelGenerator
     ```
   - 使用 uv 安装项目依赖（完整版）：
     ```bash
     uv pip install -r requirements-uv-full.txt
     ```
   - 或者使用精简版依赖（如果完整版安装遇到问题）：
     ```bash
     uv pip install -r requirements-uv.txt
     ```
   - 安装完成后，运行主程序：
     ```bash
     python main.py
     ```
     或者使用 uv 直接运行：
     ```bash
     uv run python main.py
     ```

>如果缺失部分依赖，后续**手动执行**
>```bash
>pip install XXX
>```
>进行安装即可

## 🗂 项目架构
```
novel-generator/
├── main.py                      # 入口文件, 运行 GUI
├── consistency_checker.py       # 一致性检查, 防止剧情冲突
|—— chapter_directory_parser.py  # 目录解析
|—— embedding_adapters.py        # Embedding 接口封装
|—— llm_adapters.py              # LLM 接口封装
├── prompt_definitions.py        # 定义 AI 提示词
├── utils.py                     # 常用工具函数, 文件操作
├── config_manager.py            # 管理配置 (API Key, Base URL)
├── config.json                  # 用户配置文件 (可选)
├── config.yaml                  # 用户配置文件 (推荐)
├── .env                         # 环境变量配置文件
├── novel_generator/             # 章节生成核心逻辑
├── ui/                          # 图形界面
└── vectorstore/                 # (可选) 本地向量数据库存储
```

---

## ⚙️ 配置指南
### 📌 基础配置（config.yaml）
项目支持JSON和YAML两种配置格式，推荐使用YAML格式，支持环境变量引用。

```yaml
# AI Novel Generator 配置文件
# 使用YAML格式，支持环境变量引用

# 最后使用的接口格式
last_interface_format: "OpenAI"
last_embedding_interface_format: "OpenAI"

# LLM模型配置
llm_configs:
  "DeepSeek V3":
    api_key: "${DEEPSEEK_API_KEY}"  # 从环境变量读取
    base_url: "https://api.deepseek.com/v1"
    model_name: "deepseek-chat"
    temperature: 0.7
    max_tokens: 8192
    timeout: 600
    interface_format: "OpenAI"
  
  "GPT 5":
    api_key: "${OPENAI_API_KEY}"  # 从环境变量读取
    base_url: "https://api.openai.com/v1"
    model_name: "gpt-5"
    temperature: 0.7
    max_tokens: 32768
    timeout: 600
    interface_format: "OpenAI"
  
  "智谱GLM-4.5":
    api_key: "${ZHIPUAI_API_KEY}"  # 从环境变量读取
    base_url: "https://open.bigmodel.cn/api/paas/v4"
    model_name: "glm-4.5-air"
    temperature: 0.7
    max_tokens: 8192
    timeout: 600
    interface_format: "智谱"
  
  "SiliconFlow Qwen3":
    api_key: "${SILICONFLOW_API_KEY}"  # 从环境变量读取
    base_url: "https://api.siliconflow.cn/v1"
    model_name: "Qwen/Qwen3-7B-Instruct"
    temperature: 0.7
    max_tokens: 8192
    timeout: 600
    interface_format: "SiliconFlow"

# Embedding模型配置
embedding_configs:
  "OpenAI":
    api_key: "${OPENAI_EMBEDDING_API_KEY}"  # 从环境变量读取
    base_url: "https://api.openai.com/v1"
    model_name: "text-embedding-ada-002"
    retrieval_k: 4
    interface_format: "OpenAI"
  "智谱":
    api_key: "${ZHIPUAI_API_KEY}"  # 从环境变量读取
    base_url: "https://open.bigmodel.cn/api/paas/v4"
    model_name: "embedding-2"
    retrieval_k: 4
    interface_format: "智谱"
  "SiliconFlow":
    api_key: "${SILICONFLOW_API_KEY}"  # 从环境变量读取
    base_url: "https://api.siliconflow.cn/v1"
    model_name: "BAAI/bge-m3"
    retrieval_k: 4
    interface_format: "SiliconFlow"

# 其他参数
other_params:
  topic: "星穹铁道主角星穿越到原神提瓦特大陆，拯救提瓦特大陆，并与其中的角色展开爱恨情仇的小说"
  genre: "玄幻"
  num_chapters: 120
  word_number: 4000
  filepath: "./novel_output"
```

### 🔧 配置说明
1. **生成模型配置**
   - `api_key`: 大模型服务的API密钥，推荐使用环境变量引用方式 `${API_KEY_NAME}`
   - `base_url`: API终端地址（本地服务填Ollama等地址）
   - `interface_format`: 接口模式
   - `model_name`: 主生成模型名称（如gpt-4, claude-3等）
   - `temperature`: 创意度参数（0-1，越高越有创造性）
   - `max_tokens`: 模型最大回复长度

### 🆕 新增支持的模型服务

#### SiliconFlow（硅基流动）
SiliconFlow是一个提供多种大模型API服务的平台，支持多种开源模型，包括Qwen系列等。

**配置示例：**
```yaml
# LLM配置
"SiliconFlow Qwen3":
  api_key: "${SILICONFLOW_API_KEY}"
  base_url: "https://api.siliconflow.cn/v1"
  model_name: "Qwen/Qwen3-7B-Instruct"
  temperature: 0.7
  max_tokens: 8192
  timeout: 600
  interface_format: "SiliconFlow"

# Embedding配置
"SiliconFlow":
  api_key: "${SILICONFLOW_API_KEY}"
  base_url: "https://api.siliconflow.cn/v1"
  model_name: "BAAI/bge-m3"
  retrieval_k: 4
  interface_format: "SiliconFlow"
```

**获取API密钥：**
1. 访问 [SiliconFlow官网](https://siliconflow.cn/)
2. 注册账号并登录
3. 在控制台获取API密钥
4. 将密钥添加到 `.env` 文件中的 `SILICONFLOW_API_KEY` 变量

**免费额度说明：**
SiliconFlow为新用户提供免费额度，可以满足基本的小说生成需求。

#### Gitee AI
Gitee AI提供了免费的向量模型服务。

**配置示例：**
```yaml
# Embedding配置
"Gitee AI":
  api_key: "${GITEE_AI_API_KEY}"
  base_url: "https://ai.gitee.com/v1"
  model_name: "bge-m3"
  retrieval_k: 4
  interface_format: "Gitee AI"
```

### 🎯 配置示例和推荐方案

为了帮助用户更好地使用本工具，我们提供了多种配置方案：

#### 方案一：高性价比方案（适合预算有限的用户）
- **大模型配置**: 使用DeepSeek作为主要模型，智谱GLM-4.5用于最终定稿
- **向量模型配置**: 使用SiliconFlow或Gitee AI的免费向量模型
- **适用场景**: 日常小说创作，对生成速度和成本有要求

#### 方案二：高质量方案（适合对质量要求较高的用户）
- **大模型配置**: 使用GPT-4或智谱GLM-4.5作为主要模型
- **向量模型配置**: 使用OpenAI或智谱的付费向量模型
- **适用场景**: 专业写作，出版级别的小说创作

#### 方案三：完全免费方案（适合测试使用）
- **大模型配置**: 使用Ollama在本地运行的开源模型
- **向量模型配置**: 使用Ollama本地向量模型
- **适用场景**: 学习和测试，无任何费用支出

### 📝 小说参数填写示例

#### 示例一：玄幻小说
```yaml
other_params:
  topic: "一个现代青年穿越到修仙世界，通过自己的智慧和努力最终成为一代仙帝的故事"
  genre: "玄幻"
  num_chapters: 120
  word_number: 4000
  filepath: "./novel_output/仙帝之路"
  user_guidance: "重点描写修炼过程中的奇遇和战斗场面，人物性格要鲜明，情节要有起伏"
  characters_involved: "主角李凡（现代青年）、师父青云子（仙门长老）、反派血魔宗宗主"
  key_items: "九转金丹（提升修为）、诛仙剑（神兵利器）、天机图（藏宝图）"
  scene_location: "青云山脉（修仙圣地）、血魔域（邪恶之地）、天界（最终目标）"
  time_constraint: "千年内必须突破到仙帝境界，否则将被天道惩罚"
```

#### 示例二：科幻小说
```yaml
other_params:
  topic: "人类在火星建立殖民地后，发现古老文明遗迹并揭开宇宙秘密的故事"
  genre: "科幻"
  num_chapters: 80
  word_number: 5000
  filepath: "./novel_output/火星遗迹"
  user_guidance: "注重科学细节和逻辑性，描写高科技设备和外星文明"
  characters_involved: "主角陈博士（考古学家）、AI助手ARIA、火星总督"
  key_items: "量子探测器、古代星图、能量核心"
  scene_location: "火星新北京城、古代遗迹区、地球总部"
  time_constraint: "太阳风暴将在30天内摧毁火星殖民地"
```

#### 示例三：都市小说
```yaml
other_params:
  topic: "年轻人创业失败后，通过直播带货重新站起来的励志故事"
  genre: "都市"
  num_chapters: 60
  word_number: 3000
  filepath: "./novel_output/直播人生"
  user_guidance: "贴近现实生活，描写商业竞争和人际关系"
  characters_involved: "主角张小明（创业者）、合伙人李娜、竞争对手王总"
  key_items: "手机直播设备、爆款产品、商业合同"
  scene_location: "创业园区、直播间、商业中心"
  time_constraint: "必须在三个月内还清债务，否则将失去所有"
```