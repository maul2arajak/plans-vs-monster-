"""Factory untuk membuat objek tanaman berdasarkan jenisnya."""
from __future__ import annotations

from .plants import BombPlant, CoffeePlant, ShieldPlant, ShooterPlant


class PlantFactory:
    """Memusatkan proses pembuatan tanaman agar Game tidak bergantung pada detail class."""

    _plant_classes = {
        'coffee': CoffeePlant,
        'shooter': ShooterPlant,
        'bomb': BombPlant,
        'shield': ShieldPlant,
    }

    @classmethod
    def create(cls, game, plant_type: str, row: int, col: int):
        try:
            plant_class = cls._plant_classes[plant_type]
        except KeyError as exc:
            raise ValueError(f'Jenis tanaman tidak dikenal: {plant_type}') from exc
        return plant_class(game, row, col)
