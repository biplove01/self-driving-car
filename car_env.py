# car_env.py
import gymnasium as gym
import pygame
import numpy as np
from typing import Tuple, Dict, Any

from main import Car, spawn_target
from sprites import *
from variables import *
from utility.distance_point_to_wall import distance_point_to_wall
from utility.line_intersection import line_intersection

class CarEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}

    def __init__(self, render_mode=None):
        super().__init__()
        self.render_mode = render_mode

        # Action space: [throttle, steering] ∈ [-1, 1]
        self.action_space = gym.spaces.Box(
            low=np.array([-1.0, -1.0], dtype=np.float32),
            high=np.array([1.0, 1.0], dtype=np.float32),
            dtype=np.float32
        )

        # Observation space: normalized ray distances + distance to target + angle to target (optional)
        num_rays = RAY_COUNT_FRONT + RAY_COUNT_BACK
        self.observation_space = gym.spaces.Box(
            low=0.0, high=1.0, shape=(num_rays + 2,), dtype=np.float32  # +2 for target info
        )

        # Initialize PyGame only if rendering
        if self.render_mode == "human":
            pygame.init()
            self.screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
            pygame.display.set_caption("Car RL Env")
        else:
            self.screen = None

        self.clock = None
        self.car = None
        self.walls = None
        self.target = None
        self.steps = 0
        self.max_steps = 1000  # prevent infinite episodes

        # Define walls (same as in your main)
        self.wall_defs = [
          (0, 0, GAME_WIDTH, 0),
          (GAME_WIDTH, 0, GAME_WIDTH, GAME_HEIGHT),
          (GAME_WIDTH, GAME_HEIGHT, 0, GAME_HEIGHT),
          (0, GAME_HEIGHT, 0, 0),

          # Top section
          (150, 100, 350, 100),      # top-left horizontal
          (450, 100, 650, 100),      # top-right horizontal

          # Upper verticals
          (200, 150, 200, 250),      # left upper vertical
          (600, 150, 600, 250),      # right upper vertical

          # Center bar
          (300, 280, 500, 280),      # center horizontal bar

          # Lower verticals
          (200, 350, 200, 450),      # left lower vertical
          (600, 350, 600, 450),      # right lower vertical

          # Bottom section
          (150, 500, 350, 500),      # bottom-left horizontal
          (450, 500, 650, 500),      # bottom-right horizontal

          # Small mid-bottom block
          (380, 420, 420, 420),      # short horizontal segment
      ]

    def _get_obs(self):
        # Get ray data
        ray_data = self.car.get_ray_data(self.walls)
        ray_distances = np.array([d / RAY_LENGTH for d, _ in ray_data], dtype=np.float32)

        # Add target info: normalized distance and angle
        to_target = self.target.pos - self.car.pos
        dist_to_target = np.linalg.norm(to_target) / np.sqrt(GAME_WIDTH**2 + GAME_HEIGHT**2)
        angle_to_target = np.arctan2(to_target.y, to_target.x) - np.radians(self.car.angle)
        angle_to_target = (angle_to_target + np.pi) % (2 * np.pi) - np.pi  # normalize to [-π, π]
        angle_to_target /= np.pi  # normalize to [-1, 1]

        return np.concatenate([ray_distances, [dist_to_target, angle_to_target]], dtype=np.float32)

    def _get_info(self):
        return {
            "distance_to_target": np.linalg.norm(self.target.pos - self.car.pos),
            "speed": self.car.speed,
        }

    def reset(self, seed=None, options=None) -> Tuple[np.ndarray, Dict[str, Any]]:
        super().reset(seed=seed)
        if seed is not None:
            np.random.seed(seed)

        # Create walls
        self.walls = [Wall(*w) for w in self.wall_defs]

        # Spawn car (fixed or random)
        self.car = Car(100, 300)

        # Spawn target
        self.target = spawn_target(self.walls)

        self.steps = 0

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, info


    def step(self, action: np.ndarray):
        throttle, steer = action

        # Apply continuous control
        self.car.speed += throttle * 0.5  # scale as needed
        self.car.speed = np.clip(self.car.speed, -3.0, 5.0)  # adjust based on your constants

        if abs(self.car.speed) > 0.1:
            turn_factor = 1 if self.car.speed >= 0 else -1
            self.car.angle += steer * 3.0 * turn_factor  # ROTATION_SPEED equivalent

        self.car.update_physics()
        self.car.update_position(self.walls)

        # Check collisions
        collided = False
        for wall in self.walls:
            dist, _ = distance_point_to_wall(self.car.pos, wall.start, wall.end)
            if dist < self.car.radius:
                collided = True
                break

        # Check target
        reached = self.car.check_target_reached(self.target)

        # Reward design
        reward = 0.0
        terminated = False
        truncated = False

        if collided:
            reward = -10.0
            terminated = True
        elif reached:
            reward = 50.0
            terminated = True
        else:
            # Small survival bonus + progress toward target
            reward = 0.1
            # Optional: reward for reducing distance to target
            # prev_dist = ... (store in state if needed)

        self.steps += 1
        if self.steps >= self.max_steps:
            truncated = True

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, terminated, truncated, info


    def _render_frame(self):
        if self.screen is None:
            return

        if self.clock is None:
            self.clock = pygame.time.Clock()

        self.screen.fill((0, 0, 0))  # BLACK

        for wall in self.walls:
            wall.draw(self.screen)
        self.target.draw(self.screen)
        self.car.draw_car(self.screen)

        # Optional: draw rays (slows rendering)
        ray_data = self.car.get_ray_data(self.walls)
        for dist, end_pos in ray_data:
            d = min(dist, RAY_LENGTH)
            t = d / RAY_LENGTH
            r = int(235 * (1 - t))
            color = (r, 50, 0)
            pygame.draw.line(self.screen, color, self.car.pos, end_pos, 2)

        pygame.display.flip()
        self.clock.tick(self.metadata["render_fps"])

    def close(self):
        if self.screen is not None:
            pygame.quit()
