<template>
  <a-layout class="min-h-screen bg-gray-50">
    <a-layout-header style="background: white; padding: 0; height: auto; line-height: normal;">
      <div class="flex justify-between items-center h-16 px-6 border-b border-gray-200">
        <!-- Brand -->
        <div class="flex items-center">
          <span class="text-2xl mr-3">🏛️</span>
          <h1 class="text-xl font-semibold mb-0">Archivia</h1>
        </div>
        <!-- Navbar Tabs -->
        <a-menu
          mode="horizontal"
          :selected-keys="[$route.path]"
          class="flex-1 mx-8 border-0"
          style="background: transparent; line-height: 64px;"
        >
          <a-menu-item key="/dashboard">
            <router-link to="/dashboard">Dashboard</router-link>
          </a-menu-item>
          <a-menu-item key="/guide">
            <router-link to="/guide">Guida</router-link>
          </a-menu-item>
        </a-menu>
        <!-- User info and actions -->
        <div class="flex items-center space-x-4">
          <a-typography-text>
            Ciao, <strong>{{ authStore.user?.username }}</strong>!
          </a-typography-text>
          <a-button
            type="primary"
            danger
            @click="handleLogout"
          >
            Esci
          </a-button>
        </div>
      </div>
    </a-layout-header>
    <a-layout-content style="padding: 24px; max-width: 900px; margin: 0 auto; width: 100%;">
      <a-card title="Guida all'uso di Archivia">
        <a-typography>
          <a-typography-title :level="2">Benvenuto in Archivia</a-typography-title>
          <a-typography-paragraph>
            Archivia è un sistema di gestione documentale progettato per l'archiviazione e la catalogazione di documenti digitali secondo lo standard METS ECO-MiC 1.1.
          </a-typography-paragraph>

          <a-typography-title :level="3">Funzionalità principali</a-typography-title>

          <a-typography-title :level="4">1. Gestione Documenti</a-typography-title>
          <a-typography-paragraph>
            <ul>
              <li><strong>Creazione singola:</strong> Utilizza il pulsante "Nuovo Documento" per creare un documento con metadati completi</li>
              <li><strong>Import batch da Excel:</strong> Importa più documenti contemporaneamente da un file Excel</li>
              <li><strong>Modifica:</strong> Clicca su un documento per modificarne i metadati</li>
              <li><strong>Eliminazione:</strong> Seleziona uno o più documenti ed elimina con il pulsante "Elimina Selezionati"</li>
            </ul>
          </a-typography-paragraph>

          <a-typography-title :level="4">2. Caricamento File</a-typography-title>
          <a-typography-paragraph>
            <ul>
              <li><strong>Upload singolo:</strong> Carica un'immagine per un documento specifico</li>
              <li><strong>Upload batch:</strong> Carica più immagini che verranno associate automaticamente ai documenti per logical_id</li>
              <li><strong>Upload cartella ZIP:</strong> Carica una cartella compressa con struttura ECO-MiC (master, normalized, export_high, etc.)</li>
            </ul>
          </a-typography-paragraph>

          <a-typography-title :level="4">3. Formati Supportati</a-typography-title>
          <a-typography-paragraph>
            <ul>
              <li><strong>Immagini:</strong> JPEG, PNG, TIFF</li>
              <li><strong>RAW:</strong> DNG (Adobe Digital Negative) fino a 80GB</li>
              <li><strong>Documenti:</strong> PDF</li>
            </ul>
          </a-typography-paragraph>

          <a-typography-title :level="4">4. Export METS</a-typography-title>
          <a-typography-paragraph>
            <ul>
              <li><strong>Export singolo:</strong> Esporta il METS XML di un singolo documento (con validazione ECO-MiC 1.1)</li>
              <li><strong>Export metadati CSV:</strong> Esporta i metadati di uno o più documenti in formato CSV</li>
            </ul>
          </a-typography-paragraph>

          <a-typography-title :level="4">5. Standard METS ECO-MiC 1.1</a-typography-title>
          <a-typography-paragraph>
            Il sistema genera automaticamente file METS conformi allo standard ECO-MiC 1.1 dell'ICCU (Istituto Centrale per il Catalogo Unico).
            La validazione viene eseguita tramite il servizio ufficiale prima dell'export.
          </a-typography-paragraph>

          <a-divider />

          <a-typography-paragraph type="secondary">
            <strong>Nota:</strong> Per maggiori informazioni sullo standard METS ECO-MiC, consulta la documentazione ufficiale ICCU.
          </a-typography-paragraph>
        </a-typography>
      </a-card>
    </a-layout-content>
  </a-layout>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'Guide',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const handleLogout = () => {
      authStore.logout()
      router.push('/login')
    }

    return { authStore, handleLogout }
  }
}
</script>

<style scoped>
.ant-layout-header {
  height: 64px;
  line-height: 64px;
}
</style>
