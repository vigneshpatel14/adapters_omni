import React from 'react'

const CHANNEL_ICONS = {
  'WhatsApp': '💬',
  'Discord': '🎮',
  'Slack': '📦',
  'Teams': '👥',
  'Instagram': '📸',
  'Telegram': '✈️',
  'LinkedIn': '💼',
  'WeChat': '🔗',
  'TikTok': '🎬',
}

export default function IntegrationsList({ integrations }) {
  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', marginBottom: '0.5rem', color: '#fff' }}>
          Active Integrations
        </h2>
        <p style={{ color: '#9090b0' }}>
          {integrations.length} channel{integrations.length !== 1 ? 's' : ''} connected
        </p>
      </div>

      <div className="integrations-grid">
        {integrations.map((integration) => (
          <div key={integration.id} className="integration-card">
            <div className="integration-icon">
              {integration.icon || CHANNEL_ICONS[integration.name] || '🔗'}
            </div>
            <div className="integration-details" style={{ flex: 1 }}>
              <h3>{integration.name}</h3>
              <p>{integration.instanceName}</p>
              <span className="status-badge">
                <span style={{ color: '#00ff96', marginRight: '0.3rem' }}>●</span>
                Active
              </span>
            </div>
            <div style={{ fontSize: '0.85rem', color: '#6060a0', textAlign: 'right' }}>
              {integration.createdAt}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
