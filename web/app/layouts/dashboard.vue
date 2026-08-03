<script setup lang="ts">
defineOptions({ name: 'DashboardLayout' })
const { user, signout } = useAuth()

const route = useRoute()
const isMobileOpen = ref(false)

const navItems = [
  { label: 'Overview', icon: 'i-lucide-layout-dashboard', to: '/dashboard' },
  { label: 'Links', icon: 'i-lucide-link', to: '/dashboard/links' },
  { label: 'Domains', icon: 'i-lucide-globe', to: '/dashboard/domains' },
  { label: 'Developer API', icon: 'i-lucide-code-2', to: '/dashboard/developer' },
  { label: 'Settings', icon: 'i-lucide-settings', to: '/dashboard/settings' }
]

const isActive = (to: string) => {
  if (to === '/dashboard') return route.path === '/dashboard'
  return route.path.startsWith(to)
}

// Close mobile menu on route change
watch(() => route.path, () => { isMobileOpen.value = false })
</script>

<template>
  <UApp>
    <!-- Full-screen loading fallback while auth session resolves -->
    <div
      v-if="!user"
      class="min-h-screen flex items-center justify-center bg-zinc-950 text-white"
    >
      <div class="flex flex-col items-center gap-3">
        <AppLogo />
        <UIcon
          name="i-lucide-loader-2"
          class="w-5 h-5 animate-spin text-zinc-500 mt-1"
        />
      </div>
    </div>

    <div
      v-else
      class="min-h-screen flex bg-slate-50 dark:bg-slate-950"
    >
      <!-- ── Sidebar ─────────────────────────────────────── -->
      <!-- Mobile overlay -->
      <Transition name="fade">
        <div
          v-if="isMobileOpen"
          class="fixed inset-0 z-30 bg-black/50 lg:hidden"
          @click="isMobileOpen = false"
        />
      </Transition>

      <!-- Sidebar panel -->
      <aside
        class="fixed top-0 left-0 h-full z-40 w-64 flex flex-col bg-white dark:bg-zinc-900 border-r border-zinc-200 dark:border-zinc-800 transition-transform duration-300 lg:translate-x-0 sidebar-transition"
        :class="isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'"
      >
        <!-- Logo -->
        <div class="flex items-center h-16 px-5 border-b border-zinc-200 dark:border-zinc-800 shrink-0">
          <AppLogo />
        </div>

        <!-- Nav -->
        <nav class="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          <NuxtLink
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            class="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-all duration-200 group"
            :class="isActive(item.to)
              ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-white font-semibold'
              : 'text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800/60 hover:text-zinc-900 dark:hover:text-white'"
          >
            <UIcon
              :name="item.icon"
              class="w-5 h-5 shrink-0 transition-transform duration-200 group-hover:scale-105"
              :class="isActive(item.to) ? 'text-zinc-900 dark:text-white' : ''"
            />
            {{ item.label }}
            <span
              v-if="isActive(item.to)"
              class="ml-auto w-1.5 h-1.5 rounded-full bg-zinc-900 dark:bg-zinc-100"
            />
          </NuxtLink>
        </nav>

        <!-- Bottom: user profile + signout -->
        <div class="shrink-0 p-3 border-t border-zinc-200 dark:border-zinc-800">
          <!-- Subscription badge -->
          <NuxtLink
            to="/dashboard/settings"
            class="block mb-2 px-3 py-2 rounded-md bg-zinc-100 dark:bg-zinc-800/80 border border-zinc-200 dark:border-zinc-700/60 hover:bg-zinc-200 dark:hover:bg-zinc-700/80 transition-colors"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <UIcon
                  name="i-lucide-zap"
                  class="w-4 h-4 text-amber-500"
                />
                <span class="text-xs font-semibold text-zinc-800 dark:text-zinc-200 uppercase tracking-wide">
                  {{ user?.current_subscription?.tier?.name || 'No Plan' }}
                </span>
              </div>
              <span class="text-[10px] font-medium text-amber-600 dark:text-amber-400 underline">Manage</span>
            </div>
          </NuxtLink>

          <!-- User row -->
          <div class="flex items-center justify-between px-2 py-1.5 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors">
            <NuxtLink
              to="/dashboard/settings"
              class="flex items-center gap-3 flex-1 min-w-0 pr-2"
            >
              <UAvatar
                :alt="user?.fullname || 'User'"
                size="sm"
                class="shrink-0 bg-zinc-200 dark:bg-zinc-800 text-zinc-800 dark:text-zinc-200 font-bold"
              />
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-zinc-900 dark:text-white truncate">{{ user?.fullname }}</p>
                <p class="text-xs text-zinc-500 dark:text-zinc-400 truncate">{{ user?.email }}</p>
              </div>
            </NuxtLink>
            <UButton
              icon="i-lucide-log-out"
              size="xs"
              color="neutral"
              variant="ghost"
              aria-label="Sign out"
              class="shrink-0"
              @click="signout"
            />
          </div>
        </div>
      </aside>

      <!-- ── Main content ────────────────────────────────── -->
      <div class="flex-1 flex flex-col lg:ml-64 min-h-screen bg-zinc-50/50 dark:bg-zinc-950">
        <!-- Top bar -->
        <header class="sticky top-0 z-20 h-16 flex items-center justify-between px-4 sm:px-6 bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl border-b border-zinc-200 dark:border-zinc-800 shrink-0">
          <!-- Mobile menu toggle -->
          <UButton
            icon="i-lucide-menu"
            color="neutral"
            variant="ghost"
            class="lg:hidden"
            aria-label="Open menu"
            @click="isMobileOpen = !isMobileOpen"
          />

          <!-- Spacer -->
          <div class="flex-1" />

          <!-- Right controls -->
          <div class="flex items-center gap-2">
            <UColorModeButton
              size="sm"
              color="neutral"
              variant="ghost"
            />
            <UButton
              to="/dashboard/links"
              icon="i-lucide-plus"
              size="sm"
              color="primary"
              label="New link"
              class="hidden sm:flex"
            />
          </div>
        </header>

        <!-- Page content -->
        <main class="flex-1 p-4 sm:p-6 lg:p-8">
          <slot />
        </main>
      </div>
    </div>

    <UToaster />
  </UApp>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
