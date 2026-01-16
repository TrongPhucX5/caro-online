# client/utils/constants.py
# Server connection
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5555

# Game constants
BOARD_SIZE = 15
CELL_SIZE = 30

# Colors
COLOR_PRIMARY = '#1e88e5'
COLOR_SECONDARY = '#43a047'
COLOR_DANGER = '#e53935'
COLOR_WARNING = '#ff9800'
COLOR_SUCCESS = '#4caf50'
COLOR_INFO = '#00acc1'

# Fonts
FONT_TITLE = ("Segoe UI", 24, "bold")
FONT_SUBTITLE = ("Segoe UI", 18, "bold")
FONT_NORMAL = ("Segoe UI", 11)
FONT_SMALL = ("Segoe UI", 10)

# Message types (for reference)
MESSAGE_TYPES = {
    'LOGIN': 'LOGIN',
    'LOGIN_SUCCESS': 'LOGIN_SUCCESS',
    'EDIT_PROFILE': 'EDIT_PROFILE',
    'PROFILE_UPDATED': 'PROFILE_UPDATED',
    'CREATE_ROOM': 'CREATE_ROOM',
    'JOIN_ROOM': 'JOIN_ROOM',
    'GET_ROOMS': 'GET_ROOMS',
    'GET_ONLINE_PLAYERS': 'GET_ONLINE_PLAYERS',
    'VIEW_MATCH': 'VIEW_MATCH',
    'MOVE': 'MOVE',
    'CHAT': 'CHAT',
    'SURRENDER': 'SURRENDER',
    'PLAY_AGAIN': 'PLAY_AGAIN',
    'ERROR': 'ERROR'
}