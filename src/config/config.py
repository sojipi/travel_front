"""
Configuration module for the travel assistant application.
Contains all configuration constants and settings.
"""

import os
from typing import List, Dict

# API Configuration
API_KEY = os.getenv("MODEL_API_KEY", "")
API_BASE = "https://api-inference.modelscope.cn/v1/"
MODEL_NAME = "deepseek-ai/DeepSeek-V3.2"
MAX_TOKENS = 4096
TEMPERATURE = 0.7

# ModelScope API Configuration
MODELSCOPE_API_KEY = os.getenv("MODELSCOPE_API_KEY", "") or API_KEY
MODELSCOPE_BASE_URL = "https://api-inference.modelscope.cn/v1/"
QWEN_MODEL_NAME = "Qwen/Qwen3-VL-8B-Instruct"
DEEPSEEK_MODEL_NAME = "deepseek-ai/DeepSeek-V3.2"

# Application Settings
APP_TITLE = "🧳 银发族智能旅行助手"
APP_DESCRIPTION = "专为中老年朋友设计的温暖贴心的旅行规划伙伴"
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 7860

# UI Configuration
THEME_PRIMARY = "purple"
THEME_SECONDARY = "cyan"

# Interest and Health Options
INTEREST_OPTIONS = [
    "避寒康养", "海岛度假", "文化历史", "温泉养生", "自然风光",
    "美食体验", "摄影采风", "休闲购物", "传统建筑", "民俗体验",
    "慢节奏游", "海滨漫步", "茶文化", "寺庙祈福", "古镇风情",
    "田园风光", "动物观赏", "艺术展览", "传统戏曲", "手工体验",
    "健康养生", "中医理疗", "瑜伽冥想", "森林浴", "阳光浴"
]

HEALTH_FOCUS_OPTIONS = [
    "避免过度疲劳", "饮食清淡", "需要靠近医院", "避免高原地区",
    "需要无障碍设施", "避免长时间步行", "注意防晒", "避免潮湿环境",
    "需要安静环境", "控制血压", "控制血糖", "关注空气质量",
    "需要携带药物", "保护心脏", "保持关节灵活", "预防感冒",
    "避免拥挤", "需要良好睡眠", "避免剧烈运动", "注意保暖",
    "多喝水", "定期休息", "避免暴晒", "饮食规律", "适度活动"
]

SEASON_OPTIONS = ["春季", "夏季", "秋季", "冬季"]
HEALTH_STATUS_OPTIONS = ["身体健康", "有慢性病但控制良好", "行动不便但可独立出行"]
BUDGET_OPTIONS = ["经济实惠", "舒适型", "豪华型"]
MOBILITY_OPTIONS = ["行走自如", "需要少量休息", "需要轮椅辅助"]
DURATION_OPTIONS = ["3-5天", "一周左右", "10-15天", "15天以上"]

# System Prompts
DESTINATION_SYSTEM_PROMPT = """你是一个专为银发族设计的智能旅行规划助手。你具有以下特点：
1. 温暖贴心：用温暖、耐心的语气与老年朋友交流
2. 专业可靠：基于丰富的旅行知识和经验提供专业建议
3. 细致周到：考虑到老年人的特殊需求和关注点
4. 实用性强：推荐的目的地切实可行，便于实施

请根据用户提供的季节、健康状况、预算范围和兴趣偏好，推荐3-5个适合银发族的国内旅行目的地。

**重要：你必须使用Markdown格式返回内容，包括标题、列表、粗体等Markdown语法。不要使用JSON格式或其他格式。**
"""

ITINERARY_SYSTEM_PROMPT = """你是一个专为银发族设计的智能行程规划助手。你具有以下特点：
1. 节奏舒缓：行程安排张弛有度，避免过度疲劳
2. 安全优先：充分考虑安全因素，避免高风险活动
3. 健康关怀：融入健康元素，如养生、休闲、疗养等
4. 文化体验：注重文化内涵，让旅行更有意义
5. 实用便利：考虑交通、住宿、餐饮的便利性

请根据用户的目的地、旅行时长、行动能力和健康关注点，制定一份详细的、适合银发族的旅行行程计划。

**重要：你必须使用Markdown格式返回内容，包括标题、列表、粗体等Markdown语法。不要使用JSON格式或其他格式。**
"""

CHECKLIST_SYSTEM_PROMPT = """你是一个专为银发族设计的旅行清单助手。你具有以下特点：
1. 细致入微：考虑到老年人旅行的各种细节需求
2. 分类清晰：清单内容条理清晰，便于查阅
3. 实用性强：所有建议都基于实际需求，避免冗余
4. 安全提醒：包含重要的安全注意事项
5. 个性化：根据用户的特殊需求定制清单

请根据用户的出发地、目的地、旅行时长和特殊需求，生成一份详细的、适合银发族的旅行清单。

**重要：你必须返回纯JSON格式的数据，不要包含任何额外的文字说明，不要使用Markdown代码块标记（不要使用```json或```），直接返回JSON数据即可。**
"""

# Default Values
DEFAULT_INTERESTS = ["避寒康养", "温泉养生"]
DEFAULT_HEALTH_FOCUS = ["避免过度疲劳", "饮食清淡", "定期休息"]
DEFAULT_SEASON = "秋季"
DEFAULT_HEALTH_STATUS = "身体健康"
DEFAULT_BUDGET = "舒适型"
DEFAULT_MOBILITY = "行走自如"
DEFAULT_DURATION = "一周左右"

# CSS Styles
CUSTOM_CSS = """
.gr-button {font-size: 18px !important; padding: 12px 20px !important;}
.gr-textbox input {font-size: 16px !important;}
.gr-multiselect {min-height: 120px !important;}
"""

# HTML Templates
LOADING_HTML = """
<div style="padding: 60px 40px; background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); border-radius: 15px; text-align: center; border: 2px dashed #9c27b0;">
    <div style="font-size: 64px; margin-bottom: 20px;">📋</div>
    <h3 style="color: #6a1b9a; margin: 0 0 15px 0; font-size: 24px;">旅行清单尚未生成</h3>
    <p style="color: #7b1fa2; margin: 0; font-size: 16px; line-height: 1.8;">
        填写好目的地、旅行时长和特殊需求后，点击"生成专属清单"按钮<br/>
        AI将为您生成详细的行前准备清单
    </p>
</div>
"""

# Validation Settings
MAX_INPUT_LENGTH = 500
ALLOWED_SEASONS = set(SEASON_OPTIONS)
ALLOWED_HEALTH_STATUS = set(HEALTH_STATUS_OPTIONS)
ALLOWED_BUDGET = set(BUDGET_OPTIONS)
ALLOWED_MOBILITY = set(MOBILITY_OPTIONS)
ALLOWED_DURATION = set(DURATION_OPTIONS)