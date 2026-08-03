<script setup lang="ts">
const route = useRoute()

const isMobileOpen = ref(false)

const docSections = [
  {
    title: 'Overview',
    items: [
      { label: 'Getting Started', icon: 'i-lucide-rocket', to: '/docs/get-started' },
      { label: 'Authentication', icon: 'i-lucide-key', to: '/docs/authentication' }
    ]
  },
  {
    title: 'API Reference',
    items: [
      { label: 'Domains API', icon: 'i-lucide-globe', to: '/docs/domains' },
      { label: 'Redirects & Links API', icon: 'i-lucide-link', to: '/docs/redirects' }
    ]
  }
]

const isActive = (to: string) => route.path === to

watch(() => route.path, () => {
  isMobileOpen.value = false
})
</script>

<template>
  <UApp>
    <div class="min-h-screen bg-zinc-950 text-white font-sans">
      <!-- Top Navbar -->
      <header class="sticky top-0 z-40 h-16 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-xl px-4 sm:px-6 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <UButton
            icon="i-lucide-menu"
            color="neutral"
            variant="ghost"
            class="md:hidden"
            aria-label="Toggle navigation menu"
            @click="isMobileOpen = !isMobileOpen"
          />
          <AppLogo />
          <span class="hidden sm:inline-block text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 font-mono font-semibold border border-emerald-500/20">
            v1.0 API Docs
          </span>
        </div>

        <div class="flex items-center gap-3">
          <UButton
            to="/dashboard"
            color="neutral"
            variant="soft"
            size="sm"
            class="hidden sm:flex"
          >
            Dashboard
          </UButton>
          <UButton
            to="/dashboard/developer"
            color="primary"
            size="sm"
            icon="i-lucide-code-2"
          >
            Get API Key
          </UButton>
        </div>
      </header>

      <!-- Mobile Navigation Drawer -->
      <Transition name="fade">
        <div
          v-if="isMobileOpen"
          class="fixed inset-0 z-40 bg-black/60 backdrop-blur-xs md:hidden"
          @click="isMobileOpen = false"
        />
      </Transition>

      <aside
        class="fixed top-16 left-0 bottom-0 z-50 w-72 bg-zinc-950 border-r border-zinc-800 p-6 overflow-y-auto transition-transform duration-200 md:hidden"
        :class="isMobileOpen ? 'translate-x-0' : '-translate-x-full'"
      >
        <nav class="space-y-6">
          <div
            v-for="section in docSections"
            :key="section.title"
            class="space-y-2"
          >
            <p class="text-[11px] font-bold uppercase tracking-wider text-zinc-500 px-3">
              {{ section.title }}
            </p>
            <NuxtLink
              v-for="item in section.items"
              :key="item.to"
              :to="item.to"
              class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all"
              :class="isActive(item.to)
                ? 'bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/20'
                : 'text-zinc-400 hover:text-white hover:bg-zinc-900'"
            >
              <UIcon
                :name="item.icon"
                class="w-4.5 h-4.5 shrink-0"
              />
              {{ item.label }}
            </NuxtLink>
          </div>
        </nav>
      </aside>

      <!-- Desktop Body Layout -->
      <div class="max-w-7xl mx-auto flex">
        <!-- Desktop Fixed Left Sidebar -->
        <aside class="w-64 shrink-0 border-r border-zinc-800/80 p-6 hidden md:block sticky top-16 h-[calc(100vh-4rem)] overflow-y-auto">
          <nav class="space-y-6">
            <div
              v-for="section in docSections"
              :key="section.title"
              class="space-y-1"
            >
              <p class="text-[11px] font-bold uppercase tracking-wider text-zinc-500 mb-2 px-3">
                {{ section.title }}
              </p>
              <NuxtLink
                v-for="item in section.items"
                :key="item.to"
                :to="item.to"
                class="flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium transition-all"
                :class="isActive(item.to)
                  ? 'bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/20'
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-900'"
              >
                <UIcon
                  :name="item.icon"
                  class="w-4 h-4 shrink-0"
                />
                {{ item.label }}
              </NuxtLink>
            </div>
          </nav>
        </aside>

        <!-- Main Content View -->
        <main class="flex-1 p-6 sm:p-10 max-w-4xl min-w-0">
          <slot />
        </main>
      </div>
    </div>
  </UApp>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>

<style>
main pre {
  overflow-x: auto !important;
  max-width: 100% !important;
  white-space: pre !important;
  word-break: normal !important;
  word-wrap: normal !important;
}
</style>
