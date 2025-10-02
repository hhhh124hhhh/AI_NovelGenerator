# 开发故事 #002: 主窗口现代化改造

## 故事信息
- **ID**: STORY-002
- **标题**: 主窗口现代化改造
- **Epic**: Epic 1 - 新用户引导体验 + Epic 3: 小说创作流程
- **优先级**: P0
- **估计工作量**: 8天
- **负责人**: 前端开发工程师 + UX设计师
- **状态**: 待开始

## 用户故事
**作为** AI小说生成器的用户
**我希望** 拥有一个现代化、直观的主界面
**以便** 我能够高效地进行小说创作和管理

## 验收标准

### 功能验收标准 (AC)
- [ ] **AC1**: 主窗口采用现代化设计语言，符合当前UI/UX标准
- [ ] **AC2**: 布局结构清晰，功能分区明确
- [ ] **AC3**: 提供直观的导航系统，用户可以快速访问常用功能
- [ ] **AC4**: 窗口支持自定义大小调整，布局能够自适应
- [ ] **AC5**: 提供状态栏显示实时信息和操作反馈

### 用户体验验收标准
- [ ] **UX1**: 新用户能在30秒内理解主界面布局
- [ ] **UX2**: 常用功能的点击次数不超过3次
- [ ] **UX3**: 界面元素视觉层次清晰，重要功能突出显示
- [ ] **UX4**: 提供操作提示和帮助信息
- [ ] **UX5**: 界面响应流畅，无明显卡顿

### 技术验收标准
- [ ] **TC1**: 窗口启动时间 < 2秒
- [ ] **TC2**: 界面渲染性能 < 16ms/帧
- [ ] **TC3**: 内存占用增长 < 50MB
- [ ] **TC4**: 支持1024x768以上的分辨率
- [ ] **TC5**: 与现有后端系统完全兼容

## 技术实现方案

### 1. 主窗口架构设计

#### 新主窗口结构
```
┌─────────────────────────────────────────────────────────────┐
│                      标题栏 (TitleBar)                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌───────────────────────────────────┐  │
│  │   侧边导航栏      │  │          主内容区域                │  │
│  │  (Sidebar)      │  │       (MainContent)              │  │
│  │                 │  │                                   │  │
│  │ • 快速操作       │  │  ┌─────────────────────────────┐  │  │
│  │ • 项目列表       │  │  │      标签页容器              │  │  │
│  │ • 最近使用       │  │  │    (TabView)               │  │  │
│  │ • 设置入口       │  │  │                             │  │  │
│  └─────────────────┘  │  │  ┌─────┐ ┌─────┐ ┌─────┐    │  │  │
│                       │  │  │Tab 1│ │Tab 2│ │Tab 3│    │  │  │
│                       │  │  └─────┘ └─────┘ └─────┘    │  │  │
│                       │  │  ┌─────────────────────────┐  │  │
│                       │  │  │      标签页内容          │  │  │
│                       │  │  │    (TabContent)        │  │  │
│                       │  │  └─────────────────────────┘  │  │
│                       │  └─────────────────────────────┘  │
│                       └───────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                      状态栏 (StatusBar)                      │
└─────────────────────────────────────────────────────────────┘
```

#### 主窗口类设计
```python
class ModernMainWindow(ctk.CTk):
    """现代化主窗口"""

    def __init__(self, theme_manager: ThemeManager, state_manager: StateManager):
        super().__init__()

        self.theme_manager = theme_manager
        self.state_manager = state_manager
        self.setup_window()
        self.create_components()
        self.setup_layout()
        self.bind_events()

    def setup_window(self):
        """设置窗口基本属性"""
        self.title("AI小说生成器 v2.0")
        self.geometry("1200x800")
        self.minsize(1024, 768)

        # 设置窗口图标和样式
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_components(self):
        """创建窗口组件"""
        self.title_bar = TitleBar(self, self.theme_manager)
        self.sidebar = ModernSidebar(self, self.theme_manager, self.state_manager)
        self.main_content = MainContentArea(self, self.theme_manager, self.state_manager)
        self.status_bar = ModernStatusBar(self, self.theme_manager)

    def setup_layout(self):
        """设置布局"""
        # 配置网格布局
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 放置组件
        self.title_bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=1, pady=1)
        self.sidebar.grid(row=1, column=0, sticky="nsew", padx=1, pady=1)
        self.main_content.grid(row=1, column=1, sticky="nsew", padx=1, pady=1)
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=1, pady=1)

    def bind_events(self):
        """绑定事件"""
        self.state_manager.subscribe('app', self.on_state_changed)
        self.bind('<Configure>', self.on_window_resize)

    def on_state_changed(self, state_changes):
        """状态变化回调"""
        if 'window_state' in state_changes:
            self.apply_window_state(state_changes['window_state'])

    def on_window_resize(self, event):
        """窗口大小变化事件"""
        # 处理响应式布局
        self.handle_responsive_layout(event.width, event.height)
```

