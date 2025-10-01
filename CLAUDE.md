# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

AI_NovelGenerator 是一个基于大语言模型的中文小说生成工具，能够创作具有连贯世界观和角色发展的长篇故事。项目提供图形界面让用户配置设置、生成小说元素并管理创作过程。

## 开发命令

### 运行应用程序
- **标准 Python**: `python main.py`
- **使用 uv (推荐)**: `uv run python main.py`
- **Windows 批处理文件**: `run.bat`

### 包管理
- **使用 pip 安装**: `pip install -r requirements.txt`
- **使用 uv 完整安装**: `uv pip install -r requirements-uv-full.txt`
- **使用 uv 精简安装**: `uv pip install -r requirements-uv.txt`

### 测试和开发
- **测试安装**: `python test_uv_install.py`
- **创建可执行文件**: `pyinstaller main.spec`

## 核心架构

### 入口点和GUI
- `main.py`: 应用程序入口点，初始化GUI
- `ui/`: 使用customtkinter的GUI组件
  - `main_window.py`: 主GUI控制器
  - 各种功能标签页模块（配置、生成等）

### 小说生成流水线
`novel_generator/` 包包含核心生成逻辑：

1. **架构生成** (`architecture.py`): 创建世界观和设定
2. **蓝图创建** (`blueprint.py`): 生成章节大纲和结构
3. **章节生成** (`chapter.py`): 创建单个章节内容
4. **最终化** (`finalization.py`): 处理和定稿章节
5. **知识集成** (`knowledge.py`): 处理外部知识源
6. **向量存储工具** (`vectorstore_utils.py`): 管理语义搜索功能

### 关键支持组件
- `llm_adapters.py`: 不同LLM提供商的抽象层（OpenAI、DeepSeek、Ollama等）
- `embedding_adapters.py`: 处理语义搜索的嵌入模型
- `config_manager.py`: 配置管理，支持不同环境
- `consistency_checker.py`: 验证叙事一致性并检测矛盾
- `prompt_definitions.py`: 不同生成任务的集中提示词模板
- `utils.py`: 通用工具和文件操作

## 配置系统

应用程序使用 `config.json` 进行用户设置。主要配置部分：
- LLM API设置（密钥、基础URL、模型）
- 语义搜索的嵌入配置
- 小说参数（主题、类型、章节数、字数）
- 文件路径和输出位置

## 环境支持

项目支持传统pip环境和现代uv包管理：
- 通过 `is_uv_environment()` 自动检测uv环境
- 为不同安装场景提供多个requirements文件
- 兼容Python 3.9+（推荐3.10-3.12）

## 主要依赖
- **customtkinter**: 现代GUI框架
- **langchain**: LLM编排和提示管理
- **chromadb**: 语义搜索向量数据库
- **openai**: OpenAI API客户端
- **transformers**: Hugging Face模型集成
- **torch**: 本地模型支持的PyTorch

## 开发工作流

1. **设置配置**: 用户配置API密钥、模型设置和小说参数
2. **世界观构建**: 生成小说设定、角色和世界架构
3. **章节规划**: 创建带有标题和简要描述的章节目录
4. **内容生成**: 生成具有上下文感知的单个章节
5. **一致性检查**: 验证叙事连贯性和角色发展
6. **最终化**: 处理和定稿生成的内容

## 文件组织

生成的内容在用户指定目录中组织：
- `Novel_setting.txt`: 世界观构建和角色设定
- `Novel_directory.txt`: 章节大纲和结构
- `chapter_X.txt`: 单个章节内容
- `global_summary.txt`: 整体故事摘要
- `character_state.txt`: 角色发展跟踪
- `vectorstore/`: 语义搜索的本地向量数据库