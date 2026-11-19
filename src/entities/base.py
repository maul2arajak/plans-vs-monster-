"""Abstract base class untuk seluruh objek game.

File ini memperlihatkan konsep abstraction dan encapsulation pada PBO.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

import pygame


class GameEntity(pygame.sprite.Sprite, ABC):
    """Kelas abstrak dasar untuk objek yang hidup di arena game."""

    def __init__(self, game, groups: Iterable[pygame.sprite.AbstractGroup] = ()):
        super().__init__(*groups)
        self._game = game

    @property
    def game(self):
        """Akses read-only ke pengelola game."""
        return self._game

    @abstractmethod
    def update(self, dt: int) -> None:
        """Perbarui kondisi entity berdasarkan delta time dalam milidetik."""
        raise NotImplementedError

    def draw_overlay(self, surface: pygame.Surface) -> None:
        """Overlay opsional, misalnya health bar atau jumlah peluru."""


class DamageableEntity(GameEntity, ABC):
    """Kelas abstrak untuk entity yang mempunyai hit point."""

    def __init__(self, game, max_hp: int, groups: Iterable[pygame.sprite.AbstractGroup] = ()):
        super().__init__(game, groups)
        if max_hp <= 0:
            raise ValueError('max_hp harus lebih besar dari 0')
        self._max_hp = int(max_hp)
        self._hp = int(max_hp)

    @property
    def hp(self) -> int:
        return self._hp

    @property
    def max_hp(self) -> int:
        return self._max_hp

    @property
    def is_defeated(self) -> bool:
        return self._hp <= 0

    def _reduce_hp(self, amount: int) -> bool:
        """Kurangi HP secara terkontrol dan kembalikan status kalah."""
        if amount < 0:
            raise ValueError('damage tidak boleh negatif')
        self._hp = max(0, self._hp - int(amount))
        return self.is_defeated
