#!/bin/bash
# Скрипт для сборки Android APK

set -e  # Остановка при ошибке

echo "🚀 Motion Tracker - Сборка Android APK"
echo "======================================"

# Проверка наличия buildozer
if ! command -v buildozer &> /dev/null; then
    echo "❌ Buildozer не найден. Устанавливаем..."
    pip install buildozer
fi

# Проверка Python зависимостей
echo "📦 Проверка зависимостей..."
pip install -r requirements.txt

# Очистка предыдущих сборок
echo "🧹 Очистка предыдущих сборок..."
buildozer android clean

# Сборка debug версии
echo "🔨 Сборка debug APK..."
buildozer android debug

# Проверка результата
if [ -f "bin/*.apk" ]; then
    echo "✅ Сборка завершена успешно!"
    echo "📱 APK файл: bin/"
    ls -la bin/*.apk
else
    echo "❌ Ошибка сборки!"
    exit 1
fi

echo ""
echo "📋 Следующие шаги:"
echo "1. Установите APK на Android устройство"
echo "2. Предоставьте разрешения для камеры и USB"
echo "3. Подключите OTG устройства"
echo "4. Запустите приложение"