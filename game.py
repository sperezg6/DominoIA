rom collections import deque
import random
import numpy as np
from itertools import combinations
from time import sleep, time


class Domino:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"{self.left}|{self.right}"

    def __eq__(self, other):
        if isinstance(other, Domino):
            return (self.left == other.left and self.right == other.right) or \
                   (self.left == other.right and self.right == other.left)
        return False
    
    @staticmethod
    def from_string(s):
        parts = s.split("|")    
        if len(parts) != 2:
            return None
        try:
            left, right = int(parts[0]), int(parts[1])
            if 0 <= left <= 6 and 0 <= right <= 6:
                return Domino(left, right)
        except ValueError:
            pass
        return None

class Board():
    def __init__(self, sides: np.array, hand: np.array, num_opponent_tiles: int, uncertain_tiles: np.array):
        """
        Constructor para inicializar el estado del tablero.
        :param sides: Lados abiertos en el juego de dominó.
        :param hand: Las fichas que tiene el jugador en la mano.
        :param num_opponent_tiles: Número de fichas que tiene el oponente.
        :param uncertain_tiles: Fichas que están disponibles para robar.
        """
        self.sides = sides
        self.hand = hand
        self.num_opponent_tiles = num_opponent_tiles
        self.uncertain_tiles = uncertain_tiles

    def get_legal_moves(self, player):
        """
        Calcula los movimientos legales para el jugador actual basándose en el estado del tablero.
        :param player: El jugador para el que se deben calcular los movimientos legales.
        :return: Una lista de movimientos legales y una lista de fichas disponibles para robar.
        """
        legal_moves = []  # Lista para almacenar los movimientos legales
        draw_list = []  # Lista para almacenar las fichas disponibles para robar
            # Si el tablero está vacío, todos los movimientos son legales

        if self.sides[0] is None and self.sides[1] is None:
            if player == 'MAX':
                return [tile.tolist() for tile in self.hand], []
            else:
                return [tile.tolist() for tile in self.uncertain_tiles], []



        # Verifica los movimientos legales para el jugador MAX
        if player == 'MAX':  
            for tile in self.hand:
                # Verifica si alguna ficha en la mano coincide con algún lado abierto en el tablero
                if tile[0] in self.sides or tile[1] in self.sides:
                    legal_moves.append(tile.tolist())
            
            # Si no se encontraron movimientos legales, verifica si puede robar o debe pasar
            if not legal_moves:
                if len(self.uncertain_tiles) > self.num_opponent_tiles:
                    legal_moves.append('draw')
                    for tile in self.uncertain_tiles:
                        draw_list.append(tile.tolist())
                else:
                    legal_moves.append('pass')
        # Verifica los movimientos legales para el jugador MIN
        else:
            for tile in self.uncertain_tiles:
                if tile[0] in self.sides or tile[1] in self.sides:
                    legal_moves.append(tile.tolist())

            no_play_found = False
            try:
                # Intenta encontrar un subconjunto de fichas que no se pueden jugar
                for subset in combinations(self.uncertain_tiles, self.num_opponent_tiles):
                    if all(tile[0] not in self.sides and tile[1] not in self.sides for tile in subset):
                        no_play_found = True
                        break
            except:
                import sys
                print("Error de python: ", sys.exc_info()[0:3])
                self.print_board()
            
            # Si no se encontró un movimiento legal, verifica si puede robar o debe pasar
            if no_play_found:
                if self.num_opponent_tiles < len(self.uncertain_tiles):
                    legal_moves.append('draw')
                else:
                    legal_moves.append('pass')

        return legal_moves, draw_list


    # Updated make_move method with the new_uncertain_tiles default value

    def make_move(self, move, player, drawn_tile=None):
        """
        Realiza un movimiento y devuelve un nuevo estado del tablero.
        :param move: El movimiento a realizar.
        :param player: El jugador que realiza el movimiento.
        :param drawn_tile: La ficha robada, si corresponde.
        :return: Un nuevo objeto Board que representa el estado del tablero después del movimiento.
        """
        new_num_opponent_tiles = self.num_opponent_tiles
        new_uncertain_tiles = self.uncertain_tiles
        new_hand = self.hand
        new_sides = self.sides
        

        if self.sides[0] is None and self.sides[1] is None:
            new_sides = np.array(move)
            return Board(new_sides, new_hand, new_num_opponent_tiles, new_uncertain_tiles)

        # Proceso para el jugador MAX
        if player == 'MAX':
            if move == 'draw':
                new_hand = np.vstack([self.hand, [drawn_tile]])
                index_to_remove = np.where((self.uncertain_tiles == drawn_tile).all(axis=1))[0][0]
                new_uncertain_tiles = np.delete(self.uncertain_tiles, index_to_remove, axis=0)
            elif move == 'pass':
                pass
            else:
                move = np.array(move)
                tile_index = np.where((self.hand == move).all(axis=1))[0][0]
                new_hand = np.delete(self.hand, tile_index, axis=0)
                a, b = move
                s1, s2 = self.sides
                # Cambia los lados según la ficha jugada
                if a == s1:
                    new_sides = np.array([b, s2])
                elif a == s2:
                    new_sides = np.array([s1, b])
                elif b == s1:
                    new_sides = np.array([a, s2])
                elif b == s2:
                    new_sides = np.array([s1, a])
                else:
                    raise ValueError(f"Movimiento inválido")

        # Proceso para el jugador MIN
        elif player == 'MIN':
            if move == 'draw':
                new_num_opponent_tiles += 1
            elif move == 'pass':
                pass
            else:
                move = np.array(move)
                tile_index = np.where((self.uncertain_tiles == move).all(axis=1))[0][0]
                new_uncertain_tiles = np.delete(self.uncertain_tiles, tile_index, axis=0)
                new_num_opponent_tiles -= 1
                a, b = move
                s1, s2 = self.sides
                # Cambia los lados según la ficha jugada
                if a == s1:
                    new_sides = np.array([b, s2])
                elif a == s2:
                    new_sides = np.array([s1, b])
                elif b == s1:
                    new_sides = np.array([a, s2])
                elif b == s2:
                    new_sides = np.array([s1, a])
                else:
                   raise ValueError(f"Movimiento inválido")

        else:
            raise ValueError("Jugador inválido")

        return Board(new_sides, new_hand, new_num_opponent_tiles, new_uncertain_tiles)

    def print_board(self):
        """
        Imprime el estado actual del tablero.
        """
        print("Sides:", self.sides)
        print("Hand:", self.hand)
        print("Uncertain tiles:", self.uncertain_tiles)
        print("Number of opponent tiles:", self.num_opponent_tiles)

    
    def heuristica(self):
        """
        Calcula el valor heurístico del estado actual del tablero.
        :return: Valor heurístico.
        """
        num_fichas_mano = len(self.hand)

        # Si el jugador MAX no tiene fichas, retorna un valor alto
        if num_fichas_mano == 0:
            return 10
        # Si el oponente no tiene fichas, retorna un valor bajo
        elif self.num_opponent_tiles == 0:
            return -10

        valor_h = 0
        fichas_mano_plano = [numero for ficha in self.hand for numero in ficha]

        # Diversidad: valor proporcional al número de diferentes números en las fichas de la mano
        valor_h += 4 * (len(set(fichas_mano_plano)) / num_fichas_mano) - 4

        # Número de fichas: valor proporcional a la relación entre las fichas del oponente y las fichas propias
        valor_h += 0.286 * (self.num_opponent_tiles / num_fichas_mano) - 0.0136

        return valor_h

    def is_game_over(self):
        """
        Verifica si el juego ha terminado.
        :return: True si el juego ha terminado, False en caso contrario.
        """
        return self.hand.size == 0 or self.num_opponent_tiles == 0



