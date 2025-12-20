import React, { useEffect, useRef, useState } from 'react'

function SmartTourGuide() {
  const mapRef = useRef(null)
  const [pois, setPois] = useState([])
  const [loading, setLoading] = useState(false)
  const [explanation, setExplanation] = useState('')
  const [showExplanation, setShowExplanation] = useState(false)
  const [playingAudio, setPlayingAudio] = useState(false)
  const mapInstanceRef = useRef(null)

  useEffect(() => {
    // 初始化高德地图
    initMap()
  }, [])

  const initMap = () => {
    // 加载高德地图API
    const script = document.createElement('script')
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${import.meta.env.VITE_AMAP_WEB_API_KEY}`
    script.onload = () => {
      // 确保DOM元素存在
      if (!mapRef.current) return
      
      // 创建地图实例
      const map = new window.AMap.Map(mapRef.current, {
        zoom: 15,
        resizeEnable: true,
        center: [116.4038, 39.9042] // 设置默认中心点
      })
      mapInstanceRef.current = map

      // 请求用户定位
      map.plugin('AMap.Geolocation', () => {
        const geolocation = new window.AMap.Geolocation({
          enableHighAccuracy: true,
          timeout: 10000
        })
        
        // 添加定位结果监听
        geolocation.getCurrentPosition((status, result) => {
          if (status === 'complete' && result && result.position) {
            const { position } = result
            console.log('定位成功:', position)
            // 确保地图实例可用
            if (mapInstanceRef.current) {
              mapInstanceRef.current.setCenter([position.lng, position.lat])
              // 搜索附近POI
              searchNearbyPOIs(position.lng, position.lat)
            }
          } else {
            console.error('定位失败:', result)
            // 使用默认位置搜索
            searchNearbyPOIs(116.4038, 39.9042)
          }
        })
      })

      // 添加地图事件监听
      map.on('moveend', () => {
        if (mapInstanceRef.current) {
          const center = mapInstanceRef.current.getCenter()
          if (center) {
            searchNearbyPOIs(center.lng, center.lat)
          }
        }
      })
      
      map.on('zoomend', () => {
        if (mapInstanceRef.current) {
          const center = mapInstanceRef.current.getCenter()
          if (center) {
            searchNearbyPOIs(center.lng, center.lat)
          }
        }
      })
    }
    document.head.appendChild(script)
  }

  const searchNearbyPOIs = async (lng, lat) => {
    setLoading(true)
    try {
      const response = await fetch(`http://localhost:8001/api/tour-guide/pois?lng=${lng}&lat=${lat}&radius=1000`)
      const data = await response.json()
      setPois(data.pois)
      // 在地图上标记POI
      addPOIMarkers(data.pois)
    } catch (error) {
      console.error('获取POI失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const addPOIMarkers = (pois) => {
    if (!mapInstanceRef.current) return
    // 清除现有标记
    mapInstanceRef.current.clearMap()
    // 添加新标记
    pois.forEach(poi => {
      const marker = new window.AMap.Marker({
        position: [poi.lng, poi.lat],
        title: poi.name
      })
      // 添加点击事件
      marker.on('click', () => {
        getTourExplanation(poi.name)
      })
      mapInstanceRef.current.add(marker)
    })
  }

  const getTourExplanation = async (poiName) => {
    setLoading(true)
    try {
      const response = await fetch(`http://localhost:8001/api/tour-guide/explanation?poi_name=${encodeURIComponent(poiName)}`)
      const data = await response.json()
      setExplanation(data.explanation)
      setShowExplanation(true)
    } catch (error) {
      console.error('获取导游词失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const playAudio = async () => {
    setPlayingAudio(true)
    try {
      await fetch(`http://localhost:8001/api/tour-guide/play-audio?text=${encodeURIComponent(explanation)}`)
    } catch (error) {
      console.error('播放音频失败:', error)
    } finally {
      setPlayingAudio(false)
    }
  }

  return (
    <div className="smart-tour-guide">
      <div className="map-container" ref={mapRef}></div>
      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner">加载中...</div>
        </div>
      )}
      {showExplanation && (
        <div className="explanation-panel">
          <div className="explanation-header">
            <h3>导游讲解</h3>
            <button onClick={() => setShowExplanation(false)}>关闭</button>
          </div>
          <div className="explanation-content">
            <p>{explanation}</p>
          </div>
          <div className="explanation-actions">
            <button onClick={playAudio} disabled={playingAudio}>
              {playingAudio ? '播放中...' : '播放讲解'}
            </button>
          </div>
        </div>
      )}
      <style jsx>{`
        .smart-tour-guide {
          position: relative;
          width: 100%;
          height: 600px;
        }
        .map-container {
          width: 100%;
          height: 100%;
          border-radius: 8px;
        }
        .loading-overlay {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(255, 255, 255, 0.8);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }
        .loading-spinner {
          font-size: 18px;
          color: #666;
        }
        .explanation-panel {
          position: absolute;
          bottom: 20px;
          left: 20px;
          right: 20px;
          background: white;
          border-radius: 8px;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
          padding: 20px;
          z-index: 999;
          max-height: 300px;
          overflow-y: auto;
        }
        .explanation-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 15px;
        }
        .explanation-header h3 {
          margin: 0;
          color: #333;
        }
        .explanation-content p {
          line-height: 1.6;
          color: #666;
        }
        .explanation-actions {
          margin-top: 15px;
        }
        button {
          background: #4CAF50;
          color: white;
          border: none;
          padding: 10px 20px;
          border-radius: 5px;
          cursor: pointer;
          font-size: 14px;
        }
        button:hover {
          background: #45a049;
        }
        button:disabled {
          background: #ccc;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  )
}

export default SmartTourGuide