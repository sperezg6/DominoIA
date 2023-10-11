# DominoIA Game
Domino Project that uses a minimax algorithm

## Description:

This script simulates a domino game between a human player and a machine. The game follows the basic rules of traditional domino, where players take turns placing tiles on the board, trying to match the numbers on the ends of the tiles already played. If a player cannot play a tile, they can draw from the pile or pass their turn. The game ends when one player plays all their tiles or when both players consecutively pass their turns and the pile is empty.

## Classes and Functions:
Domino: Represents an individual domino tile with two ends.

Board: Represents the current game board state and provides methods to compute legal moves, make a move, etc.

DominoesGame: Represents the domino game itself. Contains the game logic and controls the game flow.

minimax: An implementation of the Minimax algorithm with alpha-beta pruning to decide the best move for the machine.

## Usage:
To play the game, simply run the script. You'll be prompted to choose a tile to play or draw one from the pile if you cannot play any of your current tiles. The game will continue alternating between the human player and the machine until one of the players wins or the game ends in a tie.

## How to Play:
You'll be shown the current board, your tiles, and the remaining tiles in the pile.
You'll be prompted to choose a tile to play by inputting its values, e.g., "1|2".
If you cannot play a tile, you can choose to draw from the pile by typing "draw".
If the pile is empty and you cannot play a tile, you can pass your turn by typing "pass".
The game continues until one player plays all their tiles or both players consecutively pass their turns, and the pile is empty.
## Notes:
The machine uses the Minimax algorithm with alpha-beta pruning to decide its move. This ensures the machine plays optimally given the depth provided to the algorithm.
The game takes into account who won the last match and allows that player to start the next match. In case of a tie, the player with the highest tile starts.
The game has a 60-second time limit for both the human player and the machine to make a move.
Enjoy the game!
