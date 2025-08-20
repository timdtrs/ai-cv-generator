<template>
  <div class="container">
    <header class="appbar">
      <h1 class="brand" @click="goHome" role="button" tabindex="0" aria-label="Zur Startseite">CV Generator</h1>
      <div>
        <button class="secondary" @click="logoutUser">Abmelden</button>
      </div>
    </header>

    <section class="panel single">
      <div class="stepper" role="tablist" aria-label="CV Wizard">
        <div :class="['step', {active: step===1, done: step>1}]" role="tab" aria-selected="step===1">1. Template</div>
        <div :class="['step', {active: step===2, done: step>2}]" role="tab" aria-selected="step===2">2. Start</div>
        <div :class="['step', {active: step===3, done: step>3}]" role="tab" aria-selected="step===3">3. Stationen</div>
        <div :class="['step', {active: step===4}]" role="tab" aria-selected="step===4">4. Vorschau & Edit</div>
      </div>

      <transition name="fade-slide" mode="out-in">
        <!-- Schritt 1: Template Auswahl -->
        <div v-if="step===1" key="step1" class="form-grid">
          <div class="field full">
            <label class="mode-label">Template auswählen</label>
            <div class="templates">
              <button v-for="t in availableTemplates" :key="t.id"
                :class="['template-card', { selected: selectedTemplateId===t.id }]"
                @click="selectedTemplateId=t.id"
                :aria-pressed="selectedTemplateId===t.id">
                <img :src="t.preview" :alt="t.name + ' Vorschau'" />
                <div class="template-name">{{ t.name }}</div>
              </button>
            </div>
            <div class="actions">
              <button class="primary" @click="step=2">Weiter</button>
            </div>
          </div>
        </div>

        <!-- Schritt 2: Start (Auswahl Manuell vs. LinkedIn) + Persönliche Informationen bei Manuell -->
        <div v-else-if="step===2" key="step2" class="form-grid">
          <div class="mode">
            <label class="mode-label">Wie möchtest du starten?</label>
            <div class="mode-buttons">
              <button :class="['toggle', {active: mode==='manual'}]" @click="mode='manual'">Manuell eingeben</button>
              <button :class="['toggle', {active: mode==='linkedin'}]" @click="mode='linkedin'">Aus LinkedIn importieren</button>
            </div>
          </div>

          <!-- LinkedIn Import -->
          <template v-if="mode==='linkedin'">
            <div class="field full">
              <label for="li-url">LinkedIn Profil-URL</label>
              <input id="li-url" type="url" v-model="linkedInUrl" placeholder="https://www.linkedin.com/in/dein-profil" />
              <div class="hint">Hinweis: Das LinkedIn-Profil muss öffentlich sein. Login-geschützte Profile können nicht importiert werden.</div>
            </div>
            <div class="actions">
              <button @click="step=1">Zurück</button>
              <button class="primary" :disabled="busy || !isLinkedInUrl" @click="onImportLinkedIn">Importieren und anzeigen</button>
            </div>
            <div v-if="error" class="error" role="alert">{{ error }}</div>
          </template>

          <!-- Manuelle Eingabe -->
          <template v-else>
          <div class="field">
            <label>Vorname</label>
            <input v-model="personal.firstName" placeholder="Max" />
          </div>
          <div class="field">
            <label>Nachname</label>
            <input v-model="personal.lastName" placeholder="Mustermann" />
          </div>
          <div class="field">
            <label>Jobtitel/Headline</label>
            <input v-model="personal.headline" placeholder="Senior Software Engineer" />
          </div>
          <div class="field">
            <label>Ort</label>
            <input v-model="personal.location" placeholder="Berlin, Deutschland" />
          </div>
          <div class="field">
            <label>E-Mail</label>
            <input v-model="personal.email" type="email" placeholder="max@example.com" />
          </div>
          <div class="field">
            <label>Telefon</label>
            <input v-model="personal.phone" placeholder="+49 170 1234567" />
          </div>
          <div class="field full">
            <label>Zusammenfassung</label>
            <textarea v-model="personal.summary" placeholder="Kurzprofil, Stärken, Fokus, Erfolge ..."></textarea>
          </div>

            <div class="actions">
              <button @click="step=1">Zurück</button>
              <button class="secondary" @click="fillExample">Beispiel ausfüllen</button>
              <button class="primary" :disabled="!validStep1" @click="step=3">Weiter</button>
            </div>
          </template>
        </div>

        <!-- Schritt 3: Ausbildung, Erfahrung, Projekte, Zertifikate & Kenntnisse -->
        <div v-else-if="step===3" key="step3">
          <h3>Bildung</h3>
          <div v-for="(e,i) in education" :key="'edu'+i" class="group">
            <div class="group-header">
              <span class="badge">#{{ i+1 }}</span>
              <span>Bildung</span>
              <button class="btn-remove" aria-label="Bildung entfernen" @click="removeEducation(i)">✕ Entfernen</button>
            </div>
            <div class="group-body row">
              <input v-model="e.degree" placeholder="Abschluss (z.B. M.Sc. Informatik)" />
              <input v-model="e.institution" placeholder="Institution" />
              <input v-model="e.years" placeholder="Jahre (z.B. 2017–2019)" />
            </div>
          </div>
          <div class="actions">
            <button class="btn-add" @click="addEducation">＋ Bildung hinzufügen</button>
          </div>

          <h3>Berufserfahrung</h3>
          <div v-for="(x,i) in experience" :key="'exp'+i" class="group">
            <div class="group-header">
              <span class="badge">#{{ i+1 }}</span>
              <span>Erfahrung</span>
              <button class="btn-remove" aria-label="Erfahrung entfernen" @click="removeExperience(i)">✕ Entfernen</button>
            </div>
            <div class="group-body row">
              <input v-model="x.role" placeholder="Rolle (z.B. Senior Engineer)" />
              <input v-model="x.company" placeholder="Firma (z.B. ACME GmbH)" />
              <input v-model="x.location" placeholder="Ort" />
              <input v-model="x.years" placeholder="Zeitraum (z.B. 2022–heute)" />
              <textarea v-model="x.bullets" placeholder="Bulletpoints, jeweils in neuer Zeile"></textarea>
            </div>
          </div>
          <div class="actions">
            <button class="btn-add" @click="addExperience">＋ Erfahrung hinzufügen</button>
          </div>

          <h3>Eigene Projekte (optional)</h3>
          <div v-for="(p,i) in projects" :key="'prj'+i" class="group">
            <div class="group-header">
              <span class="badge">#{{ i+1 }}</span>
              <span>Projekt</span>
              <button class="btn-remove" aria-label="Projekt entfernen" @click="removeProject(i)">✕ Entfernen</button>
            </div>
            <div class="group-body row">
              <input v-model="p.name" placeholder="Projektname" />
              <textarea v-model="p.desc" placeholder="Kurzbeschreibung / Tech-Stack"></textarea>
            </div>
          </div>
          <div class="actions">
            <button class="btn-add" @click="addProject">＋ Projekt hinzufügen</button>
          </div>

          <h3>Zertifikate & Kenntnisse (optional)</h3>
          <div class="group">
            <div class="group-body row">
              <textarea v-model="certs" placeholder="Zertifikate, jeweils eigene Zeile"></textarea>
              <textarea v-model="skills" placeholder="Kenntnisse/Skills, z.B. Programmiersprachen, Frameworks, Tools"></textarea>
            </div>
          </div>

          <div class="actions">
            <button @click="step=2">Zurück</button>
            <button class="primary" :disabled="busy || !validStep2" @click="generateFromForm">Lebenslauf erzeugen</button>
          </div>
        </div>

        <!-- Schritt 4: Vorschau & Edit -->
        <div v-else key="step4">
          <div class="preview-header">
            <h3>PDF Vorschau</h3>
            <span v-if="busy" class="spinner" aria-live="polite">
              <i class="dot dot-a"></i><i class="dot dot-b"></i><i class="dot dot-c"></i>
              Rendern…
            </span>
          </div>
          <div v-if="isLoadingPreview" class="loading-screen">
            <div class="loading-inner">
              <div class="loader big"></div>
              <div class="loading-text">
                {{ loadingStage === 'render' ? 'PDF wird gerendert …' : 'LaTeX wird generiert …' }}
              </div>
              <div class="progress">
                <div class="bar"></div>
              </div>
              <div class="icons" aria-hidden="true">
                <span class="ico ico-a">📄</span>
                <span class="ico ico-b">⚙️</span>
                <span class="ico ico-c">🧠</span>
              </div>
              <div class="skeleton" role="img" aria-label="Vorschau-Platzhalter">
                <div class="sk-line w60"></div>
                <div class="sk-line w40"></div>
                <div class="sk-grid">
                  <div class="sk-col">
                    <div class="sk-line"></div>
                    <div class="sk-line w80"></div>
                    <div class="sk-line w70"></div>
                  </div>
                  <div class="sk-col">
                    <div class="sk-line w70"></div>
                    <div class="sk-line w50"></div>
                    <div class="sk-line w90"></div>
                  </div>
                </div>
              </div>
              <div class="tips">Bitte etwas Geduld — das kann je nach Umfang einige Sekunden dauern.</div>
            </div>
          </div>
          <div v-else class="preview">
            <iframe class="pdf-frame" :src="pdfUrl" title="PDF Vorschau"></iframe>
            <div v-if="busy" class="overlay"><div class="loader"></div></div>
          </div>

          <div class="edit-block">
            <label for="edit">Änderungswunsch (natürliche Sprache)</label>
            <textarea id="edit" v-model="changeInstruction" placeholder="z. B.: Füge eine neue Station bei ACME GmbH (2024–heute) hinzu und liste 2 Bulletpoints zu Cloud-Projekten."></textarea>
            <div class="actions">
              <button :disabled="busy || !latex.trim() || !changeInstruction.trim()" @click="onApplyEdit">Änderung anwenden</button>
              <a v-if="pdfUrl" class="button download-btn" :href="pdfUrl" download="cv.pdf">⬇︎ PDF herunterladen</a>
            </div>
          </div>

          <div v-if="error" class="error" role="alert">{{ error }}</div>

          <div class="actions">
            <button @click="step=3">Zurück</button>
          </div>
        </div>
      </transition>
    </section>
  </div>
  
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { getTemplate, generateLatex, renderPdf, editLatex, importFromLinkedIn } from '../api'
import { templates } from '../templates'
import { useAuth0 } from '@auth0/auth0-vue'

