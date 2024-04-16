import pygame
import os
import chess
from UI.screen import Screen

unicode_to_algebraic = {
    '♚': 'K', '♛': 'Q', '♜': 'R', '♝': 'B', '♞': 'N', '♟': 'P',
    '♔': 'k', '♕': 'q', '♖': 'r', '♗': 'b', '♘': 'n', '♙': 'p'
}

promotion_code = ['q', 'r', 'b', 'n']
promotion_list = ['queen', 'rook', 'bishop', 'knight']

class game_screen(Screen):
    def __init__(self, window_size):
        super().__init__(window_size)
        self.square_height = self.height // 8
        self.square_width = self.width // 8
        
    def click(self, mx, my):
        """_summary_

        Args:
            mx (int): x coordinate of mouse click
            my (int): y coordinate of mouse click
            
        return:
            (x, y): tile coordinates of the click
        """
        y = mx // self.square_width
        x = my // self.square_height
        return x, y
    def draw_square(self, screen, x, y, draw_board):
        loc = (x * (self.square_width), y * (self.square_height)) #position relative to the screen (pixel)

        color = 'light' if (x + y) % 2 == 1 else 'dark'
        draw_color = (238, 238, 210) if color == 'light' else (118, 150, 86)
        selected_color = (150, 255, 100)
        rect = pygame.Rect(loc[1], loc[0], self.square_width, self.square_height)
        
        pygame.draw.rect(screen, selected_color if draw_board[7-x][y][1] == 1 else draw_color, rect)
        return rect
        
    def draw(self, screen, board, draw_board, game_mode):
        screen.fill('white')
        
        for x in range(8):
            for y in range(8):
                # 0, 0 = a, 8; 0, 1 = b, 8 --> x 

                rect = self.draw_square(screen, x, y, draw_board)
                selected_color = (150, 255, 100)
                
                pos = chr(y + ord('a')) + chr((7 - x) + ord('1'))
                piece = board.piece_at(chess.parse_square(pos))

                if piece is not None:
                    piece_code = unicode_to_algebraic[piece.unicode_symbol()]
                    piece_str = None
                    match piece_code.lower():
                        case 'r':
                            piece_str = "rook" 
                        case 'n':
                            piece_str = "knight"
                        case 'b':
                            piece_str = "bishop"
                        case 'q':
                            piece_str = "queen"
                        case 'k':
                            piece_str = "king"
                        case 'p':
                            piece_str = "pawn"
                    
                    team_code = 'white' if piece_code.islower() else 'black'
                    
                    # img_path = 'C:/Users/kingk/Desktop/UET/CSTTNT/Chess/ChessAI1000elo/data/imgs/{0}-{1}.png'.format(team_code, piece_str)
                    # img_path = 'D:\\code\\co so AI\\ChessAI1000elo\\data\\imgs\\{0}-{1}.png'.format(team_code, piece_str)
                    
                    root = os.path.dirname(__file__) # 'D:\\code\\co so AI\\self_chess\\UI'
                    open_path = 'data\\imgs\\{0}-{1}.png'.format(team_code, piece_str)
                    # print(root)
                    
                    img_path = os.path.join('\\'.join(root.split('\\')[: -1]), open_path)
                    
                    image = pygame.image.load(img_path)
                    image = pygame.transform.scale(image, (self.square_width, self.square_height))

                    centering_rect = image.get_rect()
                    centering_rect.center = rect.center
                    screen.blit(image, centering_rect.topleft)

        if game_mode[0] + game_mode[1] > 0:
            pygame.draw.rect(screen, selected_color, pygame.Rect(600 + 20, self.square_height * 7, self.square_width, self.square_height))
            self.addText(screen, (630, self.square_height * 7 + (self.square_height * 1) // 5), "Undo")
        pygame.display.update()
        
    def addText(self, screen, pos, text, color = (0, 0, 0), backgroundColor = (255, 255, 255), button=False):
        title = pygame.font.SysFont('Arial', 25).render(text, True, color)
        temp_surface = pygame.Surface(title.get_size())
        temp_surface.fill(backgroundColor)
        temp_surface.blit(title, (0, 0))
        screen.blit(temp_surface, (pos[0], pos[1]))
        
