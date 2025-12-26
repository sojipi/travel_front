import React, { useEffect, useRef, useState, useCallback } from 'react'

const AMAP_KEY = import.meta.env.VITE_AMAP_WEB_API_KEY
const AMAP_STATIC_KEY = import.meta.env.VITE_AMAP_SERVER_API_KEY
const AMAP_SECRET = import.meta.env.VITE_AMAP_API_SECRET

function SmartTourGuide() {
  const mapRef = useRef(null)
  const mapInstanceRef = useRef(null)
  const markersRef = useRef([])
  const imageLayerRef = useRef(null)
  const placeSearchRef = useRef(null)
  const searchTimerRef = useRef(null)

  const [loading, setLoading] = useState(false)
  const [loadingText, setLoadingText] = useState('加载中...')
  const [showGuideModal, setShowGuideModal] = useState(false)
  const [currentPoi, setCurrentPoi] = useState({})
  const [guideContent, setGuideContent] = useState('')
  const [searchKeyword, setSearchKeyword] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [mapStyle, setMapStyle] = useState('卡通风格')
  const [showPoiLabels, setShowPoiLabels] = useState(true)

  const clearMarkers = useCallback(() => {
    markersRef.current.forEach(m => mapInstanceRef.current?.remove(m))
    markersRef.current = []
  }, [])

  const addMarkers = useCallback((pois) => {
    if (!mapInstanceRef.current || !window.AMap) return
    pois.forEach(poi => {
      const marker = new window.AMap.Text({
        text: poi.name || '未知景点',
        position: [poi.location.lng, poi.location.lat],
        offset: new window.AMap.Pixel(0, -20),
        style: {
          'background-color': '#4CAF50',
          'border': '1px solid #388E3C',
          'border-radius': '4px',
          'padding': '4px 8px',
          'font-size': '12px',
          'color': '#fff',
          'cursor': 'pointer'
        }
      })
      marker.on('click', () => fetchGuideContent(poi))
      mapInstanceRef.current.add(marker)
      markersRef.current.push(marker)
      if (!showPoiLabels) marker.hide()
    })
  }, [showPoiLabels])

  const searchPOI = useCallback(() => {
    if (!placeSearchRef.current || !mapInstanceRef.current) return
    const bounds = mapInstanceRef.current.getBounds()
    placeSearchRef.current.searchInBounds('旅游景点', bounds, (status, result) => {
      if (status === 'complete' && result.poiList) {
        clearMarkers()
        addMarkers(result.poiList.pois)
      }
    })
  }, [clearMarkers, addMarkers])

  const debounceSearch = useCallback(() => {
    if (searchTimerRef.current) clearTimeout(searchTimerRef.current)
    searchTimerRef.current = setTimeout(() => searchPOI(), 500)
  }, [searchPOI])

  useEffect(() => {
    if (typeof window.AMap !== 'undefined') {
      initMap()
      return
    }
    window._AMapSecurityConfig = { securityJsCode: AMAP_SECRET }
    const script = document.createElement('script')
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${AMAP_KEY}&plugin=AMap.Scale,AMap.ToolBar,AMap.PlaceSearch,AMap.Geolocation`
    script.onload = () => initMap()
    document.head.appendChild(script)
  }, [])

  const initMap = () => {
    if (!mapRef.current || !window.AMap) return
    const map = new window.AMap.Map(mapRef.current, {
      zoom: 14,
      viewMode: '2D',
      resizeEnable: true
    })
    mapInstanceRef.current = map
    map.addControl(new window.AMap.Scale())
    map.addControl(new window.AMap.ToolBar())

    placeSearchRef.current = new window.AMap.PlaceSearch({ type: '风景名胜', pageSize: 20 })
    map.on('complete', () => searchPOI())
    map.on('moveend', debounceSearch)
    map.on('zoomend', debounceSearch)
  }

  const fetchGuideContent = async (poi) => {
    setLoading(true)
    setLoadingText('正在生成讲解词...')
    try {
            const response = await fetch(`http://localhost:8001/api/tour-guide/explanation?poi_name=${encodeURIComponent(poi.name)}`)
      const data = await response.json()
      const content = data.explanation || '暂无讲解内容'
      setCurrentPoi(poi)
      setGuideContent(content)
      setShowGuideModal(true)
    } catch (error) {
      console.error('请求错误:', error)
      setCurrentPoi(poi)
      setGuideContent('获取讲解词失败，请稍后重试')
      setShowGuideModal(true)
    }
    setLoading(false)
  }

  const searchCity = () => {
    if (!searchKeyword.trim()) {
      setSearchResults([])
      return
    }
    const citySearch = new window.AMap.PlaceSearch({ pageSize: 10, extensions: 'base' })
    citySearch.search(searchKeyword, (status, result) => {
      if (status === 'complete' && result.poiList?.pois) {
        setSearchResults(result.poiList.pois.map(poi => ({
          name: poi.name,
          location: poi.location,
          cityname: poi.cityname || '',
          adname: poi.adname || ''
        })))
      } else {
        setSearchResults([])
      }
    })
  }

  const selectCity = (city) => {
    setSearchResults([])
    setSearchKeyword(city.name)
    if (mapInstanceRef.current) {
      mapInstanceRef.current.setCity(city.name, () => {
        clearMarkers()
        searchPOI()
      })
    }
  }

  const togglePoiLabels = () => {
    const newState = !showPoiLabels
    setShowPoiLabels(newState)
    markersRef.current.forEach(marker => newState ? marker.show() : marker.hide())
  }

  const generateCartoonMap = async () => {
    if (!mapInstanceRef.current) return
    setLoading(true)
    setLoadingText('正在生成地图...')

    const center = mapInstanceRef.current.getCenter()
    const zoom = Math.floor(mapInstanceRef.current.getZoom())
    const bounds = mapInstanceRef.current.getBounds()
    const mapSize = mapInstanceRef.current.getSize()
    const width = Math.min(Math.floor(mapSize.width), 1024)
    const height = Math.min(Math.floor(mapSize.height), 1024)

    const staticMapUrl = `https://restapi.amap.com/v3/staticmap?location=${center.lng},${center.lat}&zoom=${zoom}&size=${width}*${height}&key=${AMAP_STATIC_KEY}`

    const stylePrompt = mapStyle ? `将图片修改为${mapStyle}的地绘彩色地图。` : '将图片修改为一张卡通风格的地绘彩色地图。'
    const fullPrompt = stylePrompt + '地图包含简化的道路、标志性建筑作为可爱插图、郁郁葱葱的公园，整体氛围欢乐有趣。风格扁平干净，线条粗犷，带有柔和阴影。'

    try {
      const response = await fetch('http://localhost:8001/api/generate-cartoon-map', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          image_url: staticMapUrl,
          prompt: fullPrompt
        })
      })

      const data = await response.json()
      const imageUrl = data?.output?.choices?.[0]?.message?.content?.[0]?.image
      if (imageUrl) {
        if (imageLayerRef.current) {
          mapInstanceRef.current.remove(imageLayerRef.current)
        }
        const layerBounds = new window.AMap.Bounds(
          [bounds.southWest.lng, bounds.southWest.lat],
          [bounds.northEast.lng, bounds.northEast.lat]
        )
        imageLayerRef.current = new window.AMap.ImageLayer({
          url: imageUrl,
          bounds: layerBounds,
          zooms: [2, 20],
          zIndex: 10
        })
        mapInstanceRef.current.add(imageLayerRef.current)
      } else {
        alert('生成失败')
      }
    } catch (error) {
      console.error('生成卡通地图失败:', error)
      alert('生成失败')
    }
    setLoading(false)
  }

  const removeCartoonLayer = () => {
    if (imageLayerRef.current && mapInstanceRef.current) {
      mapInstanceRef.current.remove(imageLayerRef.current)
      imageLayerRef.current = null
    }
  }

  return (
    <div className="smart-tour-guide">
      <div className="map-container" ref={mapRef}></div>

      {/* 城市搜索框 */}
      <div className="city-search-container">
        <input
          className="city-search-input"
          value={searchKeyword}
          onChange={(e) => setSearchKeyword(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && searchCity()}
          placeholder="搜索城市"
        />
        {searchResults.length > 0 && (
          <div className="city-search-results">
            {searchResults.map((city, index) => (
              <div key={index} className="city-result-item" onClick={() => selectCity(city)}>
                {city.name}{city.cityname ? ' - ' + city.cityname : ''}{city.adname ? ', ' + city.adname : ''}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 地图风格输入框 */}
      <div className="map-style-container">
        <input
          className="map-style-input"
          value={mapStyle}
          onChange={(e) => setMapStyle(e.target.value)}
          placeholder="输入地图风格，如：卡通风格、水墨画风格"
        />
      </div>

      {/* POI标签显示/隐藏按钮 */}
      <button className="poi-toggle-btn" onClick={togglePoiLabels}>
        {showPoiLabels ? '隐藏标签' : '显示标签'}
      </button>

      {/* 生成地图按钮 */}
      <button className="cartoon-btn" onClick={generateCartoonMap}>生成地图</button>

      {/* 移除图层按钮 */}
      <button className="remove-layer-btn" onClick={removeCartoonLayer}>移除图层</button>

      {/* 加载遮罩 */}
      {loading && (
        <div className="loading-mask">
          <div className="loading-content">
            <div className="loading-spinner"></div>
            <span className="loading-text">{loadingText}</span>
          </div>
        </div>
      )}

      {/* 讲解词弹窗 */}
      {showGuideModal && (
        <div className="guide-modal" onClick={() => setShowGuideModal(false)}>
          <div className="guide-content" onClick={(e) => e.stopPropagation()}>
            <div className="guide-header">
              <span className="guide-title">{currentPoi.name}</span>
              <span className="guide-close" onClick={() => setShowGuideModal(false)}>×</span>
            </div>
            <div className="guide-body">
              <p className="guide-text">{guideContent}</p>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .smart-tour-guide {
          position: relative;
          width: 100%;
          height: 100vh;
        }
        .map-container {
          width: 100%;
          height: 100%;
        }
        .city-search-container {
          position: absolute;
          top: 10px;
          left: 10px;
          z-index: 100;
          width: 200px;
        }
        .city-search-input, .map-style-input {
          width: 100%;
          height: 36px;
          padding: 0 12px;
          background: rgba(255,255,255,0.95);
          border-radius: 18px;
          font-size: 14px;
          border: 1px solid #ddd;
          box-shadow: 0 2px 6px rgba(0,0,0,0.1);
          box-sizing: border-box;
        }
        .city-search-results {
          margin-top: 5px;
          background: rgba(255,255,255,0.95);
          border-radius: 8px;
          max-height: 200px;
          overflow-y: auto;
          box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }
        .city-result-item {
          padding: 10px 12px;
          font-size: 14px;
          color: #333;
          border-bottom: 1px solid #eee;
          cursor: pointer;
        }
        .city-result-item:hover { background: #f5f5f5; }
        .city-result-item:last-child { border-bottom: none; }
        .map-style-container {
          position: absolute;
          top: 10px;
          right: 10px;
          z-index: 100;
          width: 220px;
        }
        .poi-toggle-btn, .cartoon-btn, .remove-layer-btn {
          position: absolute;
          background: #4CAF50;
          color: #fff;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          font-size: 14px;
          cursor: pointer;
          z-index: 100;
        }
        .poi-toggle-btn { bottom: 60px; left: 10px; }
        .cartoon-btn { top: 56px; right: 10px; }
        .remove-layer-btn { top: 100px; right: 10px; background: #f44336; }
        .loading-mask {
          position: fixed;
          top: 0; left: 0; right: 0; bottom: 0;
          background: rgba(0,0,0,0.5);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 999;
        }
        .loading-content {
          background: #fff;
          padding: 20px 30px;
          border-radius: 8px;
          display: flex;
          flex-direction: column;
          align-items: center;
        }
        .loading-spinner {
          width: 30px;
          height: 30px;
          border: 3px solid #f3f3f3;
          border-top: 3px solid #3498db;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        .loading-text { margin-top: 10px; font-size: 14px; color: #333; }
        .guide-modal {
          position: fixed;
          top: 0; left: 0; right: 0; bottom: 0;
          background: rgba(0,0,0,0.5);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 998;
        }
        .guide-content {
          width: 85%;
          max-width: 500px;
          max-height: 70%;
          background: #fff;
          border-radius: 8px;
          overflow: hidden;
        }
        .guide-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 16px;
          border-bottom: 1px solid #eee;
        }
        .guide-title { font-size: 16px; font-weight: bold; color: #333; }
        .guide-close { font-size: 24px; color: #999; cursor: pointer; }
        .guide-body { padding: 16px; max-height: 300px; overflow-y: auto; }
        .guide-text { font-size: 14px; color: #666; line-height: 1.8; margin: 0; white-space: pre-wrap; }
      `}</style>
    </div>
  )
}

export default SmartTourGuide
