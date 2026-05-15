import React, { useState, useEffect } from 'react'
import { attendanceApi, personnelApi } from '../api'
import { useAuth } from '../App'
import { exportRowsToExcel } from '../utils/exportExcel'

export default function Attendance() {
  const { isAdmin } = useAuth()
  const [attendance, setAttendance] = useState([])
  const [personnel, setPersonnel] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [month, setMonth] = useState(new Date().getMonth() + 1)
  const [year, setYear] = useState(new Date().getFullYear())

  useEffect(() => {
    loadPersonnel()
    loadAttendance()
  }, [month, year])

  const loadPersonnel = async () => {
    try {
      const data = await personnelApi.list()
      setPersonnel(data)
    } catch (err) {
      setError(err.message)
    }
  }

  const loadAttendance = async () => {
    try {
      setLoading(true)
      const data = await attendanceApi.list({ month, year })
      setAttendance(data.filter((item) => item.leave_type === 'docs'))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleSyncDocs = async () => {
    try {
      setError('')
      const response = await attendanceApi.syncDocs()
      const syncedMonth = response.month || month
      const syncedYear = response.year || year
      setMonth(syncedMonth)
      setYear(syncedYear)
      const data = await attendanceApi.list({ month: syncedMonth, year: syncedYear })
      setAttendance(data.filter((item) => item.leave_type === 'docs'))
      setSuccessMessage('GUNCELLEME TAMAMLANDI')
    } catch (err) {
      setError(err.message)
    }
  }

  const exportToExcel = () => {
    exportRowsToExcel(
      attendance.map((item) => ({
        Personel: personnel.find((person) => person.id === item.personnel_id)?.name || '',
        'Ödenecek Mesai': item.working_days,
        İzin: item.leave_days,
        Toplam: (item.working_days + item.leave_days).toFixed(1),
        Ay: month,
        Yıl: year,
      })),
      'Puantaj',
      'puantaj'
    )
  }

  return (
    <div className="p-8">
      {successMessage && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-2xl text-center">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100 text-3xl text-green-600">✓</div>
            <h2 className="mb-2 text-2xl font-bold text-gray-900">{successMessage}</h2>
            <p className="mb-6 text-sm text-gray-500">Puantaj verileri basariyla yenilendi.</p>
            <button onClick={() => setSuccessMessage('')} className="rounded-lg bg-green-600 px-6 py-3 font-bold text-white transition hover:bg-green-700">Tamam</button>
          </div>
        </div>
      )}

      <h1 className="text-3xl font-bold mb-8">Puantaj</h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div>
          <label className="block text-gray-700 font-bold mb-2">Ay</label>
          <select value={month} onChange={(e) => setMonth(parseInt(e.target.value))} className="w-full px-4 py-2 border border-gray-300 rounded-lg">
            {Array.from({ length: 12 }, (_, i) => (
              <option key={i + 1} value={i + 1}>
                {new Date(2024, i).toLocaleDateString('tr-TR', { month: 'long' })}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-gray-700 font-bold mb-2">Yil</label>
          <select value={year} onChange={(e) => setYear(parseInt(e.target.value))} className="w-full px-4 py-2 border border-gray-300 rounded-lg">
            <option value="2024">2024</option>
            <option value="2025">2025</option>
            <option value="2026">2026</option>
            <option value="2027">2027</option>
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
        <h2 className="text-xl font-bold mb-4">Puantaj Ozeti ({month}/{year})</h2>
        {loading ? (
          <p className="text-center text-gray-500">Yukleniyor...</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-100">
                  <th className="px-4 py-2 text-left">Personel</th>
                  <th className="px-4 py-2 text-center">Odenecek Mesai</th>
                  <th className="px-4 py-2 text-center">Izin</th>
                  <th className="px-4 py-2 text-center">Toplam</th>
                </tr>
              </thead>
              <tbody>
                {attendance.map((item) => (
                  <tr key={item.id} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-2">{personnel.find((person) => person.id === item.personnel_id)?.name}</td>
                    <td className="px-4 py-2 text-center font-semibold text-green-700">{item.working_days}</td>
                    <td className="px-4 py-2 text-center font-semibold text-red-600">{item.leave_days}</td>
                    <td className="px-4 py-2 text-center font-bold">{(item.working_days + item.leave_days).toFixed(1)}</td>
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