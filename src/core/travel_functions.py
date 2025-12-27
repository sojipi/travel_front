"""
Core travel functions module for the travel assistant application.
Contains the main business logic for travel planning functionality.
"""

import json
from typing import List, Dict, Any
try:
    from ..api.openai_client import get_client
    from ..utils.helpers import clean_response, validate_inputs, safe_json_parse, format_interests, format_health_focus, is_valid_chinese_location
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from api.openai_client import get_client
    from utils.helpers import clean_response, validate_inputs, safe_json_parse, format_interests, format_health_focus, is_valid_chinese_location


def generate_destination_recommendation(season: str, 
                                       health_status: str, 
                                       budget: str, 
                                       interests: List[str]) -> str:
    """
    Generate destination recommendations based on user preferences.
    
    Args:
        season: Travel season
        health_status: Health status
        budget: Budget range
        interests: List of interests
        
    Returns:
        Formatted destination recommendations
    """
    # Validate inputs
    inputs = {
        'season': season,
        'health_status': health_status,
        'budget': budget
    }
    
    errors = validate_inputs(inputs)
    if errors:
        return f"输入验证失败: {', '.join(errors.values())}"
    
    # Format interests
    interests_str = format_interests(interests)
    
    try:
        client = get_client()
        response = client.generate_destination_recommendations(
            season=season,
            health_status=health_status,
            budget=budget,
            interests=interests_str
        )
        
        return clean_response(response)
        
    except Exception as e:
        return f"抱歉，生成推荐时出现了错误: {str(e)}"


def generate_itinerary_plan(destination: str, 
                           duration: str, 
                           mobility: str, 
                           health_focus: List[str]) -> str:
    """
    Generate a detailed itinerary plan.
    
    Args:
        destination: Travel destination
        duration: Trip duration
        mobility: Mobility status
        health_focus: List of health concerns
        
    Returns:
        Formatted itinerary plan
    """
    # Validate inputs
    inputs = {
        'destination': destination,
        'duration': duration,
        'mobility': mobility
    }
    
    errors = validate_inputs(inputs)
    if errors:
        return f"输入验证失败: {', '.join(errors.values())}"
    
    # Validate destination
    if not is_valid_chinese_location(destination):
        return "请输入有效的中文地名"
    
    # Format health focus
    health_focus_str = format_health_focus(health_focus)
    
    try:
        client = get_client()
        response = client.generate_itinerary_plan(
            destination=destination,
            duration=duration,
            mobility=mobility,
            health_focus=health_focus_str
        )
        
        return clean_response(response)
        
    except Exception as e:
        return f"抱歉，制定行程时出现了错误: {str(e)}"


def generate_checklist(origin: str, 
                      destination: str, 
                      duration: str, 
                      departure_date: str = "",
                      special_needs: str = "",
                      itinerary_text: str = "") -> str:
    """
    Generate a comprehensive travel checklist.
    
    Args:
        origin: Departure location
        destination: Travel destination
        duration: Trip duration
        departure_date: Departure date (optional)
        special_needs: Special requirements
        itinerary_text: Optional itinerary for context
        
    Returns:
        HTML formatted checklist
    """
    # Validate inputs
    inputs = {
        'origin': origin,
        'destination': destination,
        'duration': duration
    }
    
    errors = validate_inputs(inputs)
    if errors:
        return f"输入验证失败: {', '.join(errors.values())}"
    
    # Validate locations
    if not is_valid_chinese_location(origin):
        return "请输入有效的出发地名称"
    
    if not is_valid_chinese_location(destination):
        return "请输入有效的目的地名称"
    
    try:
        client = get_client()
        response = client.generate_checklist(
            origin=origin,
            destination=destination,
            duration=duration,
            departure_date=departure_date,
            special_needs=special_needs,
            itinerary_text=itinerary_text
        )
        
        # Parse JSON response and format as HTML
        checklist_data = safe_json_parse(response)
        if checklist_data:
            return format_checklist_html(checklist_data, departure_date, origin, destination, duration)
        else:
            # Fallback to text formatting
            return format_checklist_text(response)
        
    except Exception as e:
        return f"抱歉，生成清单时出现了错误: {str(e)}"


