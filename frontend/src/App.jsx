import { useState, useEffect } from 'react'
import heroImg from './assets/hero.png'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import { checkBackendHealth, API_BASE_URL } from './api/client'
import './App.css'

function App() {
  const [count, setCount] = useState(0)
  const [backendStatus, setBackendStatus] = useState({
    loading: true,
    connected: false,
    data: null,
    error: null,
  })

  const testConnection = async () => {
    setBackendStatus((prev) => ({ ...prev, loading: true }))
    const result = await checkBackendHealth()
    if (result.success) {
      setBackendStatus({
        loading: false,
        connected: true,
        data: result.data,
        error: null,
      })
    } else {
      setBackendStatus({
        loading: false,
        connected: false,
        data: null,
        error: result.error,
      })
    }
  }

  useEffect(() => {
    let isMounted = true
    checkBackendHealth().then((result) => {
      if (!isMounted) return
      if (result.success) {
        setBackendStatus({
          loading: false,
          connected: true,
          data: result.data,
          error: null,
        })
      } else {
        setBackendStatus({
          loading: false,
          connected: false,
          data: null,
          error: result.error,
        })
      }
    })
    return () => {
      isMounted = false
    }
  }, [])


  return (
    <>
      <section id="center">
        <div className="hero">
          <img src={heroImg} className="base" width="170" height="179" alt="" />
          <img src={reactLogo} className="framework" alt="React logo" />
          <img src={viteLogo} className="vite" alt="Vite logo" />
        </div>
        <div>
          <h1>OBE Tracking System</h1>
          <p>React Frontend + FastAPI Backend Integration</p>
        </div>

        {/* Backend Connectivity Status Card */}
        <div
          style={{
            padding: '16px 24px',
            borderRadius: '12px',
            border: `1px solid ${backendStatus.connected ? '#10b981' : backendStatus.loading ? '#6366f1' : '#ef4444'}`,
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(8px)',
            maxWidth: '520px',
            width: '100%',
            textAlign: 'center',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginBottom: '8px' }}>
            <span
              style={{
                width: '10px',
                height: '10px',
                borderRadius: '50%',
                backgroundColor: backendStatus.connected ? '#10b981' : backendStatus.loading ? '#eab308' : '#ef4444',
                display: 'inline-block',
              }}
            />
            <strong style={{ fontSize: '15px' }}>
              Backend Status: {backendStatus.loading ? 'Checking connection...' : backendStatus.connected ? 'Connected (CORS Active)' : 'Disconnected'}
            </strong>
          </div>

          <p style={{ margin: '6px 0', fontSize: '13px', opacity: 0.85 }}>
            API Target: <code>{API_BASE_URL}</code>
          </p>

          {backendStatus.data && (
            <div style={{ margin: '10px 0', padding: '8px 12px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '6px', fontSize: '13px', color: '#10b981' }}>
              <span>Server Response: <strong>{backendStatus.data.message || JSON.stringify(backendStatus.data)}</strong></span>
            </div>
          )}

          {backendStatus.error && (
            <div style={{ margin: '10px 0', padding: '8px 12px', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '6px', fontSize: '13px', color: '#f87171' }}>
              <span>{backendStatus.error}</span>
            </div>
          )}

          <div style={{ marginTop: '12px' }}>
            <button
              type="button"
              className="counter"
              style={{ margin: 0, cursor: 'pointer' }}
              onClick={testConnection}
              disabled={backendStatus.loading}
            >
              {backendStatus.loading ? 'Testing...' : 'Retest Backend Connection'}
            </button>
          </div>
        </div>

        <button
          type="button"
          className="counter"
          onClick={() => setCount((count) => count + 1)}
        >
          Count is {count}
        </button>
      </section>

      <div className="ticks"></div>

      <section id="next-steps">
        <div id="docs">
          <h2>FastAPI Backend Endpoints</h2>
          <p>Ready for end-to-end API integration</p>
          <ul style={{ textAlign: 'left' }}>
            <li><code>/api/health</code> - Health check endpoint</li>
            <li><code>/auth/login</code> - OAuth2 authentication</li>
            <li><code>/faculty/*</code> - Faculty course management</li>
            <li><code>/hod/*</code> - HOD approval & reporting</li>
          </ul>
        </div>
      </section>

      <div className="ticks"></div>
      <section id="spacer"></section>
    </>
  )
}

export default App
