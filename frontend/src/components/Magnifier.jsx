import React, { useState, useRef, useEffect } from 'react'

function Magnifier() {
  const [isDragging, setIsDragging] = useState(false)
  const [position, setPosition] = useState({ x: 20, y: 100 })
  const [zoom, setZoom] = useState(1)
  const dragOffset = useRef({ x: 0, y: 0 })
  const hasMoved = useRef(false)

  const handleMouseDown = (e) => {
    setIsDragging(true)
    hasMoved.current = false
    dragOffset.current = {
      x: e.clientX - position.x,
      y: e.clientY - position.y
    }
    e.preventDefault()
  }

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (isDragging) {
        hasMoved.current = true
        setPosition({
          x: e.clientX - dragOffset.current.x,
          y: e.clientY - dragOffset.current.y
        })
      }
    }
    const handleMouseUp = () => setIsDragging(false)

    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('mouseup', handleMouseUp)
    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isDragging])

  useEffect(() => {
    document.body.style.zoom = zoom
    document.body.style.transformOrigin = 'top left'
  }, [zoom])

  const handleClick = () => {
    if (!hasMoved.current) {
      setZoom(z => z === 1 ? 1.5 : z === 1.5 ? 2 : 1)
    }
  }

  return (
    <>
      <div
        className="magnifier-btn"
        style={{
          left: position.x / zoom,
          top: position.y / zoom,
          transform: `scale(${1/zoom})`
        }}
        onMouseDown={handleMouseDown}
        onClick={handleClick}
      >
        🔍
        {zoom > 1 && <span className="zoom-level">{zoom}x</span>}
      </div>
      <style>{`
        .magnifier-btn {
          position: fixed;
          width: 50px;
          height: 50px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 24px;
          cursor: grab;
          z-index: 9999;
          box-shadow: 0 4px 15px rgba(0,0,0,0.3);
          user-select: none;
          transform-origin: top left;
        }
        .magnifier-btn:active { cursor: grabbing; }
        .zoom-level {
          position: absolute;
          bottom: -8px;
          right: -8px;
          background: #ff6b6b;
          color: white;
          font-size: 12px;
          padding: 2px 6px;
          border-radius: 10px;
        }
      `}</style>
    </>
  )
}

export default Magnifier
