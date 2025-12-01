"""
UI components module for the travel assistant application.
Contains Gradio components and UI-related functions.
"""

import gradio as gr
from typing import Dict, Any, List
try:
    from ..config.config import (
        INTEREST_OPTIONS, HEALTH_FOCUS_OPTIONS, SEASON_OPTIONS, 
        HEALTH_STATUS_OPTIONS, BUDGET_OPTIONS, MOBILITY_OPTIONS, 
        DURATION_OPTIONS, DEFAULT_INTERESTS, DEFAULT_HEALTH_FOCUS, 
        DEFAULT_SEASON, DEFAULT_HEALTH_STATUS, DEFAULT_BUDGET, 
        DEFAULT_MOBILITY, DEFAULT_DURATION, CUSTOM_CSS, LOADING_HTML,
        APP_TITLE, APP_DESCRIPTION, THEME_PRIMARY, THEME_SECONDARY
    )
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config.config import (
        INTEREST_OPTIONS, HEALTH_FOCUS_OPTIONS, SEASON_OPTIONS, 
        HEALTH_STATUS_OPTIONS, BUDGET_OPTIONS, MOBILITY_OPTIONS, 
        DURATION_OPTIONS, DEFAULT_INTERESTS, DEFAULT_HEALTH_FOCUS, 
        DEFAULT_SEASON, DEFAULT_HEALTH_STATUS, DEFAULT_BUDGET, 
        DEFAULT_MOBILITY, DEFAULT_DURATION, CUSTOM_CSS, LOADING_HTML,
        APP_TITLE, APP_DESCRIPTION, THEME_PRIMARY, THEME_SECONDARY
    )


def create_header() -> gr.HTML:
    """Create the application header."""
    return gr.HTML(f'''
    <h1 style="text-align:center; font-size:48px; margin-bottom:10px;">
        {APP_TITLE}
    </h1>
    <p style="text-align:center; font-size:18px; color:#666; margin-bottom:30px;">
        {APP_DESCRIPTION}
    </p>
    ''')


def create_destination_section() -> Dict[str, Any]:
    """Create the destination recommendation section."""
    with gr.Column(scale=1):
        header = gr.HTML('''
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 15px; margin-bottom: 20px; text-align: center;">
            <h2 style="margin: 0; font-size: 32px;">🌟 目的地推荐</h2>
            <p style="margin: 10px 0 0 0; font-size: 16px;">根据您的需求智能推荐适合的旅行目的地</p>
        </div>
        ''')
        
        season = gr.Dropdown(
            SEASON_OPTIONS,
            label="🌸 季节",
            value=DEFAULT_SEASON,
            info="选择您计划出行的季节"
        )
        
        health = gr.Dropdown(
            HEALTH_STATUS_OPTIONS,
            label="🏥 健康状况",
            value=DEFAULT_HEALTH_STATUS,
            info="真实反映您的健康状况，便于推荐更合适的目的地"
        )
        
        budget = gr.Dropdown(
            BUDGET_OPTIONS,
            label="💰 预算范围",
            value=DEFAULT_BUDGET,
            info="选择您的预算档次"
        )
        
        interests = gr.CheckboxGroup(
            choices=INTEREST_OPTIONS,
            value=DEFAULT_INTERESTS,
            label="🎨 兴趣偏好",
            info="可选择多个您感兴趣的主题"
        )
        
        btn = gr.Button("🔍 推荐目的地", variant="primary", size="lg")
        
        output = gr.Textbox(
            label="✨ 推荐结果",
            lines=15,
            max_lines=25,
            info="系统将为您推荐3-5个适合的目的地"
        )
    
    return {
        'season': season,
        'health': health,
        'budget': budget,
        'interests': interests,
        'button': btn,
        'output': output
    }