const router = useRouter()
const { logout } = useAuth0()
const step = ref(1)
const busy = ref(false)
const error = ref('')
const pdfUrl = ref('')
const latex = ref('')
const changeInstruction = ref('')
const mode = ref('manual')
const linkedInUrl = ref('')
const isLinkedInUrl = computed(() => /linkedin\.com/i.test(linkedInUrl.value) && /^(https?:\/\/)/i.test(linkedInUrl.value))
const loadingStage = ref('idle') // 'idle' | 'generate' | 'render'
const isLoadingPreview = computed(() => step.value === 4 && busy.value && !pdfUrl.value)

// Templates selection
const availableTemplates = ref(templates)
const selectedTemplateId = ref('cv_template')

// Template preloading for backend; no direct editing in wizard
onMounted(async () => {
  try { await getTemplate() } catch (e) { /* ignore */ }
})

function goHome() { router.push('/') }
const logoutUser = () => logout({ logoutParams: { returnTo: window.location.origin } })
function clearPdfUrl() { if (pdfUrl.value) URL.revokeObjectURL(pdfUrl.value); pdfUrl.value = '' }
onBeforeUnmount(() => clearPdfUrl())

// Schritt 1: persönliche Daten
const personal = reactive({
  firstName: '', lastName: '', headline: '', location: '', email: '', phone: '', summary: ''
})
const validStep1 = computed(() => personal.firstName.trim() && personal.lastName.trim() && (personal.email.trim() || personal.phone.trim()))

