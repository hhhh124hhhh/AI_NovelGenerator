import nltk
import os
import sys

# 设置NLTK数据下载路径为项目目录
nltk_data_path = os.path.join(os.path.dirname(__file__), 'nltk_data')
if not os.path.exists(nltk_data_path):
    os.makedirs(nltk_data_path)

if nltk_data_path not in nltk.data.path:
    nltk.data.path.insert(0, nltk_data_path)

print(f"NLTK数据路径: {nltk_data_path}")
print(f"NLTK搜索路径: {nltk.data.path}")

print("开始下载NLTK数据...")
try:
    # 下载punkt数据包
    print("下载punkt数据包...")
    nltk.download('punkt', download_dir=nltk_data_path)
    print("punkt数据包下载完成")
    
    # 下载punkt_tab数据包
    print("下载punkt_tab数据包...")
    nltk.download('punkt_tab', download_dir=nltk_data_path)
    print("punkt_tab数据包下载完成")
    
    print("NLTK数据下载完成！")
except Exception as e:
    print(f"下载过程中出现错误: {e}")
    sys.exit(1)