import React, { useEffect, useMemo, useState } from 'react'
import * as XLSX from 'xlsx'
import { callProcessApi, personnelApi } from '../api'
import { formatLocalDate } from '../utils/date'
import { useAuth } from '../App'

const formatDateForInput = (value) => {
  return formatLocalDate(value)
}

const getDefaultRange = () => {
  const today = new Date()
  const start = new Date(today.getFullYear(), today.getMonth(), 1)
  return {
    startDate: formatDateForInput(start),
    endDate: formatDateForInput(today),
  }
}

const formatDuration = (value) => {
  const totalSeconds = Number(value || 0)
  if (!Number.isFinite(totalSeconds) || totalSeconds <= 0) {
    return '00:00:00'
  }

  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = Math.floor(totalSeconds % 60)

  return [hours, minutes, seconds]
    .map((part) => String(part).padStart(2, '0'))
    .join(':')
}

export default function CallProcess() {
  const { isAdmin } = useAuth()
  const defaults = getDefaultRange()
  const [records, setRecords] = useState([])
  const [personnel, setPersonnel] = useState([])
  const [selectedPersonnel, setSelectedPersonnel] = useState('')
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [startDate, setStartDate] = useState(defaults.startDate)
  const [endDate, setEndDate] = useState(defaults.endDate)
  const [searchTerm, setSearchTerm] = useState('')
  const [sortConfig, setSortConfig] = useState({ key: 'personnel_name', direction: 'asc' })

  useEffect(() => {
    loadPersonnel()
  }, [])

  useEffect(() => {
    loadRecords()
  }, [startDate, endDate, selectedPersonnel])

  const loadPersonnel = async () => {
    try {
      const data = await personnelApi.list()
      setPersonnel(data)
    } catch (err) {
      setError(err.message)
    }
  }

  const loadRecords = async () => {
    try {
      setLoading(true)
      setError('')
      const params = {
        start_date: startDate,
        end_date: endDate,
        limit: 1000,
      }
      if (selectedPersonnel) {
        params.personnel_id = selectedPersonnel
      }
      const data = await callProcessApi.list(params)
      setRecords(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (event) => {
    event.preventDefault()
    if (!file) {
      setError('Lutfen bir dosya secin')
      return
    }

    try {
      setUploading(true)
      setError('')
      await callProcessApi.uploadExcel(file)
      setFile(null)
      await loadRecords()
      setSuccessMessage('GUNCELLEME TAMAMLANDI')
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
    }
  }

  const exportToExcel = () => {
    const data = records.map((record) => ({
      'Personel Adi': personnel.find((item) => item.id === record.personnel_id)?.name || '',
      'Tarih': record.date,
      'Arama Adedi': record.call_count,
      'Konusma Suresi': formatDuration(record.talk_duration),
      'Ortalama Caldirma Suresi': formatDuration(record.average_ring_duration),
      'Yukleme Tarihi': new Date(record.uploaded_date).toLocaleDateString('tr-TR'),
    }))

    const ws = XLSX.utils.json_to_sheet(data)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, 'Cagri Sureci')
    XLSX.writeFile(wb, `cagri_sureci_${formatLocalDate()}.xlsx`)
  }

  const mappedRecords = useMemo(() => {
    const filtered = records
      .map((record) => ({
        ...record,
        personnel_name: personnel.find((item) => item.id === record.personnel_id)?.name || '',
      }))
      .filter((record) => {
        const haystack = [
          record.personnel_name,
          record.call_count,
          formatDuration(record.talk_duration),
          formatDuration(record.average_ring_duration),
          new Date(record.uploaded_date).toLocaleDateString('tr-TR'),
        ].join(' ').toLocaleLowerCase('tr')

        return haystack.includes(searchTerm.toLocaleLowerCase('tr'))
      })

    return filtered.sort((first, second) => {
      let comparison = 0

      if (sortConfig.key === 'call_count') {
        comparison = Number(first.call_count || 0) - Number(second.call_count || 0)
      } else if (sortConfig.key === 'talk_duration') {
        comparison = Number(first.talk_duration || 0) - Number(second.talk_duration || 0)
      } else if (sortConfig.key === 'average_ring_duration') {
        comparison = Number(first.average_ring_duration || 0) - Number(second.average_ring_duration || 0)
      } else if (sortConfig.key === 'uploaded_date') {
        comparison = new Date(first.uploaded_date || 0) - new Date(second.uploaded_date || 0)
      } else {
        comparison = String(first[sortConfig.key] || '').localeCompare(
          String(second[sortConfig.key] || ''),
          'tr',
          { sensitivity: 'base' }
        )
      }

      return sortConfig.direction === 'asc' ? comparison : -comparison
    })
  }, [personnel, records, searchTerm, sortConfig])

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

  return (
    <div className="p-8">
      {successMessage && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center shadow-2xl">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100 text-3xl text-green-600">
              ✓
            </div>
            <h2 className="mb-2 text-2xl font-bold text-gray-900">{successMessage}</h2>
            <p className="mb-6 text-sm text-gray-500">Cagri sureci verileri basariyla guncellendi.</p>
            <button
              onClick={() => setSuccessMessage('')}
              className="rounded-lg bg-green-600 px-6 py-3 font-bold text-white transition hover:bg-green-700"
            >
              Tamam
            </button>
          </div>
        </div>
      )}

      <h1 className="text-3xl font-bold mb-8">Cagri Sureci</h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        {isAdmin && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-bold mb-4">Excel Dosyasi Yukle</h2>
          <form onSubmit={handleFileUpload}>
            <div className="mb-4">
              <label className="block text-gray-700 font-bold mb-2">
                Dosya Secin (Excel format)
              </label>
              <input
                type="file"
                accept=".xlsx,.xls,.csv"
                onChange={(e) => setFile(e.target.files[0])}
                className="w-full"
              />
              <p className="text-sm text-gray-600 mt-2">
                Beklenen sutunlar: Personel Adi, Arama Adedi, Konusma Suresi, Ortalama Caldirma Suresi
              </p>
              <p className="text-sm text-gray-600 mt-1">
                Yuklenen dosya T-1 mantigi ile dunun tarihine islenir.
              </p>
            </div>
            <button
              type="submit"
              disabled={uploading}
              className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition disabled:opacity-50"
            >
              {uploading ? 'Yukleniyor...' : 'Yukle'}
            </button>
          </form>
        </div>
        )}

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-bold mb-4">Tarih Araligi</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-gray-700 font-bold mb-2">Personel</label>
              <select
                value={selectedPersonnel}
                onChange={(e) => setSelectedPersonnel(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              >
                <option value="">Tumu</option>
                {personnel.map((item) => (
                  <option key={item.id} value={item.id}>{item.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-gray-700 font-bold mb-2">Baslangic</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-gray-700 font-bold mb-2">Bitis</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <button
              onClick={exportToExcel}
              className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded transition"
            >
              Excel'e Aktar
            </button>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">Cagri Sureci Verileri</h2>
        <div className="mb-4">
          <label className="block text-gray-700 font-bold mb-2">Ara</label>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Personel, arama adedi, konusma suresi, ortalama caldirma suresi veya yukleme tarihi"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
          />
        </div>
        {loading ? (
          <p className="text-center text-gray-500">Yukleniyor...</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-100">
                  <th className="px-4 py-2 text-left cursor-pointer" onClick={() => requestSort('personnel_name')}>Personel Adi {getSortArrow('personnel_name')}</th>
                  <th className="px-4 py-2 text-center cursor-pointer" onClick={() => requestSort('call_count')}>Arama Adedi {getSortArrow('call_count')}</th>
                  <th className="px-4 py-2 text-center cursor-pointer" onClick={() => requestSort('talk_duration')}>Konusma Suresi {getSortArrow('talk_duration')}</th>
                  <th className="px-4 py-2 text-center cursor-pointer" onClick={() => requestSort('average_ring_duration')}>Ortalama Caldirma Suresi {getSortArrow('average_ring_duration')}</th>
                  <th className="px-4 py-2 text-left cursor-pointer" onClick={() => requestSort('uploaded_date')}>Yukleme Tarihi {getSortArrow('uploaded_date')}</th>
                </tr>
              </thead>
              <tbody>
                {mappedRecords.map((record) => (
                  <tr key={record.id} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-2">{record.personnel_name}</td>
                    <td className="px-4 py-2 text-center font-semibold">{record.call_count}</td>
                    <td className="px-4 py-2 text-center font-semibold">{formatDuration(record.talk_duration)}</td>
                    <td className="px-4 py-2 text-center font-semibold">{formatDuration(record.average_ring_duration)}</td>
                    <td className="px-4 py-2 text-sm text-gray-600">
                      {new Date(record.uploaded_date).toLocaleDateString('tr-TR')}
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