// Schritt 2: Details
const education = ref([{ degree: '', institution: '', years: '' }])
const experience = ref([{ role: '', company: '', location: '', years: '', bullets: '' }])
const projects = ref([])
const certs = ref('')
const skills = ref('')
const validStep2 = computed(() => experience.value.some(x => x.role.trim() || x.company.trim()))

function addEducation(){ education.value.push({ degree: '', institution: '', years: '' }) }
function removeEducation(i){ education.value.splice(i,1) }
function addExperience(){ experience.value.push({ role: '', company: '', location: '', years: '', bullets: '' }) }
function removeExperience(i){ experience.value.splice(i,1) }
function addProject(){ projects.value.push({ name: '', desc: '' }) }
function removeProject(i){ projects.value.splice(i,1) }

function buildNotesFromForm(){
  const lines = []
  lines.push('Profil:')
  const name = `${personal.firstName} ${personal.lastName}`.trim()
  if (name) lines.push(`${name} — ${personal.headline || ''}`.trim())
  if (personal.location) lines.push(`Ort: ${personal.location}`)
  if (personal.email || personal.phone) lines.push(`Kontakt: ${[personal.email, personal.phone].filter(Boolean).join(' | ')}`)
  if (personal.summary) { lines.push('Zusammenfassung:'); lines.push(personal.summary.trim()) }

  if (experience.value.length){
    lines.push('\nBerufserfahrung:')
    experience.value.forEach(x => {
      if (!(x.role || x.company || x.years)) return
      lines.push(`${x.years || ''} — ${[x.role, x.company, x.location].filter(Boolean).join(', ')}`.trim())
      const bullets = (x.bullets || '').split('\n').map(b=>b.trim()).filter(Boolean)
      bullets.forEach(b => lines.push(`- ${b}`))
    })
  }

  if (projects.value.length){
    lines.push('\nProjekte:')
    projects.value.forEach(p => { if (p.name || p.desc) lines.push(`${p.name} — ${p.desc}`.trim()) })
  }

  if (education.value.length){
    lines.push('\nAusbildung:')
    education.value.forEach(e => { if (e.degree || e.institution || e.years) lines.push(`${e.degree}, ${e.institution}, ${e.years}`.trim()) })
  }

  if (certs.value.trim()){
    lines.push('\nZertifikate:')
    certs.value.split('\n').map(s=>s.trim()).filter(Boolean).forEach(s=>lines.push(s))
  }

  if (skills.value.trim()){
    lines.push('\nKenntnisse:')
    lines.push(skills.value.trim())
  }
  return lines.join('\n')
}

