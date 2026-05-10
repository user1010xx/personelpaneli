const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api'

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL
    this.token = localStorage.getItem('access_token')
  }

  setToken(token) {
    this.token = token
    localStorage.setItem('access_token', token)
  }

  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    }
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
    }
    return headers
  }

  async get(endpoint) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'GET',
        headers: this.getHeaders(),
      })
      return await this.handleResponse(response)
    } catch (error) {
      throw new Error(`API Error: ${error.message}`)
    }
  }

  async post(endpoint, data) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(data),
      })
      return await this.handleResponse(response)
    } catch (error) {
      throw new Error(`API Error: ${error.message}`)
    }
  }

  async postFormData(endpoint, formData) {
    try {
      const headers = {}
      if (this.token) {
        headers['Authorization'] = `Bearer ${this.token}`
      }
      
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'POST',
        headers: headers,
        body: formData,
      })
      return await this.handleResponse(response)
    } catch (error) {
      throw new Error(`API Error: ${error.message}`)
    }
  }

  async put(endpoint, data) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'PUT',
        headers: this.getHeaders(),
        body: JSON.stringify(data),
      })
      return await this.handleResponse(response)
    } catch (error) {
      throw new Error(`API Error: ${error.message}`)
    }
  }

  async delete(endpoint) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'DELETE',
        headers: this.getHeaders(),
      })
      return await this.handleResponse(response)
    } catch (error) {
      throw new Error(`API Error: ${error.message}`)
    }
  }

  async handleResponse(response) {
    if (response.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    
    const data = await response.json()
    
    if (!response.ok) {
      throw new Error(data.detail || 'API Error')
    }
    
    return data
  }
}

export default new ApiClient()
