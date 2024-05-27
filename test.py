import chess
import chess.syzygy
import time
import cow
import chess.polyglot


if __name__ == "__main__":
    board = chess.Board()
    board = chess.Board("r2q1rk1/1bpnbppp/p3pn2/1p6/3P1B2/2NBPN2/PPQ2PPP/R4RK1 w - - 2 12") # f1d1
    board = chess.Board("6k1/pp4p1/2p5/2bp4/8/P5Pb/1P3rrP/2BRRN1K b - - 0 1") # g2g1
    board = chess.Board("8/5P2/8/8/8/6K1/3k4/8 w - - 1 9") # f7f8q
    board = chess.Board("r2q1rk1/1bpnbppp/p3pn2/1p6/3P1B2/2NBPN2/PPQ2PPP/R4RK1 w - - 2 12") # f1d1
    board = chess.Board("4q1k1/5ppp/1p6/2p5/p1P5/P2P1N2/1b2rPPP/1Q1R1K2 w - - 0 28") # f3g1
    board = chess.Board("6k1/5ppp/1p6/2p1q3/p1Pb4/P2P3N/6PP/1Q1R1K2 w - - 5 32") # b1b6
    board = chess.Board("8/5k2/1p2p3/2p2p2/p1Pn2q1/P2Q2P1/1P3P2/5BK1 b - - 0 37") # d4f3
    board = chess.Board("6r1/7p/5k1P/1pP5/5p2/3n4/5PPK/2q5 w - - 0 46") # g2g4
    board = chess.Board("r7/4k1Pp/2n1p3/1pb5/3p3N/3P4/2P2PPP/4BRK1 w - - 0 29") # h4f3
    board = chess.Board("6k1/5pp1/1p2q3/2p4p/p1P5/P2P4/6PP/1Q4K1 w - - 0 37") # h2h4
    # board = chess.Board("2k2bnr/rp3b1p/p1q2N2/P1p1ppB1/3p4/3P2NP/1PP2PP1/1R1Q1RK1 w - - 7 25") # f6h5
    # board = chess.Board("r1bqkb1r/pp1ppppp/2n2n2/2p5/2P5/2N2N2/PP1PPPPP/R1BQKB1R w KQkq - 3 4") # g2g3
    # board = chess.Board("r2q1rk1/1bpnbppp/p3pn2/1p6/3P1B2/2NBPN2/PPQ2PPP/R4RK1 w - - 2 12") # f1d1
    # board = chess.Board("4q1k1/5ppp/1p6/2p5/p1P5/P2P1N2/1b2rPPP/1Q1R1K2 w - - 0 28") # f3g1
    # board = chess.Board("6k1/5ppp/1p6/2p1q3/p1Pb4/P2P3N/6PP/1Q1R1K2 w - - 5 32") # b1b6
    # board = chess.Board("r7/4k1Pp/2n1p3/1pb5/3p3N/3P4/2P2PPP/4BRK1 w - - 0 29") # h4f3
    # board = chess.Board("r7/4k1Pp/2n1p3/1p6/1b5N/2pP4/5PPP/5RK1 w - - 0 31") # h4f3
    # board = chess.Board("8/5k2/1p2p3/2p2p2/p1Pn2q1/P2Q2P1/1P3P2/5BK1 b - - 0 37") # d4f3
    # board = chess.Board("5k2/Q6p/3p2p1/1P1P4/1PK3P1/P7/5P2/3q4 b - - 0 38") # d1c2
    # board = chess.Board("5k2/Q6p/3p2p1/1P1P4/1P1K2P1/P7/2q2P2/8 b - - 2 39") # c2f2
    # board = chess.Board("4k3/8/8/8/8/8/8/4KBN1 w - - 0 1") # e1e2
    # board = chess.Board("1k6/1N6/1K2B3/8/8/8/8/8 w - - 54 28") # b7c5
    # board = chess.Board("4k3/8/8/8/8/8/8/4KBN1 w - - 0 1") # e1e2
    # board = chess.Board("4k3/8/8/8/8/3B4/8/4K1N1 b - - 1 1") # e8e7
    # board = chess.Board("r1q2rk1/1bpnbpp1/p3pn1p/1p6/3P1B2/P1NBPN2/1PQ2PPP/3R1RK1 w - - 1 14") # h2h3
    # board = chess.Board("r3K3/1P1P3P/8/4n3/3P4/8/5k2/8 w - - 0 1")
    # board = chess.Board("6k1/2r5/5K2/7Q/8/8/8/8 w - - 0 1")
    board = chess.Board("r2qr1k1/1bp2ppp/p7/1p1pP3/3P2Q1/1P2R3/1P1N1PPP/R5K1 b - - 2 17") # d8c8

    start_time = time.time()
    move = cow.play(board, 4)
    end_time = time.time()  
    print(move, end_time - start_time)

    # print(board.piece_at(1))

    # print(board.fen())
    # print(board.__str__)
    # print(board.fen())
    # print(board.epd())
    # print(board.board_fen())
    # print(board.legal_moves)
    # print(chess.LegalMoveGenerator(board))
    # print(board.pseudo_legal_moves)

    # board = chess.Board("4k3/8/8/8/8/8/8/4KBN1 w - - 0 1")
    # board = chess.Board("8/4k3/8/8/8/3B4/8/4K1N1 w - - 2 2")
    # board = chess.Board("8/4k3/8/8/8/3B4/8/4K1N1 w - - 2 2")
    # board = chess.Board("k7/3B4/NK6/8/8/8/8/8 w - - 60 31")
    # board = chess.Board("1k6/3B4/1K6/2N5/8/8/8/8 w - - 58 30")
    # board = chess.Board("4k3/8/8/8/8/3B4/8/4K1N1 b - - 1 1")

    # board = chess.Board("1k6/8/1K2B3/2N5/8/8/8/8 b - - 55 28")
    # path_to_tablebase = "ai1/data/syzygy/3-4-5"
    # tablebase = chess.syzygy.open_tablebase(path_to_tablebase)
    # start_time = time.time()
    # z = tablebase.probe_wdl(board)
    # end_time = time.time()  
    # print(z)
    # print(end_time - start_time)

    # hàm lấy số quân cờ trên bàn cờ
    # OPENING_BOOK = chess.polyglot.open_reader("ai1/data/opening_book/3210elo.bin")
    # move = OPENING_BOOK.weighted_choice(board).move
    # move = OPENING_BOOK.get(board).move
    # print(move)
    # print(EGTABLEBASE.get_wdl(board, 0))

    # print(board.fen())
    # print(board.epd())

    # a = chess.polyglot.zobrist_hash(board)
    # print(a)
    # print(board)
    # t = []
    # t1 = time.time()
    # for square in chess.scan_reversed(board.occupied):
    #     piece = board.piece_at(square)
        
    # t2 = time.time()
    # print(t2 - t1)
    
    # t1 = time.time()
    # z = []
    # for square, piece in board.piece_map().items():
    #     z.append(square)
    # t2 = time.time()
    # print(t2 - t1)

    # print(t)
    # print(z)


    # t = []
    # for i in board.generate_legal_moves():
    #     t.append(i)
    # z = []
    # for i in board.legal_moves:
    #     z.append(i)

    # print(t == z)
    # print(t)

    # print(len(list(chess.scan_reversed(board.occupied))))

    # import timeit

    # from cow._helper import scan_reversed_new
    # print(scan_reversed_new.cache_info())