def minimax(board, depth, maximizing, alpha, beta):
    if depth == 0 or board.is_game_over():
        return board.heuristica(), None  # No move is associated with the leaf node

    best_move = None
    eval=0

    if maximizing:
        max_eval = float('-inf')
        legal_moves = board.get_legal_moves("MAX")
        

        if legal_moves[0][0] == 'draw':
            for move in legal_moves[1]:
                new_board = board.make_move("draw", 'MAX', move)

                # if player can use the drawn tile
                if move in new_board.get_legal_moves("MAX")[0]:
                    new_board=new_board.make_move(move,'MAX')
                    eval, _ = minimax(new_board, depth - 1, False, alpha, beta)
                else:
                    eval, _ = minimax(new_board, depth - 1, True, alpha, beta)
                if eval > max_eval:
                    max_eval = eval
                    # Storing the draw move and the drawn tile
                    best_move = ("draw", move)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        else:
            for move in legal_moves[0]:
                new_board = board.make_move(move, 'MAX')
                eval, _ = minimax(new_board, depth - 1, False, alpha, beta)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move  # Storing the move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        return max_eval, best_move

    else:

        min_eval = float('inf')
        legal_moves = board.get_legal_moves("MIN")

        for move in legal_moves[0]:
            new_board = board.make_move(move, 'MIN')
            if move == 'draw':
                for move in new_board.get_legal_moves("MIN")[0]:
                    if move=="draw":    
                        eval, _ = minimax(new_board, depth - 1, False, alpha, beta)
                    else:
                        new_board = board.make_move(move, "MIN") 
                        eval, _ = minimax(new_board, depth - 1, True, alpha, beta)
                        
            else:
                eval, _ = minimax(new_board, depth - 1, True, alpha, beta)

            if eval < min_eval:
                min_eval = eval
                best_move = move  # Storing the move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move

