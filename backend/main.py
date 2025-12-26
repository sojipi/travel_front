from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
import json
from datetime import datetime
from PIL import Image
import moviepy.editor as mp
from moviepy.editor import ImageSequenceClip, AudioFileClip, CompositeVideoClip
import tempfile
import uuid
import sys
import httpx
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from core.travel_functions import generate_destination_recommendation, generate_itinerary_plan, generate_checklist as create_checklist
from api.openai_client import OpenAIClient
import pyttsx3

app = FastAPI(title="银发族智能旅行助手 API", version="1.0.0")

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
                    img = img.resize((1920, 1080))  # 1080p
                    img.save(image_path, "JPEG")
                image_paths.append(image_path)
            # 保存上传的音频
            audio_path = None
            if audio:
                audio_path = os.path.join(temp_dir, "audio.mp3")
                with open(audio_path, "wb") as f:
                    f.write(await audio.read())
            # 创建视频
            clip = ImageSequenceClip(image_paths, durations=[3] * len(image_paths))  # 每张图片显示3秒
            # 添加音频
            if audio_path:
                audio_clip = AudioFileClip(audio_path)
                # 如果音频比视频长，裁剪音频
                if audio_clip.duration > clip.duration:
                    audio_clip = audio_clip.subclip(0, clip.duration)
                # 如果音频比视频短，循环音频
                elif audio_clip.duration < clip.duration:
                    audio_clip = mp.concatenate_audioclips([audio_clip] * (int(clip.duration / audio_clip.duration) + 1))
                    audio_clip = audio_clip.subclip(0, clip.duration)
                clip = clip.set_audio(audio_clip)
            # 生成唯一的视频文件名
            video_id = str(uuid.uuid4())
            video_filename = f"travel_video_{video_id}.mp4"
            video_path = os.path.join("static", video_filename)
            # 保存视频
            clip.write_videofile(video_path, fps=24, codec="libx264", audio_codec="aac")
            # 关闭所有剪辑
            clip.close()
            if audio_path:
                audio_clip.close()
            # 返回视频URL
            return {
                "message": "视频生成成功！",
                "video_path": f"/static/{video_filename}"
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
async def play_tour_audio(text: str):
    try:
        # 初始化TTS引擎
        engine = pyttsx3.init()
        # 设置语速
        engine.setProperty('rate', 150)
        # 设置音量
        engine.setProperty('volume', 0.9)
        # 播放文本
        engine.say(text)
        engine.runAndWait()
        return {"message": "音频播放完成"}
    except Exception as e:
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