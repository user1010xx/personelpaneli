import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { authApi } from '../api'
import { useAuth } from '../App'

export default function LoginPage() {
  const navigate = useNavigate()
  const { token, login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (token) {
      navigate('/dashboard')
    }
  }, [token, navigate])

  const handleLogin = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await authApi.login({ username, password })
      await login({
        accessToken: response.access_token,
        refreshToken: response.refresh_token,
      })
      navigate('/dashboard')
    } catch (err) {
      setError(err.message || 'Giriş başarısız')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-slate-950 px-4 py-10 text-white">
      <div className="absolute left-[-12rem] top-[-10rem] h-[34rem] w-[34rem] rounded-full bg-cyan-400/20 blur-3xl" />
      <div className="absolute bottom-[-16rem] right-[-10rem] h-[38rem] w-[38rem] rounded-full bg-blue-500/25 blur-3xl" />
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.045)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.045)_1px,transparent_1px)] bg-[size:42px_42px]" />

      <div className="relative grid w-full max-w-5xl overflow-hidden rounded-[2rem] border border-white/10 bg-white/10 shadow-2xl backdrop-blur-2xl md:grid-cols-[1.1fr_0.9fr]">
        <div className="hidden flex-col justify-between bg-gradient-to-br from-cyan-300 via-blue-500 to-slate-950 p-10 md:flex">
          <div>
            <div className="mb-8 flex h-14 w-14 items-center justify-center rounded-2xl bg-white text-xl font-black text-slate-950 shadow-xl">
              PP
            </div>
            <h1 className="mb-4 text-5xl font-black leading-tight tracking-tight">
              Operasyonu tek ekrandan yönetin.
            </h1>
            <p className="max-w-md text-lg font-medium text-white/80">
              Üyelik, çağrı, puantaj, kalite ve WhatsApp verileri için profesyonel performans paneli.
            </p>
          </div>
          <div className="grid grid-cols-3 gap-3 text-sm font-bold">
            <div className="rounded-2xl bg-white/15 p-4 backdrop-blur">Canlı Veri</div>
            <div className="rounded-2xl bg-white/15 p-4 backdrop-blur">Excel Export</div>
            <div className="rounded-2xl bg-white/15 p-4 backdrop-blur">Yetki Kontrolü</div>
          </div>
        </div>

        <div className="bg-white p-8 text-slate-900 md:p-12">
          <div className="mb-8">
            <p className="mb-2 text-sm font-black uppercase tracking-[0.25em] text-blue-600">Personel Panel</p>
            <h2 className="text-3xl font-black tracking-tight">Giriş Yap</h2>
            <p className="mt-2 text-sm text-slate-500">Panel hesabınızla devam edin.</p>
          </div>

          {error && (
            <div className="mb-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 font-semibold text-red-700">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-5">
            <div>
              <label className="mb-2 block font-bold text-slate-700">Kullanıcı Adı</label>
              <input
                type="text"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                className="w-full rounded-2xl border border-slate-200 px-4 py-3"
                required
              />
            </div>

            <div>
              <label className="mb-2 block font-bold text-slate-700">Şifre</label>
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="w-full rounded-2xl border border-slate-200 px-4 py-3"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-2xl bg-gradient-to-r from-blue-600 to-cyan-500 px-4 py-3 font-black text-white shadow-xl shadow-blue-500/25 disabled:opacity-50"
            >
              {loading ? 'Giriş yapılıyor...' : 'Giriş Yap'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}