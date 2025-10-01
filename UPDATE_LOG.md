# 项目更新日志

## v1.1.0 (2025-10-01)

### 新增功能
- 添加了对uv包管理器的完整支持
- 添加了YAML配置文件支持
- 添加了环境变量配置支持
- 添加了完整的中文GUI界面标签

### 改进内容

#### 1. 包管理改进
- 创建了完整的依赖文件：
  - `requirements-uv-full.txt` - 包含所有项目依赖的完整列表
  - `requirements-uv.txt` - 精简的核心依赖列表
- 创建了标准的`pyproject.toml`配置文件
- 生成了正确的`uv.lock`锁定文件
- 更新了README文档，添加了uv安装和使用说明

#### 2. 配置管理改进
- 添加了YAML格式配置文件支持 (`config.example.yaml`)
- 添加了环境变量配置支持 (`.env.example`)
- 更新了配置管理器以支持YAML和环境变量
- 配置文件现在支持`${VAR_NAME}`格式的环境变量引用

#### 3. GUI界面改进
- 创建了完整的中文标签配置文件 (`ui/chinese_labels.py`)
- 更新了所有UI模块以使用中文标签
- 改进了界面元素的布局和一致性
- 主窗口标题更改为"AI小说生成器"

#### 4. 文档改进
- 更新了README.md，添加了YAML配置和环境变量使用说明
- 创建了UV_USAGE.md，详细说明uv包管理器的使用
- 添加了配置文件示例和说明

### 文件列表
- 新增文件：
  - `pyproject.toml` - 项目配置文件
  - `requirements-uv-full.txt` - 完整uv依赖列表
  - `requirements-uv.txt` - 精简uv依赖列表
  - `config.example.yaml` - YAML配置文件示例
  - `.env.example` - 环境变量配置示例
  - `ui/chinese_labels.py` - 中文标签配置
  - `UV_USAGE.md` - uv使用说明
  - `UPDATE_LOG.md` - 更新日志

- 修改文件：
  - `README.md` - 添加uv和YAML配置说明
  - `config_manager.py` - 添加YAML和环境变量支持
  - `ui/main_window.py` - 添加中文标签支持
  - `ui/main_tab.py` - 添加中文标签支持
  - `ui/config_tab.py` - 添加中文标签支持
  - `ui/novel_params_tab.py` - 添加中文标签支持
  - `ui/setting_tab.py` - 添加中文标签支持
  - `ui/directory_tab.py` - 添加中文标签支持
  - `ui/character_tab.py` - 添加中文标签支持
  - `ui/summary_tab.py` - 添加中文标签支持
  - `ui/chapters_tab.py` - 添加中文标签支持
  - `ui/other_settings.py` - 添加中文标签支持

### 使用说明

#### 使用uv安装依赖
```bash
# 安装完整依赖（推荐）
uv pip install -r requirements-uv-full.txt

# 或安装精简依赖（网络环境较差时使用）
uv pip install -r requirements-uv.txt
```

#### 使用环境变量配置
1. 复制环境变量示例文件：
   ```bash
   cp .env.example .env
   ```
2. 编辑`.env`文件，填入您的API密钥和其他配置
3. 运行程序：
   ```bash
   uv run python main.py
   ```

#### 使用YAML配置文件
1. 复制YAML配置示例文件：
   ```bash
   cp config.example.yaml config.yaml
   ```
2. 编辑`config.yaml`文件，配置您的参数
3. 运行程序：
   ```bash
   uv run python main.py
   ```

### 注意事项
- 项目现在支持Python 3.11+版本
- 推荐使用uv包管理器进行依赖安装，速度更快
- 配置文件支持JSON和YAML两种格式
- 环境变量配置提供了更好的安全性
- GUI界面已完全中文化，用户体验更佳