async function generateFromForm(){
  error.value = ''
  busy.value = true
  clearPdfUrl()
  try {
    // Wechsel direkt zu Schritt 4, damit der Ladebildschirm sichtbar ist
    step.value = 4
    loadingStage.value = 'generate'
    const notes = buildNotesFromForm()
    const data = await generateLatex(notes, selectedTemplateId.value)
    latex.value = data.latex || ''
    if (!latex.value.trim()) throw new Error('Kein LaTeX erzeugt.')
    loadingStage.value = 'render'
    const resp = await renderPdf(latex.value)
    const blob = new Blob([resp.data], { type: 'application/pdf' })
    pdfUrl.value = URL.createObjectURL(blob)
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message
  } finally {
    busy.value = false
    loadingStage.value = 'idle'
  }
}

async function onApplyEdit(){
  error.value = ''
  busy.value = true
  try {
    const data = await editLatex(latex.value, changeInstruction.value)
    latex.value = data.latex
    changeInstruction.value = ''
    const resp = await renderPdf(latex.value)
    const blob = new Blob([resp.data], { type: 'application/pdf' })
    pdfUrl.value = URL.createObjectURL(blob)
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message
  } finally {
    busy.value = false
  }
}

async function onImportLinkedIn(){
  error.value = ''
  busy.value = true
  clearPdfUrl()
  try {
    // Direkt zu Schritt 4 für Ladebildschirm
    step.value = 4
    loadingStage.value = 'generate'
    const data = await importFromLinkedIn(linkedInUrl.value, selectedTemplateId.value)
    latex.value = data.latex || ''
    if (!latex.value.trim()) throw new Error('Kein LaTeX erzeugt.')
    loadingStage.value = 'render'
    const resp = await renderPdf(latex.value)
    const blob = new Blob([resp.data], { type: 'application/pdf' })
    pdfUrl.value = URL.createObjectURL(blob)
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message
  } finally {
    busy.value = false
    loadingStage.value = 'idle'
  }
}

function fillExample(){
  personal.firstName = 'Max'; personal.lastName = 'Mustermann'; personal.headline = 'Senior Software Engineer';
  personal.location = 'Berlin, Deutschland'; personal.email = 'max@example.com'; personal.phone = '+49 170 1234567'
  personal.summary = 'Full-Stack Entwickler mit Fokus auf sauberen Code, Tests und Cloud. Leidenschaft für Developer Experience und Automatisierung.'
  education.value = [{ degree: 'M.Sc. Informatik', institution: 'TU München', years: '2017–2019' }]
  experience.value = [{ role: 'Senior Software Engineer', company: 'ACME GmbH', location: 'Berlin', years: '2022–heute', bullets: 'Architektur Microservices (FastAPI, Python)\nCI/CD mit GitHub Actions, Docker, Kubernetes\nObservability (Prometheus, Grafana)' }]
  projects.value = [{ name: 'CV-Generator', desc: 'Vue 3, FastAPI, LaTeX/PDF – Automatisierte Lebenslauf-Erzeugung' }]
  certs.value = 'AWS Solutions Architect Associate (2023)'
  skills.value = 'Python, TypeScript, FastAPI, Vue 3, Docker, Kubernetes, PostgreSQL, Kafka, Terraform'
}
</script>

