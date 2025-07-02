"""
API маршруты для String Storage приложения
"""

from flask import Blueprint, request, jsonify
from database import DatabaseManager
from typing import Tuple, Dict, Any

# Создаем Blueprint для API маршрутов
api_bp = Blueprint('api', __name__)

# Инициализируем менеджер базы данных
db_manager = DatabaseManager()


def create_error_response(message: str, status_code: int) -> Tuple[Dict[str, str], int]:
    """
    Создание стандартизированного ответа об ошибке
    
    Args:
        message: Текст ошибки
        status_code: HTTP код ошибки
        
    Returns:
        Tuple с JSON ответом и статус кодом
    """
    return jsonify({'error': message}), status_code


def create_success_response(data: Dict[str, Any], status_code: int = 200) -> Tuple[Dict[str, Any], int]:
    """
    Создание стандартизированного успешного ответа
    
    Args:
        data: Данные для ответа
        status_code: HTTP код успеха
        
    Returns:
        Tuple с JSON ответом и статус кодом
    """
    return jsonify(data), status_code


@api_bp.route('/store', methods=['POST'])
def store_string():
    """
    Сохраняет строку под индексом из параметров запроса
    Параметры: ?index=<значение>&data=<строка>
    """
    try:
        # Получаем параметры из запроса
        index = request.args.get('index')
        if index is None:
            return create_error_response('Параметр index не найден', 400)
        
        data = request.args.get('data')
        if not data:
            return create_error_response('Параметр data не найден или пустой', 400)
        
        # Сохраняем в базе данных
        result = db_manager.store_string(index, data)
        
        return create_success_response(result, result['status_code'])
    
    except Exception as e:
        return create_error_response(str(e), 500)


@api_bp.route('/get', methods=['GET'])
def get_string():
    """
    Возвращает строку по индексу из параметров запроса
    Параметры: ?index=<значение>
    """
    try:
        # Получаем индекс из параметров запроса
        index = request.args.get('index')
        if index is None:
            return create_error_response('Параметр index не найден', 400)
        
        # Получаем данные из базы
        result = db_manager.get_string(index)
        
        if result is None:
            return create_error_response(f'Строка с индексом "{index}" не найдена', 404)
        
        return create_success_response(result)
    
    except Exception as e:
        return create_error_response(str(e), 500)


@api_bp.route('/list', methods=['GET'])
def list_indices():
    """
    Возвращает список всех доступных индексов
    """
    try:
        indices = db_manager.list_all_indices()
        
        response_data = {
            'indices': indices,
            'count': len(indices)
        }
        
        return create_success_response(response_data)
    
    except Exception as e:
        return create_error_response(str(e), 500)


@api_bp.route('/delete', methods=['DELETE'])
def delete_string():
    """
    Удаляет строку по индексу из параметров запроса
    Параметры: ?index=<значение>
    """
    try:
        # Получаем индекс из параметров запроса
        index = request.args.get('index')
        if index is None:
            return create_error_response('Параметр index не найден', 400)
        
        # Удаляем из базы данных
        success = db_manager.delete_string(index)
        
        if not success:
            return create_error_response(f'Строка с индексом "{index}" не найдена', 404)
        
        response_data = {
            'message': f'Строка с индексом "{index}" удалена'
        }
        
        return create_success_response(response_data)
    
    except Exception as e:
        return create_error_response(str(e), 500)


@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Статистика базы данных
    """
    try:
        stats = db_manager.get_statistics()
        return create_success_response(stats)
    
    except Exception as e:
        return create_error_response(str(e), 500)


@api_bp.route('/', methods=['GET'])
def info():
    """
    Информация о доступных endpoint'ах
    """
    info_data = {
        'message': 'String Storage API with SQLite',
        'database': db_manager.database_path,
        'endpoints': {
            'POST /store?index=<key>&data=<value>': 'Сохранить строку',
            'GET /get?index=<key>': 'Получить строку',
            'GET /list': 'Список всех индексов с метаданными',
            'DELETE /delete?index=<key>': 'Удалить строку',
            'GET /stats': 'Статистика базы данных'
        },
        'usage': 'Используйте параметры запроса index и data'
    }
    
    return create_success_response(info_data)