<template>
  <div class="skeleton-grid">
    <div v-for="n in 8" :key="n" class="skeleton-card">
      <div class="skeleton skeleton-card__image" />
      <div class="skeleton skeleton-card__title" />
      <div class="skeleton skeleton-card__desc" />
      <div class="skeleton skeleton-card__price" />
    </div>
  </div>
</template>

<style scoped>
.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: var(--spacing-lg);
}

.skeleton-card__image {
  aspect-ratio: 4/5;
  margin-bottom: var(--spacing-sm);
}

.skeleton-card__title {
  height: 20px;
  width: 70%;
  margin-bottom: 8px;
}

.skeleton-card__desc {
  height: 14px;
  width: 90%;
  margin-bottom: 12px;
}

.skeleton-card__price {
  height: 16px;
  width: 40%;
}
</style>
