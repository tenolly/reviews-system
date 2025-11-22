<template>
  <div class="not-found container">
    <section class="card">
      <h1>Страница не найдена</h1>
      <p>Такой страницы нет. Воспользуйтесь навигацией или вернитесь на главную.</p>
      <router-link class="btn primary" to="/">На главную</router-link>
    </section>
  </div>
</template>

<style scoped>
.not-found {
  display: flex;
  justify-content: center;
  padding-top: 64px;
}

.card {
  width: min(420px, 100%);
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 40px;
}

.card .btn.primary {
  align-self: center;
}
</style>