### 2. 标题栏组件

#### 标题栏设计
```python
class TitleBar(ctk.CTkFrame):
    """现代化标题栏"""

    def __init__(self, parent, theme_manager: ThemeManager):
        super().__init__(parent, height=60)
        self.theme_manager = theme_manager

        self.setup_components()
        self.setup_layout()

    def setup_components(self):
        """设置标题栏组件"""
        # 应用标题
        self.title_label = ctk.CTkLabel(
            self,
            text="AI小说生成器",
            font=ctk.CTkFont(size=18, weight="bold")
        )

        # 版本信息
        self.version_label = ctk.CTkLabel(
            self,
            text="v2.0",
            font=ctk.CTkFont(size=12)
        )

        # 搜索框
        self.search_box = ModernSearchBox(self, self.theme_manager)

        # 用户区域
        self.user_area = UserArea(self, self.theme_manager)

        # 窗口控制按钮
        self.window_controls = WindowControls(self, self.theme_manager)

    def setup_layout(self):
        """设置标题栏布局"""
        self.grid_columnconfigure(1, weight=1)  # 搜索框区域可扩展

        # 左侧区域
        self.title_label.grid(row=0, column=0, sticky="w", padx=(20, 10), pady=15)
        self.version_label.grid(row=0, column=1, sticky="w", padx=(0, 20), pady=17)

        # 中间搜索区域
        self.search_box.grid(row=0, column=2, sticky="ew", padx=20, pady=12)

        # 右侧用户区域
        self.user_area.grid(row=0, column=3, sticky="e", padx=(0, 10), pady=12)
        self.window_controls.grid(row=0, column=4, sticky="e", padx=(0, 10), pady=12)
```

### 3. 侧边导航栏

#### 侧边栏设计
```python
class ModernSidebar(ctk.CTkFrame):
    """现代化侧边导航栏"""

    def __init__(self, parent, theme_manager: ThemeManager, state_manager: StateManager):
        super().__init__(parent, width=250)
        self.theme_manager = theme_manager
        self.state_manager = state_manager

        self.setup_components()
        self.setup_layout()
        self.load_navigation_items()

    def setup_components(self):
        """设置侧边栏组件"""
        # 快速操作区域
        self.quick_actions = QuickActionsSection(self, self.theme_manager)

        # 项目列表
        self.projects_section = ProjectsSection(self, self.theme_manager, self.state_manager)

        # 最近使用
        self.recent_section = RecentSection(self, self.theme_manager, self.state_manager)

        # 导航菜单
        self.navigation_menu = NavigationMenu(self, self.theme_manager)

        # 设置入口
        self.settings_entry = SettingsEntry(self, self.theme_manager)

    def setup_layout(self):
        """设置侧边栏布局"""
        # 配置滚动区域
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 在滚动框架中放置组件
        self.quick_actions.parent = self.scroll_frame
        self.projects_section.parent = self.scroll_frame
        self.recent_section.parent = self.scroll_frame
        self.navigation_menu.parent = self.scroll_frame
        self.settings_entry.parent = self.scroll_frame

    def load_navigation_items(self):
        """加载导航项目"""
        self.quick_actions.render()
        self.projects_section.render()
        self.recent_section.render()
        self.navigation_menu.render()
        self.settings_entry.render()
```

### 4. 主内容区域

#### 主内容区域设计
```python
class MainContentArea(ctk.CTkFrame):
    """主内容区域"""

    def __init__(self, parent, theme_manager: ThemeManager, state_manager: StateManager):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.state_manager = state_manager

        self.setup_components()
        self.setup_layout()

    def setup_components(self):
        """设置主内容区域组件"""
        # 面包屑导航
        self.breadcrumb = BreadcrumbNavigation(self, self.theme_manager)

        # 标签页容器
        self.tab_view = ModernTabView(self, self.theme_manager, self.state_manager)

        # 快速操作工具栏
        self.quick_toolbar = QuickToolbar(self, self.theme_manager)

    def setup_layout(self):
        """设置主内容区域布局"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 面包屑导航
        self.breadcrumb.grid(row=0, column=0, sticky="ew", padx=(20, 10), pady=(10, 5))

        # 标签页容器
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        # 快速工具栏
        self.quick_toolbar.grid(row=2, column=0, sticky="ew", padx=(20, 10), pady=(5, 10))
```

