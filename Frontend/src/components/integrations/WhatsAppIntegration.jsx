import React, { useState } from 'react'
import { toast } from 'react-toastify'
import axios from 'axios'

// Backend configuration constants
const BACKEND_CONFIG = {
  api_key: 'omni-dev-key-test-2025',
  evolution_url: 'https://evolution-api-production-7611.up.railway.app',
  evolution_key: 'VigneshKey17',
  agent_api_url: 'https://api-leodev.gep.com/leo-portal-agentic-runtime-node-api/v1/workflow-engine/e9f65742-8f61-4a7f-b0d2-71b77c5391e7/stream',
  agent_api_key: 'leo_builtin',
  default_agent: 'leo',
  agent_timeout: 120,
  webhook_base64: true,
  auto_qr: true,
}

export default function WhatsAppIntegration({ onBack, onClose, onIntegrate }) {
  const [step, setStep] = useState(1) // 1: instance name, 2: qr code, 3: success
  const [instanceName, setInstanceName] = useState('')
  const [qrData, setQrData] = useState('')
  const [loading, setLoading] = useState(false)
  const [verifying, setVerifying] = useState(false)
  const [qrImage, setQrImage] = useState('')
  const [connectionStatus, setConnectionStatus] = useState(null)
  const [normalizedName, setNormalizedName] = useState('')

  // Poll connection status until connected or timeout
  const pollConnectionStatus = async (instanceName, maxAttempts = 20) => {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const statusResponse = await axios.get(
          `http://localhost:8882/api/v1/instances/${instanceName}/status`,
          { headers: { 'x-api-key': BACKEND_CONFIG.api_key } }
        )
        
        console.log(`Status check attempt ${attempt + 1}:`, statusResponse.data)
        
        if (statusResponse.data.status === 'connected') {
          console.log('✓ WhatsApp connected successfully!')
          console.log('Profile:', {
            name: statusResponse.data.channel_data?.profile_name,
            jid: statusResponse.data.channel_data?.owner_jid,
            picture: statusResponse.data.channel_data?.profile_picture_url
          })
          setConnectionStatus({
            status: 'connected',
            data: statusResponse.data.channel_data
          })
          return true
        } else if (statusResponse.data.status === 'error') {
          console.error('Connection error:', statusResponse.data.channel_data?.error)
          setConnectionStatus({
            status: 'error',
            error: statusResponse.data.channel_data?.error || 'Unknown error'
          })
          return false
        }
        
        // Still connecting, wait 2 seconds before next attempt
        console.log(`Still connecting... (${attempt + 1}/${maxAttempts})`)
        await new Promise(resolve => setTimeout(resolve, 2000))
      } catch (error) {
        console.error(`Status check attempt ${attempt + 1} failed:`, error)
        if (attempt === maxAttempts - 1) {
          setConnectionStatus({
            status: 'error',
            error: 'Could not verify connection status after timeout'
          })
          return false
        }
        await new Promise(resolve => setTimeout(resolve, 2000))
      }
    }
    
    setConnectionStatus({
      status: 'timeout',
      error: 'Connection verification timed out. Please scan the QR code.'
    })
    return false
  }

  const handleCreateInstance = async () => {
    if (!instanceName.trim()) {
      toast.error('Please enter an instance name')
      return
    }

    setLoading(true)
    setConnectionStatus(null)
    try {
      // Step 1: Create the instance
      const createResponse = await axios.post('http://localhost:8882/api/v1/instances', {
        name: instanceName,
        channel_type: 'whatsapp',
        evolution_url: BACKEND_CONFIG.evolution_url,
        evolution_key: BACKEND_CONFIG.evolution_key,
        agent_api_url: BACKEND_CONFIG.agent_api_url,
        agent_api_key: BACKEND_CONFIG.agent_api_key,
        default_agent: BACKEND_CONFIG.default_agent,
        agent_timeout: BACKEND_CONFIG.agent_timeout,
        webhook_base64: BACKEND_CONFIG.webhook_base64,
        auto_qr: BACKEND_CONFIG.auto_qr,
      }, {
        headers: {
          'x-api-key': BACKEND_CONFIG.api_key,
          'Content-Type': 'application/json',
        }
      })

      console.log('Instance created:', createResponse.data)

      // Step 2: Fetch the QR code from the dedicated endpoint
      const normalized = createResponse.data.name || instanceName.toLowerCase()
      setNormalizedName(normalized)

      const qrResponse = await axios.get(
        `http://localhost:8882/api/v1/instances/${normalized}/qr`,
        {
          headers: {
            'x-api-key': BACKEND_CONFIG.api_key,
          }
        }
      )

      console.log('QR code response:', qrResponse.data)

      if (qrResponse.data && qrResponse.data.qr_code) {
        setQrData(qrResponse.data.qr_code)
        // The backend returns it as data:image/png;base64,...
        setQrImage(qrResponse.data.qr_code)
        setStep(2)
        toast.success('✓ Instance created! Scan the QR code with your WhatsApp app.')
      } else {
        toast.error('❌ Failed to fetch QR code')
      }
    } catch (error) {
      console.error('Error creating instance:', error)
      
      // Extract error message from backend response
      let errorMessage = 'Failed to create instance'
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      }
      
      // Log full error for debugging
      console.error('Full error response:', error.response)
      
      toast.error(`❌ ${errorMessage}`)
    } finally {
      setLoading(false)
    }
  }

  const handleScanned = async () => {
    setVerifying(true)
    setConnectionStatus(null)
    
    try {
      console.log(`Starting connection verification for instance: ${normalizedName}`)
      const isConnected = await pollConnectionStatus(normalizedName)
      
      if (!isConnected && connectionStatus?.status !== 'connected') {
        const errorMsg = connectionStatus?.error || 'Failed to verify connection'
        toast.error(`⚠️ Connection verification failed: ${errorMsg}`)
        setVerifying(false)
        return
      }

      // Connected successfully
      setStep(3)
      toast.success('✓ WhatsApp successfully connected!')
      setTimeout(() => {
        onIntegrate({
          id: `whatsapp-${Date.now()}`,
          name: instanceName || 'WhatsApp',
          type: 'whatsapp',
          icon: '💬',
          status: 'active',
          createdAt: new Date().toLocaleDateString(),
        })
        onClose()
      }, 1500)
    } finally {
      setVerifying(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h2>WhatsApp Integration</h2>
            <p style={{ fontSize: '0.9rem', color: '#9090b0', marginTop: '0.3rem' }}>
              Connect via QR code scanning
            </p>
          </div>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        {step === 1 && (
          <div>
            <div className="form-group">
              <label>Instance Name</label>
              <input
                type="text"
                placeholder="e.g., Support Bot, Sales Channel..."
                value={instanceName}
                onChange={(e) => setInstanceName(e.target.value)}
                disabled={loading}
              />
              <p style={{ fontSize: '0.85rem', color: '#6060a0', marginTop: '0.4rem' }}>
                Give this connection a memorable name
              </p>
            </div>

            <div className="form-actions">
              <button className="btn btn-cancel" onClick={onBack}>
                Back
              </button>
              <button
                className="btn btn-primary"
                onClick={handleCreateInstance}
                disabled={loading || !instanceName.trim()}
              >
                {loading ? <span className="loading"></span> : 'Generate QR Code'}
              </button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div>
            <div className="qr-container">
              {qrImage ? (
                <div className="qr-code-box">
                  <img src={qrImage} alt="QR Code" style={{ width: '250px', height: '250px' }} />
                </div>
              ) : (
                <div className="qr-code-box">
                  <div style={{ width: '250px', height: '250px', background: '#f0f0f0', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <p>Loading QR Code...</p>
                  </div>
                </div>
              )}
              <div className="qr-instructions">
                <p>📱 Open WhatsApp on your phone</p>
                <p>➡️ Go to Settings → Linked Devices → Link a Device</p>
                <p>📸 Scan this QR code with your phone</p>
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
                  Verifying WhatsApp connection...
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
                  ✓ Connected! Phone: {connectionStatus.data?.profile_name || 'WhatsApp'}
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
            </div>

            <div className="form-actions">
              <button className="btn btn-cancel" onClick={() => setStep(1)} disabled={verifying}>
                Change Instance
              </button>
              <button 
                className="btn btn-primary" 
                onClick={handleScanned}
                disabled={verifying}
              >
                {verifying ? (
                  <>
                    <span className="loading" style={{ marginRight: '0.5rem' }}></span>
                    Verifying...
                  </>
                ) : (
                  "I've Scanned the Code"
                )}
              </button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div style={{ textAlign: 'center', padding: '2rem 0' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>✓</div>
            <h3 style={{ color: '#1a1a1a', marginBottom: '0.5rem' }}>Connected Successfully!</h3>
            <p style={{ color: '#666', marginBottom: '2rem' }}>
              Your WhatsApp instance "{instanceName}" is now active
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
