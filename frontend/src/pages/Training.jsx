import React, { useState, useEffect } from 'react'
import { trainingApi, personnelApi } from '../api'

export default function Training() {
  const [training, setTraining] = useState([])
  const [personnel, setPersonnel] = useState([])
  const [selectedPersonnel, setSelectedPersonnel] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    personnel_id: '',
    subject: '',
    date: new Date().toISOString().split('T')[0],
    start_time: '09:00',
    end_time: '10:00',
    trainer: '',
    notes: '',
  })

  useEffect(() => {
    loadPersonnel()
    loadTraining()
  }, [selectedPersonnel])

  const loadPersonnel = async () => {
    try {
      const data = await personnelApi.list()
      setPersonnel(data)
    } catch (err) {
      setError(err.message)
    }
  }

  const loadTraining = async () => {
    try {
      setLoading(true)
      if (selectedPersonnel) {
        const data = await trainingApi.getPersonnelTraining(selectedPersonnel)
        setTraining(data)
      } else {
        const data = await trainingApi.list({})
        setTraining(data)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleAddTraining = async (e) => {
    e.preventDefault()
    try {
      await trainingApi.create({
        ...formData,
        personnel_id: parseInt(formData.personnel_id),
      })
      setFormData({
        personnel_id: '',
        subject: '',
        date: new Date().toISOString().split('T')[0],
        start_time: '09:00',
        end_time: '10:00',
        trainer: '',
        notes: '',
      })
      setShowForm(false)
      loadTraining()
      alert('Eğitim kaydı başarıyla eklendi')
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Silmek istediğinizden emin misiniz?')) {
      try {
        await trainingApi.delete(id)
        loadTraining()
      } catch (err) {
        setError(err.message)
      }
    }
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Eğitim & Geribildirim Yönetimi</h1>

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
            {showForm ? 'İptal' : 'Eğitim Ekle'}
          </button>
        </div>
      </div>

      {showForm && (
        <div className="bg-white p-6 rounded-lg shadow mb-8">
          <h2 className="text-xl font-bold mb-4">Yeni Eğitim Ekle</h2>
          <form onSubmit={handleAddTraining} className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
              <label className="block text-gray-700 font-bold mb-2">Eğitim Konusu</label>
              <input
                type="text"
                value={formData.subject}
                onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
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
            <div>
              <label className="block text-gray-700 font-bold mb-2">Eğitmen</label>
              <input
                type="text"
                value={formData.trainer}
                onChange={(e) => setFormData({ ...formData, trainer: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-gray-700 font-bold mb-2">Başlangıç Saati</label>
              <input
                type="time"
                value={formData.start_time}
                onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>
            <div>
              <label className="block text-gray-700 font-bold mb-2">Bitiş Saati</label>
              <input
                type="time"
                value={formData.end_time}
                onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
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
          {selectedPersonnel ? 'Personel Eğitimleri' : 'Tüm Eğitimler'}
        </h2>
        {loading ? (
          <p className="text-center text-gray-500">Yükleniyor...</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-100">
                  <th className="px-4 py-2 text-left">Personel</th>
                  <th className="px-4 py-2 text-left">Konu</th>
                  <th className="px-4 py-2 text-left">Tarih</th>
                  <th className="px-4 py-2 text-center">Saat</th>
                  <th className="px-4 py-2 text-left">Eğitmen</th>
                  <th className="px-4 py-2 text-center">İşlem</th>
                </tr>
              </thead>
              <tbody>
                {training.map((t) => (
                  <tr key={t.id} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-2">
                      {personnel.find((p) => p.id === t.personnel_id)?.name}
                    </td>
                    <td className="px-4 py-2">{t.subject}</td>
                    <td className="px-4 py-2">{t.date}</td>
                    <td className="px-4 py-2 text-center text-sm">
                      {t.start_time} - {t.end_time}
                    </td>
                    <td className="px-4 py-2">{t.trainer}</td>
                    <td className="px-4 py-2 text-center">
                      <button
                        onClick={() => handleDelete(t.id)}
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
