import axios from "axios"

const envBaseURL = process.env.VUE_APP_API_URL
const apiBaseURL = envBaseURL && envBaseURL.trim() !== ''
  ? envBaseURL
  : (typeof window !== 'undefined' ? window.location.origin : '')

const TOKEN_STORAGE_KEY = 'auth_token'
const csrfSafeMethods = ['get', 'head', 'options', 'trace']

const apiClient = axios.create({
  baseURL: apiBaseURL,
  withCredentials: true,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
  timeout: 10000
})

const setAuthHeader = (token) => {
  if (token) {
    apiClient.defaults.headers.common.Authorization = `Token ${token}`
  } else {
    delete apiClient.defaults.headers.common.Authorization
  }
}

const persistToken = (token) => {
  try {
    if (token) {
      localStorage.setItem(TOKEN_STORAGE_KEY, token)
    } else {
      localStorage.removeItem(TOKEN_STORAGE_KEY)
    }
  } catch (error) {
    console.warn('Could not persist token', error)
  }
}

const bootstrapToken = () => {
  if (typeof window === 'undefined') return
  try {
    const saved = localStorage.getItem(TOKEN_STORAGE_KEY)
    if (saved) {
      setAuthHeader(saved)
    }
  } catch (error) {
    console.warn('Could not read token', error)
  }
}

bootstrapToken()

const getCsrfToken = () => {
  if (typeof document === 'undefined') {
    return ''
  }
  return document.cookie
    .split(';')
    .map((cookie) => cookie.trim())
    .find((cookie) => cookie.startsWith('csrftoken='))
    ?.split('=')[1]
    ?.trim()
}

apiClient.interceptors.request.use((config) => {
  const method = (config.method || 'get').toLowerCase()
  if (!csrfSafeMethods.includes(method)) {
    const csrf = getCsrfToken()
    if (csrf) {
      config.headers = config.headers || {}
      config.headers['X-CSRFToken'] = csrf
    }
  }
  return config
})

const normalizePage = (data) => {
  if (Array.isArray(data)) {
    return {
      results: data,
      count: data.length,
      next: null,
      previous: null
    }
  }
  return data || { results: [] }
}

const unwrap = (response) => response?.data

const handleAuthResponse = (response) => {
  const data = unwrap(response)
  const token = data?.token || data?.key
  if (token) {
    setAuthHeader(token)
    persistToken(token)
  }
  return data
}

export const clearAuth = () => {
  persistToken(null)
  setAuthHeader(null)
}

export const api = {
  client: apiClient,

  async fetchTeachers({ page = 1, pageSize = 12, search = '', tags = [], ordering } = {}) {
    const params = { page, page_size: pageSize }
    if (search && String(search).trim()) {
      params.q = String(search).trim()
    }
    if (Array.isArray(tags) && tags.length) {
      params.tags = tags.join(',')
    }
    if (ordering) {
      params.ordering = ordering
    }

    const { data } = await apiClient.get('/api/teachers/', { params })
    if (Array.isArray(data)) {
      return { results: data, count: data.length, next: null, previous: null }
    }
    return {
      results: data?.results || [],
      count: data?.count ?? (data?.results?.length || 0),
      next: data?.next || null,
      previous: data?.previous || null
    }
  },

  async fetchTeacher(id) {
    const { data } = await apiClient.get(`/api/teachers/${id}/`)
    return data
  },

  async fetchTags() {
    const { data } = await apiClient.get('/api/tags/')
    return Array.isArray(data) ? data : data?.results || []
  },

  async fetchReviews({ teacherIsu, page } = {}) {
    const params = {}
    if (teacherIsu) {
      params.teacher_isu = teacherIsu
    }
    if (page) {
      params.page = page
    }
    const { data } = await apiClient.get('/api/reviews/', { params })
    return normalizePage(data)
  },

  async createReview(payload) {
    const response = await apiClient.post('/api/reviews/', payload)
    return unwrap(response)
  },

  async updateReview(id, payload) {
    const response = await apiClient.put(`/api/reviews/${id}/`, payload)
    return unwrap(response)
  },

  async deleteReview(id) {
    const response = await apiClient.delete(`/api/reviews/${id}/`)
    return unwrap(response)
  },

  async login({ username, email, password }) {
    const payload = { username: username || email, password }
    const response = await apiClient.post('/accounts/login/', payload)
    return handleAuthResponse(response)
  },

  async logout() {
    const response = await apiClient.post('/accounts/logout/', {})
    persistToken(null)
    setAuthHeader(null)
    return unwrap(response)
  },

  async register({ username, password, password_confirm }) {
    const payload = {
      username,
      password,
      password_confirm: password_confirm || password
    }
    const response = await apiClient.post('/api/register/', payload)
    return handleAuthResponse(response)
  },

  async fetchProfile() {
    const response = await apiClient.get('/api/profile/')
    return unwrap(response)
  },

  async fetchAdminReviews() {
    const { data } = await apiClient.get('/api/admin/reviews/')
    return normalizePage(data).results || []
  },

  async deleteAdminReview(id) {
    const response = await apiClient.delete(`/api/admin/reviews/${id}/`)
    return unwrap(response)
  },

  async fetchAdminUsers() {
    const { data } = await apiClient.get('/api/admin/users/')
    return Array.isArray(data) ? data : []
  },

  async toggleAdminBan(userId) {
    const response = await apiClient.post(`/api/admin/users/${userId}/ban-toggle/`)
    return unwrap(response)
  }
}

export default api
