#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простое Android приложение Motion Tracker
Минимальная версия для тестирования сборки
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.core.window import Window

class MotionTrackerApp(App):
    """Простое приложение Motion Tracker для Android"""
    
    def build(self):
        """Создание основного интерфейса приложения"""
        Logger.info("MotionTracker: Запуск простого приложения")
        
        # Настройка окна
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        
        # Создание главного экрана
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Заголовок
        title = Label(
            text='Motion Tracker',
            font_size='24sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.2
        )
        layout.add_widget(title)
        
        # Кнопки
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.3, spacing=10)
        
        start_btn = Button(
            text='СТАРТ',
            background_color=(0, 0.7, 0, 1),
            font_size='18sp',
            bold=True
        )
        start_btn.bind(on_press=self.toggle_tracking)
        self.start_btn = start_btn
        button_layout.add_widget(start_btn)
        
        reset_btn = Button(
            text='СБРОС',
            background_color=(0.7, 0.7, 0, 1),
            font_size='18sp',
            bold=True
        )
        reset_btn.bind(on_press=self.reset_tracking)
        button_layout.add_widget(reset_btn)
        
        layout.add_widget(button_layout)
        
        # Статус
        self.status_label = Label(
            text='Готов к работе',
            font_size='16sp',
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=0.2
        )
        layout.add_widget(self.status_label)
        
        # Информация
        info_label = Label(
            text='Простое приложение для тестирования\nсборки Android APK',
            font_size='14sp',
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=0.3
        )
        layout.add_widget(info_label)
        
        return layout
    
    def toggle_tracking(self, instance):
        """Переключение трекинга"""
        if self.start_btn.text == 'СТАРТ':
            self.start_btn.text = 'СТОП'
            self.start_btn.background_color = (0.7, 0, 0, 1)
            self.status_label.text = 'Трекинг: АКТИВЕН'
            Logger.info("MotionTracker: Трекинг запущен")
        else:
            self.start_btn.text = 'СТАРТ'
            self.start_btn.background_color = (0, 0.7, 0, 1)
            self.status_label.text = 'Трекинг: ОСТАНОВЛЕН'
            Logger.info("MotionTracker: Трекинг остановлен")
    
    def reset_tracking(self, instance):
        """Сброс трекинга"""
        self.start_btn.text = 'СТАРТ'
        self.start_btn.background_color = (0, 0.7, 0, 1)
        self.status_label.text = 'Трекинг: СБРОШЕН'
        Logger.info("MotionTracker: Трекинг сброшен")
    
    def on_start(self):
        """Вызывается при запуске приложения"""
        Logger.info("MotionTracker: Приложение запущено")
    
    def on_pause(self):
        """Вызывается при паузе приложения"""
        Logger.info("MotionTracker: Приложение приостановлено")
        return True
    
    def on_resume(self):
        """Вызывается при возобновлении приложения"""
        Logger.info("MotionTracker: Приложение возобновлено")

if __name__ == '__main__':
    MotionTrackerApp().run()