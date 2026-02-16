import React, { useState, useEffect } from 'react'
import { toast, ToastContainer } from 'react-toastify'
import axios from 'axios'
import 'react-toastify/dist/ReactToastify.css'
import './App.css'
import ChannelModal from './components/ChannelModal.jsx'
import WorkflowBuilder from './components/WorkflowBuilder.jsx'

const API_BASE = 'http://localhost:8882/api/v1'
const API_KEY = 'omni-dev-key-test-2025'

function App() {
  const [showModal, setShowModal] = useState(false)
  const [showInstancesPanel, setShowInstancesPanel] = useState(false)
  const [instances, setInstances] = useState([])
  const [openMenuId, setOpenMenuId] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [renameMode, setRenameMode] = useState(null)
  const [renamingInstanceName, setRenamingInstanceName] = useState('')

  // Load instances from API
  const loadInstances = async () => {
    try {
      setIsLoading(true)
      const response = await axios.get(`${API_BASE}/instances/`, {
        headers: { 'x-api-key': API_KEY }
      })
      setInstances(response.data || [])
    } catch (error) {
      console.error('Failed to load instances:', error)
      toast.error('✗ Failed to load instances')
    } finally {
      setIsLoading(false)
    }
  }

  // Load instances on mount
  useEffect(() => {
    loadInstances()
  }, [])

  const handleMenuToggle = (instanceName) => {
    setOpenMenuId(openMenuId === instanceName ? null : instanceName)
  }

  const handleRemoveInstance = async (instanceName) => {
    if (!window.confirm(`Are you sure you want to remove "${instanceName}"?`)) {
      return
    }

    try {
      await axios.delete(`${API_BASE}/instances/${instanceName}`, {
        headers: { 'x-api-key': API_KEY }
      })
      toast.success(`✓ Instance "${instanceName}" removed successfully`)
      setOpenMenuId(null)
      loadInstances() // Refresh list
    } catch (error) {
      console.error('Failed to remove instance:', error)
      const errorMsg = error.response?.data?.message || error.message
      toast.error(`✗ Failed to remove instance: ${errorMsg}`)
    }
  }

  const handleRenameInstance = async (oldName, newName) => {
    if (!newName.trim()) {
      toast.error('✗ Instance name cannot be empty')
      return
    }

    if (newName === oldName) {
      setRenameMode(null)
      setRenamingInstanceName('')
      return
    }

    try {
      // POST to /instances/{oldName} with new name in body
      await axios.post(`${API_BASE}/instances/${oldName}`, {
        name: newName
      }, {
        headers: { 'x-api-key': API_KEY }
      })
      toast.success(`✓ Instance renamed to "${newName}"`)
      setRenameMode(null)
      setRenamingInstanceName('')
      setOpenMenuId(null)
      loadInstances() // Refresh list
    } catch (error) {
      console.error('Failed to rename instance:', error)
      const errorMsg = error.response?.data?.message || error.message
      toast.error(`✗ Failed to rename instance: ${errorMsg}`)
    }
  }

  const handleIntegrationComplete = (newIntegration) => {
    // Refresh instances from API instead of using state
    toast.success(`✓ Instance "${newIntegration.name}" created successfully`)
    setShowModal(false)
    loadInstances()
  }

  return (
    <div className="app-container">
      <ToastContainer
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop={true}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="dark"
      />

      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">Leo Workflow Engine</h1>
          <p className="app-subtitle">AI-powered workflow automation</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button
            onClick={() => setShowInstancesPanel(true)}
            style={{
              padding: '0.75rem 1.5rem',
              background: '#ffffff',
              border: '2px solid #5b9fd4',
              borderRadius: '0.5rem',
              color: '#5b9fd4',
              fontSize: '1rem',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              boxShadow: '0 2px 8px rgba(91, 159, 212, 0.1)',
            }}
            onMouseEnter={(e) => {
              e.target.style.background = '#f8fbff'
              e.target.style.boxShadow = '0 4px 14px rgba(91, 159, 212, 0.2)'
            }}
            onMouseLeave={(e) => {
              e.target.style.background = '#ffffff'
              e.target.style.boxShadow = '0 2px 8px rgba(91, 159, 212, 0.1)'
            }}
          >
            📋 Connected Instances - {instances.length || 0}
          </button>
          <button
            className="run-btn"
            onClick={() => {
              // Placeholder for run functionality
              console.log('Running workflow...')
            }}
            style={{
              padding: '0.75rem 1.5rem',
              background: 'linear-gradient(135deg, #34c759 0%, #2fa847 100%)',
              border: 'none',
              borderRadius: '0.5rem',
              color: '#fff',
              fontSize: '1rem',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              boxShadow: '0 2px 8px rgba(52, 199, 89, 0.2)',
            }}
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-2px)'
              e.target.style.boxShadow = '0 4px 14px rgba(52, 199, 89, 0.3)'
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)'
              e.target.style.boxShadow = '0 2px 8px rgba(52, 199, 89, 0.2)'
            }}
          >
            ▶ Run
          </button>
          <button
            className="integrate-btn"
            onClick={() => setShowModal(true)}
            style={{
              padding: '0.75rem 1.5rem',
              background: 'linear-gradient(135deg, #5b9fd4 0%, #4a8dc6 100%)',
              border: 'none',
              borderRadius: '0.5rem',
              color: '#fff',
              fontSize: '1rem',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              boxShadow: '0 2px 8px rgba(91, 159, 212, 0.2)',
            }}
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-2px)'
              e.target.style.boxShadow = '0 4px 14px rgba(91, 159, 212, 0.3)'
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)'
              e.target.style.boxShadow = '0 2px 8px rgba(91, 159, 212, 0.2)'
            }}
          >
            + Integrate
          </button>
        </div>
      </header>

      <main className="app-main">
        <WorkflowBuilder />
      </main>

      {/* Connected Instances Modal */}
      {showInstancesPanel && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'flex-end',
            zIndex: 2000,
          }}
          onClick={() => setShowInstancesPanel(false)}
        >
          <div
            style={{
              width: '420px',
              height: '100%',
              background: '#ffffff',
              display: 'flex',
              flexDirection: 'column',
              boxShadow: '-4px 0 20px rgba(0, 0, 0, 0.15)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div
              style={{
                padding: '1.5rem',
                borderBottom: '1px solid #e5e5e7',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <h2 style={{ margin: 0, color: '#1a1a1a', fontSize: '1.3rem', fontWeight: '700' }}>
                Connected Instances
              </h2>
              <button
                onClick={() => setShowInstancesPanel(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '1.5rem',
                  cursor: 'pointer',
                  color: '#666',
                }}
              >
                ✕
              </button>
            </div>

            {/* Content */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem' }}>
              {isLoading ? (
                <div
                  style={{
                    padding: '2rem 1rem',
                    textAlign: 'center',
                    color: '#999',
                    fontSize: '0.95rem',
                  }}
                >
                  <p style={{ margin: '0' }}>Loading instances...</p>
                </div>
              ) : instances.length === 0 ? (
                <div
                  style={{
                    padding: '2rem 1rem',
                    textAlign: 'center',
                    color: '#999',
                    fontSize: '0.95rem',
                  }}
                >
                  <p style={{ margin: '0 0 1rem 0', fontSize: '2rem' }}>🔌</p>
                  <p style={{ margin: '0 0 0.5rem 0' }}>No instances yet</p>
                  <p style={{ margin: 0, fontSize: '0.85rem' }}>Click "Integrate" to add your first connection</p>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {instances.map((instance) => (
                    <div
                      key={instance.name}
                      style={{
                        background: '#f9f9fb',
                        border: '1px solid #e5e5e7',
                        borderRadius: '0.75rem',
                        padding: '1.25rem',
                        position: 'relative',
                        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
                        transition: 'all 0.3s ease',
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.boxShadow = '0 4px 12px rgba(91, 159, 212, 0.1)'
                        e.currentTarget.style.borderColor = '#5b9fd4'
                        e.currentTarget.style.background = '#ffffff'
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.05)'
                        e.currentTarget.style.borderColor = '#e5e5e7'
                        e.currentTarget.style.background = '#f9f9fb'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div style={{ flex: 1 }}>
                          {renameMode === instance.name ? (
                            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '0.5rem' }}>
                              <input
                                autoFocus
                                type="text"
                                value={renamingInstanceName}
                                onChange={(e) => setRenamingInstanceName(e.target.value)}
                                onKeyDown={(e) => {
                                  if (e.key === 'Enter') {
                                    handleRenameInstance(instance.name, renamingInstanceName)
                                  } else if (e.key === 'Escape') {
                                    setRenameMode(null)
                                    setRenamingInstanceName('')
                                  }
                                }}
                                style={{
                                  padding: '0.5rem',
                                  border: '1px solid #5b9fd4',
                                  borderRadius: '0.35rem',
                                  fontSize: '0.9rem',
                                  flex: 1,
                                }}
                                placeholder="New instance name"
                              />
                              <button
                                onClick={() => handleRenameInstance(instance.name, renamingInstanceName)}
                                style={{
                                  padding: '0.5rem 0.75rem',
                                  background: '#34c759',
                                  color: '#fff',
                                  border: 'none',
                                  borderRadius: '0.35rem',
                                  cursor: 'pointer',
                                  fontSize: '0.8rem',
                                }}
                              >
                                ✓
                              </button>
                              <button
                                onClick={() => {
                                  setRenameMode(null)
                                  setRenamingInstanceName('')
                                }}
                                style={{
                                  padding: '0.5rem 0.75rem',
                                  background: '#d70015',
                                  color: '#fff',
                                  border: 'none',
                                  borderRadius: '0.35rem',
                                  cursor: 'pointer',
                                  fontSize: '0.8rem',
                                }}
                              >
                                ✕
                              </button>
                            </div>
                          ) : (
                            <p
                              style={{
                                margin: '0 0 0.5rem 0',
                                fontWeight: '600',
                                color: '#1a1a1a',
                                fontSize: '0.95rem',
                              }}
                            >
                              {instance.type === 'whatsapp' ? '💬' : '🎮'} {instance.name}
                            </p>
                          )}
                          <p style={{ margin: '0', fontSize: '0.8rem', color: '#666' }}>
                            {instance.type === 'whatsapp' ? 'WhatsApp Instance' : 'Discord Bot'}
                          </p>
                          {instance.status && (
                            <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.75rem', color: '#666' }}>
                              Status: <span style={{ color: instance.status === 'connected' ? '#34c759' : '#ff9500' }}>
                                {instance.status}
                              </span>
                            </p>
                          )}
                        </div>
                        <div style={{ position: 'relative' }}>
                          <button
                            onClick={() => handleMenuToggle(instance.name)}
                            style={{
                              background: 'none',
                              border: 'none',
                              fontSize: '1.2rem',
                              cursor: 'pointer',
                              padding: '0',
                              color: '#666',
                              transition: 'color 0.3s ease',
                            }}
                            onMouseEnter={(e) => (e.currentTarget.style.color = '#5b9fd4')}
                            onMouseLeave={(e) => (e.currentTarget.style.color = '#666')}
                          >
                            ⋯
                          </button>

                          {/* Dropdown Menu */}
                          {openMenuId === instance.name && (
                            <div
                              style={{
                                position: 'absolute',
                                top: '100%',
                                right: '0',
                                marginTop: '0.25rem',
                                background: '#ffffff',
                                border: '1px solid #e5e5e7',
                                borderRadius: '0.5rem',
                                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
                                zIndex: 1000,
                                minWidth: '140px',
                                overflow: 'hidden',
                              }}
                            >
                              <button
                                onClick={() => {
                                  setRenameMode(instance.name)
                                  setRenamingInstanceName(instance.name)
                                  setOpenMenuId(null)
                                }}
                                style={{
                                  width: '100%',
                                  padding: '0.75rem 1rem',
                                  border: 'none',
                                  background: 'none',
                                  textAlign: 'left',
                                  cursor: 'pointer',
                                  fontSize: '0.9rem',
                                  color: '#5b9fd4',
                                  transition: 'background 0.2s ease',
                                  borderBottom: '1px solid #e5e5e7',
                                }}
                                onMouseEnter={(e) => (e.currentTarget.style.background = '#f9f9fb')}
                                onMouseLeave={(e) => (e.currentTarget.style.background = 'none')}
                              >
                                ✏️ Rename
                              </button>
                              <button
                                onClick={() => {
                                  console.log('Disconnect instance', instance.name)
                                  setOpenMenuId(null)
                                }}
                                style={{
                                  width: '100%',
                                  padding: '0.75rem 1rem',
                                  border: 'none',
                                  background: 'none',
                                  textAlign: 'left',
                                  cursor: 'pointer',
                                  fontSize: '0.9rem',
                                  color: '#ff9500',
                                  transition: 'background 0.2s ease',
                                  borderBottom: '1px solid #e5e5e7',
                                }}
                                onMouseEnter={(e) => (e.currentTarget.style.background = '#fffaf0')}
                                onMouseLeave={(e) => (e.currentTarget.style.background = 'none')}
                              >
                                🔌 Disconnect
                              </button>
                              <button
                                onClick={() => handleRemoveInstance(instance.name)}
                                style={{
                                  width: '100%',
                                  padding: '0.75rem 1rem',
                                  border: 'none',
                                  background: 'none',
                                  textAlign: 'left',
                                  cursor: 'pointer',
                                  fontSize: '0.9rem',
                                  color: '#d70015',
                                  transition: 'background 0.2s ease',
                                }}
                                onMouseEnter={(e) => (e.currentTarget.style.background = '#fff5f5')}
                                onMouseLeave={(e) => (e.currentTarget.style.background = 'none')}
                              >
                                🗑️ Remove
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {showModal && (
        <ChannelModal
          onClose={() => setShowModal(false)}
          onIntegrate={handleIntegrationComplete}
        />
      )}
    </div>
  )
}

export default App