def create_itinerary_section() -> Dict[str, Any]:
    """Create the itinerary planning section."""
    with gr.Column(scale=1):
        header = gr.HTML('''
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 25px; border-radius: 15px; margin-bottom: 20px; text-align: center;">
            <h2 style="margin: 0; font-size: 32px;">📋 行程规划</h2>
            <p style="margin: 10px 0 0 0; font-size: 16px;">为您量身定制舒缓贴心的旅行行程</p>
        </div>
        ''')
        
        destination = gr.Textbox(
            label="📍 目的地",
            info="填写您想去或已选择的目的地"
        )
        
        duration = gr.Dropdown(
            DURATION_OPTIONS,
            label="⏰ 旅行时长",
            value=DEFAULT_DURATION,
            info="选择旅行时长"
        )
        
        mobility = gr.Dropdown(
            MOBILITY_OPTIONS,
            label="🚶 行动能力",
            value=DEFAULT_MOBILITY,
            info="选择您的行动能力"
        )
        
        health_focus = gr.CheckboxGroup(
            choices=HEALTH_FOCUS_OPTIONS,
            value=DEFAULT_HEALTH_FOCUS,
            label="❤️ 健康关注点",
            info="可选择多个您的健康关注点"
        )
        
        btn = gr.Button("📋 制定行程", variant="primary", size="lg")
        
        output = gr.Textbox(
            label="✨ 行程安排",
            lines=15,
            max_lines=25,
            info="为您量身定制的舒缓行程安排"
        )
    
    return {
        'destination': destination,
        'duration': duration,
        'mobility': mobility,
        'health_focus': health_focus,
        'button': btn,
        'output': output
    }


def create_checklist_section() -> Dict[str, Any]:
    """Create the travel checklist section."""
    with gr.Column():
        header = gr.HTML('''
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 30px; border-radius: 15px; margin-bottom: 20px; text-align: center;">
            <h2 style="margin: 0; font-size: 32px;">🎁 旅行清单</h2>
            <p style="margin: 10px 0 0 0; font-size: 16px;">生成专属的行前准备清单，让旅行更轻松</p>
        </div>
        ''')
        
        info_box = gr.HTML('''
        <div style="padding: 20px; background: #e3f2fd; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #2196f3;">
            <p style="color: #1565c0; font-size: 15px; margin: 0; line-height: 1.8;">
                💡 <strong>智能填充：</strong>如果您刚完成行程规划，清单生成时会自动使用您刚才填写的目的地和时长信息！
            </p>
        </div>
        ''')
        
        with gr.Row():
            with gr.Column(scale=1):
                origin = gr.Textbox(
                    label="🏠 出发地",
                    value="",
                    info="填写您的出发城市（例如：北京、上海、广州等）"
                )
                
                destination = gr.Textbox(
                    label="📍 目的地",
                    value="",
                    placeholder="（例如：北京、普陀山、杭州等）",
                    info="填写目的地"
                )
            
            with gr.Column(scale=1):
                duration = gr.Dropdown(
                    DURATION_OPTIONS,
                    label="⏰ 旅行时长",
                    value=DEFAULT_DURATION,
                    info="选择旅行时长"
                )
                
                needs = gr.Textbox(
                    label="⚕️ 特殊需求",
                    value="身体健康，常规旅行",
                    info="例如：高血压、糖尿病、需携带医疗器械等"
                )
        
        loading_output = gr.HTML(value="")
        btn = gr.Button("🎯 生成专属清单", variant="primary", size="lg")
        checklist_output = gr.HTML(
            label="✨ 清单内容",
            value=LOADING_HTML
        )
    
    return {
        'origin': origin,
        'destination': destination,
        'duration': duration,
        'needs': needs,
        'loading_output': loading_output,
        'button': btn,
        'output': checklist_output
    }


def create_footer() -> gr.HTML:
    """Create the application footer."""
    return gr.HTML('''
    <div style="text-align:center; margin-top:30px; padding:20px; background:#f5f5f5; border-radius:10px;">
        <p style="color:#666; font-size:14px;">
            💡 温馨提示：此应用为AI生成内容，仅供参考。具体行程请结合自身实际情况调整。<br/>
            🏥 建议出行前咨询医生，携带必要药品，关注目的地医疗资源。
        </p>
    </div>
    ''')


