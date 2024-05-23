from itertools import chain
from chess import Board, Move, PAWN, QUEEN, KING, BB_ALL, scan_reversed
from chess.syzygy import open_tablebase
from ._helper import generate_legal_promotion_queen_non_capture
from ._pesto_evaluation import calculate_score
from ._piece_evaluation import get_move_static_score

END_GAME_SCORE = 10000000
EGTABLEBASE = open_tablebase("cow/data/syzygy/3-4-5") 

def score(board: Board, is_end_game: bool) -> float:
    """
    Trả về điểm số trạng thái hiện tại của bàn cờ.

    Bao gồm điểm số từ bảng đánh giá kết hợp thông tin từ bảng kết thúc game.
    """
    if is_end_game:
        dtz = -EGTABLEBASE.get_dtz(board, 0)
        if dtz > 0: 
            # Vẫn xử lý kém ở các trường hợp tàn cuộc mà bên đang thắng có tốt. 
            # Sẽ cải thiện trong tương lai.
            pawns = board.pawns & board.occupied_co[not board.turn] & BB_ALL
            return (END_GAME_SCORE - dtz * 1000 
                    - any(scan_reversed(pawns)) * END_GAME_SCORE / 10 
                    + calculate_score(board) / 100)           
        if dtz < 0: return (-END_GAME_SCORE - dtz * 1000) + calculate_score(board) / 100
    return calculate_score(board) 

PIECE_VALUES = [10, 30, 30, 50, 90, 1000]  # pawn, knight, bishop, rook, queen, king

def get_move_score(board: Board, move: Move) -> int:
    """Trả về điểm số của nước đi (được sử dụng để sắp xếp nước đi)."""
    if move.promotion == QUEEN: return 1
    if board.is_capture(move): 
        if board.is_en_passant(move): return 0
        if not any(board.attackers(not board.turn, move.to_square)): return PIECE_VALUES[board.piece_type_at(move.to_square) - 1]
        return PIECE_VALUES[board.piece_type_at(move.to_square) - 1] - PIECE_VALUES[board.piece_type_at(move.from_square) - 1]
    return (-2 * PIECE_VALUES[KING - 1]) + get_move_static_score(board, move)

def get_move_score_qs(board: Board, move: Move) -> int:
    """Trả về điểm số của nước đi (được sử dụng để sắp xếp nước đi cho hàm quiescence)."""
    if move.promotion == QUEEN: return 1
    if not any(board.attackers(not board.turn, move.to_square)): return PIECE_VALUES[board.piece_type_at(move.to_square) - 1]
    return PIECE_VALUES[board.piece_type_at(move.to_square) - 1] - PIECE_VALUES[board.piece_type_at(move.from_square) - 1]

def organize_moves_quiescence(board: Board) -> list[Move]:
    """Trả về các nước đi hợp lệ cho hàm quiessence search sau khi đã sắp xếp."""
    return sorted([move for move in chain(board.generate_legal_moves(BB_ALL, BB_ALL & board.occupied_co[not board.turn]), 
                                              generate_legal_promotion_queen_non_capture(board))
                                              if get_move_score_qs(board, move) > 0], 
                   key=lambda move: get_move_score_qs(board, move), reverse=True)

def organize_moves(board: Board) -> list[Move]:
    """Trả về các nước đi hợp lệ sau khi đã sắp xếp."""
    return sorted(board.generate_legal_moves(), key=lambda move: get_move_score(board, move), reverse=True)

def is_null_ok(board: Board) -> bool:
    """Kiểm tra xem có thể thực hiện nước đi null không."""
    if board.is_check() or (board.peek == Move.null()): return False
    for square in scan_reversed(board.occupied_co[board.turn]):
        if board.piece_type_at(square) not in [KING, PAWN]:
            return True
    return False