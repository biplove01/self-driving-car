# test.py
import gymnasium as gym
from stable_baselines3 import PPO
from car_env import CarEnv

def main():
    # Load the trained model
    model_path = "./models/final_car_model"  # or any checkpoint like "car_model_50000_steps"
    model = PPO.load(model_path)

    # Create environment in human mode to watch
    env = CarEnv(render_mode="human")

    num_episodes = 10
    for ep in range(num_episodes):
        obs, info = env.reset()
        total_reward = 0.0
        steps = 0
        done = False

        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            steps += 1
            done = terminated or truncated

        print(f"✅ Episode {ep + 1}/{num_episodes} | Total Reward: {total_reward:.2f} | Steps: {steps}")

    env.close()
    print("🏁 Testing complete!")

if __name__ == "__main__":
    main()
