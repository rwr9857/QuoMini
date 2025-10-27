from .Random import Random_player as RandomPlayer
from .Human import Human_player as HumanPlayer
from .MiniMax import MiniMax_Player as MiniMaxPlayer
from .AlphaBeta import AlphaBeta_Player as AlphaBetaPlayer
from .MonteCarlo import Monte_Carlo_player as MonteCarloPlayer
from .MCTS import MCTS_player as MCTSPlayer

__all__ = [
    "RandomPlayer",
    "HumanPlayer",
    "MiniMaxPlayer",
    "AlphaBetaPlayer",
    "MonteCarloPlayer",
    "MCTSPlayer",
]
