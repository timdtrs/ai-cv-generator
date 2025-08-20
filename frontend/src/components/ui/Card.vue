<template>
  <div v-bind="$attrs" :class="wrapperClasses">
    <div v-if="$slots.header" class="px-5 pt-4 pb-2">
      <slot name="header" />
    </div>
    <div class="px-5 pb-4">
      <slot />
    </div>
    <div v-if="$slots.footer" class="px-5 py-3 border-t border-zinc-800/80">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  padded: { type: Boolean, default: true },
  variant: {
    type: String,
    default: 'default',
    validator: (v) => ['default', 'accent'].includes(v),
  },
})

const base = 'min-w-0 rounded-xl border backdrop-blur-sm shadow-sm'
const variants = {
  default: 'border-zinc-800/80 bg-zinc-900/60',
  accent: 'border-primary/40 bg-primary/10 ring-1 ring-primary/30 shadow-primary/20',
}

const wrapperClasses = computed(() => [base, variants[props.variant] || variants.default])
</script>
