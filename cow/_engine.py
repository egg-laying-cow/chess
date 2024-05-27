from chess import Board, Move, scan_reversed
from chess.polyglot import open_reader
from ._heuristic import END_GAME_SCORE, is_null_ok, organize_moves, organize_moves_quiescence, score

OPENING_BOOK = open_reader("cow/data/opening_book/3210elo.bin")

def quiesecence(board : Board, depth: int, MAX_DEPTH: int, is_end_game: bool, alpha: float, beta: float, turn: int):
    # Kiểm tra kết thúc game.
    if (depth < MAX_DEPTH):
        if board.is_checkmate(): return -turn * (END_GAME_SCORE + END_GAME_SCORE / (board.fullmove_number + 1))
        if board.is_insufficient_material(): return 0
        if not any(board.generate_legal_moves()): return 0
        if board.is_fifty_moves(): return 0
        if board.is_repetition(3): return 0
    if depth == 0: return -turn * score(board, is_end_game)
    
    # Tạo nước đi hợp lệ cho quiescence search.
    moves = organize_moves_quiescence(board)
    if not moves: return -turn * score(board, is_end_game)
    
    # Tìm kiếm minimax
    if turn == 1:
        max_eval = float('-inf')
        for move in moves:
            board.push(move)
            eval = quiesecence(board, depth - 1, MAX_DEPTH, is_end_game, alpha, beta, -1)
            board.pop()
            if eval > max_eval:
                max_eval = eval
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in moves:
            board.push(move)
            eval = quiesecence(board, depth - 1, MAX_DEPTH, is_end_game, alpha, beta, 1)
            board.pop()
            if eval < min_eval:
                min_eval = eval
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval    

def minimax(board : Board, depth: int, cache: dict, is_end_game: bool, alpha: float = -float('inf'), beta: float = float('inf'), turn: int = 1):
    # Kiểm tra kết thúc game.
    if board.is_checkmate(): return None, -turn * (END_GAME_SCORE + END_GAME_SCORE / (board.fullmove_number + 1))
    if board.is_insufficient_material(): return None, 0
    if not any(board.generate_legal_moves()): return None, 0
    if board.is_fifty_moves(): return None, 0
    if board.is_repetition(3): return None, 0

    # Transposition table
    cache_key = (board._transposition_key(), (depth if depth >= 0 else 0), alpha, beta, turn)
    if cache_key in cache: return cache[cache_key]

    # Trường hợp cơ sở.
    if depth <= 0: 
        eval = quiesecence(board, 12, 12, is_end_game, alpha, beta, turn)
        cache[cache_key] = (None, eval)
        return None, eval
                
    # Null move pruning
    if turn == 1:
        if (not is_end_game) and (beta != float('inf')) and ((1 < depth < 4) or ((-turn * score(board, is_end_game)) >= beta)):
            if is_null_ok(board):
                board.push(Move.null())
                _, eval = minimax(board, depth - 3, cache, is_end_game, alpha, beta, -1)
                board.pop()
                if eval >= beta: return None, beta
    else:
        if (not is_end_game) and (alpha != -float('inf')) and ((1 < depth < 4) or ((-turn * score(board, is_end_game)) <= alpha)):
            if is_null_ok(board):
                board.push(Move.null())
                _, eval = minimax(board, depth - 3, cache, is_end_game, alpha, beta, 1)
                board.pop()
                if eval <= alpha: return None, alpha

    # Tạo nước đi hợp lệ.
    legal_moves = organize_moves(board)
    
    # Tìm kiếm minimax
    if turn == 1:
        max_eval = float('-inf')
        best_move = None
        for move in legal_moves:
            board.push(move)
            _, eval = minimax(board, depth - 1, cache, is_end_game, alpha, beta, -1)
            board.pop()
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        cache[cache_key] = (best_move, max_eval)
        return (best_move, max_eval)
    else:
        min_eval = float('inf')
        best_move = None
        for move in legal_moves:
            board.push(move)
            _, eval = minimax(board, depth - 1, cache, is_end_game, alpha, beta, 1)
            board.pop()
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        cache[cache_key] = (best_move, min_eval)
        return (best_move, min_eval)

def _get_best_move(board: Board, depth):
    # Tra sách khai cuộc
    try: return OPENING_BOOK.weighted_choice(board).move.uci()
    except:
        # Tìm kiếm nước đi tốt nhất
        move, _ = minimax(board, depth, {}, len(list(scan_reversed(board.occupied))) <= 5)
        return move.uci()