#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль управления OTG устройствами для Android
Поддержка подключения ESP32 и других USB устройств
"""

import threading
import time
from typing import Dict, List, Optional
from kivy.logger import Logger

class OTGDevice:
    """Класс для представления OTG устройства"""
    
    def __init__(self, device_id: str, device_type: str, name: str):
        self.device_id = device_id
        self.device_type = device_type  # 'esp32', 'camera', 'other'
        self.name = name
        self.connected = False
        self.last_seen = time.time()
        self.data = {}
    
    def update_data(self, data: Dict):
        """Обновление данных устройства"""
        self.data.update(data)
        self.last_seen = time.time()

class OTGManager:
    """Менеджер OTG устройств для Android"""
    
    def __init__(self):
        self.devices = {}
        self.is_monitoring = False
        self.monitor_thread = None
        self.stop_event = threading.Event()
        
        # Поддерживаемые типы устройств
        self.supported_devices = {
            'esp32': {
                'vendor_ids': [0x10C4, 0x1A86],  # CP2102, CH340
                'product_names': ['CP2102', 'CH340', 'USB Serial']
            },
            'camera': {
                'vendor_ids': [0x046D, 0x0BDA],  # Logitech, Realtek
                'product_names': ['USB Camera', 'Webcam']
            }
        }
        
        Logger.info("OTGManager: Инициализирован")
    
    def start_monitoring(self):
        """Запуск мониторинга OTG устройств"""
        if self.is_monitoring:
            Logger.warning("OTGManager: Мониторинг уже запущен")
            return
        
        self.is_monitoring = True
        self.stop_event.clear()
        
        # Запускаем поток мониторинга
        self.monitor_thread = threading.Thread(target=self._monitoring_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        Logger.info("OTGManager: Мониторинг запущен")
    
    def stop_monitoring(self):
        """Остановка мониторинга OTG устройств"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        self.stop_event.set()
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
        
        Logger.info("OTGManager: Мониторинг остановлен")
    
    def _monitoring_loop(self):
        """Основной цикл мониторинга устройств"""
        while self.is_monitoring and not self.stop_event.is_set():
            try:
                # Сканируем подключенные устройства
                self._scan_devices()
                
                # Проверяем состояние существующих устройств
                self._check_device_status()
                
                # Пауза между сканированиями
                time.sleep(2.0)
                
            except Exception as e:
                Logger.error(f"OTGManager: Ошибка в цикле мониторинга: {e}")
                time.sleep(1.0)
    
    def _scan_devices(self):
        """Сканирование подключенных устройств"""
        try:
            # Для Android используем USB Host API
            devices = self._get_android_usb_devices()
            
            for device in devices:
                device_id = device.get('device_id')
                if device_id and device_id not in self.devices:
                    # Новое устройство
                    device_type = self._identify_device_type(device)
                    if device_type:
                        otg_device = OTGDevice(
                            device_id=device_id,
                            device_type=device_type,
                            name=device.get('name', 'Unknown Device')
                        )
                        self.devices[device_id] = otg_device
                        Logger.info(f"OTGManager: Обнаружено устройство {device_type}: {device_id}")
                        
        except Exception as e:
            Logger.error(f"OTGManager: Ошибка сканирования устройств: {e}")
    
    def _get_android_usb_devices(self) -> List[Dict]:
        """Получение списка USB устройств через Android API"""
        devices = []
        
        try:
            # Используем Android USB Host API
            from android import usb
            
            # Получаем список подключенных устройств
            usb_devices = usb.get_device_list()
            
            for device in usb_devices:
                device_info = {
                    'device_id': device.get_device_name(),
                    'vendor_id': device.get_vendor_id(),
                    'product_id': device.get_product_id(),
                    'name': device.get_device_name(),
                    'manufacturer': device.get_manufacturer_name(),
                    'product': device.get_product_name()
                }
                devices.append(device_info)
                
        except ImportError:
            # Fallback для тестирования без Android
            Logger.warning("OTGManager: Android USB API недоступен, используем тестовые данные")
            devices = self._get_test_devices()
        except Exception as e:
            Logger.error(f"OTGManager: Ошибка получения USB устройств: {e}")
        
        return devices
    
    def _get_test_devices(self) -> List[Dict]:
        """Тестовые устройства для разработки"""
        return [
            {
                'device_id': 'test_esp32_001',
                'vendor_id': 0x10C4,
                'product_id': 0xEA60,
                'name': 'CP2102 USB to UART Bridge',
                'manufacturer': 'Silicon Labs',
                'product': 'CP2102'
            },
            {
                'device_id': 'test_camera_001',
                'vendor_id': 0x046D,
                'product_id': 0x0825,
                'name': 'USB Camera',
                'manufacturer': 'Logitech',
                'product': 'Webcam'
            }
        ]
    
    def _identify_device_type(self, device: Dict) -> Optional[str]:
        """Определение типа устройства"""
        vendor_id = device.get('vendor_id', 0)
        product_name = device.get('product', '').lower()
        
        for device_type, config in self.supported_devices.items():
            # Проверяем по vendor ID
            if vendor_id in config['vendor_ids']:
                return device_type
            
            # Проверяем по названию продукта
            for name in config['product_names']:
                if name.lower() in product_name:
                    return device_type
        
        return None
    
    def _check_device_status(self):
        """Проверка состояния подключенных устройств"""
        current_time = time.time()
        timeout = 10.0  # Таймаут в секундах
        
        for device_id, device in list(self.devices.items()):
            if current_time - device.last_seen > timeout:
                # Устройство не отвечает
                if device.connected:
                    device.connected = False
                    Logger.warning(f"OTGManager: Устройство {device_id} отключено")
            else:
                # Устройство активно
                if not device.connected:
                    device.connected = True
                    Logger.info(f"OTGManager: Устройство {device_id} подключено")
    
    def get_connected_devices(self) -> List[OTGDevice]:
        """Получение списка подключенных устройств"""
        return [device for device in self.devices.values() if device.connected]
    
    def get_device_by_type(self, device_type: str) -> List[OTGDevice]:
        """Получение устройств по типу"""
        return [
            device for device in self.devices.values() 
            if device.device_type == device_type and device.connected
        ]
    
    def connect_device(self, device_id: str) -> bool:
        """Подключение к устройству"""
        if device_id not in self.devices:
            Logger.error(f"OTGManager: Устройство {device_id} не найдено")
            return False
        
        device = self.devices[device_id]
        
        try:
            if device.device_type == 'esp32':
                return self._connect_esp32(device)
            elif device.device_type == 'camera':
                return self._connect_camera(device)
            else:
                Logger.warning(f"OTGManager: Неизвестный тип устройства: {device.device_type}")
                return False
                
        except Exception as e:
            Logger.error(f"OTGManager: Ошибка подключения к устройству {device_id}: {e}")
            return False
    
    def _connect_esp32(self, device: OTGDevice) -> bool:
        """Подключение к ESP32"""
        try:
            # Здесь будет код для подключения к ESP32 через USB Serial
            # Для Android это будет через USB Host API
            Logger.info(f"OTGManager: Подключение к ESP32: {device.device_id}")
            
            # Обновляем данные устройства
            device.update_data({
                'connection_status': 'connected',
                'baud_rate': 115200,
                'last_command': None
            })
            
            return True
            
        except Exception as e:
            Logger.error(f"OTGManager: Ошибка подключения к ESP32: {e}")
            return False
    
    def _connect_camera(self, device: OTGDevice) -> bool:
        """Подключение к USB камере"""
        try:
            Logger.info(f"OTGManager: Подключение к камере: {device.device_id}")
            
            # Обновляем данные устройства
            device.update_data({
                'connection_status': 'connected',
                'resolution': '640x480',
                'fps': 30
            })
            
            return True
            
        except Exception as e:
            Logger.error(f"OTGManager: Ошибка подключения к камере: {e}")
            return False
    
    def disconnect_device(self, device_id: str) -> bool:
        """Отключение от устройства"""
        if device_id not in self.devices:
            return False
        
        device = self.devices[device_id]
        device.connected = False
        
        Logger.info(f"OTGManager: Отключение от устройства: {device_id}")
        return True
    
    def disconnect_all(self):
        """Отключение от всех устройств"""
        for device_id in list(self.devices.keys()):
            self.disconnect_device(device_id)
        
        Logger.info("OTGManager: Отключение от всех устройств")
    
    def send_command(self, device_id: str, command: str) -> bool:
        """Отправка команды устройству"""
        if device_id not in self.devices:
            return False
        
        device = self.devices[device_id]
        if not device.connected:
            return False
        
        try:
            if device.device_type == 'esp32':
                return self._send_esp32_command(device, command)
            else:
                Logger.warning(f"OTGManager: Отправка команд не поддерживается для {device.device_type}")
                return False
                
        except Exception as e:
            Logger.error(f"OTGManager: Ошибка отправки команды: {e}")
            return False
    
    def _send_esp32_command(self, device: OTGDevice, command: str) -> bool:
        """Отправка команды ESP32"""
        try:
            # Здесь будет код для отправки команды через USB Serial
            Logger.info(f"OTGManager: Отправка команды ESP32: {command}")
            
            # Обновляем данные устройства
            device.update_data({
                'last_command': command,
                'last_command_time': time.time()
            })
            
            return True
            
        except Exception as e:
            Logger.error(f"OTGManager: Ошибка отправки команды ESP32: {e}")
            return False