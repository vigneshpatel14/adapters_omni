import React, { useState } from 'react'
import WhatsAppIntegration from './integrations/WhatsAppIntegration.jsx'
import DiscordIntegration from './integrations/DiscordIntegration.jsx'

const CHANNELS = [
  { id: 'whatsapp', name: 'WhatsApp', icon: '💬', description: 'Connect via QR code scanning' },
  { id: 'discord', name: 'Discord', icon: '🎮', description: 'Bot integration with token' },
  { id: 'slack', name: 'Slack', icon: '📦', description: 'Workspace app integration' },
  { id: 'teams', name: 'Microsoft Teams', icon: '👥', description: 'Enterprise team communication' },
  { id: 'instagram', name: 'Instagram', icon: '📸', description: 'Instagram Direct Messages' },
  { id: 'telegram', name: 'Telegram', icon: '✈️', description: 'Telegram Bot integration' },
  { id: 'linkedin', name: 'LinkedIn', icon: '💼', description: 'LinkedIn messaging' },
  { id: 'wechat', name: 'WeChat', icon: '🔗', description: 'WeChat Official Account' },
  { id: 'tiktok', name: 'TikTok', icon: '🎬', description: 'TikTok Direct Messages' },
]

export default function ChannelModal({ onClose, onIntegrate }) {
  const [selectedChannel, setSelectedChannel] = useState(null)

  if (selectedChannel === 'whatsapp') {
    return (
      <WhatsAppIntegration
        onBack={() => setSelectedChannel(null)}
        onClose={onClose}
        onIntegrate={onIntegrate}
      />
    )
  }

  if (selectedChannel === 'discord') {
    return (
      <DiscordIntegration
        onBack={() => setSelectedChannel(null)}
        onClose={onClose}
        onIntegrate={onIntegrate}
      />
    )
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Select a Channel to Integrate</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="channels-grid">
          {CHANNELS.map((channel) => (
            <div
              key={channel.id}
              className={`channel-card ${!['whatsapp', 'discord'].includes(channel.id) ? 'disabled' : ''}`}
              onClick={() => {
                if (['whatsapp', 'discord'].includes(channel.id)) {
                  setSelectedChannel(channel.id)
                }
              }}
            >
              <div className="channel-icon">{channel.icon}</div>
              <div className="channel-info">
                <h3>{channel.name}</h3>
                <p>{channel.description}</p>
              </div>
              {!['whatsapp', 'discord'].includes(channel.id) && (
                <span className="coming-soon">Coming Soon</span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
