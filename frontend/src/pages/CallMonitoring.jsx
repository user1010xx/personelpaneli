import React, { useState, useEffect, useRef } from 'react'
import { callMonitoringApi, personnelApi } from '../api'
import { formatLocalDate } from '../utils/date'
import { exportRowsToExcel } from '../utils/exportExcel'
import { useAuth } from '../App'

export default function CallMonitoring() {
  const { isAdmin } = useAuth()
  const [calls, setCalls] = useState([])
  const [personnel, setPersonnel] = useState([])
  const [selectedPersonnel, setSelectedPersonnel] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [successDetail, setSuccessDetail] = useState('')
  const [confirmDeleteId, setConfirmDeleteId] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [editingCallId, setEditingCallId] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [sortConfig, setSortConfig] = useState({ key: 'updated_display', direction: 'desc' })
  const editingCallIdRef = useRef(null)
  const activeRequestTokenRef = useRef(0)
  const [formData, setFormData] = useState({
    personnel_id: '',
    phone_number: '',
    quality_score: 75,
    date: formatLocalDate(),
    notes: '',
  })

  useEffect(() => {
    loadPersonnel()
    loadCalls()
  }, [selectedPersonnel])

  useEffect(() => {
    editingCallIdRef.current = editingCallId
  }, [editingCallId])

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
        const data = await callMonitoringApi.list({ limit: 1000 })
        setCalls(data)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const resetFormState = () => {
    setFormData({
      personnel_id: '',
      phone_number: '',
      quality_score: 75,
        date: formatLocalDate(),
      notes: '',
    })
    setEditingCallId(null)
    setShowForm(false)
  }

  const handleAddCall = async (e) => {
    e.preventDefault()
    if (isSubmitting) {
      return
    }

    const requestToken = activeRequestTokenRef.current + 1
    try {
      setIsSubmitting(true)
      setError('')
      activeRequestTokenRef.current = requestToken
      const startedEditingCallId = editingCallIdRef.current
      const payload = {
        ...formData,
        quality_score: parseFloat(formData.quality_score),
      }

      if (editingCallId) {
        await callMonitoringApi.update(editingCallId, {
          phone_number: payload.phone_number,
          quality_score: payload.quality_score,
          date: payload.date,
          notes: payload.notes,
        })
        setSuccessDetail('Kalite puanlamasi kaydi basariyla guncellendi.')
      } else {
        await callMonitoringApi.create({
          ...payload,
          personnel_id: parseInt(formData.personnel_id),
        })
        setSuccessDetail('Kalite puanlamasi kaydi basariyla eklendi.')
      }

      setSuccessMessage('ISLEM TAMAMLANDI')

      if (activeRequestTokenRef.current !== requestToken) {
        return
      }

      if (editingCallIdRef.current !== startedEditingCallId) {
        await loadCalls()
        return
      }

      resetFormState()
      await loadCalls()
    } catch (err) {
      setError(err.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleEditCall = (call) => {
    setFormData({
      personnel_id: String(call.personnel_id),
      phone_number: call.phone_number,
      quality_score: call.quality_score,
      date: call.date,
      notes: call.notes || '',
    })
    setEditingCallId(call.id)
    setShowForm(true)
  }

  const handleDeleteCall = async (callId) => {
    try {
      setError('')
      await callMonitoringApi.delete(callId)
      if (editingCallIdRef.current === callId) {
        resetFormState()
      }
      await loadCalls()
      setSuccessDetail('Kalite puanlamasi kaydi basariyla silindi.')
      setSuccessMessage('ISLEM TAMAMLANDI')
      setConfirmDeleteId(null)
    } catch (err) {
      setError(err.message)
    }
  }

  const handleCancelForm = () => {
    resetFormState()
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
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

  const formatUpdatedAt = (updatedAt, createdAt, dateValue) => {
    const sourceValue = updatedAt || createdAt || dateValue
    if (!sourceValue) {
      return '-'
    }

    const parsedDate = new Date(sourceValue)
    if (Number.isNaN(parsedDate.getTime())) {
      if (String(sourceValue).includes('T')) {
        const normalized = String(sourceValue).replace('T', ' ').slice(0, 19)
        return normalized
      }
      const parts = String(sourceValue).split('-')
      if (parts.length === 3) {
        return `${parts[2]}-${parts[1]}-${parts[0]} - 00:00:00`
      }
      return sourceValue
    }

    const day = String(parsedDate.getDate()).padStart(2, '0')
    const month = String(parsedDate.getMonth() + 1).padStart(2, '0')
    const year = parsedDate.getFullYear()
    const hours = String(parsedDate.getHours()).padStart(2, '0')
    const minutes = String(parsedDate.getMinutes()).padStart(2, '0')
    const seconds = String(parsedDate.getSeconds()).padStart(2, '0')

    return `${day}-${month}-${year} - ${hours}:${minutes}:${seconds}`
  }

  const getProcessedCalls = () => {
    const mappedCalls = calls.map((call) => ({
      ...call,
      personnel_name: personnel.find((person) => person.id === call.personnel_id)?.name || '',
      updated_display: formatUpdatedAt(call.updated_at, call.created_at, call.date),
    }))

    const filteredCalls = mappedCalls.filter((call) => {
      const haystack = [
        call.personnel_name,
        call.phone_number,
        call.notes,
        String(call.quality_score),
        call.updated_display,
      ].join(' ').toLocaleLowerCase('tr')
      return haystack.includes(searchTerm.toLocaleLowerCase('tr'))
    })

    return [...filteredCalls].sort((first, second) => {
      let comparison = 0
      if (sortConfig.key === 'quality_score') {
        comparison = Number(first.quality_score) - Number(second.quality_score)
      } else if (sortConfig.key === 'updated_display') {
        const firstTime = new Date(first.updated_at || first.created_at || first.date).getTime()
        const secondTime = new Date(second.updated_at || second.created_at || second.date).getTime()
        comparison = firstTime - secondTime
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

  const getSummary = () => {
    const now = new Date()
    const monthStart = new Date(now.getFullYear(), now.getMonth(), 1)
    const weekStart = new Date(now)
    weekStart.setHours(0, 0, 0, 0)
    const day = weekStart.getDay()
    const diff = day === 0 ? 6 : day - 1
    weekStart.setDate(weekStart.getDate() - diff)

    const parseCallDate = (call) => new Date(call.updated_at || call.created_at || call.date)
    const monthlyCalls = calls.filter((call) => parseCallDate(call) >= monthStart)
    const weeklyCalls = calls.filter((call) => parseCallDate(call) >= weekStart)

    const avg = (items) => {
      if (!items.length) return '0.0'
      return (items.reduce((sum, item) => sum + Number(item.quality_score || 0), 0) / items.length).toFixed(1)
    }

    return {
      monthlyCount: monthlyCalls.length,
      weeklyCount: weeklyCalls.length,
      monthlyAverage: avg(monthlyCalls),
      weeklyAverage: avg(weeklyCalls),
    }
  }

  const processedCalls = getProcessedCalls()
  const summary = getSummary()

  const exportToExcel = () => {
    exportRowsToExcel(
      processedCalls.map((call) => ({
        'Personel Adı': call.personnel_name,
        'Telefon Numarası': call.phone_number,
        Puan: call.quality_score,
        'Son Güncellenen': call.updated_display,
        Not: call.notes || '-',
      })),
      'Kalite Puanlaması',
      'kalite_puanlamasi'
    )
  }

  return (
    <div className="p-8">
      {isAdmin && confirmDeleteId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center shadow-2xl">
            <h2 className="mb-2 text-2xl font-bold text-gray-900">Silme Onayi</h2>
            <p className="mb-6 text-sm text-gray-500">Bu kalite puanlamasi kaydini silmek istediginize emin misiniz?</p>
            <div className="flex justify-center gap-3">
              <button
                onClick={() => setConfirmDeleteId(null)}
                className="rounded-lg bg-gray-200 px-6 py-3 font-bold text-gray-800 transition hover:bg-gray-300"
              >
                Vazgec
              </button>
              <button
                onClick={() => handleDeleteCall(confirmDeleteId)}
                className="rounded-lg bg-red-600 px-6 py-3 font-bold text-white transition hover:bg-red-700"
              >
                Sil
              </button>
            </div>
          </div>
        </div>
      )}

      {successMessage && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center shadow-2xl">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100 text-3xl text-green-600">
              ✓
            </div>
            <h2 className="mb-2 text-2xl font-bold text-gray-900">{successMessage}</h2>
            <p className="mb-6 text-sm text-gray-500">{successDetail}</p>
            <button
              onClick={() => {
                setSuccessMessage('')
                setSuccessDetail('')
              }}
              className="rounded-lg bg-green-600 px-6 py-3 font-bold text-white transition hover:bg-green-700"
            >
              Tamam
            </button>
          </div>
        </div>
      )}

      <h1 className="text-3xl font-bold mb-8">Kalite Puanlamasi</h1>

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
            onClick={() => (showForm ? handleCancelForm() : setShowForm(true))}
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
          placeholder="Personel adi, telefon numarasi veya not ile ara"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-600 text-sm font-medium mb-2">Aylik Kayit</h3>
          <p className="text-3xl font-bold text-blue-600">{summary.monthlyCount}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-600 text-sm font-medium mb-2">Haftalik Kayit</h3>
          <p className="text-3xl font-bold text-indigo-600">{summary.weeklyCount}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-600 text-sm font-medium mb-2">Aylik Ortalama Puan</h3>
          <p className="text-3xl font-bold text-green-600">{summary.monthlyAverage}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-600 text-sm font-medium mb-2">Haftalik Ortalama Puan</h3>
          <p className="text-3xl font-bold text-emerald-600">{summary.weeklyAverage}</p>
        </div>
      </div>

      {isAdmin && showForm && (
        <div className="bg-white p-6 rounded-lg shadow mb-8">
          <h2 className="text-xl font-bold mb-4">
            {editingCallId ? 'Kalite Puanlamasi Kaydini Duzenle' : 'Yeni Kalite Puanlamasi Kaydi'}
          </h2>
          <form onSubmit={handleAddCall} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-700 font-bold mb-2">Personel Adi</label>
              <select
                value={formData.personnel_id}
                onChange={(e) => setFormData({ ...formData, personnel_id: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                disabled={Boolean(editingCallId)}
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
              <label className="block text-gray-700 font-bold mb-2">Telefon Numarasi</label>
              <input
                type="tel"
                value={formData.phone_number}
                onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>
            <div>
              <label className="block text-gray-700 font-bold mb-2">Puan</label>
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
                disabled={isSubmitting}
                className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded transition"
              >
                {isSubmitting ? 'Kaydediliyor...' : 'Kaydet'}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">
          {selectedPersonnel ? 'Personel Kalite Kayitlari' : 'Tum Kalite Kayitlari'}
        </h2>
        {loading ? (
          <p className="text-center text-gray-500">Yukleniyor...</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-100">
                  <th className="px-4 py-2 text-left cursor-pointer" onClick={() => requestSort('personnel_name')}>Personel Adi {getSortArrow('personnel_name')}</th>
                  <th className="px-4 py-2 text-left cursor-pointer" onClick={() => requestSort('phone_number')}>Telefon Numarasi {getSortArrow('phone_number')}</th>
                  <th className="px-4 py-2 text-center cursor-pointer" onClick={() => requestSort('quality_score')}>Puan {getSortArrow('quality_score')}</th>
                  <th className="px-4 py-2 text-left cursor-pointer" onClick={() => requestSort('updated_display')}>Son Guncellenen {getSortArrow('updated_display')}</th>
                  <th className="px-4 py-2 text-left cursor-pointer" onClick={() => requestSort('notes')}>Not {getSortArrow('notes')}</th>
                  <th className="px-4 py-2 text-center">Duzenle</th>
                  {isAdmin && <th className="px-4 py-2 text-center">Sil</th>}
                </tr>
              </thead>
              <tbody>
                {processedCalls.map((call) => (
                  <tr key={call.id} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-2">{call.personnel_name}</td>
                    <td className="px-4 py-2">{call.phone_number}</td>
                    <td className={`px-4 py-2 text-center font-bold ${getScoreColor(call.quality_score)}`}>
                      {call.quality_score}
                    </td>
                    <td className="px-4 py-2">
                      {call.updated_display}
                    </td>
                    <td className="px-4 py-2">{call.notes}</td>
                    <td className="px-4 py-2 text-center">
                      <button
                        onClick={() => handleEditCall(call)}
                        className="rounded bg-amber-500 px-3 py-1 text-sm font-bold text-white transition hover:bg-amber-600"
                      >
                        Duzenle
                      </button>
                    </td>
                    {isAdmin && (
                      <td className="px-4 py-2 text-center">
                        <button
                          onClick={() => setConfirmDeleteId(call.id)}
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