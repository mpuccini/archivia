<template>
  <div class="min-h-screen flex items-center justify-center" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
    <div class="max-w-md w-full px-4">
      <a-card class="shadow-2xl" style="border-radius: 16px;">
        <!-- Header -->
        <div class="text-center mb-8">
          <div class="mb-4">
            <span style="font-size: 64px;">🏛️</span>
          </div>
          <h1 class="text-3xl font-bold mb-2" style="color: #667eea;">
            Archivia
          </h1>
          <a-typography-text type="secondary">
            Sistema di Gestione Documentale METS ECO-MiC
          </a-typography-text>
        </div>

        <!-- Login Form -->
        <a-form
          :model="formState"
          @finish="handleLogin"
          layout="vertical"
        >
          <!-- Username Field -->
          <a-form-item
            label="Nome utente"
            name="username"
            :rules="[{ required: true, message: 'Inserisci il nome utente!' }]"
          >
            <a-input
              v-model:value="formState.username"
              placeholder="Inserisci il nome utente"
              size="large"
              :disabled="authStore.isLoading"
            >
              <template #prefix>
                <UserOutlined />
              </template>
            </a-input>
          </a-form-item>

          <!-- Password Field -->
          <a-form-item
            label="Password"
            name="password"
            :rules="[{ required: true, message: 'Inserisci la password!' }]"
          >
            <a-input-password
              v-model:value="formState.password"
              placeholder="Inserisci la password"
              size="large"
              :disabled="authStore.isLoading"
            >
              <template #prefix>
                <LockOutlined />
              </template>
            </a-input-password>
          </a-form-item>

          <!-- Error Message -->
          <a-alert
            v-if="authStore.error"
            :message="authStore.error"
            type="error"
            show-icon
            closable
            class="mb-4"
          />

          <!-- Submit Button -->
          <a-form-item>
            <a-button
              type="primary"
              html-type="submit"
              :loading="authStore.isLoading"
              size="large"
              block
              style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; height: 48px; font-size: 16px; font-weight: 600;"
            >
              {{ authStore.isLoading ? 'Accesso in corso...' : 'Accedi' }}
            </a-button>
          </a-form-item>
        </a-form>

        <!-- Admin Info -->
        <a-divider />
        <div class="text-center">
          <a-typography-text type="secondary" style="font-size: 12px;">
            Contatta l'amministratore per richiedere l'accesso
          </a-typography-text>
        </div>
      </a-card>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    const formState = reactive({
      username: '',
      password: ''
    })

    onMounted(async () => {
      await authStore.init()
      if (authStore.isAuthenticated) {
        router.push('/dashboard')
      }
    })

    const handleLogin = async () => {
      const success = await authStore.login(formState.username, formState.password)
      if (success) {
        router.push('/dashboard')
      }
    }

    return {
      formState,
      authStore,
      handleLogin,
      UserOutlined,
      LockOutlined
    }
  }
}
</script>
