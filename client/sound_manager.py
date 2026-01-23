import winsound
import threading
import os

class SoundManager:
    # Đường dẫn đến thư mục sounds
    SOUND_DIR = os.path.join(os.path.dirname(__file__), 'assets', 'sounds')
    
    @staticmethod
    def _play(sound_type):
        """Chạy âm thanh trong luồng riêng để không chặn UI"""
        def run():
            try:
                # Kiểm tra xem có file âm thanh thật không
                sound_file = os.path.join(SoundManager.SOUND_DIR, f"{sound_type}.wav")
                print(f"[SOUND] Trying to play: {sound_file}")
                print(f"[SOUND] File exists: {os.path.exists(sound_file)}")
                
                if os.path.exists(sound_file):
                    # Phát file âm thanh thật - dùng SND_NOSTOP để không bị ghi đè
                    print(f"[SOUND] Playing {sound_type}.wav...")
                    winsound.PlaySound(sound_file, winsound.SND_FILENAME)
                    print(f"[SOUND] Done playing {sound_type}.wav")
                else:
                    print(f"[SOUND] File not found, using beep for {sound_type}")
                    # Fallback về beep nếu không có file
                    if sound_type == 'click':
                        winsound.Beep(800, 100) 
                    elif sound_type == 'move_x':
                        winsound.Beep(1000, 200)
                    elif sound_type == 'move_o':
                        winsound.Beep(250, 200)
                    elif sound_type == 'win':
                        winsound.Beep(523, 200)  # C5
                        winsound.Beep(659, 200)  # E5
                        winsound.Beep(784, 200)  # G5
                        winsound.Beep(1047, 400) # C6
                        
                        # Tiếng vỗ tay
                        import time
                        time.sleep(0.1)
                        for _ in range(3):
                            winsound.Beep(200, 30)
                            time.sleep(0.02)
                        time.sleep(0.15)
                        for _ in range(3):
                            winsound.Beep(200, 30)
                            time.sleep(0.02)
                        time.sleep(0.15)
                        for _ in range(6):
                            winsound.Beep(200, 30)
                            time.sleep(0.02)
                    elif sound_type == 'lose':
                        winsound.Beep(784, 300)
                        winsound.Beep(659, 300)
                        winsound.Beep(523, 300)
                        winsound.Beep(392, 600)
                    elif sound_type == 'notify':
                        winsound.Beep(800, 150)
                        winsound.Beep(1000, 150)
            except Exception as e:
                print(f"[SOUND] Error: {e}")
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
