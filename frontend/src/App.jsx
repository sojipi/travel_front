import React from 'react'
import './App.css'
import DestinationRecommendation from './components/DestinationRecommendation'
import ItineraryPlan from './components/ItineraryPlan'
import TravelChecklist from './components/TravelChecklist'
import VideoEditor from './components/VideoEditor'

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>🧳 银发族智能旅行助手</h1>
        <p>专为中老年朋友设计的温暖贴心的旅行规划伙伴</p>
      </header>
      <nav className="App-nav">
        <button onClick={(event) => showTab('destination', event)}>🌟 目的地推荐</button>
        <button onClick={(event) => showTab('itinerary', event)}>📋 行程规划</button>
        <button onClick={(event) => showTab('checklist', event)}>🎁 旅行清单</button>
        <button onClick={(event) => showTab('video', event)}>🎬 视频制作</button>
      </nav>
      <main className="App-main">
        <div id="destination" className="tab active">
          <DestinationRecommendation />
        </div>
        <div id="itinerary" className="tab">
          <ItineraryPlan />
        </div>
        <div id="checklist" className="tab">
          <TravelChecklist />
        </div>
        <div id="video" className="tab">
          <VideoEditor />
        </div>
      </main>
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