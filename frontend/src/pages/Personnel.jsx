import React, { useState, useEffect } from 'react'
import { personnelApi } from '../api'
import { useAuth } from '../App'
import { exportRowsToExcel } from '../utils/exportExcel'

export default function Personnel() {
  const { isAdmin } = useAuth()
  const [personnel, setPersonnel] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')

  useEffect(() => {
    loadPersonnel()
  }, [])

  const formatDisplayDate = (value) => {
    if (!value) {
      return '-'
    }
    const parts = String(value).split('-')
    if (parts.length === 3) {
      return `${parts[2]}.${parts[1]}.${parts[0]}`
    }
    return value
  }

  const loadPersonnel = async () => {
    try {
      setLoading(true)
      const data = await personnelApi.list()
      setPersonnel(data.filter((person) => person.username || person.hire_date || person.reference || person.promotion_date))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleSyncDocs = async () => {
    try {
      const response = await personnelApi.syncDocs()
      setSuccessMessage('GUNCELLEME TAMAMLANDI')
      loadPersonnel()
    } catch (err) {
      setError(err.message)
    }
  }

  const exportToExcel = () => {
    exportRowsToExcel(
      personnel.map((person) => ({
        'Personel Adı': person.name,
        'Kullanıcı Adı': person.username || person.employee_id,
        'İşe Giriş Tarihi': formatDisplayDate(person.hire_date),
        Referans: person.reference || '-',
        Mail: person.email || '-',
        'Terfi Tarihi': formatDisplayDate(person.promotion_date),
      })),
      'Personel Listesi',
      'personel_listesi'
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
            <p className="mb-6 text-sm text-gray-500">Personel verileri basariyla yenilendi.</p>
            <button
              onClick={() => setSuccessMessage('')}
              className="rounded-lg bg-green-600 px-6 py-3 font-bold text-white transition hover:bg-green-700"
            >
              Tamam
            </button>
          </div>
        </div>
      )}

      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Personel Listesi</h1>
        <div className="flex gap-3">
          <button
            onClick={exportToExcel}
            className="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded transition"
          >
            Export
          </button>
          {isAdmin && (
          <button
            onClick={handleSyncDocs}
            className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition"
          >
            Docs Baglantisini Hazirla
          </button>
          )}
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">Google Sheets Personel Listesi</h2>
        {loading ? (
          <p className="text-center text-gray-500">Yukleniyor...</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-100">
                  <th className="px-4 py-2 text-left">Personel Adi</th>
                  <th className="px-4 py-2 text-left">Kullanici Adi</th>
                  <th className="px-4 py-2 text-left">Ise Giris Tarihi</th>
                  <th className="px-4 py-2 text-left">Referans</th>
                  <th className="px-4 py-2 text-left">Mail</th>
                  <th className="px-4 py-2 text-left">Terfi Tarihi</th>
                </tr>
              </thead>
              <tbody>
                {personnel.map((person) => (
                  <tr key={person.id} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-2">{person.name}</td>
                    <td className="px-4 py-2">{person.username || person.employee_id}</td>
                    <td className="px-4 py-2">{formatDisplayDate(person.hire_date)}</td>
                    <td className="px-4 py-2">{person.reference || '-'}</td>
                    <td className="px-4 py-2">{person.email || '-'}</td>
                    <td className="px-4 py-2">{formatDisplayDate(person.promotion_date)}</td>
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