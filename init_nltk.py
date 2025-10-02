import nltk
import os
import sys

def init_nltk():
    """初始化NLTK数据"""
    # 设置NLTK数据下载路径为用户目录
    user_nltk_path = os.path.expanduser('~/nltk_data')
    if not os.path.exists(user_nltk_path):
        os.makedirs(user_nltk_path)
    
    # 将用户目录添加到NLTK数据路径
    if user_nltk_path not in nltk.data.path:
        nltk.data.path.insert(0, user_nltk_path)
    
    print(f"NLTK数据路径: {user_nltk_path}")
    print(f"NLTK搜索路径: {nltk.data.path}")
    
    # 尝试查找数据包，如果找不到则下载
    try:
        nltk.data.find('tokenizers/punkt')
        print("punkt数据包已存在")
    except LookupError:
        print("下载punkt数据包...")
        try:
            nltk.download('punkt', download_dir=user_nltk_path)
            print("punkt数据包下载完成")
        except Exception as e:
            print(f"下载punkt数据包失败: {e}")
            return False
    
    try:
        nltk.data.find('tokenizers/punkt_tab')
        print("punkt_tab数据包已存在")
    except LookupError:
        print("下载punkt_tab数据包...")
        try:
            nltk.download('punkt_tab', download_dir=user_nltk_path)
            print("punkt_tab数据包下载完成")
        except Exception as e:
            print(f"下载punkt_tab数据包失败: {e}")
            # 这个不是致命错误，可以继续
            pass
    
    return True

if __name__ == "__main__":
    success = init_nltk()
    if success:
        print("NLTK初始化完成！")
        sys.exit(0)
    else:
        print("NLTK初始化失败！")
        sys.exit(1)