import React from 'react'
import { useNavigate } from 'react-router-dom'

export default function Navbar() {
  const navigate = useNavigate()

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    navigate('/login')
  }

  return (
    <nav className="bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex-shrink-0">
            <h1 className="text-2xl font-bold">Personel Panel</h1>
          </div>
          <div className="hidden md:flex space-x-6 text-sm">
            <a href="/dashboard" className="hover:text-blue-200">Dashboard</a>
            <a href="/personnel" className="hover:text-blue-200">Personel</a>
            <a href="/sales" className="hover:text-blue-200">Satış</a>
            <a href="/attendance" className="hover:text-blue-200">Puantaj</a>
            <a href="/warnings" className="hover:text-blue-200">Uyarılar</a>
            <a href="/training" className="hover:text-blue-200">Eğitim</a>
            <a href="/call-monitoring" className="hover:text-blue-200">Çağrılar</a>
            <a href="/whatsapp" className="hover:text-blue-200">WhatsApp</a>
          </div>
          <button
            onClick={handleLogout}
            className="bg-red-500 hover:bg-red-600 px-4 py-2 rounded transition"
          >
            Çıkış Yap
          </button>
        </div>
      </div>
    </nav>
  )
}
