import React, { useState, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import html2pdf from 'html2pdf.js'

function ItineraryPlan({ selectedVoice = 'xiaoyun', onImportToChecklist }) {
  const [destination, setDestination] = useState('')
  const [duration, setDuration] = useState('一周左右')
  const [mobility, setMobility] = useState('行走自如')
  const [healthFocus, setHealthFocus] = useState(['避免过度疲劳', '饮食清淡', '定期休息'])
  const [itinerary, setItinerary] = useState('')
  const [loading, setLoading] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [audioUrl, setAudioUrl] = useState('')
  const itineraryRef = useRef(null)

  // 清理markdown符号，用于语音生成
  const cleanMarkdown = (text) => {
    return text
      .replace(/^#{1,6}\s+/gm, '') // 移除标题符号 #
      .replace(/#{1,6}\s+/g, '') // 移除行内标题符号 #
      .replace(/\*\*/g, '') // 移除粗体符号 **
      .replace(/\*/g, '') // 移除斜体符号 *
      .replace(/^- /gm, '') // 移除列表符号 -
      .replace(/^\d+\. /gm, '') // 移除数字列表符号 1. 2. 3.
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // 移除链接，保留文本
      .replace(/`/g, '') // 移除代码符号 `
      .replace(/\n\n+/g, '\n') // 合并多余换行
      .trim()
  }

  const playTTS = async (text, voice) => {
    if (!text || isGenerating || isPlaying) return
    setIsGenerating(true)
    setIsPlaying(true)
    try {
      // 清理markdown符号后再传给TTS
      const cleanText = cleanMarkdown(text)
      const response = await fetch(`http://localhost:8001/api/tour-guide/play-audio?text=${encodeURIComponent(cleanText)}&voice=${voice}`)
      const data = await response.json()
      if (data.audio_url) {
        setAudioUrl(data.audio_url)
        const audio = new Audio(`http://localhost:8001${data.audio_url}`)
        audio.onended = () => {
          setIsPlaying(false)
          setIsGenerating(false)
        }
        audio.onerror = () => {
          setIsPlaying(false)
          setIsGenerating(false)
          alert('音频播放失败')
        }
        audio.play()
      } else {
        setIsGenerating(false)
        setIsPlaying(false)
        alert('音频生成失败')
      }
    } catch (error) {
      console.error('TTS调用错误:', error)
      setIsGenerating(false)
      setIsPlaying(false)
      alert('TTS调用失败，请检查后端配置')
    }
  }

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

  const exportToPDF = () => {
    if (!itineraryRef.current) return
    const element = itineraryRef.current
    const opt = {
      margin: 10,
      filename: `旅行计划-${destination}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    }
    html2pdf().set(opt).from(element).save()
  }

  const importToChecklist = () => {
    if (!itinerary || !destination) {
      alert('请先生成行程计划')
      return
    }
    if (onImportToChecklist) {
      onImportToChecklist(itinerary, destination)
    }
  }

  return (
    <div className="itinerary-section">
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
          <div
            ref={itineraryRef}
            className="markdown-content"
            style={{
              width: '100%',
              padding: '20px',
              fontSize: '16px',
              borderRadius: '10px',
              border: '1px solid #ddd',
              minHeight: '300px',
              background: '#fafafa',
              maxHeight: '600px',
              overflowY: 'auto',
              lineHeight: '1.8',
              color: '#333'
            }}
          >
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                h1: ({ node, ...props }) => <h1 style={{ fontSize: '28px', fontWeight: 'bold', marginTop: '24px', marginBottom: '12px', color: '#2c3e50' }} {...props} />,
                h2: ({ node, ...props }) => <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginTop: '20px', marginBottom: '10px', color: '#34495e' }} {...props} />,
                h3: ({ node, ...props }) => <h3 style={{ fontSize: '20px', fontWeight: 'bold', marginTop: '16px', marginBottom: '8px', color: '#555' }} {...props} />,
                h4: ({ node, ...props }) => <h4 style={{ fontSize: '18px', fontWeight: 'bold', marginTop: '14px', marginBottom: '6px', color: '#666' }} {...props} />,
                p: ({ node, ...props }) => <p style={{ marginTop: '8px', marginBottom: '8px', color: '#444' }} {...props} />,
                ul: ({ node, ...props }) => <ul style={{ marginTop: '8px', marginBottom: '8px', paddingLeft: '20px', color: '#444' }} {...props} />,
                ol: ({ node, ...props }) => <ol style={{ marginTop: '8px', marginBottom: '8px', paddingLeft: '20px', color: '#444' }} {...props} />,
                li: ({ node, ...props }) => <li style={{ marginBottom: '4px', color: '#444' }} {...props} />,
                strong: ({ node, ...props }) => <strong style={{ fontWeight: 'bold', color: '#2c3e50' }} {...props} />,
                code: ({ node, ...props }) => <code style={{ background: '#f4f4f4', padding: '2px 6px', borderRadius: '3px', fontFamily: 'monospace', fontSize: '0.9em' }} {...props} />,
                blockquote: ({ node, ...props }) => <blockquote style={{ borderLeft: '4px solid #667eea', paddingLeft: '16px', marginLeft: '0', color: '#555', fontStyle: 'italic' }} {...props} />
              }}
            >
              {itinerary}
            </ReactMarkdown>
          </div>
          <div style={{ marginTop: '15px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            <button
              onClick={() => playTTS(itinerary, selectedVoice)}
              disabled={isGenerating || isPlaying}
              style={{
                background: (isGenerating || isPlaying) ? '#BDBDBD' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                border: 'none',
                padding: '12px 24px',
                fontSize: '16px',
                borderRadius: '8px',
                cursor: (isGenerating || isPlaying) ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              {isGenerating ? '🔊 音频生成中...' : isPlaying ? '🔊 播放中...' : '🔊 播放行程计划'}
            </button>
            <button
              onClick={exportToPDF}
              style={{
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
            <button
              onClick={importToChecklist}
              style={{
                background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
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
              🎁 一键导入旅行清单
            </button>
          </div>
          {audioUrl && (
            <div style={{ marginTop: '12px', padding: '12px', background: '#f5f5f5', borderRadius: '4px' }}>
              <audio controls src={`http://localhost:8001${audioUrl}`} style={{ width: '100%' }} />
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ItineraryPlan