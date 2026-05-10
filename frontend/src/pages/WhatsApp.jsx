import React, { useState, useEffect } from 'react'
import { whatsappApi, personnelApi } from '../api'

export default function WhatsApp() {
  const [whatsapp, setWhatsApp] = useState([])
  const [personnel, setPersonnel] = useState([])
  const [selectedPersonnel, setSelectedPersonnel] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [startDate, setStartDate] = useState(
    new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  )
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0])

  useEffect(() => {
    loadPersonnel()
    loadWhatsApp()
  }, [selectedPersonnel, startDate, endDate])

  const loadPersonnel = async () => {
    try {
      const data = await personnelApi.list()
      setPersonnel(data)
    } catch (err) {
      setError(err.message)
    }
  }

  const loadWhatsApp = async () => {
    try {
      setLoading(true)
      if (selectedPersonnel) {
        const data = await whatsappApi.getPersonnelData(selectedPersonnel)
        setWhatsApp(data)
      } else {
        const data = await whatsappApi.list({})
        setWhatsApp(data)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getTotalUnanswered = () => {
    return whatsapp.reduce((sum, w) => sum + w.unanswered_count, 0)
  }

  const getAverageUnanswered = () => {
    return whatsapp.length > 0 ? (getTotalUnanswered() / whatsapp.length).toFixed(2) : 0
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">WhatsApp Cevapsız Mesaj Takibi</h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-600 text-sm font-medium mb-2">Toplam Cevapsız</h3>
          <p className="text-3xl font-bold text-red-600">{getTotalUnanswered()}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-600 text-sm font-medium mb-2">Günlük Ortalama</h3>
          <p className="text-3xl font-bold text-orange-600">{getAverageUnanswered()}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-600 text-sm font-medium mb-2">Kayıt Sayısı</h3>
          <p className="text-3xl font-bold text-blue-600">{whatsapp.length}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-600 text-sm font-medium mb-2">İzleme Süresi</h3>
          <p className="text-lg font-semibold">{startDate} / {endDate}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div>
          <label className="block text-gray-700 font-bold mb-2">Personel</label>
          <select
            value={selectedPersonnel || ''}
            onChange={(e) => setSelectedPersonnel(e.target.value ? parseInt(e.target.value) : null)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
          >
            <option value="">Tümü</option>
            {personnel.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-gray-700 font-bold mb-2">Başlangıç Tarihi</label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
          />
        </div>
        <div>
          <label className="block text-gray-700 font-bold mb-2">Bitiş Tarihi</label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
          />
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">
          {selectedPersonnel ? 'Personel WhatsApp Verileri' : 'Tüm WhatsApp Verileri'}
        </h2>
        {loading ? (
          <p className="text-center text-gray-500">Yükleniyor...</p>
        ) : whatsapp.length === 0 ? (
          <p className="text-center text-gray-500 py-8">Bu dönemde veri bulunmamaktadır</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-100">
                  <th className="px-4 py-2 text-left">Personel</th>
                  <th className="px-4 py-2 text-left">Tarih</th>
                  <th className="px-4 py-2 text-center">Cevapsız Mesaj</th>
                  <th className="px-4 py-2 text-left">Durum</th>
                </tr>
              </thead>
              <tbody>
                {whatsapp.map((w) => {
                  let statusColor = 'text-green-600'
                  let statusText = 'İyi'
                  
                  if (w.unanswered_count > 10) {
                    statusColor = 'text-red-600'
                    statusText = 'Yüksek'
                  } else if (w.unanswered_count > 5) {
                    statusColor = 'text-orange-600'
                    statusText = 'Orta'
                  }
                  
                  return (
                    <tr key={w.id} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-2">
                        {personnel.find((p) => p.id === w.personnel_id)?.name}
                      </td>
                      <td className="px-4 py-2">{w.date}</td>
                      <td className="px-4 py-2 text-center font-bold">
                        {w.unanswered_count}
                      </td>
                      <td className={`px-4 py-2 font-semibold ${statusColor}`}>
                        {statusText}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {selectedPersonnel && whatsapp.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow mt-8">
          <h2 className="text-xl font-bold mb-4">Personel İstatistikleri</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded">
              <p className="text-gray-600 text-sm mb-2">En Yüksek</p>
              <p className="text-2xl font-bold text-blue-600">
                {Math.max(...whatsapp.map(w => w.unanswered_count))}
              </p>
            </div>
            <div className="bg-green-50 p-4 rounded">
              <p className="text-gray-600 text-sm mb-2">En Düşük</p>
              <p className="text-2xl font-bold text-green-600">
                {Math.min(...whatsapp.map(w => w.unanswered_count))}
              </p>
            </div>
            <div className="bg-purple-50 p-4 rounded">
              <p className="text-gray-600 text-sm mb-2">Ortalama</p>
              <p className="text-2xl font-bold text-purple-600">
                {(whatsapp.reduce((sum, w) => sum + w.unanswered_count, 0) / whatsapp.length).toFixed(1)}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
