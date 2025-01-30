import time

from flask import Flask, jsonify, request
from GetIcp import ICP  # 假设 main.py 文件与你的 Flask app 在同一目录下

app = Flask(__name__)


def writelog(domain, result):
    the_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open('log.txt', 'a') as f:
        f.write(the_time + '  ' + domain + "  " + str(result["code"]) + '\n')


# 定义一个 GET 请求的接口，接收 domain 参数
@app.route('/geticp', methods=['GET'])
def get_icp():
    # 从查询参数中获取 domain，默认为 'qq.com'
    domain = request.args.get('domain', 'qq.com')
    # print(domain)
    start_time = time.time()
    # 创建 GetIcp 实例并调用 main 方法
    a = ICP()
    result = a.main(domain)
    writelog(domain, result)
    end_time = time.time()
    print("耗时：", end_time - start_time)

    # 返回结果为 JSON 格式
    return jsonify(result)


# if __name__ == '__main__':
#     app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8011)
