from chess import Board, Move
from chess.polyglot import open_reader
from chess.engine import T
from ._heuristic import END_GAME_SCORE, EGTABLEBASE, is_null_ok, organize_moves, organize_moves_quiescence, score
from ._helper import is_draw, TranspositionTable

OPENING_BOOK = open_reader("cow/data/opening_book/3210elo.bin")
TRANSPOSITION_TABLE = TranspositionTable(100000)
reset_transposition_table_flag = False
    
def quiescence(board : Board, depth: int, MAX_DEPTH: int, is_end_game: bool, alpha: float, beta: float, turn: int):
    # Kiểm tra kết thúc game.
    if (depth < MAX_DEPTH):
        if board.is_checkmate(): return -turn * (END_GAME_SCORE + END_GAME_SCORE / (board.fullmove_number + 1))
        if is_draw(board): return 0
    if depth == 0: return -turn * score(board, is_end_game)
    
    # Tạo nước đi hợp lệ cho quiescence search.
    moves = organize_moves_quiescence(board)
    if not moves: return -turn * score(board, is_end_game)
    
    # Tìm kiếm minimax
    if turn == 1:
        max_eval = float('-inf')
        for move in moves:
            board.push(move)
            eval = quiescence(board, depth - 1, MAX_DEPTH, is_end_game, alpha, beta, -1)
            board.pop()

            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in moves:
            board.push(move)
            eval = quiescence(board, depth - 1, MAX_DEPTH, is_end_game, alpha, beta, 1)
            board.pop()

            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval    

def minimax(board : Board, depth: int, MAX_DEPTH: int, cache: TranspositionTable, is_end_game: bool, alpha: float = -float('inf'), beta: float = float('inf'), turn: int = 1):
    """depth, MAX_DEPTH: số nửa nước đi."""
    # Kiểm tra kết thúc game.
    if board.is_checkmate(): return None, -turn * (END_GAME_SCORE + END_GAME_SCORE / (board.fullmove_number + 1))
    if is_draw(board): return None, 0

    # Transposition table
    cache_key = (board._transposition_key(), turn)

    if (depth + 2 <= MAX_DEPTH): 
        if (value := cache.get(cache_key, depth, alpha, beta)): 
            return value

    # Trường hợp cơ sở.
    if depth <= 0:
        eval = quiescence(board, 12, 12, is_end_game, alpha, beta, turn)
        cache.add(cache_key, (0, None, eval))
        return None, eval
                
    # Null move pruning
    if turn == 1:
        if (not is_end_game) and (beta != float('inf')) and ((1 < depth < 4) or ((-turn * score(board, is_end_game)) >= beta)):
            if is_null_ok(board):
                board.push(Move.null())
                _, eval = minimax(board, depth - 3, MAX_DEPTH, cache, is_end_game, alpha, beta, -1)
                board.pop()
                if eval >= beta: return None, beta
    else:
        if (not is_end_game) and (alpha != -float('inf')) and ((1 < depth < 4) or ((-turn * score(board, is_end_game)) <= alpha)):
            if is_null_ok(board):
                board.push(Move.null())
                _, eval = minimax(board, depth - 3, MAX_DEPTH, cache, is_end_game, alpha, beta, 1)
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
            _, eval = minimax(board, depth - 1, MAX_DEPTH, cache, is_end_game, alpha, beta, -1)
            board.pop()

            if eval > max_eval:
                max_eval = eval
                best_move = move

            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        cache.add(cache_key, (depth, best_move, max_eval))
        return best_move, max_eval
    else:
        min_eval = float('inf')
        best_move = None
        for move in legal_moves:
            board.push(move)
            _, eval = minimax(board, depth - 1, MAX_DEPTH, cache, is_end_game, alpha, beta, 1)
            board.pop()

            if eval < min_eval:
                min_eval = eval
                best_move = move
                
            beta = min(beta, eval)
            if beta <= alpha:
                break
        cache.add(cache_key, (depth, best_move, min_eval))
        return best_move, min_eval
    
def get_best_move(board: Board, depth):
    """depth: số nước đi"""
    # Tra sách khai cuộc
    try: return OPENING_BOOK.weighted_choice(board).move.uci()
    except:
        is_end_game = board.occupied.bit_count() <= 5

        # Tìm nước đi tốt nhất ở Endgame tablebase khi số quân cờ <= 5
        if is_end_game:
            wdl = EGTABLEBASE.get_wdl(board, 0)
            if wdl > 0:
                # Nếu bên đang thắng không có quân tốt thì tìm nước đi tốt nhất.
                if not (board.pawns & board.occupied_co[board.turn]):
                    return _get_best_move(board)
            elif wdl < 0:
                # Nếu bên đang thắng không có quân tốt thì tìm nước đi tốt nhất.
                if not (board.pawns & board.occupied_co[not board.turn]):
                    return _get_best_move(board)

        # reset transposition table khi số quân cờ <= 5 
        # (Do khi đó sử dụng thêm Endgame tablebase cho score() nên điểm số có thể thay đổi).
        global reset_transposition_table_flag
        if (not reset_transposition_table_flag) and is_end_game:
            reset_transposition_table_flag = True
            TRANSPOSITION_TABLE.clear()

        if reset_transposition_table_flag and (not is_end_game): 
            reset_transposition_table_flag = False
            TRANSPOSITION_TABLE.clear()

        # Tìm kiếm nước đi tốt nhất bằng minimax
        move, _ = minimax(board, depth * 2, depth * 2, TRANSPOSITION_TABLE, is_end_game)
        return move.uci()
    
def _get_best_move(board: Board):
    """
    Tìm nước đi tốt nhất khi bàn cờ chỉ còn 3-4-5 quân cờ và bên đang thắng không có quân tốt.

    Lý do cho việc này: syzygy chỉ hỗ trợ tính khoảng cách dtz 
    (số nửa nước đi cần thiết để đặt được zeroing move, bao gồm ăn quân hoặc đi tốt.)
    """
    z = {}
    for move in board.generate_legal_moves():
        board.push(move)

        if board.is_checkmate():
            board.pop()
            return move.uci()
        
        z[move] = score(board, True)
        board.pop()
    return max(z, key=z.get).uci()

def play(board: Board, depth: int = 2):
    """depth: số nước đi """
    return get_best_move(board, depth)

