# 基础环境和包管理工具设置
- 在进行项目的开发的时候，有两个核心的环境和包管理工具，docker，miniconda
- 也有一些通用工具需要进行安装
## Docker安装与配置
### Docker的必要性
- Docker作为容器，能够在进行包管理和虚拟环境管理的同时进行全部操作系统等内容的隔离，而且更适合处理有复杂依赖关系的ROS（机器人操作系统）
- Docker可以直接部署github上的许多开源项目，而不用担心任何关于环境依赖的相关问题
### 安装
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```
- 第一步通过curl获取docker的安装脚本，然后通过-o将该网页上的内容保存到get-docker.sh
- 第二部运行该sh文件，自动下载相关文件进行安装
```bash
sudo usermod -aG docker $USER # 有风险，根据自我需要执行
```
进行权限优化，将user加入docker组（组，即拥有的权限集），避免之后使用docker的时候填写sudo权限
- `usermod`：用户修改命令
- `-a`:追加，把用户添加到新的组，同时避免自己被踢出原有组
- `G`:指定要操作的组的名称
- `docker $USER`:将USER环境变量加入到docker组内

**加入之后需要重新登录系统**

## miniconda的安装与配置
### miniconda的必要性
- miniconda主要进行基础python，机器学习等环境的隔离和包管理，相比于docker更简单，快捷
- miniconda对于后续需要运行的openclaw也适合作为一个实验与调控平台
### 安装
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh
bash Miniconda3-latest-Linux-aarch64.sh
```
- 安装过程中有的时候需要输入yes，enter，一般来说默认yes就可以
```bash
conda config --add channels conda-forge
conda config --add channels bioconda
conda config --set channel_priority strict
```
- 添加一些新的下载渠道，conda-forge为Conda社区驱动渠道，包更广泛，bioconda有很多生物，ai相关包
- 最终设置渠道优先级设为**严格模式**，避免conda试图平衡不同版本的包的时候导致的环境冲突

在创建第一个环境并安装相应的包的时候可能会出现同意相关协议的要求，按照输出的信息处理就可以


## 通用工具安装
### 1.btop
- btop使我们得以用图形化方式看到磁盘读写、网络流量和每个核心的实时频率。
```bash
sudo apt install btop -y
```
输入`btop`运行，`q`退出
#### 基础控制
- m：切换显示模式（在统计图和精简视图间切换）。
- f：输入关键词搜索特定进程。
- ESC 或 m：打开主菜单（设置、帮助、退出）。
- q：直接退出程序。

#### 管理进程（右侧面板）
- 上/下方向键：选择进程。
- dd：强制杀死（Kill）选中的进程（非常常用）。
- Left/Right：更改进程的排序方式（按 CPU、按内存等）。

#### 界面自定义
- t：切换主题（btop 内置了非常多亮眼的主题）。
- 1 2 3 4：分别开启/关闭对应的面板（如按 4 隐藏网络面板）。
### 2.基础开发工具 
- 安装`build-essential`(基础编译包，包含gcc和g++)
- 安装`git`，作为版本控制工具和复制开源项目，上传项目的渠道中枢
- 安装`cmake`，方便构建大型项目，和`gdb`，方便进行代码的debug
```bash
sudo apt update
sudo apt install build-essential git cmake gdb -y
```