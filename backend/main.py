from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
import tempfile
import uuid
import sys
import shutil
import httpx
from PIL import Image
from dotenv import load_dotenv
import asyncio
import time
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from core.travel_functions import generate_destination_recommendation, generate_itinerary_plan, generate_checklist as create_checklist
from core.video_editor import create_ai_video
from api.openai_client import OpenAIClient
try:
    from backend.aliyun_tts import get_tts_client
except ImportError:
    from aliyun_tts import get_tts_client

app = FastAPI(title="银发族智能旅行助手 API", version="1.0.0")

# 音频文件清理配置
AUDIO_CLEANUP_INTERVAL = 3600  # 每小时检查一次
AUDIO_FILE_TTL = 600  # 音频文件10分钟后过期（单位：秒）
STATIC_DIR = "static"

# TTS方言配置
TTS_VOICE_OPTIONS = {
    "xiaoyun": "标准普通话",
    "chuangirl": "四川话",
    "shanshan": "粤语",
    "cuijie": "东北话",
    "xiaoze": "湖南话",
    "aikan": "天津话"
}
DEFAULT_VOICE = os.getenv("ALIYUN_TTS_DEFAULT_VOICE", "xiaoyun")


async def cleanup_old_audio_files():
    """清理过期的音频文件"""
    try:
        static_path = Path(STATIC_DIR)
        if not static_path.exists():
            return

        current_time = time.time()
        deleted_count = 0

        for file in static_path.glob("tour_audio_*.mp3"):
            file_age = current_time - file.stat().st_mtime
            if file_age > AUDIO_FILE_TTL:
                try:
                    file.unlink()
                    deleted_count += 1
                    print(f"[Cleanup] 删除过期音频文件: {file.name}")
                except Exception as e:
                    print(f"[Cleanup] 删除文件失败 {file.name}: {e}")

        if deleted_count > 0:
            print(f"[Cleanup] 清理完成，删除了 {deleted_count} 个音频文件")
    except Exception as e:
        print(f"[Cleanup] 清理任务错误: {e}")


async def start_cleanup_task():
    """启动定期清理任务"""
    while True:
        await asyncio.sleep(AUDIO_CLEANUP_INTERVAL)
        await cleanup_old_audio_files()


@app.on_event("startup")
async def startup_event():
    """应用启动时的处理"""
    print("[Startup] ========== TTS配置信息 ==========")
    print(f"[Startup] 默认语音: {DEFAULT_VOICE} ({TTS_VOICE_OPTIONS.get(DEFAULT_VOICE, '未知')})")
    print(f"[Startup] 支持的语音: {', '.join([f'{k}({v})' for k, v in TTS_VOICE_OPTIONS.items()])}")
    print("[Startup] 启动音频文件清理任务...")
    asyncio.create_task(start_cleanup_task())

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务（用于提供生成的视频）
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 请求模型
class DestinationRequest(BaseModel):
    season: str
    health: str
    budget: str
    interests: List[str]

class ItineraryRequest(BaseModel):
    destination: str
    duration: str
    mobility: str
    health_focus: List[str]

class ChecklistRequest(BaseModel):
    origin: str
    destination: str
    duration: str
    departure_date: Optional[str] = ""
    needs: str
    itinerary_content: str

