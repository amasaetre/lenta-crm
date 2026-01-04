<template>
  <div>
    <div style="margin-bottom: 2rem;">
      <NuxtLink to="/orders" class="link">← Назад к списку заказов</NuxtLink>
    </div>

    <div class="card">
      <h2>Создание нового заказа</h2>

      <form @submit.prevent="createOrder" style="margin-top: 2rem;">
        <div class="form-group">
          <label for="customer_name">Имя клиента *</label>
          <input
            id="customer_name"
            v-model="form.customer_name"
            type="text"
            required
            placeholder="Введите имя клиента"
          />
        </div>

        <div class="form-group">
          <label>Товары</label>
          <div v-for="(item, index) in form.items" :key="index" style="display: flex; gap: 1rem; margin-bottom: 1rem; align-items: end;">
            <div style="flex: 2;">
              <select
                v-model="item.product_id"
                required
                @change="updateItemPrice(index)"
              >
                <option value="">Выберите товар</option>
                <option
                  v-for="product in products"
                  :key="product.id"
                  :value="product.id"
                >
                  {{ product.name }} — {{ formatPrice(product.price) }} ₽
                </option>
              </select>
            </div>
            <div style="flex: 1;">
              <input
                v-model.number="item.quantity"
                type="number"
                min="1"
                required
                placeholder="Количество"
                @input="updateItemPrice(index)"
              />
            </div>
            <div style="flex: 1; padding: 0.75rem; background-color: var(--lenta-light-gray); border-radius: 4px;">
              <strong>{{ formatPrice(getItemTotal(index)) }} ₽</strong>
            </div>
            <button
              type="button"
              @click="removeItem(index)"
              style="padding: 0.75rem 1rem; background-color: #D32F2F; color: white; border: none; border-radius: 4px; cursor: pointer;"
            >
              Удалить
            </button>
          </div>
          <button
            type="button"
            @click="addItem"
            class="btn-secondary"
            style="margin-top: 0.5rem;"
          >
            + Добавить товар
          </button>
        </div>

        <div style="margin-top: 2rem; padding-top: 1.5rem; border-top: 2px solid var(--lenta-blue);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
            <strong style="font-size: 1.25rem;">Итого:</strong>
            <strong style="font-size: 1.5rem; color: var(--lenta-blue);">
              {{ formatPrice(totalAmount) }} ₽
            </strong>
          </div>
          <div style="display: flex; gap: 1rem;">
            <button type="submit" class="btn" :disabled="isSubmitting">
              {{ isSubmitting ? 'Создание...' : 'Создать заказ' }}
            </button>
            <NuxtLink to="/orders" class="btn btn-secondary">
              Отмена
            </NuxtLink>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
const config = useRuntimeConfig()
const apiBase = config.public.apiBase
const router = useRouter()

const { data: products } = await useFetch(`${apiBase}/api/products`)

const form = ref({
  customer_name: '',
  items: [
    { product_id: '', quantity: 1 }
  ]
})

const isSubmitting = ref(false)

function addItem() {
  form.value.items.push({ product_id: '', quantity: 1 })
}

function removeItem(index) {
  if (form.value.items.length > 1) {
    form.value.items.splice(index, 1)
  }
}

function getItemTotal(index) {
  const item = form.value.items[index]
  if (!item.product_id) return 0
  
  const product = products.value.find(p => p.id === item.product_id)
  if (!product) return 0
  
  return product.price * item.quantity
}

function updateItemPrice(index) {
}

const totalAmount = computed(() => {
  return form.value.items.reduce((sum, item, index) => {
    return sum + getItemTotal(index)
  }, 0)
})

async function createOrder() {
  if (isSubmitting.value) return
  
  if (!form.value.customer_name.trim()) {
    alert('Введите имя клиента')
    return
  }
  
  if (form.value.items.some(item => !item.product_id || item.quantity < 1)) {
    alert('Заполните все позиции заказа')
    return
  }

  isSubmitting.value = true

  try {
    const response = await fetch(`${apiBase}/api/orders`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        customer_name: form.value.customer_name,
        items: form.value.items.map(item => ({
          product_id: item.product_id,
          quantity: item.quantity
        }))
      })
    })

    if (!response.ok) {
      throw new Error('Ошибка при создании заказа')
    }

    const order = await response.json()
    router.push(`/orders/${order.id}`)
  } catch (error) {
    alert('Ошибка при создании заказа: ' + error.message)
  } finally {
    isSubmitting.value = false
  }
}

function formatPrice(price) {
  return new Intl.NumberFormat('ru-RU', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(price)
}

useHead({
  title: 'Создание заказа — Система учета интернет-заказов'
})
</script>

