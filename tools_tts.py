# -*- coding: utf-8 -*-
# @Time    : 2019/2/28 2:42 PM
# @Author  : python疯子
# @File    : TTS_TOOLS.py
# @Software: PyCharm

# 安装阿里云SDK
# pip install aliyun-python-sdk-core==2.12.0

# -*- coding: utf8 -*-

import base64
import json
import time
import hashlib
import urllib.request
import urllib.parse

import requests
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

# 阿里云的
ALI_URL = "https://nls-gateway.cn-shanghai.aliyuncs.com/stream/v1/tts"

# 思必驰
DUI_URL = "https://tts.dui.ai/runtime/v2/synthesize?productId=0226&apikey=自己的apikey"

# 阿里云的TTS
def get_token():
    # 创建AcsClient实例
    client = AcsClient("AccessKey ID", "AccessKeySecret", "cn-shanghai")
    # 创建request，并设置参数
    request = CommonRequest()
    request.set_method('POST')
    request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
    request.set_version('2018-05-18')
    request.set_uri_pattern('/pop/2018-05-18/tokens')
    response = client.do_action_with_exception(request)
    response = json.loads(response.decode("utf-8"))
    print(response)

    # token_expireTime token的有效期(时间戳)
    access_token = response.get("Token").get("Id")
    token_expireTime = response.get("Token").get("ExpireTime")
    return access_token, token_expireTime

def tts_ali(text):

    # 获取存储的access_token, token_expireTime  两个同时更新
    token_expireTime = 1551513046
    access_token = "9fcdcd2a190f49cb926dc5c2e24043c8"

    # 当前的时间戳 和 token有效期对比，如果过期则重新生成
    local_time = int(time.time())
    if local_time >= token_expireTime:
        # 重新生成并存储
        access_token, token_expireTime = get_token()

    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "X-NLS-Token":access_token,
        }

    data_info = {
        "appkey":"appkey",
        "text":text,
        "token":access_token,
        "format":"wav",
        "voice":"yina",
        "sample_rate":"16000",  # 音频采样率，默认是16000
        "volume":"50", # 音量，范围是0~100，默认50
        "speech_rate":"45", # 语速，范围是-500~500，默认是0
        "pitch_rate":"0", # 语调，范围是-500~500，默认是0

        # 试听发音人：https://ai.aliyun.com/nls/tts?spm=5176.8142029.388261.47.f8ed6d3e0NhBch
        # 发音人参数：https://help.aliyun.com/document_detail/84435.html?spm=a2c4g.11186623.6.581.69a853d5E4c3vM
        # 推荐：小梦 思悦 小美 伊娜
        }

    data = json.dumps(data_info)

    ret = requests.post(ALI_URL, headers=headers, data=data, timeout=5)
    save_wav(ret.content, "ali2.wav")


# 百度
def tts_baidu(text):
    baidu_url = "http://tsn.baidu.com/text2audio?lan=zh&ctp=1&cuid=abcdxxx&tok=自己的token值&tex={}&vol=9&per=0&spd=5&pit=5&aue=6".format(text)

    ret = requests.get(baidu_url, timeout=5)
    save_wav(ret.content, "siyue.wav")

# 思必驰
def tts_dui(text):
    data_dict = {
        "context": {"productId": "0226"},
        "request": {"requestId": "tryRequestId",
        "audio": {"audioType": "WAV", "sampleRate": 16000, "channel": 1, "sampleBytes": 2},
            "tts": {
            "text": text,
            "textType": "text",
            "voiceId": "lili1f_shangwu"}}}
    data = json.dumps(data_dict)

    headers = {
        'content-type': 'application/json',
        'User-Agent': 'Mozilla/5.0 '}

    r = requests.post(DUI_URL, data=data, headers=headers, timeout=5)

    print(r)

    # 写入文件生成音频
    save_wav(r.content, "DUI.wav")