### 5. 现代化标签页

#### 标签页容器设计
```python
class ModernTabView(ctk.CTkFrame):
    """现代化标签页容器"""

    def __init__(self, parent, theme_manager: ThemeManager, state_manager: StateManager):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.state_manager = state_manager

        self.tabs = {}
        self.current_tab = None

        self.setup_components()
        self.setup_layout()
        self.create_default_tabs()

    def setup_components(self):
        """设置标签页组件"""
        # 标签页头部
        self.tab_header = TabHeader(self, self.theme_manager)

        # 标签页内容区域
        self.tab_content = TabContentArea(self, self.theme_manager)

    def setup_layout(self):
        """设置标签页布局"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.tab_header.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.tab_content.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    def create_default_tabs(self):
        """创建默认标签页"""
        # 创建各个功能标签页
        self.add_tab("config", "配置设置", ConfigTabContent(self.tab_content, self.theme_manager))
        self.add_tab("generation", "小说生成", GenerationTabContent(self.tab_content, self.theme_manager))
        self.add_tab("characters", "角色管理", CharacterTabContent(self.tab_content, self.theme_manager))
        self.add_tab("chapters", "章节编辑", ChapterTabContent(self.tab_content, self.theme_manager))
        self.add_tab("summary", "作品概览", SummaryTabContent(self.tab_content, self.theme_manager))

    def add_tab(self, tab_id: str, title: str, content_widget):
        """添加标签页"""
        self.tabs[tab_id] = {
            'title': title,
            'content': content_widget,
            'widget': None
        }

        # 创建标签按钮
        tab_button = self.tab_header.create_tab_button(tab_id, title, self.switch_tab)
        self.tabs[tab_id]['widget'] = tab_button

    def switch_tab(self, tab_id: str):
        """切换标签页"""
        if self.current_tab:
            # 隐藏当前标签页内容
            current_content = self.tabs[self.current_tab]['content']
            current_content.grid_forget()

        # 显示新标签页内容
        new_content = self.tabs[tab_id]['content']
        new_content.grid(row=0, column=0, sticky="nsew")

        # 更新标签按钮状态
        self.tab_header.update_tab_states(tab_id)

        self.current_tab = tab_id

        # 更新状态
        self.state_manager.update_state({'active_tab': tab_id})
```

### 6. 响应式布局系统

#### 响应式布局管理器
```python
class ResponsiveLayoutManager:
    """响应式布局管理器"""

    def __init__(self):
        self.breakpoints = {
            'mobile': 768,
            'tablet': 1024,
            'desktop': 1200,
            'large': 1600
        }
        self.current_layout = 'desktop'

    def update_layout(self, width: int, height: int, main_window):
        """更新布局"""
        new_layout = self._determine_layout(width)

        if new_layout != self.current_layout:
            self._apply_layout(new_layout, main_window)
            self.current_layout = new_layout

    def _determine_layout(self, width: int) -> str:
        """确定布局类型"""
        if width < self.breakpoints['mobile']:
            return 'mobile'
        elif width < self.breakpoints['tablet']:
            return 'tablet'
        elif width < self.breakpoints['desktop']:
            return 'desktop'
        else:
            return 'large'

    def _apply_layout(self, layout_type: str, main_window):
        """应用布局"""
        if layout_type == 'mobile':
            self._apply_mobile_layout(main_window)
        elif layout_type == 'tablet':
            self._apply_tablet_layout(main_window)
        elif layout_type == 'desktop':
            self._apply_desktop_layout(main_window)
        else:
            self._apply_large_layout(main_window)

    def _apply_mobile_layout(self, main_window):
        """应用移动端布局"""
        # 隐藏侧边栏，使用汉堡菜单
        main_window.sidebar.grid_forget()
        # 调整标签页布局
        main_window.tab_header.grid_forget()
        # 使用底部导航或其他移动端友好的导航方式

    def _apply_tablet_layout(self, main_window):
        """应用平板布局"""
        # 可折叠侧边栏
        main_window.sidebar.grid(row=1, column=0, sticky="nsew", padx=1, pady=1)
        # 调整组件大小和间距

    def _apply_desktop_layout(self, main_window):
        """应用桌面布局"""
        # 标准布局
        main_window.sidebar.grid(row=1, column=0, sticky="nsew", padx=1, pady=1)
        main_window.tab_header.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

    def _apply_large_layout(self, main_window):
        """应用大屏布局"""
        # 扩展布局，可能显示更多信息
        self._apply_desktop_layout(main_window)
```

