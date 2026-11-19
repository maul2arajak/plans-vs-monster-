from __future__ import annotations

from pathlib import Path

import pygame

try:
    import cv2
except ImportError:
    cv2 = None


class CutscenePlayer:
    """Memutar video MP4 layar penuh dengan audio terpisah dan tombol skip."""

    def __init__(self, screen, clock, audio_enabled=True, font=None):
        self.screen = screen
        self.clock = clock
        self.audio_enabled = audio_enabled
        self.font = font or pygame.font.Font(None, 26)

    def _stop_audio(self):
        if not self.audio_enabled:
            return
        try:
            pygame.mixer.stop()
            pygame.mixer.music.stop()
        except pygame.error:
            pass

    def _play_audio(self, audio_path):
        if not self.audio_enabled or not audio_path or not audio_path.exists():
            return
        try:
            pygame.mixer.music.load(str(audio_path))
            pygame.mixer.music.set_volume(1.0)
            pygame.mixer.music.play()
        except pygame.error as exc:
            print(f'Audio cutscene gagal diputar {audio_path.name}: {exc}')

    def _draw_frame(self, frame):
        screen_w, screen_h = self.screen.get_size()
        frame_h, frame_w = frame.shape[:2]
        scale = min(screen_w / frame_w, screen_h / frame_h)
        target_w = max(1, int(frame_w * scale))
        target_h = max(1, int(frame_h * scale))

        if (target_w, target_h) != (frame_w, frame_h):
            frame = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_AREA)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        surface = pygame.image.frombuffer(frame.tobytes(), (target_w, target_h), 'RGB')

        self.screen.fill((0, 0, 0))
        x = (screen_w - target_w) // 2
        y = (screen_h - target_h) // 2
        self.screen.blit(surface, (x, y))

        hint = self.font.render('Tekan SPACE untuk skip', True, (245, 245, 245))
        pad_x, pad_y = 12, 7
        hint_bg = pygame.Surface((hint.get_width() + pad_x * 2, hint.get_height() + pad_y * 2), pygame.SRCALPHA)
        hint_bg.fill((0, 0, 0, 145))
        hint_bg.blit(hint, (pad_x, pad_y))
        self.screen.blit(hint_bg, (screen_w - hint_bg.get_width() - 18, screen_h - hint_bg.get_height() - 16))
        pygame.display.flip()

    def _draw_startup_error(self, title, detail):
        """Tampilkan pesan kesalahan agar cutscene pembuka tidak dilewati diam-diam."""
        self._stop_audio()
        screen_w, screen_h = self.screen.get_size()
        big_font = pygame.font.Font(None, 42)
        small_font = pygame.font.Font(None, 27)
        lines = [
            title,
            detail,

        ]

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN):
                    return False

            self.screen.fill((8, 10, 16))
            y = max(90, screen_h // 2 - 120)
            for index, text in enumerate(lines):
                font = big_font if index == 0 else small_font
                color = (255, 205, 95) if index == 0 else (235, 235, 235)
                surface = font.render(text, True, color)
                rect = surface.get_rect(center=(screen_w // 2, y))
                self.screen.blit(surface, rect)
                y += 54 if index == 0 else 38
            pygame.display.flip()
            self.clock.tick(30)

    def play(self, video_path, audio_path=None, required=False):

        video_path = Path(video_path)
        audio_path = Path(audio_path) if audio_path else None
        self._stop_audio()

        if cv2 is None:
            message = 'opencv-python belum terpasang.'
            print(f'Cutscene tidak dapat diputar: {message}')
            return self._draw_startup_error('CUTSCENE PEMBUKA GAGAL DIPUTAR', message) if required else False
        if not video_path.exists():
            message = f'File tidak ditemukan: {video_path}'
            print(f'Cutscene tidak ditemukan: {video_path}')
            return self._draw_startup_error('CUTSCENE PEMBUKA TIDAK DITEMUKAN', message) if required else False

        capture = cv2.VideoCapture(str(video_path))
        if not capture.isOpened():
            message = f'File video tidak dapat dibuka: {video_path.name}'
            print(f'Cutscene gagal dibuka: {video_path.name}')
            return self._draw_startup_error('CUTSCENE PEMBUKA GAGAL DIBUKA', message) if required else False

        fps = capture.get(cv2.CAP_PROP_FPS)
        if not fps or fps <= 0:
            fps = 25.0
        frame_delay_ms = max(1, int(round(1000 / fps)))
        self._play_audio(audio_path)

        continue_game = True
        try:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            return False
                        if event.key == pygame.K_SPACE:
                            return continue_game

                ok, frame = capture.read()
                if not ok:
                    return continue_game
                self._draw_frame(frame)
                self.clock.tick(max(1, int(round(fps))))
                pygame.time.wait(max(0, frame_delay_ms - self.clock.get_time()))
        finally:
            capture.release()
            self._stop_audio()
