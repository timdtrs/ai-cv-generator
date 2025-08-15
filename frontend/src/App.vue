<template>
  <div class="container">
    <header class="appbar">
      <h1>CV Generator</h1>
      <nav class="tabs">
        <button :class="{active: tab==='generate'}" @click="tab='generate'">Erstellen</button>
        <button :class="{active: tab==='template'}" @click="tab='template'">Template</button>
      </nav>
    </header>

    <div v-if="tab==='generate'" class="layout">
      <section class="panel left">
        <label for="notes">Deine Stichpunkte</label>
        <textarea id="notes" class="notes" v-model="notes" placeholder="Beschreibe deinen Werdegang, Skills, Stationen, Projekte, Ausbildung, Kenntnisse ..."></textarea>
        <div class="actions">
          <button class="secondary" @click="loadExample" type="button">Beispiel einfügen</button>
          <button class="primary" :disabled="busy || !notes.trim()" @click="onCreateCv">Lebenslauf erstellen</button>
        </div>

        <div v-if="error" class="error">{{ error }}</div>

        <div class="edit-block">
          <label for="edit">Änderungswunsch (natürliche Sprache)</label>
          <textarea id="edit" v-model="changeInstruction" placeholder="z. B.: Füge eine neue Station bei ACME GmbH (2024–heute) hinzu und liste 2 Bulletpoints zu Cloud-Projekten."></textarea>
          <div class="actions">
            <button :disabled="busy || !latex.trim() || !changeInstruction.trim()" @click="onApplyEdit">Änderung anwenden</button>
            <a v-if="pdfUrl" class="secondary" :href="pdfUrl" download="cv.pdf">PDF herunterladen</a>
          </div>
        </div>
      </section>

      <section class="panel right">
        <div class="preview-header">
          <h3>PDF Vorschau</h3>
          <span v-if="busy" class="spinner">Rendern…</span>
        </div>
        <div class="preview">
          <div v-if="!pdfUrl" class="placeholder">Noch keine Vorschau. Klicke „Lebenslauf erstellen“.</div>
          <iframe v-else class="pdf-frame" :src="pdfUrl"></iframe>
        </div>
      </section>
    </div>

    <section v-else class="panel single">
      <h3>LaTeX-Template</h3>
      <textarea v-model="template" class="latex"></textarea>
      <div class="actions">
        <button class="primary" :disabled="busy || !template.trim()" @click="saveTemplate">Template speichern</button>
      </div>
      <div v-if="tmplInfo" class="info">{{ tmplInfo }}</div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { getTemplate, updateTemplate, generateLatex, renderPdf, editLatex } from './api'

const tab = ref('generate')
const notes = ref('')
const template = ref('')
const latex = ref('')
const pdfUrl = ref('')
const error = ref('')
const busy = ref(false)
const tmplInfo = ref('')
const changeInstruction = ref('')

onMounted(async () => {
  try {
    const data = await getTemplate()
    template.value = data.template || ''
  } catch (e) {
    // ignore if not found on first run
  }
})

function clearPdfUrl() {
  if (pdfUrl.value) URL.revokeObjectURL(pdfUrl.value)
  pdfUrl.value = ''
}

onBeforeUnmount(() => clearPdfUrl())

async function onRender() {
  error.value = ''
  clearPdfUrl()
  busy.value = true
  try {
    const resp = await renderPdf(latex.value)
    const blob = new Blob([resp.data], { type: 'application/pdf' })
    pdfUrl.value = URL.createObjectURL(blob)
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message
  } finally {
    busy.value = false
  }
}

async function onApplyEdit() {
  error.value = ''
  busy.value = true
  try {
    const data = await editLatex(latex.value, changeInstruction.value)
    latex.value = data.latex
    changeInstruction.value = ''
    await onRender()
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message
  } finally {
    busy.value = false
  }
}

async function onCreateCv() {
  // One-click: generate full LaTeX (no placeholders), then render to PDF
  error.value = ''
  clearPdfUrl()
  busy.value = true
  try {
    const data = await generateLatex(notes.value)
    latex.value = data.latex || ''
    if (latex.value.trim()) {
      const resp = await renderPdf(latex.value)
      const blob = new Blob([resp.data], { type: 'application/pdf' })
      pdfUrl.value = URL.createObjectURL(blob)
    } else {
      throw new Error('Kein LaTeX erzeugt.')
    }
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message
  } finally {
    busy.value = false
  }
}

