import React, { useEffect, useMemo, useState } from 'react'
import { dashboardApi } from '../api'
import { formatLocalDate } from '../utils/date'
import { exportRowsToExcel } from '../utils/exportExcel'

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

const leaderCards = [
  {
    key: 'membership',
    title: 'Haftanın Üyelik Lideri',
    valueKey: 'membership_count',
    valueLabel: 'üye',
    color: 'from-emerald-500 to-teal-600',
  },
  {
    key: 'call_score',
    title: 'Haftanın Çağrı Puanı Lideri',
    valueKey: 'average_call_score',
    valueLabel: 'puan',
    color: 'from-blue-500 to-indigo-600',
  },
  {
    key: 'talk_duration',
    title: 'Haftanın Konuşma Süresi Lideri',
    valueKey: 'average_talk_duration_display',
    valueLabel: '',
    color: 'from-violet-500 to-purple-600',
  },
  {
    key: 'call_count',
    title: 'Haftanın Arama Adedi Lideri',
    valueKey: 'average_call_count',
    valueLabel: 'arama',
    color: 'from-orange-500 to-amber-600',
  },
  {
    key: 'whatsapp_unanswered',
    title: 'Haftanın Whatsapp Cevapsız Lideri',
    valueKey: 'average_whatsapp_unanswered',
    valueLabel: 'cevapsız',
    color: 'from-rose-500 to-red-600',
  },
]

