from functools import lru_cache
from chess import Board, Move, QUEEN, BLACK, WHITE, BB_SQUARES, Bitboard, square_rank, msb, scan_reversed

def generate_pseudo_legal_promotion_queen_non_capture(board: Board):
    pawns = board.pawns & board.occupied_co[board.turn]
    if not pawns:
        return
    
    if board.turn == WHITE: single_moves = pawns << 8 & ~board.occupied
    else: single_moves = pawns >> 8 & ~board.occupied

    for to_square in scan_reversed(single_moves):
        from_square = to_square + (8 if board.turn == BLACK else -8)
        if square_rank(to_square) in [0, 7]:
            yield Move(from_square, to_square, QUEEN)

def generate_legal_promotion_queen_non_capture(board: Board):
    """Hàm tạo các nước đi phong hậu không ăn quân đối phương."""
    king_mask = board.kings & board.occupied_co[board.turn]
    if king_mask:
        king = msb(king_mask)
        blockers = board._slider_blockers(king)
        checkers = board.attackers_mask(not board.turn, king)
        if checkers:
            for move in board._generate_evasions(king, checkers):
                if move.promotion == QUEEN and board._is_safe(king, blockers, move) and (not board.is_capture(move)):
                    yield move
        else:
            for move in generate_pseudo_legal_promotion_queen_non_capture(board):
                if board._is_safe(king, blockers, move):
                    yield move

@lru_cache(maxsize=100000)
def scan_reversed_new(bb: Bitboard):
    z = []
    while bb:
        z.append(r := bb.bit_length() - 1)
        bb ^= BB_SQUARES[r]
    return z