import winsound
import threading

class SoundManager:
    @staticmethod
    def _play(sound_type):
        """Chạy âm thanh trong luồng riêng để không chặn UI"""
        def run():
            try:
                if sound_type == 'click':
                    # Âm thanh cộc
                    winsound.Beep(440, 50) 
                elif sound_type == 'move_x':
                    # Âm thanh đặt X (cao)
                    winsound.Beep(600, 100)
                elif sound_type == 'move_o':
                    # Âm thanh đặt O (trầm)
                    winsound.Beep(300, 100)
                elif sound_type == 'win':
                    # Nhạc thắng
                    winsound.Beep(523, 200) # C5
                    winsound.Beep(659, 200) # E5
                    winsound.Beep(784, 400) # G5
                elif sound_type == 'lose':
                    # Nhạc thua
                    winsound.Beep(784, 200)
                    winsound.Beep(659, 200)
                    winsound.Beep(523, 400)
                elif sound_type == 'notify':
                    # Thông báo
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except:
                pass
        
        threading.Thread(target=run, daemon=True).start()

    @staticmethod
    def play_click(): SoundManager._play('click')
    @staticmethod
    def play_move_x(): SoundManager._play('move_x')
    @staticmethod
    def play_move_o(): SoundManager._play('move_o') 
    @staticmethod
    def play_win(): SoundManager._play('win')
    @staticmethod
    def play_lose(): SoundManager._play('lose')
    @staticmethod
    def play_notify(): SoundManager._play('notify')
