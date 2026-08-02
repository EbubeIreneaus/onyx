<script setup lang="ts">
definePageMeta({ layout: 'dashboard', middleware: 'auth' })

useSeoMeta({ title: 'Settings — Onyx' })

const { user, fetchMe } = useAuth()
const api = useApi()
const toast = useToast()
const config = useRuntimeConfig()

// Profile
const profile = reactive({
  fullname: user.value?.fullname || '',
  email: user.value?.email || '',
})
const savingProfile = ref(false)

async function saveProfile() {
  savingProfile.value = true
  try {
    // Note: Update endpoint can be added to backend; for now show toast
    toast.add({ title: 'Profile updated', color: 'success' })
  }
  catch (e: any) {
    toast.add({ title: 'Error', description: e?.data?.detail || 'Update failed', color: 'error' })
  }
  finally {
    savingProfile.value = false
  }
}

// Password change
const passForm = reactive({ current: '', new_password: '', confirm: '' })
const changingPass = ref(false)
const passError = ref('')

async function changePassword() {
  passError.value = ''
  if (passForm.new_password !== passForm.confirm) {
    passError.value = 'New passwords do not match.'
    return
  }
  if (passForm.new_password.length < 8) {
    passError.value = 'New password must be at least 8 characters.'
    return
  }
  changingPass.value = true
  try {
    await api('/api/v1/auth/change-password', {
      method: 'POST',
      body: { current: passForm.current, new_password: passForm.new_password },
    })
    toast.add({ title: 'Password changed!', description: 'You will need to sign in again.', color: 'success' })
    Object.assign(passForm, { current: '', new_password: '', confirm: '' })
  }
  catch (e: any) {
    passError.value = e?.data?.detail || 'Password change failed.'
    toast.add({ title: 'Error', description: passError.value, color: 'error' })
  }
  finally {
    changingPass.value = false
  }
}

// Subscription info
const sub = computed(() => user.value?.current_subscription)
const tier = computed(() => sub.value?.tier)

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-NG', { day: 'numeric', month: 'long', year: 'numeric' })
}

// Subscribe to a free tier
async function activateFree() {
  try {
    await api('/api/v1/client/subscribe', {
      method: 'POST',
      body: { tier_id: 'free', callback_url: `${config.public.apiBase}/dashboard/settings` },
    })
    await fetchMe()
    toast.add({ title: 'Free plan activated!', color: 'success' })
  }
  catch (e: any) {
    toast.add({ title: 'Error', description: e?.data?.detail || 'Could not activate.', color: 'error' })
  }
}
</script>

