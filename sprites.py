import pygame
from variables import *

class Wall:
    def __init__(self, x1, y1, x2, y2):
        self.start = pygame.Vector2(x1, y1)
        self.end = pygame.Vector2(x2, y2)

    def draw(self, screen):
        pygame.draw.line(screen, WHITE, self.start, self.end, 10)



# class Target:
#     def __init__(self, x, y, size=30):
#         self.pos = pygame.Vector2(x, y)
#         self.size = size

#         # Optional: create a rect for easy collision (though you'll likely use distance)
#         self.rect = pygame.Rect(x - size//2, y - size//2, size, size)

#     def draw(self, screen):
#         pygame.draw.rect(screen, GREEN, self.rect)


#     def is_reached(self, car_pos, threshold=20):
#         return car_pos.distance_to(self.pos) <= threshold


class Target:
    def __init__(self, x, y, size=20):
        self.pos = pygame.Vector2(x, y)
        self.size = size
        self.rect = pygame.Rect(x - size//2, y - size//2, size, size)

    def draw(self, screen):
        pygame.draw.circle(screen, GREEN, self.pos, self.size)
        pygame.draw.circle(screen, (0, 100, 0), self.pos, self.size, 2)

    def is_reached(self, car_pos, threshold=25):
        return car_pos.distance_to(self.pos) <= threshold
