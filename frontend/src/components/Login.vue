<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-blue-50 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- Card Container -->
      <div class="bg-white rounded-xl shadow-lg border border-gray-100 p-8">
        <!-- Header -->
        <div class="text-center">
          <h1 class="text-3xl font-bold text-gray-900 mb-2">
            Archivia Login
          </h1>
          <p class="text-sm text-gray-600">
            Sign in to access your documents
          </p>
        </div>

        <!-- Login Form -->
        <form @submit.prevent="handleLogin" class="mt-8 space-y-6">
          <div class="space-y-4">
            <!-- Username Field -->
            <div>
              <label for="username" class="block text-sm font-medium text-gray-700 mb-1">
                Username
              </label>
              <input
                id="username"
                v-model="username"
                type="text"
                required
                :disabled="authStore.isLoading"
                class="block w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors disabled:bg-gray-50 disabled:text-gray-500"
                placeholder="Enter your username"
              />
            </div>

            <!-- Password Field -->
            <div>
              <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                id="password"
                v-model="password"
                type="password"
                required
                :disabled="authStore.isLoading"
                class="block w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors disabled:bg-gray-50 disabled:text-gray-500"
                placeholder="Enter your password"
              />
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="authStore.error" class="bg-red-50 border border-red-200 rounded-lg p-3">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm text-red-800">{{ authStore.error }}</p>
              </div>
            </div>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="authStore.isLoading"
            class="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <svg v-if="authStore.isLoading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ authStore.isLoading ? 'Signing in...' : 'Sign in' }}
          </button>
        </form>

        <!-- Register Section -->
        <div class="mt-6 pt-6 border-t border-gray-200">
          <div class="text-center">
            <p class="text-sm text-gray-600">
              Don't have an account?
              <button
                @click="showRegister = !showRegister"
                class="font-medium text-blue-600 hover:text-blue-500 transition-colors"
              >
                {{ showRegister ? 'Hide registration' : 'Register here' }}
              </button>
            </p>
          </div>

          <!-- Registration Form -->
          <div v-if="showRegister" class="mt-6 pt-6 border-t border-gray-200">
            <h2 class="text-xl font-semibold text-gray-900 text-center mb-4">
              Create Account
            </h2>
            
            <form @submit.prevent="handleRegister" class="space-y-4">
              <!-- Registration Username -->
              <div>
                <label for="reg-username" class="block text-sm font-medium text-gray-700 mb-1">
                  Choose Username
                </label>
                <input
                  id="reg-username"
                  v-model="regUsername"
                  type="text"
                  required
                  :disabled="authStore.isLoading"
                  class="block w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors disabled:bg-gray-50 disabled:text-gray-500"
                  placeholder="Choose your username"
                />
              </div>

              <!-- Registration Password -->
              <div>
                <label for="reg-password" class="block text-sm font-medium text-gray-700 mb-1">
                  Choose Password
                </label>
                <input
                  id="reg-password"
                  v-model="regPassword"
                  type="password"
                  required
                  :disabled="authStore.isLoading"
                  class="block w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors disabled:bg-gray-50 disabled:text-gray-500"
                  placeholder="Choose your password"
                />
              </div>

              <!-- Register Button -->
              <button
                type="submit"
                :disabled="authStore.isLoading"
                class="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <svg v-if="authStore.isLoading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ authStore.isLoading ? 'Creating account...' : 'Create account' }}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const username = ref('')
    const password = ref('')
    const regUsername = ref('')
    const regPassword = ref('')
    const showRegister = ref(false)
    
    onMounted(async () => {
      await authStore.init()
      if (authStore.isAuthenticated) {
        router.push('/dashboard')
      }
    })
    
    const handleLogin = async () => {
      const success = await authStore.login(username.value, password.value)
      if (success) {
        router.push('/dashboard')
      }
    }
    
    const handleRegister = async () => {
      const success = await authStore.register(regUsername.value, regPassword.value)
      if (success) {
        router.push('/dashboard')
      }
    }
    
    return {
      username,
      password,
      regUsername,
      regPassword,
      showRegister,
      authStore,
      handleLogin,
      handleRegister
    }
  }
}
</script>
