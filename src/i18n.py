TRANSLATIONS = {
    "en": {
        "title": "Discord Orbs Earner",
        "fetch": "Fetching from Discord API...",
        "filter": "Filter games...",
        "reload": "Reload",
        "ready": "Supported Windows Games: {}",
        "settings_title": "Settings: {}",
        "settings_desc": "Configure spoofing for this game.",
        "settings_exe": "Executable Name:",
        "settings_window": "Window Title (Optional):",
        "btn_apply": "APPLY",
        "btn_close": "CLOSE",
        "btn_play": "Play",
        "btn_stop": "Stop",
        "btn_settings": "Settings",
        "active_games": "Active Games",
        "system_log": "Live System Log",
        "log_fetching": "Starting to fetch data from Discord API...",
        "log_fetch_success": "Successfully loaded {} games from Discord API.",
        "log_fetch_fail": "Failed to connect to Discord API. Using offline cache.",
        "log_spoof_start": "Started spoofing '{}' with executable '{}'...",
        "log_spoof_stop": "Stopped spoofing '{}'.",
        "log_spoof_fail": "Failed to start spoofing for '{}'.",
        "log_spoof_fail_err": "Failed to start spoofing for '{}'. Error: {}",
        "log_filtering": "Filtering games by: '{}'",
        "log_lang_change": "Language changed to {}",
        "log_settings_open": "Opened settings for: {}",
        "log_settings_apply": "Applied new settings for: {}",
        "cli_choose_lang": "Choose language / Выберите язык",
        "cli_choose_action": "Choose an action",
        "cli_search_game": "Enter game name to search",
        "cli_no_games": "No games found matching your search.",
        "cli_enter_id": "Enter the ID of the game you want to run (or 0 to go back)",
        "cli_active_games": "--- Active Games ---",
        "cli_no_active": "No active games running.",
        "cli_stop_prompt": "Enter index of game to stop (or 0 to cancel)",
        "cli_sys_log": "--- Live System Log ---",
        "more_games": "... and {} more. Use search to refine."
    },
    "ru": {
        "title": "Discord Orbs Earner",
        "fetch": "Получение данных с Discord API...",
        "filter": "Поиск игр...",
        "reload": "Обновить",
        "ready": "Поддерживаемых игр для Windows: {}",
        "settings_title": "Настройки: {}",
        "settings_desc": "Настройте параметры запуска для этой игры.",
        "settings_exe": "Исполняемый файл:",
        "settings_window": "Название окна (необязательно):",
        "btn_apply": "ПРИМЕНИТЬ",
        "btn_close": "ЗАКРЫТЬ",
        "btn_play": "Играть",
        "btn_stop": "Стоп",
        "btn_settings": "Настройки",
        "active_games": "Запущенные игры",
        "system_log": "Системный лог",
        "log_fetching": "Запрос данных из Discord API...",
        "log_fetch_success": "Успешно загружено {} игр из Discord API.",
        "log_fetch_fail": "Не удалось подключиться к API. Используется кэш.",
        "log_spoof_start": "Спуфинг '{}' запущен (файл: '{}')...",
        "log_spoof_stop": "Спуфинг '{}' остановлен.",
        "log_spoof_fail": "Ошибка запуска спуфинга для '{}'.",
        "log_spoof_fail_err": "Ошибка запуска спуфинга для '{}'. Ошибка: {}",
        "log_filtering": "Поиск игр по запросу: '{}'",
        "log_lang_change": "Язык изменен на {}",
        "log_settings_open": "Открыты настройки для: {}",
        "log_settings_apply": "Применены новые настройки для: {}",
        "cli_choose_lang": "Выберите язык / Choose language",
        "cli_choose_action": "Выберите действие",
        "cli_search_game": "Введите название игры для поиска",
        "cli_no_games": "По вашему запросу игр не найдено.",
        "cli_enter_id": "Введите ID игры для запуска (или 0 для возврата)",
        "cli_active_games": "--- Запущенные игры ---",
        "cli_no_active": "Нет запущенных игр.",
        "cli_stop_prompt": "Введите индекс игры для остановки (или 0 для отмены)",
        "cli_sys_log": "--- Системный лог ---",
        "more_games": "... и еще {}. Используйте поиск для уточнения."
    }
}

class I18n:
    def __init__(self, lang="ru"):
        self.set_lang(lang)

    def set_lang(self, lang):
        if lang not in TRANSLATIONS:
            lang = "en"
        self.lang = lang
        
    def get(self, key, *args):
        text = TRANSLATIONS[self.lang].get(key, key)
        if args:
            try:
                return text.format(*args)
            except:
                return text
        return text

# Global i18n instance
t = I18n()
