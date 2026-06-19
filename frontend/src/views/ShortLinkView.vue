<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

onMounted(async () => {
  const code = route.params.code as string
  try {
    const res = await fetch(`/api/resolve/${code}`)
    if (!res.ok) throw new Error()
    const { slug } = await res.json()
    router.replace({ name: 'menu', params: { slug } })
  } catch {
    router.replace('/')
  }
})
</script>

<template>
  <div class="loading">
    <div class="skeleton skeleton--text" />
  </div>
</template>

<style scoped>
.loading {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
.skeleton--text {
  width: 200px;
  height: 20px;
}
</style>
