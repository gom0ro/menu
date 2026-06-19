<template>
  <div class="not-found">
    <h1>404</h1>
    <p>Страница не найдена</p>
    <router-link to="/menu/la-maison">Вернуться в меню</router-link>
  </div>
</template>

<style scoped>
.not-found {
  min-height: 80vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.not-found h1 {
  font-size: 4rem;
  font-weight: 300;
}

.not-found a {
  margin-top: 16px;
  padding: 12px 32px;
  border: 1px solid var(--color-text);
  font-size: 11px;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  transition: all var(--transition-fast);
}

.not-found a:hover {
  background: var(--color-text);
  color: var(--color-bg);
}
</style>
