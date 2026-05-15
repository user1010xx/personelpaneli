import React, { useEffect, useMemo, useState } from 'react'
import { docsLinksApi, usersApi } from '../api'
import { exportRowsToExcel } from '../utils/exportExcel'

const initialForm = {
  username: '',
  email: '',
  full_name: '',
  role: 'user',
  password: '',
}

const docsInitialState = {
  personnel: '',
  attendance: '',
  warnings: '',
  whatsapp: '',
}

export default function Users() {
  const [users, setUsers] = useState([])
  const [docsLinks, setDocsLinks] = useState(docsInitialState)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [confirmDeleteUserId, setConfirmDeleteUserId] = useState(null)
  const [passwordVisible, setPasswordVisible] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [sortConfig, setSortConfig] = useState({ key: 'full_name', direction: 'asc' })
  const [editingUserId, setEditingUserId] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState(initialForm)

  useEffect(() => {
    loadUsers()
    loadDocsLinks()
  }, [])

  const loadUsers = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await usersApi.list()
      setUsers(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const loadDocsLinks = async () => {
    try {
      const data = await docsLinksApi.list()
      const nextState = { ...docsInitialState }
      data.forEach((item) => {
        nextState[item.key] = item.url
      })
      setDocsLinks(nextState)
    } catch (err) {
      setError(err.message)
    }
  }

  const resetForm = () => {
    setFormData(initialForm)
    setEditingUserId(null)
    setShowForm(false)
    setPasswordVisible(false)
  }

  const generatePassword = () => {
    const uppercase = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
    const lowercase = 'abcdefghijkmnopqrstuvwxyz'
    const numbers = '23456789'
    const special = '!@#$%^&*'
    const allChars = uppercase + lowercase + numbers + special

    const requiredChars = [
      uppercase[Math.floor(Math.random() * uppercase.length)],
      lowercase[Math.floor(Math.random() * lowercase.length)],
      numbers[Math.floor(Math.random() * numbers.length)],
      special[Math.floor(Math.random() * special.length)],
    ]

    while (requiredChars.length < 12) {
      requiredChars.push(allChars[Math.floor(Math.random() * allChars.length)])
    }

    const password = requiredChars.sort(() => Math.random() - 0.5).join('')
    setFormData((current) => ({ ...current, password }))
    setPasswordVisible(true)
  }

  const copyPassword = async () => {
    if (!formData.password) {
      setError('Kopyalanacak sifre bulunamadi')
      return
    }

    try {
      await navigator.clipboard.writeText(formData.password)
      setSuccessMessage('SIFRE KOPYALANDI')
    } catch {
      setError('Sifre kopyalanamadi')
    }
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    try {
      setError('')
      if (editingUserId) {
        const payload = {
          username: formData.username,
          email: formData.email,
          full_name: formData.full_name,
          role: formData.role,
        }
        if (formData.password) {
          payload.password = formData.password
        }
        await usersApi.update(editingUserId, payload)
      } else {
        await usersApi.create(formData)
      }
      await loadUsers()
      resetForm()
      setSuccessMessage('ISLEM TAMAMLANDI')
    } catch (err) {
      setError(err.message)
    }
  }

  const handleSaveDocsLinks = async () => {
    try {
      setError('')
      const updates = Object.entries(docsLinks)
        .filter(([, url]) => url.trim())
        .map(([key, url]) => docsLinksApi.update(key, { url }))
      if (!updates.length) {
        setError('Kaydedilecek docs linki bulunamadi')
        return
      }
      await Promise.all(updates)
      await loadDocsLinks()
      setSuccessMessage('ISLEM TAMAMLANDI')
    } catch (err) {
      setError(err.message)
    }
  }

  const handleEdit = (user) => {
    setEditingUserId(user.id)
    setFormData({
      username: user.username,
      email: user.email,
      full_name: user.full_name || '',
      role: user.role,
      password: '',
    })
    setShowForm(true)
  }

  const handleDelete = async (userId) => {
    try {
      setError('')
      await usersApi.delete(userId)
      await loadUsers()
      setSuccessMessage('ISLEM TAMAMLANDI')
    } catch (err) {
      setError(err.message)
    }
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

  const processedUsers = useMemo(() => {
    const filtered = users.filter((user) => {
      const haystack = [user.full_name, user.username, user.email, user.role]
        .join(' ')
        .toLocaleLowerCase('tr')
      return haystack.includes(searchTerm.toLocaleLowerCase('tr'))
    })

    return [...filtered].sort((first, second) => {
      const comparison = String(first[sortConfig.key] || '').localeCompare(
        String(second[sortConfig.key] || ''),
        'tr',
        { sensitivity: 'base' }
      )
      return sortConfig.direction === 'asc' ? comparison : -comparison
    })
  }, [searchTerm, sortConfig, users])

  const exportToExcel = () => {
    exportRowsToExcel(
      processedUsers.map((user) => ({
        Isim: user.full_name || '-',
        'Kullanici Adi': user.username,
        Mail: user.email,
        Statu: user.role === 'admin' ? 'Admin' : 'Kullanici',
      })),
      'Kullanicilar',
      'kullanicilar'
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
            <p className="mb-6 text-sm text-gray-500">Islem basariyla tamamlandi.</p>
            <button
              onClick={() => setSuccessMessage('')}
              className="rounded-lg bg-green-600 px-6 py-3 font-bold text-white transition hover:bg-green-700"
            >
              Tamam
            </button>
          </div>
        </div>
      )}

      {confirmDeleteUserId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center shadow-2xl">
            <h2 className="mb-2 text-2xl font-bold text-gray-900">Kullanici silinsin mi?</h2>
            <p className="mb-6 text-sm text-gray-500">Bu islem geri alinamaz.</p>
            <div className="flex justify-center gap-3">
              <button
                onClick={() => setConfirmDeleteUserId(null)}
                className="rounded-lg bg-gray-200 px-5 py-2 font-bold text-gray-700 transition hover:bg-gray-300"
              >
                Vazgec
              </button>
              <button
                onClick={() => {
                  const userId = confirmDeleteUserId
                  setConfirmDeleteUserId(null)
                  handleDelete(userId)
                }}
                className="rounded-lg bg-red-600 px-5 py-2 font-bold text-white transition hover:bg-red-700"
              >
                Sil
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-3xl font-bold">KULLANICI YONETIMI VE DUZENLEME</h1>
        <button
          onClick={() => (showForm ? resetForm() : setShowForm(true))}
          className="rounded bg-blue-500 px-4 py-2 font-bold text-white transition hover:bg-blue-600"
        >
          {showForm ? 'Iptal' : 'Kullanici Ekle'}
        </button>
      </div>

      {error && (
        <div className="mb-4 rounded border border-red-400 bg-red-100 px-4 py-3 text-red-700">
          {error}
        </div>
      )}

      <div className="mb-8 rounded-lg bg-white p-6 shadow">
        <h2 className="mb-4 text-xl font-bold">Guncel Docs Linkleri</h2>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label className="mb-2 block font-bold text-gray-700">Puantaj Guncel Link</label>
            <input
              type="text"
              value={docsLinks.attendance}
              onChange={(e) => setDocsLinks((current) => ({ ...current, attendance: e.target.value }))}
              className="w-full rounded-lg border border-gray-300 px-4 py-2"
            />
          </div>
          <div>
            <label className="mb-2 block font-bold text-gray-700">Uyari Kesinti Guncel Link</label>
            <input
              type="text"
              value={docsLinks.warnings}
              onChange={(e) => setDocsLinks((current) => ({ ...current, warnings: e.target.value }))}
              className="w-full rounded-lg border border-gray-300 px-4 py-2"
            />
          </div>
          <div>
            <label className="mb-2 block font-bold text-gray-700">Whatsapp Guncel Link</label>
            <input
              type="text"
              value={docsLinks.whatsapp}
              onChange={(e) => setDocsLinks((current) => ({ ...current, whatsapp: e.target.value }))}
              className="w-full rounded-lg border border-gray-300 px-4 py-2"
            />
          </div>
          <div>
            <label className="mb-2 block font-bold text-gray-700">Personel Guncel Link</label>
            <input
              type="text"
              value={docsLinks.personnel}
              onChange={(e) => setDocsLinks((current) => ({ ...current, personnel: e.target.value }))}
              className="w-full rounded-lg border border-gray-300 px-4 py-2"
            />
          </div>
        </div>
        <div className="mt-4">
          <button
            type="button"
            onClick={handleSaveDocsLinks}
            className="rounded bg-green-500 px-5 py-2 font-bold text-white transition hover:bg-green-600"
          >
            Linkleri Kaydet
          </button>
        </div>
      </div>

      {showForm && (
        <div className="mb-8 rounded-lg bg-white p-6 shadow">
          <h2 className="mb-4 text-xl font-bold">
            {editingUserId ? 'Kullanici Duzenle' : 'Yeni Kullanici Ekle'}
          </h2>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label className="mb-2 block font-bold text-gray-700">Isim</label>
              <input
                type="text"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                className="w-full rounded-lg border border-gray-300 px-4 py-2"
                required
              />
            </div>
            <div>
              <label className="mb-2 block font-bold text-gray-700">Kullanici Adi</label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                className="w-full rounded-lg border border-gray-300 px-4 py-2"
                required
              />
            </div>
            <div>
              <label className="mb-2 block font-bold text-gray-700">Mail</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full rounded-lg border border-gray-300 px-4 py-2"
                required
              />
            </div>
            <div>
              <label className="mb-2 block font-bold text-gray-700">Statu</label>
              <select
                value={formData.role}
                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                className="w-full rounded-lg border border-gray-300 px-4 py-2"
              >
                <option value="user">Kullanici</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            <div className="md:col-span-2">
              <label className="mb-2 block font-bold text-gray-700">
                {editingUserId ? 'Yeni Sifre' : 'Sifre'}
              </label>
              <div className="flex flex-col gap-3 md:flex-row">
                <div className="relative flex-1">
                  <input
                    type={passwordVisible ? 'text' : 'password'}
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    className="w-full rounded-lg border border-gray-300 px-4 py-2 pr-12"
                    required={!editingUserId}
                  />
                  <button
                    type="button"
                    onClick={() => setPasswordVisible((current) => !current)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-sm font-bold text-gray-500 transition hover:text-gray-700"
                  >
                    {passwordVisible ? 'Gizle' : 'Goster'}
                  </button>
                </div>
                <button
                  type="button"
                  onClick={generatePassword}
                  className="rounded bg-indigo-500 px-4 py-2 font-bold text-white transition hover:bg-indigo-600"
                >
                  Oto Sifre Uret
                </button>
                <button
                  type="button"
                  onClick={copyPassword}
                  className="rounded bg-slate-500 px-4 py-2 font-bold text-white transition hover:bg-slate-600"
                >
                  Kopyala
                </button>
              </div>
            </div>
            <div className="md:col-span-2">
              <button
                type="submit"
                className="w-full rounded bg-green-500 px-4 py-2 font-bold text-white transition hover:bg-green-600"
              >
                Kaydet
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="rounded-lg bg-white p-6 shadow">
        <h2 className="mb-4 text-xl font-bold">Kullanicilar</h2>
        <div className="mb-4 grid grid-cols-1 gap-4 md:grid-cols-4">
          <div className="md:col-span-3">
            <label className="mb-2 block font-bold text-gray-700">Ara</label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Isim, kullanici adi, mail veya statu ile ara"
              className="w-full rounded-lg border border-gray-300 px-4 py-2"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={exportToExcel}
              className="w-full rounded bg-green-500 px-4 py-2 font-bold text-white transition hover:bg-green-600"
            >
              Export
            </button>
          </div>
        </div>
        {loading ? (
          <p className="text-center text-gray-500">Yukleniyor...</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-100">
                  <th className="cursor-pointer px-4 py-2 text-left" onClick={() => requestSort('full_name')}>
                    Isim {getSortArrow('full_name')}
                  </th>
                  <th className="cursor-pointer px-4 py-2 text-left" onClick={() => requestSort('username')}>
                    Kullanici Adi {getSortArrow('username')}
                  </th>
                  <th className="cursor-pointer px-4 py-2 text-left" onClick={() => requestSort('email')}>
                    Mail {getSortArrow('email')}
                  </th>
                  <th className="cursor-pointer px-4 py-2 text-left" onClick={() => requestSort('role')}>
                    Statu {getSortArrow('role')}
                  </th>
                  <th className="px-4 py-2 text-center">Duzenle</th>
                  <th className="px-4 py-2 text-center">Sil</th>
                </tr>
              </thead>
              <tbody>
                {processedUsers.map((user) => (
                  <tr key={user.id} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-2">{user.full_name || '-'}</td>
                    <td className="px-4 py-2">{user.username}</td>
                    <td className="px-4 py-2">{user.email}</td>
                    <td className="px-4 py-2">{user.role === 'admin' ? 'Admin' : 'Kullanici'}</td>
                    <td className="px-4 py-2 text-center">
                      <button
                        onClick={() => handleEdit(user)}
                        className="rounded bg-amber-500 px-3 py-1 text-sm font-bold text-white transition hover:bg-amber-600"
                      >
                        Duzenle
                      </button>
                    </td>
                    <td className="px-4 py-2 text-center">
                      <button
                        onClick={() => setConfirmDeleteUserId(user.id)}
                        className="rounded bg-red-500 px-3 py-1 text-sm font-bold text-white transition hover:bg-red-600"
                      >
                        Sil
                      </button>
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