import React from 'react'

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-slate-950 px-4 text-white">
          <div className="max-w-md rounded-2xl border border-white/10 bg-white/10 p-8 text-center shadow-2xl">
            <h1 className="mb-3 text-2xl font-black">Beklenmeyen hata</h1>
            <p className="text-sm text-white/70">Sayfa yuklenirken bir hata olustu. Lutfen sayfayi yenileyin.</p>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}