# 使用 uv 管理 AI Novel Generator 项目

本文档说明如何使用 [uv](https://github.com/astral-sh/uv) 包管理器来安装和运行 AI Novel Generator 项目。

## 什么是 uv？

uv 是一个极快的 Python 包管理器和项目管理工具，由 Astral 开发。它可以用作 pip、pip-tools 和 virtualenv 的替代品，具有以下优势：

- 速度比 pip 快 10-100 倍
- 支持虚拟环境管理
- 兼容 pip 和 PyPI
- 单个二进制文件，易于安装

## 安装 uv

### Windows (推荐方式)

使用 PowerShell 安装：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

或者使用 pip 安装：

```bash
pip install uv
```

### macOS

使用 Homebrew 安装：

```bash
brew install uv
```

### Linux

使用 curl 安装：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 使用 uv 管理项目

### 1. 克隆项目

```bash
git clone https://github.com/YILING0013/AI_NovelGenerator
cd AI_NovelGenerator
```

### 2. 安装依赖

项目提供了三个依赖文件：

- `requirements.txt` - 完整的依赖列表（使用 pip 安装）
- `requirements-uv-full.txt` - 完整的依赖列表（使用 uv 安装，推荐）
- `requirements-uv.txt` - 精简的核心依赖列表（使用 uv 安装，适用于网络环境较差的情况）

使用 uv 安装完整依赖（推荐）：

```bash
uv pip install -r requirements-uv-full.txt
```

如果遇到网络问题或依赖冲突，可以使用精简版：

```bash
uv pip install -r requirements-uv.txt
```

### 3. 运行项目

使用 uv 运行项目：

```bash
uv run python main.py
```

或者直接运行：

```bash
python main.py
```

### 4. 创建虚拟环境（可选）

虽然 uv 不需要虚拟环境也能很好地管理依赖，但你仍然可以创建一个：

```bash
uv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖到虚拟环境
uv pip install -r requirements-uv-full.txt
```

## 项目结构

```
AI_NovelGenerator/
├── main.py                 # 主程序入口
├── pyproject.toml          # 项目配置文件
├── requirements.txt        # 完整依赖列表（pip 使用）
├── requirements-uv-full.txt # 完整依赖列表（uv 使用，推荐）
├── requirements-uv.txt     # 核心依赖列表（uv 使用）
├── uv.lock                 # uv 锁定文件
├── run.py                  # uv 启动脚本
├── run.bat                 # Windows 启动批处理脚本
├── UV_USAGE.md             # 本说明文档
├── README.md               # 项目说明
├── novel_generator/        # 核心生成模块
└── ui/                     # 图形界面模块
```

## 常见问题

### 1. 为什么提供多个依赖文件？

- `requirements.txt` - 项目原有的完整依赖列表，适用于使用 pip 安装
- `requirements-uv-full.txt` - 与 requirements.txt 相同的完整依赖列表，但格式适用于 uv 安装
- `requirements-uv.txt` - 精简的核心依赖列表，适用于网络环境较差或需要快速安装的场景

### 2. 如何更新依赖？

更新所有依赖：

```bash
uv pip install -r requirements-uv-full.txt --upgrade
```

### 3. 如何添加新依赖？

```bash
uv pip install package_name
```

然后更新 requirements-uv-full.txt 文件：

```bash
uv pip freeze > requirements-uv-full.txt
```

## 性能对比

uv 相比传统 pip 的优势：

| 操作 | pip | uv | 速度提升 |
|------|-----|-----|---------|
| 安装 requests | 2.3s | 0.1s | 23x |
| 安装 numpy | 25s | 2s | 12.5x |
| 安装大型项目 | 5分钟+ | 30秒 | 10x+ |

## 更多信息

- [uv 官方文档](https://docs.astral.sh/uv/)
- [uv GitHub 仓库](https://github.com/astral-sh/uv)