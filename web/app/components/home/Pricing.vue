<script setup lang="ts">
const plans = [
  {
    name: 'Free',
    price: '₦0',
    period: 'forever',
    description: 'Perfect for personal projects and getting started.',
    badge: null,
    cta: 'Get started free',
    ctaTo: '/signup',
    popular: false,
    features: [
      '5 short links',
      'Basic analytics',
      'Default domain only',
      'Link expiration',
      '500 clicks/month per link'
    ],
    missing: ['Custom domains', 'Custom paths', 'QR codes', 'API access']
  },
  {
    name: 'Pro',
    price: '₦5,000',
    period: '/month',
    description: 'For creators and small teams who need more power.',
    badge: 'Most Popular',
    cta: 'Start Pro',
    ctaTo: '/signup?plan=pro',
    popular: true,
    features: [
      '500 short links',
      'Advanced analytics',
      '3 custom domains',
      '50 Onyx subdomains',
      'Custom paths/slugs',
      'QR code generator',
      '50,000 clicks/month'
    ],
    missing: ['API access', 'SDK']
  },
  {
    name: 'Enterprise',
    price: '₦25,000',
    period: '/month',
    description: 'For growing businesses with advanced needs.',
    badge: 'Best Value',
    cta: 'Get Enterprise',
    ctaTo: '/signup?plan=enterprise',
    popular: false,
    features: [
      'Unlimited short links',
      'Full analytics + AI insights',
      'Unlimited custom domains',
      'Unlimited Onyx subdomains',
      'Unlimited custom paths',
      'QR code generator',
      'REST API access',
      'SDK integration',
      'Priority support'
    ],
    missing: []
  }
]
</script>

<template>
  <section
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
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
        <div
          v-for="plan in plans"
          :key="plan.name"
          class="relative flex flex-col rounded-2xl border transition-all duration-300"
          :class="plan.popular
            ? 'bg-zinc-600 border-zinc-500 shadow-2xl shadow-zinc-500/30 scale-105'
            : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-zinc-300 dark:hover:border-zinc-700 hover:shadow-lg'"
        >
          <!-- Popular badge -->
          <div
            v-if="plan.badge"
            class="absolute -top-4 left-1/2 -translate-x-1/2"
          >
            <span
              class="px-4 py-1 text-xs font-bold rounded-full uppercase tracking-widest"
              :class="plan.popular ? 'bg-white text-zinc-700' : 'bg-zinc-100 dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300'"
            >
              {{ plan.badge }}
            </span>
          </div>

          <div class="p-8 flex flex-col flex-1">
            <!-- Plan name & price -->
            <div class="mb-6">
              <h3
                class="text-lg font-bold mb-1"
                :class="plan.popular ? 'text-white' : 'text-slate-900 dark:text-white'"
              >
                {{ plan.name }}
              </h3>
              <p
                class="text-sm mb-4"
                :class="plan.popular ? 'text-zinc-200' : 'text-slate-500 dark:text-slate-400'"
              >
                {{ plan.description }}
              </p>
              <div class="flex items-baseline gap-1">
                <span
                  class="text-4xl font-extrabold"
                  :class="plan.popular ? 'text-white' : 'text-slate-900 dark:text-white'"
                >
                  {{ plan.price }}
                </span>
                <span
                  class="text-sm"
                  :class="plan.popular ? 'text-zinc-200' : 'text-slate-400'"
                >
                  {{ plan.period }}
                </span>
              </div>
            </div>

            <!-- CTA button -->
            <NuxtLink
              :to="plan.ctaTo"
              class="mb-8"
            >
              <UButton
                block
                size="lg"
                class="rounded-xl"
                :color="plan.popular ? 'neutral' : 'primary'"
                :variant="plan.popular ? 'solid' : 'solid'"
              >
                {{ plan.cta }}
              </UButton>
            </NuxtLink>

            <!-- Feature list -->
            <ul class="space-y-3 flex-1">
              <li
                v-for="feat in plan.features"
                :key="feat"
                class="flex items-center gap-2.5 text-sm"
                :class="plan.popular ? 'text-zinc-100' : 'text-slate-700 dark:text-slate-300'"
              >
                <UIcon
                  name="i-lucide-check"
                  class="w-4 h-4 shrink-0"
                  :class="plan.popular ? 'text-zinc-200' : 'text-zinc-600 dark:text-zinc-400'"
                />
                {{ feat }}
              </li>
              <li
                v-for="feat in plan.missing"
                :key="feat"
                class="flex items-center gap-2.5 text-sm"
                :class="plan.popular ? 'text-zinc-300/60' : 'text-slate-400 dark:text-slate-600'"
              >
                <UIcon
                  name="i-lucide-minus"
                  class="w-4 h-4 shrink-0"
                />
                {{ feat }}
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
