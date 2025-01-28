import time

from flask import Flask, jsonify, request
from GetIcp import ICP  # 假设 main.py 文件与你的 Flask app 在同一目录下

app = Flask(__name__)

# 定义白名单
IP_WHITELIST = ['127.0.0.1', '192.168.1.100']  # 这里是允许访问的 IP 列表，你可以根据需求添加


def writelog(domain, result):
    the_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open('log.txt', 'a') as f:
        f.write(the_time + '  ' + domain + "  " + str(result["code"]) + '\n')

# 定义一个函数检查 IP 是否在白名单中
def check_ip():
    client_ip = request.remote_addr  # 获取请求客户端的 IP 地址
    if client_ip not in IP_WHITELIST:
        return False
    print(client_ip)
    return True


# 定义一个 GET 请求的接口，接收 domain 参数
@app.route('/geticp', methods=['GET'])
def get_icp():
    # 检查 IP 是否在白名单中
    if not check_ip():
        return jsonify({"code": 123, "msg": "工信部服务器异常"}), 403  # 403 Forbidden 错误

    # 从查询参数中获取 domain，默认为 'qq.com'
    domain = request.args.get('domain', 'qq.com')

    start_time = time.time()
    # 创建 GetIcp 实例并调用 main 方法
    a = ICP()
    result = a.main(domain)
    writelog(domain, result)
    end_time = time.time()
    print("耗时：", end_time - start_time)

    # 返回结果为 JSON 格式
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
