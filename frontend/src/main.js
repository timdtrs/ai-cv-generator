import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index.js'
import { createAuth0 } from '@auth0/auth0-vue'
import './assets/tailwind.css'

const app = createApp(App)

// Install router first to ensure navigation is ready
app.use(router)

// Read Auth0 settings from Vite env (provided at build time)
const domain = import.meta.env.VITE_AUTH0_DOMAIN
const clientId = import.meta.env.VITE_AUTH0_CLIENT_ID
const audience = import.meta.env.VITE_AUTH0_AUDIENCE

app.use(
  createAuth0({
    domain,
    clientId,
    authorizationParams: {
      redirect_uri: window.location.origin + '/callback',
      ...(audience ? { audience } : {}),
    },
    cacheLocation: 'localstorage',
    useRefreshTokens: true,
    onRedirectCallback: (appState) => {
      const target = appState?.targetUrl || '/tool'
      router.push(target)
    },
  })
)

// Expose a token getter early so axios can attach Authorization headers
try {
  const auth0 = app.config.globalProperties?.$auth0
  if (auth0) {
    window.__getAccessToken = async () => {
      try {
        return audience
          ? await auth0.getAccessTokenSilently({ audience })
          : await auth0.getAccessTokenSilently()
      } catch (e) {
        return null
      }
    }
  }
} catch (_) { /* noop */ }

app.mount('#app')
