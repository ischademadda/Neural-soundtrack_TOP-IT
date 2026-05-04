# core/services/mock_gigachat_service.py
import json
import random
import time

class MockGigaChatService:
    """Имитация GigaChat API для разработки"""
    
    MUSIC_RESPONSES = {
        "пробежка": {
            "tracks": [
                {"name": "Eye of the Tiger", "artist": "Survivor", "link": "https://music.yandex.ru/album/1234/track/5678"},
                {"name": "Stronger", "artist": "Kanye West", "link": "https://music.yandex.ru/album/2345/track/6789"},
                {"name": "Can't Hold Us", "artist": "Macklemore", "link": "https://music.yandex.ru/album/3456/track/7890"}
            ],
            "playlists": [
                {"name": "Running Motivation", "link": "https://music.yandex.ru/users/runner/playlists/111"},
                {"name": "Cardio Power", "link": "https://music.yandex.ru/users/runner/playlists/222"}
            ]
        },
        "дождь": {
            "tracks": [
                {"name": "Rainy Day", "artist": "Chill Hop", "link": "https://music.yandex.ru/album/4567/track/8901"},
                {"name": "Blue Monday", "artist": "New Order", "link": "https://music.yandex.ru/album/5678/track/9012"},
                {"name": "November Rain", "artist": "Guns N' Roses", "link": "https://music.yandex.ru/album/6789/track/0123"}
            ],
            "playlists": [
                {"name": "Rainy Mood", "link": "https://music.yandex.ru/users/chill/playlists/333"},
                {"name": "Melancholy Vibes", "link": "https://music.yandex.ru/users/chill/playlists/444"}
            ]
        },
        "рок": {
            "tracks": [
                {"name": "Bohemian Rhapsody", "artist": "Queen", "link": "https://music.yandex.ru/album/7890/track/1234"},
                {"name": "Stairway to Heaven", "artist": "Led Zeppelin", "link": "https://music.yandex.ru/album/8901/track/2345"},
                {"name": "Sweet Child O' Mine", "artist": "Guns N' Roses", "link": "https://music.yandex.ru/album/9012/track/3456"}
            ],
            "playlists": [
                {"name": "Classic Rock", "link": "https://music.yandex.ru/users/rock/playlists/555"},
                {"name": "Rock Legends", "link": "https://music.yandex.ru/users/rock/playlists/666"}
            ]
        }
    }
    
    def get_music_recommendation(self, user_query, system_prompt):
        """Имитирует ответ GigaChat"""
        time.sleep(1)  # Имитация задержки сети
        
        query_lower = user_query.lower()
        
        # Проверка на музыкальные ключевые слова
        music_keywords = ['музыка', 'песня', 'трек', 'плейлист', 'слушать', 'рок', 'поп', 'джаз']
        
        if not any(keyword in query_lower for keyword in music_keywords):
            # Нецелевой запрос
            return {
                "status": "success",
                "data": "FILTERED_NO_MUSIC"
            }
        
        # Ищем подходящий ответ
        for keyword, response in self.MUSIC_RESPONSES.items():
            if keyword in query_lower:
                return {
                    "status": "success",
                    "data": json.dumps(response, ensure_ascii=False)
                }
        
        # Дефолтный ответ для любых музыкальных запросов
        return {
            "status": "success",
            "data": json.dumps(self.MUSIC_RESPONSES["рок"], ensure_ascii=False)
        }