import json

settings_json = json.dumps([
    {'type': 'bool',
     'title': 'Sound',
     'desc': 'Toggle sound on or off',
     'section': 'sound',
     'key': 'sound_on'}
])
