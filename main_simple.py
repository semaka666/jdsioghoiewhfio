#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Упрощенная версия Motion Tracker для Android
Без OpenCV - только базовый функционал
"""

import os
import sys
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.camera import Camera
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.core.window import Window

class MotionTrackerApp(App):
    """Упрощенное приложение Motion Tracker для Android"""
    
    def build(self):
        """Создание основного интерфейса приложения"""
        Logger.info("MotionTracker: Инициализация упрощенного приложения")
        
        # Настройка окна для мобильных устройств
        Window.clearcolor = (0.1, 0.1, 0.1, 1)  # Темный фон
        
        # Создание главного экрана
        self.main_screen = MainScreen()
        
        # Подключение событий
        self.setup_events()
        
        return self.main_screen
    
    def setup_events(self):
        """Настройка событий приложения"""
        # Обновление интерфейса каждые 100мс
        Clock.schedule_interval(self.update_ui, 0.1)
    
    def update_ui(self, dt):
        """Обновление пользовательского интерфейса"""
        # Простое обновление статуса
        pass
    
    def on_start(self):
        """Вызывается при запуске приложения"""
        Logger.info("MotionTracker: Упрощенное приложение запущено")
        
        # Запрос разрешений
        self.request_permissions()
    
    def on_pause(self):
        """Вызывается при паузе приложения"""
        Logger.info("MotionTracker: Приложение приостановлено")
        return True
    
    def on_resume(self):
        """Вызывается при возобновлении приложения"""
        Logger.info("MotionTracker: Приложение возобновлено")
    
    def request_permissions(self):
        """Запрос необходимых разрешений"""
        try:
            from android.permissions import request_permissions, Permission
            
            permissions = [
                Permission.CAMERA,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
            ]
            
            def callback(permissions, results):
                if all(results):
                    Logger.info("MotionTracker: Все разрешения получены")
                    self.main_screen.enable_features()
                else:
                    Logger.warning("MotionTracker: Некоторые разрешения не получены")
                    self.show_permission_error()
            
            request_permissions(permissions, callback)
        except ImportError:
            # Для тестирования без Android
            Logger.info("MotionTracker: Android API недоступен, пропускаем разрешения")
            self.main_screen.enable_features()
    
    def show_permission_error(self):
        """Показ ошибки разрешений"""
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text='Необходимы разрешения для работы приложения'))
        
        popup = Popup(
            title='Ошибка разрешений',
            content=content,
            size_hint=(0.8, 0.4)
        )
        popup.open()
    
    def on_stop(self):
        """Вызывается при остановке приложения"""
        Logger.info("MotionTracker: Приложение остановлено")

class MainScreen(BoxLayout):
    """Упрощенный главный экран приложения"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = [10, 10, 10, 10]
        
        # Создаем интерфейс
        self._create_interface()
        
        Logger.info("MainScreen: Упрощенный интерфейс создан")
    
    def _create_interface(self):
        """Создание пользовательского интерфейса"""
        # Заголовок
        header = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        
        title = Label(
            text='Motion Tracker (Simple)',
            font_size='24sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        header.add_widget(title)
        
        self.add_widget(header)
        
        # Область камеры
        camera_container = BoxLayout(orientation='vertical', size_hint_y=0.6)
        
        # Видео с камеры
        self.camera_widget = Camera(
            resolution=(640, 480),
            play=True,
            size_hint_y=0.8
        )
        camera_container.add_widget(self.camera_widget)
        
        # Статус
        status_label = Label(
            text='Камера: Инициализация...',
            size_hint_y=0.2,
            font_size='16sp',
            color=(1, 1, 1, 1)
        )
        self.status_label = status_label
        camera_container.add_widget(status_label)
        
        self.add_widget(camera_container)
        
        # Кнопки управления
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=10)
        
        # Кнопка запуска/остановки
        start_btn = Button(
            text='СТАРТ',
            background_color=(0, 0.7, 0, 1),
            font_size='18sp',
            bold=True
        )
        start_btn.bind(on_press=self._toggle_tracking)
        self.start_btn = start_btn
        buttons_layout.add_widget(start_btn)
        
        # Кнопка сброса
        reset_btn = Button(
            text='СБРОС',
            background_color=(0.7, 0.7, 0, 1),
            font_size='18sp',
            bold=True
        )
        reset_btn.bind(on_press=self._reset_tracking)
        buttons_layout.add_widget(reset_btn)
        
        self.add_widget(buttons_layout)
        
        # Статусная панель
        status_panel = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=10)
        
        # Статус камеры
        camera_status = Label(
            text='Камера: ОТКЛ',
            size_hint_x=0.5,
            font_size='14sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        self.camera_status = camera_status
        status_panel.add_widget(camera_status)
        
        # Общий статус
        general_status = Label(
            text='Готов',
            size_hint_x=0.5,
            font_size='14sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        self.general_status = general_status
        status_panel.add_widget(general_status)
        
        self.add_widget(status_panel)
    
    def _toggle_tracking(self, instance):
        """Переключение трекинга"""
        if self.start_btn.text == 'СТАРТ':
            self.start_btn.text = 'СТОП'
            self.start_btn.background_color = (0.7, 0, 0, 1)
            self.status_label.text = 'Трекинг: АКТИВЕН'
            Logger.info("MainScreen: Запуск трекинга")
        else:
            self.start_btn.text = 'СТАРТ'
            self.start_btn.background_color = (0, 0.7, 0, 1)
            self.status_label.text = 'Трекинг: ОСТАНОВЛЕН'
            Logger.info("MainScreen: Остановка трекинга")
    
    def _reset_tracking(self, instance):
        """Сброс трекинга"""
        self.start_btn.text = 'СТАРТ'
        self.start_btn.background_color = (0, 0.7, 0, 1)
        self.status_label.text = 'Трекинг: СБРОШЕН'
        Logger.info("MainScreen: Сброс трекинга")
    
    def enable_features(self):
        """Включение функций после получения разрешений"""
        self.camera_status.text = 'Камера: ГОТОВ'
        self.camera_status.color = (0, 1, 0, 1)
        self.general_status.text = 'Готов к работе'
        self.general_status.color = (0, 1, 0, 1)
        self.status_label.text = 'Камера: ГОТОВА'
        Logger.info("MainScreen: Функции включены")

if __name__ == '__main__':
    MotionTrackerApp().run()