# 目的地推荐API
@app.post("/api/recommend-destinations")
async def recommend_destinations(request: DestinationRequest):
    try:
        result = generate_destination_recommendation(
            season=request.season,
            health_status=request.health,
            budget=request.budget,
            interests=request.interests
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 行程规划API
@app.post("/api/generate-itinerary")
async def generate_itinerary(request: ItineraryRequest):
    try:
        result = generate_itinerary_plan(
            destination=request.destination,
            duration=request.duration,
            mobility=request.mobility,
            health_focus=request.health_focus
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 旅行清单API
@app.post("/api/generate-checklist")
async def generate_checklist_api(request: ChecklistRequest):
    try:
        result = create_checklist(
            origin=request.origin,
            destination=request.destination,
            duration=request.duration,
            departure_date=request.departure_date,
            special_needs=request.needs,
            itinerary_text=request.itinerary_content
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 视频制作API
@app.post("/api/create-video")
async def create_video(images: List[UploadFile] = File(...), audio: Optional[UploadFile] = File(None)):
    try:
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 保存上传的图片
            image_paths = []
            for i, image in enumerate(images):
                image_path = os.path.join(temp_dir, f"image_{i}.jpg")
                with open(image_path, "wb") as f:
                    f.write(await image.read())
                # 调整图片尺寸，处理RGBA转RGB
                with Image.open(image_path) as img:
                    if img.mode == 'RGBA':
                        img = img.convert('RGB')
                    img.save(image_path, "JPEG")
                image_paths.append(image_path)
            # 保存上传的音频
            audio_path = None
            if audio:
                audio_path = os.path.join(temp_dir, "audio.mp3")
                with open(audio_path, "wb") as f:
                    f.write(await audio.read())

            # 使用AI视频生成
            result = create_ai_video(
                images=image_paths,
                audio=audio_path,
                target_width=720,
                target_height=1280  # 9:16 竖屏比例
            )

            # 复制视频到static目录
            video_id = str(uuid.uuid4())
            video_filename = f"travel_video_{video_id}.mp4"
            video_dest = os.path.join("static", video_filename)
            shutil.copy(result['video_path'], video_dest)

            return {
                "message": "AI视频生成成功！",
                "video_path": f"/static/{video_filename}",
                "script": result.get('script', ''),
                "image_descriptions": result.get('image_descriptions', [])
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 健康评估API
@app.get("/api/health-assessment")
async def health_assessment():
    try:
        # 这里应该调用健康评估模型
        # 暂时使用模拟数据
        return {
            "result": "健康评估结果：您的身体状况良好，可以进行适度的旅行。建议携带常用药物，避免过度劳累。"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 智能导游API - 获取附近POI
@app.get("/api/tour-guide/pois")
async def get_nearby_pois(lng: float, lat: float, radius: int = 1000):
    try:
        # 这里应该调用高德地图API获取POI数据
        # 暂时使用模拟数据
        pois = [
            {"id": "1", "name": "故宫博物院", "type": "旅游景点", "lng": 116.3970, "lat": 39.9087, "address": "北京市东城区景山前街4号"},
            {"id": "2", "name": "天安门广场", "type": "旅游景点", "lng": 116.4038, "lat": 39.9042, "address": "北京市东城区天安门广场"},
            {"id": "3", "name": "颐和园", "type": "旅游景点", "lng": 116.2750, "lat": 39.9917, "address": "北京市海淀区新建宫门路19号"}
        ]
        return {"pois": pois}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 智能导游API - 获取导游讲解词
@app.get("/api/tour-guide/explanation")
async def get_tour_explanation(poi_name: str):
    try:
        client = OpenAIClient()
        system_prompt = "你是一个专业的导游，为银发族游客提供详细、生动的景点讲解。讲解内容要通俗易懂，富有感染力，同时考虑老年人的特点，语速适中，重点突出历史文化和景点特色。"
        user_prompt = f"请为{poi_name}编写一段导游讲解词，适合银发族游客。讲解要详细介绍景点的历史背景、主要特色和参观要点。"
        explanation = client.generate_response(system_prompt, user_prompt, use_modelscope=True)
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 智能导游API - 播放导游词（TTS）
@app.get("/api/tour-guide/play-audio")
async def play_tour_audio(text: str, voice: str = "xiaoyun"):
    try:
        print(f"[TTS] 开始生成语音，文本: {text}, 语音: {voice}")
        # 获取阿里云TTS客户端
        tts_client = await get_tts_client()

        # 调用TTS
        print(f"[TTS] 调用text_to_speech...")
        audio_data = await tts_client.text_to_speech(
            text=text,
            format="mp3",
            sample_rate=16000,
            voice=voice,
            volume=80,
            speech_rate=0,
            pitch_rate=0
        )
        print(f"[TTS] 音频数据生成成功，大小: {len(audio_data)} bytes")

        # 保存音频文件
        audio_id = str(uuid.uuid4())
        audio_filename = f"tour_audio_{audio_id}.mp3"
        audio_path = os.path.join("static", audio_filename)

        with open(audio_path, "wb") as f:
            f.write(audio_data)

        print(f"[TTS] 音频文件已保存: {audio_filename} (将在 {AUDIO_FILE_TTL} 秒后自动清理)")

        return {
            "message": "音频生成成功",
            "audio_url": f"/static/{audio_filename}",
            "format": "mp3",
            "sample_rate": 16000,
            "voice": voice,
            "ttl": AUDIO_FILE_TTL
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[TTS] 错误: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# 安全提示API
@app.get("/api/safety-tips")
async def safety_tips():
    try:
        # 这里应该调用安全提示模型
        # 暂时使用模拟数据
        return {
            "result": "旅行安全提示：\n1. 携带身份证和老年证\n2. 随身携带常用药物\n3. 注意饮食卫生\n4. 避免单独行动\n5. 保持手机电量充足\n6. 告知家人旅行计划"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 图片生成代理API - 解决跨域问题
class ImageGenerationRequest(BaseModel):
    image_url: str
    prompt: str

@app.post("/api/generate-cartoon-map")
async def generate_cartoon_map(request: ImageGenerationRequest):
    try:
        api_key = os.getenv("DASHSCOPE_API_KEY")
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "qwen-image-edit-plus-2025-10-30",
                    "input": {
                        "messages": [{
                            "role": "user",
                            "content": [{"image": request.image_url}, {"text": request.prompt}]
                        }]
                    },
                    "parameters": {"n": 1, "negative_prompt": "低质量", "prompt_extend": True, "watermark": False}
                }
            )
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)