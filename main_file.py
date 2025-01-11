import pygame
import random

class Game:
    """
    A game where the player clicks on a wanted character within a time limit.
    - Each level starts with 4 characters and adds 3 more after each success.
    - The player must find the target character within 40 seconds.
    - The player is allowed up to 3 misses per level.
    """

    def __init__(self):
        """
        Initializes the game by setting up pygame, loading assets (images, sounds),
        setting up the screen, and initializing game state variables.
        """
        pygame.init() # Initialize all pygame modules
        pygame.mixer.init()  # Initialize the mixer for sounds

        # Game display variables
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 1100, 600 #The size of the screen.
        self.WHITE = (255, 255, 255) #RGB color code.
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Wanted")

        # Game state variables
        self.score = 0
        self.misses = 0
        self.remaining_time = 40 # 40 seconds per level
        self.target_pos = None # Position of the target character
        self.target_image = None # Target character's image
        self.target_speed = [2, 2] # Speed of the target character
        self.moving_characters = [] # List of non-target characters
        self.total_characters = 4 # Start with 4 characters

        # Load game assets
        self.correct_sound, self.wrong_sound, self.background_change_sound = self.load_sounds()
        self.images = self.load_images()
        self.backgrounds_and_characters = self.load_backgrounds()
        self.current_background = None

        # Play background sound in a loop
        if self.background_change_sound:
            pygame.mixer.Sound.play(self.background_change_sound, loops=-1)

    @staticmethod #A static method used to load images without requiring an instance of the class.
                  #This method doesn't depend on any instance attributes or methods, so it is defined as static.
    def load_sounds():
        """"
        Loads and returns the sound files for correct, wrong, and background change sounds
        """
        try:
            correct_sound = pygame.mixer.Sound("correct-6033.mp3")
            wrong_sound = pygame.mixer.Sound("wrong-100536.mp3")
            background_change_sound = pygame.mixer.Sound("fast-rocky-loop-275535.mp3")
            return correct_sound, wrong_sound, background_change_sound
        except pygame.error as e:
            print(f"Error loading sound: {e}")
            return None, None, None

    @staticmethod #A static method used to load images without requiring an instance of the class.
                  #This method doesn't depend on any instance attributes or methods, so it is defined as static.
    def load_images():
        """
        Loads the images for all characters and scales them to a fixed size.
        Returns a dictionary with character names as keys and image objects as values.
        If an image fails to load, it prints an error and skips the character.
        """
        characters = ["yoshi", "luigi", "mario", "brown", "toad", "wario"]
        images = {}
        for char in characters:
            try:
                images[char] = pygame.transform.scale(pygame.image.load(f"{char}.png"), (70, 70))
            except pygame.error as e:
                print(f"Error loading image for {char}: {e}")
                images[char] = None
        return images

    def load_backgrounds(self):
        """
        Loads the backgrounds for each character and associates them with the character images.
        """
        backgrounds_and_characters = {}
        for char, image in self.images.items():
            try:
                background = pygame.image.load(f"{char}_background.png")
                backgrounds_and_characters[background] = image
            except pygame.error as e:
                print(f"Error loading background for {char}: {e}")
        return backgrounds_and_characters

    def reset_game_state(self, reset_score=False):
        """
        Resets the game state, including score, number of characters, target position,
        moving characters, and remaining time.
        If reset_score is True, the score will be reset to zero.
        """
        if reset_score:
            self.score = 0
            self.total_characters = 4
        self.select_new_background_and_target()
        self.set_target_position()
        self.set_moving_characters()
        self.remaining_time = 40
        self.misses = 0

    def select_new_background_and_target(self):
        """
        Randomly selects a new background and target character, and sets a random speed
        for the target character.
        """
        self.current_background, self.target_image = random.choice(list(self.backgrounds_and_characters.items()))
        self.target_speed = [random.randint(2, 5), random.randint(2, 5)]
        self.current_background = pygame.transform.scale(self.current_background, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

    def set_target_position(self):
        """
        Randomly sets the position of the target character on the screen.
        """
        self.target_pos = [random.randint(self.SCREEN_WIDTH // 2, self.SCREEN_WIDTH - 50),
                           random.randint(50, self.SCREEN_HEIGHT - 50)]

    def set_moving_characters(self):
        """
        Sets up the moving characters for the current level. The total number of characters
        is based on the current level (starts with 4 characters).
        """
        all_characters = list(self.backgrounds_and_characters.values())
        all_characters.remove(self.target_image)
        self.moving_characters = []
        for _ in range(self.total_characters):
            char = random.choice(all_characters)
            speed = [random.randint(2, 5), random.randint(2, 5)]
            self.moving_characters.append({
                "pos": [random.randint(self.SCREEN_WIDTH // 2, self.SCREEN_WIDTH - 50),
                        random.randint(50, self.SCREEN_HEIGHT - 50)],
                "speed": speed,
                "image": char,
            })

    def handle_events(self):
        """
        Handles all user inputs such as mouse clicks and closing the game window.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event.pos)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
        return True

    def handle_mouse_click(self, mouse_pos):
        """
        Handle mouse clicks to check if the target is hit.
        """
        target_rect = self.target_image.get_rect(topleft=self.target_pos)
        if target_rect.collidepoint(mouse_pos):
            self.score += 1
            if self.correct_sound:
                self.correct_sound.play()
            self.total_characters += 2
            self.reset_game_state()
        else:
            self.misses += 1
            if self.wrong_sound:
                self.wrong_sound.play()
            if self.misses >= 3:  # Allow 3 misses
                self.show_game_over_screen()

    def move_target(self):
        """
        Move the target character within the screen boundaries.
        """
        self.target_pos[0] += self.target_speed[0]
        self.target_pos[1] += self.target_speed[1]
        if self.target_pos[0] < self.SCREEN_WIDTH // 2 or self.target_pos[0] + 70 > self.SCREEN_WIDTH:
            self.target_speed[0] *= -1
        if self.target_pos[1] < 0 or self.target_pos[1] + 70 > self.SCREEN_HEIGHT:
            self.target_speed[1] *= -1

    def move_characters(self):
        """
        Move other characters within the screen boundaries.
        """
        for char in self.moving_characters:
            char["pos"][0] += char["speed"][0]
            char["pos"][1] += char["speed"][1]
            if char["pos"][0] < self.SCREEN_WIDTH // 2 or char["pos"][0] + 70 > self.SCREEN_WIDTH:
                char["speed"][0] *= -1
            if char["pos"][1] < 0 or char["pos"][1] + 70 > self.SCREEN_HEIGHT:
                char["speed"][1] *= -1

    def draw_screen(self):
        """
        Draw the game elements on the screen.
        """
        self.screen.fill(self.WHITE)
        self.screen.blit(self.current_background, (0, 0))
        self.screen.blit(self.target_image, self.target_pos)
        for char in self.moving_characters:
            self.screen.blit(char["image"], char["pos"])

        font = pygame.font.Font("MessyFont.ttf", 30)
        score_text = font.render(f"Score: {self.score}", True, (0, 0, 0))
        timer_text = font.render(f"Time: {int(self.remaining_time)}", True, (0, 0, 0))
        misses_text = font.render(f"Misses: {self.misses}/3", True, (0, 0, 0))
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(timer_text, (10, 50))
        self.screen.blit(misses_text, (10, 90))
        pygame.display.flip()

    def show_flashing_wanted_screen(self):
        """ This method displays the flashing 'WANTED' text and background image at the beginning. """
        try:
            flashing_text_font = pygame.font.Font("SuperFreak.ttf", 300)
            text = flashing_text_font.render("WANTED", True, (225, 225, 225))  # Initial color red

            flashing_background = pygame.image.load("wanted_background.png")
            flashing_background = pygame.transform.scale(flashing_background, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

            for _ in range(6):
                self.screen.blit(flashing_background, (0, 0))
                if _ % 2 == 0:
                    # Flash with text
                    self.screen.blit(text, (
                        self.SCREEN_WIDTH // 2 - text.get_width() // 2,
                        self.SCREEN_HEIGHT // 2 - text.get_height() // 2
                    ))
                pygame.display.flip()
                pygame.time.delay(300)

            self.screen.blit(flashing_background, (0, 0))
            self.screen.blit(text, (
                self.SCREEN_WIDTH // 2 - text.get_width() // 2,
                self.SCREEN_HEIGHT // 2 - text.get_height() // 2
            ))
            pygame.display.flip()
            pygame.time.delay(3000)
        except ( FileNotFoundError, Exception) as e:
            print(f"An error show_flashing_wanted_screen occurred: {e}")

    def show_instructions_screen(self):
        """Display the opening screen with instructions."""
        try:
            instructions_image = pygame.image.load("instructions_background.png")
            instructions_image = pygame.transform.scale(instructions_image, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

            instructions = [
                "Spot the Fugitive Character!",
                "Some characters have disappeared into the crowd.",
                "Can you spot the wanted ones?",
                "Mission: Find the wanted character before time runs out.",
                "Lives: You have 3 chances per level.",
                "Timer: You have 40 seconds to find the target.",
                "Score: Find the target to score points.",
                "Ready to test your skills? Press ENTER to start the chase.",
            ]

            font = pygame.font.Font("curly_font.ttf", 28)

            self.screen.blit(instructions_image, (0, 0))
            total_text_height = len(instructions) * font.get_height()
            start_y = (self.SCREEN_HEIGHT - total_text_height) // 2

            for i, line in enumerate(instructions):
                text = font.render(line, True, (255, 255, 255))
                text_width = text.get_width()
                text_x = (self.SCREEN_WIDTH - text_width) // 2
                self.screen.blit(text, (text_x, start_y + i * font.get_height()))

            pygame.display.flip()
        except (FileNotFoundError, Exception) as e:
            print(f"An error show_instructions_screen occurred: {e}")

    def show_game_over_screen(self):
        """
        Display the game over screen and reset the game if the player chooses to continue.
        """
        try:
            game_over_image = pygame.image.load("game_over_background.png")
            game_over_image = pygame.transform.scale(game_over_image, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

            font = pygame.font.Font("curly_font.ttf", 170)
            text1 = font.render("Game Over", True, (255, 255, 255))

            font = pygame.font.Font("curly_font.ttf", 50)
            text = font.render("Close, but not close enough!", True, (255, 255, 255))

            score_text = font.render(f"Final Score: {self.score}", True, (255, 255, 255))

            self.screen.blit(game_over_image, (0, 0))
            self.screen.blit(text1, (self.SCREEN_WIDTH // 2 - text1.get_width() // 2,
                                     self.SCREEN_HEIGHT // 4 - text1.get_height() // 2))
            self.screen.blit(text, (self.SCREEN_WIDTH // 2 - text.get_width() // 2,
                                    self.SCREEN_HEIGHT // 2 - text.get_height() // 2))

            self.screen.blit(score_text, (self.SCREEN_WIDTH // 2 - score_text.get_width() // 2,
                                          self.SCREEN_HEIGHT // 1.5 - score_text.get_height() // 2))

            pygame.display.flip()
            pygame.time.delay(5000)
            self.ask_to_play_again()
        except (FileNotFoundError, Exception) as e:
            print(f"An error occurred in show_game_over_screen: {e}")

    def ask_to_play_again(self):
        """
        Display the play again screen and continue based on players input to either run again or exit
        """
        try:
            font = pygame.font.Font("curly_font.ttf", 110)
            play_again = font.render("Press ENTER to play", True, (225, 225, 225))
            play_again_text = font.render("again or ESC to quit", True, (225, 225, 225))

            background = pygame.image.load("play_again_background.png")
            background = pygame.transform.scale(background, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            self.screen.blit(background, (0, 0))

            text_width = max(play_again.get_width(), play_again_text.get_width())
            text_height = play_again.get_height() + play_again_text.get_height()
            text_x = (self.SCREEN_WIDTH - text_width) // 2
            text_y = (self.SCREEN_HEIGHT - text_height) // 2

            self.screen.blit(play_again, (text_x, text_y))
            self.screen.blit(play_again_text, (text_x, text_y + play_again.get_height()))

            pygame.display.flip()

            waiting_for_input = True
            while waiting_for_input:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            self.reset_game_state(reset_score=True)
                            waiting_for_input = False
                        elif event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            exit()
        except (FileNotFoundError, Exception) as e:
            print(f"An error ask_to_play_again occurred: {e}")

    def play(self):
        """ Main game loop that handles events, updates, and drawing """
        self.show_flashing_wanted_screen()
        self.show_instructions_screen()

        waiting_for_start = True
        while waiting_for_start:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        waiting_for_start = False

        self.reset_game_state()

        while self.remaining_time > 0 and self.misses < 3:
            game_active = self.handle_events()
            if not game_active:
                pygame.quit()
                exit()

            self.move_target()
            self.move_characters()

            self.remaining_time -= 1 / 60
            self.draw_screen()
            self.clock.tick(60) # Maintain 60 FPS - the display refreshes the image 60 times per second.

        if self.misses >= 3 or self.remaining_time <= 0:
            self.show_game_over_screen()

if __name__ == "__main__":
    game = Game()
    game.play()
