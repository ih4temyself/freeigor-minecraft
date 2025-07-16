import json
import time

JSON_FILE = 'users.json'

class UserManager:
    def __init__(self, json_file=JSON_FILE):
        self.json_file = json_file
        self.users = self.load_json()
    
    def load_json(self):
        try:
            with open(self.json_file, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_json(self):
        try:
            with open(self.json_file, 'w') as file:
                json.dump(self.users, file, indent=2)
            return True
        except Exception as e:
            print(f"Error saving JSON: {str(e)}")
            return False
    
    def parse_user_json(self, json_data):
        try:
            if isinstance(json_data, str):
                data = json.loads(json_data)
            else:
                data = json_data

            users = {}
            for user_id, info in data.items():
                users[user_id] = {
                    'name': info.get('name', ''),
                    'admin': info.get('admin', 'False') == 'True',
                    'balance': int(info.get('balance', 0)), 
                    'usages_per_hour': int(info.get('usages_per_hour', 0)),
                    'last_reset': float(info.get('last_reset', 0)),  # Время последнего сброса
                    'current_usages': int(info.get('current_usages', 0))  # Текущий счетчик команд
                }
            return users
        except json.JSONDecodeError:
            print("Error: Invalid JSON format")
            return {}
        except Exception as e:
            print(f"Error parsing JSON: {str(e)}")
            return {}
    
    def is_admin(self, user_id):
        self.users = self.load_json()
        user_id = str(user_id)
        return self.users.get(user_id, {}).get('admin', False)
    
    def get_param(self, user_id, param):
        self.users = self.load_json()
        user_id = str(user_id)
        return self.users.get(user_id, {}).get(param)
    
    def update_param(self, user_id: int, param: str, value):
        self.users = self.load_json()
        user_id = str(user_id)
        if user_id in self.users:
            if param in ['balance', 'usages_per_hour', 'current_usages']:
                self.users[user_id][param] = int(value)
            elif param == 'admin':
                self.users[user_id][param] = str(value).lower() == 'true'
            elif param == 'last_reset':
                self.users[user_id][param] = float(value)
            else:
                self.users[user_id][param] = value
            self.save_json()
            return True
        return False
    
    def check_and_add_user(self, user_id, username="unknown"):
        self.users = self.load_json()
        user_id = str(user_id)
        if user_id not in self.users:
            new_user = {
                'name': username,
                'admin': False,
                'balance': 0,
                'usages_per_hour': 30,
                'last_reset': time.time(),  # Текущее время для сброса
                'current_usages': 0  # Начальный счетчик
            }
            self.users[user_id] = new_user
            self.save_json()
    
    def check_usage_limit(self, user_id):
        """Проверяет и обновляет лимит команд."""
        self.users = self.load_json()
        user_id = str(user_id)
        if user_id not in self.users:
            return False, "Пользователь не найден."

        if self.is_admin(user_id):
            return True, "Администраторы не имеют лимита."

        current_time = time.time()
        last_reset = self.users[user_id].get('last_reset', current_time)
        current_usages = self.users[user_id].get('current_usages', 0)
        max_usages = self.users[user_id].get('usages_per_hour', 30)

        # Проверяем, прошел ли час с последнего сброса
        if current_time - last_reset >= 3600:  # 3600 секунд = 1 час
            self.users[user_id]['current_usages'] = 0
            self.users[user_id]['last_reset'] = current_time
            self.save_json()
            current_usages = 0

        if current_usages >= max_usages:
            return False, f"Лимит команд ({max_usages} в час) исчерпан. Подождите до следующего часа."

        # Увеличиваем счетчик использованных команд
        self.users[user_id]['current_usages'] = current_usages + 1
        self.save_json()
        return True, f"Осталось команд: {max_usages - self.users[user_id]['current_usages']}"

if __name__ == "__main__":
    UserManager = UserManager()
    UserManager.update_param(user_id=5955315444, param="admin", value="false")