export default function Dashboard() {
  const defaults = getDefaultRange()
  const [summary, setSummary] = useState(null)
  const [startDate, setStartDate] = useState(defaults.startDate)
  const [endDate, setEndDate] = useState(defaults.endDate)
  const [searchTerm, setSearchTerm] = useState('')
  const [sortConfig, setSortConfig] = useState({ key: 'personnel_name', direction: 'asc' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    loadDashboard()
  }, [startDate, endDate])

  const loadDashboard = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await dashboardApi.summary(startDate, endDate)
      setSummary(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const rows = useMemo(() => {
    const sourceRows = summary?.rows || []
    return [...sourceRows]
      .filter((row) => {
        const haystack = [
          row.personnel_name,
          row.membership_count,
          row.average_call_count,
          row.average_talk_duration_display,
          row.average_call_score,
          row.average_whatsapp_unanswered,
        ].join(' ').toLocaleLowerCase('tr')
        return haystack.includes(searchTerm.toLocaleLowerCase('tr'))
      })
      .sort((first, second) => {
        const textKeys = ['personnel_name', 'average_talk_duration_display']
        let comparison = 0
        if (textKeys.includes(sortConfig.key)) {
          comparison = String(first[sortConfig.key] || '').localeCompare(
            String(second[sortConfig.key] || ''),
            'tr',
            { sensitivity: 'base' }
          )
        } else {
          comparison = Number(first[sortConfig.key] || 0) - Number(second[sortConfig.key] || 0)
        }
        return sortConfig.direction === 'asc' ? comparison : -comparison
      })
  }, [searchTerm, sortConfig, summary])

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

  const renderLeaderValue = (leader, card) => {
    const value = leader?.[card.valueKey]
    if (value === undefined || value === null || value === '') return '-'
    return `${value}${card.valueLabel ? ` ${card.valueLabel}` : ''}`
  }

  const exportToExcel = () => {
    exportRowsToExcel(
      rows.map((row) => ({
        'Personel Adı': row.personnel_name,
        'Üye Adedi': row.membership_count,
        'Ortalama Arama Adedi': row.average_call_count,
        'Ortalama Konuşma Süresi': row.average_talk_duration_display,
        'Ortalama Çağrı Puanı': row.average_call_score,
        'Ortalama Whatsapp Cevapsız Adedi': row.average_whatsapp_unanswered,
      })),
      'Dashboard',
      'dashboard'
    )
  }

  return (
    <div className="p-8">
      <div className="mb-8 overflow-hidden rounded-[28px] border border-white/50 bg-gradient-to-br from-slate-950 via-blue-950 to-cyan-900 p-8 text-white shadow-2xl">
        <div className="flex flex-col justify-between gap-6 lg:flex-row lg:items-end">
          <div>
            <p className="mb-3 text-sm font-black uppercase tracking-[0.28em] text-cyan-200">Performans Merkezi</p>
            <h1 className="text-4xl font-black tracking-tight lg:text-5xl">Dashboard</h1>
            <p className="mt-3 max-w-2xl text-white/70">
              Seçilen tarih aralığına göre liderler ve personel performans özetleri
            </p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/10 px-5 py-4 backdrop-blur">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-cyan-100">Aktif Aralık</p>
            <p className="mt-1 text-lg font-black">{startDate} / {endDate}</p>
          </div>
        </div>
      </div>

      {error && (
        <div className="mb-4 rounded border border-red-400 bg-red-100 px-4 py-3 text-red-700">
          {error}
        </div>
      )}

      <div className="mb-8 rounded-2xl bg-white p-6 shadow">
        <h2 className="mb-4 text-xl font-bold">Tarih Filtreleme</h2>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div>
            <label className="mb-2 block font-bold text-gray-700">Başlangıç Tarihi</label>
            <input
              type="date"
              value={startDate}
              onChange={(event) => setStartDate(event.target.value)}
              className="w-full rounded-lg border border-gray-300 px-4 py-2"
            />
          </div>
          <div>
            <label className="mb-2 block font-bold text-gray-700">Bitiş Tarihi</label>
            <input
              type="date"
              value={endDate}
              onChange={(event) => setEndDate(event.target.value)}
              className="w-full rounded-lg border border-gray-300 px-4 py-2"
            />
          </div>
          <div>
            <label className="mb-2 block font-bold text-gray-700">Ara</label>
            <input
              type="text"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Personel veya değer ara"
              className="w-full rounded-lg border border-gray-300 px-4 py-2"
            />
          </div>
        </div>
        <button
          onClick={exportToExcel}
          className="mt-4 rounded bg-green-500 px-5 py-2 font-bold text-white transition hover:bg-green-600"
        >
          Export
        </button>
      </div>

      <div className="mb-8 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-5">
        {leaderCards.map((card) => (
          <div key={card.key} className={`rounded-2xl bg-gradient-to-br ${card.color} p-5 text-white shadow-lg`}>
            <h3 className="mb-4 text-sm font-bold uppercase tracking-wide">{card.title}</h3>
            <div className="space-y-3">
              {(summary?.leaders?.[card.key] || []).map((leader, index) => (
                <div key={`${card.key}-${leader.personnel_id}`} className="rounded-xl bg-white/15 p-3 backdrop-blur">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-bold">{index + 1}. {leader.personnel_name}</span>
                    <span className="text-sm font-semibold">{renderLeaderValue(leader, card)}</span>
                  </div>
                </div>
              ))}
              {(!summary?.leaders?.[card.key] || summary.leaders[card.key].length === 0) && (
                <div className="rounded-xl bg-white/15 p-3 text-sm">Seçilen aralıkta veri yok</div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="rounded-2xl bg-white p-6 shadow">
        <h2 className="mb-4 text-xl font-bold">Personel Performans Tablosu</h2>
        {loading ? (
          <p className="py-8 text-center text-gray-500">Yükleniyor...</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-100">
                  <th className="cursor-pointer px-4 py-3 text-left" onClick={() => requestSort('personnel_name')}>
                    Personel Adı {getSortArrow('personnel_name')}
                  </th>
                  <th className="cursor-pointer px-4 py-3 text-center" onClick={() => requestSort('membership_count')}>
                    Üye Adedi {getSortArrow('membership_count')}
                  </th>
                  <th className="cursor-pointer px-4 py-3 text-center" onClick={() => requestSort('average_call_count')}>
                    Ortalama Arama Adedi {getSortArrow('average_call_count')}
                  </th>
                  <th className="cursor-pointer px-4 py-3 text-center" onClick={() => requestSort('average_talk_duration')}>
                    Ortalama Konuşma Süresi {getSortArrow('average_talk_duration')}
                  </th>
                  <th className="cursor-pointer px-4 py-3 text-center" onClick={() => requestSort('average_call_score')}>
                    Ortalama Çağrı Puanı {getSortArrow('average_call_score')}
                  </th>
                  <th className="cursor-pointer px-4 py-3 text-center" onClick={() => requestSort('average_whatsapp_unanswered')}>
                    Ortalama Whatsapp Cevapsız Adedi {getSortArrow('average_whatsapp_unanswered')}
                  </th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={row.personnel_id} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-3 font-semibold">{row.personnel_name}</td>
                    <td className="px-4 py-3 text-center">{row.membership_count}</td>
                    <td className="px-4 py-3 text-center">{row.average_call_count}</td>
                    <td className="px-4 py-3 text-center">{row.average_talk_duration_display}</td>
                    <td className="px-4 py-3 text-center">{row.average_call_score}</td>
                    <td className="px-4 py-3 text-center">{row.average_whatsapp_unanswered}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {rows.length === 0 && (
              <p className="py-8 text-center text-gray-500">Seçilen aralıkta veri bulunamadı</p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}