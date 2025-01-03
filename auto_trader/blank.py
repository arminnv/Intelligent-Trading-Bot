from stable_baselines3 import PPO
# cmd_util was renamed env_util for clarity
from stable_baselines3.common.env_util import make_atari_env

# num_env was renamed n_envs
env = make_atari_env("BreakoutNoFrameskip-v4", n_envs=8, seed=21)

# we use batch_size instead of nminibatches which
# was dependent on the number of environments
# batch_size = (n_steps * n_envs) // nminibatches = 256
# noptepochs was renamed n_epochs
model = PPO("MlpPolicy", env, n_steps=128, batch_size=256,
            n_epochs=4, ent_coef=0.01, verbose=1)

model.learn(int(1e5))



"""

import numpy as np

from sb3_contrib import RecurrentPPO
from stable_baselines3.common.evaluation import evaluate_policy

model = RecurrentPPO("MlpLstmPolicy", "CartPole-v1", verbose=1)
model.learn(5000)

env = model.get_env()
mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=20, warn=False)
print(mean_reward)

model.save("ppo_recurrent")
del model # remove to demonstrate saving and loading

model = RecurrentPPO.load("ppo_recurrent")

obs = env.reset()
# cell and hidden state of the LSTM
lstm_states = None
num_envs = 1
# Episode start signals are used to reset the lstm states
episode_starts = np.ones((num_envs,), dtype=bool)
while True:
    action, lstm_states = model.predict(obs, state=lstm_states, episode_start=episode_starts, deterministic=True)
    obs, rewards, dones, info = env.step(action)
    episode_starts = dones
    env.render()
"""
