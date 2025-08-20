<template>
  <component
    :is="as || 'button'"
    :class="computedClasses"
    v-bind="$attrs"
  >
    <slot />
  </component>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  as: { type: [String, Object], default: 'button' },
  variant: {
    type: String,
    default: 'default',
    validator: (v) => ['default', 'secondary', 'outline', 'ghost'].includes(v),
  },
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['sm', 'md', 'lg'].includes(v),
  },
})

const base =
  'inline-flex items-center justify-center whitespace-nowrap rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 disabled:opacity-50 disabled:pointer-events-none'

const sizes = {
  sm: 'h-8 px-3 text-sm',
  md: 'h-9 px-4 text-sm',
  lg: 'h-10 px-5 text-base',
}

const variants = {
  default: 'bg-primary text-white shadow hover:bg-primary/90',
  secondary: 'bg-zinc-800 text-zinc-100 hover:bg-zinc-700',
  outline: 'border border-zinc-700 bg-transparent hover:bg-zinc-800/40',
  ghost: 'bg-transparent hover:bg-zinc-800/40',
}

const computedClasses = computed(() => {
  return [base, sizes[props.size], variants[props.variant]].join(' ')
})
</script>

