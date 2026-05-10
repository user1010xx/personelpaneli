import React, { useState, useEffect } from 'react'
import { personnelApi, salesApi } from '../api'
import * as XLSX from 'xlsx'

export default function Sales() {
  const [sales, setSales] = useState([])
  const [personnel, setPersonnel] = useState([])
  const [filteredPersonnel, setFilteredPersonnel] = useState(null)
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [startDate, setStartDate] = useState(new Date().toISOString().split('T')[0])
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0])

  useEffect(() => {
    loadPersonnel()
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
      const data = await salesApi.list({
        start_date: startDate,
        end_date: endDate,
      })
      setSales(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (e) => {
    e.preventDefault()
    if (!file) {
      setError('Lütfen bir dosya seçin')
      return
    }

    try {
      setLoading(true)
      await salesApi.uploadExcel(file)
      setError('')
      setFile(null)
      loadSales()
      alert('Satış verileri başarıyla yüklendi')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const exportToExcel = () => {
    const data = sales.map(s => ({
      'Personel Adı': personnel.find(p => p.id === s.personnel_id)?.name,
      'Tarih': s.date,
      'Satış Adedi': s.sales_count,
      'Yükleme Tarihi': new Date(s.uploaded_date).toLocaleDateString('tr-TR'),
    }))

    const ws = XLSX.utils.json_to_sheet(data)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, 'Satış Verileri')
    XLSX.writeFile(wb, `satis_${new Date().toISOString().split('T')[0]}.xlsx`)
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Satış Yönetimi</h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        {/* Excel Upload */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-bold mb-4">Excel Dosyası Yükle</h2>
          <form onSubmit={handleFileUpload}>
            <div className="mb-4">
              <label className="block text-gray-700 font-bold mb-2">
                Dosya Seçin (Excel format)
              </label>
              <input
                type="file"
                accept=".xlsx,.xls,.csv"
                onChange={(e) => setFile(e.target.files[0])}
                className="w-full"
              />
              <p className="text-sm text-gray-600 mt-2">
                Beklenen sütunlar: Personel Adı, Tarih, Satış Adedi
              </p>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition disabled:opacity-50"
            >
              {loading ? 'Yükleniyor...' : 'Yükle'}
            </button>
          </form>
        </div>

        {/* Tarih Filtreleme */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-bold mb-4">Tarih Aralığı</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-gray-700 font-bold mb-2">Başlangıç</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-gray-700 font-bold mb-2">Bitiş</label>
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

      {/* Satış Tablosu */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">Satış Verileri</h2>
        {loading ? (
          <p className="text-center text-gray-500">Yükleniyor...</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-100">
                  <th className="px-4 py-2 text-left">Personel</th>
                  <th className="px-4 py-2 text-left">Tarih</th>
                  <th className="px-4 py-2 text-center">Satış Adedi</th>
                  <th className="px-4 py-2 text-left">Yükleme Tarihi</th>
                </tr>
              </thead>
              <tbody>
                {sales.map((sale) => (
                  <tr key={sale.id} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-2">
                      {personnel.find(p => p.id === sale.personnel_id)?.name}
                    </td>
                    <td className="px-4 py-2">{sale.date}</td>
                    <td className="px-4 py-2 text-center font-semibold">{sale.sales_count}</td>
                    <td className="px-4 py-2 text-sm text-gray-600">
                      {new Date(sale.uploaded_date).toLocaleDateString('tr-TR')}
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
