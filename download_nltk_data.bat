@echo off
echo 正在下载NLTK数据包...
python download_nltk_data.py
if %errorlevel% == 0 (
    echo NLTK数据包下载完成！
) else (
    echo NLTK数据包下载失败！
)
pause