import React, { useState, useEffect } from 'react'
import { attendanceApi, personnelApi } from '../api'

export default function Attendance() {
  const [attendance, setAttendance] = useState([])
  const [personnel, setPersonnel] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [month, setMonth] = useState(new Date().getMonth() + 1)
  const [year, setYear] = useState(new Date().getFullYear())
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    personnel_id: '',
    working_days: 0,
    leave_days: 0,
    salary_amount: 0,
  })

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
      setAttendance(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleAddAttendance = async (e) => {
    e.preventDefault()
    try {
      await attendanceApi.create({
        ...formData,
        month: parseInt(month),
        year: parseInt(year),
        personnel_id: parseInt(formData.personnel_id),
      })
      setFormData({
        personnel_id: '',
        working_days: 0,
        leave_days: 0,
        salary_amount: 0,
      })
      setShowForm(false)
      loadAttendance()
      alert('Puantaj kaydı başarıyla eklendi')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Puantaj Yönetimi</h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div>
          <label className="block text-gray-700 font-bold mb-2">Ay</label>
          <select
            value={month}
            onChange={(e) => setMonth(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
          >
            {Array.from({ length: 12 }, (_, i) => (
              <option key={i + 1} value={i + 1}>
                {new Date(2024, i).toLocaleDateString('tr-TR', { month: 'long' })}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-gray-700 font-bold mb-2">Yıl</label>
          <select
            value={year}
            onChange={(e) => setYear(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
          >
            <option value="2023">2023</option>
            <option value="2024">2024</option>
            <option value="2025">2025</option>
            <option value="2026">2026</option>
          </select>
        </div>
        <div className="flex items-end">
          <button
            onClick={() => setShowForm(!showForm)}
            className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition"
          >
            {showForm ? 'İptal' : 'Kayıt Ekle'}
          </button>
        </div>
      </div>

      {showForm && (
        <div className="bg-white p-6 rounded-lg shadow mb-8">
          <h2 className="text-xl font-bold mb-4">Yeni Puantaj Kaydı Ekle</h2>
          <form onSubmit={handleAddAttendance} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-700 font-bold mb-2">Personel</label>
              <select
                value={formData.personnel_id}
                onChange={(e) => setFormData({ ...formData, personnel_id: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              >
                <option value="">Seçiniz</option>
                {personnel.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-gray-700 font-bold mb-2">Çalışma Günü</label>
              <input
                type="number"
                step="0.5"
                value={formData.working_days}
                onChange={(e) => setFormData({ ...formData, working_days: parseFloat(e.target.value) })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>
            <div>
              <label className="block text-gray-700 font-bold mb-2">İzin Günü</label>
              <input
                type="number"
                step="0.5"
                value={formData.leave_days}
                onChange={(e) => setFormData({ ...formData, leave_days: parseFloat(e.target.value) })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>
            <div>
              <label className="block text-gray-700 font-bold mb-2">Maaş (TL)</label>
              <input
                type="number"
                step="0.01"
                value={formData.salary_amount}
                onChange={(e) => setFormData({ ...formData, salary_amount: parseFloat(e.target.value) })}
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
        <h2 className="text-xl font-bold mb-4">Puantaj Listesi ({month}/{year})</h2>
        {loading ? (
          <p className="text-center text-gray-500">Yükleniyor...</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-100">
                  <th className="px-4 py-2 text-left">Personel</th>
                  <th className="px-4 py-2 text-center">Çalışma Günü</th>
                  <th className="px-4 py-2 text-center">İzin Günü</th>
                  <th className="px-4 py-2 text-center">Toplam</th>
                  <th className="px-4 py-2 text-center">Maaş</th>
                </tr>
              </thead>
              <tbody>
                {attendance.map((a) => (
                  <tr key={a.id} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-2">
                      {personnel.find((p) => p.id === a.personnel_id)?.name}
                    </td>
                    <td className="px-4 py-2 text-center">{a.working_days}</td>
                    <td className="px-4 py-2 text-center">{a.leave_days}</td>
                    <td className="px-4 py-2 text-center font-semibold">
                      {(a.working_days + a.leave_days).toFixed(1)}
                    </td>
                    <td className="px-4 py-2 text-center">
                      {a.salary_amount ? `${a.salary_amount.toFixed(2)} TL` : '-'}
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
