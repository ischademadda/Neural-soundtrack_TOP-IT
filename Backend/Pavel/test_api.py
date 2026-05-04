import requests
import json

URL = "http://127.0.0.1:8000/api/search/"

def test_query(query_text):
    print(f"Запрос: {query_text}")
    
    try:
        response = requests.post(
            URL,
            headers={"Content-Type": "application/json"},
            json={"query": query_text},
            timeout=30
        )
        
        print(f"Статус код: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nОтвет сервера:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        
        elif response.status_code == 400:
            print(f"\nОшибка 400: Неверный формат запроса")
            print(response.text)
        
        elif response.status_code == 429:
            print(f"\n️Ошибка 429: Превышен лимит запросов")
            print(response.text)
        
        elif response.status_code == 500:
            print(f"\nОшибка 500: Внутренняя ошибка сервера")
            print(response.text)
        
        elif response.status_code == 503:
            print(f"\nОшибка 503: Сервис недоступен")
            print(response.text)
        
        elif response.status_code == 504:
            print(f"\nОшибка 504: Превышено время ожидания")
            print(response.text)
        
        else:
            print(f"\nОшибка {response.status_code}:")
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("Ошибка: Превышено время ожидания (30 сек)")
    except requests.exceptions.ConnectionError:
        print("Ошибка: Не удалось подключиться к серверу")
        print("Убедитесь, что сервер запущен: python manage.py runserver")
    except Exception as e:
        print(f"Ошибка: {e}")

# тест
if __name__ == "__main__":
    print("\nТЕСТИРОВАНИЕ НЕЙРО-САУНДТРЕК")
    
    test_query("песни для утренней пробежки")
    
    print("Тестирование завершено!")