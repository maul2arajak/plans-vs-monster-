"""Entity proyektil tanaman penembak."""
from __future__ import annotations

import pygame

from ..settings import SCREEN_WIDTH
from .base import GameEntity


class Projectile(GameEntity):
    """Peluru kopi yang bergerak ke kanan dan melukai monster."""

    def __init__(self, game, x: float, y: float, row: int):
        super().__init__(game, (game.all_sprites, game.projectiles))
        self.row = row
        self.image = game.assets['projectile']
        self._position = pygame.Vector2(x, y)
        self.rect = self.image.get_rect(center=(round(x), round(y)))
        self._speed = 430
        self._damage_value = 28

    @property
    def damage_value(self) -> int:
        return self._damage_value

    def update(self, dt: int) -> None:
        self._position.x += self._speed * dt / 1000.0
        self.rect.centerx = round(self._position.x)
        if self.rect.left > SCREEN_WIDTH:
            self.kill()
            return

        for monster in list(self.game.monsters):
            if monster.row == self.row and self.rect.colliderect(monster.hitbox):
                self.game.play_sound('projectile_hit')
                monster.take_damage(self.damage_value)
                self.kill()
                break
