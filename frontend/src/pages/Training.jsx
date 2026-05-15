import React, { useState, useEffect } from 'react'
import { trainingApi, personnelApi } from '../api'
import { useAuth } from '../App'
import { formatLocalDate } from '../utils/date'
import { exportRowsToExcel } from '../utils/exportExcel'

export default function Training() {
  const { isAdmin } = useAuth()
  const [training, setTraining] = useState([])
  const [personnel, setPersonnel] = useState([])
  const [selectedPersonnel, setSelectedPersonnel] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [sortConfig, setSortConfig] = useState({ key: 'date', direction: 'desc' })
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    personnel_id: '',
    subject: '',
    date: formatLocalDate(),
    start_time: '09:00',
    end_time: '10:00',
    trainer: '',
    notes: '',
  })

  useEffect(() => {
    loadPersonnel()
    loadTraining()
  }, [selectedPersonnel])

  const formatDisplayDate = (value) => {
    if (!value) return '-'
    const parts = String(value).split('-')
    if (parts.length === 3) return `${parts[2]}.${parts[1]}.${parts[0]}`
    return value
  }

  const requestSort = (key) => {
    let direction = 'asc'
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc'
    }
    setSortConfig({ key, direction })
  }

  const getSortArrow = (key) => {
    if (sortConfig.key !== key) return '↕'
    return sortConfig.direction === 'asc' ? '↑' : '↓'
  }

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
      setError('')
      await trainingApi.create({
        ...formData,
        personnel_id: parseInt(formData.personnel_id),
      })
      setFormData({
        personnel_id: '',
        subject: '',
        date: formatLocalDate(),
        start_time: '09:00',
        end_time: '10:00',
        trainer: '',
        notes: '',
      })
      setShowForm(false)
      await loadTraining()
      setSuccessMessage('ISLEM TAMAMLANDI')
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDeleteTraining = async (trainingId) => {
    try {
      setError('')
      await trainingApi.delete(trainingId)
      await loadTraining()
      setSuccessMessage('ISLEM TAMAMLANDI')
    } catch (err) {
      setError(err.message)
    }
  }

  const getFilteredTraining = () => {
    const mappedTraining = training.map((item) => ({
      ...item,
      personnel_name: personnel.find((person) => person.id === item.personnel_id)?.name || '',
    }))

    const filteredTraining = mappedTraining.filter((item) => {
      const haystack = [
        item.personnel_name,
        item.subject,
        item.trainer,
        item.notes,
        item.date,
      ].join(' ').toLocaleLowerCase('tr')
      return haystack.includes(searchTerm.toLocaleLowerCase('tr'))
    })

    return [...filteredTraining].sort((first, second) => {
      let comparison = 0
      if (sortConfig.key === 'date') {
        comparison = new Date(first.date).getTime() - new Date(second.date).getTime()
      } else {
        comparison = String(first[sortConfig.key] ?? '').localeCompare(
          String(second[sortConfig.key] ?? ''),
          'tr',
          { sensitivity: 'base' }
        )
      }
      return sortConfig.direction === 'asc' ? comparison : -comparison
    })
  }

  const exportToExcel = () => {
    exportRowsToExcel(
      getFilteredTraining().map((item) => ({
        Personel: item.personnel_name,
        Baslik: item.subject,
        Tarih: formatDisplayDate(item.date),
        Saat: `${item.start_time} - ${item.end_time}`,
        Yetkili: item.trainer || '-',
        Not: item.notes || '-',
      })),
      'Egitim ve Geribildirim',
      'egitim_geribildirim'
    )
  }

  return (
    <div className="p-8">
      {successMessage && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-2xl text-center">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100 text-3xl text-green-600">
              ✓
            </div>
            <h2 className="mb-2 text-2xl font-bold text-gray-900">{successMessage}</h2>
            <p className="mb-6 text-sm text-gray-500">Islem basariyla tamamlandi.</p>
            <button
              onClick={() => setSuccessMessage('')}
              className="rounded-lg bg-green-600 px-6 py-3 font-bold text-white transition hover:bg-green-700"
            >
              Tamam
            </button>
          </div>
        </div>
      )}

      <h1 className="text-3xl font-bold mb-8">Egitim ve Geribildirim</h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div>
          <label className="block text-gray-700 font-bold mb-2">Personel Filtreleme</label>
          <select
            value={selectedPersonnel || ''}
            onChange={(e) => setSelectedPersonnel(e.target.value ? parseInt(e.target.value) : null)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
          >
            <option value="">Tumu</option>
            {personnel.map((person) => (
              <option key={person.id} value={person.id}>
                {person.name}
              </option>
            ))}
          </select>
        </div>
        {isAdmin && (
        <div className="flex items-end">
          <button
            onClick={() => setShowForm(!showForm)}
            className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition"
          >
            {showForm ? 'Iptal' : 'Kayit Ekle'}
          </button>
        </div>
        )}
        <div className="flex items-end">
          <button
            onClick={exportToExcel}
            className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded transition"
          >
            Export
          </button>
        </div>
      </div>

      <div className="mb-8">
        <label className="block text-gray-700 font-bold mb-2">Ara</label>
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Personel, baslik, yetkili veya not ara"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg"
        />
      </div>

      {isAdmin && showForm && (
        <div className="bg-white p-6 rounded-lg shadow mb-8">
          <h2 className="text-xl font-bold mb-4">Yeni Egitim ve Geribildirim Kaydi</h2>
          <form onSubmit={handleAddTraining} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-700 font-bold mb-2">Personel</label>
              <select
                value={formData.personnel_id}
                onChange={(e) => setFormData({ ...formData, personnel_id: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              >
                <option value="">Seciniz</option>
                {personnel.map((person) => (
                  <option key={person.id} value={person.id}>
                    {person.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-gray-700 font-bold mb-2">Baslik</label>
              <input
                type="text"
                value={formData.subject}
                onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                placeholder="Egitim veya geribildirim konusu"
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
              <label className="block text-gray-700 font-bold mb-2">Egitmen / Geri Bildirim Veren</label>
              <input
                type="text"
                value={formData.trainer}
                onChange={(e) => setFormData({ ...formData, trainer: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-gray-700 font-bold mb-2">Baslangic Saati</label>
              <input
                type="time"
                value={formData.start_time}
                onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>
            <div>
              <label className="block text-gray-700 font-bold mb-2">Bitis Saati</label>
              <input
                type="time"
                value={formData.end_time}
                onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-gray-700 font-bold mb-2">Not</label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                rows="3"
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
        <h2 className="text-xl font-bold mb-4">
          {selectedPersonnel ? 'Personel Kayitlari' : 'Tum Kayitlar'}
        </h2>
        {loading ? (
          <p className="text-center text-gray-500">Yukleniyor...</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-100">
                  <th className="px-4 py-2 text-left cursor-pointer" onClick={() => requestSort('personnel_name')}>Personel {getSortArrow('personnel_name')}</th>
                  <th className="px-4 py-2 text-left cursor-pointer" onClick={() => requestSort('subject')}>Baslik {getSortArrow('subject')}</th>
                  <th className="px-4 py-2 text-left cursor-pointer" onClick={() => requestSort('date')}>Tarih {getSortArrow('date')}</th>
                  <th className="px-4 py-2 text-center">Saat</th>
                  <th className="px-4 py-2 text-left cursor-pointer" onClick={() => requestSort('trainer')}>Yetkili {getSortArrow('trainer')}</th>
                  <th className="px-4 py-2 text-left cursor-pointer" onClick={() => requestSort('notes')}>Not {getSortArrow('notes')}</th>
                  {isAdmin && <th className="px-4 py-2 text-center">Sil</th>}
                </tr>
              </thead>
              <tbody>
                {getFilteredTraining().map((item) => (
                  <tr key={item.id} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-2">{item.personnel_name}</td>
                    <td className="px-4 py-2">{item.subject}</td>
                    <td className="px-4 py-2">{formatDisplayDate(item.date)}</td>
                    <td className="px-4 py-2 text-center">{item.start_time} - {item.end_time}</td>
                    <td className="px-4 py-2">{item.trainer}</td>
                    <td className="px-4 py-2">{item.notes}</td>
                    {isAdmin && (
                    <td className="px-4 py-2 text-center">
                      <button
                        onClick={() => handleDeleteTraining(item.id)}
                        className="rounded bg-red-500 px-3 py-1 text-sm font-bold text-white transition hover:bg-red-600"
                      >
                        Sil
                      </button>
                    </td>
                    )}
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