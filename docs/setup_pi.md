# 树莓派初步设置

## 1.购买内容：

- 树莓派5 8G
- HAT拓展版（容纳固态硬盘）
- 散热风扇
- 固态硬盘（由于openclaw读写量较大，使用固态硬盘）
- 原装充电器

**总价格在1500左右**

## 2.系统烧录与u盘启动

### 为什么使用Raspberry Pi Imager

1. 普通文件只能放置数据块，只有Raspberry Pi Imager会烧录引导程序去特定分区引导程序
2. 官方的配套严密，操作更简洁方便，且进行了校验，不易出错
3. 提供无头模式的预注入，可以直接将需要连接的wifi名称，密码（建议使用手机热点进行测试）直接烧录，避免后续网络连接的相关问题

> 注意，这里除了u盘启动之外的别的方法都可行，但是以我目前的流程举例

### 版本选择

**推荐选择**Raspberry Pi OS Lite (64-bit)（400MB左右），由于该版本没有桌面端，可以降低资源占用，发热，且更为流畅

### 相关配置：
1. **务必勾选exclude system drives（排除系统盘**避免格式化电脑
2. Configure wireless LAN：配置wifi，配置好手机热点名称和密码，如果有区域的选择的要求，一定选择目前的地区
3. Set locale settings：选择自己的区域
4. Keyboard layout：选择us布局，避免后续出现映射不一致等问题

### u盘启动

1. 提前插入u盘（因为树莓派启动的时候会自动寻找引导程序，在通电之后插入可能不会生效）
2. 插入电源，不用触碰开关，会自动从红灯转化成绿灯，然后闪烁一下，之后就保持长绿
3. 等待片刻，直到手机热点显示成功连接，就代表连接成功
4. 如果一直没有反应或者中途拔出，可以重新烧录u盘，流程同上，然后直接重新插入u盘进行树莓派的重新烧录

## 3.ssh接通与系统克隆

### ssh连接

- 由于我们使用的是u盘启动的方式，且将网络与密码烧录到了系统中，因此可以通过连接在同一网络的电脑进行ssh连接

代码如下（请自行替换成自己提前设置的名称与主机名）

```bash
ssh pi@moving-claw.local 
# ssh是安全外壳协议的缩写，其允许在没有显示器与键盘的情况下，由电脑通过局域网建立安全的加密渠道与树莓派连接

# pi是你在目标机器（movinf-claw）上的用户名，@代表“在”的含义，pi@... 的意思就是：“我要以 pi 这个用户的身份登录

# 后边的moving-claw就是主机名称，.local则是局域网协议，使得不必查找ip连接，而是直接在局域网内连接
```

### 检查数据分区

```bash
lsblk # List Block Devices，列出所有连接到主板的存储块设备
```

```bash
pi@moving-claw:~ $ lsblk
NAME    MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
loop0     7:0    0     2G  0 loop
sda       8:0    1 117.2G  0 disk
├─sda1    8:1    1   512M  0 part /boot/firmware
└─sda2    8:2    1 116.7G  0 part /
zram0   254:0    0     2G  0 disk [SWAP]
nvme0n1 259:0    0 238.5G  0 disk
```

- 这里的sda就是目前的u盘，挂载着 /boot/firmware（引导分区）和 /（系统根目录）。
- nvme0n1就是我们的固态，后续就需要将sda内部的系统克隆进来
- zram：虚拟内存，由系统在RAM中划分出来的区域，可以减少不常用的后台数据对内存的占用情况，减小OOM的可能
- loop0:在安装部分特殊的软件的时候，系统把文件视作硬盘来读取，可以无视

### 系统克隆

