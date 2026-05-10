import React, { useState, useEffect } from 'react'
import { personnelApi } from '../api'

export default function Personnel() {
  const [personnel, setPersonnel] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    employee_id: '',
    department: '',
    position: '',
    email: '',
    phone: '',
  })

  useEffect(() => {
    loadPersonnel()
  }, [])

  const loadPersonnel = async () => {
    try {
      setLoading(true)
      const data = await personnelApi.list()
      setPersonnel(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleAddPersonnel = async (e) => {
    e.preventDefault()
    try {
      await personnelApi.create(formData)
      setFormData({
        name: '',
        employee_id: '',
        department: '',
        position: '',
        email: '',
        phone: '',
      })
      setShowForm(false)
      loadPersonnel()
      alert('Personel başarıyla eklendi')
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Silmek istediğinizden emin misiniz?')) {
      try {
        await personnelApi.delete(id)
        loadPersonnel()
      } catch (err) {
        setError(err.message)
      }
    }
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Personel Yönetimi</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition"
        >
          {showForm ? 'İptal' : 'Yeni Personel Ekle'}
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {showForm && (
        <div className="bg-white p-6 rounded-lg shadow mb-8">
          <h2 className="text-xl font-bold mb-4">Yeni Personel Ekle</h2>
          <form onSubmit={handleAddPersonnel} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-700 font-bold mb-2">Ad-Soyad</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>
            <div>
              <label className="block text-gray-700 font-bold mb-2">Personel ID</label>
              <input
                type="text"
                value={formData.employee_id}
                onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>
            <div>
              <label className="block text-gray-700 font-bold mb-2">Departman</label>
              <input
                type="text"
                value={formData.department}
                onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-gray-700 font-bold mb-2">Pozisyon</label>
              <input
                type="text"
                value={formData.position}
                onChange={(e) => setFormData({ ...formData, position: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-gray-700 font-bold mb-2">Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-gray-700 font-bold mb-2">Telefon</label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
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
        <h2 className="text-xl font-bold mb-4">Personel Listesi</h2>
        {loading ? (
          <p className="text-center text-gray-500">Yükleniyor...</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-100">
                  <th className="px-4 py-2 text-left">Ad-Soyad</th>
                  <th className="px-4 py-2 text-left">Personel ID</th>
                  <th className="px-4 py-2 text-left">Departman</th>
                  <th className="px-4 py-2 text-left">Pozisyon</th>
                  <th className="px-4 py-2 text-left">Email</th>
                  <th className="px-4 py-2 text-center">İşlem</th>
                </tr>
              </thead>
              <tbody>
                {personnel.map((p) => (
                  <tr key={p.id} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-2">{p.name}</td>
                    <td className="px-4 py-2">{p.employee_id}</td>
                    <td className="px-4 py-2">{p.department}</td>
                    <td className="px-4 py-2">{p.position}</td>
                    <td className="px-4 py-2">{p.email}</td>
                    <td className="px-4 py-2 text-center">
                      <button
                        onClick={() => handleDelete(p.id)}
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
