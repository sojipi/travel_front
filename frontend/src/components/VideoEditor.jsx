import React, { useState } from 'react'

function VideoEditor() {
  const [images, setImages] = useState([])
  const [audio, setAudio] = useState(null)
  const [videoUrl, setVideoUrl] = useState('')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  const handleImageChange = (e) => {
    setImages(Array.from(e.target.files))
  }

  const handleAudioChange = (e) => {
    setAudio(e.target.files[0])
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (images.length === 0) {
      setMessage('请至少上传一张图片')
      return
    }
    setLoading(true)
    try {
      const formData = new FormData()
      images.forEach((image, index) => {
        formData.append(`images`, image)
      })
      if (audio) {
        formData.append('audio', audio)
      }
      const response = await fetch('/api/create-video', {
        method: 'POST',
        body: formData,
      })
      const data = await response.json()
      if (response.ok) {
        setVideoUrl(data.video_path)
        setMessage(data.message)
      } else {
        setMessage(data.error)
      }
    } catch (error) {
      console.error('Error creating video:', error)
      setMessage('抱歉，生成视频时出现了错误。')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="video-editor-section">
      <div style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', padding: '25px', borderRadius: '15px', marginBottom: '20px', textAlign: 'center' }}>
        <h2 style={{ margin: 0, fontSize: '32px' }}>🎬 视频制作</h2>
        <p style={{ margin: '10px 0 0 0', fontSize: '16px' }}>将您的旅行照片制作成精彩的视频</p>
      </div>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label style={{ fontSize: '18px', marginBottom: '10px', display: 'block', textAlign: 'left' }}>🖼️ 上传图片</label>
          <input 
            type="file" 
            multiple 
            accept="image/*" 
            onChange={handleImageChange}
            style={{ width: '100%', padding: '12px', fontSize: '16px', borderRadius: '10px', border: '1px solid #ddd', marginBottom: '20px' }}
          />
          {images.length > 0 && (
            <p style={{ fontSize: '16px', marginBottom: '20px', textAlign: 'left' }}>已选择 {images.length} 张图片</p>
          )}
        </div>
        <div className="form-group">
          <label style={{ fontSize: '18px', marginBottom: '10px', display: 'block', textAlign: 'left' }}>🎵 上传音频（可选）</label>
          <input 
            type="file" 
            accept="audio/*" 
            onChange={handleAudioChange}
            style={{ width: '100%', padding: '12px', fontSize: '16px', borderRadius: '10px', border: '1px solid #ddd', marginBottom: '20px' }}
          />
          {audio && (
            <p style={{ fontSize: '16px', marginBottom: '20px', textAlign: 'left' }}>已选择音频: {audio.name}</p>
          )}
        </div>
        <button 
          type="submit" 
          disabled={loading}
          style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', border: 'none', padding: '15px 30px', fontSize: '18px', borderRadius: '10px', cursor: 'pointer', transition: 'all 0.3s ease' }}
        >
          {loading ? '🎬 生成视频中...' : '🎬 生成视频'}
        </button>
      </form>
      {message && (
        <p style={{ marginTop: '20px', fontSize: '16px', color: message.includes('成功') ? 'green' : 'red' }}>{message}</p>
      )}
      {videoUrl && (
        <div style={{ marginTop: '30px' }}>
          <label style={{ fontSize: '18px', marginBottom: '10px', display: 'block', textAlign: 'left' }}>🎬 生成的视频</label>
          <video 
            src={videoUrl} 
            controls 
            style={{ width: '100%', maxWidth: '800px', borderRadius: '10px', border: '1px solid #ddd' }}
          />
        </div>
      )}
    </div>
  )
}

export default VideoEditor