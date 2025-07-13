import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = 'http://localhost:8000'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: null,
    isLoading: false,
    error: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token
  },

  actions: {
    async login(username, password) {
      this.isLoading = true
      this.error = null

      try {
        const response = await axios.post(`${API_URL}/auth/login`, {
          username,
          password
        })

        this.token = response.data.access_token
        if (typeof window !== 'undefined' && window.localStorage) {
          localStorage.setItem('token', this.token)
        }
        
        // Set axios default header
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        
        // Get user info
        await this.fetchUser()
        
        return true
      } catch (error) {
        this.error = error.response?.data?.detail || 'Login failed'
        return false
      } finally {
        this.isLoading = false
      }
    },

    async register(username, password) {
      this.isLoading = true
      this.error = null

      try {
        await axios.post(`${API_URL}/auth/register`, {
          username,
          password
        })
        
        // Auto-login after successful registration
        return await this.login(username, password)
      } catch (error) {
        this.error = error.response?.data?.detail || 'Registration failed'
        return false
      } finally {
        this.isLoading = false
      }
    },

    async fetchUser() {
      if (!this.token) return

      try {
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        const response = await axios.get(`${API_URL}/auth/me`)
        this.user = response.data
      } catch (error) {
        console.error('Failed to fetch user:', error)
        this.logout()
      }
    },

    logout() {
      this.user = null
      this.token = null
      if (typeof window !== 'undefined' && window.localStorage) {
        localStorage.removeItem('token')
      }
      delete axios.defaults.headers.common['Authorization']
    },

    async init() {
      // Safely get token from localStorage
      if (typeof window !== 'undefined' && window.localStorage) {
        this.token = localStorage.getItem('token')
      }
      
      if (this.token) {
        await this.fetchUser()
      }
    }
  }
})
