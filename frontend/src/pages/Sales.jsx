import React, { useEffect, useMemo, useState } from 'react'
import * as XLSX from 'xlsx'
import { personnelApi, salesApi } from '../api'
import { formatLocalDate } from '../utils/date'
import { useAuth } from '../App'

const formatDateForInput = (value) => {
  return formatLocalDate(value)
}

const getDefaultRange = () => {
  const today = new Date()
  const firstDay = new Date(today.getFullYear(), today.getMonth(), 1)
  const yesterday = new Date(today.getFullYear(), today.getMonth(), Math.max(today.getDate() - 1, 1))

  return {
    startDate: formatDateForInput(firstDay),
    endDate: formatDateForInput(yesterday),
  }
}

export default function Sales() {
  const { isAdmin } = useAuth()
  const defaults = getDefaultRange()
  const [sales, setSales] = useState([])
  const [personnel, setPersonnel] = useState([])
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [sortConfig, setSortConfig] = useState({ key: 'personnel_name', direction: 'asc' })
  const [startDate, setStartDate] = useState(defaults.startDate)
  const [endDate, setEndDate] = useState(defaults.endDate)

  useEffect(() => {
    loadPersonnel()
  }, [])

  useEffect(() => {
    loadSales()
  }, [startDate, endDate])

  const loadPersonnel = async () => {
    try {
      const data = await personnelApi.list()
      setPersonnel(data)
    } catch (err) {
      setError(err.message)
    }
  }

  const loadSales = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await salesApi.list({
        start_date: startDate,
        end_date: endDate,
        limit: 1000,
      })
      setSales(data)
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
      await salesApi.uploadExcel(file)
      setFile(null)
      await loadSales()
      setSuccessMessage('GUNCELLEME TAMAMLANDI')
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
    }
  }

  const summarizedSales = useMemo(() => {
    const grouped = new Map()

    sales.forEach((sale) => {
      const personnelName = personnel.find((person) => person.id === sale.personnel_id)?.name || ''
      const current = grouped.get(sale.personnel_id) || {
        personnel_id: sale.personnel_id,
        personnel_name: personnelName,
        sales_count: 0,
        uploaded_date: sale.uploaded_date,
      }

      current.sales_count += Number(sale.sales_count || 0)
      if (!current.uploaded_date || new Date(sale.uploaded_date) > new Date(current.uploaded_date)) {
        current.uploaded_date = sale.uploaded_date
      }
      grouped.set(sale.personnel_id, current)
    })

    return [...grouped.values()]
      .map((item) => ({
        ...item,
        uploaded_date_display: item.uploaded_date
          ? new Date(item.uploaded_date).toLocaleDateString('tr-TR')
          : '-',
      }))
      .filter((item) => {
        const haystack = [
          item.personnel_name,
          item.sales_count,
          item.uploaded_date_display,
        ].join(' ').toLocaleLowerCase('tr')

        return haystack.includes(searchTerm.toLocaleLowerCase('tr'))
      })
      .sort((first, second) => {
        let comparison = 0

        if (sortConfig.key === 'sales_count') {
          comparison = Number(first.sales_count || 0) - Number(second.sales_count || 0)
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
  }, [personnel, sales, searchTerm, sortConfig])

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

  const exportToExcel = () => {
    const data = summarizedSales.map((sale) => ({
      'Personel Adi': sale.personnel_name,
      'Uye Adedi': sale.sales_count,
      'Yukleme Tarihi': sale.uploaded_date_display,
    }))

    const ws = XLSX.utils.json_to_sheet(data)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, 'Uye Adedi Verileri')
    XLSX.writeFile(wb, `uye_adedi_${formatLocalDate()}.xlsx`)
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
            <p className="mb-6 text-sm text-gray-500">Uye adedi verileri basariyla yuklendi.</p>
            <button
              onClick={() => setSuccessMessage('')}
              className="rounded-lg bg-green-600 px-6 py-3 font-bold text-white transition hover:bg-green-700"
            >
              Tamam
            </button>
          </div>
        </div>
      )}

      <h1 className="text-3xl font-bold mb-8">Uye Adedi</h1>

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
                Beklenen sutunlar: Personel Adi, Uye Adedi
              </p>
              <p className="text-sm text-gray-600 mt-1">
                Dosya her zaman T-1 mantigi ile dunun tarihine kaydedilir.
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
        <h2 className="text-xl font-bold mb-4">Uye Adedi Verileri</h2>
        <div className="mb-4">
          <label className="block text-gray-700 font-bold mb-2">Ara</label>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Personel, uye adedi veya yukleme tarihi ile ara"
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
                  <th className="px-4 py-2 text-left cursor-pointer" onClick={() => requestSort('personnel_name')}>
                    Personel {getSortArrow('personnel_name')}
                  </th>
                  <th className="px-4 py-2 text-center cursor-pointer" onClick={() => requestSort('sales_count')}>
                    Uye Adedi {getSortArrow('sales_count')}
                  </th>
                  <th className="px-4 py-2 text-left cursor-pointer" onClick={() => requestSort('uploaded_date')}>
                    Yukleme Tarihi {getSortArrow('uploaded_date')}
                  </th>
                </tr>
              </thead>
              <tbody>
                {summarizedSales.map((sale) => (
                  <tr key={sale.personnel_id} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-2">{sale.personnel_name}</td>
                    <td className="px-4 py-2 text-center font-semibold">{sale.sales_count}</td>
                    <td className="px-4 py-2 text-sm text-gray-600">{sale.uploaded_date_display}</td>
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