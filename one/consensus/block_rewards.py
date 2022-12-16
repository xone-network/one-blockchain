from __future__ import annotations

from one.util.ints import uint32, uint64

# 1 One coin = 100,000,000 = 1 billion mojo.
_mojo_per_one = 100000000
_reward_per = [
    (10000, 300000),
    (8000, 600000),
    (6000, 900000),
    (4000, 1200000),
    (3000, 1500000),
    (2000, 1800000),
    (1500, 2100000),
    (1000, 2500000),
    (800, 3000000),
    (600, 3500000),
    (400, 4000000),
    (300, 5000000),
    (200, 6000000),
    (100, 8000000),
    (80, 10000000),
    (60, 15000000),
    (40, 20000000),
    (30, 30000000),
    (20, 40000000),
    (15, 60000000),
]


def calculate_reward(height: uint32, index: int = 0) -> int:
    if height >= 60000000:
        return 10
    else:
        _reward, _height,  = _reward_per[index]
        if height < _height:
            return _reward
        else:
            return calculate_reward(height, ++index)


def calculate_pool_reward(height: uint32) -> uint64:
    """
    Returns the pool reward at a certain block height. The pool earns 7/8 of the reward in each block. If the farmer
    is solo farming, they act as the pool, and therefore earn the entire block reward.
    These halving events will not be hit at the exact times
    (3 years, etc), due to fluctuations in difficulty. They will likely come early, if the network space and VDF
    rates increase continuously.
    """
    return uint64(int((7 / 8) * calculate_reward(height) * _mojo_per_one))


def calculate_base_farmer_reward(height: uint32) -> uint64:
    """
    Returns the base farmer reward at a certain block height.
    The base fee reward is 1/8 of total block reward

    Returns the coinbase reward at a certain block height. These halving events will not be hit at the exact times
    (3 years, etc), due to fluctuations in difficulty. They will likely come early, if the network space and VDF
    rates increase continuously.
    """
    return uint64(int((1 / 8) * calculate_reward(height) * _mojo_per_one))


def calculate_base_community_reward(height: uint32) -> uint64:
    """
    Community Rewards: 10% every block
    """
    return uint64(int((3 / 100) * calculate_reward(height) * _mojo_per_one))


def calculate_base_timelord_fee(height: uint32) -> uint64:
    """
    Community Rewards: 0.5% every block
    """
    return uint64(int((1 / 100) * calculate_reward(height) * _mojo_per_one))