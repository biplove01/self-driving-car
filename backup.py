import pygame
import math

# Constants
WIDTH, HEIGHT = 800, 600
CAR_SIZE = (20, 40)
SENSOR_LEN = 150
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)


class Car:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.angle = 0
        self.speed = 3
        # Weights for [Left, Center, Right] sensors
        self.weights = [-0.8, 0.1, 0.8]
        self.bias = 0

    def get_sensor_data(self, walls):
        readings = []
        # Angles for sensors: -45, 0, 45 degrees
        for angle_offset in [-45, 0, 45]:
            rad = math.radians(self.angle + angle_offset)
            end_x = self.pos.x + math.cos(rad) * SENSOR_LEN
            end_y = self.pos.y + math.sin(rad) * SENSOR_LEN

            # Simple ray-wall intersection (collision check)
            dist = SENSOR_LEN
            for wall in walls:
                # Returns 0.0 to 1.0 (normalized distance)
                # Logic simplified for brevity: check distance to wall Rect
                clipline = wall.clipline(
                    (self.pos.x, self.pos.y), (end_x, end_y))
                if clipline:
                    d = pygame.Vector2(self.pos).distance_to(clipline[0])
                    dist = min(dist, d)
            readings.append(dist / SENSOR_LEN)
        return readings

    def drive(self, sensors):
        # Perceptron calculation: Y = tanh(W*X + b)
        steering = 0
        for i in range(len(sensors)):
            # Invert sensor (1 = clear, 0 = obstacle)
            val = 1.0 - sensors[i]
            steering += val * self.weights[i]

        self.angle += (steering + self.bias) * 5
        rad = math.radians(self.angle)
        self.pos.x += math.cos(rad) * self.speed
        self.pos.y += math.sin(rad) * self.speed

    def draw(self, screen):
        rect = pygame.Surface(CAR_SIZE, pygame.SRCALPHA)
        rect.fill(RED)
        # rotated = pygame.transform.rotate(rect, -self.angle - 90)
        # screen.blit(rotated, rotated.get_rect(center=self.pos))
        screen.blit(rect, rect.get_rect(center=self.pos))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    car = Car(100, 100)
    walls = [
        pygame.Rect(0, 0, WIDTH, 20), pygame.Rect(0, HEIGHT - 20, WIDTH, 20),
        pygame.Rect(0, 0, 20, HEIGHT), pygame.Rect(WIDTH - 20, 0, 20, HEIGHT),
        pygame.Rect(300, 200, 200, 20), pygame.Rect(200, 400, 20, 150)
    ]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BLACK)
        for wall in walls:
            pygame.draw.rect(screen, WHITE, wall)

        sensor_data = car.get_sensor_data(walls)
        # car.drive(sensor_data)
        car.draw(screen)

        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()
