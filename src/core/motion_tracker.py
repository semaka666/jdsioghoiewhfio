#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль детекции движения для Android
Адаптированная версия оригинального трекера
"""

import cv2
import numpy as np
import threading
import time
from typing import Dict, List, Tuple, Optional
from kivy.logger import Logger

class MotionTracker:
    """Класс для детекции движения на Android"""
    
    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self.camera = None
        self.background_subtractor = None
        self.motion_detected = False
        self.motion_history = []
        self.max_history = 50
        
        # Статистика
        self.stats = {
            'frames_processed': 0,
            'motion_detections': 0,
            'fps': 0,
            'last_motion_time': 0
        }
        
        # Настройки детекции
        self.sensitivity = 50  # Чувствительность (0-100)
        self.min_area = 500   # Минимальная площадь для детекции
        
        # Поток обработки
        self.processing_thread = None
        self.stop_event = threading.Event()
        
        Logger.info("MotionTracker: Инициализирован")
    
    def initialize_camera(self, camera_index: int = 0) -> bool:
        """Инициализация камеры"""
        try:
            # Для Android используем Camera API через Kivy
            from kivy.core.camera import Camera as KivyCamera
            
            self.camera = KivyCamera(index=camera_index, resolution=(640, 480))
            self.camera.play = True
            
            # Инициализируем детектор фона
            self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
                detectShadows=True,
                varThreshold=50
            )
            
            Logger.info(f"MotionTracker: Камера {camera_index} инициализирована")
            return True
            
        except Exception as e:
            Logger.error(f"MotionTracker: Ошибка инициализации камеры: {e}")
            return False
    
    def start(self) -> bool:
        """Запуск трекинга движения"""
        if self.is_running:
            Logger.warning("MotionTracker: Трекинг уже запущен")
            return False
        
        if not self.camera:
            Logger.error("MotionTracker: Камера не инициализирована")
            return False
        
        self.is_running = True
        self.stop_event.clear()
        
        # Запускаем поток обработки
        self.processing_thread = threading.Thread(target=self._processing_loop)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        Logger.info("MotionTracker: Трекинг запущен")
        return True
    
    def stop(self):
        """Остановка трекинга движения"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.stop_event.set()
        
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=2.0)
        
        if self.camera:
            self.camera.play = False
        
        Logger.info("MotionTracker: Трекинг остановлен")
    
    def pause(self):
        """Приостановка трекинга"""
        self.is_paused = True
        Logger.info("MotionTracker: Трекинг приостановлен")
    
    def resume(self):
        """Возобновление трекинга"""
        self.is_paused = False
        Logger.info("MotionTracker: Трекинг возобновлен")
    
    def _processing_loop(self):
        """Основной цикл обработки кадров"""
        frame_count = 0
        start_time = time.time()
        
        while self.is_running and not self.stop_event.is_set():
            if self.is_paused:
                time.sleep(0.1)
                continue
            
            try:
                # Получаем кадр от камеры
                if not self.camera or not self.camera.texture:
                    time.sleep(0.033)  # ~30 FPS
                    continue
                
                # Конвертируем текстуру Kivy в numpy array
                frame = self._texture_to_numpy(self.camera.texture)
                if frame is None:
                    continue
                
                # Обрабатываем кадр
                motion_detected = self._process_frame(frame)
                
                # Обновляем статистику
                frame_count += 1
                self.stats['frames_processed'] = frame_count
                
                if motion_detected:
                    self.stats['motion_detections'] += 1
                    self.stats['last_motion_time'] = time.time()
                
                # Вычисляем FPS каждые 30 кадров
                if frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    self.stats['fps'] = frame_count / elapsed if elapsed > 0 else 0
                
                # Контроль FPS
                time.sleep(0.033)  # ~30 FPS
                
            except Exception as e:
                Logger.error(f"MotionTracker: Ошибка в цикле обработки: {e}")
                time.sleep(0.1)
    
    def _texture_to_numpy(self, texture) -> Optional[np.ndarray]:
        """Конвертация текстуры Kivy в numpy array"""
        try:
            if not texture:
                return None
            
            # Получаем данные текстуры
            pixels = texture.pixels
            if not pixels:
                return None
            
            # Конвертируем в numpy array
            # Kivy использует формат RGBA, OpenCV ожидает BGR
            width, height = texture.size
            frame = np.frombuffer(pixels, dtype=np.uint8)
            frame = frame.reshape((height, width, 4))  # RGBA
            
            # Конвертируем RGBA в BGR
            frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
            
            return frame
            
        except Exception as e:
            Logger.error(f"MotionTracker: Ошибка конвертации текстуры: {e}")
            return None
    
    def _process_frame(self, frame: np.ndarray) -> bool:
        """Обработка кадра для детекции движения"""
        try:
            # Применяем детектор фона
            fg_mask = self.background_subtractor.apply(frame)
            
            # Морфологические операции для очистки маски
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
            
            # Находим контуры
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            motion_detected = False
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > self.min_area:
                    motion_detected = True
                    break
            
            # Обновляем историю движения
            self.motion_history.append(motion_detected)
            if len(self.motion_history) > self.max_history:
                self.motion_history.pop(0)
            
            self.motion_detected = motion_detected
            return motion_detected
            
        except Exception as e:
            Logger.error(f"MotionTracker: Ошибка обработки кадра: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Получение статистики трекинга"""
        return self.stats.copy()
    
    def get_motion_status(self) -> bool:
        """Получение текущего статуса движения"""
        return self.motion_detected
    
    def set_sensitivity(self, value: int):
        """Установка чувствительности детекции (0-100)"""
        self.sensitivity = max(0, min(100, value))
        # Адаптируем параметры детектора под чувствительность
        if self.background_subtractor:
            threshold = int(50 * (100 - self.sensitivity) / 100)
            self.background_subtractor.setVarThreshold(threshold)
    
    def set_min_area(self, value: int):
        """Установка минимальной площади для детекции"""
        self.min_area = max(100, value)
    
    def get_motion_history(self) -> List[bool]:
        """Получение истории движения"""
        return self.motion_history.copy()