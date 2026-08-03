<script setup lang="ts">
const { user, isAuthenticated, signout } = useAuth()

const navLinks = [
  { label: 'Features', to: '/#features' },
  { label: 'Pricing', to: '/#pricing' },
  { label: 'FAQ', to: '/#faq' }
]

const isScrolled = ref(false)
onMounted(() => {
  window.addEventListener('scroll', () => {
    isScrolled.value = window.scrollY > 20
  })
})
</script>

<template>
  <UApp>
    <!-- Header -->
    <header
      class="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
      :class="isScrolled
        ? 'bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border-b border-slate-200/60 dark:border-slate-800/60 shadow-sm'
        : 'bg-transparent'"
    >
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <AppLogo />

          <!-- Nav links (hidden on mobile) -->
          <nav class="hidden md:flex items-center gap-1">
            <NuxtLink
              v-for="link in navLinks"
              :key="link.to"
              :to="link.to"
              class="px-3 py-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-zinc-600 dark:hover:text-zinc-400 transition-colors rounded-lg hover:bg-zinc-50 dark:hover:bg-zinc-950/30"
            >
              {{ link.label }}
            </NuxtLink>
          </nav>

          <!-- Right actions -->
          <div class="flex items-center gap-2">
            <UColorModeButton
              size="sm"
              color="neutral"
              variant="ghost"
            />

            <template v-if="isAuthenticated">
              <NuxtLink to="/dashboard">
                <UButton
                  size="sm"
                  variant="soft"
                  color="primary"
                >
                  Dashboard
                </UButton>
              </NuxtLink>
              <UButton
                size="sm"
                color="neutral"
                variant="ghost"
                @click="signout"
              >
                Sign out
              </UButton>
            </template>
            <template v-else>
              <NuxtLink to="/login">
                <UButton
                  size="sm"
                  color="neutral"
                  variant="ghost"
                >
                  Sign in
                </UButton>
              </NuxtLink>
              <NuxtLink to="/signup">
                <UButton
                  size="sm"
                  color="primary"
                >
                  Get started free
                </UButton>
              </NuxtLink>
            </template>
          </div>
        </div>
      </div>
    </header>

    <!-- Page content -->
    <main class="pt-16">
      <slot />
    </main>

    <!-- Footer -->
    <footer class="border-t border-slate-200 dark:border-slate-800 mt-24">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div class="col-span-1 md:col-span-2">
            <AppLogo />
            <p class="mt-4 text-sm text-slate-500 dark:text-slate-400 max-w-xs leading-relaxed">
              Powerful URL shortening and link management for modern teams and creators. Track, manage, and grow with Onyx.
            </p>
          </div>
          <div>
            <h4 class="text-sm font-semibold text-slate-900 dark:text-white mb-3">
              Product
            </h4>
            <ul class="space-y-2">
              <li
                v-for="link in [['Features', '/#features'], ['Pricing', '/#pricing'], ['Dashboard', '/dashboard']]"
                :key="link[0]"
              >
                <NuxtLink
                  :to="link[1]"
                  class="text-sm text-slate-500 hover:text-zinc-600 dark:text-slate-400 dark:hover:text-zinc-400 transition-colors"
                >
                  {{ link[0] }}
                </NuxtLink>
              </li>
            </ul>
          </div>
          <div>
            <h4 class="text-sm font-semibold text-slate-900 dark:text-white mb-3">
              Legal
            </h4>
            <ul class="space-y-2">
              <li
                v-for="link in [['Privacy Policy', '/privacy'], ['Terms of Service', '/terms']]"
                :key="link[0]"
              >
                <NuxtLink
                  :to="link[1]"
                  class="text-sm text-slate-500 hover:text-zinc-600 dark:text-slate-400 dark:hover:text-zinc-400 transition-colors"
                >
                  {{ link[0] }}
                </NuxtLink>
              </li>
            </ul>
          </div>
        </div>
        <div class="mt-8 pt-8 border-t border-slate-200 dark:border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p class="text-sm text-slate-500 dark:text-slate-400">
            © {{ new Date().getFullYear() }} Onyx. All rights reserved.
          </p>
          <p class="text-sm text-slate-400">
            Built with ❤️ for the modern web
          </p>
        </div>
      </div>
    </footer>

    <UToaster />
  </UApp>
</template>
