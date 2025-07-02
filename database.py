"""
Модуль для работы с базой данных SQLite
"""

import sqlite3
import os
from typing import Optional, List, Dict, Any
from datetime import datetime


class DatabaseManager:
    """Класс для управления базой данных"""
    
    def __init__(self, database_path: str = 'strings.db'):
        self.database_path = database_path
        self.init_database()
    
    def init_database(self) -> None:
        """Инициализация базы данных и создание таблиц"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                index_key TEXT UNIQUE NOT NULL,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self) -> sqlite3.Connection:
        """Получение подключения к базе данных"""
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def store_string(self, index: str, data: str) -> Dict[str, Any]:
        """
        Сохранение или обновление строки
        
        Args:
            index: Индекс записи
            data: Данные для сохранения
            
        Returns:
            Dict с информацией о результате операции
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Пытаемся вставить новую запись
            cursor.execute('''
                INSERT INTO strings (index_key, data) 
                VALUES (?, ?)
            ''', (index, data))
            
            result = {
                'action': 'created',
                'message': f'Строка сохранена под индексом "{index}"',
                'status_code': 201
            }
            
        except sqlite3.IntegrityError:
            # Если индекс уже существует, обновляем запись
            cursor.execute('''
                UPDATE strings 
                SET data = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE index_key = ?
            ''', (data, index))
            
            result = {
                'action': 'updated',
                'message': f'Строка обновлена под индексом "{index}"',
                'status_code': 200
            }
        
        conn.commit()
        conn.close()
        
        result.update({
            'index': index,
            'length': len(data)
        })
        
        return result
    
    def get_string(self, index: str) -> Optional[Dict[str, Any]]:
        """
        Получение строки по индексу
        
        Args:
            index: Индекс записи
            
        Returns:
            Dict с данными записи или None если не найдена
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT index_key, data, created_at, updated_at 
            FROM strings 
            WHERE index_key = ?
        ''', (index,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return None
        
        return {
            'index': row['index_key'],
            'data': row['data'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
    
    def delete_string(self, index: str) -> bool:
        """
        Удаление строки по индексу
        
        Args:
            index: Индекс записи
            
        Returns:
            True если запись была удалена, False если не найдена
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Проверяем существование записи
        cursor.execute('SELECT COUNT(*) FROM strings WHERE index_key = ?', (index,))
        count = cursor.fetchone()[0]
        
        if count == 0:
            conn.close()
            return False
        
        # Удаляем запись
        cursor.execute('DELETE FROM strings WHERE index_key = ?', (index,))
        conn.commit()
        conn.close()
        
        return True
    
    def list_all_indices(self) -> List[Dict[str, Any]]:
        """
        Получение списка всех индексов с метаданными
        
        Returns:
            List словарей с информацией о записях
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT index_key, created_at, updated_at, LENGTH(data) as data_length
            FROM strings 
            ORDER BY created_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        indices = []
        for row in rows:
            indices.append({
                'index': row['index_key'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'data_length': row['data_length']
            })
        
        return indices
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Получение статистики базы данных
        
        Returns:
            Dict со статистикой
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Общее количество записей
        cursor.execute('SELECT COUNT(*) as count FROM strings')
        total_count = cursor.fetchone()['count']
        
        # Общий размер данных
        cursor.execute('SELECT SUM(LENGTH(data)) as total_size FROM strings')
        total_size = cursor.fetchone()['total_size'] or 0
        
        # Последняя запись
        cursor.execute('''
            SELECT index_key, created_at 
            FROM strings 
            ORDER BY created_at DESC 
            LIMIT 1
        ''')
        latest = cursor.fetchone()
        
        conn.close()
        
        stats = {
            'total_records': total_count,
            'total_data_size': total_size,
            'database_file': self.database_path,
            'database_exists': os.path.exists(self.database_path)
        }
        
        if latest:
            stats['latest_record'] = {
                'index': latest['index_key'],
                'created_at': latest['created_at']
            }
        
        return stats