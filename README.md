# 基于BERT的对话意图和槽位联合识别模块

本仓库是intentslot这个项目在数梅派上的部署版本，所有的参数使用release版本训练得到，该版本添加了使用数梅派调用语音检测的模块，以及发送串口指令模块

## News

- Last update on Mar. 18, 2025

## 运行环境
- Python 3.12.8
- Pytorch 2.6.0
- Huggingface Transformers 4.49.0

直接创建环境
```angular2html
# 1. 先通过Conda创建环境
conda env create -f environment.yml

# 2. 激活环境
conda activate 环境名称

# 3. 安装Pip包（在已激活的环境中）
pip install -r requirements.txt
```

## 直接使用训练好的模型

在release_3.0.0中下载`bert-base-chinese.zip`和`result.zip`这两个文件并且解压到该项目的根目录，运行`python test.py '请打开二楼的灯'`，查看结果。


## 如何克隆树莓派镜像

在开发过程中，定期备份是一个好习惯，可以在出现意外情况时保证损失最小。

在Uubntu下，将树莓派的SD卡通过读卡器插入电脑，查看磁盘信息

```
(base) acc@acc-server:~$ sudo fdisk -l
Disk /dev/sda：29.72 GiB，31914983424 字节，62333952 个扇区
Disk model: SD Card Reader  
单元：扇区 / 1 * 512 = 512 字节
扇区大小(逻辑/物理)：512 字节 / 512 字节
I/O 大小(最小/最佳)：512 字节 / 512 字节
磁盘标签类型：dos
磁盘标识符：0xc35fc243

设备       启动    起点     末尾     扇区  大小 Id 类型
/dev/sda1          8192  1056767  1048576  512M  c W95 FAT32 (LBA)
/dev/sda2       1056768 62333951 61277184 29.2G 83 Linux
```

可以看到SD卡对应的设备是`/dev/sda`，通过下面的命令可以克隆SD卡到文件

```
(base) acc@acc-server:~$ sudo dd if=/dev/sda of=sd_backup1.img bs=4M status=progress conv=sync
276824064 字节 (277 MB, 264 MiB) 已复制，3 s，92.2 MB/s
```

通过如下命令将镜像恢复到SD卡

```
sudo dd if=sd_backup.img of=/dev/sda bs=4M status=progress conv=sync
```

## 参考

本项目地址
> https://github.com/dwgan/intentslot

参考
> https://github.com/Linear95/bert-intent-slot-detector
>
>  https://github.com/mzc421/NLP/tree/main/bert-intent-slot

