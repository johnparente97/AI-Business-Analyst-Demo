/**
 * ErrorBoundary — Global error boundary
 * Catches unhandled errors in the React tree and displays a styled fallback UI.
 */

import { Component } from 'react'
import type { ReactNode, ErrorInfo } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('[ErrorBoundary] Caught error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
            background: '#09090b',
            padding: '1rem',
          }}
        >
          <div
            style={{
              maxWidth: '28rem',
              width: '100%',
              padding: '2.5rem',
              borderRadius: '1.5rem',
              background: 'rgba(17, 17, 19, 0.85)',
              backdropFilter: 'blur(20px)',
              WebkitBackdropFilter: 'blur(20px)',
              border: '1px solid rgba(139, 92, 246, 0.15)',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
              textAlign: 'center' as const,
            }}
          >
            {/* Icon */}
            <div
              style={{
                width: '3.5rem',
                height: '3.5rem',
                borderRadius: '1rem',
                background: 'linear-gradient(135deg, #7c3aed, #a855f7)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1.25rem',
                fontSize: '1.5rem',
                boxShadow: '0 10px 20px -5px rgba(139, 92, 246, 0.3)',
              }}
            >
              ⚠️
            </div>

            <h2
              style={{
                color: '#f4f4f5',
                fontSize: '1.25rem',
                fontWeight: 700,
                margin: '0 0 0.5rem',
              }}
            >
              Something went wrong
            </h2>

            <p
              style={{
                color: '#71717a',
                fontSize: '0.875rem',
                lineHeight: 1.6,
                margin: '0 0 1.5rem',
              }}
            >
              An unexpected error occurred. You can reset the app and try again.
            </p>

            {this.state.error && (
              <pre
                style={{
                  color: '#ef4444',
                  fontSize: '0.7rem',
                  background: 'rgba(239, 68, 68, 0.08)',
                  border: '1px solid rgba(239, 68, 68, 0.15)',
                  borderRadius: '0.75rem',
                  padding: '0.75rem',
                  marginBottom: '1.5rem',
                  textAlign: 'left' as const,
                  overflow: 'auto',
                  maxHeight: '6rem',
                  whiteSpace: 'pre-wrap' as const,
                  wordBreak: 'break-word' as const,
                }}
              >
                {this.state.error.message}
              </pre>
            )}

            <button
              onClick={() => this.setState({ hasError: false, error: null })}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.75rem 2rem',
                borderRadius: '0.75rem',
                border: 'none',
                background: 'linear-gradient(135deg, #7c3aed, #9333ea)',
                color: '#fff',
                fontSize: '0.875rem',
                fontWeight: 700,
                cursor: 'pointer',
                boxShadow: '0 10px 25px -5px rgba(139, 92, 246, 0.35)',
                transition: 'transform 150ms, box-shadow 150ms',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'scale(1.05)'
                e.currentTarget.style.boxShadow = '0 15px 30px -5px rgba(139, 92, 246, 0.45)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'scale(1)'
                e.currentTarget.style.boxShadow = '0 10px 25px -5px rgba(139, 92, 246, 0.35)'
              }}
            >
              Reset
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
