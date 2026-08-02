<template>
  <NuxtLink to="/" class="flex items-center gap-2 group" aria-label="Onyx Home">
    <div class="relative flex items-center justify-center w-8 h-8">
      <div class="absolute inset-0 bg-zinc-600 rounded-lg rotate-45 group-hover:rotate-[55deg] transition-transform duration-300" />
      <svg
        class="relative z-10 w-4 h-4 text-white"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M13.5 3L4.5 12.5L10.5 12.5L10.5 21L19.5 11.5L13.5 11.5L13.5 3Z"
          fill="currentColor"
        />
      </svg>
    </div>
    <span class="text-xl font-bold tracking-tight text-slate-900 dark:text-white">
      on<span class="text-zinc-600">yx</span>
    </span>
  </NuxtLink>
</template>
