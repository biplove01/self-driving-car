import pygame
from variables import *
import math
import random

from sprites import *
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


    def check_target_reached(self, target):
        return target.is_reached(self.pos)



def spawn_target(walls, min_distance=20):

    # Safe bounds: inside outer walls with margin
    min_x, max_x = 60, GAME_WIDTH - 60
    min_y, max_y = 60, GAME_HEIGHT - 60


    for _ in range(100):
        x = random.uniform(min_x, max_x)
        y = random.uniform(min_y, max_y)
        pos = pygame.Vector2(x, y)
        if is_position_safe(pos, walls, min_distance):
            print("First method success in creating target")
            return Target(int(x), int(y))



    best_pos = pygame.Vector2(GAME_WIDTH // 2, GAME_HEIGHT // 2)  # default center
    best_dist = -1

    # Use a coarse grid (adjust step for speed vs accuracy)
    step = 20
    x = min_x
    while x <= max_x:
        y = min_y
        while y <= max_y:
            pos = pygame.Vector2(x, y)
            min_wall_dist = min(
                distance_point_to_wall(pos, wall.start, wall.end)[0]
                for wall in walls
            )
            if min_wall_dist > best_dist:
                best_dist = min_wall_dist
                best_pos = pos
            y += step
        x += step

    print("Spawning target")

    return Target(int(best_pos.x), int(best_pos.y))


def is_position_safe(pos, walls, min_distance):
    for wall in walls:
        dist, _ = distance_point_to_wall(pos, wall.start, wall.end)
        if dist < min_distance:
            return False
    return True



def main():
    pygame.init()
    screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
    clock = pygame.time.Clock()

    running = True

    # walls = [
    #     Wall(50, 50, 750, 50),      # top wall
    #     Wall(750, 50, 750, 550),    # right wall
    #     Wall(750, 550, 50, 550),    # bottom wall
    #     Wall(50, 550, 50, 50),      # left wall

    #     Wall(150, 200, 300, 200),
    #     Wall(500, 50, 500, 150),

    #     Wall(200, 300, 200, 450),
    #     Wall(330, 450, 480, 450),
    #     Wall(600, 300, 400, 300),
    #     Wall(600, 200, 600, 450),
    # ]

    walls = [
    # Outer boundary — full screen
    Wall(0, 0, GAME_WIDTH, 0),
    Wall(GAME_WIDTH, 0, GAME_WIDTH, GAME_HEIGHT),
    Wall(GAME_WIDTH, GAME_HEIGHT, 0, GAME_HEIGHT),
    Wall(0, GAME_HEIGHT, 0, 0),

    Wall(150, 100, 350, 100),      # top-left horizontal
    Wall(450, 100, 650, 100),      # top-right horizontal

    Wall(200, 150, 200, 250),      # left upper vertical
    Wall(600, 150, 600, 250),      # right upper vertical

    Wall(300, 280, 500, 280),      # center horizontal bar

    Wall(200, 350, 200, 450),      # left lower vertical
    Wall(600, 350, 600, 450),      # right lower vertical

    Wall(150, 500, 350, 500),      # bottom-left horizontal
    Wall(450, 500, 650, 500),      # bottom-right horizontal

    Wall(380, 420, 420, 420),      # small mid-bottom block
]

    car = Car(300, 300)
    target = spawn_target(walls)



    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


        screen.fill(BLACK)

        for wall in walls:
            wall.draw(screen=screen)

        car.move(walls)
        car.update_position(walls)

        if car.check_target_reached(target):
            target = spawn_target(walls)
        target.draw(screen)


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
            pygame.draw.line(screen, color, car.pos, end_pos, 2)

        car.draw_car(screen)


        # define car
        clock.tick(60)
        #call car draw and move function here
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
