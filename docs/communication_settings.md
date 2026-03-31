# 通信架构与设置
## 主要通信方式
### mqtt协议
#### 简要介绍：
- mqtt采用**订阅-发布**的模型，主要流程中有四个部分组成：
    - Broker：通信的中央枢纽。负责高效地接收所有消息并进行精准分发。
    - Publisher：消息的发送方。它不需要建立与接收方的直接连接，只需将消息打上特定的“标签”发送给 Broker 即可。
    - Subscriber：消息的接收方。它提前向 Broker 登记自己感兴趣的“标签”。一旦 Broker 收到带有该标签的消息，就会瞬间推送给所有相应的订阅者。
    - Topic (主题/标签)：用于消息分类和路由的标识符。
  
#### 作用原理：系统里有一个总控台（Broker）。当某个设备（Publisher）在特定频道（Topic）上广播了一条指令，总控台会瞬间把这条指令转播给所有正在监听该频道的所有设备（Subscribers）。发送方发完即走，接收方根据设置进行响应，双方在空间和时间上完全解耦。
  
#### 为何使用mqtt：
  - 在这个项目中，系统被划分为负责复杂推理的“**大脑**”和负责执行的“**躯干**”。引入 MQTT为了精准解决物理机器人的核心痛点：

    - **快速反射控制**：当大脑规划出移动或抓取指令，或者按下键盘发出 forward 等指令时，控制信号必须**立刻传达**。MQTT 的**协议头部极小**，能够将包含动作类型、速度和时间戳的 JSON 指令，以极低的延迟通过 moving-claw/control 这一主题瞬间推送到树莓派。
  
    - 物理安全与急停机制：移动机器人在运行中发生断网的时候。通过 MQTT 极低开销的长连接特性，持续在 moving-claw/heartbeat 主题上发送和接收 ping 信号。一旦心跳监测逻辑发现超过 3 秒未收到回应（意味着网络波动或 PC 死机），树莓派将触发物理急停，防止机器人发生碰撞。

    - 网络容错：局域网或 Tailscale 的信号可能会抖动。Mosquitto Broker 的存在切断了 PC 与树莓派的硬连接。即便发生短暂丢包，指令也不会直接导致程序崩溃。

    - 架构分流：MQTT 剥离了这些重负载，而是专门用来跑轻量、高频的运动控制和底层硬件状态反馈。

### grpc协议
#### 简要介绍
- 它的目标是让系统中的不同计算机能够像调用本地函数一样，去调用另一台机器上的代码逻辑，并且完全屏蔽底层的网络通信细节，减少精力的花销。
#### 工作原理
- 它的核心主要基于两大基石：

  - Protocol Buffers 作为数据格式：只需在一个 .proto 文件中定义好数据结构和接口，编译器就会自动为生成底层代码。在传输时，数据会被压缩成极其紧凑的二进制流，体积更小，解析速度极快。

  - HTTP/2 作为传输载体：它天然支持双向流（双方都可以随时、独立地向对方发送一连串的消息，而不需要等待对方的回应）、多路复用（在一个连接上同时发送多个请求而不阻塞）以及极低的网络延迟。
#### 为何使用grpc
- 在项目中，树莓派 作为终端仅负责传感器采集与硬件控制，而复杂的视觉推理任务必须交由云端/边缘 PC 来处理。gRPC 成为了连接“眼睛”和“大脑”的最佳桥梁：

  - 支撑高带宽的视频传输：根据定义的 vision.proto，树莓派将视频信息等源源不断地发送给 PC。gRPC 的流式传输能力契合了这种需求，可以在一个持久连接上高效地推送连续的视频帧，而不会像普通 HTTP 那样每次都重新建立连接。

  - 跨越设备的算力调用：通过 gRPC 服务端核心的 VisionServicer，树莓派上的 Python 脚本只需调用 StreamVideo，就能直接触发 PC 端运算。

  - 强类型保障 AI 数据的对齐：AI 视觉模型返回的结果非常复杂，包含边界框的坐标、标签和置信度。通过grpc的各个模块和proto设置，确保了树莓派接收到的坐标数据是经过严格类型检查的杜绝了 JSON 解析时常见的类型错误和数据丢失。

  - 与 MQTT 的职责分离：gRPC 则被独立出来，专门负责视频流和目标检测这种“重负载、强结构”部分，保证系统拥有高带宽的视觉传输通道。
