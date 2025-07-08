import pygame

def blit_rotate_center(surf, image, topleft, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)
    surf.blit(rotated_image, new_rect.topleft)

def scale_image(image, scale):
    size = round(image.get_width() * scale), round(image.get_height() * scale)
    return pygame.transform.scale(image, size)