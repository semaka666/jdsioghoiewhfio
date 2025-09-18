#!/bin/bash

# Скрипт для быстрой загрузки проекта в GitHub
# Использование: ./upload_to_github.sh

echo "🚀 Загрузка Motion Tracker в GitHub..."

# Проверяем, что мы в правильной папке
if [ ! -f "main.py" ]; then
    echo "❌ Ошибка: main.py не найден. Запустите скрипт из папки android_motion_tracker"
    exit 1
fi

# Проверяем, что git инициализирован
if [ ! -d ".git" ]; then
    echo "📦 Инициализация Git репозитория..."
    git init
    git branch -M main
fi

# Добавляем все файлы
echo "📁 Добавление файлов..."
git add .

# Создаем коммит
echo "💾 Создание коммита..."
git commit -m "Initial commit: Motion Tracker Android app with GitHub Actions"

echo ""
echo "✅ Готово! Теперь выполните следующие шаги:"
echo ""
echo "1. Создайте репозиторий на GitHub.com"
echo "2. Скопируйте URL репозитория"
echo "3. Выполните команды:"
echo ""
echo "   git remote add origin https://github.com/ВАШ_ПОЛЬЗОВАТЕЛЬ/ВАШ_РЕПОЗИТОРИЙ.git"
echo "   git push -u origin main"
echo ""
echo "4. GitHub Actions автоматически соберет APK (~15 минут)"
echo "5. Скачайте APK из раздела Actions > Artifacts"
echo ""
echo "📖 Подробные инструкции в README_GITHUB.md"