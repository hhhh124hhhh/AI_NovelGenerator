# download_nltk_data.py
# -*- coding: utf-8 -*-
"""
下载NLTK所需的数据包
"""

import nltk
import ssl
import sys
import os

def download_nltk_data():
    """下载NLTK所需的数据包"""
    try:
        # 尝试创建SSL上下文
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context
            
        print("开始下载NLTK数据包...")
        
        # 下载punkt数据包
        print("正在下载punkt数据包...")
        nltk.download('punkt', quiet=True)
        print("punkt数据包下载完成")
        
        # 下载punkt_tab数据包
        print("正在下载punkt_tab数据包...")
        nltk.download('punkt_tab', quiet=True)
        print("punkt_tab数据包下载完成")
        
        print("所有NLTK数据包下载完成！")
        return True
        
    except Exception as e:
        print(f"下载NLTK数据包时出错: {e}")
        return False

if __name__ == "__main__":
    success = download_nltk_data()
    if success:
        print("NLTK数据包下载成功！")
        sys.exit(0)
    else:
        print("NLTK数据包下载失败！")
        sys.exit(1)