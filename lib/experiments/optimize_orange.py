from typing import Literal, Union
from lib.experiments.win_stats import win_stats
from lib.gameplay import Game
from lib.gameplay.params import DEFAULT_PARAMETERS, GameParameters
from lib.logging.database import MongoLogger
import logging
import uuid
import optuna
from typing import cast


def objective(trial: optuna.Trial) -> float:
    orange_params: GameParameters = {
        # Player specific parameters
        "road_building_reward": trial.suggest_float(
            "road_building_reward", 3.5, 4.5
        ),  # 4,
        "settlement_building_reward": trial.suggest_float(
            "settlement_building_reward", 2.7, 3.7
        ),  # 3.2,
        "city_building_reward": trial.suggest_float(
            "city_building_reward", 2.1, 3.1
        ),  # 2.6,
        "development_card_reward": trial.suggest_float(
            "development_card_reward", 1.1, 2.1
        ),  # 1.6,
        "settlement_building_cost": trial.suggest_float(
            "settlement_building_cost", 0, 0.7
        ),  # 0.2,
        "city_building_cost": trial.suggest_float(
            "city_building_cost", 1.1, 2.1
        ),  # 1.6,
        "development_card_cost": trial.suggest_float(
            "development_card_cost", 0.3, 1.3
        ),  # 0.8,
        "road_building_cost": trial.suggest_float("road_building_cost", 0, 0.9),  # 0.4,
        "play_development_card_cost_bias": 0,  # 0,
        "play_development_card_reward": 2,  # 2.0,
        "road_building_when_abundant_resources": trial.suggest_float(
            "road_building_when_abundant_resources", 0.01, 0.3
        ),  # 0.1,
        "development_card_reward_when_abundant_resources": trial.suggest_float(
            "development_card_reward_when_abundant_resources", 0, 0.4
        ),  # 0.2,
        # Applies to all players
        "bank_exchange_rate": 3,
        "num_cards_per_resource": 36,
    }

    try:
        game = Game(
            parameters=[
                DEFAULT_PARAMETERS,
                DEFAULT_PARAMETERS,
                DEFAULT_PARAMETERS,
                orange_params,
            ],
            experiment_id=trial.study.study_name,
        )
        game.play()
    except Exception as _:
        logger.error("Game failed")
        return 0

    return game.players[3].points()


logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)


def optimize_orange(
    num_games: int,
    mode: Literal["optimize", "evaluate"] = "optimize",
    study_name: Union[str, None] = None,
) -> None:
    if mode == "optimize":
        study_name = str(uuid.uuid4())
        study = optuna.create_study(direction="maximize", study_name=study_name)
        study.optimize(objective, n_trials=num_games)
        MongoLogger.log(
            "optimize_orange", {"study_name": study_name, **study.best_params}
        )
    elif mode == "evaluate" and study_name is not None:
        study = MongoLogger.get_orange_study(study_name)
        if study is None:
            logger.error(f"Study {study_name} not found")
            return

        study_params = {
            **study,
            "play_development_card_cost_bias": 0,
            "play_development_card_reward": 2,
        }
        print(study_params)
        win_stats(
            num_games=num_games,
            parameters=[
                DEFAULT_PARAMETERS,
                DEFAULT_PARAMETERS,
                DEFAULT_PARAMETERS,
                cast(GameParameters, study_params),
            ],
        )
