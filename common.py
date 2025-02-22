import json

settings_file = 'settings.json'


# Function to load settings from a file
def load_settings():
    try:
        with open(settings_file, 'r') as file:
            settings = json.load(file)
            return settings
    except Exception as e:
        print(f"Error loading settings: {e}")
        return {}


# Function to save settings to a file
def save_settings(settings):
    try:
        with open(settings_file, 'w') as file:
            json.dump(settings, file, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")
