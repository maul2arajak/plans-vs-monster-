from pathlib import Path
import pygame


def load_image(path, scale=None, alpha=True):
    path = Path(path)
    img = pygame.image.load(str(path))
    img = img.convert_alpha() if alpha else img.convert()
    if scale:
        img = pygame.transform.scale(img, scale)
    return img


def load_frames(folder, scale=None):
    folder = Path(folder)
    files = sorted([p for p in folder.iterdir() if p.suffix.lower() in (".png", ".jpg", ".jpeg")])
    return [load_image(p, scale=scale) for p in files]


def draw_text(surface, text, font, color, center=None, topleft=None, midtop=None):
    img = font.render(str(text), True, color)
    rect = img.get_rect()
    if center:
        rect.center = center
    elif topleft:
        rect.topleft = topleft
    elif midtop:
        rect.midtop = midtop
    surface.blit(img, rect)
    return rect
