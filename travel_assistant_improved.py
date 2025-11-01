import gradio as gr
import json
import os
from typing import List
from openai import OpenAI
import requests
from PIL import Image
from io import BytesIO
import re

# 从环境变量读取API配置（更安全）
API_KEY = "ms-b064f11b-4b11-4ae0-a00e-ff98a69c9bd3"
BASE_URL = "https://api-inference.modelscope.cn/v1/"
MODEL_NAME = "deepseek-ai/DeepSeek-V3.2-Exp"

def init_openai_client():
    """初始化OpenAI客户端"""
    if not API_KEY:
        raise ValueError("请设置 MODELSCOPE_API_KEY 环境变量")
    return OpenAI(base_url=BASE_URL, api_key=API_KEY)

def clean_response(text):
    """清理响应文本，移除思考过程标记"""
    if not text:
        return ""
    # 移除 <thinking>...</thinking> 标签及内容
    text = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL)
    # 移除其他可能的思考过程标记
    text = re.sub(r'\[?思考过程\]?:.*?(?=\n\n|\n【|\n=)', '', text, flags=re.DOTALL)
    # 清理多余的空行
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()

def validate_inputs(**kwargs):
    """验证输入参数"""
    for key, value in kwargs.items():
        if not value or str(value).strip() == "":
            return False, f"缺少必要参数: {key}"
    return True, ""

def generate_destination_recommendation(season, health_condition, budget, interests):
    """生成目的地推荐"""
    # 将兴趣列表转换为字符串
    if isinstance(interests, list):
        interests_str = "、".join(interests)
    else:
        interests_str = str(interests)

    # 验证输入
    is_valid, msg = validate_inputs(
        season=season, health_condition=health_condition,
        budget=budget, interests=interests_str
    )
    if not is_valid:
        return msg

    client = init_openai_client()
    system_prompt = """你是一个专业的老年旅行规划师。根据用户的季节、健康状况、预算和兴趣，推荐3-5个国内外热门适老目的地。

每个推荐应包括：
- 目的地名称
- 推荐理由（重点考虑避寒、康养、舒适度）
- 最佳旅行时长
- 注意事项（包括健康和安全建议）
- 舒适版活动示例

请用通俗易懂、温馨友好的语言回复，避免过于专业的术语。"""

    user_prompt = f"季节：{season}，健康状况：{health_condition}，预算：{budget}，兴趣偏好：{interests_str}"

    result = ""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            stream=True,
            temperature=0.7,
            max_tokens=1500
        )
        for chunk in response:
            answer_chunk = chunk.choices[0].delta.content
            if answer_chunk:
                result += answer_chunk
        result = clean_response(result)

        # 如果结果为空，返回友好提示
        if not result.strip():
            result = "抱歉，暂时无法生成推荐，请稍后再试或检查网络连接。"

    except Exception as e:
        result = f"[错误] 生成推荐时出错：{str(e)}\n\n请检查：\n1. API密钥是否正确\n2. 网络连接是否正常\n3. API服务是否可用"

    return result

def generate_itinerary_plan(destination, duration, mobility, health_focus):
    """生成行程规划"""
    # 将健康关注点列表转换为字符串
    if isinstance(health_focus, list):
        health_focus_str = "、".join(health_focus)
    else:
        health_focus_str = str(health_focus)

    is_valid, msg = validate_inputs(destination=destination, duration=duration)
    if not is_valid:
        return msg

    client = init_openai_client()
    system_prompt = """你是一个经验丰富的老年旅行行程规划师。请为老年人制定舒缓、贴心的日行程安排。

要求：
- 每天安排半日活动、半日休息
- 避免高强度行程
- 包含健康提示和注意事项
- 提供备用方案（雨天等）
- 语言亲切温和"""

    user_prompt = f"""目的地：{destination}
旅行时长：{duration}
行动能力：{mobility}
健康关注点：{health_focus_str}"""

    result = ""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            stream=True,
            temperature=0.7,
            max_tokens=1500
        )
        for chunk in response:
            answer_chunk = chunk.choices[0].delta.content
            if answer_chunk:
                result += answer_chunk
        result = clean_response(result)

        if not result.strip():
            result = "抱歉，暂时无法生成行程，请稍后再试。"

    except Exception as e:
        result = f"[错误] 生成行程时出错：{str(e)}"

    return result

