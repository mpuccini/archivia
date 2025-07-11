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
  background: linear-gradient(135deg, var(--primary-lighter) 0%, var(--bg-secondary) 100%);
  padding: var(--spacing-lg);
}

.login-form {
  background: var(--bg-primary);
  padding: var(--spacing-2xl);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  border: 1px solid var(--border-primary);
  min-width: 400px;
  max-width: 500px;
  width: 100%;
}

h1, h2 {
  text-align: center;
  color: var(--text-primary);
  margin-bottom: var(--spacing-xl);
  font-weight: 600;
}

h1 {
  font-size: var(--text-2xl);
  color: var(--primary-dark);
}

h2 {
  font-size: var(--text-xl);
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-xl);
  border-top: 1px solid var(--border-primary);
}

.form-group {
  margin-bottom: var(--spacing-lg);
}

label {
  display: block;
  margin-bottom: var(--spacing-sm);
  color: var(--text-secondary);
  font-weight: 500;
  font-size: var(--text-sm);
}

input {
  width: 100%;
  padding: var(--spacing-md);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  font-family: var(--font-sans);
}

input:focus {
  outline: none;
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px rgba(50, 169, 195, 0.1);
}

button {
  width: 100%;
  padding: var(--spacing-md);
  background-color: var(--primary-color);
  color: var(--text-inverse);
  border: 1px solid var(--primary-color);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: var(--font-sans);
}

button:hover:not(:disabled) {
  background-color: var(--primary-dark);
  border-color: var(--primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.error {
  background-color: #FEE2E2;
  color: #991B1B;
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-lg);
  border: 1px solid #FECACA;
  font-size: var(--text-sm);
}

.register-link {
  text-align: center;
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--border-primary);
}

.register-link p {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.register-link a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  transition: color var(--transition-fast);
}

.register-link a:hover {
  color: var(--primary-dark);
  text-decoration: underline;
}

.register-form {
  margin-top: var(--spacing-xl);
}

@media (max-width: 480px) {
  .login-form {
    min-width: auto;
    padding: var(--spacing-xl);
  }
}
</style>
