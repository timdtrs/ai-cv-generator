// Define available templates and preview images.
// Ensure matching .tex files exist in the backend templates directory with the same id.

export const templates = [
  {
    id: 'cv_template',
    name: 'Klassisch',
    preview: new URL('./assets/templates/classic.svg', import.meta.url).href,
  },
  {
    id: 'modern',
    name: 'Modern',
    preview: new URL('./assets/templates/modern.svg', import.meta.url).href,
  },
  {
    id: 'minimal',
    name: 'Minimal',
    preview: new URL('./assets/templates/minimal.svg', import.meta.url).href,
  },
]

