import sys
import pygame
import numpy as np
from const import *

pygame.init()
WIDTH = 600
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("X si 0")

screen.fill(BG_COLOR)


class StartWindow:
    def __init__(self):
        self.running = True
        self.depth = 3

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.running = False
                    elif event.key == pygame.K_UP:
                        self.depth = min(10, self.depth + 1)
                    elif event.key == pygame.K_DOWN:
                        self.depth = max(3, self.depth - 1)

            self.draw()
            pygame.display.flip()

        return self.depth

    def draw(self):
        screen.fill(BG_COLOR)

        font = pygame.font.Font(None, 36)
        text = font.render("Press Enter to start", True, (255, 255, 255))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)

        depth_text = font.render(f"AI Depth: {self.depth}", True, (255, 255, 255))
        depth_rect = depth_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(depth_text, depth_rect)

        pygame.display.flip()


def main_game(selected_depth):
    screen.fill(BG_COLOR)

    class Board:
        def __init__(self):
            self.squares = np.zeros((LIN, COL))
            self.empty_squares = np.copy(self.squares)
            self.marked_squares = 0

        def final(self):
            for j in range(COL):
                if self.squares[0][j] == self.squares[1][j] == self.squares[2][j] == self.squares[3][j] != 0:
                    return self.squares[0][j]

            for i in range(LIN):
                if self.squares[i][0] == self.squares[i][1] == self.squares[i][2] == self.squares[i][3] != 0:
                    return self.squares[i][0]

            if self.squares[0][0] == self.squares[1][1] == self.squares[2][2] == self.squares[3][3] != 0:
                return self.squares[0][0]

            if self.squares[0][3] == self.squares[1][2] == self.squares[2][1] == self.squares[3][0] != 0:
                return self.squares[0][3]

            return 0

        def mark_square(self, row, col, player):
            self.squares[row][col] = player

        def empty_square(self, row, col):
            return self.squares[row][col] == 0

        def is_full(self):
            return self.marked_squares == LIN * COL

        def is_empty(self):
            return self.marked_squares == 0


    def lines():
        for i in range(1, COL):
            pygame.draw.line(screen, LINE_COLOR, (SQ_SIZE * i, 0), (SQ_SIZE * i, HEIGHT), LINE_WIDTH)

        for i in range(1, LIN):
            pygame.draw.line(screen, LINE_COLOR, (0, SQ_SIZE * i), (WIDTH, SQ_SIZE * i), LINE_WIDTH)

    class Game:
        def __init__(self):
            self.board = Board()
            self.player = 1
            self.score = {"Player 1": 0, "AI": 0}
            lines()

        def reset_board(self):
            self.board = Board()
            self.player = 1

        def show_end_message(self, winner):
            if winner == 1:
                message = "Player 1 wins!"
                self.score["Player 1"] += 1
            elif winner == 2:
                message = "AI wins!"
                self.score["AI"] += 1
            else:
                message = "It's a tie!"

            font = pygame.font.Font(None, 36)
            text = font.render(message, True, (255, 0, 0))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text, text_rect)

            font = pygame.font.Font(None, 40)
            player1_score_text = font.render(f"Player 1: {self.score['Player 1']}", True, (0, 255, 0))
            player2_score_text = font.render(f"AI: {self.score['AI']}", True, (0, 255, 0))
            screen.blit(player1_score_text, (10, 10))
            screen.blit(player2_score_text, (10, 40))

            pygame.display.update()
            pygame.time.delay(3000)
            screen.fill(BG_COLOR)
            lines()
            self.reset_board()

        def draw_fig(self, row, col):
            if self.player == 1:
                pygame.draw.line(screen, CROSS_COLOR, (col * SQ_SIZE + 30, row * SQ_SIZE + SQ_SIZE - 30),
                                 (col * SQ_SIZE + SQ_SIZE - 30, row * SQ_SIZE + 30), LINE_WIDTH)
                pygame.draw.line(screen, CROSS_COLOR, (col * SQ_SIZE + 30, row * SQ_SIZE + 30),
                                 (col * SQ_SIZE + SQ_SIZE - 30, row * SQ_SIZE + SQ_SIZE - 30), LINE_WIDTH)

            if self.player == 2:
                pygame.draw.circle(screen, CIRCLE_COLOR, (col * SQ_SIZE + SQ_SIZE // 2, row * SQ_SIZE + SQ_SIZE // 2),
                                   50,
                                   LINE_WIDTH)

        def ai_move(self, depth):
            best_score = float('-inf')
            best_move = None
            alpha = float('-inf')
            beta = float('inf')

            for row in range(LIN):
                for col in range(COL):
                    if self.board.empty_square(row, col):
                        self.board.mark_square(row, col, self.player)
                        score = self.minimax(self.board, 0, False, depth, alpha, beta)
                        self.board.mark_square(row, col, 0)

                        if score > best_score:
                            best_score = score
                            best_move = (row, col)

                        alpha = max(alpha, best_score)
                        if alpha >= beta:
                            break

            if best_move:
                row, col = best_move
                self.board.mark_square(row, col, self.player)
                self.draw_fig(row, col)
                self.player = self.player % 2 + 1
                self.board.marked_squares += 1

                winner = self.board.final()
                if winner == 1:
                    self.show_end_message(1)
                elif winner == 2:
                    self.show_end_message(2)
                elif self.board.is_full():
                    self.show_end_message(0)

        def minimax(self, board, depth, is_maximizing, max_depth, alpha, beta):
            if board.final() == 1:
                return -1
            elif board.final() == 2:
                return 1
            elif board.is_full() or depth >= max_depth:
                return 0

            if is_maximizing:
                best_score = float('-inf')
                for row in range(LIN):
                    for col in range(COL):
                        if board.empty_square(row, col):
                            board.mark_square(row, col, 2)
                            score = self.minimax(board, depth + 1, False, max_depth, alpha, beta)
                            board.mark_square(row, col, 0)
                            best_score = max(score, best_score)
                            alpha = max(alpha, best_score)
                            if alpha >= beta:
                                return best_score
                return best_score
            else:
                best_score = float('inf')
                for row in range(LIN):
                    for col in range(COL):
                        if board.empty_square(row, col):
                            board.mark_square(row, col, 1)
                            score = self.minimax(board, depth + 1, True, max_depth, alpha, beta)
                            board.mark_square(row, col, 0)
                            best_score = min(score, best_score)
                            beta = min(beta, best_score)
                            if beta <= alpha:
                                return best_score
                return best_score

    game = Game()
    lines()
    pygame.display.update()
    finished = False

    depth = selected_depth

    while not finished:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                position = event.pos
                row = position[1] // SQ_SIZE
                col = position[0] // SQ_SIZE

                if game.board.empty_square(row, col):
                    game.board.mark_square(row, col, game.player)
                    game.board.marked_squares += 1
                    game.draw_fig(row, col)
                    game.player = game.player % 2 + 1
                    print(game.board.squares)
                    print(game.board.marked_squares)
                    game.ai_move(depth)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                start_window = StartWindow()
                depth = start_window.run()
                game = Game()
                screen.fill(BG_COLOR)
                lines()
                pygame.display.update()

        if game.board.is_full():
            game.show_end_message(0)
            finished = True

        pygame.display.update()


if __name__ == "__main__":
    start_window = StartWindow()
    selected_depth = start_window.run()
    main_game(selected_depth)