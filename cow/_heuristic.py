from itertools import chain
from chess import Board, Move, QUEEN, KING
from chess.syzygy import open_tablebase
from ._helper import generate_legal_promotion_queen_non_capture
from ._pesto_evaluation import calculate_score
from ._piece_evaluation import get_move_static_score

END_GAME_SCORE = 10000000
EGTABLEBASE = open_tablebase("cow/data/syzygy/3-4-5") 
PIECE_VALUES = [10, 30, 30, 50, 90, 1000]  # pawn, knight, bishop, rook, queen, king

def score(board: Board, is_end_game: bool) -> float:
    """
    Hàm này trả về điểm số của trạng thái hiện tại của bàn cờ (tính cho bên vừa di chuyển).

    Nếu số quân cờ trên bàn còn ít hơn 6 quân, sử dụng dtz từ tablebase để hỗ trợ đánh giá.

    Ý tưởng:

    (Trước tiên, tìm hiểu dtz và hàm get_dtz của thư viện python-chess)
    
    Điểm dược tính như sau:
    Nếu dtz > 0 (bên vừa đi đang thắng):
    - Điểm gốc: END_GAME_SCORE (điểm nhận được khi chiến thắng)
    - Trừ (dtz * 1000): Nếu bên thắng không có tốt, phần này giúp tiến nhanh đến các nước ăn quân. 
    (Cũng có thể hiểu là tiến nhanh tới chiến thắng)
    - Trừ (END_GAME_SCORE / 10) nếu bên đang thắng còn quân tốt. Mục đích loại bỏ quân tốt sớm nhất có thể.
    (Khi bên đang thắng có quân tốt, dtz luôn = 1 hoặc -2 tùy theo nước đi hiện tại của bên nào.)
    - Trừ (END_GAME_SCORE / 200) * số quân cờ còn lại bên đang thua. 
    - Điểm số đánh giá trạng thái tĩnh của bàn cờ / 10.
    (rất nhỏ, dùng để chọn node tốt nhất khi các thông số trên bằng nhau giữa các node)
    
    Tương tự với dtz < 0.
    """
    if is_end_game:
        dtz = -EGTABLEBASE.get_dtz(board, 0)
        if dtz > 0: 
            return (END_GAME_SCORE - dtz * 1000 
                    - ((board.pawns & board.occupied_co[not board.turn]) != 0) * END_GAME_SCORE / 10
                    - board.occupied_co[board.turn].bit_count() * END_GAME_SCORE / 200
                    + calculate_score(board) / 100)           
        if dtz < 0: 
            return (-END_GAME_SCORE - dtz * 1000 
                    + ((board.pawns & board.occupied_co[board.turn]) != 0) * END_GAME_SCORE / 10
                    + board.occupied_co[not board.turn].bit_count() * END_GAME_SCORE / 200 
                    + calculate_score(board) / 100)
    return calculate_score(board) 

def get_move_score(board: Board, move: Move) -> int:
    """
    Trả về điểm số của nước đi (được sử dụng để sắp xếp nước đi).
    
    Thứ tự ưu tiên:
    - Nước đi ăn quân không được bảo vệ
    - Nước đi ăn quân thắng (ví dụ tốt ăn mã, ...)
    - Nước đi phong hậu
    - Nước đi ăn quân hòa 
    - Nước đi ăn quân thua 
    - Nước đi không ăn quân, sắp xếp theo điểm số di chuyển tĩnh.
    """
    if board.is_capture(move): 
        # Bắt tốt qua đường
        if board.is_en_passant(move): 
            if not board._attackers_mask(not board.turn, move.to_square, board.occupied): 
                return PIECE_VALUES[0]
            return 0
        
        # ăn quân bình thường
        if not board._attackers_mask(not board.turn, move.to_square, board.occupied): 
            return PIECE_VALUES[board.piece_type_at(move.to_square) - 1]
        return PIECE_VALUES[board.piece_type_at(move.to_square) - 1] - PIECE_VALUES[board.piece_type_at(move.from_square) - 1]
    
    if move.promotion == QUEEN: return 2
    
    return (-2 * PIECE_VALUES[KING - 1]) + get_move_static_score(board, move)

def organize_moves(board: Board) -> list[Move]:
    """ Sinh ra tất cả các nước đi hợp lệ và sắp xếp chúng theo thứ tự giảm dần của get_move_score() """
    return sorted(list(board.generate_legal_moves()), key=lambda move: get_move_score(board, move), reverse=True)

def get_move_score_qs(board: Board, move: Move) -> int:
    """
    Trả về điểm số của nước đi (được sử dụng để sắp xếp nước đi cho hàm quiescence).
    
    Các nước đi dành cho hàm quiessence search đã được lọc trước khi gọi hàm này.

    Hàm này hỗ trợ sắp xếp các nước đi đã lọc.

    Thứ tự ưu tiên:
    - Nước đi ăn quân không được bảo vệ
    - Nước đi ăn quân thắng
    - Nước đi phong hậu
    """
    if move.promotion == QUEEN and (not board.is_capture(move)): return 2

    # Bắt tốt qua đường
    if board.is_en_passant(move):
        if not board._attackers_mask(not board.turn, move.to_square, board.occupied): 
            return PIECE_VALUES[0]
        return 0
    
    # ăn quân bình thường
    if not board._attackers_mask(not board.turn, move.to_square, board.occupied): 
        return PIECE_VALUES[board.piece_type_at(move.to_square) - 1]
    return PIECE_VALUES[board.piece_type_at(move.to_square) - 1] - PIECE_VALUES[board.piece_type_at(move.from_square) - 1]

def organize_moves_quiescence(board: Board) -> list[Move]:
    """
    Trả về các nước đi hợp lệ cho hàm quiessence search sau khi đã sắp xếp.

    Các nước đi dành cho hàm quiescence search bao gồm:
    - Nước đi ăn quân không đợc bảo vệ
    - Nước đi ăn quân thắng
    - Nước đi phong hậu
    """
    return sorted([move for move in chain(board.generate_legal_moves(to_mask = board.occupied_co[not board.turn]),
                                              board.generate_legal_ep(), 
                                              generate_legal_promotion_queen_non_capture(board))
                                              if get_move_score_qs(board, move) > 0], 
                   key=lambda move: get_move_score_qs(board, move), reverse=True)

def is_null_ok(board: Board) -> bool:
    """
    Kiểm tra xem có thể thực hiện nước đi null không.

    Các điều kiện bao gồm: 
    - Vua không bị chiếu
    - Nước đi trước đó không phải là nước đi null
    - Bên di chuyển tồn tại những quân khác không phải tốt hoặc vua.
    """
    if board.is_check() or (board.peek == Move.null()): return False
    if board.occupied_co[board.turn] & (board.knights | board.bishops | board.rooks | board.queens):
        return True
    return False