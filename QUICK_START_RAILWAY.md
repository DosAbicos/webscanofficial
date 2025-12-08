# ⚡ Быстрый старт Railway.app

## 🎯 За 15 минут до запуска!

### 1️⃣ Загрузите в GitHub (3 минуты)

```bash
# В терминале Emergent
cd /app
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/ВАШ_USERNAME/ВАШ_РЕПО.git
git push -u origin main
```

### 2️⃣ Создайте проект на Railway (2 минуты)

1. Откройте [railway.app](https://railway.app)
2. Login with GitHub
3. New Project → Deploy from GitHub repo
4. Выберите ваш репозиторий

### 3️⃣ Настройте переменные (2 минуты)

В Railway → Variables → Add:

```
MONGO_URL=mongodb://localhost:27017
DB_NAME=barcode_manager
CORS_ORIGINS=*
```

### 4️⃣ Получите URL (1 минута)

Settings → Domains → Generate Domain

Скопируйте URL (например: `my-app.up.railway.app`)

### 5️⃣ Обновите Frontend (3 минуты)

В `/app/frontend/.env`:

```env
REACT_APP_BACKEND_URL=https://my-app.up.railway.app
```

Затем:

```bash
git add frontend/.env
git commit -m "Update backend URL"
git push
```

### 6️⃣ Готово! (5 минут ожидание)

Подождите пока Railway завершит деплой (смотрите прогресс в Deployments)

Откройте ваш URL → Приложение работает! 🎉

---

## 📞 Если что-то не работает:

1. Проверьте логи: Railway → Deployments → View Logs
2. Убедитесь что все файлы в git: `git status`
3. Проверьте что переменные добавлены правильно

**Подробная инструкция:** `/app/RAILWAY_DEPLOYMENT.md`