def create_loading_animation() -> str:
    """Create loading animation HTML."""
    return """
    <script>
        (function() {
            // 移除可能存在的旧遮罩
            const oldOverlay = document.getElementById('app_loading_overlay');
            if (oldOverlay) {
                oldOverlay.remove();
            }

            // 创建新的全屏遮罩，直接插入到body
            const overlay = document.createElement('div');
            overlay.id = 'app_loading_overlay';
            overlay.innerHTML = `
                <div style="
                    position: fixed !important;
                    top: 0 !important;
                    left: 0 !important;
                    width: 100vw !important;
                    height: 100vh !important;
                    min-height: 100vh !important;
                    background-color: rgba(0,0,0,0.85) !important;
                    z-index: 2147483647 !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    animation: fadeIn 0.3s ease-in;
                    pointer-events: all !important;
                ">
                    <div style="
                        background: white;
                        padding: 80px 100px !important;
                        border-radius: 25px;
                        text-align: center;
                        box-shadow: 0 15px 60px rgba(0,0,0,0.7);
                        animation: pulse 2s ease-in-out infinite;
                        max-width: 700px !important;
                        margin: 40px;
                    ">
                        <div style="
                            width: 120px !important;
                            height: 120px !important;
                            margin: 0 auto 40px;
                            border: 10px solid #f0f0f0;
                            border-top: 10px solid #667eea;
                            border-radius: 50%;
                            animation: spin 1s linear infinite;
                        "></div>
                        <h2 style="
                            font-size: 36px !important;
                            color: #333;
                            margin: 0 0 20px 0;
                            font-weight: bold;
                        ">正在生成专属清单</h2>
                        <p style="
                            font-size: 22px !important;
                            color: #666;
                            margin: 0;
                            line-height: 1.6;
                        ">AI正在为您精心准备，请稍候...</p>
                    </div>
                    <style>
                        @keyframes spin {
                            0% { transform: rotate(0deg); }
                            100% { transform: rotate(360deg); }
                        }
                        @keyframes pulse {
                            0%, 100% { transform: scale(1); }
                            50% { transform: scale(1.05); }
                        }
                        @keyframes fadeIn {
                            from { opacity: 0; }
                            to { opacity: 1; }
                        }
                        #app_loading_overlay {
                            position: fixed !important;
                            top: 0 !important;
                            left: 0 !important;
                            width: 100vw !important;
                            height: 100vh !important;
                            z-index: 2147483647 !important;
                        }
                    </style>
                </div>
            `;
            document.body.appendChild(overlay);
        })();
    </script>
    """


def hide_loading_animation() -> str:
    """Create script to hide loading animation."""
    return """
    <script>
        (function() {
            const overlay = document.getElementById('app_loading_overlay');
            if (overlay) {
                overlay.remove();
            }
        })();
    </script>
    """


def create_video_editor_section() -> Dict[str, Any]:
    """Create the video editor section."""
    with gr.Column(scale=1):
        header = gr.HTML('''
        <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); color: white; padding: 25px; border-radius: 15px; margin-bottom: 20px; text-align: center;">
            <h2 style="margin: 0; font-size: 32px;">🎬 视频制作</h2>
            <p style="margin: 10px 0 0 0; font-size: 16px;">将您的旅行照片制作成精美的视频</p>
        </div>
        ''')
        
        # Image upload section
        images_input = gr.Files(
            label="📷 上传图片",
            file_types=[".jpg", ".jpeg", ".png", ".gif"]
        )
        
        # Audio upload section
        audio_input = gr.File(
            label="🎵 上传音频（可选）",
            file_types=[".mp3", ".wav", ".ogg"]
        )
        
        # Video settings
        with gr.Row(): 
            fps = gr.Slider(
                minimum=10, 
                maximum=60, 
                value=24, 
                step=1,
                label="🎞️ 帧率 (FPS)"
            )
            
            duration_per_image = gr.Slider(
                minimum=0.5, 
                maximum=10.0, 
                value=3.0, 
                step=0.1,
                label="⏱️ 每张图片显示时长 (秒)"
            )
        
        with gr.Row(): 
            transition_duration = gr.Slider(
                minimum=0.1, 
                maximum=2.0, 
                value=0.5, 
                step=0.1,
                label="🔄 转场时长 (秒)"
            )
            
            animation_type = gr.Dropdown(
                choices=["fade", "zoom", "pan"],
                value="fade",
                label="✨ 动画效果"
            )
        
        # Action buttons
        btn = gr.Button("🎬 生成视频", variant="primary", size="lg")
        
        # Loading and output sections
        loading_output = gr.HTML(value="")
        
        result_message = gr.Textbox(
            label="📝 处理结果",
            lines=2
        )
        
        # Video output - 优化显示尺寸，适合电脑观看
        video_output = gr.Video(
            label="🎥 生成的视频",
            height=480,  # 降低显示高度，适合电脑屏幕
            width=270,   # 保持9:16比例，270x480
            format="mp4"
        )
        
        # Download button
        download_button = gr.Button(
            "💾 下载视频", 
            variant="secondary", 
            size="lg"
        )
        
    return {
        'images_input': images_input,
        'audio_input': audio_input,
        'fps': fps,
        'duration_per_image': duration_per_image,
        'transition_duration': transition_duration,
        'animation_type': animation_type,
        'button': btn,
        'loading_output': loading_output,
        'result_message': result_message,
        'video_output': video_output,
        'download_button': download_button
    }

def create_app_theme() -> gr.themes.Soft:
    """Create the application theme."""
    return gr.themes.Soft(primary_hue=THEME_PRIMARY, secondary_hue=THEME_SECONDARY)