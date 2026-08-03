<script setup lang="ts">
const faqs = [
  {
    label: 'Can I use my own domain with Onyx?',
    content: 'Yes! On Pro and Enterprise plans you can connect your own custom domain. Simply add a CNAME record and complete TXT verification — we walk you through the whole process.'
  },
  {
    label: 'How does link expiration work?',
    content: 'Each link you create automatically expires after a set number of days based on your subscription tier\'s link durability setting. You can also set a custom expiration date — it will be capped at your tier\'s maximum.'
  },
  {
    label: 'Is there a free plan?',
    content: 'Absolutely. The Free plan gives you 5 active short links, basic analytics, and access to our default Onyx domain. No credit card required.'
  },
  {
    label: 'How is billing handled?',
    content: 'Billing is powered by Paystack. We support all major Nigerian debit and credit cards. Subscriptions are billed monthly and auto-renew until cancelled.'
  },
  {
    label: 'Can I access Onyx via API?',
    content: 'Yes — API access is available on the Enterprise plan. Full REST API documentation and SDK support are included.'
  },
  {
    label: 'What happens to my links if I downgrade?',
    content: 'Existing links remain active, but you won\'t be able to create new links beyond your new plan\'s quota. Custom domain links using domains not on the free plan will be deactivated.'
  }
]
</script>

<template>
  <section
    id="faq"
    class="py-24 px-4 sm:px-6"
  >
    <div class="max-w-3xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-12">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-100 dark:bg-zinc-950/50 text-zinc-700 dark:text-zinc-300 text-sm font-medium mb-4">
          <UIcon
            name="i-lucide-help-circle"
            class="w-4 h-4"
          />
          FAQ
        </div>
        <h2 class="text-4xl font-bold text-slate-900 dark:text-white mb-3">
          Frequently asked<br><span class="gradient-text">questions</span>
        </h2>
        <p class="text-slate-500 dark:text-slate-400">
          Can't find your answer? <NuxtLink
            to="mailto:hello@onyx.com"
            class="text-zinc-600 underline"
          >Contact us</NuxtLink>.
        </p>
      </div>

      <!-- Accordion -->
      <UAccordion
        :items="faqs"
        class="divide-y divide-slate-200 dark:divide-slate-800"
      />

      <!-- CTA at bottom -->
      <div class="mt-12 p-8 rounded-2xl bg-linear-to-br from-zinc-600 to-indigo-600 text-center">
        <h3 class="text-2xl font-bold text-white mb-2">
          Ready to get started?
        </h3>
        <p class="text-zinc-200 mb-6">
          Join thousands of teams already using Onyx.
        </p>
        <div class="flex flex-col sm:flex-row gap-3 justify-center">
          <NuxtLink to="/signup">
            <UButton
              size="lg"
              color="neutral"
              class="rounded-xl"
            >
              Start for free
            </UButton>
          </NuxtLink>
          <NuxtLink to="/#pricing">
            <UButton
              size="lg"
              color="neutral"
              variant="ghost"
              class="rounded-xl text-white border-white/30 hover:bg-white/10"
            >
              View pricing
            </UButton>
          </NuxtLink>
        </div>
      </div>
    </div>
  </section>
</template>
