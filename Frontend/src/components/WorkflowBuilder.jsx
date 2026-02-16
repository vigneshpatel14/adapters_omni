import React from 'react'

export default function WorkflowBuilder() {
  return (
    <div style={{
      width: '100%',
      height: '100%',
      background: '#f5f5f7',
      position: 'relative',
      overflow: 'hidden',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
    }}>
      {/* Canvas Background */}
      <div style={{
        flex: 1,
        position: 'relative',
        width: '100%',
        height: '100%',
        backgroundImage: `
          linear-gradient(rgba(91, 159, 212, 0.05) 1px, transparent 1px),
          linear-gradient(90deg, rgba(91, 159, 212, 0.05) 1px, transparent 1px)
        `,
        backgroundSize: '50px 50px',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        overflow: 'hidden',
      }}>
        {/* Workflow Container */}
        <div style={{
          position: 'relative',
          width: '1000px',
          height: '300px',
          background: 'transparent',
        }}>
          {/* SVG for connecting lines */}
          <svg
            style={{
              position: 'absolute',
              width: '100%',
              height: '100%',
              top: 0,
              left: 0,
              pointerEvents: 'none',
              zIndex: 1,
            }}
          >
            {/* Line from START to PROCESS */}
            <defs>
              <linearGradient id="lineGradient1" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style={{ stopColor: '#5b9fd4', stopOpacity: 0.3 }} />
                <stop offset="100%" style={{ stopColor: '#5b9fd4', stopOpacity: 0.6 }} />
              </linearGradient>
              <linearGradient id="lineGradient2" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style={{ stopColor: '#5b9fd4', stopOpacity: 0.6 }} />
                <stop offset="100%" style={{ stopColor: '#34c759', stopOpacity: 0.3 }} />
              </linearGradient>
            </defs>

            {/* Line from START to PROCESS */}
            <line
              x1="160"
              y1="150"
              x2="330"
              y2="150"
              stroke="url(#lineGradient1)"
              strokeWidth="3"
              strokeLinecap="round"
            />
            {/* Arrow head 1 */}
            <polygon
              points="330,150 320,145 320,155"
              fill="#5b9fd4"
              opacity="0.6"
            />

            {/* Line from PROCESS to RESPOND */}
            <line
              x1="470"
              y1="150"
              x2="640"
              y2="150"
              stroke="url(#lineGradient2)"
              strokeWidth="3"
              strokeLinecap="round"
            />
            {/* Arrow head 2 */}
            <polygon
              points="640,150 630,145 630,155"
              fill="#34c759"
              opacity="0.6"
            />

            {/* Connection circles */}
            <circle cx="160" cy="150" r="4" fill="#5b9fd4" opacity="0.5" />
            <circle cx="330" cy="150" r="4" fill="#5b9fd4" opacity="0.5" />
            <circle cx="470" cy="150" r="4" fill="#5b9fd4" opacity="0.5" />
            <circle cx="640" cy="150" r="4" fill="#34c759" opacity="0.5" />
          </svg>

        {/* START Node */}
        <div
          style={{
            position: 'absolute',
            left: '20px',
            top: '50%',
            transform: 'translateY(-50%)',
            width: '140px',
            background: '#ffffff',
            border: '2px solid #5b9fd4',
            borderRadius: '12px',
            padding: '1.5rem 1.25rem',
            boxShadow: '0 4px 16px rgba(91, 159, 212, 0.15)',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            textAlign: 'center',
            zIndex: 10,
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(calc(-50% - 5px))'
            e.currentTarget.style.boxShadow = '0 8px 24px rgba(91, 159, 212, 0.25)'
            e.currentTarget.style.borderColor = '#4a8dc6'
            e.currentTarget.style.background = '#f8fbff'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(-50%)'
            e.currentTarget.style.boxShadow = '0 4px 16px rgba(91, 159, 212, 0.15)'
            e.currentTarget.style.borderColor = '#5b9fd4'
            e.currentTarget.style.background = '#ffffff'
          }}
        >
          <div style={{
            fontSize: '2.2rem',
            marginBottom: '0.6rem',
            fontWeight: 'bold',
            color: '#5b9fd4',
          }}>▶</div>
          <div style={{
            fontSize: '0.95rem',
            fontWeight: '700',
            color: '#1a1a1a',
            marginBottom: '0.4rem',
          }}>START</div>
          <div style={{
            fontSize: '0.8rem',
            color: '#666',
            fontWeight: '500',
          }}>Trigger Event</div>
        </div>

        {/* PROCESS Node */}
        <div
          style={{
            position: 'absolute',
            left: '50%',
            top: '50%',
            transform: 'translate(-50%, -50%)',
            width: '140px',
            background: '#ffffff',
            border: '2px solid #5b9fd4',
            borderRadius: '12px',
            padding: '1.5rem 1.25rem',
            boxShadow: '0 4px 16px rgba(91, 159, 212, 0.15)',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            textAlign: 'center',
            zIndex: 10,
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translate(-50%, calc(-50% - 5px))'
            e.currentTarget.style.boxShadow = '0 8px 24px rgba(91, 159, 212, 0.25)'
            e.currentTarget.style.borderColor = '#4a8dc6'
            e.currentTarget.style.background = '#f8fbff'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translate(-50%, -50%)'
            e.currentTarget.style.boxShadow = '0 4px 16px rgba(91, 159, 212, 0.15)'
            e.currentTarget.style.borderColor = '#5b9fd4'
            e.currentTarget.style.background = '#ffffff'
          }}
        >
          <div style={{
            fontSize: '2.2rem',
            marginBottom: '0.6rem',
            fontWeight: 'bold',
            color: '#5b9fd4',
          }}>⚙️</div>
          <div style={{
            fontSize: '0.95rem',
            fontWeight: '700',
            color: '#1a1a1a',
            marginBottom: '0.4rem',
          }}>PROCESS</div>
          <div style={{
            fontSize: '0.8rem',
            color: '#666',
            fontWeight: '500',
          }}>AI Agent Logic</div>
        </div>

        {/* RESPOND Node */}
        <div
          style={{
            position: 'absolute',
            right: '20px',
            top: '50%',
            transform: 'translateY(-50%)',
            width: '140px',
            background: '#ffffff',
            border: '2px solid #34c759',
            borderRadius: '12px',
            padding: '1.5rem 1.25rem',
            boxShadow: '0 4px 16px rgba(52, 199, 89, 0.15)',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            textAlign: 'center',
            zIndex: 10,
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(calc(-50% - 5px))'
            e.currentTarget.style.boxShadow = '0 8px 24px rgba(52, 199, 89, 0.25)'
            e.currentTarget.style.borderColor = '#2fa847'
            e.currentTarget.style.background = '#f0fdf4'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(-50%)'
            e.currentTarget.style.boxShadow = '0 4px 16px rgba(52, 199, 89, 0.15)'
            e.currentTarget.style.borderColor = '#34c759'
            e.currentTarget.style.background = '#ffffff'
          }}
        >
          <div style={{
            fontSize: '2.2rem',
            marginBottom: '0.6rem',
            fontWeight: 'bold',
            color: '#34c759',
          }}>✓</div>
          <div style={{
            fontSize: '0.95rem',
            fontWeight: '700',
            color: '#1a1a1a',
            marginBottom: '0.4rem',
          }}>RESPOND</div>
          <div style={{
            fontSize: '0.8rem',
            color: '#666',
            fontWeight: '500',
          }}>Send Output</div>
        </div>
        </div>
      </div>
    </div>
  )
}
