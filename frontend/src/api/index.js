import apiClient from './client'

const buildQuery = (params = {}) => {
  const cleanParams = Object.fromEntries(
    Object.entries(params).filter(([, value]) => value !== undefined && value !== null && value !== '')
  )
  const query = new URLSearchParams(cleanParams).toString()
  return query ? `?${query}` : ''
}

const withLimit = (params = {}) => ({ limit: 1000, ...params })

// Auth API
export const authApi = {
  register: (data) => apiClient.post('/auth/register', data),
  login: (credentials) => apiClient.post('/auth/login', credentials),
  getCurrentUser: () => apiClient.get('/auth/me'),
  logout: (refreshToken) => apiClient.post('/auth/logout', { refresh_token: refreshToken }),
}

// Users API
export const usersApi = {
  list: (params = {}) => apiClient.get(`/users${buildQuery(withLimit(params))}`),
  create: (data) => apiClient.post('/users', data),
  update: (id, data) => apiClient.put(`/users/${id}`, data),
  delete: (id) => apiClient.delete(`/users/${id}`),
}

export const docsLinksApi = {
  list: () => apiClient.get('/docs-links'),
  update: (key, data) => apiClient.put(`/docs-links/${key}`, data),
}

export const dashboardApi = {
  summary: (startDate, endDate) =>
    apiClient.get(`/dashboard/summary?start_date=${startDate}&end_date=${endDate}`),
}

// Personnel API
export const personnelApi = {
  list: (params = {}) => apiClient.get(`/personnel${buildQuery(withLimit(params))}`),
  get: (id) => apiClient.get(`/personnel/${id}`),
  create: (data) => apiClient.post('/personnel', data),
  update: (id, data) => apiClient.put(`/personnel/${id}`, data),
  delete: (id) => apiClient.delete(`/personnel/${id}`),
  syncDocs: () => apiClient.post('/personnel/sync-docs', {}),
}

// Sales API
export const salesApi = {
  list: (params) => {
    return apiClient.get(`/sales${buildQuery(withLimit(params))}`)
  },
  getSummary: (personnelId, startDate, endDate) =>
    apiClient.get(`/sales/personnel/${personnelId}/summary?start_date=${startDate}&end_date=${endDate}`),
  getAllSummary: (startDate, endDate) =>
    apiClient.get(`/sales/summary?start_date=${startDate}&end_date=${endDate}`),
  uploadExcel: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.postFormData('/sales/upload-excel', formData)
  },
  create: (data) => apiClient.post('/sales', data),
  update: (id, data) => apiClient.put(`/sales/${id}`, data),
}

// Attendance API
export const attendanceApi = {
  list: (params) => {
    return apiClient.get(`/attendance${buildQuery(withLimit(params))}`)
  },
  get: (personnelId, month, year) =>
    apiClient.get(`/attendance/${personnelId}/${month}/${year}`),
  create: (data) => apiClient.post('/attendance', data),
  update: (id, data) => apiClient.put(`/attendance/${id}`, data),
  delete: (id) => apiClient.delete(`/attendance/${id}`),
  syncDocs: () => apiClient.post('/attendance/sync-docs', {}),
}

// Warnings API
export const warningsApi = {
  list: (params) => {
    return apiClient.get(`/warnings${buildQuery(withLimit(params))}`)
  },
  getPersonnelWarnings: (personnelId) =>
    apiClient.get(`/warnings/personnel/${personnelId}`),
  getPersonnelSummary: (personnelId) =>
    apiClient.get(`/warnings/personnel/${personnelId}/summary`),
  create: (data) => apiClient.post('/warnings', data),
  update: (id, data) => apiClient.put(`/warnings/${id}`, data),
  delete: (id) => apiClient.delete(`/warnings/${id}`),
  syncDocs: () => apiClient.post('/warnings/sync-docs', {}),
}

// Training API
export const trainingApi = {
  list: (params) => {
    return apiClient.get(`/training${buildQuery(withLimit(params))}`)
  },
  getPersonnelTraining: (personnelId) =>
    apiClient.get(`/training/personnel/${personnelId}`),
  create: (data) => apiClient.post('/training', data),
  update: (id, data) => apiClient.put(`/training/${id}`, data),
  delete: (id) => apiClient.delete(`/training/${id}`),
}

// Call Monitoring API
export const callMonitoringApi = {
  list: (params) => {
    return apiClient.get(`/call-monitoring${buildQuery(withLimit(params))}`)
  },
  getPersonnelCalls: (personnelId) =>
    apiClient.get(`/call-monitoring/personnel/${personnelId}`),
  getPersonnelSummary: (personnelId) =>
    apiClient.get(`/call-monitoring/personnel/${personnelId}/summary`),
  create: (data) => apiClient.post('/call-monitoring', data),
  update: (id, data) => apiClient.put(`/call-monitoring/${id}`, data),
  delete: (id) => apiClient.delete(`/call-monitoring/${id}`),
}

// WhatsApp API
export const whatsappApi = {
  list: (params) => {
    return apiClient.get(`/whatsapp${buildQuery(withLimit(params))}`)
  },
  getPersonnelData: (personnelId, params) =>
    apiClient.get(`/whatsapp/personnel/${personnelId}${buildQuery(params)}`),
  getPersonnelSummary: (personnelId) =>
    apiClient.get(`/whatsapp/personnel/${personnelId}/summary`),
  create: (data) => apiClient.post('/whatsapp', data),
  update: (id, data) => apiClient.put(`/whatsapp/${id}`, data),
  delete: (id) => apiClient.delete(`/whatsapp/${id}`),
  syncDocs: () => apiClient.post('/whatsapp/sync-docs', {}),
}

export const callProcessApi = {
  list: (params) => {
    return apiClient.get(`/call-process${buildQuery(withLimit(params))}`)
  },
  getSummary: (startDate, endDate) =>
    apiClient.get(`/call-process/summary?start_date=${startDate}&end_date=${endDate}`),
  uploadExcel: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.postFormData('/call-process/upload-excel', formData)
  },
  create: (data) => apiClient.post('/call-process', data),
  update: (id, data) => apiClient.put(`/call-process/${id}`, data),
}
