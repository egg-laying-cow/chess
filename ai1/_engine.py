import GUI.Board
import random
import chess
from ._heuristic import score, sort_moves, is_noisy_move, is_null_ok
from ._opening_book import OPENING_BOOK

PIECE_VALUES = {
    chess.PAWN: 10,
    chess.KNIGHT: 30,
    chess.BISHOP: 30,
    chess.ROOK: 50,
    chess.QUEEN: 90,
    chess.KING: 1000,
}

def quiesecence(board : chess.Board, depth: int, MAX_DEPTH: int, alpha: float, beta: float, turn: int):
    if (depth < MAX_DEPTH) and board.is_game_over(): return -turn * score(board, is_game_over=True)
    if depth == 0: return -turn * score(board)

    legal_moves = [move for move in board.legal_moves if is_noisy_move(board, move)]
    if len(legal_moves) == 0: return -turn * score(board)
    sort_moves(board, legal_moves)
    
    if turn == 1:
        max_eval = float('-inf')
        for move in legal_moves:
            board.push(move)
            eval = quiesecence(board, depth - 1, MAX_DEPTH, alpha, beta, -1)
            board.pop()
            if eval > max_eval:
                max_eval = eval
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in legal_moves:
            board.push(move)
            eval = quiesecence(board, depth - 1, MAX_DEPTH, alpha, beta, 1)
            board.pop()
            if eval < min_eval:
                min_eval = eval
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval    

def minimax(board : chess.Board, depth: int, alpha: float = -float('inf'), beta: float = float('inf'), turn: int = 1):
    if board.is_game_over(): return None, -turn * score(board, is_game_over=True)
    if depth <= 0: return None, quiesecence(board, 10, 10, alpha, beta, turn)
                
    # null move pruning
    if turn == 1:
        if (beta != float('inf')) and ((1 < depth < 4) or ((-turn * score(board)) >= beta)):
            if is_null_ok(board):
                board.push(chess.Move.null())
                _, eval = minimax(board, depth - 3, alpha, beta, -1)
                board.pop()
                if eval >= beta: return None, beta
    else:
        if (alpha != -float('inf')) and ((1 < depth < 4) or ((-turn * score(board)) <= alpha)):
            if is_null_ok(board):
                board.push(chess.Move.null())
                _, eval = minimax(board, depth - 3, alpha, beta, 1)
                board.pop()
                if eval <= alpha: return None, alpha

    legal_moves = list(board.legal_moves)
    sort_moves(board, legal_moves)
    
    if turn == 1:
        max_eval = float('-inf')
        best_move = None
        for move in legal_moves:
            board.push(move)
            _, eval = minimax(board, depth - 1, alpha, beta, -1)
            board.pop()
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return (best_move, max_eval)
    else:
        min_eval = float('inf')
        best_move = None
        for move in legal_moves:
            board.push(move)
            _, eval = minimax(board, depth - 1, alpha, beta, 1)
            board.pop()
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return (best_move, min_eval)


def _get_best_move(board: chess.Board):
    if (board.fullmove_number <= 20):
        board_fen = board.fen()
        if board_fen in OPENING_BOOK[board.turn]:
            move = random.choice(OPENING_BOOK[board.turn][board_fen])
            return move
    move, _ = minimax(board, 4)
    return move.uci()

