import pygame
from .settings import *
from .support import draw_text


class UI:
    def __init__(self, game):
        self.game = game

    def panel(self, surf, rect, fill=(245, 245, 245, 155), border=(255, 255, 255, 210), radius=10):
        box = pygame.Surface(rect.size, pygame.SRCALPHA)
        box.fill(fill)
        surf.blit(box, rect.topleft)
        pygame.draw.rect(surf, border, rect, 2, border_radius=radius)

    def slot_rects(self):
        return [pygame.Rect(CARD_START_X + i * (CARD_SLOT_W + CARD_GAP), CARD_START_Y, CARD_SLOT_W, CARD_SLOT_H)
                for i in range(len(PLANT_ORDER))]

    def slot_at_pos(self, pos):
        for i, rect in enumerate(self.slot_rects()):
            if rect.collidepoint(pos):
                return i
        return None

    def shovel_rect(self):
        return pygame.Rect(SCREEN_WIDTH - 92, SCREEN_HEIGHT - 92, 72, 72)

    def draw(self, surf):
        self.draw_seed_bank(surf)
        self.draw_clock(surf)
        self.draw_lives(surf)
        self.draw_shovel(surf)
        self.draw_drag_hint(surf)

    def draw_seed_bank(self, surf):
        rects = self.slot_rects()
        bank = pygame.Rect(CARD_START_X - 8, CARD_START_Y - 6,
                           len(rects) * CARD_SLOT_W + (len(rects) - 1) * CARD_GAP + 16,
                           CARD_SLOT_H + 12)
        self.panel(surf, bank, fill=(248, 248, 248, 112), border=(255, 255, 255, 220), radius=10)

        for i, ptype in enumerate(PLANT_ORDER):
            rect = rects[i]
            selected = i == self.game.selected_index
            fill = (255, 255, 255, 150) if selected else (255, 255, 255, 95)
            slot_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
            slot_surf.fill(fill)
            surf.blit(slot_surf, rect.topleft)
            border = (250, 231, 124) if selected else (18, 18, 18)
            pygame.draw.rect(surf, border, rect, 2, border_radius=6)

            icon = pygame.transform.smoothscale(self.game.assets[ptype], (42, 42))
            surf.blit(icon, icon.get_rect(center=(rect.centerx, rect.y + 30)))
            count_label = self.game.font.render(f"{self.game.plant_counts[ptype]}/{PLANT_LIMITS[ptype]}", False, (18, 18, 18))
            surf.blit(count_label, count_label.get_rect(center=(rect.centerx, rect.bottom - 14)))

    def draw_clock(self, surf):

        progress = min(1.0, self.game.elapsed_ms / GAME_DURATION_MS)
        total = int(CLOCK_START_MINUTES + progress * (CLOCK_END_MINUTES - CLOCK_START_MINUTES))
        hour = total // 60
        minute = total % 60
        clock_rect = pygame.Rect(SCREEN_WIDTH // 2 - 112, 10, 224, 72)
        self.panel(surf, clock_rect, fill=(45, 45, 50, 215), border=(120, 125, 130, 220), radius=8)
        draw_text(surf, f'{hour:02d}:{minute:02d}', self.game.font_big, (178, 182, 186), center=(clock_rect.centerx, clock_rect.y + 28))
        draw_text(surf, f'Tingkat: {self.game.difficulty_label}', self.game.font_tiny, (224, 205, 132), center=(clock_rect.centerx, clock_rect.bottom - 13))

    def draw_lives(self, surf):
        info = pygame.Rect(SCREEN_WIDTH - 190, 14, 170, 58)
        self.panel(surf, info, fill=(45, 45, 50, 190), border=(120, 125, 130, 220), radius=8)
        label = self.game.font_small.render('Base', False, (225, 225, 225))
        surf.blit(label, (info.x + 12, info.y + 8))
        start_x = info.x + 55
        for i in range(3):
            heart = self.game.assets['heart'].copy()
            if i >= self.game.lives:
                heart.fill((40, 40, 40, 190), special_flags=pygame.BLEND_RGBA_MULT)
            surf.blit(heart, (start_x + i * 34, info.y + 19))

    def draw_shovel(self, surf):
        rect = self.shovel_rect()
        active = self.game.shovel_mode
        fill = (255, 255, 255, 150) if active else (255, 255, 255, 95)
        border = (255, 226, 95) if active else (20, 20, 20)
        slot = pygame.Surface(rect.size, pygame.SRCALPHA)
        slot.fill(fill)
        surf.blit(slot, rect.topleft)
        pygame.draw.rect(surf, border, rect, 3 if active else 2, border_radius=8)
        icon = self.game.assets['shovel']
        surf.blit(icon, icon.get_rect(center=(rect.centerx, rect.y + 30)))
        label = self.game.font_tiny.render('Hapus', False, (20, 20, 20) if not active else (255, 240, 130))
        surf.blit(label, label.get_rect(center=(rect.centerx, rect.bottom - 13)))

    def draw_drag_hint(self, surf):
        mx, my = pygame.mouse.get_pos()
        if self.game.dragging_bean:
            draw_text(surf, 'Lepas di atas Penembak', self.game.font_tiny, (255, 244, 175), center=(mx, my - 28))
        elif self.game.dragging_plant_type:
            draw_text(surf, 'Lepas di kotak rumput', self.game.font_tiny, (255, 244, 175), center=(mx, my - 34))
        elif self.game.shovel_mode:
            draw_text(surf, 'Klik tanaman untuk hapus', self.game.font_tiny, (255, 210, 160), center=(mx, my - 28))
