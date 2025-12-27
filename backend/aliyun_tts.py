"""
阿里云TTS Token获取模块
自动获取和刷新Access Token
"""

import json
from datetime import datetime, timedelta
import httpx
import os

try:
    from aliyunsdkcore.client import AcsClient
    from aliyunsdkcore.request import CommonRequest
except ImportError:
    AcsClient = None
    CommonRequest = None


class AliyunTTSClient:
    """阿里云TTS客户端"""

    def __init__(self, appkey: str, access_key_id: str, access_key_secret: str, region: str = "cn-shanghai"):
        """
        初始化阿里云TTS客户端

        Args:
            appkey: 阿里云TTS项目AppKey
            access_key_id: 阿里云AccessKey ID（用于获取Token）
            access_key_secret: 阿里云AccessKey Secret（用于签名计算）
            region: 地域，默认cn-shanghai
        """
        self.appkey = appkey
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.region = region
        self.token = None
        self.expire_time = None

        # TTS服务地址
        self.tts_urls = {
            "cn-shanghai": "https://nls-gateway-cn-shanghai.aliyuncs.com/stream/v1/tts",
            "cn-beijing": "https://nls-gateway-cn-beijing.aliyuncs.com/stream/v1/tts",
            "cn-shenzhen": "https://nls-gateway-cn-shenzhen.aliyuncs.com/stream/v1/tts"
        }

        # 初始化阿里云SDK客户端
        if AcsClient:
            self.acs_client = AcsClient(
                self.access_key_id,
                self.access_key_secret,
                self.region
            )
        else:
            self.acs_client = None
            print("[TTS] 警告: 未安装aliyun-python-sdk-core，Token获取可能失败")

    async def get_token(self) -> str:
        """
        获取Access Token

        Returns:
            Token字符串
        """
        # 检查Token是否仍然有效（提前1小时刷新）
        if self.token and self.expire_time:
            if datetime.now() + timedelta(hours=1) < self.expire_time:
                print(f"[TTS] 使用缓存的Token，过期时间: {self.expire_time}")
                return self.token

        print(f"[TTS] 获取新的Access Token...")

        if self.acs_client:
            # 使用阿里云SDK获取Token
            request = CommonRequest()
            request.set_method('POST')
            request.set_domain(f'nls-meta.{self.region}.aliyuncs.com')
            request.set_version('2019-02-28')
            request.set_action_name('CreateToken')

            try:
                response = self.acs_client.do_action_with_exception(request)
                data = json.loads(response)

                if 'Token' in data and 'Id' in data['Token']:
                    self.token = data['Token']['Id']
                    self.expire_time = datetime.fromtimestamp(data['Token']['ExpireTime'])
                    print(f"[TTS] Token获取成功，过期时间: {self.expire_time}")
                    return self.token
                else:
                    raise Exception(f"获取Token失败: {data}")
            except Exception as e:
                raise Exception(f"SDK调用失败: {str(e)}")
        else:
            raise Exception("未安装aliyun-python-sdk-core，请先安装: pip install aliyun-python-sdk-core==2.15.1")
    
    def _split_text_for_tts(self, text: str, max_length: int = 300) -> list:
        """
        将长文本分段，每段不超过最大长度

        Args:
            text: 原始文本
            max_length: 每段最大字符数（阿里云限制为300）

        Returns:
            分段后的文本列表
        """
        if len(text) <= max_length:
            return [text]

        segments = []
        current_segment = ""

        # 按段落分割（换行符、句号等）
        sentences = []
        for char in text:
            current_segment += char
            if char in ['\n', '。', '！', '？', '.', '!', '?']:
                sentences.append(current_segment)
                current_segment = ""

        if current_segment:
            sentences.append(current_segment)

        # 将句子合并成不超长的段落
        result = []
        current = ""
        for sentence in sentences:
            if len(current + sentence) <= max_length:
                current += sentence
            else:
                if current:
                    result.append(current)
                # 如果单个句子太长，强制分割
                if len(sentence) > max_length:
                    for i in range(0, len(sentence), max_length):
                        result.append(sentence[i:i + max_length])
                else:
                    current = sentence

        if current:
            result.append(current)

        print(f"[TTS] 文本分段：原长度={len(text)}, 分成{len(result)}段")
        return result

    async def text_to_speech(
        self,
        text: str,
        format: str = "mp3",
        sample_rate: int = 16000,
        voice: str = "chuangirl",
        volume: int = 80,
        speech_rate: int = 0,
        pitch_rate: int = 0
    ) -> bytes:
        """
        文本转语音（支持长文本自动分段）

        Args:
            text: 待合成文本
            format: 音频格式（mp3, wav, pcm）
            sample_rate: 采样率（8000, 16000）
            voice: 发音人
            volume: 音量（0-100）
            speech_rate: 语速（-500~500）
            pitch_rate: 语调（-500~500）

        Returns:
            音频数据（bytes）
        """
        print(f"[TTS] text_to_speech调用参数: text长度={len(text)}, voice={voice}, format={format}")

        # 获取Token
        token = await self.get_token()

        # 分割长文本
        text_segments = self._split_text_for_tts(text)

        # 如果只有一段，直接合成
        if len(text_segments) == 1:
            return await self._synthesize_single(text_segments[0], token, format, sample_rate,
                                                    voice, volume, speech_rate, pitch_rate)

        # 多段合成，需要拼接音频
        all_audio_data = bytearray()
        for i, segment in enumerate(text_segments):
            print(f"[TTS] 合成第 {i+1}/{len(text_segments)} 段，长度={len(segment)}")
            audio_data = await self._synthesize_single(segment, token, format, sample_rate,
                                                        voice, volume, speech_rate, pitch_rate)
            all_audio_data.extend(audio_data)

        print(f"[TTS] 总共合成 {len(text_segments)} 段，总大小: {len(all_audio_data)} bytes")
        return bytes(all_audio_data)

    async def _synthesize_single(
        self,
        text: str,
        token: str,
        format: str,
        sample_rate: int,
        voice: str,
        volume: int,
        speech_rate: int,
        pitch_rate: int
    ) -> bytes:
        """
        合成单段文本

        Args:
            text: 待合成文本
            token: 访问令牌
            其他参数：同text_to_speech

        Returns:
            音频数据（bytes）
        """
        # 构造请求
        tts_url = self.tts_urls.get(self.region, self.tts_urls["cn-shanghai"])

        payload = {
            "appkey": self.appkey,
            "token": token,
            "text": text,
            "format": format,
            "sample_rate": sample_rate,
            "voice": voice,
            "volume": volume,
            "speech_rate": speech_rate,
            "pitch_rate": pitch_rate
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                tts_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code != 200:
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                print(f"[TTS] 错误响应: {error_data}")
                raise Exception(f"TTS调用失败: {error_data}")

            return response.content


# 全局客户端实例
_client_instance = None


async def get_tts_client() -> AliyunTTSClient:
    """
    获取全局TTS客户端实例
    
    Returns:
        AliyunTTSClient实例
    """
    global _client_instance
    
    if _client_instance is None:
        appkey = os.getenv("ALIYUN_TTS_APPKEY")
        access_key_id = os.getenv("ALIYUN_ACCESS_KEY_ID")
        access_key_secret = os.getenv("ALIYUN_ACCESS_KEY_SECRET")
        region = os.getenv("ALIYUN_TTS_REGION", "cn-shanghai")
        
        if not appkey or not access_key_id or not access_key_secret:
            raise ValueError("阿里云TTS配置未设置，请在.env文件中配置ALIYUN_TTS_APPKEY、ALIYUN_ACCESS_KEY_ID和ALIYUN_ACCESS_KEY_SECRET")
        
        _client_instance = AliyunTTSClient(appkey, access_key_id, access_key_secret, region)
    
    return _client_instance
