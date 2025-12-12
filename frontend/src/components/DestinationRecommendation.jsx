import React, { useState } from 'react'

function DestinationRecommendation() {
  const [season, setSeason] = useState('秋季')
  const [healthStatus, setHealthStatus] = useState('身体健康')
  const [budget, setBudget] = useState('舒适型')
  const [interests, setInterests] = useState(['避寒康养', '温泉养生'])
  const [recommendation, setRecommendation] = useState('')
  const [loading, setLoading] = useState(false)

  const seasonOptions = ['春季', '夏季', '秋季', '冬季']
  const healthStatusOptions = ['身体健康', '有慢性病但控制良好', '行动不便但可独立出行']
  const budgetOptions = ['经济实惠', '舒适型', '豪华型']
  const interestOptions = [
    '避寒康养', '海岛度假', '文化历史', '温泉养生', '自然风光',
    '美食体验', '摄影采风', '休闲购物', '传统建筑', '民俗体验',
    '慢节奏游', '海滨漫步', '茶文化', '寺庙祈福', '古镇风情',
    '田园风光', '动物观赏', '艺术展览', '传统戏曲', '手工体验',
    '健康养生', '中医理疗', '瑜伽冥想', '森林浴', '阳光浴'
  ]

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const response = await fetch('/api/recommend-destinations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ season, health: healthStatus, budget, interests }),
      })
      const data = await response.json()
      setRecommendation(data.result)
    } catch (error) {
      console.error('Error generating destination:', error)
      setRecommendation('抱歉，生成推荐时出现了错误。')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="destination-section">
      <div style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', padding: '25px', borderRadius: '15px', marginBottom: '20px', textAlign: 'center' }}>
        <h2 style={{ margin: 0, fontSize: '32px' }}>🌟 目的地推荐</h2>
        <p style={{ margin: '10px 0 0 0', fontSize: '16px' }}>根据您的需求智能推荐适合的旅行目的地</p>
      </div>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label style={{ fontSize: '18px', marginBottom: '10px', display: 'block', textAlign: 'left' }}>🌸 季节</label>
          <select 
            value={season} 
            onChange={(e) => setSeason(e.target.value)}
            style={{ width: '100%', padding: '12px', fontSize: '16px', borderRadius: '10px', border: '1px solid #ddd', marginBottom: '20px' }}
          >
            {seasonOptions.map((option) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label style={{ fontSize: '18px', marginBottom: '10px', display: 'block', textAlign: 'left' }}>🏥 健康状况</label>
          <select 
            value={healthStatus} 
            onChange={(e) => setHealthStatus(e.target.value)}
            style={{ width: '100%', padding: '12px', fontSize: '16px', borderRadius: '10px', border: '1px solid #ddd', marginBottom: '20px' }}
          >
            {healthStatusOptions.map((option) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label style={{ fontSize: '18px', marginBottom: '10px', display: 'block', textAlign: 'left' }}>💰 预算范围</label>
          <select 
            value={budget} 
            onChange={(e) => setBudget(e.target.value)}
            style={{ width: '100%', padding: '12px', fontSize: '16px', borderRadius: '10px', border: '1px solid #ddd', marginBottom: '20px' }}
          >
            {budgetOptions.map((option) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label style={{ fontSize: '18px', marginBottom: '10px', display: 'block', textAlign: 'left' }}>🎨 兴趣偏好</label>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '10px', marginBottom: '20px' }}>
            {interestOptions.map((option) => (
              <div key={option} style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <input 
                  type="checkbox" 
                  id={option} 
                  value={option} 
                  checked={interests.includes(option)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setInterests([...interests, option])
                    } else {
                      setInterests(interests.filter((item) => item !== option))
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
          {loading ? '🔍 生成推荐中...' : '🔍 推荐目的地'}
        </button>
      </form>
      {recommendation && (
        <div style={{ marginTop: '30px' }}>
          <label style={{ fontSize: '18px', marginBottom: '10px', display: 'block', textAlign: 'left' }}>✨ 推荐结果</label>
          <textarea 
            value={recommendation} 
            readOnly 
            style={{ width: '100%', padding: '20px', fontSize: '16px', borderRadius: '10px', border: '1px solid #ddd', minHeight: '300px', resize: 'vertical' }}
          />
        </div>
      )}
    </div>
  )
}

export default DestinationRecommendation