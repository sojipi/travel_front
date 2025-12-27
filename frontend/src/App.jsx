import React, { useState, useEffect } from 'react'
import './App.css'
import DestinationRecommendation from './components/DestinationRecommendation'
import ItineraryPlan from './components/ItineraryPlan'
import TravelChecklist from './components/TravelChecklist'
import VideoEditor from './components/VideoEditor'
import SmartTourGuide from './components/SmartTourGuide'
import Magnifier from './components/Magnifier'

const voiceOptions = [
  { value: 'xiaoyun', label: '默认（标准普通话）' },
  { value: 'chuangirl', label: '四川话' },
  { value: 'shanshan', label: '粤语' },
  { value: 'cuijie', label: '东北话' },
  { value: 'xiaoze', label: '湖南话' },
  { value: 'aikan', label: '天津话' }
]

function App() {
  const [selectedVoice, setSelectedVoice] = useState(() => {
    const saved = localStorage.getItem('tts_voice')
    return saved || 'xiaoyun'
  })
  const [showVoiceSettings, setShowVoiceSettings] = useState(false)
  const [importedItinerary, setImportedItinerary] = useState('')
  const [importedDestination, setImportedDestination] = useState('')

  useEffect(() => {
    localStorage.setItem('tts_voice', selectedVoice)
  }, [selectedVoice])

  return (
    <div className="App">
      <header className="App-header">
        <h1>🧳 银发族智能旅行助手</h1>
        <p>专为中老年朋友设计的温暖贴心的旅行规划伙伴</p>
        <button className="voice-settings-btn" onClick={() => setShowVoiceSettings(true)}>
          🎙️ 方言设置
        </button>
      </header>
      <nav className="App-nav">
        <button onClick={(event) => showTab('destination', event)}>🌟 目的地推荐</button>
        <button onClick={(event) => showTab('itinerary', event)}>📋 行程规划</button>
        <button onClick={(event) => showTab('checklist', event)}>🎁 旅行清单</button>
        <button onClick={(event) => showTab('video', event)}>🎬 视频制作</button>
        <button onClick={(event) => showTab('tour-guide', event)}>🧭 智能导游</button>
      </nav>
      <main className="App-main">
        <div id="destination" className="tab active">
          <DestinationRecommendation selectedVoice={selectedVoice} />
        </div>
        <div id="itinerary" className="tab">
          <ItineraryPlan selectedVoice={selectedVoice} onImportToChecklist={(itinerary, dest) => {
            setImportedItinerary(itinerary)
            setImportedDestination(dest)
            // 切换到旅行清单标签
            setTimeout(() => {
              const checklistTab = document.getElementById('checklist')
              const navButtons = document.querySelectorAll('.App-nav button')
              checklistTab.classList.add('active')
              navButtons.forEach(btn => btn.classList.remove('active'))
              navButtons[2].classList.add('active')
            }, 100)
          }} />
        </div>
        <div id="checklist" className="tab">
          <TravelChecklist importedItinerary={importedItinerary} importedDestination={importedDestination} />
        </div>
        <div id="video" className="tab">
          <VideoEditor />
        </div>
        <div id="tour-guide" className="tab">
          <SmartTourGuide selectedVoice={selectedVoice} />
        </div>
      </main>
      <Magnifier />
      
      {showVoiceSettings && (
        <div className="voice-settings-modal" onClick={() => setShowVoiceSettings(false)}>
          <div className="voice-settings-content" onClick={(e) => e.stopPropagation()}>
            <div className="voice-settings-header">
              <h2>🎙️ 方言设置</h2>
              <span className="voice-settings-close" onClick={() => setShowVoiceSettings(false)}>×</span>
            </div>
            <div className="voice-settings-body">
              <label>选择语音风格：</label>
              <select
                className="voice-settings-select"
                value={selectedVoice}
                onChange={(e) => {
                  setSelectedVoice(e.target.value)
                  localStorage.setItem('tts_voice', e.target.value)
                }}
              >
                {voiceOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <p className="voice-settings-hint">设置后将自动应用于前两个页面的语音播放功能</p>
              <div className="voice-settings-footer">
                <button className="voice-settings-confirm" onClick={() => setShowVoiceSettings(false)}>
                  确定
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function showTab(tabName, event) {
  const tabs = document.querySelectorAll('.tab')
  const navButtons = document.querySelectorAll('.App-nav button')
  
  tabs.forEach(tab => tab.classList.remove('active'))
  navButtons.forEach(button => button.classList.remove('active'))
  
  document.getElementById(tabName).classList.add('active')
  event.target.classList.add('active')
}

export default App