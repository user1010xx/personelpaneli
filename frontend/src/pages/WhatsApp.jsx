import React, { useEffect, useMemo, useState } from 'react'
import { personnelApi, whatsappApi } from '../api'
import { useAuth } from '../App'
import { formatLocalDate } from '../utils/date'
import { exportRowsToExcel } from '../utils/exportExcel'

const formatDateForInput = (value) => {
  return formatLocalDate(value)
}

const getDefaultDateRange = () => {
  const today = new Date()
  const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)

  return {
    startDate: formatDateForInput(startOfMonth),
    endDate: formatDateForInput(today),
  }
}

export default function WhatsApp() {
  const { isAdmin } = useAuth()
  const defaultDateRange = getDefaultDateRange()
  const [whatsapp, setWhatsApp] = useState([])
  const [personnel, setPersonnel] = useState([])
  const [selectedPersonnel, setSelectedPersonnel] = useState(null)
  const [loading, setLoading] = useState(false)
  const [syncing, setSyncing] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [sortConfig, setSortConfig] = useState({ key: 'personnel_name', direction: 'asc' })
  const [startDate, setStartDate] = useState(defaultDateRange.startDate)
  const [endDate, setEndDate] = useState(defaultDateRange.endDate)

  useEffect(() => {
    loadPersonnel()
  }, [])

  useEffect(() => {
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
      setError('')
      const params = { start_date: startDate, end_date: endDate, limit: 1000 }
      if (selectedPersonnel) {
        const data = await whatsappApi.getPersonnelData(selectedPersonnel, params)
        setWhatsApp(data)
      } else {
        const data = await whatsappApi.list(params)
        setWhatsApp(data)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const processedRecords = useMemo(() => {
    const mapped = whatsapp.map((item) => ({
      ...item,
      personnel_name: personnel.find((person) => person.id === item.personnel_id)?.name || '',
    }))

    const filtered = mapped.filter((item) => {
      const haystack = [
        item.personnel_name,
        item.whatsapp_count,
        item.device_count,
        item.average_unanswered_count,
        item.unanswered_count,
      ].join(' ').toLocaleLowerCase('tr')

      return haystack.includes(searchTerm.toLocaleLowerCase('tr'))
    })

    return filtered.sort((first, second) => {
      const numericKeys = ['whatsapp_count', 'device_count', 'average_unanswered_count', 'unanswered_count']
      let comparison = 0

      if (sortConfig.key === 'date') {
        comparison = new Date(first.date || 0) - new Date(second.date || 0)
      } else if (numericKeys.includes(sortConfig.key)) {
        comparison = Number(first[sortConfig.key] || 0) - Number(second[sortConfig.key] || 0)
      } else {
        comparison = String(first[sortConfig.key] || '').localeCompare(
          String(second[sortConfig.key] || ''),
          'tr',
          { sensitivity: 'base' }
        )
      }

      return sortConfig.direction === 'asc' ? comparison : -comparison
    })
  }, [personnel, searchTerm, sortConfig, whatsapp])

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

  const handleSyncDocs = async () => {
    try {
      setSyncing(true)
      setError('')
      await whatsappApi.syncDocs()
      await loadWhatsApp()
      setSuccessMessage('GUNCELLEME TAMAMLANDI')
    } catch (err) {
      setError(err.message)
    } finally {
      setSyncing(false)
    }
  }

  const totalWhatsappCount = processedRecords.reduce((sum, item) => sum + Number(item.whatsapp_count || 0), 0)
  const totalDeviceCount = processedRecords.reduce((sum, item) => sum + Number(item.device_count || 0), 0)
  const totalUnanswered = processedRecords.reduce((sum, item) => sum + Number(item.unanswered_count || 0), 0)
  const averageUnanswered = processedRecords.length > 0 ? (totalUnanswered / processedRecords.length).toFixed(2) : '0.00'

  const exportToExcel = () => {
    exportRowsToExcel(
      processedRecords.map((item) => ({
        'Personel Adı': item.personnel_name,
        'WhatsApp Adedi': item.whatsapp_count,
        'Cihaz Adedi': item.device_count,
        'Ortalama Cevapsız': item.average_unanswered_count,
        'Total Cevapsız': item.unanswered_count,
      })),
      'WhatsApp',
      'whatsapp'
    )
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
            <p className="mb-6 text-sm text-gray-500">WhatsApp verileri basariyla yenilendi.</p>
            <button
              onClick={() => setSuccessMessage('')}
              className="rounded-lg bg-green-600 px-6 py-3 font-bold text-white transition hover:bg-green-700"
            >
              Tamam
            </button>
          </div>
        </div>
      )}

      <h1 className="mb-8 text-3xl font-bold">WhatsApp Takip</h1>

      {error && (
        <div className="mb-4 rounded border border-red-400 bg-red-100 px-4 py-3 text-red-700">
          {error}
        </div>
      )}

      <div className="mb-8 grid grid-cols-1 gap-4 md:grid-cols-5">
        <div className="rounded-lg bg-white p-6 shadow">
          <h3 className="mb-2 text-sm font-medium text-gray-600">Toplam WhatsApp Adedi</h3>
          <p className="text-3xl font-bold text-blue-600">{totalWhatsappCount}</p>
        </div>
        <div className="rounded-lg bg-white p-6 shadow">
          <h3 className="mb-2 text-sm font-medium text-gray-600">Toplam Cihaz Adedi</h3>
          <p className="text-3xl font-bold text-purple-600">{totalDeviceCount}</p>
        </div>
        <div className="rounded-lg bg-white p-6 shadow">
          <h3 className="mb-2 text-sm font-medium text-gray-600">Ortalama Cevapsiz</h3>
          <p className="text-3xl font-bold text-orange-600">{averageUnanswered}</p>
        </div>
        <div className="rounded-lg bg-white p-6 shadow">
          <h3 className="mb-2 text-sm font-medium text-gray-600">Total Cevapsiz</h3>
          <p className="text-3xl font-bold text-red-600">{totalUnanswered}</p>
        </div>
      </div>

      <div className="mb-8 grid grid-cols-1 gap-4 md:grid-cols-4">
        <div>
          <label className="mb-2 block font-bold text-gray-700">Personel</label>
          <select
            value={selectedPersonnel || ''}
            onChange={(e) => setSelectedPersonnel(e.target.value ? parseInt(e.target.value, 10) : null)}
            className="w-full rounded-lg border border-gray-300 px-4 py-2"
          >
            <option value="">Tumu</option>
            {personnel.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-2 block font-bold text-gray-700">Baslangic Tarihi</label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-4 py-2"
          />
        </div>
        <div>
          <label className="mb-2 block font-bold text-gray-700">Bitis Tarihi</label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-4 py-2"
          />
        </div>
        {isAdmin && (
        <div className="flex items-end">
          <button
            onClick={handleSyncDocs}
            disabled={syncing}
            className="w-full rounded bg-blue-500 px-4 py-2 font-bold text-white transition hover:bg-blue-600 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {syncing ? 'Hazirlaniyor...' : 'Docs Baglantisini Hazirla'}
          </button>
        </div>
        )}
        <div className="flex items-end">
          <button
            onClick={exportToExcel}
            className="w-full rounded bg-green-500 px-4 py-2 font-bold text-white transition hover:bg-green-600"
          >
            Export
          </button>
        </div>
      </div>

      <div className="mb-8">
        <label className="mb-2 block font-bold text-gray-700">Ara</label>
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Personel, WhatsApp adedi, cihaz adedi veya cevapsize gore ara"
          className="w-full rounded-lg border border-gray-300 px-4 py-2"
        />
      </div>

      <div className="rounded-lg bg-white p-6 shadow">
        <h2 className="mb-4 text-xl font-bold">
          {selectedPersonnel ? 'Personel WhatsApp Verileri' : 'Tum WhatsApp Verileri'}
        </h2>
        {loading ? (
          <p className="text-center text-gray-500">Yukleniyor...</p>
        ) : processedRecords.length === 0 ? (
          <p className="py-8 text-center text-gray-500">Bu donemde veri bulunmamaktadir</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-100">
                  <th className="cursor-pointer px-4 py-2 text-left" onClick={() => requestSort('personnel_name')}>
                    Personel Adi {getSortArrow('personnel_name')}
                  </th>
                  <th className="cursor-pointer px-4 py-2 text-center" onClick={() => requestSort('whatsapp_count')}>
                    WhatsApp Adedi {getSortArrow('whatsapp_count')}
                  </th>
                  <th className="cursor-pointer px-4 py-2 text-center" onClick={() => requestSort('device_count')}>
                    Cihaz Adedi {getSortArrow('device_count')}
                  </th>
                  <th className="cursor-pointer px-4 py-2 text-center" onClick={() => requestSort('average_unanswered_count')}>
                    Ortalama Cevapsiz {getSortArrow('average_unanswered_count')}
                  </th>
                  <th className="cursor-pointer px-4 py-2 text-center" onClick={() => requestSort('unanswered_count')}>
                    Total Cevapsiz {getSortArrow('unanswered_count')}
                  </th>
                </tr>
              </thead>
              <tbody>
                {processedRecords.map((item) => (
                  <tr key={item.id} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-2">{item.personnel_name}</td>
                    <td className="px-4 py-2 text-center font-bold">{item.whatsapp_count}</td>
                    <td className="px-4 py-2 text-center font-bold">{item.device_count}</td>
                    <td className="px-4 py-2 text-center font-bold">{item.average_unanswered_count}</td>
                    <td className="px-4 py-2 text-center font-bold text-red-600">{item.unanswered_count}</td>
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