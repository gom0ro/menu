import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

type ThemeMode = 'light' | 'dark' | 'auto'

export const useThemeStore = defineStore('theme', () => {
  const mode = ref<ThemeMode>((localStorage.getItem('theme-mode') as ThemeMode) || 'auto')
  const isDark = ref(false)

  function getAutoDark(): boolean {
    const hour = new Date().getHours()
    return hour >= 20 || hour < 7
  }

  function apply() {
    const dark = mode.value === 'dark' || (mode.value === 'auto' && getAutoDark())
    isDark.value = dark
    document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light')
    const meta = document.querySelector('meta[name="theme-color"]')
    if (meta) meta.setAttribute('content', dark ? '#0a0a0a' : '#ffffff')
  }

  function setMode(m: ThemeMode) {
    mode.value = m
    localStorage.setItem('theme-mode', m)
    apply()
  }

  function toggle() {
    setMode(isDark.value ? 'light' : 'dark')
  }

  watch(mode, apply, { immediate: true })

  // Re-check auto theme every minute
  setInterval(() => {
    if (mode.value === 'auto') apply()
  }, 60_000)

  return { mode, isDark, setMode, toggle, apply }
})