def tts_xunfei(text):
    # API请求地址、API KEY、APP ID等参数，提前填好备用
    api_url = "http://api.xfyun.cn/v1/service/v1/tts"
    API_KEY = "自己的API_KEY"
    APP_ID = "自己的APP_ID"
    OUTPUT_FILE = "讯飞.wav"  # 输出音频的保存路径，请根据自己的情况替换
    TEXT = text

    # 构造输出音频配置参数custom_skill.py3
    Param = {"auf": "audio/L16;rate=16000",  # 音频采样率
        "aue": "raw",  # 音频编码，raw(生成wav)或lame(生成mp3)
        "voice_name": "x_xiaoyuan", "speed": "50",  # 语速[0,100]
        "volume": "77",  # 音量[0,100]
        "pitch": "50",  # 音高[0,100]
        "engine_type": "aisound"  # 引擎类型。aisound（普通效果），intp65（中文），intp65_en（英文）
        }
    # 配置参数编码为base64字符串，过程：字典→明文字符串→utf8编码→base64(bytes)→base64字符串
    Param_str = json.dumps(Param)  # 得到明文字符串
    Param_utf8 = Param_str.encode('utf8')  # 得到utf8编码(bytes类型)
    Param_b64 = base64.b64encode(Param_utf8)  # 得到base64编码(bytes类型)
    Param_b64str = Param_b64.decode('utf8')  # 得到base64字符串

    # 构造HTTP请求的头部
    time_now = str(int(time.time()))
    checksum = (API_KEY + time_now + Param_b64str).encode('utf8')
    checksum_md5 = hashlib.md5(checksum).hexdigest()
    header = {"X-Appid": APP_ID, "X-CurTime": time_now, "X-Param": Param_b64str, "X-CheckSum": checksum_md5}

    # 构造HTTP请求Body
    body = {"text": TEXT}
    body_urlencode = urllib.parse.urlencode(body)
    body_utf8 = body_urlencode.encode('utf8')

    # 发送HTTP POST请求
    req = urllib.request.Request(api_url, data=body_utf8, headers=header)
    response = urllib.request.urlopen(req)

    # 读取结果
    response_head = response.headers['Content-Type']
    if (response_head == "audio/mpeg"):
        data = response.read()  # a 'bytes' object
        save_wav(data, OUTPUT_FILE)
    else:
        print(response.read().decode('utf8'))

# 灵云
def tts_lingyun(text):

    linghyun_URL = "http://api.hcicloud.com:8880/tts/synthtext"
    request_data = "2014-6-18 10:10:11"

    data = request_data + "参数"
    md5 = hashlib.md5()
    md5.update(data.encode('utf-8'))  # 注意转码
    res = md5.hexdigest()

    headers = {"x-app-key": "c95d54cf", "x-sdk-version": "3.9", "x-request-date": request_data,
        "x-task-config": "capkey=tts.cloud.xiaokun,audioformat=mp3,speed=2,volume=9.99", "x-session-key": res,
        "x-udid": "101:1234567890"}

    r = requests.post(linghyun_URL, headers=headers,
                      data=text.encode('utf-8'),
                      timeout=5)

    # 获取音频数据
    ret = r.content
    ret = ret[ret.find(b'</ResponseInfo>') + 15:]

    # 写入文件生成音频
    save_wav(bytes(ret), "灵云.mp3")

# 写入文件生成音频
def save_wav(data, file_path):
    with open(file_path, "wb") as f:
        f.write(data)



if __name__ == '__main__':
    # 文字最后以英文格式的3个? 或 3个! 结尾，否则最后3个字发音不出来
    text = "我们公司代理记账200元一个月起，有专业的财税服务团队，对您进行三对一式的服务，根据您公司情况给您制定合理的财税方案。而且咱们现在还支持APP的线上做账，具体的我让咱们的客户经理和您联系吧。"
    # tts_ali(text)
    tts_dui(text)
    tts_lingyun(text)




