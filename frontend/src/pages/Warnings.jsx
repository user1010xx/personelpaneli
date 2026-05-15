import React, { useState, useEffect } from 'react'
import { warningsApi, personnelApi } from '../api'
import { useAuth } from '../App'
import { exportRowsToExcel } from '../utils/exportExcel'

export default function Warnings() {
  const { isAdmin } = useAuth()
  const [warnings, setWarnings] = useState([])
  const [personnel, setPersonnel] = useState([])
  const [selectedPersonnel, setSelectedPersonnel] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [sortConfig, setSortConfig] = useState({ key: 'date', direction: 'desc' })

  useEffect(() => {
    loadPersonnel()
    loadWarnings()
  }, [selectedPersonnel])

  const formatDisplayDate = (value) => {
    if (!value) return '-'
    const parts = String(value).split('-')
    if (parts.length === 3) return `${parts[2]}.${parts[1]}.${parts[0]}`
    return value
  }

  const parseDateValue = (value) => {
    if (!value) return 0
    const parsed = new Date(value)
    return Number.isNaN(parsed.getTime()) ? 0 : parsed.getTime()
  }

  const parseDeductionValue = (value) => {
    if (!value) return 0
    const match = String(value).match(/\d+/)
    return match ? parseInt(match[0], 10) : 0
  }

  const requestSort = (key) => {
    let direction = 'asc'
    if (sortConfig.key === key && sortConfig.direction === 'asc') direction = 'desc'
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

  const loadWarnings = async () => {
    try {
      setLoading(true)
      if (selectedPersonnel) {
        const data = await warningsApi.getPersonnelWarnings(selectedPersonnel)
        setWarnings(data)
      } else {
        const data = await warningsApi.list({})
        setWarnings(data)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleSyncDocs = async () => {
    try {
      setError('')
      await warningsApi.syncDocs()
      setSuccessMessage('GUNCELLEME TAMAMLANDI')
      await loadWarnings()
    } catch (err) {
      setSuccessMessage('')
      setError(err.message)
    }
  }

  const getSortedWarnings = () => {
    const mappedWarnings = warnings.map((item) => ({
      ...item,
      personnel_name: personnel.find((person) => person.id === item.personnel_id)?.name || '',
      deduction_display: item.deduction || 'Uyari',
    }))

    const filteredWarnings = mappedWarnings.filter((item) => {
      const haystack = [
        item.personnel_name,
        item.deduction_display,
        item.subject,
      ].join(' ').toLocaleLowerCase('tr')

      return haystack.includes(searchTerm.toLocaleLowerCase('tr'))
    })

    return [...filteredWarnings].sort((first, second) => {
      let comparison = 0

      if (sortConfig.key === 'date') {
        comparison = parseDateValue(first.date) - parseDateValue(second.date)
      } else if (sortConfig.key === 'deduction_display') {
        const firstDeduction = parseDeductionValue(first.deduction_display)
        const secondDeduction = parseDeductionValue(second.deduction_display)
        if (firstDeduction !== secondDeduction) {
          comparison = firstDeduction - secondDeduction
        } else {
          comparison = String(first.deduction_display).localeCompare(
            String(second.deduction_display),
            'tr',
            { sensitivity: 'base' }
          )
        }
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
      getSortedWarnings().map((warning) => ({
        'Personel Adı': warning.personnel_name,
        Kesinti: warning.deduction_display,
        Konu: warning.subject,
        Tarih: formatDisplayDate(warning.date),
      })),
      'Uyarı Kesinti',
      'uyari_kesinti'
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
            <p className="mb-6 text-sm text-gray-500">Uyari kesinti verileri basariyla yenilendi.</p>
            <button onClick={() => setSuccessMessage('')} className="rounded-lg bg-green-600 px-6 py-3 font-bold text-white transition hover:bg-green-700">
              Tamam
            </button>
          </div>
        </div>
      )}

      <h1 className="text-3xl font-bold mb-8">Uyari Kesinti</h1>

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
              <option key={person.id} value={person.id}>{person.name}</option>
            ))}
          </select>
        </div>
        {isAdmin && (
        <div className="flex items-end">
          <button onClick={handleSyncDocs} className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition">
            Docs Baglantisini Hazirla
          </button>
        </div>
        )}
        <div className="flex items-end">
          <button onClick={exportToExcel} className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded transition">
            Export
          </button>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">
          {selectedPersonnel ? 'Personel Uyari Kesinti Kayitlari' : 'Tum Uyari Kesinti Kayitlari'}
        </h2>
        <div className="mb-4">
          <label className="block text-gray-700 font-bold mb-2">Ara</label>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Isim, konu veya kesinti ile ara"
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
                  <th className="px-4 py-2 text-left cursor-pointer" onClick={() => requestSort('deduction_display')}>Kesinti {getSortArrow('deduction_display')}</th>
                  <th className="px-4 py-2 text-left cursor-pointer" onClick={() => requestSort('subject')}>Konu {getSortArrow('subject')}</th>
                  <th className="px-4 py-2 text-left cursor-pointer" onClick={() => requestSort('date')}>Tarih {getSortArrow('date')}</th>
                </tr>
              </thead>
              <tbody>
                {getSortedWarnings().map((warning) => (
                  <tr key={warning.id} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-2">{warning.personnel_name}</td>
                    <td className="px-4 py-2">{warning.deduction_display}</td>
                    <td className="px-4 py-2">{warning.subject}</td>
                    <td className="px-4 py-2">{formatDisplayDate(warning.date)}</td>
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