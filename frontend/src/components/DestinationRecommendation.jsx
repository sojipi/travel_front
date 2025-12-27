import React, { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

function DestinationRecommendation({ selectedVoice = 'xiaoyun' }) {
  const [season, setSeason] = useState('秋季')
  const [healthStatus, setHealthStatus] = useState('身体健康')
  const [budget, setBudget] = useState('舒适型')
  const [interests, setInterests] = useState(['避寒康养', '温泉养生'])
  const [recommendation, setRecommendation] = useState('')
  const [loading, setLoading] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [audioUrl, setAudioUrl] = useState('')

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
          <div
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
              {recommendation}
            </ReactMarkdown>
          </div>
          <button
            onClick={() => playTTS(recommendation, selectedVoice)}
            disabled={isGenerating || isPlaying}
            style={{
              marginTop: '15px',
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
            {isGenerating ? '🔊 音频生成中...' : isPlaying ? '🔊 播放中...' : '🔊 播放推荐内容'}
          </button>
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

export default DestinationRecommendation