from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ASSET_DIR = BASE_DIR / 'assets'
MAP_DIR = BASE_DIR / 'maps'

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60


GRID_COLS = 9
GRID_ROWS = 5
CELL_W = 90
CELL_H = 64
GRID_X = 180
GRID_Y = 282
GRID_W = GRID_COLS * CELL_W
GRID_H = GRID_ROWS * CELL_H

LANE_Y = [GRID_Y + r * CELL_H + CELL_H // 2 for r in range(GRID_ROWS)]


GAME_DURATION_MS = 5 * 60 * 1000
CLOCK_START_MINUTES = 1 * 60
CLOCK_END_MINUTES = 6 * 60


DIFFICULTY_EASY_END_MS = 2 * 60 * 1000
DIFFICULTY_MEDIUM_END_MS = 4 * 60 * 1000


FINISH_CLOCK_HOLD_MS = 900

PLANT_LIMITS = {
    'coffee': 5,
    'shooter': 7,
    'bomb': 3,
    'shield': 4,
}

PLANT_ORDER = ['coffee', 'shooter', 'bomb', 'shield']
PLANT_HP = {'coffee': 90, 'shooter': 90, 'bomb': 70, 'shield': 300}

COFFEE_SPAWN_MS = 5000
COFFEE_AMMO_VALUE = 3
SHOOT_COOLDOWN_MS = 980

MONSTER_FIRST_SPAWN_DELAY_MS = 4_000
MONSTER_INITIAL_TIMER_MS = 1_800
MONSTER_SPAWN_BASE_MS = 11_000
MONSTER_MIN_SPAWN_MS = 4_000
MONSTER_SPAWN_REDUCTION_MS = MONSTER_SPAWN_BASE_MS - MONSTER_MIN_SPAWN_MS


MONSTER_SPEED_MIN = 19
MONSTER_SPEED_MAX = 27
MONSTER_SPEED_PROGRESS_BONUS = 4

PLANT_SCALES = {
    'coffee': (60, 60),
    'shooter': (66, 66),
    'bomb': (70, 70),
    'shield': (68, 68),
    'coffee_bean': (28, 38),
    'projectile': (14, 14),
}
MONSTER_FRAME_SCALE = (118, 92)

WORLD_BG_PATH = ASSET_DIR / 'world/haunted_lawn_zoom.png'

TOP_BAR_Y = 12
CARD_SLOT_W = 64
CARD_SLOT_H = 88
CARD_GAP = 8
CARD_START_X = 18
CARD_START_Y = 12


SHOVEL_SLOT_SIZE = 72


AUDIO_DIR = ASSET_DIR / 'audio'
GAME_MUSIC = AUDIO_DIR / 'Under_the_Buried_Ivy.mp3'
MONSTER_HOWL_SOUND = AUDIO_DIR / 'monster_howl.wav'
SHOOTER_SHOOT_SOUND = AUDIO_DIR / 'shooter_shoot.wav'
PROJECTILE_HIT_SOUND = AUDIO_DIR / 'projectile_hit.wav'

BOMB_EXPLOSION_SOUND = AUDIO_DIR / 'bomb_explosion.wav'
MONSTER_ATTACK_SOUND = AUDIO_DIR / 'monster_attack.wav'



VIDEO_DIR = ASSET_DIR / 'videos'
INTRO_VIDEO = VIDEO_DIR / 'pembuka battle.mp4'
INTRO_VIDEO_AUDIO = VIDEO_DIR / 'pembuka battle.mp3'
WIN_VIDEO = VIDEO_DIR / 'menang battle.mp4'
WIN_VIDEO_AUDIO = VIDEO_DIR / 'menang battle.mp3'
LOSE_VIDEO = VIDEO_DIR / 'kalah battle.mp4'
LOSE_VIDEO_AUDIO = VIDEO_DIR / 'kalah battle.mp3'
