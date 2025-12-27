import React, { useState, useRef, useEffect } from 'react'
import html2pdf from 'html2pdf.js'

function TravelChecklist({ importedItinerary, importedDestination }) {
  const [origin, setOrigin] = useState('')
  const [destination, setDestination] = useState('')
  const [duration, setDuration] = useState('一周左右')
  const [departureDate, setDepartureDate] = useState('')
  const [needs, setNeeds] = useState('')
  const [itinerary, setItinerary] = useState('')
  const [checklist, setChecklist] = useState('')
  const [loading, setLoading] = useState(false)
  const checklistRef = useRef(null)

  // 当接收到导入的数据时，自动填充表单
  useEffect(() => {
    if (importedItinerary) {
      setItinerary(importedItinerary)
    }
    if (importedDestination) {
      setDestination(importedDestination)
    }
  }, [importedItinerary, importedDestination])

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
        body: JSON.stringify({ 
          origin, 
          destination, 
          duration, 
          departure_date: departureDate,
          needs, 
          itinerary_content: itinerary 
        }),
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

  const exportToPDF = () => {
    if (!checklistRef.current) return
    const element = checklistRef.current
    const opt = {
      margin: 10,
      filename: `旅行清单-${destination || '未命名'}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    }
    html2pdf().set(opt).from(element).save()
  }

  return (
    <div className="checklist-section">
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
          <label style={{ fontSize: '18px', marginBottom: '10px', display: 'block', textAlign: 'left' }}>📅 出发日期</label>
          <input 
            type="date" 
            value={departureDate} 
            onChange={(e) => setDepartureDate(e.target.value)}
            style={{ width: '100%', padding: '12px', fontSize: '16px', borderRadius: '10px', border: '1px solid #ddd', marginBottom: '20px' }}
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
          <div
            ref={checklistRef}
            dangerouslySetInnerHTML={{ __html: checklist }}
            style={{ width: '100%', padding: '20px', fontSize: '16px', borderRadius: '10px', border: '1px solid #ddd', minHeight: '300px', background: '#fff', lineHeight: '1.8' }}
          />
          <button
            onClick={exportToPDF}
            style={{
              marginTop: '15px',
              background: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              fontSize: '16px',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            📄 导出PDF
          </button>
        </div>
      )}
    </div>
  )
}

export default TravelChecklist