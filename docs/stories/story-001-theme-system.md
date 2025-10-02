# 开发故事 #001: 主题系统重构

## 故事信息
- **ID**: STORY-001
- **标题**: 主题系统重构
- **Epic**: Epic 1 - 新用户引导体验
- **优先级**: P0
- **估计工作量**: 5天
- **负责人**: 前端开发工程师
- **状态**: 待开始

## 用户故事
**作为** AI小说生成器的用户
**我希望** 能够在深色和浅色主题之间自由切换
**以便** 根据我的使用环境和个人偏好获得最佳视觉体验

## 验收标准

### 功能验收标准 (AC)
- [ ] **AC1**: 用户可以通过界面按钮一键切换深色/浅色主题
- [ ] **AC2**: 主题切换后所有界面元素立即更新，无需重启应用
- [ ] **AC3**: 应用会记住用户的主题选择，下次启动时自动应用
- [ ] **AC4**: 深色主题符合现代暗色模式设计标准，保护用户视力
- [ ] **AC5**: 浅色主题清新明快，适合白天使用环境

### 技术验收标准
- [ ] **TC1**: 主题切换响应时间 < 200ms
- [ ] **TC2**: 主题配置文件结构清晰，易于扩展新主题
- [ ] **TC3**: 主题切换不影响应用性能和内存使用
- [ ] **TC4**: 主题系统与现有组件系统完全兼容

## 技术实现方案

### 1. 主题管理器架构

#### 核心类设计
```python
class ThemeManager:
    """主题管理器 - 单例模式"""

    def __init__(self):
        self._current_theme = 'dark'
        self._themes = {}
        self._observers = []
        self._config_path = 'config/themes.json'

    def register_theme(self, name: str, theme_config: dict) -> bool:
        """注册新主题"""

    def apply_theme(self, theme_name: str) -> bool:
        """应用指定主题"""

    def get_current_theme(self) -> str:
        """获取当前主题名称"""

    def get_theme_style(self, component: str, state: str = 'normal') -> dict:
        """获取组件样式"""

    def toggle_theme(self) -> str:
        """切换主题 (深色<->浅色)"""

    def save_preference(self, theme_name: str) -> None:
        """保存用户主题偏好"""
```

#### 主题配置结构
```json
{
  "themes": {
    "dark": {
      "name": "深色主题",
      "colors": {
        "primary": "#0078D4",
        "secondary": "#6C757D",
        "background": "#1E1E1E",
        "surface": "#252526",
        "text": "#CCCCCC",
        "text_secondary": "#969696",
        "border": "#3E3E42",
        "success": "#107C10",
        "warning": "#FF8C00",
        "error": "#D13438"
      },
      "typography": {
        "font_family": "Microsoft YaHei UI",
        "font_size": {
          "xs": 10,
          "sm": 12,
          "md": 14,
          "lg": 16,
          "xl": 18,
          "xxl": 24
        },
        "line_height": 1.5
      },
      "spacing": {
        "xs": 2,
        "sm": 4,
        "md": 8,
        "lg": 16,
        "xl": 24,
        "xxl": 32
      },
      "shadows": {
        "sm": "0 1px 2px rgba(0,0,0,0.3)",
        "md": "0 4px 6px rgba(0,0,0,0.3)",
        "lg": "0 10px 15px rgba(0,0,0,0.3)"
      }
    },
    "light": {
      "name": "浅色主题",
      "colors": {
        "primary": "#0078D4",
        "secondary": "#6C757D",
        "background": "#FFFFFF",
        "surface": "#F8F9FA",
        "text": "#212529",
        "text_secondary": "#6C757D",
        "border": "#DEE2E6",
        "success": "#28A745",
        "warning": "#FFC107",
        "error": "#DC3545"
      }
    }
  }
}
```

### 2. 组件样式系统

#### 基础样式接口
```python
class StyledComponent:
    """样式化组件基类"""

    def __init__(self, theme_manager: ThemeManager):
        self.theme_manager = theme_manager
        self.theme_manager.subscribe(self.on_theme_changed)

    def on_theme_changed(self, new_theme: str) -> None:
        """主题变化回调"""
        self.apply_styles()

    def apply_styles(self) -> None:
        """应用当前主题样式"""
        theme = self.theme_manager.get_current_theme()
        styles = self.theme_manager.get_theme_style(self.__class__.__name__)
        self._apply_styles_to_widget(styles)

    def _apply_styles_to_widget(self, styles: dict) -> None:
        """将样式应用到具体组件"""
        raise NotImplementedError
```

#### 样式应用工具
```python
class StyleUtils:
    """样式工具类"""

    @staticmethod
    def apply_color(widget, color_name: str, color_value: str):
        """应用颜色样式"""
        if hasattr(widget, 'configure'):
            if color_name in ['fg', 'foreground']:
                widget.configure(fg=color_value)
            elif color_name in ['bg', 'background']:
                widget.configure(bg=color_value)

    @staticmethod
    def apply_font(widget, font_config: dict):
        """应用字体样式"""
        font = (
            font_config.get('family', 'Arial'),
            font_config.get('size', 12),
            font_config.get('weight', 'normal')
        )
        widget.configure(font=font)

    @staticmethod
    def apply_spacing(widget, spacing_config: dict):
        """应用间距样式"""
        if hasattr(widget, 'configure'):
            widget.configure(padx=spacing_config.get('x', 0),
                           pady=spacing_config.get('y', 0))
```

