import re

import requests
import urllib3
import json
import time
import hashlib
import base64
import ujson
import random
import os
from YZM import Distinguish
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ICP:
    def __init__(self):
        self.secretKey = None
        self.wordCount = None
        self.auth_data = None
        self.cookie = None
        self.distinguish = Distinguish()
        self.cookie_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32'}
        self.home = 'https://beian.miit.gov.cn/'
        self.url = 'https://hlwicpfwc.miit.gov.cn/icpproject_query/api/auth'
        # self.getCheckImage = 'https://hlwicpfwc.miit.gov.cn/icpproject_query/api/image/getCheckImage'
        self.getCheckImage = 'https://hlwicpfwc.miit.gov.cn/icpproject_query/api/image/getCheckImagePoint'
        self.checkImage = 'https://hlwicpfwc.miit.gov.cn/icpproject_query/api/image/checkImage'
        # 正常查询
        self.queryByCondition = 'https://hlwicpfwc.miit.gov.cn/icpproject_query/api/icpAbbreviateInfo/queryByCondition'
        # 违法违规域名查询
        self.blackqueryByCondition = 'https://hlwicpfwc.miit.gov.cn/icpproject_query/api/blackListDomain/queryByCondition'
        # 违法违规APP,小程序,快应用
        self.blackappAndMiniByCondition = 'https://hlwicpfwc.miit.gov.cn/icpproject_query/api/blackListDomain/queryByCondition_appAndMini'
        self.p_uuid = ''
        self.token = ''
        self.clientUid = ''
        self.clientUid_data = ''
        self.try_again = 5
        # self.exdir()
        self.DEBUG = False

    def debugprint(self, output):
        if self.DEBUG:
            print("DEBUG：" + str(output))

    @staticmethod
    def exdir():
        if not os.path.exists('./img'):
            os.mkdir('./img')
        if not os.path.exists('./img/big'):
            os.mkdir('./img/big')
        if not os.path.exists('./img/small'):
            os.mkdir('./img/small')

    def _init_session(self):
        """
           初始化一个同步的 requests 会话
           """
        self.session = requests.Session()
        self.session.trust_env = False  # 禁用从系统环境读取代理配置
        # 如果需要忽略 SSL 验证，可以加上 verify=False
        self.session.verify = False
        # 添加默认的 headers 或其他配置
        self.session.headers.update({
            "User-Agent": self.cookie_headers['User-Agent'],
        })

    def close_session(self):
        if self.session:
            self.session.close()

    def get_token(self):
        timeStamp = round(time.time() * 1000)
        authSecret = 'testtest' + str(timeStamp)
        authKey = hashlib.md5(authSecret.encode(encoding='UTF-8')).hexdigest()
        self.auth_data = {'authKey': authKey, 'timeStamp': timeStamp}
        self.cookie = self.get_cookie() # 没什么用
        self.base_header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32',
            'Origin': 'https://beian.miit.gov.cn',
            'Referer': 'https://beian.miit.gov.cn/',
            # 'Cookie': f'__jsluid_s={self.cookie}',
            'Accept': 'application/json, text/plain, */*'
        }
        try:
            with self.session.request(method="POST", url=self.url, data=self.auth_data, headers=self.base_header) as req:
                req = req.text
                t = ujson.loads(req)
                self.debugprint(t)
                return t['params']['bussiness']
        except Exception as e:
            return e

    def get_cookie(self):
        with self.session.request(method="GET", url=self.home, headers=self.cookie_headers) as req:
            self.debugprint(req.cookies)
            jsluid_s = re.compile('[0-9a-z]{32}').search(str(req.cookies))[0]

            return jsluid_s

    # 新增的UID加密生成算法
    def get_clientUid(self):
        characters = "0123456789abcdef"
        unique_id = ['0'] * 36

        for i in range(36):
            unique_id[i] = random.choice(characters)

        unique_id[14] = '4'
        unique_id[19] = characters[(3 & int(unique_id[19], 16)) | 8]
        unique_id[8] = unique_id[13] = unique_id[18] = unique_id[23] = "-"

        point_id = "point-" + ''.join(unique_id)

        return ujson.dumps({"clientUid": point_id})

    def get_img(self):
        length = str(len(str(self.clientUid_data).encode('utf-8')))
        self.base_header.update({'Content-Length': length, 'Token': self.token})
        self.base_header['Content-Type'] = 'application/json'
        with self.session.request(method="POST", url=self.getCheckImage, data=self.clientUid_data, headers=self.base_header) as req:
            response = req.json()
            self.debugprint(response)
            self.p_uuid = response['params']['uuid']
            big_image = response['params']['bigImage']
            small_image = response['params']['smallImage']
            self.secretKey = response['params']['secretKey']
            self.wordCount = response['params']['wordCount']

            # # 保存大图
            # with open(f"./img/big/a-{tid}-{str(i)}.jpg", "wb") as big_img_file:
            #     big_img_file.write(base64.b64decode(big_image))
            #
            # # 保存小图
            # with open(f"./img/small/a-{tid}-{str(i)}.jpg", "wb") as small_img_file:
            #     small_img_file.write(base64.b64decode(small_image))
            # print(f"已获取{str(i)}张验证码")
        return big_image, small_image

    def aes_ecb_encrypt(self, plaintext: bytes, key: bytes, block_size=16):
        backend = default_backend()
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=backend)

        padding_length = block_size - (len(plaintext) % block_size)
        plaintext_padded = plaintext + bytes([padding_length]) * padding_length

        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext_padded) + encryptor.finalize()

        return base64.b64encode(ciphertext).decode('utf-8')

    def generate_pointjson(self, big_img, small_img, secretKey):
        dis_result = self.distinguish.main(big_img, small_img)
        if dis_result:
            if len(dis_result) == 4:
                self.debugprint(dis_result)
            else:
                self.debugprint(f"验证码小图识别失败！ {dis_result}")
                return {"code": 103, "msg": "验证码小图识别失败"}
        else:
            self.debugprint(f"验证码大图识别失败！ {dis_result}")
            return {"code": 101, "msg": "验证码大图识别失败"}
        new_points = [[p[0] + 20, p[1] + 20] for p in dis_result]
        pointJson = [{"x": p[0], "y": p[1]} for p in new_points]
        self.debugprint(json.dumps(pointJson))
        enc_pointJson = self.aes_ecb_encrypt(json.dumps(pointJson).replace(" ", "").encode(), secretKey.encode())
        self.debugprint(enc_pointJson)
        return {"code": 200, "data": enc_pointJson}

    def check_img(self, big_image, small_image):
        # 识别验证码
        pointJson = self.generate_pointjson(big_image, small_image, self.secretKey)
        # 识别错误
        if not pointJson["code"] == 200:
            return pointJson
        pointJson = pointJson["data"]
        # 判断验证码
        data = ujson.loads(ujson.dumps({"token": self.p_uuid,
                                        "secretKey": self.secretKey,
                                        "clientUid": self.clientUid,
                                        "pointJson": pointJson}))
        length = str(len(str(data).encode('utf-8')))
        self.base_header.update({'Content-Length': length})
        with self.session.request(method="POST", url=self.checkImage, json=data, headers=self.base_header) as req:
            res = req.text
            data = ujson.loads(res)
            if not data["success"]:
                self.debugprint(f"验证码识别识别 {data}")
                return {"code": 104, "msg": "验证码识别失败"}
            sign = data["params"]["sign"]
            return {"code": 200, "data": sign}

    def get_beian(self, sign, domain):
        info = {'pageNum': '', 'pageSize': '', 'unitName': domain, "serviceType": 1}
        # 验证码识别成功，获取数据
        length = str(len(str(ujson.dumps(info, ensure_ascii=False)).encode('utf-8')))
        self.base_header.update({'Content-Length': length, 'Uuid': self.p_uuid, 'Token': self.token, 'Sign': sign})
        with self.session.request(method="POST", url=self.queryByCondition, data=ujson.dumps(info, ensure_ascii=False),
                                  headers=self.base_header) as req:
            res = req.text
            return ujson.loads(res)

    def main(self, domain):
        self._init_session()


        """新的开始"""
        # 获取验证码前的参数
        self.token = self.get_token()
        self.clientUid_data = self.get_clientUid()
        self.clientUid = ujson.loads(self.clientUid_data)["clientUid"]

        # 获取并且识别验证码
        big_image, small_image = self.get_img()
        sign = self.check_img(big_image, small_image)

        if sign["code"] != 200:
            print(sign)
            return sign
        sign = sign["data"]
        # 获取数据
        try:
            data = self.get_beian(sign, domain)
            print(data)
        except Exception as e:
            return {"code": 122, "msg": "查询失败", "result": str(e)}
        finally:
            self.close_session()
        if data['code'] == 500:
            return {"code": 123, "msg": "工信部服务器异常"}
        return data


if __name__ == '__main__':
    start = time.time()

    a = ICP()
    a.main("qq.com")

    end = time.time()
    print(end - start)

