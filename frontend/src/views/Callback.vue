<template>
  <main class="container">
    <div class="panel single" style="text-align:center; padding: 40px 0;">
      <h2>Anmeldung wird verarbeitet…</h2>
      <p class="hint">Bitte warten, du wirst gleich weitergeleitet.</p>
    </div>
  </main>
  
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth0 } from '@auth0/auth0-vue'

const router = useRouter()
const { handleRedirectCallback, isAuthenticated } = useAuth0()

onMounted(async () => {
  try {
    const result = await handleRedirectCallback()
    const target = result?.appState?.targetUrl || '/tool'
    await router.replace(target)
  } catch (e) {
    // If already authenticated or callback already processed, go to tool or home
    router.replace(isAuthenticated ? '/tool' : '/')
  }
})
</script>

<style scoped>
.hint { color: #9bb0da; }
</style>
