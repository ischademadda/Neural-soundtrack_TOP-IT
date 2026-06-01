from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os

from .prompts import SYSTEM_PROMPT
from .utils.validation import validate_music_response

USE_MOCK_SERVICE = os.getenv('USE_MOCK_SERVICE', 'False').lower() == 'true' # Проверка режима работы

if USE_MOCK_SERVICE:
    from .services.mock_gigachat_service import MockGigaChatService
    print("Режим: Mock")
else:
    from .services.gigachat_service import GigaChatService
    print("Режим: GigaChat API")


@csrf_exempt
@require_http_methods(["POST"])
def music_search(request):
    
    try: # Парсинг запроса
        body = json.loads(request.body)
        user_query = body.get('query', '').strip()
        
        if not user_query:
            return JsonResponse({
                "status": "error",
                "message": "Пустой запрос"
            }, status=400)
        
        print(f"\nЗапрос: {user_query}")
        
        if USE_MOCK_SERVICE: # Создание сервиса
            service = MockGigaChatService()
        else:
            service = GigaChatService()
        
        result = service.get_music_recommendation(user_query, SYSTEM_PROMPT) # Получение рекомендации
        
        if result["status"] == "error": # Обработка ошибок от сервиса
            message = result.get('message', 'Ошибка сервиса')
            error_code = result.get('code', 'UNKNOWN')
            
            print(f"Ошибка сервиса: {message} (код: {error_code})")
            
            if error_code == "TIMEOUT": # разные статусы в зависимости от ошибки
                return JsonResponse({
                    "status": "error",
                    "message": "Превышено время ожидания ответа от сервиса"
                }, status=504)  # Gateway Timeout
            
            elif error_code == "CONNECTION_ERROR":
                return JsonResponse({
                    "status": "error",
                    "message": "Не удалось подключиться к сервису рекомендаций"
                }, status=503)  # Service Unavailable
            
            elif error_code in ["FORBIDDEN", "UNAUTHORIZED", "AUTH_ERROR"]:
                return JsonResponse({
                    "status": "error",
                    "message": "Ошибка авторизации сервиса"
                }, status=500)
            
            elif error_code == "RATE_LIMIT":
                return JsonResponse({
                    "status": "error",
                    "message": "Превышен лимит запросов, попробуйте позже"
                }, status=429)  # Too Many Requests
            
            else:
                return JsonResponse({
                    "status": "error",
                    "message": message
                }, status=500)
        
        is_valid, validation_result = validate_music_response(result["data"]) # Валидация ответа
        
        if not is_valid:
            print(f"Валидация не прошла: {validation_result}")
            return JsonResponse({
                "status": "success",
                "data": {"message": validation_result}
            })
        
        print("Успешный ответ!")
        return JsonResponse({
            "status": "success",
            "data": validation_result
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            "status": "error",
            "message": "Неверный формат запроса"
        }, status=400)
    
    except Exception as e:
        print(f"Ошибка в music_search: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            "status": "error",
            "message": "Внутренняя ошибка сервера"
        }, status=500)