"""Entity pendukung: biji kopi dan efek ledakan."""
from __future__ import annotations

import math
import random

import pygame

from ..settings import COFFEE_AMMO_VALUE
from .base import GameEntity


class Explosion(GameEntity):
    """Animasi efek ledakan bom."""

    def __init__(self, game, center):
        super().__init__(game, (game.all_sprites, game.effects))
        self._frames = game.explosion_frames if game.explosion_frames else [game.assets['bomb']]
        self._frame_index = 0
        self._animation_timer = 0
        self.image = self._frames[0]
        self.rect = self.image.get_rect(center=center)

    def update(self, dt: int) -> None:
        self._animation_timer += dt
        if self._animation_timer < 55:
            return
        self._animation_timer = 0
        self._frame_index += 1
        if self._frame_index >= len(self._frames):
            self.kill()
            return
        center = self.rect.center
        self.image = self._frames[self._frame_index]
        self.rect = self.image.get_rect(center=center)


class CoffeeBean(GameEntity):
    """Biji kopi yang dapat ditarik ke tanaman penembak."""

    def __init__(self, game, x: float, y: float, owner=None):
        super().__init__(game, (game.all_sprites, game.beans))
        self.image = game.assets['coffee_bean'].copy()
        self._home_position = pygame.Vector2(x, y)
        self._position = pygame.Vector2(x, y)
        self.rect = self.image.get_rect(center=(round(x), round(y)))
        self._life = 10_000
        self._float_timer = random.random() * 1000
        self._owner = owner
        self._owner_released = False
        self._dragging = False
        self._drag_offset = pygame.Vector2()

    @property
    def dragging(self) -> bool:
        return self._dragging

    def release_owner(self) -> None:
        if self._owner and not self._owner_released:
            self._owner.active_beans = max(0, self._owner.active_beans - 1)
            self._owner_released = True

    def start_drag(self, mouse_pos) -> None:
        self._dragging = True
        self._drag_offset = self._position - pygame.Vector2(mouse_pos)

    def drag_to(self, mouse_pos) -> None:
        self._position = pygame.Vector2(mouse_pos) + self._drag_offset
        self.rect.center = (round(self._position.x), round(self._position.y))

    def drop_on_shooter(self, shooter) -> None:
        shooter.add_ammo(COFFEE_AMMO_VALUE)
        self.game.coffee_stock += 1
        self.release_owner()
        self.kill()

    def cancel_drag(self) -> None:
        self._dragging = False
        self._position = self._home_position.copy()
        self.rect.center = (round(self._position.x), round(self._position.y))

    def update(self, dt: int) -> None:
        if self._dragging:
            return
        self._life -= dt
        if self._life <= 0:
            self.release_owner()
            self.kill()
            return
        self._float_timer += dt * 0.005
        bob = math.sin(self._float_timer) * 0.35
        self._position.y = self._home_position.y + bob * 8
        self.rect.center = (round(self._position.x), round(self._position.y))