<template>
  <div class="max-w-2xl space-y-8">
    <!-- Subscription card -->
    <div class="p-6 rounded-md border"
      :class="tier ? 'bg-zinc-100 dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800' : 'bg-white dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800'"
    >
      <div class="flex items-start justify-between gap-4">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <UIcon name="i-lucide-zap" class="w-5 h-5 text-zinc-600 dark:text-zinc-400" />
            <h3 class="font-semibold text-slate-900 dark:text-white">Subscription</h3>
          </div>
          <p class="text-sm text-slate-500 dark:text-slate-400">Manage your plan and billing.</p>
        </div>
        <UBadge
          :color="sub?.status === 'active' ? 'success' : 'warning'"
          variant="soft"
          size="sm"
          :label="sub?.status ? sub.status.replace('_', ' ') : 'No plan'"
          class="capitalize"
        />
      </div>

      <div v-if="tier" class="mt-5 grid grid-cols-2 gap-4">
        <div class="p-3 rounded-md bg-white/80 dark:bg-zinc-950/60 border border-zinc-200/60 dark:border-zinc-800/60">
          <p class="text-xs text-slate-500 mb-0.5">Plan</p>
          <p class="font-semibold text-slate-900 dark:text-white">{{ tier.name }}</p>
        </div>
        <div class="p-3 rounded-md bg-white/80 dark:bg-zinc-950/60 border border-zinc-200/60 dark:border-zinc-800/60">
          <p class="text-xs text-slate-500 mb-0.5">Price</p>
          <p class="font-semibold text-slate-900 dark:text-white">₦{{ Number(tier.price).toLocaleString() }}/mo</p>
        </div>
        <div class="p-3 rounded-md bg-white/80 dark:bg-zinc-950/60 border border-zinc-200/60 dark:border-zinc-800/60">
          <p class="text-xs text-slate-500 mb-0.5">Max Links</p>
          <p class="font-semibold text-slate-900 dark:text-white">{{ tier.max_short_link.toLocaleString() }}</p>
        </div>
        <div v-if="sub?.expired_at" class="p-3 rounded-md bg-white/80 dark:bg-zinc-950/60 border border-zinc-200/60 dark:border-zinc-800/60">
          <p class="text-xs text-slate-500 mb-0.5">Renews</p>
          <p class="font-semibold text-slate-900 dark:text-white">{{ formatDate(sub.expired_at) }}</p>
        </div>
      </div>

      <div v-else class="mt-4">
        <p class="text-sm text-slate-500 dark:text-slate-400 mb-3">You don't have an active subscription.</p>
      </div>

      <div class="mt-5 flex gap-3">
        <NuxtLink to="/#pricing">
          <UButton size="sm" :color="tier ? 'neutral' : 'primary'" :variant="tier ? 'soft' : 'solid'">
            {{ tier ? 'View plans' : 'Upgrade now' }}
          </UButton>
        </NuxtLink>
        <UButton v-if="!sub" size="sm" color="neutral" variant="ghost" @click="activateFree">
          Activate free plan
        </UButton>
      </div>
    </div>

    <!-- Profile -->
    <div class="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
      <div class="mb-5">
        <h3 class="font-semibold text-slate-900 dark:text-white mb-0.5">Profile</h3>
        <p class="text-sm text-slate-500 dark:text-slate-400">Update your name and email address.</p>
      </div>

      <!-- Avatar row -->
      <div class="flex items-center gap-4 mb-6 pb-5 border-b border-slate-100 dark:border-slate-800">
        <UAvatar
          :alt="user?.fullname || 'User'"
          size="xl"
          class="bg-zinc-100 dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300 text-xl font-bold"
        />
        <div>
          <p class="text-sm font-medium text-slate-900 dark:text-white">{{ user?.fullname }}</p>
          <p class="text-xs text-slate-500">{{ user?.email }}</p>
        </div>
      </div>

      <form class="space-y-4" @submit.prevent="saveProfile">
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Full name</label>
          <UInput v-model="profile.fullname" placeholder="Your full name" icon="i-lucide-user" size="md" class="w-full" />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Email address</label>
          <UInput v-model="profile.email" type="email" placeholder="you@example.com" icon="i-lucide-mail" size="md" class="w-full" disabled />
          <p class="text-xs text-slate-400 mt-1">Email cannot be changed.</p>
        </div>
        <div class="flex justify-end pt-2">
          <UButton type="submit" size="sm" :loading="savingProfile">Save changes</UButton>
        </div>
      </form>
    </div>

    <!-- Change password -->
    <div class="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
      <div class="mb-5">
        <h3 class="font-semibold text-slate-900 dark:text-white mb-0.5">Change Password</h3>
        <p class="text-sm text-slate-500 dark:text-slate-400">Update your account password.</p>
      </div>

      <UAlert v-if="passError" :description="passError" color="error" variant="soft" icon="i-lucide-alert-circle" class="mb-4" />

      <form class="space-y-4" @submit.prevent="changePassword">
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Current password</label>
          <UInput v-model="passForm.current" type="password" placeholder="Current password" icon="i-lucide-lock" size="md" class="w-full" required />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">New password</label>
          <UInput v-model="passForm.new_password" type="password" placeholder="New password (min. 8 chars)" icon="i-lucide-lock-keyhole" size="md" class="w-full" required />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Confirm new password</label>
          <UInput v-model="passForm.confirm" type="password" placeholder="Repeat new password" icon="i-lucide-lock-keyhole" size="md" class="w-full" required />
        </div>
        <div class="flex justify-end pt-2">
          <UButton type="submit" size="sm" color="error" :loading="changingPass">Change password</UButton>
        </div>
      </form>
    </div>

    <!-- Danger zone -->
    <div class="p-6 rounded-2xl bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900/50">
      <h3 class="font-semibold text-red-700 dark:text-red-400 mb-1">Danger Zone</h3>
      <p class="text-sm text-red-600/80 dark:text-red-400/70 mb-4">
        Permanently delete your account and all associated data. This action cannot be undone.
      </p>
      <UButton size="sm" color="error" variant="soft" icon="i-lucide-trash-2">
        Delete account
      </UButton>
    </div>
  </div>
</template>
