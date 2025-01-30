# ICP_FLASK_YOLOY11

## 1 简介

- ICP_FLASK_YOLOY11是一个基于深度学习的目标检测和图像比对系统，结合了YOLOv11（YOLO系列目标检测）和Siamese网络（图像相似度比对）技术，开发的关于 ICP 域名查询的api接口。。该项目通过深度学习识别验证码，可以自完成验证码的绕过，从而查询域名是否已经进行 ICP 备案的功能。
- 下载地址

```
bash
https://github.com/mBigFish/ICP_FLASK_YOLOY11
```

## 2 使用方法

- 安装依赖

```
plaintext
pip install -r requirements.txt
```

- 运行`API.py`即可开启api使用
- 或运行`GetIcp.py`即可单个网站查询

## 3 使用场景

- 适用于需要核实域名备案情况的互联网公司或个人。
- 可以集成到更复杂的业务系统中，作为域名备案查询的一部分。

## 4 使用截图

![image-20250130133125976](https://blog.mbigfish.com/images/%E3%80%90%E5%BC%80%E5%8F%91%E3%80%91%E7%88%AC%E8%99%AB%E4%B9%8BICP%E5%A4%87%E6%A1%88%E6%9F%A5%E8%AF%A2/image-20250130133125976.png)

![image-20250130133017966](https://blog.mbigfish.com/images/%E3%80%90%E5%BC%80%E5%8F%91%E3%80%91%E7%88%AC%E8%99%AB%E4%B9%8BICP%E5%A4%87%E6%A1%88%E6%9F%A5%E8%AF%A2/image-20250130133017966.png)

![image-20250130133047366](https://blog.mbigfish.com/images/%E3%80%90%E5%BC%80%E5%8F%91%E3%80%91%E7%88%AC%E8%99%AB%E4%B9%8BICP%E5%A4%87%E6%A1%88%E6%9F%A5%E8%AF%A2/image-20250130133047366.png)

## 5 参考：

- [Siamese-pytorch](https://github.com/bubbliiiing/Siamese-pytorch) 孪生神0经网络
- [ultralytics](https://github.com/ultralytics/ultralytics) YOLOv11
- [ICP-spider](https://github.com/ravizhan/ICP-spider)