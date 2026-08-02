<script setup lang="ts">
definePageMeta({ layout: false })

useSeoMeta({
  title: 'Sign In — Onyx',
  description: 'Sign in to your Onyx account to manage your links, domains, and analytics.',
})

const { signin, loading, isAuthenticated } = useAuth()

// Redirect if already logged in
if (isAuthenticated.value) {
  navigateTo('/dashboard')
}

const state = reactive({ email: '', password: '' })
const error = ref('')

async function handleSubmit() {
  error.value = ''
  try {
    await signin(state.email, state.password)
  }
  catch (err: any) {
    error.value = err?.data?.detail || 'Sign in failed. Please check your credentials.'
  }
}
</script>

<template>
  <UApp>
    <div class="min-h-screen flex">
      <!-- Left panel (decorative) -->
      <div class="hidden lg:flex flex-col justify-between w-1/2 bg-gradient-to-br from-zinc-900 via-zinc-800 to-indigo-900 p-12 relative overflow-hidden">
        <!-- Grid pattern -->
        <div class="absolute inset-0 opacity-10"
          style="background-image: linear-gradient(rgba(255,255,255,.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.1) 1px, transparent 1px); background-size: 40px 40px;" />

        <!-- Glow blobs -->
        <div class="absolute top-1/4 left-1/4 w-64 h-64 bg-zinc-500/30 rounded-full blur-3xl" />
        <div class="absolute bottom-1/4 right-1/4 w-48 h-48 bg-indigo-500/30 rounded-full blur-3xl" />

        <div class="relative z-10">
          <NuxtLink to="/" class="inline-block">
            <div class="flex items-center gap-2">
              <div class="w-8 h-8 bg-white/20 backdrop-blur rounded-lg rotate-45" />
              <span class="text-xl font-bold text-white">onyx</span>
            </div>
          </NuxtLink>
        </div>

        <div class="relative z-10 space-y-6">
          <blockquote class="text-white/90 text-xl font-medium leading-relaxed">
            "Onyx transformed how we share content. Our branded links get 40% more clicks."
          </blockquote>
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-white/20 backdrop-blur flex items-center justify-center text-white font-bold">A</div>
            <div>
              <p class="text-white font-semibold">Adebayo Seun</p>
              <p class="text-zinc-300 text-sm">Founder, GrowthHQ</p>
            </div>
          </div>

          <!-- Feature chips -->
          <div class="flex flex-wrap gap-2 pt-4">
            <span v-for="feat in ['Custom Domains', 'Analytics', 'QR Codes', 'API Access']" :key="feat"
              class="px-3 py-1 rounded-full bg-white/10 backdrop-blur text-white/80 text-xs font-medium border border-white/20">
              {{ feat }}
            </span>
          </div>
        </div>

        <div class="relative z-10 text-zinc-300 text-sm">
          © {{ new Date().getFullYear() }} Onyx. All rights reserved.
        </div>
      </div>

      <!-- Right panel (form) -->
      <div class="flex-1 flex items-center justify-center p-6 sm:p-12 bg-white dark:bg-slate-950">
        <div class="w-full max-w-md">
          <!-- Mobile logo -->
          <div class="lg:hidden mb-8 text-center">
            <AppLogo />
          </div>

          <div class="mb-8">
            <h1 class="text-3xl font-bold text-slate-900 dark:text-white mb-2">Welcome back</h1>
            <p class="text-slate-500 dark:text-slate-400">Sign in to your Onyx account</p>
          </div>

          <!-- Error alert -->
          <UAlert
            v-if="error"
            :description="error"
            color="error"
            variant="soft"
            icon="i-lucide-alert-circle"
            class="mb-6"
          />

          <form class="space-y-5" @submit.prevent="handleSubmit">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Email address</label>
              <UInput
                v-model="state.email"
                type="email"
                placeholder="you@example.com"
                autocomplete="email"
                required
                icon="i-lucide-mail"
                size="lg"
                class="w-full"
              />
            </div>

            <div>
              <div class="flex items-center justify-between mb-1.5">
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Password</label>
                <NuxtLink to="/forgot-password" class="text-xs text-zinc-600 hover:text-zinc-700 dark:text-zinc-400 dark:hover:text-zinc-300">
                  Forgot password?
                </NuxtLink>
              </div>
              <UInput
                v-model="state.password"
                type="password"
                placeholder="••••••••"
                autocomplete="current-password"
                required
                icon="i-lucide-lock"
                size="lg"
                class="w-full"
              />
            </div>

            <UButton
              type="submit"
              block
              size="lg"
              :loading="loading"
              class="rounded-xl mt-2"
            >
              Sign in
            </UButton>
          </form>

          <p class="text-center text-sm text-slate-500 dark:text-slate-400 mt-6">
            Don't have an account?
            <NuxtLink to="/signup" class="font-medium text-zinc-600 hover:text-zinc-700 dark:text-zinc-400">
              Create one free
            </NuxtLink>
          </p>
        </div>
      </div>
    </div>

    <UToaster />
  </UApp>
</template>
