<script setup lang="ts">
definePageMeta({ layout: 'dashboard', middleware: 'auth' })

useSeoMeta({ title: 'Settings — Onyx' })

const { user, fetchMe } = useAuth()
const api = useApi()
const toast = useToast()
const route = useRoute()
const router = useRouter()

// Profile
const profile = reactive({
  fullname: user.value?.fullname || '',
  email: user.value?.email || ''
})
const savingProfile = ref(false)

watch(user, (val) => {
  if (val) {
    profile.fullname = val.fullname
    profile.email = val.email
  }
}, { immediate: true })

async function saveProfile() {
  savingProfile.value = true
  try {
    toast.add({ title: 'Profile updated', color: 'success' })
  } catch (e: any) {
    toast.add({ title: 'Error', description: e?.data?.detail || 'Update failed', color: 'error' })
  } finally {
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
      body: { current: passForm.current, new_password: passForm.new_password }
    })
    toast.add({ title: 'Password changed!', description: 'You will need to sign in again.', color: 'success' })
    Object.assign(passForm, { current: '', new_password: '', confirm: '' })
  } catch (e: any) {
    passError.value = e?.data?.detail || 'Password change failed.'
    toast.add({ title: 'Error', description: passError.value, color: 'error' })
  } finally {
    changingPass.value = false
  }
}

// Subscription & Tiers
const sub = computed(() => user.value?.current_subscription)
const tier = computed(() => sub.value?.tier)
const tiers = ref<any[]>([])
const loadingTiers = ref(false)
const subscribingTierId = ref<string | null>(null)
const showCancelModal = ref(false)
const cancellingSub = ref(false)

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-NG', { day: 'numeric', month: 'long', year: 'numeric' })
}

async function fetchTiers() {
  loadingTiers.value = true
  try {
    const res = await api<any[]>('/api/v1/client/tiers')
    tiers.value = res || []
  } catch (e: any) {
    toast.add({ title: 'Error', description: 'Failed to load subscription tiers.', color: 'error' })
  } finally {
    loadingTiers.value = false
  }
}

async function handleUpgrade(tierId: string) {
  subscribingTierId.value = tierId
  try {
    const res = await api<{ success: boolean, authorization_url?: string, message?: string }>('/api/v1/client/subscribe', {
      method: 'POST',
      body: {
        tier_id: tierId,
        callback_url: `${window.location.origin}/dashboard/settings`
      }
    })

    if (res.authorization_url) {
      window.location.href = res.authorization_url
      return
    }

    if (res.success) {
      await fetchMe()
      toast.add({ title: 'Subscription updated!', description: res.message || 'Plan activated', color: 'success' })
    }
  } catch (e: any) {
    toast.add({ title: 'Upgrade error', description: e?.data?.detail || 'Could not process subscription', color: 'error' })
  } finally {
    subscribingTierId.value = null
  }
}

async function cancelSubscription() {
  cancellingSub.value = true
  try {
    await api('/api/v1/client/cancel', { method: 'POST' })
    await fetchMe()
    showCancelModal.value = false
    toast.add({ title: 'Subscription cancelled', description: 'Your plan will remain active until its expiration date.', color: 'warning' })
  } catch (e: any) {
    toast.add({ title: 'Error', description: e?.data?.detail || 'Could not cancel subscription', color: 'error' })
  } finally {
    cancellingSub.value = false
  }
}

onMounted(async () => {
  await fetchTiers()

  // Auto-checkout if query param ?plan=tier_id exists
  const planParam = route.query.plan as string
  if (planParam) {
    // Clear query param from URL without page reload
    router.replace({ query: {} })
    await handleUpgrade(planParam)
  }
})
</script>