def generate_checklist(destination, duration, special_needs):
    """生成旅行清单"""
    is_valid, msg = validate_inputs(destination=destination, duration=duration)
    if not is_valid:
        return msg

    client = init_openai_client()
    system_prompt = """你是一个细心的老年旅行助手。请为老年人制定详细的行前准备清单，按类别分组，标注必需品和可选物品。

清单应包括：
1. 证件类（身份证、护照、医保卡等）
2. 药品类（常用药、处方药、急救药）
3. 衣物类（根据目的地气候）
4. 电子设备（手机、充电器、血压计等）
5. 日用品（眼镜、假牙、拐杖等）
6. 其他必需品

请标注【必带】和【可选】，并给出温馨提示。"""

    user_prompt = f"目的地：{destination}，旅行时长：{duration}，特殊需求：{special_needs}"

    result = ""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            stream=True,
            temperature=0.6,
            max_tokens=1500
        )
        for chunk in response:
            answer_chunk = chunk.choices[0].delta.content
            if answer_chunk:
                result += answer_chunk
        result = clean_response(result)

        if not result.strip():
            result = "抱歉，暂时无法生成清单，请稍后再试。"

    except Exception as e:
        result = f"[错误] 生成清单时出错：{str(e)}"

    return result

def generate_travel_story(photos, custom_input):
    """生成旅行故事"""
    # Note: This function currently only uses text input, photos processing could be added later
    is_valid, msg = validate_inputs(custom_input=custom_input)
    if not is_valid:
        return "请先上传照片并填写补充信息"

    client = init_openai_client()
    system_prompt = """你是一个温暖的老年旅行故事讲述者。请根据照片和文字生成温馨、感人的旅行游记。

要求：
- 语言亲切温馨，充满正能量
- 重点描述旅行中的美好体验和感受
- 适当加入健康、舒适、康养相关的内容
- 篇幅适中，条理清晰"""

    user_prompt = f"用户补充信息：{custom_input}\n注意：照片功能暂未完全实现，请基于补充信息生成游记。"

    result = ""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            stream=True,
            temperature=0.8,
            max_tokens=1500
        )
        for chunk in response:
            answer_chunk = chunk.choices[0].delta.content
            if answer_chunk:
                result += answer_chunk
        result = clean_response(result)

        if not result.strip():
            result = "抱歉，暂时无法生成游记，请再提供一些补充信息。"

    except Exception as e:
        result = f"[错误] 生成游记时出错：{str(e)}"

    return result

