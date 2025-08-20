<template>
  <div>
    <RouterView />
  </div>
  
  <!-- Floating background accents for a modern feel -->
  <div class="bg-accent bg-accent-a" aria-hidden="true"></div>
  <div class="bg-accent bg-accent-b" aria-hidden="true"></div>
</template>

<script setup>
// Router wird in main.js eingebunden; hier nur die View-Hülle
import { onMounted, onBeforeUnmount } from 'vue'
import { useAuth0 } from '@auth0/auth0-vue'

const { getAccessTokenSilently } = useAuth0()
const audience = import.meta.env.VITE_AUTH0_AUDIENCE

onMounted(() => {
  // Expose a token getter for axios interceptor
  window.__getAccessToken = async () => {
    try {
      if (audience) {
        return await getAccessTokenSilently({ audience })
      }
      return await getAccessTokenSilently()
    } catch (e) {
      return null
    }
  }
})

onBeforeUnmount(() => {
  delete window.__getAccessToken
})
</script>

<style>
:root { font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji"; }
* { box-sizing: border-box; }
body { margin: 0; background: #0b1020; color: #e9eef6; }
.container { max-width: 1200px; margin: 0 auto; padding: 20px; }

/* Base buttons */
button, a.button { padding: 10px 14px; border: 1px solid #2a3657; background: #121a33; color: #c9d6f2; cursor: pointer; border-radius: 10px; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; transition: transform 0.15s ease, box-shadow 0.2s ease; }
button.primary, a.button.primary { background: linear-gradient(180deg, #2a6ef2 0%, #265ed6 100%); border-color: #2a6ef2; color: #fff; }
button.secondary, a.button.secondary { background: #121a33; }
button:hover:not(:disabled), a.button:hover { transform: translateY(-1px); box-shadow: 0 8px 24px rgba(42, 110, 242, 0.25); }
button:active:not(:disabled), a.button:active { transform: translateY(0); box-shadow: 0 4px 12px rgba(42, 110, 242, 0.18); }
button:disabled { opacity: 0.6; cursor: not-allowed; }

/* Floating background accents */
.bg-accent { position: fixed; inset: auto; pointer-events: none; filter: blur(60px); opacity: 0.3; z-index: -1; }
.bg-accent-a { width: 40vw; height: 40vw; left: -10vw; top: -10vw; background: radial-gradient(closest-side, #2a6ef2, transparent 70%); animation: float 14s ease-in-out infinite; }
.bg-accent-b { width: 40vw; height: 40vw; right: -10vw; bottom: -10vw; background: radial-gradient(closest-side, #29d98c, transparent 70%); animation: float 18s ease-in-out infinite reverse; }
@keyframes float { 0% { transform: translateY(0) } 50% { transform: translateY(20px) } 100% { transform: translateY(0) } }

/* Moved stray global styles back inside a style block */
.latex-block { margin-top: 16px; }
.download { margin-top: 12px; }

.preview-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.spinner { color: #9eb5ff; font-size: 13px; }
.preview { background: #0b122a; border: 1px solid #273359; border-radius: 10px; min-height: 320px; display: grid; }
.pdf-frame { width: 100%; height: 70vh; min-height: 480px; border: none; border-radius: 10px; }
.placeholder { color: #7f8db7; display: grid; place-items: center; min-height: 200px; }

.edit-block { margin-top: 16px; }

/* Responsive adjustments */
@media (max-width: 1100px) {
  .layout { grid-template-columns: 1fr; }
  .notes { min-height: 360px; }
  .pdf-frame { height: 60vh; min-height: 360px; }
  .placeholder { min-height: 160px; }
}

@media (max-width: 720px) {
  .container { padding: 12px; }
  .appbar { flex-direction: column; gap: 8px; align-items: flex-start; }
  .tabs { flex-wrap: wrap; }
  textarea { font-size: 13px; }
  .notes { min-height: 300px; }
  .pdf-frame { height: 55vh; min-height: 280px; }
}
</style>