<template>
  <div class="max-w-4xl space-y-8">
    <!-- Subscription & Current Plan Card -->
    <div
      class="p-6 rounded-md border"
      :class="tier ? 'bg-zinc-900 text-white border-zinc-800' : 'bg-white dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800'"
    >
      <div class="flex items-start justify-between gap-4">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <UIcon
              name="i-lucide-zap"
              class="w-5 h-5 text-amber-400"
            />
            <h3 class="font-semibold text-lg">
              Current Subscription
            </h3>
          </div>
          <p class="text-sm text-zinc-400">
            Manage your active plan and billing status.
          </p>
        </div>
        <UBadge
          :color="sub?.status === 'active' ? 'success' : sub?.status === 'cancelled' ? 'warning' : 'neutral'"
          variant="solid"
          size="sm"
          class="capitalize"
        >
          {{ sub?.status ? sub.status.replace('_', ' ') : 'No Plan' }}
        </UBadge>
      </div>

      <div
        v-if="tier"
        class="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-3"
      >
        <div class="p-3.5 rounded-md bg-zinc-950/60 border border-zinc-800">
          <p class="text-xs text-zinc-400 mb-0.5">
            Active Tier
          </p>
          <p class="font-bold text-zinc-100">
            {{ tier.name }}
          </p>
        </div>
        <div class="p-3.5 rounded-md bg-zinc-950/60 border border-zinc-800">
          <p class="text-xs text-zinc-400 mb-0.5">
            Price
          </p>
          <p class="font-bold text-zinc-100">
            ₦{{ Number(tier.price).toLocaleString() }}/mo
          </p>
        </div>
        <div class="p-3.5 rounded-md bg-zinc-950/60 border border-zinc-800">
          <p class="text-xs text-zinc-400 mb-0.5">
            Max Short Links
          </p>
          <p class="font-bold text-zinc-100">
            {{ Number(tier.max_short_link).toLocaleString() }}
          </p>
        </div>
        <div
          v-if="sub?.expired_at"
          class="p-3.5 rounded-md bg-zinc-950/60 border border-zinc-800"
        >
          <p class="text-xs text-zinc-400 mb-0.5">
            Renews / Expires
          </p>
          <p class="font-bold text-zinc-100">
            {{ formatDate(sub.expired_at) }}
          </p>
        </div>
      </div>

      <div
        v-else
        class="mt-4 text-sm text-zinc-400"
      >
        You currently do not have an active subscription. Choose a plan below to unlock custom domains and extra features.
      </div>

      <!-- Action buttons -->
      <div
        v-if="sub && sub.status === 'active' && Number(tier?.price) > 0"
        class="mt-6 flex justify-end"
      >
        <UButton
          color="error"
          variant="soft"
          size="sm"
          icon="i-lucide-x-circle"
          @click="showCancelModal = true"
        >
          Cancel Subscription
        </UButton>
      </div>
    </div>

    <!-- Available Plans / Upgrade Grid -->
    <div>
      <div class="mb-4">
        <h3 class="text-lg font-bold text-slate-900 dark:text-white">
          Available Plans
        </h3>
        <p class="text-sm text-slate-500 dark:text-slate-400">
          Select a tier to upgrade your subscription using Paystack.
        </p>
      </div>

      <div
        v-if="loadingTiers"
        class="py-12 flex justify-center"
      >
        <UIcon
          name="i-lucide-loader-2"
          class="w-8 h-8 animate-spin text-zinc-500"
        />
      </div>

      <div
        v-else
        class="grid grid-cols-1 md:grid-cols-3 gap-4"
      >
        <div
          v-for="t in tiers"
          :key="t.tier_id"
          class="p-5 rounded-md border bg-white dark:bg-zinc-900 flex flex-col justify-between transition-all"
          :class="tier?.tier_id === t.tier_id ? 'border-zinc-900 dark:border-zinc-100 shadow-sm' : 'border-zinc-200 dark:border-zinc-800'"
        >
          <div>
            <div class="flex items-center justify-between mb-2">
              <h4 class="font-bold text-base text-slate-900 dark:text-white">
                {{ t.name }}
              </h4>
              <UBadge
                v-if="tier?.tier_id === t.tier_id"
                color="primary"
                variant="soft"
                size="xs"
              >
                Current
              </UBadge>
            </div>
            <p class="text-2xl font-extrabold text-slate-900 dark:text-white mb-3">
              ₦{{ Number(t.price).toLocaleString() }}<span class="text-xs font-normal text-slate-500">/mo</span>
            </p>
            <p
              v-if="t.description"
              class="text-xs text-slate-500 dark:text-slate-400 mb-4"
            >
              {{ t.description }}
            </p>

            <ul class="space-y-2 text-xs text-slate-600 dark:text-slate-300 mb-6">
              <li class="flex items-center gap-2">
                <UIcon
                  name="i-lucide-check"
                  class="w-4 h-4 text-emerald-500 shrink-0"
                />
                <span>{{ t.max_short_link }} Short Links</span>
              </li>
              <li class="flex items-center gap-2">
                <UIcon
                  name="i-lucide-check"
                  class="w-4 h-4 text-emerald-500 shrink-0"
                />
                <span>{{ t.max_custom_domains }} Custom Domains</span>
              </li>
              <li class="flex items-center gap-2">
                <UIcon
                  name="i-lucide-check"
                  class="w-4 h-4 text-emerald-500 shrink-0"
                />
                <span>{{ t.max_onyx_subdomains }} Subdomains</span>
              </li>
            </ul>
          </div>

          <UButton
            block
            size="md"
            :color="tier?.tier_id === t.tier_id ? 'neutral' : 'primary'"
            :variant="tier?.tier_id === t.tier_id ? 'outline' : 'solid'"
            :loading="subscribingTierId === t.tier_id"
            :disabled="tier?.tier_id === t.tier_id"
            @click="handleUpgrade(t.tier_id)"
          >
            {{ tier?.tier_id === t.tier_id ? 'Current Plan' : Number(t.price) === 0 ? 'Activate Free' : 'Upgrade' }}
          </UButton>
        </div>
      </div>
    </div>

    <!-- Profile Form -->
    <div class="p-6 rounded-md bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800">
      <div class="mb-5">
        <h3 class="font-semibold text-slate-900 dark:text-white mb-0.5">
          Profile Details
        </h3>
        <p class="text-sm text-slate-500 dark:text-slate-400">
          View and update your personal information.
        </p>
      </div>

      <div class="flex items-center gap-4 mb-6 pb-5 border-b border-zinc-100 dark:border-zinc-800">
        <UAvatar
          :alt="user?.fullname || 'User'"
          size="lg"
          class="bg-zinc-200 dark:bg-zinc-800 text-zinc-800 dark:text-zinc-200 font-bold"
        />
        <div>
          <p class="text-sm font-semibold text-slate-900 dark:text-white">
            {{ user?.fullname }}
          </p>
          <p class="text-xs text-slate-500">
            {{ user?.email }}
          </p>
        </div>
      </div>

      <form
        class="space-y-4"
        @submit.prevent="saveProfile"
      >
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Full name</label>
          <UInput
            v-model="profile.fullname"
            placeholder="Your full name"
            icon="i-lucide-user"
            size="md"
            class="w-full"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Email address</label>
          <UInput
            v-model="profile.email"
            type="email"
            icon="i-lucide-mail"
            size="md"
            class="w-full"
            disabled
          />
        </div>
        <div class="flex justify-end pt-2">
          <UButton
            type="submit"
            size="sm"
            :loading="savingProfile"
          >
            Save changes
          </UButton>
        </div>
      </form>
    </div>

    <!-- Password Change Form -->
    <div class="p-6 rounded-md bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800">
      <div class="mb-5">
        <h3 class="font-semibold text-slate-900 dark:text-white mb-0.5">
          Change Password
        </h3>
        <p class="text-sm text-slate-500 dark:text-slate-400">
          Update your account password securely.
        </p>
      </div>

      <UAlert
        v-if="passError"
        :description="passError"
        color="error"
        variant="soft"
        icon="i-lucide-alert-circle"
        class="mb-4"
      />

      <form
        class="space-y-4"
        @submit.prevent="changePassword"
      >
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Current password</label>
          <UInput
            v-model="passForm.current"
            type="password"
            icon="i-lucide-lock"
            size="md"
            class="w-full"
            required
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">New password</label>
          <UInput
            v-model="passForm.new_password"
            type="password"
            icon="i-lucide-lock-keyhole"
            size="md"
            class="w-full"
            required
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Confirm new password</label>
          <UInput
            v-model="passForm.confirm"
            type="password"
            icon="i-lucide-lock-keyhole"
            size="md"
            class="w-full"
            required
          />
        </div>
        <div class="flex justify-end pt-2">
          <UButton
            type="submit"
            size="sm"
            color="error"
            :loading="changingPass"
          >
            Change password
          </UButton>
        </div>
      </form>
    </div>

    <!-- Cancel Confirmation Modal -->
    <UModal
      v-model:open="showCancelModal"
      title="Cancel Subscription?"
      description="Are you sure you want to cancel your current subscription?"
    >
      <template #body>
        <p class="text-sm text-slate-600 dark:text-slate-300">
          Your plan will be marked as cancelled. You will continue to have access to your tier features until <strong>{{ sub?.expired_at ? formatDate(sub.expired_at) : 'the end of your billing cycle' }}</strong>.
        </p>
      </template>

      <template #footer>
        <div class="flex justify-end gap-2">
          <UButton
            color="neutral"
            variant="ghost"
            @click="showCancelModal = false"
          >
            Keep Plan
          </UButton>
          <UButton
            color="error"
            :loading="cancellingSub"
            @click="cancelSubscription"
          >
            Confirm Cancel
          </UButton>
        </div>
      </template>
    </UModal>
  </div>
</template>
