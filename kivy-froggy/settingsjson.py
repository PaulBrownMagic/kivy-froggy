import json

settings_json = json.dumps([
    {'type': 'bool',
     'title': 'Sound',
     'desc': 'Toggle sound on or off',
     'section': 'settings',
     'key': 'sound_on'},
    {'type': 'options',
     'title': 'Difficulty',
     'desc': 'Can you keep up?',
     'section': 'settings',
     'key': 'difficulty',
     'options': ['Easy', 'Medium', 'Hard', 'Impossible']}
])
