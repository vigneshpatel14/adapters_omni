import React, { useState } from 'react'
import { toast } from 'react-toastify'
import axios from 'axios'

// Backend configuration constants for Discord
const BACKEND_CONFIG = {
  api_key: 'omni-dev-key-test-2025',
  agent_api_url: 'https://api-leodev.gep.com/leo-portal-agentic-runtime-node-api/v1/workflow-engine/e9f65742-8f61-4a7f-b0d2-71b77c5391e7/stream',
  agent_api_key: 'leo_builtin',
  default_agent: 'leo',
  agent_timeout: 120,
  webhook_base64: true,
  discord_voice_enabled: false,
  discord_slash_commands_enabled: true,
}

export default function DiscordIntegration({ onBack, onClose, onIntegrate }) {
  const [instanceName, setInstanceName] = useState('')
  const [botToken, setBotToken] = useState('')
  const [clientId, setClientId] = useState('')
  const [guildId, setGuildId] = useState('')
  const [defaultChannelId, setDefaultChannelId] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [verifying, setVerifying] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState(null)

  // Validate Discord bot token format (basic check: should be long alphanumeric string with dots)
  const isValidBotToken = (token) => {
    return token && token.length > 50 && token.includes('.')
  }

  // Validate Discord Client ID format (should be numeric)
  const isValidClientId = (id) => {
    return id && /^\d+$/.test(id) && id.length >= 15
  }

  // Poll connection status until connected or timeout
  const pollConnectionStatus = async (instanceName, maxAttempts = 15) => {
    let finalStatus = null
    
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const statusResponse = await axios.get(
          `http://localhost:8882/api/v1/instances/${instanceName}/status`,
          { headers: { 'x-api-key': BACKEND_CONFIG.api_key } }
        )
        
        console.log(`Status check attempt ${attempt + 1}:`, statusResponse.data)
        
        if (statusResponse.data.status === 'connected') {
          console.log('✓ Discord bot connected successfully!')
          finalStatus = {
            status: 'connected',
            data: statusResponse.data.channel_data
          }
          setConnectionStatus(finalStatus)
          return true
        } else if (statusResponse.data.status === 'starting') {
          // Bot is initializing - keep this as the current status
          console.log('✓ Discord bot is initializing (starting status accepted)')
          finalStatus = {
            status: 'starting',
            data: statusResponse.data.channel_data
          }
          // Keep polling but don't return yet - wait to see if it connects
          console.log(`Still initializing... (${attempt + 1}/${maxAttempts})`)
          await new Promise(resolve => setTimeout(resolve, 1500))
          continue
        } else if (statusResponse.data.status === 'error') {
          console.error('Connection error:', statusResponse.data.channel_data?.error)
          finalStatus = {
            status: 'error',
            error: statusResponse.data.channel_data?.error || 'Unknown error'
          }
          setConnectionStatus(finalStatus)
          return false
        }
        
        // Wait 1.5 seconds before next attempt
        await new Promise(resolve => setTimeout(resolve, 1500))
      } catch (error) {
        console.error(`Status check attempt ${attempt + 1} failed:`, error)
        if (attempt === maxAttempts - 1) {
          finalStatus = {
            status: 'error',
            error: 'Could not verify connection status'
          }
          setConnectionStatus(finalStatus)
          return false
        }
        await new Promise(resolve => setTimeout(resolve, 1500))
      }
    }
    
    // After max attempts, use whatever final status we got
    if (finalStatus) {
      setConnectionStatus(finalStatus)
      // Accept 'starting' status as valid (bot is initializing)
      if (finalStatus.status === 'starting') {
        return true
      }
    } else {
      setConnectionStatus({
        status: 'timeout',
        error: 'Connection verification timed out. Bot may still be connecting.'
      })
    }
    
    return false
  }

  const handleConnect = async () => {
    // Frontend validation
    if (!instanceName.trim()) {
      toast.error('❌ Please enter an instance name')
      return
    }
    
    if (!botToken.trim()) {
      toast.error('❌ Please enter your Discord bot token')
      return
    }
    
    if (!clientId.trim()) {
      toast.error('❌ Please enter your Discord client ID')
      return
    }

    // Validate token format
    if (!isValidBotToken(botToken)) {
      toast.error('❌ Invalid bot token format. Should be a long string with dots (e.g., token.XXXX.YYYY)')
      return
    }

    // Validate client ID format
    if (!isValidClientId(clientId)) {
      toast.error('❌ Invalid client ID. Should be a numeric snowflake ID (at least 15 digits)')
      return
    }

    setLoading(true)
    setConnectionStatus(null)
    
    try {
      // Step 1: Create Discord instance
      console.log('Creating Discord instance with token and client_id...')
      const createResponse = await axios.post('http://localhost:8882/api/v1/instances', {
        name: instanceName,
        channel_type: 'discord',
        discord_bot_token: botToken,  // Note: correct field name is discord_bot_token
        discord_client_id: clientId,
        discord_guild_id: guildId || null,
        discord_default_channel_id: defaultChannelId || null,
        webhook_base64: BACKEND_CONFIG.webhook_base64,
        discord_voice_enabled: BACKEND_CONFIG.discord_voice_enabled,
        discord_slash_commands_enabled: BACKEND_CONFIG.discord_slash_commands_enabled,
        agent_api_url: BACKEND_CONFIG.agent_api_url,
        agent_api_key: BACKEND_CONFIG.agent_api_key,
        default_agent: BACKEND_CONFIG.default_agent,
        agent_timeout: BACKEND_CONFIG.agent_timeout,
      }, {
        headers: {
          'x-api-key': BACKEND_CONFIG.api_key,
          'Content-Type': 'application/json',
        }
      })

      console.log('Instance created response:', createResponse.data)
      
      // Toast 1: Instance created successfully
      toast.success('✅ Instance created successfully!')
      
      // Toast 2: Show buffering/verification state
      toast.loading('🔄 Verifying bot token and connecting...', { autoClose: false })
      
      // Step 2: Verify connection status
      setVerifying(true)
      const normalizedName = createResponse.data.name || instanceName.toLowerCase()
      const isConnected = await pollConnectionStatus(normalizedName)
      
      // Close the loading toast and show final status
      toast.dismiss()
      
      // Check the verification result
      if (isConnected) {
        // Successfully verified
        if (connectionStatus?.status === 'connected') {
          // Successfully connected
          toast.success(`✅ Bot "${instanceName}" connected successfully!`)
        } else if (connectionStatus?.status === 'starting') {
          // Still initializing, but instance was created successfully
          toast.info(`⏳ Bot "${instanceName}" is initializing... (may take up to 30 seconds)`)
        }
      } else {
        // Verification failed
        const errorMsg = connectionStatus?.error || 'Failed to verify connection'
        toast.error(`❌ Connection failed: ${errorMsg}`)
        setLoading(false)
        setVerifying(false)
        return
      }
      
      setTimeout(() => {
        onIntegrate({
          id: `discord-${Date.now()}`,
          name: instanceName || 'Discord Bot',
          type: 'discord',
          icon: '🎮',
          botId: connectionStatus?.data?.bot_id,
          status: 'active',
          createdAt: new Date().toLocaleDateString(),
        })
        onClose()
      }, 1500)
    } catch (error) {
      console.error('Error creating Discord instance:', error)
      
      // Close loading toast if still open
      toast.dismiss()
      
      // Extract detailed error message
      let errorMessage = 'Failed to create Discord instance'
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      } else if (error.message) {
        errorMessage = error.message
      }
      
      // Log full error for debugging
      console.error('Full error response:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      })
      
      toast.error(`❌ ${errorMessage}`)
    } finally {
      setLoading(false)
      setVerifying(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h2>Discord Integration</h2>
            <p style={{ fontSize: '0.9rem', color: '#9090b0', marginTop: '0.3rem' }}>
              Bot authentication via developer credentials
            </p>
          </div>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="form-group">
          <label>Instance Name</label>
          <input
            type="text"
            placeholder="e.g., Community Bot, Alerts Bot..."
            value={instanceName}
            onChange={(e) => setInstanceName(e.target.value)}
            disabled={loading || verifying}
          />
          <p style={{ fontSize: '0.85rem', color: '#6060a0', marginTop: '0.4rem' }}>
            Give this bot connection a memorable name
          </p>
        </div>

        <div className="form-group">
          <label>Bot Token *</label>
          <div style={{ position: 'relative' }}>
            <input
              type={showPassword ? 'text' : 'password'}
              placeholder="Enter your Discord bot token"
              value={botToken}
              onChange={(e) => setBotToken(e.target.value)}
              disabled={loading || verifying}
              style={{ borderColor: botToken && !isValidBotToken(botToken) ? '#ff6b6b' : undefined }}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              style={{
                position: 'absolute',
                right: '1rem',
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'none',
                border: 'none',
                color: '#9090b0',
                cursor: 'pointer',
                fontSize: '1.1rem'
              }}
            >
              {showPassword ? '🙈' : '👁️'}
            </button>
          </div>
          {botToken && !isValidBotToken(botToken) && (
            <p style={{ fontSize: '0.85rem', color: '#ff6b6b', marginTop: '0.4rem' }}>
              ⚠️ Token format invalid. Should be a long string with dots.
            </p>
          )}
          {!botToken && (
            <p style={{ fontSize: '0.85rem', color: '#6060a0', marginTop: '0.4rem' }}>
              Get from{' '}
              <a href="https://discord.com/developers/applications" target="_blank" rel="noopener noreferrer"
                style={{ color: '#00d4ff', textDecoration: 'none' }}>
                Discord Developer Portal → Bot → Copy Token
              </a>
            </p>
          )}
        </div>

        <div className="form-group">
          <label>Client ID *</label>
          <input
            type="text"
            placeholder="Enter your Discord application client ID"
            value={clientId}
            onChange={(e) => setClientId(e.target.value)}
            disabled={loading || verifying}
            style={{ borderColor: clientId && !isValidClientId(clientId) ? '#ff6b6b' : undefined }}
          />
          {clientId && !isValidClientId(clientId) && (
            <p style={{ fontSize: '0.85rem', color: '#ff6b6b', marginTop: '0.4rem' }}>
              ⚠️ Client ID invalid. Should be a numeric snowflake (15+ digits).
            </p>
          )}
          {!clientId && (
            <p style={{ fontSize: '0.85rem', color: '#6060a0', marginTop: '0.4rem' }}>
              Get from{' '}
              <a href="https://discord.com/developers/applications" target="_blank" rel="noopener noreferrer"
                style={{ color: '#00d4ff', textDecoration: 'none' }}>
                Discord Developer Portal → Application
              </a>
            </p>
          )}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div className="form-group">
            <label>Guild ID (optional)</label>
            <input
              type="text"
              placeholder="Your server ID (if specific server)"
              value={guildId}
              onChange={(e) => setGuildId(e.target.value)}
              disabled={loading || verifying}
            />
            <p style={{ fontSize: '0.85rem', color: '#6060a0', marginTop: '0.4rem' }}>
              Optional: Restrict to specific server
            </p>
          </div>

          <div className="form-group">
            <label>Default Channel ID (optional)</label>
            <input
              type="text"
              placeholder="Channel ID for messages"
              value={defaultChannelId}
              onChange={(e) => setDefaultChannelId(e.target.value)}
              disabled={loading || verifying}
            />
            <p style={{ fontSize: '0.85rem', color: '#6060a0', marginTop: '0.4rem' }}>
              Optional: Default message channel
            </p>
          </div>
        </div>

        {verifying && (
          <div style={{
            padding: '1rem',
            marginTop: '1rem',
            background: '#f0f7fc',
            borderLeft: '3px solid #5b9fd4',
            borderRadius: '0.5rem',
            fontSize: '0.9rem',
            color: '#5b9fd4'
          }}>
            <span className="loading" style={{ marginRight: '0.5rem' }}></span>
            Verifying Discord bot connection...
          </div>
        )}

        {connectionStatus?.status === 'connected' && (
          <div style={{
            padding: '1rem',
            marginTop: '1rem',
            background: '#f0fdf4',
            borderLeft: '3px solid #34c759',
            borderRadius: '0.5rem',
            fontSize: '0.9rem',
            color: '#34c759'
          }}>
            ✓ Bot connected successfully!
            {connectionStatus.data?.bot_id && ` (Bot ID: ${connectionStatus.data.bot_id})`}
          </div>
        )}

        {connectionStatus?.status === 'error' && (
          <div style={{
            padding: '1rem',
            marginTop: '1rem',
            background: '#fff5f5',
            borderLeft: '3px solid #d70015',
            borderRadius: '0.5rem',
            fontSize: '0.9rem',
            color: '#d70015'
          }}>
            ❌ Connection failed: {connectionStatus.error}
          </div>
        )}

        <div className="form-actions">
          <button className="btn btn-cancel" onClick={onBack} disabled={loading || verifying}>
            Back
          </button>
          <button
            className="btn btn-primary"
            onClick={handleConnect}
            disabled={
              loading || 
              verifying ||
              !instanceName.trim() || 
              !botToken.trim() ||
              !clientId.trim() ||
              !isValidBotToken(botToken) ||
              !isValidClientId(clientId)
            }
          >
            {verifying ? (
              <>
                <span className="loading" style={{ marginRight: '0.5rem' }}></span>
                Verifying...
              </>
            ) : loading ? (
              <>
                <span className="loading" style={{ marginRight: '0.5rem' }}></span>
                Creating...
              </>
            ) : (
              'Connect Bot'
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
