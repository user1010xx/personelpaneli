import React, { useState, useEffect } from 'react'
import { callMonitoringApi, personnelApi } from '../api'

export default function CallMonitoring() {
  const [calls, setCalls] = useState([])
  const [personnel, setPersonnel] = useState([])
  const [selectedPersonnel, setSelectedPersonnel] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    personnel_id: '',
    phone_number: '',
    quality_score: 75,
    date: new Date().toISOString().split('T')[0],
    notes: '',
  })

  useEffect(() => {
    loadPersonnel()
    loadCalls()
  }, [selectedPersonnel])

  const loadPersonnel = async () => {
    try {
      const data = await personnelApi.list()
      setPersonnel(data)
    } catch (err) {
      setError(err.message)
    }
  }

  const loadCalls = async () => {
    try {
      setLoading(true)
      if (selectedPersonnel) {
        const data = await callMonitoringApi.getPersonnelCalls(selectedPersonnel)
        setCalls(data)
      } else {
        const data = await callMonitoringApi.list({})
        setCalls(data)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleAddCall = async (e) => {
    e.preventDefault()
    try {
      await callMonitoringApi.create({
        ...formData,
        personnel_id: parseInt(formData.personnel_id),
        quality_score: parseFloat(formData.quality_score),
      })
      setFormData({
        personnel_id: '',
        phone_number: '',
        quality_score: 75,
        date: new Date().toISOString().split('T')[0],
        notes: '',
      })
      setShowForm(false)
      loadCalls()
      alert('Çağrı kaydı başarıyla eklendi')
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Silmek istediğinizden emin misiniz?')) {
      try {
        await callMonitoringApi.delete(id)
        loadCalls()
      } catch (err) {
        setError(err.message)
      }
    }
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Dinlenen Çağrılar Yönetimi</h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <div>
          <label className="block text-gray-700 font-bold mb-2">Personel Filtreleme</label>
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
        <div className="flex items-end">
          <button
            onClick={() => setShowForm(!showForm)}
            className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition"
          >
            {showForm ? 'İptal' : 'Çağrı Ekle'}
          </button>
        </div>
      </div>

      {showForm && (
        <div className="bg-white p-6 rounded-lg shadow mb-8">
          <h2 className="text-xl font-bold mb-4">Yeni Çağrı Kaydı Ekle</h2>
          <form onSubmit={handleAddCall} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-700 font-bold mb-2">Personel</label>
              <select
                value={formData.personnel_id}
                onChange={(e) => setFormData({ ...formData, personnel_id: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              >
                <option value="">Seçiniz</option>
                {personnel.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-gray-700 font-bold mb-2">Telefon Numarası</label>
              <input
                type="tel"
                value={formData.phone_number}
                onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>
            <div>
              <label className="block text-gray-700 font-bold mb-2">Kalite Puanı (0-100)</label>
              <input
                type="number"
                min="0"
                max="100"
                value={formData.quality_score}
                onChange={(e) => setFormData({ ...formData, quality_score: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>
            <div>
              <label className="block text-gray-700 font-bold mb-2">Tarih</label>
              <input
                type="date"
                value={formData.date}
                onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-gray-700 font-bold mb-2">Notlar</label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                rows="2"
              ></textarea>
            </div>
            <div className="md:col-span-2">
              <button
                type="submit"
                className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded transition"
              >
                Kaydet
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">
          {selectedPersonnel ? 'Personel Çağrıları' : 'Tüm Çağrılar'}
        </h2>
        {loading ? (
          <p className="text-center text-gray-500">Yükleniyor...</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-100">
                  <th className="px-4 py-2 text-left">Personel</th>
                  <th className="px-4 py-2 text-left">Telefon</th>
                  <th className="px-4 py-2 text-center">Kalite Puanı</th>
                  <th className="px-4 py-2 text-left">Tarih</th>
                  <th className="px-4 py-2 text-left">Notlar</th>
                  <th className="px-4 py-2 text-center">İşlem</th>
                </tr>
              </thead>
              <tbody>
                {calls.map((call) => (
                  <tr key={call.id} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-2">
                      {personnel.find((p) => p.id === call.personnel_id)?.name}
                    </td>
                    <td className="px-4 py-2">{call.phone_number}</td>
                    <td className={`px-4 py-2 text-center font-bold ${getScoreColor(call.quality_score)}`}>
                      {call.quality_score}/100
                    </td>
                    <td className="px-4 py-2">{call.date}</td>
                    <td className="px-4 py-2 text-sm">{call.notes}</td>
                    <td className="px-4 py-2 text-center">
                      <button
                        onClick={() => handleDelete(call.id)}
                        className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-sm transition"
                      >
                        Sil
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
