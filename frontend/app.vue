<template>
  <div>
    <header class="header">
      <div class="container">
        <div class="header-content">
          <h1>Информационная система учета интернет-заказов</h1>
          <nav class="nav">
            <NuxtLink to="/">Главная</NuxtLink>
            <NuxtLink to="/orders">Заказы</NuxtLink>
          </nav>
        </div>
      </div>
    </header>

    <main class="main-content">
      <div class="container">
        <NuxtPage />
      </div>
    </main>

    <footer class="footer">
      <div class="container">
        <p>Торговая сеть «Лента» — Система учета интернет-заказов</p>
      </div>
    </footer>
  </div>
</template>

