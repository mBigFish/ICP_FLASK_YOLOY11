

# ICP_FLASK_YOLOY11

## 1 简介

ICP_FLASK_YOLOY11是一个基于深度学习的目标检测和图像比对系统，结合了YOLOv11（YOLO系列目标检测）和Siamese网络（图像相似度比对）技术，开发的关于 ICP 域名查询的api接口。。该项目通过深度学习识别验证码，可以自完成验证码的绕过，从而查询域名是否已经进行 ICP 备案的功能。

## 2 使用方法

- 安装依赖

```
pip install -r requirements.txt
```

- 运行`API.py`即可

## 3 使用场景

- 适用于需要核实域名备案情况的互联网公司或个人。
- 可以集成到更复杂的业务系统中，作为域名备案查询的一部分。

## 4 参考：

- [Siamese-pytorch](https://github.com/bubbliiiing/Siamese-pytorch) 孪生神0经网络

- [ultralytics](https://github.com/ultralytics/ultralytics) YOLOv11

- [ICP-spider](https://github.com/ravizhan/ICP-spider) 