def format_checklist_html(data: Dict[str, Any], departure_date: str = "", origin: str = "", destination: str = "", duration: str = "") -> str:
    """
    Format checklist data as HTML.
    
    Args:
        data: Parsed checklist data
        departure_date: Departure date
        origin: Departure location
        destination: Travel destination
        duration: Trip duration
        
    Returns:
        HTML formatted checklist
    """
    # Generate booking dates based on departure date and duration
    booking_dates = generate_booking_dates(departure_date, duration)
    
    trip_info = ""
    if origin or destination:
        trip_info = f"<p style='color: #95a5a6; font-size: 14px; margin: 5px 0;'>"
        if origin and destination:
            trip_info += f"{origin} → {destination}"
        if duration:
            trip_info += f" | {duration}"
        if departure_date:
            trip_info += f" | 出发：{departure_date}"
        trip_info += "</p>"
    
    html = f"""
    <div style="font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif; max-width: 800px; margin: 0 auto; background: #fafafa; padding: 20px; border-radius: 15px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #2c3e50; font-size: 32px; margin-bottom: 10px;">🎁 专属旅行清单</h1>
            <p style="color: #7f8c8d; font-size: 16px;">为您的旅行做好充分准备</p>
            {trip_info}
        </div>
    """
    
    # Document checklist
    documents = data.get("documents", [])
    if documents:
        html += create_checklist_section("📄 证件类", documents, "#e8f4fd", "#2980b9")
    
    # Clothing checklist
    clothing = data.get("clothing", [])
    if clothing:
        html += create_checklist_section("👕 衣物类", clothing, "#fef9e7", "#f39c12")
    
    # Medications checklist
    medications = data.get("medications", [])
    if medications:
        html += create_checklist_section("💊 药品类", medications, "#ffe6e6", "#e74c3c")
    
    # Daily items checklist
    daily_items = data.get("daily_items", [])
    if daily_items:
        html += create_checklist_section("🧴 生活用品类", daily_items, "#e8f8f5", "#27ae60")
    
    # Electronics checklist
    electronics = data.get("electronics", [])
    if electronics:
        html += create_checklist_section("📱 电子设备类", electronics, "#f0f3f4", "#95a5a6")
    
    # Financial checklist
    financial = data.get("financial", [])
    if financial:
        html += create_checklist_section("💰 财务准备", financial, "#eafaf1", "#2ecc71")
    
    # Safety checklist
    safety = data.get("safety", [])
    if safety:
        html += create_checklist_section("🛡️ 安全用品", safety, "#fadbd8", "#c0392b")
    
    # Entertainment checklist
    entertainment = data.get("entertainment", [])
    if entertainment:
        html += create_checklist_section("🎮 娱乐用品", entertainment, "#e8daef", "#8e44ad")
    
    # Special items checklist
    special_items = data.get("special_items", [])
    if special_items:
        html += create_checklist_section("⭐ 特殊用品", special_items, "#fdedec", "#e91e63")
    
    # Booking guides with dates - always show if we have dates
    booking_guides = data.get("booking_guides", {})
    if booking_dates.get('departure_date') or booking_guides:
        html += create_booking_guides_section(booking_guides, booking_dates)
    
    # Tips
    tips = data.get("tips", [])
    if tips:
        html += create_tips_section(tips)
    
    # Footer
    html += """
        <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; text-align: center; color: #666; font-size: 13px; margin-top: 20px;">
            <p style="margin: 5px 0;">💡 此清单仅供参考，请根据实际情况调整</p>
        </div>
    </div>
    """
    
    return html


def create_checklist_section(title: str, items: List[str], bg_color: str, title_color: str) -> str:
    """Create a checklist section HTML."""
    html = f"""
    <div style="background: {bg_color}; padding: 20px; border-radius: 10px; margin-bottom: 15px; border-left: 5px solid {title_color};">
        <h3 style="margin: 0 0 15px 0; color: {title_color}; font-size: 20px;">{title}</h3>
        <ul style="margin: 0; padding-left: 20px; color: #555;">
    """
    
    for item in items:
        html += f'<li style="margin-bottom: 8px; line-height: 1.6;">{item}</li>'
    
    html += """
        </ul>
    </div>
    """
    
    return html


