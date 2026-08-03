<script setup lang="ts">
defineOptions({ name: 'AdminLayout' })

const { user, fetchUser, signout } = useAuth()
const route = useRoute()
const isMobileOpen = ref(false)

onMounted(() => {
  fetchUser()
})

const adminNav = [
  { label: 'Overview', icon: 'i-lucide-layout-dashboard', to: '/admin' },
  { label: 'Users', icon: 'i-lucide-users', to: '/admin/users' },
  { label: 'Domains', icon: 'i-lucide-globe', to: '/admin/domains' },
  { label: 'Short Links', icon: 'i-lucide-link', to: '/admin/links' },
  { label: 'Tiers & Pricing', icon: 'i-lucide-layers', to: '/admin/tiers' }
]

const isActive = (to: string) => {
  if (to === '/admin') return route.path === '/admin'
  return route.path.startsWith(to)
}

watch(() => route.path, () => {
  isMobileOpen.value = false
})
</script>

<template>
  <UApp>
    <!-- Auth Guard Loading -->
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

    <!-- Non-Admin Access Warning -->
    <div
      v-else-if="!user.is_admin"
      class="min-h-screen flex items-center justify-center bg-zinc-950 text-white p-6"
    >
      <div class="max-w-md text-center space-y-6 bg-zinc-900 border border-zinc-800 p-8 rounded-2xl">
        <div class="inline-flex p-4 rounded-full bg-rose-500/10 text-rose-400">
          <UIcon
            name="i-lucide-shield-alert"
            class="w-10 h-10"
          />
        </div>
        <div>
          <h1 class="text-xl font-bold text-white mb-2">
            Access Denied
          </h1>
          <p class="text-sm text-zinc-400">
            You do not have administrative privileges to access the Admin Portal.
          </p>
        </div>
        <UButton
          to="/dashboard"
          color="primary"
          size="md"
        >
          Return to Dashboard
        </UButton>
      </div>
    </div>

    <!-- Admin Portal Interface -->
    <div
      v-else
      class="min-h-screen flex bg-zinc-950 text-white font-sans"
    >
      <!-- Mobile Overlay -->
      <Transition name="fade">
        <div
          v-if="isMobileOpen"
          class="fixed inset-0 z-30 bg-black/60 lg:hidden"
          @click="isMobileOpen = false"
        />
      </Transition>

      <!-- Admin Sidebar -->
      <aside
        class="fixed top-0 left-0 h-full z-40 w-64 flex flex-col bg-zinc-900 border-r border-zinc-800 transition-transform duration-300 lg:translate-x-0"
        :class="isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'"
      >
        <!-- Top Logo Header -->
        <div class="flex items-center justify-between h-16 px-5 border-b border-zinc-800 shrink-0">
          <div class="flex items-center gap-2">
            <AppLogo />
            <span class="text-[10px] px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-400 font-mono font-bold border border-rose-500/20">ADMIN</span>
          </div>
        </div>

        <!-- Navigation Menu -->
        <nav class="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          <NuxtLink
            v-for="item in adminNav"
            :key="item.to"
            :to="item.to"
            class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all group"
            :class="isActive(item.to)
              ? 'bg-rose-500/10 text-rose-400 font-semibold border border-rose-500/20'
              : 'text-zinc-400 hover:bg-zinc-800 hover:text-white'"
          >
            <UIcon
              :name="item.icon"
              class="w-5 h-5 shrink-0"
            />
            {{ item.label }}
          </NuxtLink>
        </nav>

        <!-- Bottom Return & User Profile -->
        <div class="shrink-0 p-3 border-t border-zinc-800 space-y-2">
          <UButton
            to="/dashboard"
            icon="i-lucide-arrow-left"
            color="neutral"
            variant="soft"
            size="sm"
            block
          >
            User Dashboard
          </UButton>

          <div class="flex items-center justify-between px-2 py-2 rounded-xl bg-zinc-950 border border-zinc-800">
            <div class="flex items-center gap-2.5 min-w-0">
              <UAvatar
                :alt="user?.fullname || 'Admin'"
                size="sm"
                class="bg-rose-500/20 text-rose-400 font-bold shrink-0"
              />
              <div class="min-w-0">
                <p class="text-xs font-semibold text-white truncate">
                  {{ user?.fullname }}
                </p>
                <p class="text-[11px] text-rose-400 font-mono">
                  Administrator
                </p>
              </div>
            </div>
            <UButton
              icon="i-lucide-log-out"
              size="xs"
              color="neutral"
              variant="ghost"
              @click="signout"
            />
          </div>
        </div>
      </aside>

      <!-- Main Admin Content -->
      <div class="flex-1 flex flex-col lg:ml-64 min-h-screen bg-zinc-950">
        <!-- Top Bar -->
        <header class="sticky top-0 z-20 h-16 flex items-center justify-between px-4 sm:px-6 bg-zinc-950/80 backdrop-blur-xl border-b border-zinc-800 shrink-0">
          <UButton
            icon="i-lucide-menu"
            color="neutral"
            variant="ghost"
            class="lg:hidden"
            @click="isMobileOpen = !isMobileOpen"
          />

          <div class="flex-1" />

          <div class="flex items-center gap-3">
            <UColorModeButton
              size="sm"
              color="neutral"
              variant="ghost"
            />
          </div>
        </header>

        <!-- Page Content View -->
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
