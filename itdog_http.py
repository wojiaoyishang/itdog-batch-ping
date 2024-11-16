import re
import json
import base64
import hashlib
import asyncio
import requests
import websockets

from urllib.parse import urlparse

session = requests.Session()


def x(input_str, key):
    output = ""
    key = key + "PTNo2n3Ev5"
    for i, char in enumerate(input_str):
        char_code = ord(char) ^ ord(key[i % len(key)])
        output += chr(char_code)
    return output


def set_ret(_0x132031):
    _0x1db96b = _0x132031[:8]
    _0x6339b6 = int(_0x132031[12:]) if len(_0x132031) > 12 else 0
    _0x56549e = _0x6339b6 * 2 + 18 - 2
    encrypted = x(str(_0x56549e), _0x1db96b)
    guard_encrypted = base64.b64encode(encrypted.encode()).decode()
    return guard_encrypted


async def get_data(wss_url, task_id, task_token):
    async with websockets.connect(wss_url) as websocket:

        await websocket.send(json.dumps({"task_id": task_id, "task_token": task_token}))
        # print(json.dumps({"task_id": task_id, "task_token": task_token}))

        message = {}
        while not ("type" in message and message['type'] == "finished"):
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5)
                try:
                    message = json.loads(message)

                    if 'type' in message and message['type'] == 'finished':
                        break

                    if 'head' not in message or message['head'] == '':
                        print(f"({message['name']})\tIP: {message['ip']}\t请求失败")
                        return


                    print(message)

                except json.JSONDecodeError:
                    # print("服务器返回错误的信息：", message)
                    break
            except asyncio.TimeoutError:
                return
                # await websocket.send(json.dumps({"task_id": task_id, "task_token": task_token}))

        print("服务器测速完成，等待断开连接。")
        await websocket.close()


async def cloudflare_hit(url):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://www.itdog.cn',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'referer': 'https://www.itdog.cn/http/',
        'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    }

    data = {
        'line': '',
        'host': url,
        'host_s': urlparse(url).hostname,
        'check_mode': 'fast',
        'ipv4': '',
        'method': 'get',
        'referer': '',
        'ua': '',
        'cookies': '',
        'redirect_num': '5',
        'dns_server_type': 'isp',
        'dns_server': '',
    }

    if 'guardret' not in session.cookies:
        session.post('https://www.itdog.cn/http/', headers=headers, data=data)

    if 'guard' in session.cookies:
        session.cookies['guardret'] = set_ret(session.cookies['guard'])

    response = session.post('https://www.itdog.cn/http/', headers=headers, data=data)

    pattern = re.compile(r"""var wss_url='(.*)';""")
    wss_url = pattern.search(response.content.decode()).group(1)
    pattern = re.compile(r"""var task_id='(.*)';""")
    task_id = pattern.search(response.content.decode()).group(1)

    task_token = hashlib.md5((task_id + "token_20230313000136kwyktxb0tgspm00yo5").encode()).hexdigest()[8:-8]

    try:
        await get_data(wss_url, task_id, task_token)
    except Exception as e:
        pass


async def main():
    await cloudflare_hit("https://www.baidu.com")


if __name__ == '__main__':
    asyncio.run(
        main()
    )
