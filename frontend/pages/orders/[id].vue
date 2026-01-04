<template>
  <div>
    <div style="margin-bottom: 2rem;">
      <NuxtLink to="/orders" class="link">← Назад к списку заказов</NuxtLink>
    </div>

    <div v-if="pending" class="loading">
      Загрузка заказа...
    </div>

    <div v-else-if="error" class="card" style="background-color: #FFEBEE; color: #D32F2F;">
      Ошибка загрузки заказа: {{ error.message }}
    </div>

    <div v-else-if="order" class="card">
      <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 2rem; flex-wrap: wrap; gap: 1rem;">
        <div>
          <h2>Заказ #{{ order.id }}</h2>
          <p style="color: var(--lenta-text-light); margin-top: 0.5rem;">
            Дата оформления: {{ formatDate(order.created_at) }}
          </p>
        </div>
        <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
          <span :class="`status-badge status-${getStatusClass(order.status)}`" style="font-size: 1rem;">
            {{ order.status }}
          </span>
          <div style="display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap;">
            <label for="status-select" style="font-weight: 500;">Изменить статус:</label>
            <select
              id="status-select"
              :value="order.status"
              @change="updateStatus"
              :disabled="isUpdating"
              style="padding: 0.5rem; border: 1px solid var(--lenta-border); border-radius: 4px; font-size: 0.9rem;"
            >
              <option value="новый">новый</option>
              <option value="в обработке">в обработке</option>
              <option value="выполнен">выполнен</option>
              <option value="отменен">отменен</option>
            </select>
          </div>
          <div v-if="statusUpdateMessage" style="padding: 0.5rem 1rem; background-color: #E8F5E9; color: #388E3C; border-radius: 4px; font-size: 0.9rem;">
            {{ statusUpdateMessage }}
          </div>
        </div>
      </div>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; margin-bottom: 2rem;">
        <div>
          <h3 style="margin-bottom: 0.5rem; color: var(--lenta-text-light); font-size: 0.9rem; text-transform: uppercase;">Клиент</h3>
          <p style="font-size: 1.25rem; font-weight: 600;">{{ order.customer_name }}</p>
        </div>
        <div>
          <h3 style="margin-bottom: 0.5rem; color: var(--lenta-text-light); font-size: 0.9rem; text-transform: uppercase;">Количество позиций</h3>
          <p style="font-size: 1.25rem; font-weight: 600;">{{ order.items.length }} {{ getItemsWord(order.items.length) }}</p>
        </div>
        <div>
          <h3 style="margin-bottom: 0.5rem; color: var(--lenta-text-light); font-size: 0.9rem; text-transform: uppercase;">Итоговая сумма</h3>
          <p style="font-size: 1.5rem; font-weight: 600; color: var(--lenta-blue);">{{ formatPrice(order.total_amount) }} ₽</p>
        </div>
      </div>

      <div>
        <h3 style="margin-bottom: 1rem;">Состав заказа</h3>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>№</th>
                <th>Товар</th>
                <th style="text-align: center;">Количество</th>
                <th style="text-align: right;">Цена за ед.</th>
                <th style="text-align: right;">Сумма</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in order.items" :key="item.id">
                <td>{{ index + 1 }}</td>
                <td style="font-weight: 500;">{{ item.product_name }}</td>
                <td style="text-align: center;">{{ item.quantity }} шт.</td>
                <td style="text-align: right;">{{ formatPrice(item.price) }} ₽</td>
                <td style="text-align: right; font-weight: 600; color: var(--lenta-blue);">
                  {{ formatPrice(item.total) }} ₽
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="order-total">
          <span>Итого:</span>
          <span style="color: var(--lenta-blue);">
            {{ formatPrice(order.total_amount) }} ₽
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const route = useRoute()
const router = useRouter()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const orderId = route.params.id
const isUpdating = ref(false)

const { data: order, pending, error, refresh } = await useFetch(`${apiBase}/api/orders/${orderId}`)

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

function getItemsWord(count) {
  const lastDigit = count % 10
  const lastTwoDigits = count % 100
  
  if (lastTwoDigits >= 11 && lastTwoDigits <= 19) {
    return 'позиций'
  }
  if (lastDigit === 1) {
    return 'позиция'
  }
  if (lastDigit >= 2 && lastDigit <= 4) {
    return 'позиции'
  }
  return 'позиций'
}

const statusUpdateMessage = ref('')

async function updateStatus(event) {
  const newStatus = event.target.value
  if (newStatus === order.value.status) return
  
  isUpdating.value = true
  statusUpdateMessage.value = ''
  
  try {
    const response = await fetch(`${apiBase}/api/orders/${orderId}/status`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ status: newStatus })
    })
    
    if (!response.ok) {
      throw new Error('Ошибка при обновлении статуса')
    }
    
    statusUpdateMessage.value = 'Статус успешно обновлен'
    await refresh()
    
    setTimeout(() => {
      statusUpdateMessage.value = ''
    }, 3000)
  } catch (error) {
    alert('Ошибка при обновлении статуса: ' + error.message)
    event.target.value = order.value.status
  } finally {
    isUpdating.value = false
  }
}

useHead({
  title: computed(() => order.value ? `Заказ #${order.value.id} — Система учета интернет-заказов` : 'Заказ')
})
</script>

