import pygame
from pygame.locals import *
import sys
import time
import random
import json
import os
from datetime import datetime
from enum import Enum

class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"

class Theme(Enum):
    DARK = "dark"
    LIGHT = "light"
    NEON = "neon"
    RETRO = "retro"

class TypingGame:
   
    def __init__(self):
        # Screen dimensions
        self.w = 1200
        self.h = 700
        
        # Game state
        self.reset = True
        self.active = False
        self.input_text = ''
        self.target_text = ''
        self.time_start = 0
        self.total_time = 0
        self.accuracy = 0
        self.wpm = 0
        self.end = False
        self.char_index = 0
        
        # Settings
        self.difficulty = Difficulty.MEDIUM
        self.theme = Theme.DARK
        self.sound_enabled = True
        
        # Statistics
        self.stats = self.load_stats()
        self.current_errors = 0
        self.correct_chars = 0
        
        # Colors - will be set by theme
        self.colors = {}
        self.set_theme_colors()
        
        # Real-time feedback
        self.char_colors = []
        
        # Initialize pygame
        pygame.init()
        
        # Load images with error handling
        try:
            self.open_img = pygame.image.load('type-speed-open.png')
            self.open_img = pygame.transform.scale(self.open_img, (self.w, self.h))
            
            self.bg = pygame.image.load('background.jpg')
            self.bg = pygame.transform.scale(self.bg, (self.w, self.h))
        except pygame.error:
            self.open_img = None
            self.bg = None
        
        # Sound system disabled for compatibility
        self.sound_enabled = False
        
        self.screen = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Advanced Speed Typing Test')
        
        # Fonts
        self.fonts = {
            'large': pygame.font.Font(None, 48),
            'medium': pygame.font.Font(None, 32),
            'small': pygame.font.Font(None, 24),
            'tiny': pygame.font.Font(None, 18)
        }
       
        
    def play_sound(self, sound_name):
        """Sound system disabled for compatibility"""
        pass
    
    def set_theme_colors(self):
        """Set colors based on current theme"""
        themes = {
            Theme.DARK: {
                'bg': (20, 20, 25),
                'text': (240, 240, 240),
                'correct': (100, 255, 100),
                'error': (255, 100, 100),
                'cursor': (255, 255, 100),
                'input_bg': (40, 40, 50),
                'input_border': (100, 100, 120),
                'button': (60, 60, 80),
                'button_hover': (80, 80, 100)
            },
            Theme.LIGHT: {
                'bg': (250, 250, 255),
                'text': (40, 40, 50),
                'correct': (50, 150, 50),
                'error': (200, 50, 50),
                'cursor': (100, 100, 200),
                'input_bg': (255, 255, 255),
                'input_border': (200, 200, 220),
                'button': (220, 220, 240),
                'button_hover': (200, 200, 220)
            },
            Theme.NEON: {
                'bg': (10, 0, 20),
                'text': (0, 255, 255),
                'correct': (0, 255, 100),
                'error': (255, 0, 100),
                'cursor': (255, 255, 0),
                'input_bg': (20, 0, 40),
                'input_border': (100, 0, 200),
                'button': (50, 0, 100),
                'button_hover': (80, 0, 160)
            }
        }
        self.colors = themes.get(self.theme, themes[Theme.DARK])
    
    def load_stats(self):
        """Load statistics from file"""
        try:
            with open('typing_stats.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                'games_played': 0,
                'best_wpm': 0,
                'best_accuracy': 0,
                'total_time': 0,
                'history': []
            }
    
    def save_stats(self):
        """Save statistics to file"""
        with open('typing_stats.json', 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def draw_text(self, msg, pos, font_size='medium', color=None, center=True):
        """Enhanced text drawing with better positioning"""
        if color is None:
            color = self.colors['text']
        
        font = self.fonts[font_size]
        text = font.render(msg, True, color)
        
        if center:
            if isinstance(pos, tuple) and len(pos) == 2:
                text_rect = text.get_rect(center=pos)
            else:
                text_rect = text.get_rect(center=(self.w // 2, pos))
        else:
            text_rect = text.get_rect(topleft=pos)
        
        self.screen.blit(text, text_rect)
        return text_rect   
        
    def get_text_by_difficulty(self):
        """Get text based on difficulty level"""
        try:
            with open('sentences.txt', 'r') as f:
                sentences = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            sentences = [
                "The quick brown fox jumps over the lazy dog.",
                "Programming is the art of telling another human what one wants the computer to do.",
                "In order to understand recursion, you must first understand recursion."
            ]
        
        if self.difficulty == Difficulty.EASY:
            # Return shorter, simpler sentences
            easy_sentences = [s for s in sentences if len(s) < 50 and s.count(',') <= 1]
            return random.choice(easy_sentences if easy_sentences else sentences[:3])
        elif self.difficulty == Difficulty.MEDIUM:
            # Return medium length sentences
            return random.choice(sentences)
        elif self.difficulty == Difficulty.HARD:
            # Return longer sentences or combine multiple
            if len(sentences) > 1 and random.random() < 0.5:
                return f"{random.choice(sentences)} {random.choice(sentences)}"
            return random.choice(sentences)
        else:  # EXPERT
            # Return very challenging text with numbers and symbols
            expert_additions = [
                "Programming languages: Python (2.7, 3.8+), JavaScript (ES6), C++ (ISO/IEC 14882:2017).",
                "Special characters: @#$%^&*()_+-=[]{}|;':,.<>?/~`!",
                "Mixed case: CamelCase, snake_case, kebab-case, PascalCase, SCREAMING_SNAKE_CASE."
            ]
            if random.random() < 0.3:
                return random.choice(expert_additions)
            return random.choice(sentences)

    def calculate_results(self):
        """Calculate typing results with improved accuracy"""
        if self.end:
            return
            
        self.total_time = time.time() - self.time_start
        
        # More accurate accuracy calculation
        if len(self.target_text) > 0:
            self.accuracy = (self.correct_chars / len(self.target_text)) * 100
        else:
            self.accuracy = 0
        
        # WPM calculation (standard: 5 characters = 1 word)
        if self.total_time > 0:
            self.wpm = (len(self.input_text) / 5) * (60 / self.total_time)
        else:
            self.wpm = 0
        
        self.end = True
        
        # Update statistics
        self.update_stats()
    
    def update_stats(self):
        """Update and save statistics"""
        self.stats['games_played'] += 1
        self.stats['total_time'] += self.total_time
        
        if self.wpm > self.stats['best_wpm']:
            self.stats['best_wpm'] = self.wpm
        
        if self.accuracy > self.stats['best_accuracy']:
            self.stats['best_accuracy'] = self.accuracy
        
        # Add to history
        game_record = {
            'date': datetime.now().isoformat(),
            'wpm': round(self.wpm, 1),
            'accuracy': round(self.accuracy, 1),
            'time': round(self.total_time, 1),
            'difficulty': self.difficulty.value,
            'errors': self.current_errors
        }
        
        self.stats['history'].append(game_record)
        
        # Keep only last 50 games
        if len(self.stats['history']) > 50:
            self.stats['history'] = self.stats['history'][-50:]
        
        self.save_stats()
    
    def draw_results_screen(self):
        """Draw comprehensive results screen"""
        self.screen.fill(self.colors['bg'])
        
        # Title
        self.draw_text("Test Complete!", (self.w // 2, 100), 'large', self.colors['text'])
        
        # Main results
        y_pos = 200
        results = [
            f"WPM: {self.wpm:.1f}",
            f"Accuracy: {self.accuracy:.1f}%",
            f"Time: {self.total_time:.1f}s",
            f"Errors: {self.current_errors}"
        ]
        
        for result in results:
            color = self.colors['correct'] if 'WPM' in result or 'Accuracy' in result else self.colors['text']
            self.draw_text(result, (self.w // 2, y_pos), 'medium', color)
            y_pos += 40
        
        # Personal bests
        y_pos += 30
        self.draw_text("Personal Bests:", (self.w // 2, y_pos), 'medium', self.colors['text'])
        y_pos += 40
        
        best_texts = [
            f"Best WPM: {self.stats['best_wpm']:.1f}",
            f"Best Accuracy: {self.stats['best_accuracy']:.1f}%",
            f"Games Played: {self.stats['games_played']}"
        ]
        
        for text in best_texts:
            self.draw_text(text, (self.w // 2, y_pos), 'small', self.colors['text'])
            y_pos += 30
        
        # Buttons
        self.draw_button("Play Again", (self.w // 2 - 100, self.h - 100), (200, 50))
        self.draw_button("Settings", (self.w // 2 + 120, self.h - 100), (120, 50))
    
    def draw_button(self, text, pos, size, hover=False):
        """Draw a modern button"""
        color = self.colors['button_hover'] if hover else self.colors['button']
        rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, self.colors['input_border'], rect, 2, border_radius=10)
        
        # Center text in button
        text_pos = (pos[0] + size[0] // 2, pos[1] + size[1] // 2)
        self.draw_text(text, text_pos, 'small', self.colors['text'])
        return rect

    def draw_typing_area(self):
        """Draw the main typing interface with real-time feedback"""
        # Input box
        input_rect = pygame.Rect(50, 400, self.w - 100, 60)
        pygame.draw.rect(self.screen, self.colors['input_bg'], input_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.colors['input_border'], input_rect, 3, border_radius=10)
        
        # Target text with character-by-character highlighting
        self.draw_highlighted_text()
        
        # Input text
        input_surface = self.fonts['medium'].render(self.input_text, True, self.colors['text'])
        self.screen.blit(input_surface, (70, 420))
        
        # Cursor
        if self.active and not self.end:
            cursor_x = 70 + input_surface.get_width()
            if int(time.time() * 2) % 2:  # Blinking cursor
                pygame.draw.line(self.screen, self.colors['cursor'], 
                               (cursor_x, 415), (cursor_x, 445), 2)
        
        # Real-time stats
        if self.active and not self.end and self.time_start > 0:
            current_time = time.time() - self.time_start
            current_wpm = (len(self.input_text) / 5) * (60 / max(current_time, 1))
            current_accuracy = (self.correct_chars / max(len(self.input_text), 1)) * 100 if len(self.input_text) > 0 else 100
            
            stats_text = f"WPM: {current_wpm:.0f} | Accuracy: {current_accuracy:.0f}% | Time: {current_time:.0f}s"
            self.draw_text(stats_text, (self.w // 2, 500), 'small', self.colors['text'])
    
    def draw_highlighted_text(self):
        """Draw target text with character-by-character highlighting"""
        if not self.target_text:
            return
        
        font = self.fonts['medium']
        x, y = 70, 300
        max_width = self.w - 140
        
        for i, char in enumerate(self.target_text):
            # Determine color based on typing progress
            if i < len(self.input_text):
                if i < len(self.input_text) and self.input_text[i] == char:
                    color = self.colors['correct']
                else:
                    color = self.colors['error']
            elif i == len(self.input_text):
                color = self.colors['cursor']  # Current character
            else:
                color = self.colors['text']  # Untyped characters
            
            char_surface = font.render(char, True, color)
            
            # Handle line wrapping
            if x + char_surface.get_width() > max_width:
                x = 70
                y += 35
            
            self.screen.blit(char_surface, (x, y))
            x += char_surface.get_width()
    
    def handle_typing(self, event):
        """Handle typing input with improved feedback"""
        if not self.active or self.end:
            return
        
        if event.key == pygame.K_RETURN:
            if len(self.input_text) >= len(self.target_text) * 0.8:  # Allow completion at 80%
                self.calculate_results()
            
        elif event.key == pygame.K_BACKSPACE:
            if len(self.input_text) > 0:
                self.input_text = self.input_text[:-1]
                self.char_index = len(self.input_text)
                # Recalculate correct chars
                self.correct_chars = sum(1 for i, c in enumerate(self.input_text) 
                                       if i < len(self.target_text) and c == self.target_text[i])
        
        elif event.unicode and event.unicode.isprintable():
            self.input_text += event.unicode
            
            # Check if character is correct
            if len(self.input_text) <= len(self.target_text):
                if self.input_text[-1] == self.target_text[len(self.input_text) - 1]:
                    self.correct_chars += 1
                else:
                    self.current_errors += 1
            
            # Auto-complete when reaching end
            if len(self.input_text) >= len(self.target_text):
                self.calculate_results()
    
    def run(self):
        """Main game loop with improved structure"""
        self.reset_game()
        clock = pygame.time.Clock()
        
        self.running = True
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                    sys.exit()
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.end:
                        # Check if clicking in input area
                        input_rect = pygame.Rect(50, 400, self.w - 100, 60)
                        if input_rect.collidepoint(mouse_pos):
                            self.active = True
                            if not self.time_start:
                                self.time_start = time.time()
                    else:
                        # Handle button clicks on results screen
                        play_again_rect = pygame.Rect(self.w // 2 - 100, self.h - 100, 200, 50)
                        settings_rect = pygame.Rect(self.w // 2 + 120, self.h - 100, 120, 50)
                        
                        if play_again_rect.collidepoint(mouse_pos):
                            self.reset_game()
                        elif settings_rect.collidepoint(mouse_pos):
                            self.show_settings_menu()
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.active:
                            self.active = False
                        else:
                            self.running = False
                    elif event.key == pygame.K_F1:  # F1 for quick settings
                        self.show_settings_menu()
                    elif event.key == pygame.K_F2:  # F2 to toggle theme
                        themes = list(Theme)
                        current_index = themes.index(self.theme)
                        self.theme = themes[(current_index + 1) % len(themes)]
                        self.set_theme_colors()
                    elif event.key == pygame.K_F3:  # F3 reserved for future features
                        pass  # Could add more features here
                    else:
                        self.handle_typing(event)
            
            # Draw everything
            if not self.end:
                self.draw_game_screen()
            else:
                self.draw_results_screen()
            
            pygame.display.flip()
            clock.tick(60)
    
    def draw_game_screen(self):
        """Draw the main game screen"""
        self.screen.fill(self.colors['bg'])
        
        # Draw background if available
        if self.bg:
            # Scale and center background
            bg_scaled = pygame.transform.scale(self.bg, (self.w, self.h))
            bg_surface = pygame.Surface((self.w, self.h))
            bg_surface.blit(bg_scaled, (0, 0))
            bg_surface.set_alpha(30)  # Make it subtle
            self.screen.blit(bg_surface, (0, 0))
        
        # Title
        self.draw_text("Advanced Speed Typing Test", (self.w // 2, 50), 'large', self.colors['text'])
        
        # Difficulty indicator
        diff_text = f"Difficulty: {self.difficulty.value.title()}"
        self.draw_text(diff_text, (self.w // 2, 100), 'small', self.colors['text'])
        
        # Instructions
        if not self.active:
            self.draw_text("Click in the text box below and start typing!", 
                         (self.w // 2, 150), 'small', self.colors['text'])
            self.draw_text("Press ESC to quit | Press ENTER to finish early (80% minimum)", 
                         (self.w // 2, 180), 'tiny', self.colors['text'])
            self.draw_text(f"Theme: {self.theme.value.title()} | Press F2 to change theme", 
                         (self.w // 2, 200), 'tiny', self.colors['text'])
        
        # Target text label
        self.draw_text("Type this text:", (self.w // 2, 250), 'small', self.colors['text'])
        
        # Main typing area
        self.draw_typing_area()
    
    def show_settings_menu(self):
        """Cycle through settings"""
        # Cycle through themes
        themes = list(Theme)
        current_index = themes.index(self.theme)
        self.theme = themes[(current_index + 1) % len(themes)]
        self.set_theme_colors()
        
        # Also cycle difficulty
        difficulties = list(Difficulty)
        current_index = difficulties.index(self.difficulty)
        self.difficulty = difficulties[(current_index + 1) % len(difficulties)]

    def reset_game(self):
        """Reset game state for a new round"""
        # Show splash screen briefly if available
        if self.open_img:
            self.screen.blit(pygame.transform.scale(self.open_img, (self.w, self.h)), (0, 0))
            pygame.display.flip()
            pygame.time.wait(500)  # Brief pause
        
        # Reset game state
        self.reset = False
        self.end = False
        self.active = False
        self.input_text = ''
        self.time_start = 0
        self.total_time = 0
        self.wpm = 0
        self.accuracy = 0
        self.char_index = 0
        self.current_errors = 0
        self.correct_chars = 0
        self.char_colors = []
        
        # Get new text based on difficulty
        self.target_text = self.get_text_by_difficulty()
        if not self.target_text:
            self.target_text = "The quick brown fox jumps over the lazy dog."
        
        # Initialize character colors
        self.char_colors = [self.colors['text']] * len(self.target_text)



if __name__ == "__main__":
    game = TypingGame()
    try:
        game.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    finally:
        pygame.quit()

