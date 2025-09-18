#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Главный экран приложения Motion Tracker
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.camera import Camera
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.logger import Logger

class StatusIndicator(Label):
    """Индикатор статуса с цветовой индикацией"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self._update_rect, pos=self._update_rect)
        self._update_rect()
    
    def _update_rect(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.2, 0.2, 0.2, 1)  # Темно-серый фон
            Rectangle(pos=self.pos, size=self.size)
    
    def set_status(self, status: str, color: tuple = (0, 1, 0, 1)):
        """Установка статуса с цветом"""
        self.text = status
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*color)
            Rectangle(pos=self.pos, size=self.size)

class MainScreen(BoxLayout):
    """Главный экран приложения"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = [10, 10, 10, 10]
        
        # Компоненты интерфейса
        self.camera_widget = None
        self.status_indicators = {}
        self.control_buttons = {}
        self.settings_panel = None
        
        # Создаем интерфейс
        self._create_interface()
        
        Logger.info("MainScreen: Интерфейс создан")
    
    def _create_interface(self):
        """Создание пользовательского интерфейса"""
        # Заголовок
        self._create_header()
        
        # Основная область с камерой и панелью управления
        main_area = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.7)
        
        # Область камеры
        camera_area = self._create_camera_area()
        main_area.add_widget(camera_area)
        
        # Панель управления
        control_panel = self._create_control_panel()
        main_area.add_widget(control_panel)
        
        self.add_widget(main_area)
        
        # Статусная панель
        self._create_status_panel()
        
        # Панель настроек
        self._create_settings_panel()
    
    def _create_header(self):
        """Создание заголовка"""
        header = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        
        title = Label(
            text='Motion Tracker',
            font_size='24sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        header.add_widget(title)
        
        # Кнопка настроек
        settings_btn = Button(
            text='⚙️',
            size_hint_x=0.2,
            font_size='20sp'
        )
        settings_btn.bind(on_press=self._toggle_settings)
        header.add_widget(settings_btn)
        
        self.add_widget(header)
    
    def _create_camera_area(self):
        """Создание области камеры"""
        camera_container = BoxLayout(orientation='vertical', size_hint_x=0.6)
        
        # Видео с камеры
        self.camera_widget = Camera(
            resolution=(640, 480),
            play=True,
            size_hint_y=0.8
        )
        camera_container.add_widget(self.camera_widget)
        
        # Индикатор движения
        motion_indicator = StatusIndicator(
            text='Движение: НЕТ',
            size_hint_y=0.1,
            font_size='16sp',
            color=(1, 1, 1, 1)
        )
        self.status_indicators['motion'] = motion_indicator
        camera_container.add_widget(motion_indicator)
        
        # Статистика FPS
        fps_label = Label(
            text='FPS: 0',
            size_hint_y=0.1,
            font_size='14sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        self.status_indicators['fps'] = fps_label
        camera_container.add_widget(fps_label)
        
        return camera_container
    
    def _create_control_panel(self):
        """Создание панели управления"""
        control_panel = BoxLayout(orientation='vertical', size_hint_x=0.4, spacing=10)
        
        # Кнопки управления
        buttons_layout = GridLayout(cols=2, spacing=10, size_hint_y=0.4)
        
        # Кнопка запуска/остановки
        start_btn = Button(
            text='СТАРТ',
            background_color=(0, 0.7, 0, 1),
            font_size='18sp',
            bold=True
        )
        start_btn.bind(on_press=self._toggle_tracking)
        self.control_buttons['start'] = start_btn
        buttons_layout.add_widget(start_btn)
        
        # Кнопка сброса
        reset_btn = Button(
            text='СБРОС',
            background_color=(0.7, 0.7, 0, 1),
            font_size='18sp',
            bold=True
        )
        reset_btn.bind(on_press=self._reset_tracking)
        self.control_buttons['reset'] = reset_btn
        buttons_layout.add_widget(reset_btn)
        
        # Кнопка калибровки
        calibrate_btn = Button(
            text='КАЛИБРОВКА',
            background_color=(0, 0.5, 0.7, 1),
            font_size='16sp'
        )
        calibrate_btn.bind(on_press=self._calibrate_camera)
        self.control_buttons['calibrate'] = calibrate_btn
        buttons_layout.add_widget(calibrate_btn)
        
        # Кнопка OTG
        otg_btn = Button(
            text='OTG',
            background_color=(0.7, 0, 0.7, 1),
            font_size='16sp'
        )
        otg_btn.bind(on_press=self._show_otg_devices)
        self.control_buttons['otg'] = otg_btn
        buttons_layout.add_widget(otg_btn)
        
        control_panel.add_widget(buttons_layout)
        
        # Настройки чувствительности
        sensitivity_layout = BoxLayout(orientation='vertical', size_hint_y=0.3)
        
        sensitivity_label = Label(
            text='Чувствительность: 50%',
            font_size='14sp',
            color=(1, 1, 1, 1)
        )
        self.status_indicators['sensitivity'] = sensitivity_label
        sensitivity_layout.add_widget(sensitivity_label)
        
        sensitivity_slider = Slider(
            min=0,
            max=100,
            value=50,
            step=1,
            size_hint_y=0.5
        )
        sensitivity_slider.bind(value=self._on_sensitivity_change)
        sensitivity_layout.add_widget(sensitivity_slider)
        
        control_panel.add_widget(sensitivity_layout)
        
        # Переключатель отображения
        display_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        
        display_switch = Switch(active=True)
        display_switch.bind(active=self._toggle_display_mode)
        display_layout.add_widget(display_switch)
        
        display_label = Label(
            text='Показывать секторы',
            font_size='12sp',
            color=(1, 1, 1, 1)
        )
        display_layout.add_widget(display_label)
        
        control_panel.add_widget(display_layout)
        
        return control_panel
    
    def _create_status_panel(self):
        """Создание статусной панели"""
        status_panel = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=10)
        
        # Статус камеры
        camera_status = StatusIndicator(
            text='Камера: ОТКЛ',
            size_hint_x=0.25
        )
        self.status_indicators['camera'] = camera_status
        status_panel.add_widget(camera_status)
        
        # Статус OTG
        otg_status = StatusIndicator(
            text='OTG: НЕТ',
            size_hint_x=0.25
        )
        self.status_indicators['otg'] = otg_status
        status_panel.add_widget(otg_status)
        
        # Статус ESP32
        esp32_status = StatusIndicator(
            text='ESP32: НЕТ',
            size_hint_x=0.25
        )
        self.status_indicators['esp32'] = esp32_status
        status_panel.add_widget(esp32_status)
        
        # Общий статус
        general_status = StatusIndicator(
            text='Готов',
            size_hint_x=0.25
        )
        self.status_indicators['general'] = general_status
        status_panel.add_widget(general_status)
        
        self.add_widget(status_panel)
    
    def _create_settings_panel(self):
        """Создание панели настроек (скрытой по умолчанию)"""
        self.settings_panel = BoxLayout(
            orientation='vertical',
            size_hint_y=0.2,
            spacing=5
        )
        self.settings_panel.opacity = 0  # Скрыта по умолчанию
        
        # Настройки камеры
        camera_settings = GridLayout(cols=2, spacing=5, size_hint_y=0.5)
        
        camera_settings.add_widget(Label(text='Разрешение:', font_size='12sp'))
        resolution_btn = Button(text='640x480', font_size='12sp')
        camera_settings.add_widget(resolution_btn)
        
        camera_settings.add_widget(Label(text='FPS:', font_size='12sp'))
        fps_btn = Button(text='30', font_size='12sp')
        camera_settings.add_widget(fps_btn)
        
        self.settings_panel.add_widget(camera_settings)
        
        # Настройки детекции
        detection_settings = GridLayout(cols=2, spacing=5, size_hint_y=0.5)
        
        detection_settings.add_widget(Label(text='Мин. площадь:', font_size='12sp'))
        area_btn = Button(text='500', font_size='12sp')
        detection_settings.add_widget(area_btn)
        
        detection_settings.add_widget(Label(text='Алгоритм:', font_size='12sp'))
        algo_btn = Button(text='MOG2', font_size='12sp')
        detection_settings.add_widget(algo_btn)
        
        self.settings_panel.add_widget(detection_settings)
        
        self.add_widget(self.settings_panel)
    
    def _toggle_settings(self, instance):
        """Переключение видимости панели настроек"""
        if self.settings_panel.opacity == 0:
            self.settings_panel.opacity = 1
            self.settings_panel.size_hint_y = 0.2
        else:
            self.settings_panel.opacity = 0
            self.settings_panel.size_hint_y = 0
    
    def _toggle_tracking(self, instance):
        """Переключение трекинга"""
        if self.control_buttons['start'].text == 'СТАРТ':
            self.control_buttons['start'].text = 'СТОП'
            self.control_buttons['start'].background_color = (0.7, 0, 0, 1)
            Logger.info("MainScreen: Запуск трекинга")
        else:
            self.control_buttons['start'].text = 'СТАРТ'
            self.control_buttons['start'].background_color = (0, 0.7, 0, 1)
            Logger.info("MainScreen: Остановка трекинга")
    
    def _reset_tracking(self, instance):
        """Сброс трекинга"""
        Logger.info("MainScreen: Сброс трекинга")
        # Здесь будет логика сброса
    
    def _calibrate_camera(self, instance):
        """Калибровка камеры"""
        Logger.info("MainScreen: Калибровка камеры")
        # Здесь будет логика калибровки
    
    def _show_otg_devices(self, instance):
        """Показ OTG устройств"""
        Logger.info("MainScreen: Показ OTG устройств")
        # Здесь будет показ списка устройств
    
    def _on_sensitivity_change(self, instance, value):
        """Изменение чувствительности"""
        self.status_indicators['sensitivity'].text = f'Чувствительность: {int(value)}%'
        Logger.info(f"MainScreen: Изменена чувствительность на {int(value)}%")
    
    def _toggle_display_mode(self, instance, value):
        """Переключение режима отображения"""
        mode = "включено" if value else "отключено"
        Logger.info(f"MainScreen: Отображение секторов {mode}")
    
    def update_stats(self, stats: dict):
        """Обновление статистики"""
        if 'fps' in stats:
            self.status_indicators['fps'].text = f'FPS: {stats["fps"]:.1f}'
        
        if 'motion_detections' in stats:
            motion_text = 'Движение: ДА' if stats.get('motion_detected', False) else 'Движение: НЕТ'
            self.status_indicators['motion'].text = motion_text
            
            # Обновляем цвет индикатора
            color = (1, 0, 0, 1) if stats.get('motion_detected', False) else (0, 1, 0, 1)
            self.status_indicators['motion'].set_status(motion_text, color)
    
    def update_otg_status(self, devices: list):
        """Обновление статуса OTG устройств"""
        device_count = len(devices)
        self.status_indicators['otg'].text = f'OTG: {device_count}'
        
        # Проверяем наличие ESP32
        esp32_count = len([d for d in devices if d.device_type == 'esp32'])
        self.status_indicators['esp32'].text = f'ESP32: {esp32_count}'
        
        # Обновляем цвета индикаторов
        otg_color = (0, 1, 0, 1) if device_count > 0 else (0.5, 0.5, 0.5, 1)
        esp32_color = (0, 1, 0, 1) if esp32_count > 0 else (0.5, 0.5, 0.5, 1)
        
        self.status_indicators['otg'].set_status(f'OTG: {device_count}', otg_color)
        self.status_indicators['esp32'].set_status(f'ESP32: {esp32_count}', esp32_color)
    
    def enable_features(self):
        """Включение функций после получения разрешений"""
        self.status_indicators['camera'].set_status('Камера: ГОТОВ', (0, 1, 0, 1))
        self.status_indicators['general'].set_status('Готов к работе', (0, 1, 0, 1))
        Logger.info("MainScreen: Функции включены")