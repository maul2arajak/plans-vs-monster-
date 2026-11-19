import pygame
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_BG_PATH


class TiledMapRenderer:


    def __init__(self, filename='night_forest.tmx'):
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert()
        self.render_background()

    def render_background(self):
        self.surface.fill((8, 14, 18))
        try:
            bg = pygame.image.load(str(WORLD_BG_PATH)).convert()
            bg = pygame.transform.smoothscale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surface.blit(bg, (0, 0))
        except Exception:
            self.surface.fill((9, 22, 26))
            for y in range(0, SCREEN_HEIGHT, 64):
                for x in range(0, SCREEN_WIDTH, 64):
                    color = (20, 60, 44) if (x // 64 + y // 64) % 2 else (16, 48, 34)
                    pygame.draw.rect(self.surface, color, (x, y, 64, 64))

        
        shade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        shade.fill((0, 4, 10, 18))
        self.surface.blit(shade, (0, 0))

    def draw(self, screen):
        screen.blit(self.surface, (0, 0))