<style>
.appbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.brand { margin: 0; font-size: 22px; font-weight: 700; color: #e9eef6; }
.brand:hover { text-decoration: underline; cursor: pointer; }

.panel { background: #0f1630; border: 1px solid #1c2646; border-radius: 12px; padding: 14px; }
.panel.single { max-width: 980px; margin: 0 auto; }
.panel h3 { margin: 16px 0 8px; }

.stepper { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 12px; }
.step { padding: 10px 12px; border-radius: 10px; border: 1px solid #273359; background: #0b122a; color: #c9d6f2; text-align: center; font-weight: 600; opacity: 0.8; }
.step.active { background: linear-gradient(180deg, #2a6ef2 0%, #265ed6 100%); color: #fff; border-color: #2a6ef2; opacity: 1; }
.step.done { background: #152047; border-color: #2a6ef2; opacity: 1; }

.mode { grid-column: 1/-1; display: grid; gap: 8px; margin-bottom: 8px; }
.mode-label { font-weight: 700; color: #c9d6f2; }
.mode-buttons { display: flex; gap: 8px; }
.toggle { padding: 10px 12px; border-radius: 10px; border: 1px solid #273359; background: #0b122a; color: #c9d6f2; cursor: pointer; }
.toggle.active { background: #152047; border-color: #2a6ef2; }

.form-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.field { display: grid; gap: 6px; }
.field.full { grid-column: 1/-1; }

label { font-weight: 600; color: #c9d6f2; }
input, textarea { width: 100%; padding: 10px 12px; border: 1px solid #273359; background: #0b122a; color: #e9eef6; border-radius: 10px; outline: none; }
textarea { min-height: 120px; resize: vertical; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }

.row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 8px; }
.row textarea { grid-column: 1 / -2; min-height: 80px; }
.row .ghost { grid-column: -2 / -1; align-self: end; }

.actions { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0; }
button, a.button { padding: 10px 14px; border: 1px solid #2a3657; background: #121a33; color: #c9d6f2; cursor: pointer; border-radius: 10px; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; transition: transform 0.15s ease, box-shadow 0.2s ease; }
button.primary { background: linear-gradient(180deg, #2a6ef2 0%, #265ed6 100%); border-color: #2a6ef2; color: #fff; }
button.secondary { background: #121a33; }
button.ghost { background: transparent; border-color: #273359; opacity: 0.9; }
button.btn-add { background: #152047; border-color: #2a6ef2; color: #dbe5ff; }
button.btn-add:hover { box-shadow: 0 8px 24px rgba(42, 110, 242, 0.25); }
button.btn-remove { background: #2a1120; border-color: #7a2a3a; color: #ffd6e0; }
button.btn-remove:hover { box-shadow: 0 8px 24px rgba(255, 107, 107, 0.2); }
button:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 8px 24px rgba(42, 110, 242, 0.25); }
button:disabled { opacity: 0.6; cursor: not-allowed; }

.preview-header { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 8px; }
.spinner { color: #c9d6f2; font-size: 14px; opacity: 0.9; display: inline-flex; align-items: center; gap: 6px; }
.dot { width: 6px; height: 6px; background: #9eb5ff; border-radius: 50%; display: inline-block; animation: bounce 1.2s infinite ease-in-out; }
.dot-b { animation-delay: 0.2s }
.dot-c { animation-delay: 0.4s }
@keyframes bounce { 0%, 80%, 100% { transform: scale(0.8); opacity: .6 } 40% { transform: scale(1); opacity: 1 } }

.preview { position: relative; background: #0b122a; border: 1px dashed #273359; border-radius: 10px; min-height: 320px; display: flex; align-items: center; justify-content: center; padding: 8px; }
.pdf-frame { width: 100%; height: 70vh; border: none; border-radius: 6px; background: #0b122a; }
.placeholder { color: #8ea0c9; text-align: center; padding: 12px; }
.hint { margin-top: 4px; color: #8ea0c9; font-size: 12px; }
.overlay { position: absolute; inset: 0; display: grid; place-items: center; background: rgba(11,18,42,0.55); border-radius: 10px; }
.loader { width: 28px; height: 28px; border: 3px solid rgba(158,181,255,0.25); border-top-color: #9eb5ff; border-radius: 50%; animation: spin 0.9s linear infinite; }
@keyframes spin { to { transform: rotate(360deg) } }

/* Interstitial loading screen */
.loading-screen { background: #0b122a; border: 1px dashed #273359; border-radius: 12px; min-height: 360px; display: grid; place-items: center; padding: 24px; }
.loading-inner { display: grid; gap: 12px; justify-items: center; text-align: center; max-width: 520px; }
.loader.big { width: 44px; height: 44px; border-width: 4px; }
.loading-text { color: #cfe0ff; font-weight: 700; }
.progress { width: 100%; height: 8px; background: #0f1630; border: 1px solid #273359; border-radius: 999px; overflow: hidden; }
.progress .bar { height: 100%; width: 35%; background: linear-gradient(90deg, rgba(158,181,255,0.1) 0%, #9eb5ff 50%, rgba(158,181,255,0.1) 100%); animation: slide 1.2s ease-in-out infinite; border-radius: 999px; }
@keyframes slide { 0% { transform: translateX(-10%); } 50% { transform: translateX(180%); } 100% { transform: translateX(-10%); } }
.tips { color: #8ea0c9; font-size: 12px; }

/* Animated icons */
.icons { display: flex; gap: 12px; margin-top: 6px; }
.ico { font-size: 22px; filter: drop-shadow(0 2px 6px rgba(0,0,0,0.2)); opacity: 0.9; }
.ico-a { animation: float 2.6s ease-in-out infinite; }
.ico-b { animation: float 2.8s ease-in-out infinite 0.2s; }
.ico-c { animation: float 3.0s ease-in-out infinite 0.35s; }
@keyframes float { 0% { transform: translateY(0) } 50% { transform: translateY(-6px) } 100% { transform: translateY(0) } }

/* Skeleton preview */
.skeleton { width: 100%; margin-top: 6px; display: grid; gap: 8px; }
.sk-line { height: 10px; border-radius: 6px; background: linear-gradient(90deg, #0f1630 0%, #1a2445 20%, #0f1630 40%); background-size: 200% 100%; animation: shimmer 1.2s linear infinite; }
.sk-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.sk-col { display: grid; gap: 8px; }
.sk-line.w60 { width: 60%; }
.sk-line.w40 { width: 40%; }
.sk-line.w80 { width: 80%; }
.sk-line.w70 { width: 70%; }
.sk-line.w50 { width: 50%; }
.sk-line.w90 { width: 90%; }
@keyframes shimmer { 0% { background-position: 200% 0 } 100% { background-position: -200% 0 } }

.error { color: #ff6b6b; margin-top: 8px; }

.fade-slide-enter-active, .fade-slide-leave-active { transition: opacity .22s ease, transform .22s ease; }
.fade-slide-enter-from, .fade-slide-leave-to { opacity: 0; transform: translateY(6px); }

@media (max-width: 880px) {
  .grid { grid-template-columns: 1fr; }
  .row { grid-template-columns: 1fr; }
  .row textarea, .row .ghost { grid-column: auto; }
}

/* Grouped card styling for repeated items */
.group { border: 1px solid #273359; background: #0b122a; border-radius: 12px; padding: 10px; margin-bottom: 10px; box-shadow: 0 2px 0 rgba(0,0,0,0.15) inset; }
.group-header { display: flex; align-items: center; justify-content: space-between; gap: 8px; padding-bottom: 8px; border-bottom: 1px dashed #273359; margin-bottom: 8px; }
.badge { display: inline-flex; align-items: center; justify-content: center; min-width: 22px; height: 22px; font-size: 12px; font-weight: 700; background: #152047; color: #cfe0ff; border: 1px solid #2a6ef2; border-radius: 999px; }
.group-body { padding-top: 4px; }

/* Fancy download button */
a.button.download-btn { background: linear-gradient(180deg, #29d98c 0%, #18a86a 100%); border-color: #18a86a; color: #04151f; }
a.button.download-btn:hover { box-shadow: 0 8px 24px rgba(41, 217, 140, 0.25); }

/* Template selection */
.templates { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 10px; }
.template-card { display: grid; gap: 6px; border: 1px solid #273359; background: #0b122a; border-radius: 12px; padding: 8px; cursor: pointer; }
.template-card.selected { border-color: #2a6ef2; box-shadow: 0 6px 20px rgba(42,110,242,0.15); }
.template-card img { width: 100%; height: auto; border-radius: 8px; display: block; }
.template-name { font-weight: 700; color: #e9eef6; text-align: center; font-size: 14px; }

@media (max-width: 680px) {
  .templates { grid-template-columns: 1fr; }
}
</style>
