from functools import lru_cache
from chess import Board, Move, QUEEN, BLACK, WHITE, msb, scan_reversed, BB_RANK_1, BB_RANK_8

def generate_legal_promotion_queen_non_capture(board: Board):
    """Hàm tạo các nước đi phong hậu không ăn quân đối phương."""
    pawns = board.pawns & board.occupied_co[board.turn]
    if not pawns: return

    if board.turn == WHITE: 
        to_mask = (pawns << 8 & ~board.occupied) & BB_RANK_8
    else: 
        to_mask = (pawns >> 8 & ~board.occupied) & BB_RANK_1
    if not to_mask: return

    king_mask = board.kings & board.occupied_co[board.turn]
    if king_mask:
        king = msb(king_mask)
        blockers = board._slider_blockers(king)
        checkers = board.attackers_mask(not board.turn, king)
        if checkers:
            from_mask = (to_mask >> 8) if board.turn == WHITE else (to_mask << 8)
            for move in board._generate_evasions(king, checkers, from_mask, to_mask):
                if move.promotion == QUEEN and board._is_safe(king, blockers, move):
                    yield move
        else:
            for to_square in scan_reversed(to_mask):
                from_square = to_square + (8 if board.turn == BLACK else -8)
                move = Move(from_square, to_square, QUEEN)
                if board._is_safe(king, blockers, move):
                    yield move


