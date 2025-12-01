"""
Main application entry point for the travel assistant.
This module creates and launches the Gradio application.
"""

import gradio as gr
import os
import tempfile
import shutil
from typing import Optional, Dict, Any, List

# Import modules
try:
    from .config.config import APP_TITLE, APP_DESCRIPTION, CUSTOM_CSS
    from .core.travel_functions import (
        generate_destination_recommendation,
        generate_itinerary_plan,
        generate_checklist
    )
    from .core.video_editor import create_video_from_images, validate_media_files
    from .ui.components import (
        create_app_theme,
        create_header,
        create_destination_section,
        create_itinerary_section,
        create_checklist_section,
        create_video_editor_section,
        create_footer,
        create_loading_animation,
        hide_loading_animation
    )
    from .utils.helpers import extract_hotels_from_itinerary
except ImportError:
    from config.config import APP_TITLE, APP_DESCRIPTION, CUSTOM_CSS
    from core.travel_functions import (
        generate_destination_recommendation,
        generate_itinerary_plan,
        generate_checklist
    )
    from core.video_editor import create_video_from_images, validate_media_files
    from ui.components import (
        create_app_theme,
        create_header,
        create_destination_section,
        create_itinerary_section,
        create_checklist_section,
        create_video_editor_section,
        create_footer,
        create_loading_animation,
        hide_loading_animation
    )
    from utils.helpers import extract_hotels_from_itinerary


def create_app() -> gr.Blocks:
    """
    Create the main Gradio application.
    
    Returns:
        gr.Blocks: The configured Gradio application
    """
    theme = create_app_theme()
    
    with gr.Blocks(
        title=APP_TITLE,
        css=CUSTOM_CSS,
        theme=theme,
        head=["<meta name='viewport' content='width=device-width, initial-scale=1.0'>"]
    ) as app:
        
        # Create header
        create_header()
        
        # State variables for sharing data between tabs
        itinerary_state = gr.State("")  # Store itinerary content
        destination_state = gr.State("")  # Store destination for sharing
        duration_state = gr.State("")  # Store duration for sharing
        video_output_state = gr.State("")  # Store video output path
        
        with gr.Tab("🌟 目的地推荐"):
            destination_section = create_destination_section()
            
            # Bind destination recommendation events
            destination_section['button'].click(
                fn=generate_destination_recommendation,
                inputs=[
                    destination_section['season'],
                    destination_section['health'],
                    destination_section['budget'],
                    destination_section['interests']
                ],
                outputs=destination_section['output']
            )
        
        with gr.Tab("📋 行程规划"):
            itinerary_section = create_itinerary_section()
            
            # Bind itinerary planning events - store result in state
            def generate_itinerary_with_state(destination, duration, mobility, health_focus):
                """Generate itinerary and store it in state for checklist sharing."""
                result = generate_itinerary_plan(destination, duration, mobility, health_focus)
                return result, result, destination, duration  # Return itinerary, state updates, and shared values
            
            itinerary_section['button'].click(
                fn=generate_itinerary_with_state,
                inputs=[
                    itinerary_section['destination'],
                    itinerary_section['duration'],
                    itinerary_section['mobility'],
                    itinerary_section['health_focus']
                ],
                outputs=[
                    itinerary_section['output'],
                    itinerary_state,
                    destination_state,
                    duration_state
                ]
            )
        
        with gr.Tab("🎁 旅行清单"):
            checklist_section = create_checklist_section()
            
            # Auto-fill destination and duration when itinerary is generated
            def auto_fill_checklist_fields(shared_destination, shared_duration):
                """Auto-fill checklist fields with shared values from itinerary."""
                return shared_destination, shared_duration
            
            # Connect state changes to auto-fill checklist fields
            destination_state.change(
                fn=auto_fill_checklist_fields,
                inputs=[destination_state, duration_state],
                outputs=[
                    checklist_section['destination'],
                    checklist_section['duration']
                ]
            )
            
            duration_state.change(
                fn=auto_fill_checklist_fields,
                inputs=[destination_state, duration_state],
                outputs=[
                    checklist_section['destination'],
                    checklist_section['duration']
                ]
            )
            
            # Bind checklist generation events - use itinerary state
            def generate_checklist_with_itinerary(origin, destination, duration, needs, itinerary_content):
                """Generate checklist with itinerary context."""
                # Extract hotels from itinerary if available
                hotels = extract_hotels_from_itinerary(itinerary_content)
                
                # Build enhanced special needs with hotel information
                enhanced_needs = needs
                if hotels:
                    hotel_info = f"行程规划中提到的酒店：{', '.join(hotels)}"
                    enhanced_needs = f"{needs}\n{hotel_info}" if needs else hotel_info
                
                # Generate checklist and return both loading and output components
                checklist_result = generate_checklist(origin, destination, duration, enhanced_needs, itinerary_content)
                return create_loading_animation(), checklist_result
            
            checklist_section['button'].click(
                fn=generate_checklist_with_itinerary,
                inputs=[
                    checklist_section['origin'],
                    checklist_section['destination'],
                    checklist_section['duration'],
                    checklist_section['needs'],
                    itinerary_state
                ],
                outputs=[
                    checklist_section['loading_output'],
                    checklist_section['output']
                ]
            ).then(
                fn=lambda: hide_loading_animation(),
                outputs=checklist_section['loading_output']
            )
        
        with gr.Tab("🎬 视频制作"):
            video_section = create_video_editor_section()
            
            # Bind video generation events
            def generate_video(images, audio, fps, duration_per_image, transition_duration, animation_type):
                try:
                    # Validate inputs
                    if not images:
                        return "", "请至少上传一张图片", None, ""
                    
                    # Convert Gradio File objects to paths
                    image_paths = [img.name for img in images]
                    audio_path = audio.name if audio else None
                    
                    # Create video - 使用适合手机的9:16竖屏比例
                    video_path = create_video_from_images(
                        image_paths,
                        audio_path,
                        fps,
                        duration_per_image,
                        transition_duration,
                        animation_type,
                        target_width=720,
                        target_height=1280  # 9:16 竖屏比例，适合手机播放
                    )
                    
                    return "", f"视频生成成功！", video_path, video_path
                    
                except Exception as e:
                    error_msg = f"视频生成失败: {str(e)}"
                    return "", error_msg, None, ""
            
            video_section['button'].click(
                fn=generate_video,
                inputs=[
                    video_section['images_input'],
                    video_section['audio_input'],
                    video_section['fps'],
                    video_section['duration_per_image'],
                    video_section['transition_duration'],
                    video_section['animation_type']
                ],
                outputs=[
                    video_section['loading_output'],
                    video_section['result_message'],
                    video_section['video_output'],
                    video_output_state
                ]
            )
            
            # Bind download event
            def handle_download(video_path):
                if not video_path or not os.path.exists(video_path):
                    return None
                
                try:
                    # Create a temporary file for download
                    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False, dir=tempfile.gettempdir()) as tmp:
                        download_path = tmp.name
                    
                    # Copy file to ensure permissions are correct
                    shutil.copy2(video_path, download_path)
                    
                    # Return the file object for download
                    return gr.File(value=download_path, label="旅行视频.mp4")
                except Exception as e:
                    print(f"下载视频时出错: {str(e)}")
                    return None
            
            video_section['download_button'].click(
                fn=handle_download,
                inputs=[video_output_state],
                outputs=[gr.File(label="下载视频")]
            )
        
        # Create footer
        create_footer()
        
        return app


def main():
    """Main function to launch the application."""
    # Create the application
    app = create_app()
    
    # Launch the application
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True,
        debug=False
    )


if __name__ == "__main__":
    main()