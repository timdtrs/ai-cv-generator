import axios from 'axios'

// In container, nginx proxies /api to backend
const api = axios.create({
  baseURL: '/api',
})

export const getTemplate = () => api.get('/template').then(r => r.data)
export const updateTemplate = (template) => api.put('/template', { template }).then(r => r.data)
export const generateLatex = (inputText, templateOverride = null) => api.post('/generate', {
  input_text: inputText,
  template_override: templateOverride,
}).then(r => r.data)
export const renderPdf = (latex) => api.post('/render', { latex }, { responseType: 'blob' })
export const generatePdf = (inputText) => api.post('/generate-pdf', { input_text: inputText }, { responseType: 'blob' })
export const editLatex = (latex, instruction) => api.post('/edit', { latex, instruction }).then(r => r.data)
// Note: structured generation removed; always generate full LaTeX

export default api
