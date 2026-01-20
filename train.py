# train.py
import os
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback, BaseCallback
from car_env import CarEnv

# ------------------ dirs ------------------
os.makedirs("models", exist_ok=True)

# ------------------ env ------------------
def make_env():
    return CarEnv(render_mode=None)  # fastest

env = DummyVecEnv([make_env])

# ------------------ callbacks ------------------
class ProgressCallback(BaseCallback):
    def __init__(self, total_steps, print_every=10_000):
        super().__init__()
        self.total_steps = total_steps
        self.print_every = print_every

    def _on_step(self):
        if self.num_timesteps % self.print_every == 0:
            percent = 100 * self.num_timesteps / self.total_steps
            print(f"{self.num_timesteps}/{self.total_steps} steps ({percent:.1f}%)")
        return True

checkpoint_callback = CheckpointCallback(
    save_freq=20_000,
    save_path="models/",
    name_prefix="car_model"
)

# ------------------ model ------------------
TOTAL_STEPS = 200_000

model = PPO(
    "MlpPolicy",
    env,
    verbose=1,
    learning_rate=3e-4,
    tensorboard_log="tb_logs/"
)

# ------------------ train ------------------
model.learn(
    total_timesteps=TOTAL_STEPS,
    callback=[checkpoint_callback, ProgressCallback(TOTAL_STEPS)],
    tb_log_name="ppo_car"
)

# ------------------ save ------------------
model.save("models/final_car_model")
