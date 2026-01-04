<template>
  <div>
    <div class="card">
      <h2>Информационная система учета интернет-заказов торговой сети</h2>
      <p style="margin-top: 1rem; color: var(--lenta-text-light);">
        Система предназначена для автоматизации учета интернет-заказов посредством сети Интернет.
        Используется сотрудниками центрального офиса торговой сети для ведения учета и управления заказами.
      </p>
    </div>

    <div v-if="stats" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-top: 2rem;">
      <div class="card stat-card" style="background-color: #1a3a5f; color: white; border-left: 4px solid var(--lenta-blue);">
        <div style="font-size: 0.9rem; opacity: 0.85; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.5px;">Всего заказов</div>
        <div style="font-size: 2.5rem; font-weight: 700;">{{ stats.total_orders }}</div>
      </div>
      <div class="card stat-card" style="background-color: #2c4a6b; color: white; border-left: 4px solid #4a6fa5;">
        <div style="font-size: 0.9rem; opacity: 0.85; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.5px;">Общая сумма</div>
        <div style="font-size: 2.5rem; font-weight: 700;">{{ formatPrice(stats.total_amount) }} ₽</div>
      </div>
      <div class="card stat-card" style="background-color: #3d5a6b; color: white; border-left: 4px solid #5a8fa5;">
        <div style="font-size: 0.9rem; opacity: 0.85; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.5px;">Выполнено</div>
        <div style="font-size: 2.5rem; font-weight: 700;">{{ stats.status_counts['выполнен'] || 0 }}</div>
      </div>
      <div class="card stat-card" style="background-color: #4a5a6b; color: white; border-left: 4px solid #6a8fa5;">
        <div style="font-size: 0.9rem; opacity: 0.85; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.5px;">В обработке</div>
        <div style="font-size: 2.5rem; font-weight: 700;">{{ stats.status_counts['в обработке'] || 0 }}</div>
      </div>
    </div>

    <div v-if="stats" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 2rem; margin-top: 2rem;">
      <ClientOnly>
        <div class="card">
          <h3 style="margin-bottom: 1.5rem; color: var(--lenta-text);">Наиболее популярные продукты</h3>
          <div v-if="popularProducts && popularProducts.length > 0" style="position: relative; height: 400px;">
            <canvas ref="productsChart"></canvas>
          </div>
          <div v-else style="display: flex; align-items: center; justify-content: center; height: 300px; color: var(--lenta-text-light);">
            Нет данных для отображения
          </div>
        </div>
        <template #fallback>
          <div class="card">
            <h3 style="margin-bottom: 1.5rem; color: var(--lenta-text);">Наиболее популярные продукты</h3>
            <div style="display: flex; align-items: center; justify-content: center; height: 300px; color: var(--lenta-text-light);">
              Загрузка графика...
            </div>
          </div>
        </template>
      </ClientOnly>
      <div class="card">
        <h3 style="margin-bottom: 1.5rem; color: var(--lenta-text);">Статистика по статусам</h3>
        <div style="display: grid; gap: 1rem;">
          <div v-for="(count, status) in stats.status_counts" :key="status" style="padding: 1rem; background-color: var(--lenta-light-gray); border-radius: 8px; border-left: 3px solid var(--lenta-blue);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span :class="`status-badge status-${getStatusClass(status)}`" style="font-size: 0.9rem;">
                {{ status }}
              </span>
              <span style="font-size: 1.5rem; font-weight: 700; color: var(--lenta-blue);">
                {{ count }}
              </span>
            </div>
            <div style="margin-top: 0.5rem;">
              <div style="background-color: #e0e0e0; height: 6px; border-radius: 3px; overflow: hidden;">
                <div :style="`width: ${(count / stats.total_orders) * 100}%; background-color: var(--lenta-blue); height: 100%; transition: width 0.3s ease;`"></div>
              </div>
              <div style="font-size: 0.85rem; color: var(--lenta-text-light); margin-top: 0.25rem;">
                {{ ((count / stats.total_orders) * 100).toFixed(1) }}% от общего количества
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card" style="margin-top: 2rem;">
      <div style="margin-bottom: 1.5rem;">
        <h3 style="margin-bottom: 1rem;">Основные возможности системы:</h3>
        <ul style="list-style-position: inside; line-height: 2;">
          <li>Просмотр списка интернет-заказов с фильтрацией и поиском</li>
          <li>Создание новых заказов</li>
          <li>Просмотр детальной информации о заказе</li>
          <li>Изменение статуса заказа</li>
          <li>Управление справочником товаров</li>
        </ul>
      </div>

      <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
        <NuxtLink to="/orders" class="btn">
          Перейти к разделу «Заказы»
        </NuxtLink>
        <NuxtLink to="/orders/new" class="btn btn-secondary">
          Создать новый заказ
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup>
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const { data: stats } = await useFetch(`${apiBase}/api/orders/stats/summary`)
const { data: popularProducts } = await useFetch(`${apiBase}/api/products/popular?limit=10`)
const productsChart = ref(null)
let chartInstance = null
let Chart = null

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

onMounted(async () => {
  if (process.client) {
    const chartModule = await import('chart.js')
    Chart = chartModule.Chart
    const { BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend } = chartModule
    Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend)
    
    await nextTick()
    if (popularProducts.value && popularProducts.value.length > 0 && productsChart.value) {
      createProductsChart()
    }
  }
})

watch(popularProducts, async () => {
  if (process.client && popularProducts.value && popularProducts.value.length > 0 && Chart) {
    await nextTick()
    if (productsChart.value) {
      if (chartInstance) {
        chartInstance.destroy()
      }
      createProductsChart()
    }
  }
}, { immediate: false })

function createProductsChart() {
  if (!popularProducts.value || popularProducts.value.length === 0 || !productsChart.value || !Chart) return

  const labels = popularProducts.value.map(p => {
    const name = p.product_name
    return name.length > 30 ? name.substring(0, 27) + '...' : name
  })
  const quantities = popularProducts.value.map(p => p.total_quantity)
  
  const baseColors = [
    '#003C95', '#1a4fa5', '#2c5fb5', '#3d6fc5', '#4a7fd5',
    '#5a8fe5', '#6a9ff5', '#7aafff', '#8abfff', '#9acfff'
  ]
  const colors = baseColors.slice(0, quantities.length)

  const ctx = productsChart.value.getContext('2d')
  
  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Количество (шт.)',
        data: quantities,
        backgroundColor: colors,
        borderColor: '#003C95',
        borderWidth: 1,
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 12,
          titleFont: {
            size: 13,
            weight: '600'
          },
          bodyFont: {
            size: 12
          },
          callbacks: {
            title: function(context) {
              const index = context[0].dataIndex
              return popularProducts.value[index].product_name
            },
            label: function(context) {
              const index = context.dataIndex
              const product = popularProducts.value[index]
              return [
                `Количество: ${product.total_quantity} шт.`,
                `Заказов: ${product.order_count}`
              ]
            }
          }
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          ticks: {
            font: {
              size: 11
            }
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        y: {
          ticks: {
            font: {
              size: 11
            }
          },
          grid: {
            display: false
          }
        }
      }
    }
  })
}

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.destroy()
  }
})

useHead({
  title: 'Главная — Система учета интернет-заказов'
})
</script>

