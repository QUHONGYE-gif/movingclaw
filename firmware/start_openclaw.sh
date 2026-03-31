#!/bin/bash

# 1. 显式声明路径，防止 systemd 找不到工具
export PATH="/home/pi/.npm-global/bin:/home/pi/miniconda3/bin:$PATH"

# 2. 初始化 Conda（针对 systemd 这种非交互式 Shell 是必须的）
source /home/pi/miniconda3/etc/profile.d/conda.sh

# 3. 激活你的虚拟环境
conda activate openclaw_env

# 4. 注入性能优化环境变量
export NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache
mkdir -p /var/tmp/openclaw-compile-cache
export OPENCLAW_NO_RESPAWN=1

# 5. 切换到工作目录
cd /home/pi/Moving-Claw

# 6. 使用绝对路径启动核心进程
exec /home/pi/.npm-global/bin/openclaw gateway --force