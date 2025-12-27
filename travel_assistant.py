import gradio as gr
import json
import os
from typing import List
from openai import OpenAI
import requests
from PIL import Image
from io import BytesIO
import re

# API配置
API_KEY = ""
BASE_URL = "https://api-inference.modelscope.cn/v1/"
MODEL_NAME = "deepseek-ai/DeepSeek-V3.2"

def init_openai_client():
    return OpenAI(base_url=BASE_URL, api_key=API_KEY)

def clean_response(text):
    """清理响应文本，移除思考过程标记"""
    # 移除 <thinking>...</thinking> 标签及内容
    text = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL)
    # 移除其他可能的思考过程标记
    text = re.sub(r'\[?思考过程\]?:.*?(?=\n\n|\n【|\n=)', '', text, flags=re.DOTALL)
    # 清理多余的空行
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()

def generate_destination_recommendation(season, health_condition, budget, interests):
    client = init_openai_client()
    system_prompt = """你是一个专业的老年旅行规划师。根据用户的季节、健康状况、预算和兴趣，推荐3-5个国内外热门适老目的地。
每个推荐应包括：目的地名称、推荐理由、最佳旅行时长、注意事项。请用通俗易懂的语言回复。"""
    
    user_prompt = f"季节：{season}，健康状况：{health_condition}，预算：{budget}，兴趣偏好：{interests}"
    
    result = ""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            stream=True
        )
        for chunk in response:
            answer_chunk = chunk.choices[0].delta.content
            if answer_chunk:
                result += answer_chunk
        result = clean_response(result)
    except Exception as e:
        result = f"[错误] 生成推荐时出错：{str(e)}"
    
    return result

def generate_itinerary_plan(destination, duration, mobility, health_focus):
    client = init_openai_client()
    system_prompt = """你是一个经验丰富的老年旅行行程规划师。请为老年人制定舒缓、贴心的日行程安排。"""
    
    user_prompt = f"目的地：{destination}，旅行时长：{duration}，行动能力：{mobility}，健康关注点：{health_focus}"
    
    result = ""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            stream=True
        )
        for chunk in response:
            answer_chunk = chunk.choices[0].delta.content
            if answer_chunk:
                result += answer_chunk
        result = clean_response(result)
    except Exception as e:
        result = f"[错误] 生成行程时出错：{str(e)}"
    
    return result

def generate_checklist(destination, duration, special_needs):
    client = init_openai_client()
    system_prompt = """你是一个细心的老年旅行助手。请为老年人制定详细的行前准备清单，按类别分组，标注必需品和可选物品。"""
    
    user_prompt = f"目的地：{destination}，旅行时长：{duration}，特殊需求：{special_needs}"
    
    result = ""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            stream=True
        )
        for chunk in response:
            answer_chunk = chunk.choices[0].delta.content
            if answer_chunk:
                result += answer_chunk
        result = clean_response(result)
    except Exception as e:
        result = f"[错误] 生成清单时出错：{str(e)}"
    
    return result

def generate_travel_story(photos, custom_input):
    client = init_openai_client()
    system_prompt = """你是一个温暖的老年旅行故事讲述者。请根据照片和文字生成温馨、感人的旅行游记，语言亲切温馨，充满正能量。"""
    
    user_prompt = f"用户补充信息：{custom_input}"
    
    result = ""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            stream=True
        )
        for chunk in response:
            answer_chunk = chunk.choices[0].delta.content
            if answer_chunk:
                result += answer_chunk
        result = clean_response(result)
    except Exception as e:
        result = f"[错误] 生成游记时出错：{str(e)}"
    
    return result

def create_app():
    with gr.Blocks(title="🧳 银发族智能旅行助手", theme=gr.themes.Soft(primary_hue="purple", secondary_hue="cyan")) as app:
        gr.HTML('<h1 style="text-align:center;font-size:48px;">🧳 银发族智能旅行助手</h1>')
        
        with gr.Tabs():
            with gr.Tab("🌍 智能推荐与规划"):
                with gr.Row():
                    with gr.Column():
                        season = gr.Dropdown(["春季", "夏季", "秋季", "冬季"], label="🌸 季节", value="秋季")
                        health = gr.Dropdown(["身体健康", "有慢性病但控制良好"], label="🏥 健康状况", value="身体健康")
                        budget = gr.Dropdown(["经济实惠", "舒适型", "豪华型"], label="💰 预算", value="舒适型")
                        interests = gr.Textbox(label="🎨 兴趣偏好", value="避寒、康养")
                        btn1 = gr.Button("🔍 推荐目的地", variant="primary")
                        output1 = gr.Textbox(label="✨ 推荐结果", lines=20)
                        btn1.click(fn=generate_destination_recommendation, inputs=[season, health, budget, interests], outputs=[output1])
                    
                    with gr.Column():
                        dest = gr.Textbox(label="📍 目的地")
                        dur = gr.Dropdown(["3-5天", "一周左右", "10-15天"], label="⏰ 旅行时长", value="一周左右")
                        mobility = gr.Dropdown(["行走自如", "需要少量休息"], label="🚶 行动能力", value="行走自如")
                        health_focus = gr.Textbox(label="❤️ 健康关注点")
                        btn2 = gr.Button("📋 制定行程", variant="primary")
                        output2 = gr.Textbox(label="✨ 行程安排", lines=20)
                        btn2.click(fn=generate_itinerary_plan, inputs=[dest, dur, mobility, health_focus], outputs=[output2])
            
            with gr.Tab("📝 清单与导游服务"):
                with gr.Row():
                    with gr.Column():
                        checklist_dest = gr.Textbox(label="📍 目的地")
                        checklist_dur = gr.Dropdown(["3-5天", "一周左右"], label="⏰ 旅行时长", value="一周左右")
                        checklist_needs = gr.Textbox(label="⚕️ 特殊需求")
                        btn3 = gr.Button("📋 生成清单", variant="primary")
                        output3 = gr.Textbox(label="✨ 清单内容", lines=20)
                        btn3.click(fn=generate_checklist, inputs=[checklist_dest, checklist_dur, checklist_needs], outputs=[output3])
            
            with gr.Tab("🎬 旅行游记生成"):
                with gr.Row():
                    with gr.Column():
                        photos = gr.File(file_count="multiple", file_types=["image"], label="📷 上传旅行照片")
                        story_input = gr.Textbox(label="✍️ 补充信息", lines=5)
                        btn4 = gr.Button("✨ 生成游记", variant="primary")
                        output4 = gr.Textbox(label="✨ 游记内容", lines=20)
                        btn4.click(fn=generate_travel_story, inputs=[photos, story_input], outputs=[output4])
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.launch(server_name="0.0.0.0", server_port=7860, inbrowser=True)
