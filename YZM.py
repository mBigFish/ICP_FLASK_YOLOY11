import base64
import os
import shutil
import time
import cv2
import numpy as np
import onnxruntime


# 自定义进度条
def print_progress_bar(iteration, total, prefix='', length=100, fill='█'):
    """
    打印进度条
    :param iteration: 当前迭代次数
    :param total: 总迭代次数
    :param prefix: 前缀（显示进度信息）
    :param length: 进度条的长度
    :param fill: 进度条填充的字符
    """
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'{prefix} |{bar}| {percent}% 完成')


class Distinguish:
    def __init__(self):
        """
        初始化 ONNX 目标检测器
        - 加载 ONNX 模型
        - 设置类别名称、输入尺寸、置信度阈值等参数
        """
        self.result_list = None
        self.boxes_list = None
        self.small_original_image = None
        self.big_original_image = None
        self.big_img_path = None
        self.small_img_path = None
        self.class_names = ["text"]  # 检测类别名称
        self.input_size = (512, 512)  # 输入图像的尺寸
        self.conf_threshold = 0.8  # 置信度阈值
        self.nms_threshold = 0.7  # 非极大值抑制阈值
        self.colors = np.random.uniform(0, 255, size=(len(self.class_names), 3))  # 随机生成颜色以标识类别
        self.yolov11_moder = 'yolov11.onnx'  # ONNX 模型路径
        self.siamese_moder = 'siamese.onnx'  # Siamese网络模型
        self.yolov11_session = onnxruntime.InferenceSession(self.yolov11_moder)  # 加载 ONNX 模型
        self.siamese_session = onnxruntime.InferenceSession(self.siamese_moder)  # 加载Siamese网络模型
        self.Debug = False

    @staticmethod
    def image_to_ndarray(image_path):
        """
        将图片文件转换为 numpy.ndarray 格式
        :param image_path: 图片的文件路径
        :return: 转换后的 numpy.ndarray 图像数据
        """
        # 使用 OpenCV 读取图片
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        # 检查图片是否成功读取
        if img is None:
            raise ValueError(f"无法读取图片文件: {image_path}")
        return img

    @staticmethod
    def read_base64_image(base64_string):
        """
        将Base64编码的字符串转换为图像
        :param base64_string: Base64编码的图像字符串
        :return: 解码后的图像
        """
        # 解码Base64字符串为字节串
        img_data = base64.b64decode(base64_string)

        # 将解码后的字节串转换为numpy数组（OpenCV使用numpy作为其基础）
        np_array = np.frombuffer(img_data, np.uint8)

        # 使用OpenCV的imdecode函数将字节数据解析为cv::Mat对象
        img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        return img

    def preprocess_image(self, big_img, small_img):
        """
        预处理输入图像，使其适配模型输入要求
        :return: 预处理后的图像、原始图像和缩放比例
        """
        self.big_img_path = big_img
        self.small_img_path = small_img
        if self.Debug:
            self.big_original_image = self.image_to_ndarray(self.big_img_path)
            self.small_original_image = self.image_to_ndarray(self.small_img_path)

        else:
            self.big_original_image = self.read_base64_image(self.big_img_path)
            self.small_original_image = self.read_base64_image(self.small_img_path)

    def detect_objects(self):
        """
        执行目标检测
        :return: 检测结果列表
        """
        height, width, _ = self.big_original_image.shape  # 获取图像尺寸
        length = max(self.input_size)  # 获取最长边长度
        if height > length or width > length:
            self.big_original_image = cv2.resize(self.big_original_image, (512, 192))
            height, width, _ = self.big_original_image.shape  # 获取图像尺寸
        image = np.zeros((length, length, 3), np.uint8)  # 创建方形黑色背景
        image[0:height, 0:width] = self.big_original_image  # 将原图填充到方形图像中

        scale = length / self.input_size[0]  # 计算缩放比例
        blob = cv2.dnn.blobFromImage(image, scalefactor=1 / 255.0, size=self.input_size, swapRB=True)

        input_name = self.yolov11_session.get_inputs()[0].name  # 获取模型输入层名称
        outputs = self.yolov11_session.run(None, {input_name: blob})  # 运行模型推理
        outputs = np.array([cv2.transpose(outputs[0][0])])  # 转置输出数据

        rows = outputs.shape[1]  # 获取检测框数量
        boxes, scores, class_ids = [], [], []

        # 解析检测结果
        for i in range(rows):
            class_scores = outputs[0][i][4:]  # 获取所有类别的得分
            _, max_score, _, (x, max_class_idx) = cv2.minMaxLoc(class_scores)  # 获取最大类别得分
            if max_score >= self.conf_threshold:  # 如果得分高于阈值，则保存检测框
                box = [
                    int(outputs[0][i][0] - (0.5 * outputs[0][i][2])),  # 左上角 x
                    int(outputs[0][i][1] - (0.5 * outputs[0][i][3])),  # 左上角 y
                    int(outputs[0][i][2]),  # 宽度
                    int(outputs[0][i][3]),  # 高度
                ]
                boxes.append(box)
                scores.append(max_score)
                class_ids.append(max_class_idx)
        # 进行非极大值抑制（NMS）
        result_indices = cv2.dnn.NMSBoxes(boxes, scores, self.conf_threshold, self.nms_threshold)
        self.boxes_list = []
        if len(result_indices) > 0:
            for i in result_indices.flatten():
                box = boxes[i]
                detection = {
                    "class_id": class_ids[i],
                    "class_name": self.class_names[class_ids[i]],
                    "confidence": scores[i],
                    "box": [
                        round(box[0] * scale),
                        round(box[1] * scale),
                        round(box[2] * scale),
                        round(box[3] * scale),
                    ],
                }
                self.boxes_list.append(detection)

    def draw_boxes(self, sava_name='result.jpg'):
        """
        在图像上绘制检测结果
        :param image: 原始图像
        :param detections: 检测结果列表
        """
        for box in self.boxes_list:
            x1, y1, width, height = box["box"]
            class_id = box["class_id"]
            color = self.colors[class_id]  # 获取类别对应颜色
            label = f"{box['class_name']} ({box['confidence']:.2f})"  # 标签内容
            cv2.rectangle(self.big_original_image, (x1, y1), (x1 + width, y1 + height), color, 2)  # 绘制边界框
            cv2.putText(self.big_original_image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)  # 绘制类别标签
        cv2.imwrite(sava_name, self.big_original_image)
        # cv2.imshow("Detections", self.big_original_image)  # 显示结果
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()  # 关闭窗口

    def draw_result(self):
        for box in self.boxes_list:
            x1, y1, width, height = box["box"]
            class_id = box["class_id"]
            color = self.colors[class_id]  # 获取类别对应颜色
            cv2.rectangle(self.big_original_image, (x1, y1), (x1 + width, y1 + height), color, 2)  # 绘制边界框
        # 如果有匹配的结果，绘制匹配的顺序序号
        for idx, match in enumerate(self.result_list, start=1):  # 使用enumerate来获取序号，start=1表示从1开始
            x, y = match
            # 在匹配点附近显示序号
            cv2.putText(self.big_original_image, str(idx), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.imshow("Detections", self.big_original_image)  # 显示结果
        cv2.waitKey(0)
        cv2.destroyAllWindows()  # 关闭窗口

    def siamese(self):
        """
        使用Siamese网络进行目标比对，判断是否为同一个物体
        :param boxes: YOLO模型检测到的目标框，格式为 (x, y, width, height)
        :return: 比对结果列表，包含被判定为同一物体的目标框的左上角坐标 (x, y)
        """
        # 设置待检测区域在小图像上的 x 坐标位置，这些是预定义的关键区域
        positions = [165, 200, 231, 265]

        # 用于存储匹配成功的目标框坐标
        self.result_list = []

        # 遍历预定义的位置，提取小图像中的区域进行比对
        for x in positions:
            # 如果已找到4个匹配的目标，则提前结束循环
            if len(self.result_list) == 4:
                break

            # 截取小图像的指定区域（从坐标 (11, x) 开始，尺寸为 28x26）
            raw_image2 = self.small_original_image[11:11 + 28, x:x + 26]
            # 将图像从 BGR 转换为 RGB 格式（OpenCV 默认 BGR，而模型通常使用 RGB）
            img2 = cv2.cvtColor(raw_image2, cv2.COLOR_BGR2RGB)
            # 调整图像尺寸为 (105, 105)，适应 Siamese 网络的输入要求
            img2 = cv2.resize(img2, (105, 105))
            # 对小图像进行归一化处理，将像素值缩放到 [0,1] 范围，提升模型稳定性
            image_data_2 = np.array(img2) / 255.0
            # 调整图像的通道顺序，从 (H, W, C) 变为 (C, H, W)，符合深度学习框架的输入格式
            image_data_2 = np.transpose(image_data_2, (2, 0, 1))
            # 增加 batch 维度，变为 (1, 3, 105, 105)，以适应模型输入
            image_data_2 = np.expand_dims(image_data_2, axis=0).astype(np.float32)
            # 遍历检测到的目标框，与小图像进行比对
            for box in self.boxes_list:
                box = box["box"]
                # 提取大图像中的目标区域（根据检测框的坐标和尺寸裁剪）
                raw_image1 = self.big_original_image[box[1]:box[1] + box[3] + 2, box[0]:box[0] + box[2] + 2]
                # 将目标区域从 BGR 转换为 RGB 格式
                img1 = cv2.cvtColor(raw_image1, cv2.COLOR_BGR2RGB)
                # 调整图像大小为 (105, 105)，以匹配 Siamese 网络输入要求
                img1 = cv2.resize(img1, (105, 105))
                # 对目标区域进行归一化处理
                image_data_1 = np.array(img1) / 255.0
                # 调整通道顺序 (H, W, C) -> (C, H, W)
                image_data_1 = np.transpose(image_data_1, (2, 0, 1))
                # 增加 batch 维度，变为 (1, 3, 105, 105)
                image_data_1 = np.expand_dims(image_data_1, axis=0).astype(np.float32)
                # 准备输入数据，将小图和目标区域图像一起输入到 Siamese 网络
                inputs = {'input': image_data_1, "input.53": image_data_2}
                # 运行 Siamese 网络，进行图像相似度比对
                output = self.siamese_session.run(None, inputs)
                # 使用 Sigmoid 函数将网络输出转换为 0-1 之间的相似度分数
                output_sigmoid = 1 / (1 + np.exp(-output[0]))
                # 获取相似度分数（0 表示完全不同，1 表示完全相同）
                res = output_sigmoid[0][0]
                # 如果相似度分数大于阈值 0.7，则认为是同一物体，记录坐标
                if res >= 0.7:
                    self.result_list.append([box[0], box[1]])  # 记录检测框左上角坐标
                    break  # 跳出循环，避免重复记录同一目标

        # 返回最终匹配成功的检测框坐标列表
        return self.result_list

    def main(self, big_img, small_img):
        self.preprocess_image(big_img, small_img)
        self.detect_objects()  # 运行检测
        if len(self.boxes_list) >= 5:
            result = self.siamese()
            return result
        return False

# 使用示例
if __name__ == "__main__":
    big = 'img/big.jpg'
    small_img = 'img/small.jpg'
    start = time.time()

    dec = Distinguish()  # 创建检测器实例
    dec.main(big, small_img)

    end = time.time()
    print("耗时：", end - start)
    dec.draw_result()