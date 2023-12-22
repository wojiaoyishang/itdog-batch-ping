import re
import json
import hashlib
import asyncio
import websockets
import requests


def itdog_batch_ping(host, node_id, callback, cidr_filter=True, gateway="last"):
    """
    爬取 itdog 测速网站，批量 Ping 服务器。

    :param host: 检测的IP地址，参考：域名或IPv4，每行一个，IP可填入范围和CIDR形式，可混合，最多支持256个检测目标 / 1万个字符。（传入列表，每一个项代表一行）
    :param node_id: 节点ID，使用“,”分隔。参考：1274,1226,1282,1150
    :param callback: 检测结果回调函数，回调函数应该提供一个参数，用于接收字典。参考字典：
                    {'ip': '检测的IP地址', 'result': '延迟', 'node_id': '节点ID', 'task_num': 99（任务数）, 'address': '解析到的服务器地理位置'}
    :param cidr_filter:  是否过滤CIDR格式中的网络地址、网关地址、广播地址，True 或 False，默认为 True
    :param gateway:  最后一个是网关地址（last，默认） 还是 第一个是网关地址（first）
    """
    if isinstance(host, str):
        host = [host]

    headers = {
        'Referer': 'https://www.itdog.cn/batch_ping/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    }

    data = {
        'host': "\r\n".join(host),  # 检测的IP
        'node_id': node_id,  # 节点ID，用“,”分割
        'cidr_filter': 'true' if cidr_filter else 'false',  # 过滤CIDR格式中的网络地址、网关地址、广播地址
        'gateway': gateway  # 最后一个是网关地址（last） 还是 第一个是网关地址（first）
    }

    response = requests.post('https://www.itdog.cn/batch_ping/', headers=headers, data=data)

    pattern = re.compile(r"""var wss_url='(.*)';""")
    wss_url = pattern.search(response.content.decode()).group(1)
    pattern = re.compile(r"""var task_id='(.*)';""")
    task_id = pattern.search(response.content.decode()).group(1)
    # print(wss_url, task_id + "token_20230313000136kwyktxb0tgspm00yo5")
    task_token = hashlib.md5((task_id + "token_20230313000136kwyktxb0tgspm00yo5").encode()).hexdigest()[8:-8]

    async def get_data():
        async with websockets.connect(wss_url) as websocket:

            await websocket.send(json.dumps({"task_id": task_id, "task_token": task_token}))
            # print(json.dumps({"task_id": task_id, "task_token": task_token}))

            message = {}
            while not ("type" in message and message['type'] == "finished"):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=0.5)
                    try:
                        message = json.loads(message)
                    except json.JSONDecodeError:
                        # print("服务器返回错误的信息：", message)
                        break
                    if not ("type" in message and message['type'] == "finished"):
                        callback(message)
                except asyncio.TimeoutError:
                    await websocket.send(json.dumps({"task_id": task_id, "task_token": task_token}))

            # print("服务器测速完成，等待断开连接。")
            await websocket.close()
            # get_data_loop.close()

    asyncio.run(get_data())


itdog_batch_ping(["1.0.0.0", "1.0.0.1"], "1274,1226,1282,1150", lambda x: print(x))
