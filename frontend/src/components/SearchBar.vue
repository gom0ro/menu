<script setup lang="ts">
defineProps<{ modelValue: string }>()
defineEmits<{ 'update:modelValue': [value: string] }>()
</script>

<template>
  <div class="search">
    <svg class="search__icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
    </svg>
    <input
      :value="modelValue"
      type="search"
      placeholder="Поиск блюд..."
      class="search__input"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
  </div>
</template>

<style scoped>
.search {
  position: relative;
  max-width: 400px;
  width: 100%;
}

.search__icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-muted);
  pointer-events: none;
}

.search__input {
  width: 100%;
  padding: 12px 16px 12px 44px;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text);
  border-radius: var(--radius-sm);
  transition: border-color var(--transition-fast);
}

.search__input:focus {
  outline: none;
  border-color: var(--color-text);
}

.search__input::placeholder {
  color: var(--color-text-muted);
}
</style>