## 实现步骤

### 第1-2天: 基础架构搭建
- [ ] 设计新主窗口架构
- [ ] 实现基础窗口类
- [ ] 创建组件基类
- [ ] 设置基础布局系统

### 第3天: 标题栏和侧边栏开发
- [ ] 实现现代化标题栏
- [ ] 开发侧边导航栏
- [ ] 创建快速操作组件
- [ ] 实现项目列表功能

### 第4天: 主内容区域开发
- [ ] 实现主内容区域布局
- [ ] 开发现代化标签页容器
- [ ] 创建面包屑导航
- [ ] 实现快速工具栏

### 第5天: 响应式布局系统
- [ ] 设计响应式断点
- [ ] 实现布局管理器
- [ ] 适配不同屏幕尺寸
- [ ] 测试布局切换效果

### 第6天: 标签页内容迁移
- [ ] 迁移配置标签页
- [ ] 迁移生成标签页
- [ ] 迁移角色和章节标签页
- [ ] 确保功能完整性

### 第7天: 交互和动画
- [ ] 添加过渡动画
- [ ] 实现拖拽调整
- [ ] 优化用户交互
- [ ] 完善键盘快捷键

### 第8天: 集成测试和优化
- [ ] 集成所有组件
- [ ] 性能优化
- [ ] 兼容性测试
- [ ] 用户体验调优

## 测试计划

### 单元测试
```python
class TestModernMainWindow(unittest.TestCase):
    def setUp(self):
        self.theme_manager = ThemeManager()
        self.state_manager = StateManager()
        self.main_window = ModernMainWindow(self.theme_manager, self.state_manager)

    def test_window_initialization(self):
        """测试窗口初始化"""
        self.assertIsNotNone(self.main_window.title_bar)
        self.assertIsNotNone(self.main_window.sidebar)
        self.assertIsNotNone(self.main_window.main_content)
        self.assertIsNotNone(self.main_window.status_bar)

    def test_responsive_layout(self):
        """测试响应式布局"""
        layout_manager = ResponsiveLayoutManager()
        layout_manager.update_layout(800, 600, self.main_window)
        # 验证布局是否正确调整
```

### 集成测试
- [ ] 主窗口组件正确集成
- [ ] 标签页切换功能正常
- [ ] 响应式布局正确工作
- [ ] 状态管理系统正常

### 用户体验测试
- [ ] 新用户引导流程测试
- [ ] 功能可用性测试
- [ ] 性能表现测试
- [ ] 视觉效果评估

## 风险评估

### 技术风险
**风险**: CustomTkinter布局限制可能影响设计实现
**影响**: 中等
**缓解措施**:
- 深入研究CustomTkinter布局系统
- 准备自定义布局方案
- 进行充分的原型测试

### 兼容性风险
**风险**: 新布局可能与现有功能不兼容
**影响**: 高
**缓解措施**:
- 渐进式迁移策略
- 完善的回退机制
- 充分的测试覆盖

### 性能风险
**风险**: 复杂布局可能影响性能
**影响**: 中等
**缓解措施**:
- 组件懒加载
- 布局缓存机制
- 性能监控和优化

## 依赖关系

### 前置依赖
- [x] STORY-001: 主题系统重构

### 后续依赖
- [ ] STORY-003: 配置界面现代化
- [ ] STORY-004: 生成流程优化
- [ ] STORY-005: 角色管理重构

## 验收检查清单

### 功能检查
- [ ] 主窗口正确显示和布局
- [ ] 所有导航功能正常工作
- [ ] 标签页切换流畅
- [ ] 响应式布局正确适配
- [ ] 与后端功能完全兼容

### 质量检查
- [ ] 代码质量符合标准
- [ ] 测试覆盖率达标
- [ ] 性能指标符合要求
- [ ] 用户体验测试通过

### 文档检查
- [ ] 组件API文档完整
- [ ] 使用指南提供
- [ ] 迁移文档准备
- [ ] 故障排除指南

---

**故事状态**: 待开始
**开始日期**: TBD
**预计完成**: TBD
**实际完成**: TBD
**开发人员**: TBD
**测试人员**: TBD
**UX设计师**: TBD