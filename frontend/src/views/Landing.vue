<template>
  <main>
    <!-- Topbar -->
    <header class="w-full">
      <div class="mx-auto max-w-6xl px-4 sm:px-6 py-4 flex items-center justify-between">
        <RouterLink to="/" class="inline-flex items-baseline gap-1 select-none">
          <span class="text-xl font-extrabold tracking-tight text-zinc-100">CV</span>
          <span class="text-xl font-extrabold tracking-tight text-primary">Gen</span>
        </RouterLink>
        <nav class="flex items-center gap-2">
          <RouterLink v-if="isAuthenticated" to="/tool">
            <UiButton size="sm">Zum Tool</UiButton>
          </RouterLink>
          <UiButton v-else size="sm" @click="login">Anmelden</UiButton>
        </nav>
      </div>
    </header>

    <!-- Hero -->
    <section class="relative overflow-hidden">
      <div class="absolute inset-0 -z-10 bg-[radial-gradient(60%_40%_at_20%_0%,rgba(42,110,242,0.35)_0%,transparent_60%),radial-gradient(50%_30%_at_90%_10%,rgba(41,217,140,0.25)_0%,transparent_60%)]"></div>
      <div class="mx-auto max-w-6xl px-4 sm:px-6 py-14 lg:py-20">
        <div class="grid gap-10 lg:grid-cols-2 lg:gap-12 items-center">
          <div class="text-center lg:text-left">
            <h1 id="hero-title" class="text-3xl sm:text-5xl/tight font-extrabold tracking-tight text-zinc-50">
              Dein Lebenslauf. Einfach. Klar. Schnell.
            </h1>
            <p class="mt-3 text-zinc-300 text-base sm:text-lg max-w-prose mx-auto lg:mx-0">
              Erstelle in wenigen Minuten einen sauberen, professionellen Lebenslauf — ohne Layout‑Stress.
            </p>
            <div class="mt-6 flex items-center gap-3 justify-center lg:justify-start">
              <RouterLink to="/tool">
                <UiButton size="lg">Jetzt testen</UiButton>
              </RouterLink>
            </div>
          </div>

          <div class="relative">
            <div class="absolute -inset-4 -z-10 bg-primary/20 blur-3xl rounded-3xl"></div>
            <div class="rounded-2xl border border-zinc-800/80 bg-zinc-900/60 backdrop-blur shadow-xl">
              <div class="h-8 border-b border-zinc-800/80 flex items-center gap-1 px-3">
                <span class="size-2 rounded-full bg-zinc-700"></span>
                <span class="size-2 rounded-full bg-zinc-700"></span>
                <span class="size-2 rounded-full bg-zinc-700"></span>
              </div>
              <div class="p-5">
                <div class="space-y-3">
                  <div class="h-3 w-3/5 rounded bg-zinc-700/60 shimmer"></div>
                  <div class="h-3 w-2/5 rounded bg-zinc-700/60 shimmer"></div>
                  <div class="h-2"></div>
                  <div class="h-3 w-[92%] rounded bg-zinc-700/60 shimmer"></div>
                  <div class="h-3 w-[86%] rounded bg-zinc-700/60 shimmer"></div>
                  <div class="h-3 w-2/3 rounded bg-zinc-700/60 shimmer"></div>
                  <div class="h-2"></div>
                  <div class="h-3 w-4/5 rounded bg-zinc-700/60 shimmer"></div>
                  <div class="h-3 w-3/4 rounded bg-zinc-700/60 shimmer"></div>
                  <div class="h-3 w-2/3 rounded bg-zinc-700/60 shimmer"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Value props (moved above steps) -->
    <section class="mx-auto max-w-6xl px-4 sm:px-6 py-10">
      <div class="grid gap-4 cols-3-fixed">
        <UiCard>
          <div class="flex flex-col items-center text-center gap-1 p-5">
            <div class="size-10 rounded-md bg-zinc-800 text-zinc-300 grid place-items-center shadow-sm">⚡</div>
            <div class="font-semibold text-zinc-100">Schneller Start</div>
            <div class="text-zinc-400 text-sm">Stichpunkte rein, PDF raus.</div>
          </div>
        </UiCard>
        <UiCard>
          <div class="flex flex-col items-center text-center gap-1 p-5">
            <div class="size-10 rounded-md bg-zinc-800 text-zinc-300 grid place-items-center shadow-sm">📄</div>
            <div class="font-semibold text-zinc-100">Sauberes Layout</div>
            <div class="text-zinc-400 text-sm">Klar strukturiertes LaTeX‑Template.</div>
          </div>
        </UiCard>
        <UiCard>
          <div class="flex flex-col items-center text-center gap-1 p-5">
            <div class="size-10 rounded-md bg-zinc-800 text-zinc-300 grid place-items-center shadow-sm">📥</div>
            <div class="font-semibold text-zinc-100">Direkter Download als PDF</div>
            <div class="text-zinc-400 text-sm">Ein Klick, sofort als PDF.</div>
          </div>
        </UiCard>
      </div>
    </section>

    <!-- Steps (now below values) -->
    <section class="mx-auto max-w-6xl px-4 sm:px-6 pb-14">
      <h2 id="examples-title" class="text-center text-lg font-semibold text-zinc-200">So funktioniert’s</h2>
      <div class="mt-5 grid cols-3-fixed gap-4">
        <UiCard >
          <template #header>
            <div class="text-sm font-bold text-zinc-100">1. Stichpunkte eingeben</div>
          </template>
          <div class="font-mono text-xs leading-relaxed text-zinc-300 bg-zinc-900/80 border border-zinc-800 rounded-lg p-3">
            • Senior Software Engineer – ACME GmbH, Berlin<br />
            • Microservices, FastAPI, Kubernetes<br />
            • TU München – M.Sc. Informatik
          </div>
        </UiCard>

        <UiCard>
          <template #header>
            <div class="text-sm font-bold text-zinc-100">2. LinkedIn‑Import (optional)</div>
          </template>
          <div class="bg-zinc-900/80 border border-zinc-800 rounded-lg p-2 flex items-center gap-2 text-zinc-400">
            <span class="size-2 rounded-full bg-zinc-700"></span>
            <span class="size-2 rounded-full bg-zinc-700"></span>
            <span class="size-2 rounded-full bg-zinc-700"></span>
            <span class="truncate text-sm">https://www.linkedin.com/in/mustermann</span>
          </div>
        </UiCard>

        <UiCard>
          <template #header>
            <div class="text-sm font-bold text-zinc-100">3. PDF‑Vorschau erzeugen</div>
          </template>
          <div class="bg-zinc-900/80 border border-dashed border-zinc-800 rounded-lg p-3 space-y-2">
            <div class="h-3 w-2/3 rounded bg-zinc-700/60"></div>
            <div class="h-3 w-1/3 rounded bg-zinc-700/60"></div>
            <div class="h-2"></div>
            <div class="h-3 w-[92%] rounded bg-zinc-700/60"></div>
            <div class="h-3 w-[85%] rounded bg-zinc-700/60"></div>
            <div class="h-3 w-[65%] rounded bg-zinc-700/60"></div>
          </div>
        </UiCard>
      </div>
    </section>
  </main>
</template>

<script setup>
import { useAuth0 } from '@auth0/auth0-vue'
import UiButton from '@/components/ui/Button.vue'
import UiCard from '@/components/ui/Card.vue'

const { isAuthenticated, loginWithRedirect } = useAuth0()

const login = () => loginWithRedirect({ appState: { targetUrl: '/tool' } })
</script>

<style scoped>
.shimmer {
  position: relative;
  overflow: hidden;
}
.shimmer::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
  transform: translateX(-100%);
  animation: shimmer 2.2s infinite;
}
@keyframes shimmer { 0% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }
</style>
