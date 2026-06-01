import json
from datetime import datetime

MUSIC_KEYWORDS = [
    'трек', 'песня', 'исполнитель', 'плейлист', 'музыка', 
    'слушать', 'track', 'song', 'artist', 'playlist', 'music',
    'жанр', 'альбом', 'мелодия', 'ритм', 'звук', 'басс', 'чарт',
    'композиция', 'sound', 'артист', 'сингл', 'фит', 'feat'
]


def validate_music_response(response_text):
    
    if "FILTERED_NO_MUSIC" in response_text: # Проверка на спец-метку фильтрации
        log_validation_result("FILTERED", response_text[:50])
        return False, "По вашему запросу ничего не найдено"
    
    response_lower = response_text.lower()
    if not any(keyword in response_lower for keyword in MUSIC_KEYWORDS): # Проверка на наличие музыкальных ключевых слов
        log_validation_result("NO_KEYWORDS", response_text[:50])
        return False, "По вашему запросу ничего не найдено"
    
    try: # Попытка распарсить JSON
        clean_response = response_text.strip() # Отчистка ответа от возможных markdown-оберток
        if clean_response.startswith('```json'):
            clean_response = clean_response.replace('```json', '').replace('```', '').strip()
        elif clean_response.startswith('```'):
            clean_response = clean_response.replace('```', '').strip()
        
        data = json.loads(clean_response)
        
        tracks = data.get('tracks', []) # Проверка структуры
        playlists = data.get('playlists', [])
        
        if len(tracks) != 6:
            log_validation_result("WRONG_TRACKS", f"tracks={len(tracks)}")
            return False, f"Ошибка формата ответа (треки): нужно 6, получено {len(tracks)}"
        
        if len(playlists) != 2:
            log_validation_result("WRONG_PLAYLISTS", f"playlists={len(playlists)}")
            return False, f"Ошибка формата ответа (плейлисты): нужно 2, получено {len(playlists)}"
        
        for track in tracks:
            if 'link' not in track or 'music.yandex.ru' not in track.get('link', ''):
                log_validation_result("BAD_TRACK_LINK", track.get('link', 'no link'))
                return False, "Ошибка формата ссылок на треки"
        
        for playlist in playlists:
            if 'link' not in playlist or 'music.yandex.ru' not in playlist.get('link', ''):
                log_validation_result("BAD_PLAYLIST_LINK", playlist.get('link', 'no link'))
                return False, "Ошибка формата ссылок на плейлисты"
        
        log_validation_result("SUCCESS", f"tracks={len(tracks)}, playlists={len(playlists)}")
        return True, data
        
    except json.JSONDecodeError as e:
        log_validation_result("JSON_ERROR", str(e)[:50])
        return False, "Ошибка обработки ответа (не JSON)"
    except Exception as e:
        log_validation_result("EXCEPTION", str(e)[:50])
        return False, "Ошибка обработки ответа"


def log_validation_result(status, details):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {status}: {details}\n"
    
    try: # Пишем в файл лога
        with open("logs/validation.log", "a", encoding="utf-8") as f:
            f.write(log_entry)
    except:
        pass
    
    print(f"Валидация: {status}")