<template>
  <div class="login-container">
    <div class="login-form">
      <h1>Archivia Login</h1>
      
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">Username:</label>
          <input
            id="username"
            v-model="username"
            type="text"
            required
            :disabled="authStore.isLoading"
          />
        </div>
        
        <div class="form-group">
          <label for="password">Password:</label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            :disabled="authStore.isLoading"
          />
        </div>
        
        <div v-if="authStore.error" class="error">
          {{ authStore.error }}
        </div>
        
        <button type="submit" :disabled="authStore.isLoading">
          {{ authStore.isLoading ? 'Logging in...' : 'Login' }}
        </button>
      </form>
      
      <div class="register-link">
        <p>Don't have an account? <a href="#" @click.prevent="showRegister = !showRegister">Register here</a></p>
      </div>
      
      <div v-if="showRegister" class="register-form">
        <h2>Register</h2>
        <form @submit.prevent="handleRegister">
          <div class="form-group">
            <label for="reg-username">Username:</label>
            <input
              id="reg-username"
              v-model="regUsername"
              type="text"
              required
              :disabled="authStore.isLoading"
            />
          </div>
          
          <div class="form-group">
            <label for="reg-password">Password:</label>
            <input
              id="reg-password"
              v-model="regPassword"
              type="password"
              required
              :disabled="authStore.isLoading"
            />
          </div>
          
          <button type="submit" :disabled="authStore.isLoading">
            {{ authStore.isLoading ? 'Registering...' : 'Register' }}
          </button>
        </form>
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

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f0f0;
}

.login-form {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  min-width: 300px;
}

h1, h2 {
  text-align: center;
  color: #333;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-weight: 500;
}

input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

input:focus {
  outline: none;
  border-color: #007bff;
}

button {
  width: 100%;
  padding: 0.75rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

button:hover:not(:disabled) {
  background-color: #0056b3;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.error {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.register-link {
  text-align: center;
  margin-top: 1rem;
}

.register-link a {
  color: #007bff;
  text-decoration: none;
}

.register-link a:hover {
  text-decoration: underline;
}

.register-form {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #eee;
}
</style>
