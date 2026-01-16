# client/views/__init__.py
from .login_view import LoginView
from .lobby_view import LobbyView
from .game_view import GameView
from .profile_view import ProfileView

__all__ = ['LoginView', 'LobbyView', 'GameView', 'ProfileView']