async function onGeneratePdf() {
  error.value = ''
  clearPdfUrl()
  busy.value = true
  try {
    const resp = await generatePdf(notes.value)
    const blob = new Blob([resp.data], { type: 'application/pdf' })
    pdfUrl.value = URL.createObjectURL(blob)
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message
  } finally {
    busy.value = false
  }
}

async function saveTemplate() {
  error.value = ''
  tmplInfo.value = ''
  busy.value = true
  try {
    await updateTemplate(template.value)
    tmplInfo.value = 'Template gespeichert.'
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message
  } finally {
    busy.value = false
    setTimeout(() => (tmplInfo.value = ''), 2000)
  }
}

const exampleNotes = `Profil:\nFull-Stack Softwareentwickler mit 5+ Jahren Erfahrung in Web-, API- und Cloud-Entwicklung. Fokus auf sauberen Code, Tests und DevOps-Automatisierung.\n\nBerufserfahrung:\n2022–heute — Senior Software Engineer, ACME GmbH, Berlin\n- Architektur und Entwicklung einer Microservices-Plattform (FastAPI, Python)\n- CI/CD mit GitHub Actions, Docker, Kubernetes; Deployment in AWS\n- Performance-Optimierung (-40% Latenz), Observability (Prometheus, Grafana)\n\n2019–2022 — Software Engineer, Beta AG, München\n- Entwicklung eines Vue.js Frontends und Node.js Backends\n- Einführung automatisierter Tests (Jest, Pytest) und Code-Reviews\n- Zusammenarbeit mit UX für zugängliche Komponenten\n\nProjekte:\nCV-Generator — Vue 3, FastAPI, Tectonic: Automatische LaTeX-Erzeugung und PDF-Render\nEvent-Streaming — Datenpipeline mit Kafka, Faust, PostgreSQL\n\nAusbildung:\nM.Sc. Informatik, TU München, 2017–2019 (Schwerpunkt: Maschinelles Lernen)\nB.Sc. Informatik, HS Augsburg, 2014–2017\n\nKenntnisse:\nProgrammiersprachen: Python, TypeScript, SQL, Go (Grundlagen)\nFrameworks: FastAPI, Vue 3, Node.js, Flask\nDevOps: Docker, Kubernetes, Terraform, GitHub Actions\nDaten: PostgreSQL, Redis, Kafka, Elasticsearch\nMethoden: TDD, Clean Architecture, Domain-Driven Design\n\nZertifikate:\nAWS Solutions Architect Associate (2023)\n\nSprachen:\nDeutsch (C2), Englisch (C1)\n\nEngagement:\nMentor in Open-Source-Projekten, Konferenzvorträge zu API-Design`;

function loadExample() {
  notes.value = exampleNotes;
}
</script>

<style>
:root { font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji"; }
* { box-sizing: border-box; }
body { margin: 0; background: #0b1020; color: #e9eef6; }
.container { max-width: 1200px; margin: 0 auto; padding: 20px; }
.appbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
h1 { margin: 0; font-size: 22px; font-weight: 700; color: #e9eef6; }
.tabs { display: flex; gap: 8px; }
.tabs button { padding: 8px 12px; border: 1px solid #2a3657; background: #121a33; color: #c9d6f2; cursor: pointer; border-radius: 8px; }
.tabs button.active { background: #2a6ef2; color: #fff; border-color: #2a6ef2; }

.layout { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 16px; align-items: start; }
.panel { background: #0f1630; border: 1px solid #1c2646; border-radius: 12px; padding: 14px; }
.panel.single { max-width: 920px; margin: 0 auto; }
.panel h3 { margin-top: 4px; }

label { display: block; margin: 8px 0; font-weight: 600; color: #c9d6f2; }
textarea { width: 100%; min-height: 140px; padding: 10px 12px; border: 1px solid #273359; background: #0b122a; color: #e9eef6; border-radius: 10px; outline: none; resize: vertical; font-size: 14px; line-height: 1.35; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }
.latex { min-height: 260px; }
.notes { min-height: 420px; }
.actions { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0; }
button, a.button, .tabs button, .actions a { padding: 10px 14px; border: 1px solid #2a3657; background: #121a33; color: #c9d6f2; cursor: pointer; border-radius: 10px; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; }
button.primary, .actions .primary { background: linear-gradient(180deg, #2a6ef2 0%, #265ed6 100%); border-color: #2a6ef2; color: #fff; }
button.secondary, .actions .secondary { background: #121a33; }
button:disabled { opacity: 0.6; cursor: not-allowed; }
.error { color: #ff6b6b; margin-top: 8px; }
.info { color: #29d98c; margin-top: 8px; }
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
