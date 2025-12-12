import React, { useState } from 'react'

function TravelChecklist() {
  const [origin, setOrigin] = useState('')
  const [destination, setDestination] = useState('')
  const [duration, setDuration] = useState('一周左右')
  const [needs, setNeeds] = useState('')
  const [itinerary, setItinerary] = useState('')
  const [checklist, setChecklist] = useState('')
  const [loading, setLoading] = useState(false)

  const durationOptions = ['3-5天', '一周左右', '10-15天', '15天以上']

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const response = await fetch('/api/generate-checklist', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ origin, destination, duration, needs, itinerary_content: itinerary }),
      })
      const data = await response.json()
      setChecklist(data.result)
    } catch (error) {
      console.error('Error generating checklist:', error)
      setChecklist('抱歉，生成清单时出现了错误。')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="checklist-section">
      <div style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', padding: '25px', borderRadius: '15px', marginBottom: '20px', textAlign: 'center' }}>
        <h2 style={{ margin: 0, fontSize: '32px' }}>🎁 旅行清单</h2>
        <p style={{ margin: '10px 0 0 0', fontSize: '16px' }}>根据您的需求生成详细的旅行清单</p>
      </div>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label style={{ fontSize: '18px', marginBottom: '10px', display: 'block', textAlign: 'left' }}>🏠 出发地</label>
          <input 
            type="text" 
            value={origin} 
            onChange={(e) => setOrigin(e.target.value)}
            placeholder="请输入出发地" 
            style={{ width: '100%', padding: '12px', fontSize: '16px', borderRadius: '10px', border: '1px solid #ddd', marginBottom: '20px' }}
          />
        </div>
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
          <label style={{ fontSize: '18px', marginBottom: '10px', display: 'block', textAlign: 'left' }}>📝 特殊需求</label>
          <textarea 
            value={needs} 
            onChange={(e) => setNeeds(e.target.value)}
            placeholder="请输入您的特殊需求，如饮食、住宿、医疗等" 
            style={{ width: '100%', padding: '12px', fontSize: '16px', borderRadius: '10px', border: '1px solid #ddd', minHeight: '100px', resize: 'vertical', marginBottom: '20px' }}
          />
        </div>
        <div className="form-group">
          <label style={{ fontSize: '18px', marginBottom: '10px', display: 'block', textAlign: 'left' }}>📋 行程内容（可选）</label>
          <textarea 
            value={itinerary} 
            onChange={(e) => setItinerary(e.target.value)}
            placeholder="如果您已经有行程内容，可以粘贴在这里" 
            style={{ width: '100%', padding: '12px', fontSize: '16px', borderRadius: '10px', border: '1px solid #ddd', minHeight: '100px', resize: 'vertical', marginBottom: '20px' }}
          />
        </div>
        <button 
          type="submit" 
          disabled={loading}
          style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', border: 'none', padding: '15px 30px', fontSize: '18px', borderRadius: '10px', cursor: 'pointer', transition: 'all 0.3s ease' }}
        >
          {loading ? '🎁 生成清单中...' : '🎁 生成清单'}
        </button>
      </form>
      {checklist && (
        <div style={{ marginTop: '30px' }}>
          <label style={{ fontSize: '18px', marginBottom: '10px', display: 'block', textAlign: 'left' }}>🎁 清单结果</label>
          <textarea 
            value={checklist} 
            readOnly 
            style={{ width: '100%', padding: '20px', fontSize: '16px', borderRadius: '10px', border: '1px solid #ddd', minHeight: '300px', resize: 'vertical' }}
          />
        </div>
      )}
    </div>
  )
}

export default TravelChecklist