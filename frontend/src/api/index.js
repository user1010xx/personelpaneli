import apiClient from './client'

// Auth API
export const authApi = {
  register: (data) => apiClient.post('/auth/register', data),
  login: (credentials) => apiClient.post('/auth/login', credentials),
  getCurrentUser: () => apiClient.get('/auth/me'),
}

// Users API
export const usersApi = {
  list: () => apiClient.get('/users'),
  create: (data) => apiClient.post('/users', data),
  update: (id, data) => apiClient.put(`/users/${id}`, data),
  delete: (id) => apiClient.delete(`/users/${id}`),
}

// Personnel API
export const personnelApi = {
  list: () => apiClient.get('/personnel'),
  get: (id) => apiClient.get(`/personnel/${id}`),
  create: (data) => apiClient.post('/personnel', data),
  update: (id, data) => apiClient.put(`/personnel/${id}`, data),
  delete: (id) => apiClient.delete(`/personnel/${id}`),
}

// Sales API
export const salesApi = {
  list: (params) => {
    const query = new URLSearchParams(params).toString()
    return apiClient.get(`/sales?${query}`)
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
    const query = new URLSearchParams(params).toString()
    return apiClient.get(`/attendance?${query}`)
  },
  get: (personnelId, month, year) =>
    apiClient.get(`/attendance/${personnelId}/${month}/${year}`),
  create: (data) => apiClient.post('/attendance', data),
  update: (id, data) => apiClient.put(`/attendance/${id}`, data),
  delete: (id) => apiClient.delete(`/attendance/${id}`),
}

// Warnings API
export const warningsApi = {
  list: (params) => {
    const query = new URLSearchParams(params).toString()
    return apiClient.get(`/warnings?${query}`)
  },
  getPersonnelWarnings: (personnelId) =>
    apiClient.get(`/warnings/personnel/${personnelId}`),
  getPersonnelSummary: (personnelId) =>
    apiClient.get(`/warnings/personnel/${personnelId}/summary`),
  create: (data) => apiClient.post('/warnings', data),
  update: (id, data) => apiClient.put(`/warnings/${id}`, data),
  delete: (id) => apiClient.delete(`/warnings/${id}`),
}

// Training API
export const trainingApi = {
  list: (params) => {
    const query = new URLSearchParams(params).toString()
    return apiClient.get(`/training?${query}`)
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
    const query = new URLSearchParams(params).toString()
    return apiClient.get(`/call-monitoring?${query}`)
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
    const query = new URLSearchParams(params).toString()
    return apiClient.get(`/whatsapp?${query}`)
  },
  getPersonnelData: (personnelId) =>
    apiClient.get(`/whatsapp/personnel/${personnelId}`),
  getPersonnelSummary: (personnelId) =>
    apiClient.get(`/whatsapp/personnel/${personnelId}/summary`),
  create: (data) => apiClient.post('/whatsapp', data),
  update: (id, data) => apiClient.put(`/whatsapp/${id}`, data),
  delete: (id) => apiClient.delete(`/whatsapp/${id}`),
}
