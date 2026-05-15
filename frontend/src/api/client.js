const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export class ApiError extends Error {
  constructor(message, status = null, payload = null) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.payload = payload
  }
}

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL
    this.authStore = null
    this.refreshPromise = null
  }

  setAuthStore(store) {
    this.authStore = store
  }

  getToken() {
    return this.authStore?.getAccessToken?.() || null
  }

  getRefreshToken() {
    return this.authStore?.getRefreshToken?.() || null
  }

  setSession(session) {
    this.authStore?.setSession?.(session)
  }

  async clearSession() {
    const refreshToken = this.getRefreshToken()
    const accessToken = this.getToken()
    if (refreshToken) {
      try {
        await fetch(`${this.baseURL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
          },
          body: JSON.stringify({ refresh_token: refreshToken }),
        })
      } catch {}
    }
    this.authStore?.clearSession?.()
  }

  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    }
    const token = this.getToken()
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    return headers
  }

  async get(endpoint) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'GET',
        headers: this.getHeaders(),
      })
      return await this.handleResponse(response, { method: 'GET', endpoint })
    } catch (error) {
      throw this.normalizeError(error)
    }
  }

  async post(endpoint, data) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(data),
      })
      return await this.handleResponse(response, { method: 'POST', endpoint, data })
    } catch (error) {
      throw this.normalizeError(error)
    }
  }

  async postFormData(endpoint, formData) {
    try {
      const headers = {}
      const token = this.getToken()
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
      
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'POST',
        headers: headers,
        body: formData,
      })
      return await this.handleResponse(response, { method: 'POST_FORM_DATA', endpoint, formData })
    } catch (error) {
      throw this.normalizeError(error)
    }
  }

  async put(endpoint, data) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'PUT',
        headers: this.getHeaders(),
        body: JSON.stringify(data),
      })
      return await this.handleResponse(response, { method: 'PUT', endpoint, data })
    } catch (error) {
      throw this.normalizeError(error)
    }
  }

  async delete(endpoint) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'DELETE',
        headers: this.getHeaders(),
      })
      return await this.handleResponse(response, { method: 'DELETE', endpoint })
    } catch (error) {
      throw this.normalizeError(error)
    }
  }

  normalizeError(error) {
    if (error instanceof ApiError) {
      return error
    }
    return new ApiError(error.message || 'API istegi tamamlanamadi.')
  }

  async handleResponse(response, requestConfig = null) {
    let data = null
    try {
      data = await response.json()
    } catch {
      data = null
    }

    if (response.status === 401) {
      const canRefresh = requestConfig && !requestConfig._retried && requestConfig.endpoint !== '/auth/refresh' && requestConfig.endpoint !== '/auth/login'
      if (canRefresh) {
        const refreshed = await this.refreshSession()
        if (refreshed) {
          return this.retryRequest({ ...requestConfig, _retried: true })
        }
      }
      await this.clearSession()
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
      throw new ApiError('Oturum sureniz doldu. Lutfen tekrar giris yapin.', response.status, data)
    }
    
    if (!response.ok) {
      if (response.status === 403) {
        throw new ApiError('Bu islem icin yetkiniz yok.', response.status, data)
      }
      if (response.status >= 500) {
        throw new ApiError(data?.request_id ? `Sunucu hatasi olustu. Request ID: ${data.request_id}` : 'Sunucu hatasi olustu. Lutfen tekrar deneyin.', response.status, data)
      }
      throw new ApiError(data?.detail || 'Islem tamamlanamadi.', response.status, data)
    }
    
    return data
  }

  async retryRequest(requestConfig) {
    const options = {
      method: requestConfig.method === 'POST_FORM_DATA' ? 'POST' : requestConfig.method,
      headers: requestConfig.method === 'POST_FORM_DATA' ? this.getMultipartHeaders() : this.getHeaders(),
    }
    if (requestConfig.method === 'POST_FORM_DATA') {
      options.body = requestConfig.formData
    } else if (['POST', 'PUT'].includes(requestConfig.method)) {
      options.body = JSON.stringify(requestConfig.data)
    }
    const response = await fetch(`${this.baseURL}${requestConfig.endpoint}`, options)
    return this.handleResponse(response, requestConfig)
  }

  getMultipartHeaders() {
    const headers = {}
    const token = this.getToken()
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }
    return headers
  }

  async refreshSession() {
    if (this.refreshPromise) {
      return this.refreshPromise
    }

    const refreshToken = this.getRefreshToken()
    if (!refreshToken) {
      return false
    }

    this.refreshPromise = (async () => {
      try {
        const response = await fetch(`${this.baseURL}/auth/refresh`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ refresh_token: refreshToken }),
        })

        if (!response.ok) {
          return false
        }

        const data = await response.json()
        this.setSession({ accessToken: data.access_token, refreshToken: data.refresh_token })
        return true
      } catch {
        return false
      } finally {
        this.refreshPromise = null
      }
    })()

    return this.refreshPromise
  }
}

const apiClient = new ApiClient()
export default apiClient
