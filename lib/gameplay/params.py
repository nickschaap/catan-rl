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


DEFAULT_PARAMETERS: GameParameters = {
    "road_building_reward": 1.0,
    "settlement_building_reward": 20.0,
    "city_building_reward": 11.0,
    "development_card_reward": 1.2,
    "settlement_building_cost": 1.0,
    "city_building_cost": 1.0,
    "development_card_cost": 1.0,
    "road_building_cost": 1.0,
    "play_development_card_cost_bias": 0,
    "bank_exchange_rate": 3,
    "num_cards_per_resource": 19,
}
