<script setup lang="ts">
const props = withDefaults(defineProps<{
  permission: string
  label: string
  icon?: string
  color?: 'primary' | 'neutral' | 'error' | 'success' | 'warning'
  size?: 'xs' | 'sm' | 'md' | 'lg'
  variant?: 'solid' | 'outline' | 'soft' | 'subtle' | 'ghost' | 'link'
  block?: boolean
}>(), {
  color: 'neutral',
  size: 'md',
  variant: 'solid',
  block: false,
})

const emit = defineEmits<{
  (e: 'click', evt: MouseEvent): void
}>()

const { user } = useAuth()
const router = useRouter()

const userPermissions = computed<string[]>(() => {
  return [...(user.value?.current_subscription?.tier?.permissions || [])]
})

const isSubActive = computed(() => {
  const sub = user.value?.current_subscription
  if (!sub) return false
  if (sub.status !== 'active') return false
  if (!sub.expired_at) return false
  return new Date(sub.expired_at).getTime() > Date.now()
})

const hasPermission = computed(() => {
  if (!isSubActive.value) return false
  return userPermissions.value.includes(props.permission)
})

function handleLockedClick() {
  router.push('/dashboard/settings')
}
</script>

<template>
  <div v-if="!hasPermission" class="inline-block relative group">
    <UButton
      :color="color"
      :variant="variant"
      :size="size"
      :block="block"
      disabled
      class="opacity-60 cursor-not-allowed border-dashed border-amber-300 dark:border-amber-700/60"
      @click="handleLockedClick"
    >
      <template #leading>
        <UIcon name="i-lucide-lock" class="w-4 h-4 text-amber-500 shrink-0" />
      </template>
      <span>{{ label }}</span>
    </UButton>

    <!-- Hover tooltip -->
    <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:flex flex-col items-center z-50 pointer-events-none">
      <div class="bg-zinc-900 dark:bg-zinc-100 text-zinc-100 dark:text-zinc-900 text-xs font-semibold px-2.5 py-1.5 rounded-md shadow-lg whitespace-nowrap flex items-center gap-1.5">
        <UIcon name="i-lucide-zap" class="w-3.5 h-3.5 text-amber-400 dark:text-amber-600" />
        <span>Upgrade plan to access</span>
      </div>
      <div class="w-2 h-2 bg-zinc-900 dark:bg-zinc-100 rotate-45 -mt-1" />
    </div>
  </div>

  <UButton
    v-else
    :color="color"
    :variant="variant"
    :size="size"
    :block="block"
    :icon="icon"
    @click="emit('click', $event)"
  >
    {{ label }}
  </UButton>
</template>