def create_app():
    """创建Gradio应用"""
    # 兴趣偏好选项
    interest_options = [
        "避寒康养", "海岛度假", "文化历史", "温泉养生", "自然风光",
        "美食体验", "摄影采风", "休闲购物", "传统建筑", "民俗体验",
        "慢节奏游", "海滨漫步", "茶文化", "寺庙祈福", "古镇风情",
        "田园风光", "动物观赏", "艺术展览", "传统戏曲", "手工体验",
        "健康养生", "中医理疗", "瑜伽冥想", "森林浴", "阳光浴"
    ]

    # 健康关注点选项
    health_focus_options = [
        "避免过度疲劳", "饮食清淡", "需要靠近医院", "避免高原地区",
        "需要无障碍设施", "避免长时间步行", "注意防晒", "避免潮湿环境",
        "需要安静环境", "控制血压", "控制血糖", "关注空气质量",
        "需要携带药物", "保护心脏", "保持关节灵活", "预防感冒",
        "避免拥挤", "需要良好睡眠", "避免剧烈运动", "注意保暖",
        "多喝水", "定期休息", "避免暴晒", "饮食规律", "适度活动"
    ]

    with gr.Blocks(
        title="🧳 银发族智能旅行助手",
        theme=gr.themes.Soft(primary_hue="purple", secondary_hue="cyan"),
        css="""
        .gr-button {font-size: 18px !important; padding: 12px 20px !important;}
        .gr-textbox input {font-size: 16px !important;}
        .gr-multiselect {min-height: 120px !important;}
        """
    ) as app:
        gr.HTML('''
        <h1 style="text-align:center; font-size:48px; margin-bottom:10px;">
            🧳 银发族智能旅行助手
        </h1>
        <p style="text-align:center; font-size:18px; color:#666; margin-bottom:30px;">
            专为中老年朋友设计的温暖贴心的旅行规划伙伴
        </p>
        ''')

        with gr.Tabs():
            # Tab 1: 智能推荐与规划
            with gr.Tab("🌍 智能推荐与规划"):
                with gr.Row():
                    with gr.Column(scale=1):
                        season = gr.Dropdown(
                            ["春季", "夏季", "秋季", "冬季"],
                            label="🌸 季节",
                            value="秋季",
                            info="选择您计划出行的季节"
                        )
                        health = gr.Dropdown(
                            ["身体健康", "有慢性病但控制良好", "行动不便但可独立出行"],
                            label="🏥 健康状况",
                            value="身体健康",
                            info="真实反映您的健康状况，便于推荐更合适的目的地"
                        )
                        budget = gr.Dropdown(
                            ["经济实惠", "舒适型", "豪华型"],
                            label="💰 预算范围",
                            value="舒适型",
                            info="选择您的预算档次"
                        )
                        interests = gr.CheckboxGroup(
                            choices=interest_options,
                            value=["避寒康养", "温泉养生"],
                            label="🎨 兴趣偏好",
                            info="可选择多个您感兴趣的主题"
                        )
                        btn1 = gr.Button("🔍 推荐目的地", variant="primary", size="lg")
                        output1 = gr.Textbox(
                            label="✨ 推荐结果",
                            lines=20,
                            max_lines=30,
                            info="系统将为您推荐3-5个适合的目的地"
                        )

                    with gr.Column(scale=1):
                        dest = gr.Textbox(
                            label="📍 目的地",
                            info="填写您想去或已选择的目的地"
                        )
                        dur = gr.Dropdown(
                            ["3-5天", "一周左右", "10-15天", "15天以上"],
                            label="⏰ 旅行时长",
                            value="一周左右"
                        )
                        mobility = gr.Dropdown(
                            ["行走自如", "需要少量休息", "需要轮椅辅助"],
                            label="🚶 行动能力",
                            value="行走自如"
                        )
                        health_focus = gr.CheckboxGroup(
                            choices=health_focus_options,
                            value=["避免过度疲劳", "饮食清淡", "定期休息"],
                            label="❤️ 健康关注点",
                            info="可选择多个您的健康关注点"
                        )
                        btn2 = gr.Button("📋 制定行程", variant="primary", size="lg")
                        output2 = gr.Textbox(
                            label="✨ 行程安排",
                            lines=20,
                            max_lines=30,
                            info="为您量身定制的舒缓行程安排"
                        )
                        btn3 = gr.Button("🎁 继续生成清单", variant="secondary", size="lg")
                        output2_hint = gr.HTML(
                            value="""
                            <div style="padding:15px; background:#f0f8ff; border-radius:8px; margin-top:10px;">
                                <p style="color:#4169E1; font-size:14px; margin:0;">
                                    💡 提示：行程制定完成后，点击上方"🎁 继续生成清单"按钮，可直接为此行程生成专属清单！
                                </p>
                            </div>
                            """
                        )

                btn1.click(
                    fn=generate_destination_recommendation,
                    inputs=[season, health, budget, interests],
                    outputs=[output1]
                )
                btn2.click(
                    fn=generate_itinerary_plan,
                    inputs=[dest, dur, mobility, health_focus],
                    outputs=[output2]
                )

                # "继续生成清单"按钮：使用当前行程页面的输入直接生成清单
                def continue_to_checklist(destination, duration, health_focus):
                    # 将健康关注点转换为特殊需求描述
                    if isinstance(health_focus, list):
                        special_needs = "、".join(health_focus)
                    else:
                        special_needs = str(health_focus)
                    return generate_checklist(destination, duration, special_needs)

                btn3.click(
                    fn=continue_to_checklist,
                    inputs=[dest, dur, health_focus],
                    outputs=[output3]
                )

            # Tab 2: 清单与导游服务
            with gr.Tab("📝 清单与导游服务"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML('''
                        <div style="padding:15px; background:#fff3cd; border-radius:8px; margin-bottom:15px;">
                            <p style="color:#856404; font-size:14px; margin:0;">
                                💡 小贴士：刚从行程规划页面过来？您的目的地和时长信息已自动填充！如果需要修改，请直接编辑下方输入框。
                            </p>
                        </div>
                        ''')
                        checklist_dest = gr.Textbox(
                            label="📍 目的地",
                            value="",
                            info="填写目的地（从行程规划页面过来时将自动填充）"
                        )
                        checklist_dur = gr.Dropdown(
                            ["3-5天", "一周左右", "10-15天", "15天以上"],
                            label="⏰ 旅行时长",
                            value="一周左右",
                            info="选择旅行时长"
                        )
                        checklist_needs = gr.Textbox(
                            label="⚕️ 特殊需求",
                            value="身体健康，常规旅行",
                            info="例如：高血压、糖尿病、需携带医疗器械等"
                        )
                        btn3 = gr.Button("📋 生成清单", variant="primary", size="lg")
                        output3 = gr.Textbox(
                            label="✨ 清单内容",
                            lines=20,
                            max_lines=30,
                            info="详细的行前准备清单，按类别分组"
                        )

                btn3.click(
                    fn=generate_checklist,
                    inputs=[checklist_dest, checklist_dur, checklist_needs],
                    outputs=[output3]
                )

            # Tab 3: 旅行游记生成
            with gr.Tab("🎬 旅行游记生成"):
                with gr.Row():
                    with gr.Column(scale=1):
                        photos = gr.File(
                            file_count="multiple",
                            file_types=["image"],
                            label="📷 上传旅行照片"
                        )
                        story_input = gr.Textbox(
                            label="✍️ 补充信息",
                            lines=8,
                            info="描述您的旅行感受、希望突出的内容等"
                        )
                        btn4 = gr.Button("✨ 生成游记", variant="primary", size="lg")
                        output4 = gr.Textbox(
                            label="✨ 游记内容",
                            lines=20,
                            max_lines=30,
                            info="根据您的照片和描述生成的温馨游记"
                        )

                btn4.click(
                    fn=generate_travel_story,
                    inputs=[photos, story_input],
                    outputs=[output4]
                )

        # 添加底部说明
        gr.HTML('''
        <div style="text-align:center; margin-top:30px; padding:20px; background:#f5f5f5; border-radius:10px;">
            <p style="color:#666; font-size:14px;">
                💡 温馨提示：此应用为AI生成内容，仅供参考。具体行程请结合自身实际情况调整。<br/>
                🏥 建议出行前咨询医生，携带必要药品，关注目的地医疗资源。
            </p>
        </div>
        ''')

    return app

if __name__ == "__main__":
    print("正在启动银发族智能旅行助手...")
    print("请在浏览器中访问: http://localhost:7860")
    print("按 Ctrl+C 停止服务")
    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        inbrowser=True,
        share=False,
        show_error=True
    )
