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

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from core.travel_functions import generate_destination_recommendation, generate_itinerary_plan, generate_checklist

app = FastAPI(title="银发族智能旅行助手 API", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
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
async def generate_checklist(request: ChecklistRequest):
    try:
        result = generate_checklist(
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
                # 调整图片尺寸
                with Image.open(image_path) as img:
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)