<script setup lang="ts">
definePageMeta({ layout: false })

useSeoMeta({
  title: 'Create Account — Onyx',
  description: 'Create a free Onyx account and start shortening links in seconds.',
})

const { signup, loading, isAuthenticated } = useAuth()

if (isAuthenticated.value) {
  navigateTo('/dashboard')
}

const state = reactive({ fullname: '', email: '', password: '', confirm: '' })
const error = ref('')

const route = useRoute()

async function handleSubmit() {
  error.value = ''
  if (state.password !== state.confirm) {
    error.value = 'Passwords do not match.'
    return
  }
  if (state.password.length < 8) {
    error.value = 'Password must be at least 8 characters.'
    return
  }
  try {
    await signup(state.fullname, state.email, state.password)
    const planParam = route.query.plan
    if (planParam) {
      await navigateTo(`/dashboard/settings?plan=${planParam}`)
    }
  }
  catch (err: any) {
    error.value = err?.data?.detail || 'Registration failed. Please try again.'
  }
}

const features = [
  'Free forever plan — no credit card needed',
  '5 short links to get started',
  'Visitor analytics included',
  'Upgrade anytime to unlock more',
]
</script>

<template>
  <UApp>
    <div class="min-h-screen flex">
      <!-- Left panel -->
      <div class="hidden lg:flex flex-col justify-between w-1/2 bg-gradient-to-br from-zinc-900 via-zinc-800 to-indigo-900 p-12 relative overflow-hidden">
        <div class="absolute inset-0 opacity-10"
          style="background-image: linear-gradient(rgba(255,255,255,.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.1) 1px, transparent 1px); background-size: 40px 40px;" />
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

        <div class="relative z-10 space-y-8">
          <div>
            <h2 class="text-3xl font-bold text-white mb-4">Start managing your links smarter</h2>
            <p class="text-zinc-200 leading-relaxed">
              Join thousands of creators, marketers, and businesses who trust Onyx for their link management needs.
            </p>
          </div>

          <ul class="space-y-3">
            <li v-for="feat in features" :key="feat" class="flex items-center gap-3 text-zinc-100">
              <div class="w-5 h-5 rounded-full bg-zinc-400/30 flex items-center justify-center shrink-0">
                <UIcon name="i-lucide-check" class="w-3 h-3 text-zinc-300" />
              </div>
              <span class="text-sm">{{ feat }}</span>
            </li>
          </ul>
        </div>

        <div class="relative z-10 text-zinc-300 text-sm">
          © {{ new Date().getFullYear() }} Onyx. All rights reserved.
        </div>
      </div>

      <!-- Right panel (form) -->
      <div class="flex-1 flex items-center justify-center p-6 sm:p-12 bg-white dark:bg-slate-950">
        <div class="w-full max-w-md">
          <div class="lg:hidden mb-8 text-center">
            <AppLogo />
          </div>

          <div class="mb-8">
            <h1 class="text-3xl font-bold text-slate-900 dark:text-white mb-2">Create your account</h1>
            <p class="text-slate-500 dark:text-slate-400">Free forever. No credit card required.</p>
          </div>

          <UAlert
            v-if="error"
            :description="error"
            color="error"
            variant="soft"
            icon="i-lucide-alert-circle"
            class="mb-6"
          />

          <form class="space-y-4" @submit.prevent="handleSubmit">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Full name</label>
              <UInput
                v-model="state.fullname"
                type="text"
                placeholder="Jane Doe"
                autocomplete="name"
                required
                icon="i-lucide-user"
                size="lg"
                class="w-full"
              />
            </div>

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
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Password</label>
              <UInput
                v-model="state.password"
                type="password"
                placeholder="At least 8 characters"
                autocomplete="new-password"
                required
                icon="i-lucide-lock"
                size="lg"
                class="w-full"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Confirm password</label>
              <UInput
                v-model="state.confirm"
                type="password"
                placeholder="Repeat your password"
                autocomplete="new-password"
                required
                icon="i-lucide-lock-keyhole"
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
              Create account
            </UButton>
          </form>

          <p class="text-center text-xs text-slate-400 mt-4">
            By creating an account you agree to our
            <NuxtLink to="/terms" class="text-zinc-600 hover:underline">Terms</NuxtLink>
            and
            <NuxtLink to="/privacy" class="text-zinc-600 hover:underline">Privacy Policy</NuxtLink>.
          </p>

          <p class="text-center text-sm text-slate-500 dark:text-slate-400 mt-5">
            Already have an account?
            <NuxtLink to="/login" class="font-medium text-zinc-600 hover:text-zinc-700 dark:text-zinc-400">
              Sign in
            </NuxtLink>
          </p>
        </div>
      </div>
    </div>

    <UToaster />
  </UApp>
</template>
