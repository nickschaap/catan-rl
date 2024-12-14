from typing import TypedDict


class GameParameters(TypedDict):
    road_building_reward: float
    settlement_building_reward: float
    city_building_reward: float
    development_card_reward: float
    settlement_building_cost: float
    city_building_cost: float
    development_card_cost: float
    road_building_cost: float
    play_development_card_cost_bias: float
    bank_exchange_rate: int
    num_cards_per_resource: int
    play_development_card_reward: float
    road_building_when_abundant_resources: float
    development_card_reward_when_abundant_resources: float


# Lower values decrease the cost
# Lower values decrease the reward
DEFAULT_PARAMETERS: GameParameters = {
    # Player specific parameters
    "road_building_reward": 4,
    "settlement_building_reward": 3.2,
    "city_building_reward": 2.6,
    "development_card_reward": 1.6,
    "settlement_building_cost": 0.2,
    "city_building_cost": 1.6,
    "development_card_cost": 0.8,
    "road_building_cost": 0.4,
    "play_development_card_cost_bias": 0,
    "play_development_card_reward": 2.0,
    "road_building_when_abundant_resources": 0.1,  # possible values between 0.1 and 0.3
    "development_card_reward_when_abundant_resources": 0.2,  # possible values between 0.1 and 0.3
    # Applies to all players
    "bank_exchange_rate": 3,
    "num_cards_per_resource": 36,
}
