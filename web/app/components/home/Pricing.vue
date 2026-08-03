<script setup lang="ts">
import { availablePermissions } from '~/libs/permission'

const api = useApi()
const tiers = ref<any[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await api('/api/v1/client/subscription/pricings')
    if (Array.isArray(res)) {
      tiers.value = res
    }
  } catch (err) {
    console.error('Failed to fetch pricing tiers:', err)
  } finally {
    loading.value = false
  }
})

function hasPermission(tier: any, permValue: string): boolean {
  if (!tier?.permissions || !Array.isArray(tier.permissions)) return false
  return tier.permissions.includes(permValue)
}

function formatPrice(price: number | string): string {
  const num = Number(price)
  if (isNaN(num) || num <= 0) return '₦0'
  return `₦${num.toLocaleString()}`
}
</script>

<template>
  <section
    v-if="!loading && tiers.length > 0"
    id="pricing"
    class="py-24 px-4 sm:px-6 bg-slate-50 dark:bg-slate-950"
  >
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-16">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-100 dark:bg-zinc-950/50 text-zinc-700 dark:text-zinc-300 text-sm font-medium mb-4">
          <UIcon
            name="i-lucide-tag"
            class="w-4 h-4"
          />
          Simple pricing
        </div>
        <h2 class="text-4xl sm:text-5xl font-bold text-slate-900 dark:text-white mb-4">
          Start free, scale as you<br>
          <span class="gradient-text">grow</span>
        </h2>
        <p class="text-lg text-slate-500 dark:text-slate-400">
          No hidden fees. Cancel anytime. Upgrade whenever you're ready.
        </p>
      </div>

      <!-- Plans grid -->
      <div
        class="grid grid-cols-1 gap-8 items-start"
        :class="tiers.length === 1 ? 'max-w-md mx-auto grid-cols-1' : tiers.length === 2 ? 'max-w-4xl mx-auto md:grid-cols-2' : 'md:grid-cols-3'"
      >
        <div
          v-for="tier in tiers"
          :key="tier.id || tier.name"
          class="relative flex flex-col rounded-2xl border transition-all duration-300 bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-zinc-300 dark:hover:border-zinc-700 hover:shadow-lg"
        >
          <div class="p-8 flex flex-col flex-1">
            <!-- Plan name & price -->
            <div class="mb-6">
              <h3 class="text-xl font-bold mb-1 text-slate-900 dark:text-white capitalize">
                {{ tier.name }}
              </h3>
              <p class="text-sm mb-4 text-slate-500 dark:text-slate-400 min-h-[2.5rem]">
                {{ tier.description || 'Flexible plan tailored for your needs.' }}
              </p>
              <div class="flex items-baseline gap-1">
                <span class="text-4xl font-extrabold text-slate-900 dark:text-white">
                  {{ formatPrice(tier.price) }}
                </span>
                <span class="text-sm text-slate-400">
                  {{ Number(tier.price) <= 0 ? 'forever' : '/month' }}
                </span>
              </div>
            </div>

            <!-- CTA button -->
            <NuxtLink
              :to="`/signup?plan=${tier.name}`"
              class="mb-8"
            >
              <UButton
                block
                size="lg"
                class="rounded-xl"
                color="primary"
                variant="solid"
              >
                {{ Number(tier.price) <= 0 ? 'Get started free' : `Choose ${tier.name}` }}
              </UButton>
            </NuxtLink>

            <!-- Feature list -->
            <ul class="space-y-3 flex-1 border-t border-slate-100 dark:border-slate-800/80 pt-6">
              <li
                v-for="perm in availablePermissions"
                :key="perm.value"
                class="flex items-center gap-2.5 text-sm"
              >
                <UIcon
                  v-if="hasPermission(tier, perm.value)"
                  name="i-lucide-check"
                  class="w-4 h-4 shrink-0 text-emerald-500"
                />
                <UIcon
                  v-else
                  name="i-lucide-minus"
                  class="w-4 h-4 shrink-0 text-zinc-400 dark:text-zinc-600"
                />
                <span :class="hasPermission(tier, perm.value) ? 'text-slate-700 dark:text-slate-300 font-medium' : 'text-slate-400 dark:text-slate-600 line-through opacity-70'">
                  {{ perm.label }}
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Money-back note -->
      <p class="text-center text-sm text-slate-500 dark:text-slate-400 mt-10">
        <UIcon
          name="i-lucide-shield-check"
          class="w-4 h-4 inline-block mr-1 text-emerald-500"
        />
        All paid plans come with a 14-day money-back guarantee. Powered by Paystack.
      </p>
    </div>
  </section>
</template>