1. 软件与工具准备

    对于网络下载过慢的问题，可以使用[ssh隧道借用电脑vpn高速下载相关资源](#ssh隧道局域网共享代理)，或者采取电脑下载压缩包，[scp高速传输到树莓派](#scp传输)或者进行[清华源的替换（不推荐，有一些新的包清华源并没有更新，有条件尽量使用电脑vpn下载）](#清华源替换)

    

    ```bash
    sudo apt update && sudo apt install -y git # -y直接确认，不用后续手动确认
    ```

    - apt是树莓派系统（Debian系）的“应用商店”，可以更方便的管理软件和软件之间的依赖关系、软件卸载更新等内容，update是刷新应用商店的软件列表。因为系统是刚烧录的，如果不刷新，它就不知道去哪里下载最新版的软件。
    - git是版本控制工具，可以方便的进行不同版本代码的存档，合并，协作，也可以方便的拉取别人的代码，或者推送自己的代码到github上
2. 拉取克隆工具
    ```bash
    git clone https://github.com/geerlingguy/rpi-clone.git
    ```
    - git clone代表直接从该链接原封不动的克隆该链接下的内容
    - 该项目是一个树莓派热备份的项目，允许在不关机的前提下进行完整的备份与克隆，并且自动进行扩容与引导文件的修改，适合进行系统迁移与备份
3. 安装与授权
    ```bash
    cd rpi-clone # 进入下载的文件夹
    sudo cp rpi-clone rpi-clone-setup /usr/local/sbin
    ```
    - 将两个核心的脚本文件复制到[系统目录](Directory_Structure.md)中
4. 最终克隆安装
   ```bash
   sudo rpi-clone nvme0n1 #（替换成自己的固态名称）
   ```
   - 启动脚本进行克隆
   - 遇到询问的部分直接回车就可以

### 修改启动顺序
- 由于目前的启动顺序还是默认的优先sd卡和u盘，需要修改成优先ssd卡启动

1. 输入`sudo raspi-config` 
2. 用方向键选择 6 Advanced Options，回车。
3. 选择 A4 Boot Order，回车。
4. 选择 NVMe/USB Boot，回车。（如果显示EEPROM无法支持nvme，直接确认就好）
5. 最终确认，ok
6. 最后选 Finish
7. 输入`sudo poweroff`，然后拔出u盘，重启服务

## 4.tailscale连接配置
### 配置
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
sudo systemctl enable --now tailscaled
```
- curl -fsSL |sh: curl，一个下载工具。
    - -f: 报错时不输出错误 HTML 页面。
    - -s: 静默模式，不显示进度条。
    - -S: 如果出错，显示错误信息。
    - -L: 自动跟随重定向（如果服务器更换了链接地址）。
    - | sh: 管道符号。它把下载下来的脚本内容直接传递给 shell 执行。
- tailscale up：启动tailscale服务，会弹出一个链接，复制打开并与其他设备上注册的账号关联即可
- systemctl enable --now tailscaled：systemctl: Linux 系统服务管理工具。
  - enable: 设置服务为开机自启动
  - --now: 一个组合参数。它不仅设置开机自启，还会立即启动该服务。
  - tailscaled: 注意末尾多了一个 d，这代表 Daemon（守护进程）。
- 若想查看自己的tailscale的地址，输入`tailscale ip -4`
### 连接
1. 开启树莓派，确定能够连接互联网，同时开启另一台登陆了tailscale的设备（可在不同网络），
2. 输入`ssh pi@100.x.x.x`，将ip替换成树莓派的tailscale地址，可以在其他设备的networks-mydevices里查看，进行连接
[更多信息可以参考附录](#tailscale流程推荐)

## 5.总结
- 现在，你已经完成了最基础的树莓派的配置，应该可以对树莓派进行轻松的连接和高速网络下载，接下来就是[基础环境和环境管理软件的配置](setup_basic_environment.md)

## 网络链接附录
### ssh隧道（局域网共享代理）
- 本质原理是将电脑转换成一个无线网关，在树莓派发送请求的时候先通过电脑，再通过运营商网络进行连接，因此能够用到电脑上的vpn等工具
#### 普通流程
1. 打开代理软件，开启允许局域网连接（通常只监听 127.0.0.1（本地回环地址）。开启“允许局域网连接”后，软件会扩大监听范围，开始监听 PC 在局域网内的私有 IP）
2. 查看代理软件的端口号，如7890，7897，等并记录
3. 树莓派写下临时变量（仅当前终端生效）
```bash
export http_proxy=http://<你笔记本的局域网IP>:<你查到的端口号>
export https_proxy=http://<你笔记本的局域网IP>:<你查到的端口号>
```
#### tailscale流程（推荐）
前提：普通流程的1，2，并记录tailscale在另一个设备上的ip
- 这里的命令是对全局生效的命令，所有的流量都走另一个设备的节点，由另一个设备进行转发，传送
- 首先在电脑端设置：右键 Tailscale 图标 -> Exit Node -> Run as Exit Node
- 之后在tailscale的配置页面：https://login.tailscale.com/admin/machines 勾选设备右侧的 ... (三个点) -> 选择 Edit route settings -> 在弹出的窗口中，勾选 Use as exit node -> 点击 Save。
- 然后修改流量出口节点为另一台设备的tailscale的ip，同时加上exit-node-allow-lan-access，允许ssh保持连接而不中断
```bash
sudo tailscale up --exit-node=100.x.x.x --exit-node-allow-lan-access
```
- 如果重启之后有问题可以这样设置
```bash
sudo tailscale up --exit-node=100.x.x.x --exit-node-allow-lan-access --accept-routes --reset
```
- `curl ip.gs`测试，检查ip是否是另一台设备的出口ip

- 永久化配置：
```bash
nano ~/.bashrc # 打开环境配置文件
export http_proxy="http://<你电脑的IP>:7890"
export https_proxy="http://<你电脑的IP>:7890"
source ~/.bashrc #立刻生效
```
`Ctrl+O -> Enter -> Ctrl+X`

- 恢复：直接卸载出口节点
```bash
sudo tailscale up --exit-node=
```
##### **常见问题**
1. **magicdns配置问题**

    - **症状**：虽然前边的配置成功了，但是在实际使用的时候，仍然没有完全走的电脑的隧道流量，速度很慢
    - **原因**：由于树莓派的系统特殊性，其系统管理器默认使用路由器的dns，而tailscale的本质原理是通过magicdns修改dns地址，这两者之间发生dns冲突，导致解析延迟和连接到很远的服务器而不是通过隧道连接本地电脑作为流量出口
- 问题检查
```bash
 tailscale status
 ```
- 如果出现`Health check: overwritten`就代表存在这个问题
- 解决方案：https://tailscale.com/docs/reference/faq/dns-resolv-conf
  - 确保在处理之前隧道出口设备开启了`Allow Exit Node`
  - 使用**systemd-resolved**，由它进行统一的dns自动调度，更加现代化，避免冲突
    ```bash
    sudo apt update && sudo apt install systemd-resolved -y #下载安装
    sudo systemctl enable --now systemd-resolved #开机自启动
    sudo ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf #接管dns配置服务
    sudo tailscale up --exit-node=100.82.30.32 --exit-node-allow-lan-access --reset #启动tailscale并设置出口节点（替换成自己的tailscale出口的序号）
    ```
- 检查
  ```bash
  resolvectl status
  ```
  - 只要输出`resolv.conf mode: stub`，`Global` (全局)：出现了 `100.100.100.100 `和 `tail8b7421.ts.net`，`Link 3 (wlan0)`：识别到了你树莓派连接的 Wi-Fi 路由器 DNS，

### scp传输
- scp传输利用 SSH 加密通道进行设备之间的快速传输
- 基本语法结构`scp [选项] [源路径] [目标路径]`

如
```bash
# 格式：scp <本地文件路径> <用户名>@<主机名或IP>:<目标目录>
scp C:\Users\Downloads\Miniconda3.sh pi@moving-claw.local:/home/pi/
```

### 清华源替换
```bash
sudo sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list #核心软件仓库的替换
sudo sed -i 's|security.debian.org/debian-security|mirrors.tuna.tsinghua.edu.cn/debian-security|g' /etc/apt/sources.list #更新源的替换
sudo sed -i 's/archive.raspberrypi.com/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/raspi.sources #替换树莓派专用源 
sudo apt update #更新列表
```
- sed:Stream Editor 的缩写，用于过滤和转换文本，其流程是先读取相关文件->存放到临时空间内->处理修改->输出，其标准格式是`sed [选项] '动作' 文件名`
- -i: 意为 "in-place"（原地编辑），有了它，sed 会直接保存修改到文件里。
- 's/旧字符串/新字符串/g': 这是 sed 最常用的替换语法。
- s: 代表 substitute（替换）。
- /: 分隔符（也可以用其他符号，如命令 2 中用的是 |）。
- g: 代表 global（全局），即替换掉每一行中所有匹配到的内容
```bash
sudo sed -i 's|mirrors.tuna.tsinghua.edu.cn/debian-security|security.debian.org/debian-security|g' /etc/apt/sources.list
sudo sed -i 's/mirrors.tuna.tsinghua.edu.cn/deb.debian.org/g' /etc/apt/sources.list
sudo sed -i 's/mirrors.tuna.tsinghua.edu.cn/archive.raspberrypi.com/g' /etc/apt/sources.list.d/raspi.sources
```
- 如果出现了问题可以用这样的命令进行复原