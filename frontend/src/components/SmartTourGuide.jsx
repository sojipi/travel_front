import React, { useEffect, useRef, useState } from 'react'

function SmartTourGuide() {
  const mapRef = useRef(null)
  const [pois, setPois] = useState([])
  const [loading, setLoading] = useState(false)
  const [playing, setPlaying] = useState(false)
  const [currentPoi, setCurrentPoi] = useState(null)
  const mapInstanceRef = useRef(null)
  const markersRef = useRef([])

  useEffect(() => {
    // 初始化高德地图
    if (!window.AMap) {
      // 动态加载高德地图API
      const script = document.createElement('script')
      script.src = `https://webapi.amap.com/maps?v=2.0&key=${import.meta.env.VITE_AMAP_WEB_API_KEY}`
      script.onload = initMap
      document.head.appendChild(script)
    } else {
      initMap()
    }
  }, [])

  const initMap = () => {
    // 创建地图实例
    const map = new window.AMap.Map(mapRef.current, {
      zoom: 15,
      resizeEnable: true
    })
    mapInstanceRef.current = map

    // 请求用户定位
    map.plugin('AMap.Geolocation', () => {
      const geolocation = new window.AMap.Geolocation({
        enableHighAccuracy: true,
        timeout: 10000
      })
      map.addControl(geolocation)
      geolocation.getCurrentPosition((status, result) => {
        if (status === 'complete') {
          onLocateSuccess(result)
        } else {
          console.error('定位失败:', result)
          // 如果定位失败，使用默认位置（北京）
          map.setCenter([116.397428, 39.90923])
          searchPois([116.397428, 39.90923], 1000)
        }
      })
    })

    // 监听地图移动和缩放事件
    map.on('moveend', () => {
      const center = map.getCenter()
      const zoom = map.getZoom()
      const radius = calculateRadius(zoom)
      searchPois([center.lng, center.lat], radius)
    })
    map.on('zoomend', () => {
      const center = map.getCenter()
      const zoom = map.getZoom()
      const radius = calculateRadius(zoom)
      searchPois([center.lng, center.lat], radius)
    })
  }

  const onLocateSuccess = (result) => {
    const { position } = result
    mapInstanceRef.current.setCenter([position.lng, position.lat])
    searchPois([position.lng, position.lat], 1000)
  }

  const calculateRadius = (zoom) => {
    // 根据缩放级别计算搜索半径
    return Math.max(500, 5000 / zoom)
  }

  const searchPois = async (center, radius) => {
    setLoading(true)
    try {
      const response = await fetch(`http://localhost:8001/api/tour-guide/pois?lng=${center[0]}&lat=${center[1]}&radius=${radius}`)
      const data = await response.json()
      setPois(data.pois)
      addMarkersToMap(data.pois)
    } catch (error) {
      console.error('搜索POI失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const addMarkersToMap = (pois) => {
    // 清除旧标记
    markersRef.current.forEach(marker => {
      if (marker) {
        mapInstanceRef.current.remove(marker)
      }
    })
    markersRef.current = []

    // 添加新标记
    pois.forEach(poi => {
      const marker = new window.AMap.Marker({
        position: [poi.lng, poi.lat],
        title: poi.name
      })
      marker.on('click', () => {
        onPoiClick(poi)
      })
      mapInstanceRef.current.add(marker)
      markersRef.current.push(marker)
    })
  }

  const onPoiClick = async (poi) => {
    setCurrentPoi(poi)
    setLoading(true)
    try {
      // 获取导游讲解词
      const response = await fetch(`http://localhost:8001/api/tour-guide/explanation?poi_name=${encodeURIComponent(poi.name)}`)
      const data = await response.json()
      // 播放导游词
      await playAudio(data.explanation)
    } catch (error) {
      console.error('获取导游词失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const playAudio = async (text) => {
    setPlaying(true)
    try {
      await fetch(`http://localhost:8001/api/tour-guide/play-audio?text=${encodeURIComponent(text)}`)
    } catch (error) {
      console.error('播放音频失败:', error)
    } finally {
      setPlaying(false)
    }
  }

  return (
    <div className="smart-tour-guide">
      <h2>🧭 智能导游</h2>
      <div className="map-container" ref={mapRef}></div>
      <div className="pois-list">
        <h3>附近景点</h3>
        {loading ? (
          <div className="loading">加载中...</div>
        ) : (
          <ul>
            {pois.map(poi => (
              <li key={poi.id} onClick={() => onPoiClick(poi)}>
                <h4>{poi.name}</h4>
                <p>{poi.type}</p>
                <p>{poi.address}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
      {loading && (
        <div className="overlay">
          <div className="overlay-content">
            <div className="spinner"></div>
            <p>正在加载...</p>
          </div>
        </div>
      )}
      {playing && (
        <div className="overlay">
          <div className="overlay-content">
            <div className="spinner"></div>
            <p>正在播放导游词...</p>
          </div>
        </div>
      )}
      <style jsx>{`
        .smart-tour-guide {
          display: flex;
          flex-direction: column;
          height: 100%;
        }
        .map-container {
          width: 100%;
          height: 500px;
          border: 1px solid #ddd;
          border-radius: 8px;
          margin-bottom: 20px;
        }
        .pois-list {
          flex: 1;
          overflow-y: auto;
        }
        .pois-list ul {
          list-style: none;
          padding: 0;
        }
        .pois-list li {
          padding: 15px;
          border: 1px solid #ddd;
          border-radius: 8px;
          margin-bottom: 10px;
          cursor: pointer;
          transition: background-color 0.3s;
        }
        .pois-list li:hover {
          background-color: #f5f5f5;
        }
        .overlay {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background-color: rgba(0, 0, 0, 0.5);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 1000;
        }
        .overlay-content {
          background-color: white;
          padding: 20px;
          border-radius: 8px;
          text-align: center;
        }
        .spinner {
          width: 40px;
          height: 40px;
          border: 4px solid #f3f3f3;
          border-top: 4px solid #3498db;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto 20px;
        }
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        .loading {
          text-align: center;
          padding: 20px;
          color: #666;
        }
      `}</style>
    </div>
  )
}

export default SmartTourGuide