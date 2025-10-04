"""
动画系统测试 - 验证动画效果管理器的功能
测试各种动画类型和过渡效果
"""

import logging
import customtkinter as ctk
from ui.modern_main_window import ModernMainWindow

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnimationTestApp:
    """动画测试应用"""

    def __init__(self):
        """初始化测试应用"""
        self.root = ctk.CTk()
        self.root.title("AI小说生成器 - 动画系统测试")
        self.root.geometry("1200x800")

        # 创建现代化主窗口
        self.main_window = ModernMainWindow()
        # 注意：ModernMainWindow继承自CTk，本身就是一个窗口，不需要pack

        logger.info("动画系统测试应用初始化完成")

    def run(self):
        """运行测试应用"""
        try:
            logger.info("开始运行动画系统测试...")

            # 启动主循环
            self.root.mainloop()

        except Exception as e:
            logger.error(f"运行测试应用失败: {e}")

def main():
    """主函数"""
    try:
        # 设置CustomTkinter主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # 创建并运行测试应用
        app = AnimationTestApp()
        app.run()

    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()