### 3. 主题切换UI组件

#### 主题切换按钮
```python
class ThemeToggleButton(ctk.CTkButton):
    """主题切换按钮"""

    def __init__(self, parent, theme_manager: ThemeManager):
        self.theme_manager = theme_manager
        self.current_theme = theme_manager.get_current_theme()

        super().__init__(
            parent,
            text=self._get_button_text(),
            command=self._toggle_theme,
            width=40,
            height=40
        )

        self._update_icon()
        self.theme_manager.subscribe(self._on_theme_changed)

    def _toggle_theme(self):
        """切换主题"""
        new_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.theme_manager.apply_theme(new_theme)

    def _on_theme_changed(self, theme_name: str):
        """主题变化回调"""
        self.current_theme = theme_name
        self._update_button_text()
        self._update_icon()

    def _get_button_text(self) -> str:
        """获取按钮文本"""
        return "🌙" if self.current_theme == 'light' else "☀️"

    def _update_icon(self):
        """更新图标"""
        self.configure(text=self._get_button_text())
```

### 4. 配置持久化

#### 主题配置管理
```python
class ThemeConfig:
    """主题配置管理"""

    def __init__(self, config_file: str = 'config/theme_config.json'):
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """加载配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'preferred_theme': 'dark', 'auto_switch': False}

    def save_preference(self, theme_name: str):
        """保存主题偏好"""
        self.config['preferred_theme'] = theme_name
        self._save_config()

    def get_preference(self) -> str:
        """获取主题偏好"""
        return self.config.get('preferred_theme', 'dark')

    def _save_config(self):
        """保存配置"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
```

## 实现步骤

### 第1天: 基础架构搭建
- [ ] 创建ThemeManager核心类
- [ ] 设计主题配置数据结构
- [ ] 实现主题注册和加载机制
- [ ] 创建基础配置文件

### 第2天: 样式系统开发
- [ ] 实现StyledComponent基类
- [ ] 开发StyleUtils工具类
- [ ] 创建样式应用机制
- [ ] 设计组件样式接口

### 第3天: 深色主题实现
- [ ] 设计深色主题配色方案
- [ ] 实现深色主题样式配置
- [ ] 应用到核心组件
- [ ] 测试深色主题效果

### 第4天: 浅色主题和切换功能
- [ ] 设计浅色主题配色方案
- [ ] 实现浅色主题样式配置
- [ ] 开发主题切换按钮组件
- [ ] 实现主题切换逻辑

### 第5天: 集成测试和优化
- [ ] 集成主题系统到主应用
- [ ] 实现配置持久化
- [ ] 性能优化和测试
- [ ] 用户体验微调

## 测试计划

### 单元测试
```python
class TestThemeManager(unittest.TestCase):
    def setUp(self):
        self.theme_manager = ThemeManager()

    def test_theme_registration(self):
        """测试主题注册功能"""
        result = self.theme_manager.register_theme('test', {})
        self.assertTrue(result)

    def test_theme_switching(self):
        """测试主题切换功能"""
        initial = self.theme_manager.get_current_theme()
        new_theme = self.theme_manager.toggle_theme()
        self.assertNotEqual(initial, new_theme)

    def test_style_retrieval(self):
        """测试样式获取功能"""
        style = self.theme_manager.get_theme_style('button')
        self.assertIsInstance(style, dict)
```

### 集成测试
- [ ] 主题切换不影响应用功能
- [ ] 所有组件正确响应主题变化
- [ ] 配置保存和加载正常
- [ ] 性能表现符合要求

### 用户体验测试
- [ ] 主题切换流畅性测试
- [ ] 视觉效果评估
- [ ] 不同场景下的可用性测试
- [ ] 用户反馈收集

## 风险评估

### 技术风险
**风险**: CustomTkinter的主题限制可能影响样式自定义
**影响**: 中等
**缓解措施**:
- 深入研究CustomTkinter的主题API
- 准备备用方案（如自定义绘制）
- 与CustomTkinter社区保持沟通

### 用户体验风险
**风险**: 主题切换可能造成视觉闪烁
**影响**: 低
**缓解措施**:
- 实现平滑过渡动画
- 优化样式更新逻辑
- 预加载主题资源

### 性能风险
**风险**: 主题系统可能增加内存占用
**影响**: 低
**缓解措施**:
- 实现主题资源缓存
- 优化样式计算逻辑
- 监控内存使用情况

## 依赖关系

### 前置依赖
- [ ] STORY-000: 基础组件架构搭建

### 后续依赖
- [ ] STORY-002: 导航栏现代化改造
- [ ] STORY-003: 主界面布局优化
- [ ] STORY-004: 配置界面重构

## 验收检查清单

### 功能检查
- [ ] 深色主题正确应用
- [ ] 浅色主题正确应用
- [ ] 主题切换按钮功能正常
- [ ] 主题偏好正确保存和加载
- [ ] 所有界面元素响应主题变化

### 质量检查
- [ ] 代码符合项目规范
- [ ] 单元测试覆盖率 > 90%
- [ ] 集成测试通过
- [ ] 性能测试通过
- [ ] 用户体验测试通过

### 文档检查
- [ ] API文档完整
- [ ] 使用示例提供
- [ ] 配置说明清晰
- [ ] 故障排除指南

---

**故事状态**: 待开始
**开始日期**: TBD
**预计完成**: TBD
**实际完成**: TBD
**开发人员**: TBD
**测试人员**: TBD