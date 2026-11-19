"""Entity monster musuh."""
from __future__ import annotations

import random

import pygame

from ..settings import (
    CELL_H,
    GAME_DURATION_MS,
    GRID_X,
    GRID_Y,
    MONSTER_SPEED_MAX,
    MONSTER_SPEED_MIN,
    MONSTER_SPEED_PROGRESS_BONUS,
    SCREEN_WIDTH,
)
from .base import DamageableEntity


class Monster(DamageableEntity):
    """Monster berjalan dari kanan ke kiri dan menyerang tanaman di depannya."""

    def __init__(self, game, row: int):
        super().__init__(game, 185, (game.all_sprites, game.monsters))
        self.row = row
        self._walk_frames = game.monster_walk_frames
        self._attack_frames = game.monster_attack_frames or game.monster_walk_frames
        self._frames = self._walk_frames
        self._frame_index = random.randrange(len(self._frames)) if self._frames else 0
        self.image = self._frames[self._frame_index]
        self._midbottom_x = float(SCREEN_WIDTH + 55)
        self._midbottom_y = float(GRID_Y + row * CELL_H + CELL_H - 4)
        self.rect = self.image.get_rect(midbottom=(int(self._midbottom_x), int(self._midbottom_y)))
        self.hitbox = self._make_hitbox()
        progress = min(1.0, game.elapsed_ms / GAME_DURATION_MS)
        speed_bonus = int(progress * MONSTER_SPEED_PROGRESS_BONUS)
        self._speed = random.randint(MONSTER_SPEED_MIN, MONSTER_SPEED_MAX) + speed_bonus
        self._state = 'walk'
        self._animation_timer = 0
        self._attack_timer = 520
        self._attack_sfx_timer = 0
        self._target = None
        self._flash_ms = 0
        self.game.play_sound('monster_howl')

    @property
    def state(self) -> str:
        return self._state

    def _make_hitbox(self) -> pygame.Rect:
        return pygame.Rect(
            self.rect.left + 26,
            self.rect.top + 18,
            max(26, self.rect.width - 52),
            max(38, self.rect.height - 30),
        )

    def _set_state(self, state: str) -> None:
        if self._state == state:
            return
        self._state = state
        self._frame_index = 0
        self._animation_timer = 0
        self._frames = self._attack_frames if state == 'attack' else self._walk_frames
        if not self._frames:
            self._frames = [self.image]

    def front_attack_rect(self) -> pygame.Rect:
        return pygame.Rect(self.rect.left - 8, self.rect.top + 30, 54, max(30, self.rect.height - 40))

    def _find_target(self):
        zone = self.front_attack_rect()
        candidates = [
            plant
            for plant in self.game.plants
            if plant.row == self.row and zone.colliderect(plant.rect.inflate(10, -8))
        ]
        return max(candidates, key=lambda plant: plant.rect.right) if candidates else None

    def update(self, dt: int) -> None:
        self._target = self._find_target()
        if self._target and self._target.plant_type == 'bomb':
            self._target.explode(trigger_monster=self)
            return

        if self._target:
            self._set_state('attack')
            self._attack_sfx_timer -= dt
            if self._attack_sfx_timer <= 0:
                self._attack_sfx_timer = 850
                self.game.play_sound('monster_attack')
            self._attack_timer -= dt
            if self._attack_timer <= 0:
                self._attack_timer = 650
                self._target.take_damage(18)
        else:
            self._set_state('walk')
            self._attack_sfx_timer = 0
            self._midbottom_x -= self._speed * dt / 1000.0
            if self.rect.right < GRID_X - 110:
                self.game.lives -= 1
                self.kill()
                return

        self._animation_timer += dt
        step = 105 if self.state == 'walk' else 88
        if self._animation_timer >= step:
            self._animation_timer = 0
            self._frame_index = (self._frame_index + 1) % len(self._frames)

        self.image = self._frames[self._frame_index % len(self._frames)]
        if self._flash_ms > 0:
            self._flash_ms -= dt
            tinted = self.image.copy()
            tinted.fill((255, 90, 90, 55), special_flags=pygame.BLEND_RGBA_ADD)
            self.image = tinted
        self.rect = self.image.get_rect(midbottom=(int(self._midbottom_x), int(self._midbottom_y)))
        self.hitbox = self._make_hitbox()

    def take_damage(self, amount: int) -> None:
        defeated = self._reduce_hp(amount)
        self._flash_ms = 90
        if defeated:
            self.kill()

    # Alias untuk kompatibilitas dengan source sebelum refactor.
    def damage(self, amount: int) -> None:
        self.take_damage(amount)

    def draw_overlay(self, surface: pygame.Surface) -> None:
        if self.hp >= self.max_hp:
            return
        width, height = 44, 5
        x = self.rect.centerx - width // 2
        y = self.rect.top + 10
        pygame.draw.rect(surface, (18, 18, 18), (x, y, width, height), border_radius=3)
        pygame.draw.rect(
            surface,
            (212, 60, 72),
            (x, y, int(width * max(0, self.hp) / self.max_hp), height),
            border_radius=3,
        )
