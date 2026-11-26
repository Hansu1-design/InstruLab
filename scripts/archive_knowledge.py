#!/usr/bin/env python
"""知识库阶段性归档脚本"""
import shutil, os, glob
from datetime import datetime

src = r'G:\Claudek\知识库\supervisor_kb'
ts = datetime.now().strftime('%Y%m%d_%H%M%S')
dst = rf'G:\Claudek\知识库\存档\snapshot_{ts}'

os.makedirs(dst, exist_ok=True)
os.makedirs(os.path.join(dst, '公开实盘研究'), exist_ok=True)

# 要归档的文件模式
patterns = ['精读-*.md', '碰撞-*.md', 'MOC-*.md', '苏淑靖-*.md']

count = 0
for pat in patterns:
    for f in glob.glob(os.path.join(src, pat)):
        shutil.copy2(f, dst)
        count += 1

# 公开实盘研究子目录
for f in glob.glob(os.path.join(src, '公开实盘研究', '*.md')):
    shutil.copy2(f, os.path.join(dst, '公开实盘研究'))
    count += 1

# 综合参考文档
for f in glob.glob(os.path.join(src, '*综合*.md')):
    shutil.copy2(f, dst)
    count += 1

print(f'[{datetime.now().strftime("%H:%M:%S")}] 归档完成: {count} 篇笔记')
print(f'  路径: {dst}')
print(f'  大小: {sum(os.path.getsize(os.path.join(dst,f)) for f in os.listdir(dst) if f.endswith(".md"))/1024:.0f} KB')
