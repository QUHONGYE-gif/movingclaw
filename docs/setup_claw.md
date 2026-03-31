# openclaw设置与初始化
## 基础设置
### 设置原理
- `node.js`：由于openclaw本身主要由typescript写成（Javascript的超集），需要运行在`node.js`环境下，所以必须要安装该环境
- 由于我们的项目需求，我们的openclaw需要常驻，依赖 Linux 的底层的 systemd（系统服务）来保持后台常驻
    >systemed:核心初始化程序，是系统启动的时候启动的第一个服务，支持并行，按需启动等需求，进而实现开机自启动和重启
- 由于systemd 服务在开机自启或后台运行时，会去操作系统的全局环境变量路径（如 /usr/bin/node）中寻找可执行文件。如果把 Node.js 装在 Conda 的隔离环境里，系统服务找不到它，守护进程启动失败。因此，我们使用带有 exec 命令的 Wrapper 脚本进行启动
  > exec：exec会直接替换当前的进程，确保我们后续的指令能够直接作用到程序本身，而不需要通过最初的进程进行中转，也能直接传达控制指令，节省资源。

  > Wrapper脚本：Wrapper脚本是在exec之前提前进行布置和包装的程序，提前设置好相关的程序和路径等
### 具体流程
1. 安装
```bash
conda activate openclaw_env
curl -fsSL https://openclaw.ai/install.sh | bash #下载并直接使用安装脚本
openclaw onboard #初始激活
```
2. 初始配置：按照流程依次同意风险和安全指南，进行quickstart，其他的模型可以先选择暂时跳过或者不配置，后续跑通之后再进行修改
3. 创建Wrapper脚本
- 建议在`/home/pi/Moving-Claw/`创建相应文件[start_openclaw.sh](../firmware/start_openclaw.sh)（**替换相应路径**）
4. 赋予执行权限
```bash
chmod +x /home/pi/Moving-Claw/start_openclaw.sh
```
5. 配置systemd，在`/etc/systemd/system`[创建](../firmware/openclaw.service)
6. 重启并启动
```bash
sudo systemctl daemon-reload
sudo systemctl restart openclaw
sudo systemctl status openclaw
```
7. 检查：
```bash
journalctl -fu openclaw
```
## openclaw安装设置

1. 进行服务挂起和检查
```Bash
sudo systemctl daemon-reload #重载配置，确认该服务运行
sudo systemctl enable --now openclaw #允许该进程开机自启动
sudo systemctl status openclaw #查看当前状态
```
   - 如果是**绿色**的active (running)就代表成功
2. 出现问题的话检查日志
```bash
journalctl -u openclaw -n 20 --no-pager #查看出现的问题

which openclaw #查看实际的安装路径，记录下来该路径
```
将该路径修改到`start_openclaw.sh`里`exec /home/pi/.npm-global/bin/openclaw gateway --force`

3. 进行电脑访问测试（openclaw为了安全设置，默认只允许本地（127.0.0.1）访问）
  ```Bash
  openclaw dashboard --no-open #执行之后会输出一长串token=xxxx 的长 URL，复制`=`后边的内容作为密钥
  ``` 
  电脑端打开新的窗口，架设ssh隧道
  ```powershell
  ssh -L 18789:127.0.0.1:18789 pi@<100.82.30.32>#替换成树莓派的tailscale ip
  ```
4. 浏览器打开 http://127.0.0.1:18789，将密钥填入
5. 修改密码登陆（避免以后一直使用临时令牌）  
    
    - 进入设置中的security，找到 Control UI Password 这一项，输入你想要的登录密码。点击 Save。
6. 目前为了稳定性，暂时不配置尾网或者lan,可根据自己的需要进行修改

## 后续登陆配置
1. 打开拥有tailscale的设备
```bash
ssh -L 18789:127.0.0.1:18789 pi@<100.82.30.32>#替换成树莓派的tailscale ip
```
2. 登陆 http://127.0.0.1:18789
## 附录