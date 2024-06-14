from collections import OrderedDict
from functools import lru_cache
from chess import Board, Move, QUEEN, BLACK, WHITE, BB_RANK_1, BB_RANK_8, msb, scan_reversed
from chess import BB_FILES, BB_ALL, BB_FILE_A, BB_FILE_H


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

def is_draw(board: Board):
    return (board.is_insufficient_material() 
            or (not any(board.generate_legal_moves())) 
            or board.is_fifty_moves() 
            or board.is_repetition(3))

class TranspositionTable:
    def __init__(self, max_size: int = 100000):
        self.__max_size = max_size
        self.__table = OrderedDict()

    def add(self, key, value):
        if key in self.__table:
            self.__table.move_to_end(key)
        else:
            if len(self.__table) >= self.__max_size:
                self.__table.popitem(last=False)
        self.__table[key] = value        

    def get(self, key, depth, alpha, beta):
        if key not in self.__table: 
            return None
        
        v_depth, v_move, v_eval = self.__table[key]
        
        if depth <= v_depth: 
            if v_depth == 0:
                return v_move, v_eval
            
            if key[-1] == 1:
                if v_eval <= alpha: 
                    return v_move, v_eval
            else:
                if v_eval >= beta: 
                    return v_move, v_eval
        
        return None
    
    def __contains__(self, key):
        return key in self.__table
    
    def clear(self):
        self.__table.clear()


@lru_cache(maxsize=2000)
def count_doubled_pawns(wpawns, bpawns):
    wdoubled_pawns_count, bdoubled_pawns_count = 0, 0
    for column in BB_FILES:
        wpawns_in_column  = (wpawns & column).bit_count()
        bpawns_in_column  = (bpawns & column).bit_count()
        wdoubled_pawns_count += wpawns_in_column - 1  if wpawns_in_column > 1 else 0
        bdoubled_pawns_count += bpawns_in_column - 1 if bpawns_in_column > 1 else 0

    return wdoubled_pawns_count, bdoubled_pawns_count

@lru_cache(maxsize=2000)
def calculate_passed_pawns_score(wpawns, bpawns):
    """Những con tốt có thể bị bắt bằng cách bắt tốt qua đường cũng được tính là tốt thông"""
    wp, bp = 0, 0
    for i in range(1, 6):
        wp |= wpawns << (8 * i)
        bp |= bpawns >> (8 * i)
    wp &= BB_ALL
    bp &= BB_ALL

    wps2 = ((wpawns - (wpawns & BB_FILE_A)) >> 1) | ((wpawns - (wpawns & BB_FILE_H)) << 1) 
    bps2 = (bpawns - (bpawns & BB_FILE_A)) >> 1 | (bpawns - (bpawns & BB_FILE_H)) << 1

    wp2, bp2 = 0, 0
    for i in range(1, 6):
        wp2 |= wps2 << (8 * i)
        bp2 |= bps2 >> (8 * i)
    wp2 &= BB_ALL
    bp2 &= BB_ALL

    wpassed_pawns = wpawns & ~bp & ~bp2
    bpassed_pawns = bpawns & ~wp & ~wp2

    z1 = 0
    z2 = 0
    for square in scan_reversed(wpassed_pawns):
        z1 += 8 - (7 - square // 8)
    for square in scan_reversed(bpassed_pawns):
        z2 += 8 - square // 8
    
    return z1, z2


