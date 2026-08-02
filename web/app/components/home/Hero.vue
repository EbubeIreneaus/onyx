<script setup lang="ts">
const { isAuthenticated } = useAuth()
const url = ref('')
const isShortening = ref(false)
const result = ref<string | null>(null)
const error = ref<string | null>(null)

const handleShorten = async () => {
  if (!url.value.trim()) return
  if (!isAuthenticated.value) {
    navigateTo('/signup')
    return
  }
  isShortening.value = true
  error.value = null
  result.value = null
  const { createLink } = useLinks()
  const link = await createLink({ destination: url.value.trim() })
  isShortening.value = false
  if (link) {
    result.value = `https://${link.domain}/${link.slug}`
    url.value = ''
  }
}

const copied = ref(false)
const copyResult = async () => {
  if (!result.value) return
  await navigator.clipboard.writeText(result.value)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}

const stats = [
  { value: '10M+', label: 'Links shortened' },
  { value: '500K+', label: 'Active users' },
  { value: '99.9%', label: 'Uptime' },
  { value: '180+', label: 'Countries served' },
]
</script>

<template>
  <section class="relative min-h-screen flex flex-col items-center justify-center overflow-hidden">
    <!-- Background gradients -->
    <div class="absolute inset-0 hero-gradient pointer-events-none" />
    <div class="absolute top-1/4 -left-32 w-96 h-96 bg-zinc-500/10 rounded-full blur-3xl pointer-events-none" />
    <div class="absolute top-1/3 -right-32 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

    <div class="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 text-center">
      <!-- Badge -->
      <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-zinc-100 dark:bg-zinc-950/60 border border-zinc-200 dark:border-zinc-800/60 mb-8 animate-fade-up">
        <span class="w-2 h-2 rounded-full bg-zinc-500 animate-pulse" />
        <span class="text-sm font-medium text-zinc-700 dark:text-zinc-300">Now with AI-powered analytics</span>
      </div>

      <!-- Headline -->
      <h1 class="text-5xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight leading-tight mb-6">
        <span class="text-slate-900 dark:text-white">Links that</span><br>
        <span class="gradient-text">work smarter</span>
      </h1>

      <p class="text-xl text-slate-500 dark:text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
        Shorten, brand, and track every link. Custom domains, QR codes, and deep analytics — all in one powerful platform.
      </p>

      <!-- URL shortener input -->
      <div class="max-w-2xl mx-auto mb-6">
        <div class="flex flex-col sm:flex-row gap-3 p-2 bg-white dark:bg-slate-900 rounded-2xl shadow-xl shadow-slate-200/50 dark:shadow-slate-950/50 border border-slate-200 dark:border-slate-800">
          <div class="relative flex-1">
            <UIcon name="i-lucide-link" class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              v-model="url"
              type="url"
              placeholder="Paste your long URL here..."
              class="w-full pl-11 pr-4 py-3.5 bg-transparent text-slate-900 dark:text-white placeholder-slate-400 text-base outline-none"
              @keydown.enter="handleShorten"
            >
          </div>
          <UButton
            size="lg"
            :loading="isShortening"
            :disabled="!url.trim()"
            class="shrink-0 rounded-xl pulse-glow"
            @click="handleShorten"
          >
            Shorten URL
          </UButton>
        </div>

        <!-- Result -->
        <Transition name="slide-down">
          <div
            v-if="result"
            class="mt-3 flex items-center justify-between gap-3 px-4 py-3 bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800/50 rounded-xl"
          >
            <a :href="result" target="_blank" class="text-emerald-700 dark:text-emerald-300 font-medium hover:underline truncate">
              {{ result }}
            </a>
            <UButton
              :icon="copied ? 'i-lucide-check' : 'i-lucide-copy'"
              size="xs"
              :color="copied ? 'success' : 'neutral'"
              variant="soft"
              @click="copyResult"
            />
          </div>
        </Transition>
      </div>

      <!-- CTA buttons -->
      <div class="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
        <NuxtLink to="/signup">
          <UButton size="xl" class="rounded-xl" trailing-icon="i-lucide-arrow-right">
            Start for free
          </UButton>
        </NuxtLink>
        <NuxtLink to="/#pricing">
          <UButton size="xl" color="neutral" variant="ghost" class="rounded-xl" trailing-icon="i-lucide-chevron-down">
            See pricing
          </UButton>
        </NuxtLink>
      </div>

      <!-- Stats row -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-6 max-w-2xl mx-auto">
        <div
          v-for="stat in stats"
          :key="stat.label"
          class="text-center"
        >
          <div class="text-3xl font-bold text-slate-900 dark:text-white">{{ stat.value }}</div>
          <div class="text-sm text-slate-500 dark:text-slate-400 mt-1">{{ stat.label }}</div>
        </div>
      </div>
    </div>

    <!-- Scroll indicator -->
    <div class="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
      <UIcon name="i-lucide-chevron-down" class="w-6 h-6 text-slate-400" />
    </div>
  </section>
</template>

<style scoped>
.slide-down-enter-active, .slide-down-leave-active { transition: all 0.3s ease; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-10px); }
</style>
