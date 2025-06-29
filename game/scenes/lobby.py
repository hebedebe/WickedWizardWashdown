from engine import Game, Scene
from engine.ui import UIManager, Button, Label
import pygame


class LobbyScene(Scene):
    """Scene for multiplayer lobby where players wait before starting a game."""
    
    def __init__(self):
        super().__init__("Lobby")
        self.ui_manager = None
        self.is_host = False
        self.connected_players = []
        
    def on_enter(self) -> None:
        super().on_enter()
        
        # Setup UI
        screen_size = pygame.display.get_surface().get_size()
        self.ui_manager = UIManager(screen_size)
        
        # Create title
        title_label = Label(
            pygame.Rect((screen_size[0] - 200) // 2, 50, 200, 40),
            "Game Lobby",
            name="title_label"
        )
        self.ui_manager.add_widget(title_label)
        
        # Player list label
        players_label = Label(
            pygame.Rect(50, 150, 300, 30),
            "Connected Players:",
            name="players_label"
        )
        self.ui_manager.add_widget(players_label)
        
        # Create lobby buttons
        self.create_lobby_buttons()
        
    def create_lobby_buttons(self) -> None:
        """Create buttons for lobby actions."""
        screen_size = pygame.display.get_surface().get_size()
        button_width = 200
        button_height = 50
        button_spacing = 20
        
        # Start Game button (only for host)
        start_game_button = Button(
            pygame.Rect((screen_size[0] - button_width) // 2, 
                       screen_size[1] - 150, button_width, button_height),
            "Start Game",
            name="start_game_button"
        )
        start_game_button.add_event_handler("clicked", self.on_start_game_clicked)
        self.ui_manager.add_widget(start_game_button)
        
        # Leave Lobby button
        leave_button = Button(
            pygame.Rect((screen_size[0] - button_width) // 2, 
                       screen_size[1] - 80, button_width, button_height),
            "Leave Lobby",
            name="leave_button"
        )
        leave_button.add_event_handler("clicked", self.on_leave_lobby_clicked)
        self.ui_manager.add_widget(leave_button)
        
    def on_start_game_clicked(self, event) -> None:
        """Handle start game button click."""
        if self.game and self.is_host:
            # TODO: Start multiplayer game
            self.game.load_scene("game")
            
    def on_leave_lobby_clicked(self, event) -> None:
        """Handle leave lobby button click."""
        if self.game:
            self.game.pop_scene()
            
    def update(self, dt: float) -> None:
        super().update(dt)
        
        if self.ui_manager:
            self.ui_manager.update(dt)
            
    def render(self, screen: pygame.Surface) -> None:
        # Dark green background
        self.background_color = pygame.Color(20, 40, 30)
        super().render(screen)
        
        # Render player list
        if self.connected_players:
            font = pygame.font.Font(None, 24)
            y_offset = 200
            for i, player in enumerate(self.connected_players):
                text = font.render(f"{i+1}. {player}", True, pygame.Color(255, 255, 255))
                screen.blit(text, (70, y_offset + i * 30))
        
        if self.ui_manager:
            self.ui_manager.render(screen)
            
    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        
        if self.ui_manager:
            if self.ui_manager.handle_event(event):
                return
                
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.game:
                    self.game.pop_scene()
                    
    def add_player(self, player_name: str) -> None:
        """Add a player to the lobby."""
        if player_name not in self.connected_players:
            self.connected_players.append(player_name)
            
    def remove_player(self, player_name: str) -> None:
        """Remove a player from the lobby."""
        if player_name in self.connected_players:
            self.connected_players.remove(player_name)