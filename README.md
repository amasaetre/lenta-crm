# Информационная система учета интернет-заказов торговой сети

Веб-приложение для автоматизации учета интернет-заказов.

## Технологии

- **Backend:** Python FastAPI, SQLite, SQLModel
- **Frontend:** Nuxt 3, Chart.js

## Запуск

### Backend

```bash
cd backend
pip install -r requirements.txt
python run.py
```

Или:

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

API доступен: http://localhost:8000  
Документация: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Приложение доступно: http://localhost:3000
