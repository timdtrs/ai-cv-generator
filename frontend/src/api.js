import axios from 'axios'

// In container, nginx proxies /api to backend
const api = axios.create({ baseURL: '/api' })

// Attach Auth0 access token to every API request (if available)
api.interceptors.request.use(async (config) => {
  try {
    const getter = window.__getAccessToken
    if (typeof getter === 'function') {
      const token = await getter()
      if (token) {
        config.headers = config.headers || {}
        config.headers.Authorization = `Bearer ${token}`
      }
    }
  } catch (e) {
    // Ignore token errors; backend will return 401
  }
  return config
})

export const getTemplate = () => api.get('/template').then(r => r.data)
export const updateTemplate = (template) => api.put('/template', { template }).then(r => r.data)
export const generateLatex = (inputText, templateId = null, templateOverride = null) => api.post('/generate', {
  input_text: inputText,
  ...(templateId ? { template_id: templateId } : {}),
  ...(templateOverride ? { template_override: templateOverride } : {}),
}).then(r => r.data)
export const renderPdf = (latex) => api.post('/render', { latex }, { responseType: 'blob' })
export const generatePdf = (inputText, templateId = null) => api.post('/generate-pdf', {
  input_text: inputText,
  ...(templateId ? { template_id: templateId } : {}),
}, { responseType: 'blob' })
export const editLatex = (latex, instruction) => api.post('/edit', { latex, instruction }).then(r => r.data)
export const importFromLinkedIn = (url, templateId = null, templateOverride = null) => api.post('/import/linkedin', {
  url,
  ...(templateId ? { template_id: templateId } : {}),
  ...(templateOverride ? { template_override: templateOverride } : {}),
}).then(r => r.data)
// Note: structured generation removed; always generate full LaTeX

export default api
