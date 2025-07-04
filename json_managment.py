import json

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
                    'usages_per_hour': int(info.get('usages_per_hour', 0))
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
    
    def update_param(self, user_id : int, param : str, value : str):
        self.users = self.load_json()
        user_id = str(user_id)
        if user_id in self.users:
            if param in self.users[user_id]:
                if param in ['balance', 'usages_per_hour']:
                    self.users[user_id][param] = int(value)
                elif param == 'admin':
                    self.users[user_id][param] = str(value).lower() == 'true'
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
                'usages_per_hour': 30
            }
            self.users[user_id] = new_user
            self.save_json()
            return 

# user_id = message.from_user.id
# username = message.from_user.username or message.from_user.first_name or "unknown"
    
# was_added = user_manager.check_and_add_user(user_id, username)

if __name__ == "__main__":
    UserManager = UserManager()
    UserManager.update_param(user_id=5955315444, param="admin", value="false")
