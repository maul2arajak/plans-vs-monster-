"""Hierarki class tanaman untuk Coffee vs Monster.

Plant menjadi superclass. CoffeePlant, ShooterPlant, BombPlant, dan ShieldPlant
menunjukkan inheritance serta polymorphism melalui method update().
"""
from __future__ import annotations

from abc import ABC, abstractmethod
import random

import pygame

from ..settings import CELL_H, CELL_W, COFFEE_SPAWN_MS, GRID_X, GRID_Y, PLANT_HP, SHOOT_COOLDOWN_MS
from .base import DamageableEntity
from .items import CoffeeBean, Explosion
from .projectiles import Projectile


class Plant(DamageableEntity, ABC):
    """Superclass abstrak untuk seluruh tanaman."""

    def __init__(self, game, plant_type: str, row: int, col: int, image: pygame.Surface):
        super().__init__(game, PLANT_HP[plant_type], (game.all_sprites, game.plants))
        self._plant_type = plant_type
        self.row = row
        self.col = col
        self.image = image
        center = game.cell_center(row, col)
        self.rect = self.image.get_rect(midbottom=(center[0], center[1] + CELL_H // 2 - 4))
        self.grid_rect = pygame.Rect(GRID_X + col * CELL_W, GRID_Y + row * CELL_H, CELL_W, CELL_H)

    @property
    def plant_type(self) -> str:
        return self._plant_type

    def take_damage(self, amount: int) -> None:
        if self._reduce_hp(amount):
            # Jatah kartu tetap terpakai apabila tanaman dikalahkan monster.
            self.game.remove_plant(self, free_limit=False)

    # Alias dipertahankan agar pemanggilan lama tetap kompatibel.
    def damage(self, amount: int) -> None:
        self.take_damage(amount)

    @abstractmethod
    def update(self, dt: int) -> None:
        raise NotImplementedError

    def draw_overlay(self, surface: pygame.Surface) -> None:
        if self.hp >= self.max_hp:
            return
        width, height = 38, 5
        x = self.rect.centerx - width // 2
        y = self.rect.top - 6
        pygame.draw.rect(surface, (18, 22, 18), (x, y, width, height), border_radius=3)
        pygame.draw.rect(
            surface,
            (84, 196, 92),
            (x, y, int(width * max(0, self.hp) / self.max_hp), height),
            border_radius=3,
        )


class CoffeePlant(Plant):
    """Tanaman penghasil biji kopi."""

    def __init__(self, game, row: int, col: int):
        self._frames = game.coffee_frames if getattr(game, 'coffee_frames', None) else [game.assets['coffee']]
        self._frame_index = 0
        self._animation_timer = random.randint(0, 180)
        super().__init__(game, 'coffee', row, col, self._frames[0])
        self._spawn_timer = COFFEE_SPAWN_MS
        self.active_beans = 0

    def _animate(self, dt: int) -> None:
        if not self._frames:
            return
        self._animation_timer += dt
        if self._animation_timer >= 170:
            self._animation_timer = 0
            self._frame_index = (self._frame_index + 1) % len(self._frames)
            midbottom = self.rect.midbottom
            self.image = self._frames[self._frame_index]
            self.rect = self.image.get_rect(midbottom=midbottom)

    def update(self, dt: int) -> None:
        self._animate(dt)
        if self.active_beans >= 3:
            return
        self._spawn_timer -= dt
        if self._spawn_timer <= 0:
            self._spawn_timer = COFFEE_SPAWN_MS
            x = self.rect.centerx + random.randint(-10, 10)
            y = self.rect.top + random.randint(-4, 6)
            CoffeeBean(self.game, x, y, owner=self)
            self.active_beans += 1


class ShooterPlant(Plant):
    """Tanaman yang menembakkan proyektil jika memiliki amunisi."""

    def __init__(self, game, row: int, col: int):
        super().__init__(game, 'shooter', row, col, game.shooter_frames[0])
        self._frames = game.shooter_frames
        self._frame_index = 0
        self._animation_timer = 0
        self._shooting_animation_ms = 0
        self._shoot_timer = 300
        self._ammo = 0

    @property
    def ammo(self) -> int:
        return self._ammo

    def add_ammo(self, amount: int) -> None:
        if amount < 0:
            raise ValueError('ammo tambahan tidak boleh negatif')
        self._ammo += int(amount)

    def _has_target(self) -> bool:
        return any(
            monster.row == self.row and monster.rect.centerx > self.rect.centerx - 8
            for monster in self.game.monsters
        )

    def update(self, dt: int) -> None:
        self._shoot_timer -= dt
        if self._ammo > 0 and self._has_target() and self._shoot_timer <= 0:
            self._shoot_timer = SHOOT_COOLDOWN_MS
            self._ammo -= 1
            self._shooting_animation_ms = 330
            self.game.play_sound('shooter_shoot')
            Projectile(self.game, self.rect.right - 4, self.rect.centery - 14, self.row)

        midbottom = self.rect.midbottom
        if self._shooting_animation_ms > 0:
            self._shooting_animation_ms -= dt
            self._animation_timer += dt
            if self._animation_timer >= 80:
                self._animation_timer = 0
                self._frame_index = (self._frame_index + 1) % len(self._frames)
        else:
            self._frame_index = 0
            self._animation_timer = 0
        self.image = self._frames[self._frame_index]
        self.rect = self.image.get_rect(midbottom=midbottom)

    def draw_overlay(self, surface: pygame.Surface) -> None:
        super().draw_overlay(surface)
        label = self.game.font_small.render(
            str(self.ammo),
            False,
            (255, 243, 160) if self.ammo else (255, 132, 132),
        )
        padding = 3
        box = pygame.Rect(0, 0, label.get_width() + padding * 2 + 4, label.get_height() + 2)
        box.midbottom = (self.rect.centerx, self.rect.top - 6)
        pygame.draw.rect(surface, (12, 18, 12), box, border_radius=5)
        pygame.draw.rect(surface, (220, 230, 210), box, 1, border_radius=5)
        surface.blit(label, (box.x + padding + 2, box.y + 1))


class BombPlant(Plant):
    """Tanaman ranjau yang langsung meledak ketika monster mendekat."""

    def __init__(self, game, row: int, col: int):
        super().__init__(game, 'bomb', row, col, game.assets['bomb'])
        self._trigger_rect = pygame.Rect(
            self.grid_rect.left - 8,
            self.grid_rect.top + 4,
            self.grid_rect.width + 120,
            self.grid_rect.height - 8,
        )

    @property
    def trigger_rect(self) -> pygame.Rect:
        return self._trigger_rect.copy()

    def _monster_on_mine(self, monster) -> bool:
        if monster.row != self.row:
            return False
        hitbox = monster.hitbox.inflate(-4, -8)
        if self._trigger_rect.colliderect(hitbox):
            return True
        if self._trigger_rect.colliderect(monster.front_attack_rect()):
            return True
        front_x = hitbox.left
        feet_x = monster.rect.midbottom[0]
        return self._trigger_rect.left <= front_x <= self._trigger_rect.right or self._trigger_rect.left <= feet_x <= self._trigger_rect.right

    def update(self, dt: int) -> None:
        for monster in list(self.game.monsters):
            if self._monster_on_mine(monster):
                self.explode(trigger_monster=monster)
                break

    def explode(self, trigger_monster=None) -> None:
        self.game.play_sound('bomb_explosion')
        Explosion(self.game, self.grid_rect.center)
        targets = []
        if trigger_monster is not None and trigger_monster.alive():
            targets.append(trigger_monster)
        for monster in list(self.game.monsters):
            if monster not in targets and self._monster_on_mine(monster):
                targets.append(monster)
        for monster in targets:
            monster.take_damage(9999)
        self.game.remove_plant(self, free_limit=False)
        self.game.add_flash(self.grid_rect.center, (255, 188, 72))


class ShieldPlant(Plant):
    """Tanaman pelindung dengan HP tinggi."""

    def __init__(self, game, row: int, col: int):
        super().__init__(game, 'shield', row, col, game.assets['shield'])

    def update(self, dt: int) -> None:
        # Shield tidak mempunyai aksi aktif, tetapi tetap menjadi implementasi
        # konkret dari update() pada abstract class Plant.
        return None
