# Инструкции по сборке APK

## Подготовка окружения

### 1. Установка системных зависимостей

#### macOS:
```bash
# Установка через Homebrew
brew install autoconf automake libtool pkg-config
brew install libffi openssl
brew install python3

# Установка Java (требуется для Android SDK)
brew install openjdk@11
```

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-11-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
```

#### Windows:
- Установите Python 3.8+
- Установите Git
- Установите Java JDK 11
- Установите Android Studio

### 2. Установка Python зависимостей

```bash
# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install --upgrade pip
pip install -r requirements.txt
pip install buildozer
```

### 3. Настройка Android SDK

#### Автоматическая установка (рекомендуется):
```bash
# Buildozer автоматически скачает SDK и NDK
buildozer android debug
```

#### Ручная установка:
1. Скачайте Android SDK Command Line Tools
2. Установите через sdkmanager:
   ```bash
   sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.0"
   sdkmanager "ndk;25.1.8937393"
   ```

3. Настройте переменные окружения:
   ```bash
   export ANDROIDSDK="$HOME/Android/Sdk"
   export ANDROIDNDK="$HOME/Android/Sdk/ndk/25.1.8937393"
   export ANDROIDAPI="33"
   export NDKAPI="21"
   ```

## Сборка APK

### 1. Первоначальная настройка

```bash
# Переход в папку проекта
cd android_motion_tracker

# Инициализация (создает .buildozer папку)
buildozer init
```

### 2. Сборка debug версии

```bash
# Полная очистка и сборка
buildozer android clean
buildozer android debug

# Или быстрая сборка (если уже собирали)
buildozer android debug
```

### 3. Сборка release версии

```bash
# Создание подписанного APK
buildozer android release

# APK будет в папке bin/
ls bin/
```

## Настройка подписи APK

### 1. Создание keystore

```bash
keytool -genkey -v -keystore motiontracker.keystore -alias motiontracker -keyalg RSA -keysize 2048 -validity 10000
```

### 2. Настройка buildozer.spec

Добавьте в секцию `[app]`:
```ini
# (str) Path to a custom keystore
android.keystore = motiontracker.keystore

# (str) Keystore password
android.keystore_password = your_password

# (str) Key alias
android.keyalias = motiontracker

# (str) Key password
android.keyalias_password = your_password
```

## Оптимизация APK

### 1. Уменьшение размера

В `buildozer.spec`:
```ini
# Включить ProGuard
android.add_src = proguard-rules.pro

# Минимизировать зависимости
requirements = python3,kivy,opencv-python-headless,numpy
```

### 2. Создание AAB (Android App Bundle)

```ini
# В buildozer.spec
android.release_artifact = aab
```

```bash
buildozer android release
```

## Тестирование

### 1. Установка на устройство

```bash
# Через ADB
adb install bin/motiontracker-1.0.0-debug.apk

# Или через файловый менеджер
# Скопируйте APK на устройство и установите
```

### 2. Отладка

```bash
# Просмотр логов
adb logcat | grep python

# Подключение к устройству
adb devices

# Запуск приложения
adb shell am start -n com.motiontracker.app/.PythonActivity
```

## Решение проблем

### Ошибки сборки

1. **"NDK not found"**:
   ```bash
   buildozer android clean
   buildozer android debug
   ```

2. **"SDK not found"**:
   - Проверьте переменные окружения
   - Убедитесь в правильности путей

3. **"Permission denied"**:
   ```bash
   chmod +x ~/.buildozer/android/platform/android-ndk-*/build/tools/make_standalone_toolchain.py
   ```

### Проблемы с зависимостями

1. **OpenCV не собирается**:
   ```ini
   # В buildozer.spec используйте opencv-python-headless
   requirements = python3,kivy,opencv-python-headless,numpy
   ```

2. **Kivy проблемы**:
   ```bash
   # Обновите Kivy
   pip install --upgrade kivy
   ```

### Проблемы с OTG

1. **Устройства не обнаружены**:
   - Проверьте разрешения в манифесте
   - Убедитесь в поддержке USB Host на устройстве

2. **Ошибки подключения**:
   - Проверьте совместимость устройств
   - Обновите драйверы

## Автоматизация сборки

### GitHub Actions

Создайте `.github/workflows/build.yml`:
```yaml
name: Build APK

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    
    - name: Install dependencies
      run: |
        pip install buildozer
        pip install -r requirements.txt
    
    - name: Build APK
      run: buildozer android debug
    
    - name: Upload APK
      uses: actions/upload-artifact@v2
      with:
        name: motiontracker-apk
        path: bin/*.apk
```

## Дополнительные ресурсы

- [Buildozer документация](https://buildozer.readthedocs.io/)
- [Kivy для Android](https://kivy.org/doc/stable/guide/android.html)
- [Android USB Host API](https://developer.android.com/guide/topics/connectivity/usb/host)
- [OpenCV для Android](https://opencv.org/android/)