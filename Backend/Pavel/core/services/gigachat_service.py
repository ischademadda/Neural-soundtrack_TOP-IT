import requests
import base64
import os
import uuid
import warnings
from dotenv import load_dotenv
from urllib3.exceptions import InsecureRequestWarning

warnings.simplefilter('ignore', InsecureRequestWarning) # Отключение предупреждения о сертификатах
load_dotenv()


class GigaChatService:
    
    def __init__(self):
        self.auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        self.chat_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        self.models_url = "https://gigachat.devices.sberbank.ru/api/v1/models"
        
        self.client_id = os.getenv('GIGACHAT_CLIENT_ID')
        self.client_secret = os.getenv('GIGACHAT_CLIENT_SECRET')
        self.access_token = None
    
    def _get_auth_header(self):
        
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        return f"Basic {encoded}"
    
    def _generate_rquid(self):
        return str(uuid.uuid4()) # уникальный UUID для каждого запроса
    
    def get_access_token(self):
        try:
            print("Получение токена авторизации...")
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'RqUID': self._generate_rquid(),
                'Authorization': self._get_auth_header()
            }
            
            payload = {
                'scope': 'GIGACHAT_API_PERS'
            }
            
            response = requests.post(
                self.auth_url,
                headers=headers,
                data=payload,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                print(f"Токен получен: {self.access_token[:30]}...")
                return self.access_token
            else:
                print(f"Ошибка авторизации: {response.status_code}")
                print(f"Ответ: {response.text}")
                return None
                
        except Exception as e:
            print(f"Исключение при получении токена: {type(e).__name__}: {e}")
            return None
    
    def send_chat_request(self, user_message, system_prompt):
    
        if not self.access_token:
            self.get_access_token()
        
        if not self.access_token:
            return {"error": "Не удалось авторизоваться в GigaChat", "code": "AUTH_ERROR"}
        
        try:
            print(f"Отправка запроса к чату...")
            print(f"URL: {self.chat_url}")
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.access_token}'
            }
            
            payload = {
                "model": "GigaChat-2-Max",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.5,
                "top_p": 0.1,
                "n": 1,
                "profanity_check": True
            }
            
            response = requests.post(
                self.chat_url,
                headers=headers,
                json=payload,
                verify=False,
                timeout=30
            )
            
            print(f"Статус ответа: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'choices' in data and len(data['choices']) > 0:
                    answer = data['choices'][0]['message']['content']
                    print("Ответ получен успешно!")
                    return {"success": True, "response": answer}
                else:
                    print("Неверная структура ответа")
                    return {"error": "Неверная структура ответа API", "code": "INVALID_RESPONSE"}
            
            else:
                print(f"Ошибка запроса: {response.status_code}")
                print(f"Ответ сервера: {response.text[:200]}")
                
                if response.status_code == 403:
                    return {"error": "Chat API не активирован (403 Forbidden)", "code": "FORBIDDEN"}
                elif response.status_code == 401:
                    return {"error": "Неверный токен авторизации (401)", "code": "UNAUTHORIZED"}
                elif response.status_code == 400:
                    return {"error": "Неверный формат запроса (400)", "code": "BAD_REQUEST"}
                elif response.status_code == 429:
                    return {"error": "Превышен лимит запросов (429)", "code": "RATE_LIMIT"}
                elif response.status_code >= 500:
                    return {"error": "Ошибка сервера GigaChat (500)", "code": "SERVER_ERROR"}
                else:
                    return {"error": f"Ошибка API: {response.status_code}", "code": "API_ERROR"}
                    
        except requests.exceptions.Timeout:
            print("Превышено время ожидания (30 сек)")
            return {"error": "Превышено время ожидания ответа от сервиса", "code": "TIMEOUT"}
        
        except requests.exceptions.ConnectionError as e:
            print(f"Ошибка подключения: {e}")
            return {"error": "Не удалось подключиться к серверу GigaChat", "code": "CONNECTION_ERROR"}
        
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {type(e).__name__}: {e}")
            return {"error": "Ошибка сети при отправке запроса", "code": "NETWORK_ERROR"}
        
        except Exception as e:
            print(f"Неожиданная ошибка: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return {"error": f"Внутренняя ошибка: {str(e)}", "code": "INTERNAL_ERROR"}
    
    def get_music_recommendation(self, user_query, system_prompt):
        
        result = self.send_chat_request(user_query, system_prompt)
        
        if result.get("error"):
            return {
                "status": "error",
                "message": "Ошибка сервиса рекомендаций"
            }
        
        return {
            "status": "success",
            "data": result["response"]
        }