def create_booking_guides_section(booking_guides: Dict[str, Any], booking_dates: Dict[str, str]) -> str:
    """Create booking guides section HTML."""
    html = """
    <div style="background: #fff3e0; padding: 20px; border-radius: 10px; margin-bottom: 15px; border-left: 5px solid #e65100;">
        <h3 style="margin: 0 0 15px 0; color: #e65100; font-size: 20px;">🎫 预订指南</h3>
    """
    
    # Add date information
    if booking_dates.get('departure_date'):
        html += f"""
        <div style="background: #ffe8cc; padding: 12px; border-radius: 6px; margin-bottom: 15px;">
            <p style="margin: 5px 0; color: #e65100; font-size: 15px; font-weight: 500;">
                📅 出发日期：<strong>{booking_dates['departure_date']}</strong>
            </p>
            <p style="margin: 5px 0; color: #666; font-size: 14px;">
                🏠 住宿日期：{booking_dates['check_in_date']} 至 {booking_dates['check_out_date']}
            </p>
        </div>
        """
    
    # Display booking guides if available
    if booking_guides and len(booking_guides) > 0:
        for category, info in booking_guides.items():
            if isinstance(info, dict):
                html += f'<h4 style="color: #f57c00; margin: 10px 0 5px 0;">{info.get("title", category)}</h4>'
                
                platforms = info.get('platforms', [])
                if platforms:
                    html += '<ul style="margin: 5px 0; padding-left: 20px; color: #555;">'
                    for platform in platforms:
                        html += f'<li style="margin-bottom: 5px;">{platform}</li>'
                    html += '</ul>'
                
                notes = info.get('notes', [])
                if notes:
                    html += '<ul style="margin: 5px 0; padding-left: 20px; color: #666;">'
                    for note in notes:
                        html += f'<li style="margin-bottom: 5px;">{note}</li>'
                    html += '</ul>'
    else:
        # Default booking guides if AI doesn't provide
        html += """
        <div style="background: #fff; padding: 15px; border-radius: 6px; margin-top: 10px;">
            <h4 style="color: #f57c00; margin: 10px 0 5px 0;">✈️ 机票/火车票预订</h4>
            <ul style="margin: 5px 0; padding-left: 20px; color: #555;">
                <li style="margin-bottom: 5px;">推荐平台：12306（铁路）、携程、去哪儿、飞猪、同程</li>
                <li style="margin-bottom: 5px;">预订时间：提前7-15天预订优惠更大</li>
                <li style="margin-bottom: 5px;">注意事项：确认出行日期和证件有效期，保留电子票据</li>
            </ul>
            
            <h4 style="color: #f57c00; margin: 10px 0 5px 0;">🏨 酒店预订</h4>
            <ul style="margin: 5px 0; padding-left: 20px; color: #555;">
                <li style="margin-bottom: 5px;">推荐平台：携程、美团、飞猪、去哪儿、Booking</li>
                <li style="margin-bottom: 5px;">预订建议：选择靠近景点或市中心的酒店，考虑无障碍设施</li>
                <li style="margin-bottom: 5px;">注意事项：确认入住和退房时间，查看取消政策</li>
            </ul>
            
            <h4 style="color: #f57c00; margin: 10px 0 5px 0;">🎟️ 景点门票</h4>
            <ul style="margin: 5px 0; padding-left: 20px; color: #555;">
                <li style="margin-bottom: 5px;">推荐平台：携程、美团、同程、景区官网</li>
                <li style="margin-bottom: 5px;">提前购票：提前1-3天预订热门景点门票，避免排队</li>
                <li style="margin-bottom: 5px;">优惠政策：老年证、学生证、军人证可能有优惠</li>
            </ul>
        </div>
        """
    
    html += """
    </div>
    """
    
    return html


def generate_booking_dates(departure_date: str, duration: str) -> Dict[str, str]:
    """
    Generate booking dates based on departure date and duration.
    
    Args:
        departure_date: Departure date in YYYY-MM-DD format
        duration: Trip duration (e.g., '3-5天', '一周左右', '10-15天', '15天以上')
        
    Returns:
        Dictionary containing booking dates
    """
    if not departure_date:
        return {
            'departure_date': '',
            'check_in_date': '',
            'check_out_date': '',
            'estimated_days': 7
        }
    
    try:
        from datetime import datetime, timedelta
        
        # Parse departure date
        dep_date = datetime.strptime(departure_date, '%Y-%m-%d')
        
        # Estimate number of days based on duration
        duration_map = {
            '3-5天': 4,
            '一周左右': 7,
            '10-15天': 12,
            '15天以上': 15
        }
        estimated_days = duration_map.get(duration, 7)
        
        # Calculate check-in and check-out dates
        check_in = dep_date
        check_out = dep_date + timedelta(days=estimated_days)
        
        # Format dates
        dep_date_str = dep_date.strftime('%Y年%m月%d日')
        check_in_str = check_in.strftime('%Y年%m月%d日')
        check_out_str = check_out.strftime('%Y年%m月%d日')
        
        return {
            'departure_date': dep_date_str,
            'check_in_date': check_in_str,
            'check_out_date': check_out_str,
            'estimated_days': estimated_days
        }
    except Exception:
        return {
            'departure_date': departure_date,
            'check_in_date': '',
            'check_out_date': '',
            'estimated_days': 7
        }


def create_tips_section(tips: List[str]) -> str:
    """Create tips section HTML."""
    html = """
    <div style="background: #fff3e0; padding: 20px; border-radius: 10px; margin-bottom: 15px; border-left: 5px solid #e65100;">
        <h3 style="margin: 0 0 15px 0; color: #e65100; font-size: 20px;">💡 温馨提示</h3>
    """
    
    for tip in tips:
        html += f'<p style="margin: 8px 0; color: #555; line-height: 1.6;">• {tip}</p>'
    
    html += """
    </div>
    """
    
    return html


def format_checklist_text(response: str) -> str:
    """
    Fallback text formatting for checklist.
    
    Args:
        response: Raw response text
        
    Returns:
        Basic HTML formatted text
    """
    return f"""
    <div style="font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif; max-width: 800px; margin: 0 auto; background: #fafafa; padding: 20px; border-radius: 15px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #2c3e50; font-size: 32px; margin-bottom: 10px;">🎁 旅行清单</h1>
            <p style="color: #7f8c8d; font-size: 16px;">为您的旅行做好充分准备</p>
        </div>
        
        <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #ddd;">
            <pre style="white-space: pre-wrap; font-family: inherit; margin: 0; color: #555; line-height: 1.6;">{clean_response(response)}</pre>
        </div>
        
        <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; text-align: center; color: #666; font-size: 13px; margin-top: 20px;">
            <p style="margin: 5px 0;">💡 此清单仅供参考，请根据实际情况调整</p>
        </div>
    </div>
    """