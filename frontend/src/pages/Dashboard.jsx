import React, { useState, useEffect } from 'react'
import { personnelApi, salesApi, attendanceApi, warningsApi } from '../api'

export default function Dashboard() {
  const [personnel, setPersonnel] = useState([])
  const [startDate, setStartDate] = useState(new Date().toISOString().split('T')[0])
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0])
  const [salesSummary, setSalesSummary] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    loadPersonnel()
  }, [])

  useEffect(() => {
    if (startDate && endDate) {
      loadSalesSummary()
    }
  }, [startDate, endDate])

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

  const loadSalesSummary = async () => {
    try {
      setLoading(true)
      const data = await salesApi.getAllSummary(startDate, endDate)
      setSalesSummary(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-600 text-sm font-medium mb-2">Toplam Personel</h3>
          <p className="text-3xl font-bold text-blue-600">{personnel.length}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-600 text-sm font-medium mb-2">Tarih Aralığı</h3>
          <p className="text-lg font-semibold">{startDate} / {endDate}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-600 text-sm font-medium mb-2">Toplam Satış</h3>
          <p className="text-3xl font-bold text-green-600">
            {salesSummary ? Object.values(salesSummary).reduce((sum, p) => sum + (p.total || 0), 0) : 0}
          </p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow mb-8">
        <h2 className="text-xl font-bold mb-4">Tarih Filtreleme</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-gray-700 font-bold mb-2">Başlangıç Tarihi</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg"
            />
          </div>
          <div>
            <label className="block text-gray-700 font-bold mb-2">Bitiş Tarihi</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg"
            />
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">Personel Satış Özeti</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-100">
                <th className="px-4 py-2 text-left">Personel Adı</th>
                <th className="px-4 py-2 text-center">Toplam Satış</th>
                <th className="px-4 py-2 text-center">Günlük Ortalama</th>
              </tr>
            </thead>
            <tbody>
              {salesSummary && Object.entries(salesSummary).map(([name, data]) => (
                <tr key={name} className="border-b hover:bg-gray-50">
                  <td className="px-4 py-2">{name}</td>
                  <td className="px-4 py-2 text-center font-semibold">{data.total}</td>
                  <td className="px-4 py-2 text-center">{data.average.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