class DominoesGame:
    def __init__(self):
        self.board = deque()  # Representación del tablero como deque
        self.all_dominoes = [Domino(a, b) for a in range(7) for b in range(a, 7)]  # Genera las 28 fichas de dominó
        self.player1 = []  # nuestro jugador
        self.player2 = []  # jugador oponente
        self.pile = []  # fichas que no se han repartido
        self.previous_winner = None  
        self.previous_game_tied = False
        

    def deal_dominoes(self):
        
        random.shuffle(self.all_dominoes) #se mezclan las fichas
        self.player1 = self.all_dominoes[:7] #se reparten las fichas 7 para nuestro jugador
        self.player2 = self.all_dominoes[7:14] #se reparten las fichas 7 para el oponente
        self.pile = self.all_dominoes[14:] #se reparten las fichas restantes al pozo

    def print_dominoes(self, player):
        for i, domino in enumerate(player):
            print(f"{i}: {domino}")

    def number_dominoes_in_pile(self):
        return len(self.pile)
    
    def print_board(self):
        print(" ".join([str(domino) for domino in self.board]))

    def draw_from_pile(self, hand):
        if self.pile: #si el pozo no esta vacio
            draw_domino = self.pile.pop() #se saca una ficha del pozo
            hand.append(draw_domino)
            return draw_domino
        else: #si el pozo esta vacio
            return None #no se saca ninguna ficha

    def is_legal_move(self, domino):
        if not self.board:
            return ('left', 'normal')  # Si el tablero está vacío, podemos colocar el dominó en cualquier extremo. Elegimos 'left' por defecto.
        
        # Verificar si el dominó puede colocarse en el extremo izquierdo del tablero
        if domino.right == self.board[0].left:
            return ('left', 'reversed')
        elif domino.left == self.board[0].left:
            return ('left', 'normal')
        
        # Verificar si el dominó puede colocarse en el extremo derecho del tablero
        if domino.right == self.board[-1].right:
            return ('right', 'normal')
        elif domino.left == self.board[-1].right:
            return ('right', 'reversed')
        
        # Si no se puede colocar en ningún extremo, retornar None
        return None
        
    def place_domino(self, domino):
        legal_moves = self.is_legal_move(domino)
        
        # Si no hay movimientos legales, no se puede colocar el dominó
        if not legal_moves:
            return
            
        position, orientation = legal_moves  # Desempaquetar la tupla

        if position == 'left':
            if orientation == 'reversed':
                self.board.appendleft(Domino(domino.left, domino.right))
            else:
                self.board.appendleft(Domino(domino.right, domino.left))
        elif position == 'right':
            if orientation == 'reversed':
                self.board.append(Domino(domino.left, domino.right))
            else:
                self.board.append(Domino(domino.right, domino.left))

            
    def is_game_tied(self):
        # El juego está empatado si ambos jugadores no pueden jugar y el pozo está vacío
        for domino in self.player1:
            if self.is_legal_move(domino):
                return False
        for domino in self.player2:
            if self.is_legal_move(domino):
                return False
        if self.pile:
            return False
        return True
    
    def highest_tile(self):
    # Primero, vamos a buscar la mula más alta en manos de los jugadores.
        for i in range(6, -1, -1):  # Comenzamos con la mula de 6|6 y vamos hacia abajo.
            mula = Domino(i, i)
            if mula in self.player1:
                return 'player'
            elif mula in self.player2:
                return 'machine'
        
        # Si ninguno tiene una mula, buscamos la ficha con un 6 que tenga el puntaje más alto en el otro lado.
        for i in range(6, -1, -1):
            tile1 = Domino(6, i)
            tile2 = Domino(i, 6)
            if tile1 in self.player1 or tile2 in self.player1:
                return 'player'
            elif tile1 in self.player2 or tile2 in self.player2:
                return 'machine'
        
        # Continúa con 5, 4, 3, etc., si es necesario.
        for num in range(5, -1, -1):
            for i in range(6, -1, -1):
                tile1 = Domino(num, i)
                tile2 = Domino(i, num)
                if tile1 in self.player1 or tile2 in self.player1:
                    return 'player'
                elif tile1 in self.player2 or tile2 in self.player2:
                    return 'machine'

        # En el caso improbable de que todas las fichas sean iguales (lo cual no debería ocurrir en un juego normal),
        # simplemente devuelve 'player' para que el jugador juegue primero.
        return 'player'


    def player_input(self):
        print("Tablero Actual:")  # Imprime el tablero actual
        self.print_board()
        print("Tus fichas:")  # Imprime las fichas del jugador
        self.print_dominoes(self.player1)
        print("Fichas de la máquina:")  # Imprime las fichas de la máquina
        print(len(self.player2))
        print("Número de fichas en el pozo:")  # Imprime las fichas del pozo
        print(len(self.pile))

        while True:
            domino_choice = input("Elige un dominó para jugar (por ejemplo, '1|2'), 'draw', o 'pass': ")  # Pide al jugador que elija una ficha
            
            if domino_choice == "draw":  # Si el jugador elige pescar
                if self.pile:  # Si hay fichas en el pozo
                    drawn_domino = self.draw_from_pile(self.player1)
                    print(f"Has pescado {drawn_domino}.")
                    sleep (1)   
                    print("Tus fichas:")  # Imprime las fichas del jugador
                    self.print_dominoes(self.player1)
                    print("Número de Fichas en el pozo:")  # Imprime las fichas dels´ pozo
                    print(len(self.pile))
                    print("Tablero Actual:")  # Imprime el tablero actual
                    self.print_board()
                    continue
                else:
                    print("El pozo está vacío. No puedes pescar.")
                    continue
            elif domino_choice == "pass":  # Si el jugador pasa
                if self.pile:  # Si hay fichas en el pozo
                    print("No puedes pasar mientras haya fichas en el pozo. Debes pescar.")
                    continue
                else:
                    return None
            else:
                chosen_domino = domino_choice.split("|")  # Separa la ficha en dos partes
                chosen_domino = Domino(int(chosen_domino[0]), int(chosen_domino[1]))  # Convierte las partes en un objeto Domino
                if chosen_domino not in self.player1:
                    print("No tienes esa ficha. Elige otra.")
                    continue
                else:
                    return chosen_domino

                

    def machine_move(self):
        # Verificar si el tablero tiene fichas y, de ser así, obtener los extremos
        draw_count = 0
        if len(self.board) > 0:
            sides = np.array([self.board[0].left, self.board[-1].right])
        else:
            sides = np.array([None, None])

        # Convertir el estado actual del juego a un objeto Board
        hand = np.array([[tile.left, tile.right] for tile in self.player2])
        num_opponent_tiles = len(self.player1)
        uncertain_tiles = np.array([[tile.left, tile.right] for tile in self.pile])
        board = Board(sides, hand, num_opponent_tiles, uncertain_tiles)
        
        # Llamar al algoritmo minimax para determinar el mejor movimiento
        _, best_move = minimax(board, 4, True, float('-inf'), float('inf'))
        
        if best_move == "pass":
            return None
        elif best_move[0] == "draw":
            drawn_tile = self.draw_from_pile(self.player2)
            self.player2.append(drawn_tile)  
            return drawn_tile
        
        else:
            # Buscar y devolver la instancia correspondiente de self.player2
            for tile in self.player2:
                if tile.left == best_move[0] and tile.right == best_move[1]:
                    return tile


    def play(self):
        self.deal_dominoes()  # Reparte las fichas
        print("Bienvenido al juego de dominó.")
        sleep(1)
        new_game = input("¿Es un nuevo juego? (sí/no): ").strip().lower() == "sí"
        if new_game: # Si es un nuevo juego, reinicia las variables de estado
            self.previous_winner = None
            self.previous_game_tied = False
        if self.previous_winner: # Si hay información previa
            if self.previous_winner == 'player': 
                print("Como ganaste la partida anterior, tú empiezas.")
                player_turn = True # El jugador que gano empieza
            else:
                print("Como la máquina ganó la partida anterior, ella empieza.")
                player_turn = False
        elif self.previous_game_tied:
            print("La partida anterior fue un empate.")
            starting_player = self.highest_tile()
            player_turn = starting_player == 'player'
        else:  # Si es un nuevo juego o no hay información previa
            starting_player = self.highest_tile()
            if starting_player == "player":
                print("Tú inicias la partida.")
                player_turn = True
            else:
                print("La máquina inicia la partida.")
                player_turn = False

        sleep(2)

        while True: # Ciclo principal del juego
            self.print_board()
            if player_turn: # Si es el turno del jugador
                start_time = time()
                domino = self.player_input()
                elapsed_time = time() - start_time
                if elapsed_time > 60: # Si el jugador tarda más de 60 segundos en realizar su movimiento
                    print("Has excedido el límite de tiempo de 60 segundos para realizar tu movimiento.")
                    print("El turno pasa a la máquina.")
                    player_turn = not player_turn  # Cambia el turno
                else:
                    print(f"Has tardado {elapsed_time:.2f} segundos en realizar tu movimiento.")
                    sleep(1)
            else:
                start_time = time() 
                domino = self.machine_move()
                elapsed_time = time() - start_time
                if domino:
                    if isinstance(domino, tuple) and domino[0] == "draw": # Si la máquina roba una ficha
                        print(f"La máquina ha tomado {domino[1]} ficha(s) del pozo.") # Imprime el número de fichas robadas
                        continue  
                    elif isinstance(domino, Domino):  
                        print(f"La máquina juega la ficha {domino}.") # Imprime la ficha jugada
                        sleep(1)
                else:
                    print("La máquina pasa su turno.")
                if elapsed_time > 60:
                    print("La máquina ha excedido el límite de tiempo de 60 segundos para realizar su movimiento.")
                    print("El turno pasa a ti.")
                    player_turn = not player_turn
                else:
                    print(f"La máquina ha tardado {elapsed_time:.2f} segundos en realizar su movimiento.")

            if domino: # Si se ha jugado una ficha
                if self.is_legal_move(domino): # Verifica si el movimiento es legal
                    self.place_domino(domino) # Coloca la ficha en el tablero
                    if player_turn:
                        self.player1.remove(domino)
                    else:
                        self.player2.remove(domino)
                else:
                    print("Movimiento no permitido. Inténtalo de nuevo.")
                    sleep(1)
                    continue  # Vuelve al inicio del ciclo
            else:
                print("Pasas tu turno.")
                sleep(1)

            # Cambiar el turno
            player_turn = not player_turn

            # Condiciones de finalización
            if not self.player1:
                print("¡Has ganado!")
                self.previous_winner = 'player'
                self.previous_game_tied = False
                print("Tablero Final:")
                self.print_board()
                sleep(1)
                print("Juego Terminado")
                break
            elif not self.player2:
                print("La máquina gana!")
                self.previous_winner = 'machine'
                self.previous_game_tied = False
                print("Tablero Final:")
                self.print_board()
                sleep(1)
                print("Juego Terminado")
                break
            if self.is_game_tied():
                print("El juego termina en empate.")
                self.previous_winner = None
                self.previous_game_tied = True
                print("Tablero Final:")
                self.print_board()
                sleep(1)
                print("Juego Terminado")
                break

game = DominoesGame()
game.play()
