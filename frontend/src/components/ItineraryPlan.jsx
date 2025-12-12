import React, { useState } from 'react'

function ItineraryPlan() {
  const [destination, setDestination] = useState('')
  const [duration, setDuration] = useState('一周左右')
  const [mobility, setMobility] = useState('行走自如')
  const [healthFocus, setHealthFocus] = useState(['避免过度疲劳', '饮食清淡', '定期休息'])
  const [itinerary, setItinerary] = useState('')
  const [loading, setLoading] = useState(false)

  const durationOptions = ['3-5天', '一周左右', '10-15天', '15天以上']
  const mobilityOptions = ['行走自如', '需要少量休息', '需要轮椅辅助']
  const healthFocusOptions = [
    '避免过度疲劳', '饮食清淡', '需要靠近医院', '避免高原地区',
    '需要无障碍设施', '避免长时间步行', '注意防晒', '避免潮湿环境',
    '需要安静环境', '控制血压', '控制血糖', '关注空气质量',
    '需要携带药物', '保护心脏', '保持关节灵活', '预防感冒',
    '避免拥挤', '需要良好睡眠', '避免剧烈运动', '注意保暖',
    '多喝水', '定期休息', '避免暴晒', '饮食规律', '适度活动'
  ]

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const response = await fetch('/api/generate-itinerary', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ destination, duration, mobility, health_focus: healthFocus }),
      })
      const data = await response.json()
      setItinerary(data.result)
    } catch (error) {
      console.error('Error generating itinerary:', error)
      setItinerary('抱歉，生成行程时出现了错误。')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="itinerary-section">
      <div style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', padding: '25px', borderRadius: '15px', marginBottom: '20px', textAlign: 'center' }}>
        <h2 style={{ margin: 0, fontSize: '32px' }}>📋 行程规划</h2>
        <p style={{ margin: '10px 0 0 0', fontSize: '16px' }}>根据您的需求智能生成详细的旅行行程</p>
      </div>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label style={{ fontSize: '18px', marginBottom: '10px', display: 'block', textAlign: 'left' }}>🏝️ 目的地</label>
          <input 
            type="text" 
            value={destination} 
            onChange={(e) => setDestination(e.target.value)}
            placeholder="请输入旅行目的地" 
            style={{ width: '100%', padding: '12px', fontSize: '16px', borderRadius: '10px', border: '1px solid #ddd', marginBottom: '20px' }}
            required
          />
        </div>
        <div className="form-group">
          <label style={{ fontSize: '18px', marginBottom: '10px', display: 'block', textAlign: 'left' }}>⏱️ 旅行时长</label>
          <select 
            value={duration} 
            onChange={(e) => setDuration(e.target.value)}
            style={{ width: '100%', padding: '12px', fontSize: '16px', borderRadius: '10px', border: '1px solid #ddd', marginBottom: '20px' }}
          >
            {durationOptions.map((option) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label style={{ fontSize: '18px', marginBottom: '10px', display: 'block', textAlign: 'left' }}>🚶 行动能力</label>
          <select 
            value={mobility} 
            onChange={(e) => setMobility(e.target.value)}
            style={{ width: '100%', padding: '12px', fontSize: '16px', borderRadius: '10px', border: '1px solid #ddd', marginBottom: '20px' }}
          >
            {mobilityOptions.map((option) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label style={{ fontSize: '18px', marginBottom: '10px', display: 'block', textAlign: 'left' }}>🏥 健康关注点</label>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '10px', marginBottom: '20px' }}>
            {healthFocusOptions.map((option) => (
              <div key={option} style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <input 
                  type="checkbox" 
                  id={option} 
                  value={option} 
                  checked={healthFocus.includes(option)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setHealthFocus([...healthFocus, option])
                    } else {
                      setHealthFocus(healthFocus.filter((item) => item !== option))
                    }
                  }}
                  style={{ width: '20px', height: '20px', cursor: 'pointer' }}
                />
                <label htmlFor={option} style={{ cursor: 'pointer' }}>{option}</label>
              </div>
            ))}
          </div>
        </div>
        <button 
          type="submit" 
          disabled={loading}
          style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', border: 'none', padding: '15px 30px', fontSize: '18px', borderRadius: '10px', cursor: 'pointer', transition: 'all 0.3s ease' }}
        >
          {loading ? '📋 生成行程中...' : '📋 生成行程'}
        </button>
      </form>
      {itinerary && (
        <div style={{ marginTop: '30px' }}>
          <label style={{ fontSize: '18px', marginBottom: '10px', display: 'block', textAlign: 'left' }}>📋 行程结果</label>
          <textarea 
            value={itinerary} 
            readOnly 
            style={{ width: '100%', padding: '20px', fontSize: '16px', borderRadius: '10px', border: '1px solid #ddd', minHeight: '300px', resize: 'vertical' }}
          />
        </div>
      )}
    </div>
  )
}

export default ItineraryPlan