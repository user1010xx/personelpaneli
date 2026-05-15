import React from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../App'

const navLinks = [
  { path: '/dashboard', label: 'Dashboard' },
  { path: '/personnel', label: 'Personel' },
  { path: '/sales', label: 'Üye Adedi' },
  { path: '/attendance', label: 'Puantaj' },
  { path: '/warnings', label: 'Uyarı Kesinti' },
  { path: '/training', label: 'Eğitim' },
  { path: '/call-process', label: 'Çağrı Süreci' },
  { path: '/call-monitoring', label: 'Kalite' },
  { path: '/whatsapp', label: 'WhatsApp' },
]

export default function Navbar() {
  const navigate = useNavigate()
  const location = useLocation()
  const { logout, isAdmin } = useAuth()
  const adminLink = { path: '/users', label: 'Kullanıcı Yönetimi' }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav className="sticky top-0 z-50 border-b border-slate-800 bg-slate-950 text-white shadow-2xl">
      <div className="h-[2px] bg-gradient-to-r from-cyan-300 via-blue-500 to-emerald-300" />
      <div className="mx-auto flex min-h-[72px] max-w-[1680px] items-center gap-4 px-5 lg:px-8">
        <Link to="/dashboard" className="group flex min-w-fit items-center gap-3">
          <div className="relative flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-300 to-blue-500 font-black text-slate-950 shadow-lg shadow-blue-500/25 ring-1 ring-white/25">
            <span>PP</span>
            <span className="absolute -right-1 -top-1 h-3 w-3 rounded-full bg-emerald-300 ring-4 ring-slate-950" />
          </div>
          <div>
            <h1 className="text-lg font-black tracking-[-0.045em] text-white drop-shadow lg:text-xl">Personel Panel</h1>
            <p className="text-[10px] font-black uppercase tracking-[0.28em] text-cyan-200 drop-shadow">
              Operasyon Merkezi
            </p>
          </div>
        </Link>

          <div className="hidden flex-1 items-center justify-center xl:flex">
            <div className="flex items-center gap-1 rounded-2xl border border-slate-700 bg-slate-900 p-1 shadow-inner shadow-black/20">
            {navLinks.map((link) => {
              const active = location.pathname === link.path
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`rounded-xl px-3 py-2 text-[13px] font-black tracking-[-0.015em] transition ${
                    active
                      ? 'bg-white text-slate-950 shadow-lg shadow-white/10'
                      : 'text-slate-100 hover:bg-slate-800 hover:text-white'
                  }`}
                >
                  {link.label}
                </Link>
              )
            })}
          </div>
        </div>

        <div className="ml-auto flex min-w-fit items-center gap-3">
          {isAdmin && (
            <Link
              to={adminLink.path}
              className={`hidden rounded-2xl border px-4 py-2 text-[13px] font-black tracking-[-0.015em] shadow-lg transition md:block ${
                location.pathname === adminLink.path
                  ? 'border-cyan-200 bg-cyan-200 text-slate-950 shadow-cyan-500/20'
                  : 'border-cyan-200/40 bg-slate-900 text-cyan-100 shadow-cyan-950/10 hover:bg-slate-800'
              }`}
            >
              {adminLink.label}
            </Link>
          )}

          <button
            onClick={handleLogout}
            className="rounded-2xl border border-red-300/25 bg-red-500/90 px-4 py-2 text-sm font-black text-white shadow-lg shadow-red-950/20 hover:bg-red-500"
          >
            Çıkış
          </button>
        </div>
      </div>

      <div className="flex gap-2 overflow-x-auto border-t border-slate-800 bg-slate-950 px-4 py-2 xl:hidden">
        {navLinks.map((link) => {
          const active = location.pathname === link.path
          return (
            <Link
              key={link.path}
              to={link.path}
              className={`whitespace-nowrap rounded-full px-3 py-1.5 text-xs font-bold ${
                active ? 'bg-white text-slate-950' : 'bg-slate-800 text-slate-100'
              }`}
            >
              {link.label}
            </Link>
          )
        })}
        {isAdmin && (
          <Link
            to={adminLink.path}
            className={`whitespace-nowrap rounded-full px-3 py-1.5 text-xs font-bold ${
              location.pathname === adminLink.path ? 'bg-cyan-200 text-slate-950' : 'bg-slate-800 text-cyan-100'
            }`}
          >
            {adminLink.label}
          </Link>
        )}
      </div>
    </nav>
  )
}