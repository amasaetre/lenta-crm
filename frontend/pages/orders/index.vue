<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; flex-wrap: wrap; gap: 1rem;">
      <h2>Список интернет-заказов</h2>
      <NuxtLink to="/orders/new" class="btn">
        + Создать заказ
      </NuxtLink>
    </div>

    <div v-if="orders && orders.length > 0" class="card" style="margin-bottom: 2rem;">
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
        <div class="form-group" style="margin-bottom: 0;">
          <label for="search">Поиск по клиенту</label>
          <input
            id="search"
            v-model="searchQuery"
            type="text"
            placeholder="Введите имя клиента..."
            style="width: 100%;"
          />
        </div>
        <div class="form-group" style="margin-bottom: 0;">
          <label for="status-filter">Фильтр по статусу</label>
          <select
            id="status-filter"
            v-model="statusFilter"
            style="width: 100%;"
          >
            <option value="">Все статусы</option>
            <option value="новый">новый</option>
            <option value="в обработке">в обработке</option>
            <option value="выполнен">выполнен</option>
            <option value="отменен">отменен</option>
          </select>
        </div>
        <div style="display: flex; align-items: end;">
          <button
            v-if="searchQuery || statusFilter"
            @click="clearFilters"
            class="btn btn-secondary"
            style="width: 100%;"
          >
            Сбросить фильтры
          </button>
        </div>
      </div>
      <div v-if="filteredOrders.length !== orders.length" style="margin-top: 1rem; color: var(--lenta-text-light);">
        Показано {{ filteredOrders.length }} из {{ orders.length }} заказов
      </div>
    </div>

    <div v-if="pending" class="loading">
      Загрузка заказов...
    </div>

    <div v-else-if="error" class="card" style="background-color: #FFEBEE; color: #D32F2F;">
      Ошибка загрузки заказов: {{ error.message }}
    </div>

    <div v-else-if="orders && orders.length === 0" class="empty-state">
      <p>Заказов пока нет</p>
      <NuxtLink to="/orders/new" class="btn" style="margin-top: 1rem;">
        Создать первый заказ
      </NuxtLink>
    </div>

    <div v-else-if="filteredOrders.length === 0" class="empty-state">
      <p>Заказы не найдены по заданным критериям</p>
      <button @click="clearFilters" class="btn" style="margin-top: 1rem;">
        Сбросить фильтры
      </button>
    </div>

    <div v-else class="table-container">
      <table>
        <thead>
          <tr>
            <th>Номер заказа</th>
            <th>Дата оформления</th>
            <th>Клиент</th>
            <th>Общая сумма</th>
            <th>Статус</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in filteredOrders" :key="order.id">
            <td>#{{ order.id }}</td>
            <td>{{ formatDate(order.created_at) }}</td>
            <td>{{ order.customer_name }}</td>
            <td>{{ formatPrice(order.total_amount) }} ₽</td>
            <td>
              <span :class="`status-badge status-${getStatusClass(order.status)}`">
                {{ order.status }}
              </span>
            </td>
            <td>
              <NuxtLink :to="`/orders/${order.id}`" class="link">
                Просмотр
              </NuxtLink>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const { data: orders, pending, error } = await useFetch(`${apiBase}/api/orders`)

const searchQuery = ref('')
const statusFilter = ref('')

const filteredOrders = computed(() => {
  if (!orders.value) return []
  
  let result = orders.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(order => 
      order.customer_name.toLowerCase().includes(query) ||
      order.id.toString().includes(query)
    )
  }
  
  if (statusFilter.value) {
    result = result.filter(order => order.status === statusFilter.value)
  }
  
  return result
})

function clearFilters() {
  searchQuery.value = ''
  statusFilter.value = ''
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleString('ru-RU', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatPrice(price) {
  return new Intl.NumberFormat('ru-RU', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(price)
}

function getStatusClass(status) {
  const statusMap = {
    'новый': 'new',
    'в обработке': 'processing',
    'выполнен': 'completed',
    'отменен': 'cancelled'
  }
  return statusMap[status.toLowerCase()] || 'new'
}

useHead({
  title: 'Заказы — Система учета интернет-заказов'
})
</script>

