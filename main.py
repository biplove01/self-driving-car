import pygame
from variables import *
import math

from utility.distance_point_to_wall import distance_point_to_wall
from utility.line_intersection import line_intersection


class Car:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.angle = 0
        self.speed = 0
        self.radius = CAR_SIZE[1]/2


    def draw_car(self, screen):
        rect = pygame.Surface(CAR_SIZE, pygame.SRCALPHA)
        rect.fill(RED)
        rotated_car = pygame.transform.rotate(rect, -self.angle)
        screen.blit(rotated_car, rotated_car.get_rect(center=self.pos))


    def move(self, walls):
        keys = pygame.key.get_pressed()

        # Rotation
        if keys[pygame.K_a]:
            if self.speed > 0:
                self.angle -= ROTATION_SPEED_CAR
            if self.speed < 0:
                self.angle += ROTATION_SPEED_CAR
        if keys[pygame.K_d]:
            if self.speed > 0:
                self.angle += ROTATION_SPEED_CAR
            if self.speed < 0:
                self.angle -= ROTATION_SPEED_CAR


        if keys[pygame.K_w]:
            self.speed += ACCELERATION
            if self.speed >= MAX_DRIVE_SPEED:
                self.speed = MAX_DRIVE_SPEED

        if keys[pygame.K_s]:
            self.speed -= ACCELERATION
            if self.speed <= MAX_REVERSE_SPEED:
                self.speed = MAX_REVERSE_SPEED

        self.update_physics()


    def update_physics(self):
        if self.speed > 0:
            self.speed = max(0, self.speed - FRICTION)
        elif self.speed < 0:
            self.speed = min(0, self.speed + FRICTION)
        if abs(self.speed) < FRICTION:
            self.speed = 0


    def update_position(self, walls):
        # Get desired movement vector
        direction = pygame.Vector2(0, -1).rotate(self.angle)
        displacement = direction * self.speed
        # print(f"Displacement: {displacement}")

        next_pos = self.pos + displacement

        # Check collision with all walls
        collision = False
        for wall in walls:
            dist, _ = distance_point_to_wall(next_pos, wall.start, wall.end)
            if dist < self.radius:
                collision = True
                break

        # Only move if no collision
        if not collision:
            self.pos = next_pos
        else:
            # Optional: reduce speed on collision (optional realism)
            self.speed = 0


    def get_ray_data(self, walls):
        data = []
        for i in range(RAY_COUNT_FRONT):
            angle_offset_front = -60 + i * (120 / max(1, RAY_COUNT_FRONT - 1))
            ray_angle_front = self.angle + angle_offset_front

            direction = pygame.Vector2(0, -1).rotate(ray_angle_front)
            ray_end = self.pos + direction * RAY_LENGTH

            closest_point = None
            closest_dist = RAY_LENGTH

            for wall in walls:
                intersect = line_intersection(self.pos, ray_end, wall.start, wall.end)
                if intersect:
                    dist = self.pos.distance_to(intersect)
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_point = intersect

            if closest_point:
                data.append((closest_dist, closest_point))
            else:
                data.append((RAY_LENGTH, ray_end))

        for i in range(RAY_COUNT_BACK):
            angle_offset_back = 80 + i * (200 / max(1, RAY_COUNT_BACK - 1))
            ray_angle_back = self.angle + angle_offset_back

            direction = pygame.Vector2(0, -1).rotate(ray_angle_back)
            ray_end = self.pos + direction * RAY_LENGTH

            closest_point = None
            closest_dist = RAY_LENGTH

            for wall in walls:
                intersect = line_intersection(self.pos, ray_end, wall.start, wall.end)
                if intersect:
                    dist = self.pos.distance_to(intersect)
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_point = intersect

            if closest_point:
                data.append((closest_dist, closest_point))
            else:
                data.append((RAY_LENGTH, ray_end))
        return data


class Wall:
    def __init__(self, x1, y1, x2, y2):
        self.start = pygame.Vector2(x1, y1)
        self.end = pygame.Vector2(x2, y2)

    def draw(self, screen):
        pygame.draw.line(screen, WHITE, self.start, self.end, 10)


def main():
    pygame.init()
    screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
    clock = pygame.time.Clock()
    car = Car(300, 300)


    running = True

    walls = [
        Wall(50, 50, 750, 50),      # top wall
        Wall(750, 50, 750, 550),    # right wall
        Wall(750, 550, 50, 550),    # bottom wall
        Wall(50, 550, 50, 50),      # left wall

        Wall(150, 200, 300, 200),
        Wall(500, 50, 500, 150),

        Wall(200, 300, 200, 450),
        Wall(330, 450, 480, 450),
        Wall(600, 300, 400, 300),
        Wall(600, 200, 600, 450),
    ]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


        screen.fill(BLACK)
        # car.move()

        for wall in walls:
            wall.draw(screen=screen)

        car.move(walls)
        car.update_position(walls)


        ray_data = car.get_ray_data(walls)
        color = (0, 150, 0)

        # Draw rays
        for dist, end_pos in ray_data:


            d = min(dist, RAY_LENGTH)
            t = d / RAY_LENGTH          # nromalizing to 1

            # interpolate red → green
            r = int(235 * (1 - t))
            g = 50
            b = 0

            color = (r, g, b)


            # color = RAY_COLOR if dist < RAY_LENGTH else (GREEN)
            pygame.draw.line(screen, color, car.pos, end_pos, 2)

        car.draw_car(screen)


        # define car
        clock.tick(60)
        #call car draw and move function here
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