## 配置方案
### mqtt部分
#### 本地终端电脑配置（windows）
- windows本地笔记本需要作为brocker（服务器）来转发相关信息，和作为client（客户端）订阅树莓派发回来的报告（心跳信息）
- 具体流程
1. 使用winget快速安装[winget安装](#附录)
```powershell
winget install EclipseFoundation.Mosquitto
```
2. 开放默认端口，配置防火墙放行(**注意，必须要以管理员身份重新打开 PowerShell**)
```powershell
New-NetFirewallRule -DisplayName "MQTT" -Direction Inbound -LocalPort 1883 -Protocol TCP -Action Allow
```
   - `New-NetFirewallRule`：调用网络安全模块，创建一个新的防火墙规则。
   - `-DisplayName "MQTT"`：在“高级安全 Windows 防火墙”管理面板中显示的规则名称，方便后续查找和维护。
   - `-Direction Inbound`：这条规则适用于进入本机的流量（外部连入本机）
   - `-LocalPort 1883`：开放默认的1883端口
   - `-Protocol TCP`:采用mqtt默认的tcp协议
   - `-Action Allow`:设置为“允许”，即放行符合上述条件的流量  
3. 配置 Mosquitto 允许匿名与局域网访问（允许哪些设备连接）
```powershell
notepad "C:\Program Files\mosquitto\mosquitto.conf"
```
- 在打开的记事本文档的最末尾，新起几行，粘贴以下配置（暂时性设置，仅测试使用）：
```powershell
listener 1883
allow_anonymous true
```
- **永久化设置（推荐）**：
  1. 创建存储数据的文件夹
    ```powershell
    New-Item -Path "C:\mosquitto\data" -ItemType Directory -Force #替换成自己选择的文件夹路径
    ```
  2. 将完整配置写入 mosquitto.conf
   ```powershell
   notepad "C:\Program Files\mosquitto\mosquitto.conf"
   ```
   3. 在文件的最末尾，将内容修改或补充为以下完整的 5 行：
    ```powershell
    listener 1883
    allow_anonymous true    #允许匿名访问
    persistence true    # 开启数据持久化。
    persistence_location C:\mosquitto\data\ #替换成自己的路径，最后的反斜杠 \ 必不可少
    autosave_interval 1800  # 隔 1800 秒（30分钟）将内存中的数据自动存盘一次
    ```
4. 拉起相关服务
```powershell
Start-Service mosquitto
```
- 只要没有报错，就没有问题
#### 树莓派配置
1. 进入虚拟环境（openclaw_env）
2. 安装对应mqtt库
```bash
pip install paho-mqtt
```
#### 测试
1. 在电脑上创建虚拟环境并安装库
```powershell
conda create -n claw_brain python=3.10 -y
conda activate claw_brain
pip install paho-mqtt
```
2. 电脑上在对应文件夹创建[电脑测试文件](../test/pc_test.py)并运行
```powershell
python pc_test.py #每三秒发送一次测试信息
```
3. 树莓派上激活环境，创建[树莓派测试文件](../test/pi_test.py)(可使用nano，vim，或者vscode服务器等多种方式)并运行（务必将内部的100.X.X.X 替换为笔记本的真实 Tailscale IP）
```bash
python pi_test.py
```
4. 成功的表现：一旦树莓派运行，会在树莓派屏幕上看到瞬间接收指令并算出延迟（在几毫秒到几十毫秒之间），同时，笔记本屏幕上会立刻弹出 `[收到树莓派反馈] {"status": "success", "echo_seq": 1}！`
### grpc部分
#### 电脑端配置
1. 创建对应的[测试文件](../test/vision_server.py),这段代码会开启 50051 端口，接收树莓派发来的图像流，用 OpenCV 解码并弹出一个实时窗口，然后模拟返回识别结果
2. 进入虚拟环境装包
```powershell
pip install grpcio grpcio-tools opencv-python numpy
```
3. 创建[契约文件](../test/vision.proto)
4. 编译（确保路径正确）
```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. vision.proto
```
- `python -m grpc_tools.protoc`:调用 Python 中安装的 grpc_tools 包里的 protoc 编译器
- `-I.`：-I 等同于 --proto_path。指定编译器去哪里寻找 .proto 文件以及它们 import 的依赖文件。. 表示当前目录。
- `--python_out=.`：生成处理 Protocol Buffers 数据结构的 Python 文件。通常生成 vision_pb2.py
- `--grpc_python_out=.`：生成处理 gRPC 服务逻辑（客户端 Stub 和服务端接口）的 Python 文件。通常生成 vision_pb2_grpc.py
- `vision.proto`:源文件
5. 运行
```powershell
python vision_server.py
```
#### 树莓派配置
1. 进入 firmware 文件夹（激活 openclaw_env 环境），新建一个[测试文件](../test/vision_client.py)(注意替换ip)
2. 进入虚拟环境装包
```bash
pip install grpcio grpcio-tools opencv-python-headless numpy
```
3. 创建[契约文件](../test/vision.proto)
4. 编译(同上)
5. 运行
```bash
python vision_client.py
```
#### 结果
Windows 桌面上会弹出一个名为 "PC Vision Server" 的小窗口，里面有一块黑色的画面，绿色的 `Mock Frame: 0, 1, 2...` 数字在不断跳动

树莓派终端里，会不断收到 PC 发回来的 `👁️ [PC 大脑反馈] 看到: target_pen！`

## 附录
### winget配置
- 如果winget没有反应，可能由以下两个问题导致
#### 版本过旧、未安装
- 解决方案：
  - 从 Microsoft Store 更新：
    - 打开 Microsoft Store。
    - 搜索 “应用安装程序” (App Installer)。
    - 如果有“更新”按钮，点击更新；如果没有安装，点击安装。
    - 安装完成后，重启 PowerShell 或 命令提示符，再次输入 winget
#### 未写入环境变量
- 解决方案：
  - 按下 Win + R，输入 sysdm.cpl，回车。
  - 点击 高级 选项卡 -> 环境变量。
  - 在 用户变量 中找到 Path，双击打开。
  - 检查是否有以下路径：`%LocalAppData%\Microsoft\WindowsApps`
  - 如果没有，手动添加进去。
#### 如果输入 `winget --version` 能看到版本号，就说明你已经激活成功了！