"""
UI system demonstration showing various widgets and layouts.
"""

import pygame
from engine import *
from engine.ui import *

class UIDemo(Scene):
    """Scene demonstrating UI widgets and features."""
    
    def __init__(self):
        super().__init__("UIDemo")
        self.ui_manager = None
        self.slider_value = 0.5
        self.button_clicks = 0
        
    def on_enter(self) -> None:
        super().on_enter()
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self) -> None:
        """Setup all UI elements."""
        screen_size = pygame.display.get_surface().get_size()
        self.ui_manager = UIManager(screen_size)
        
        # Main panel
        main_panel = Panel(
            pygame.Rect(50, 50, screen_size[0] - 100, screen_size[1] - 100),
            name="main_panel",
            background_color=pygame.Color(40, 40, 40, 200),
            border_color=pygame.Color(100, 100, 100),
            border_width=2
        )
        self.ui_manager.add_widget(main_panel)
        
        # Title
        title = Label(
            pygame.Rect(20, 20, 300, 40),
            "UI System Demo",
            name="title"
        )
        title.text_color = pygame.Color(255, 255, 255)
        title.align_x = 'center'
        main_panel.add_child(title)
        
        # Buttons section
        self.setup_buttons(main_panel)
        
        # Sliders section
        self.setup_sliders(main_panel)
        
        # Labels section
        self.setup_labels(main_panel)
        
        # Input demonstration
        self.setup_input_demo(main_panel)
        
    def setup_buttons(self, parent: Widget) -> None:
        """Setup button demonstrations."""
        # Section title
        button_title = Label(
            pygame.Rect(20, 80, 200, 30),
            "Buttons:",
            name="button_title"
        )
        button_title.text_color = pygame.Color(255, 255, 0)
        parent.add_child(button_title)
        
        # Basic button
        basic_button = Button(
            pygame.Rect(20, 120, 120, 40),
            "Click Me!",
            name="basic_button"
        )
        basic_button.add_event_handler("clicked", self.on_basic_button_clicked)
        parent.add_child(basic_button)
        
        # Styled button
        styled_button = Button(
            pygame.Rect(160, 120, 120, 40),
            "Styled",
            name="styled_button"
        )
        # Customize colors
        styled_button.colors[WidgetState.NORMAL]['background'] = pygame.Color(0, 100, 200)
        styled_button.colors[WidgetState.HOVER]['background'] = pygame.Color(0, 120, 240)
        styled_button.colors[WidgetState.PRESSED]['background'] = pygame.Color(0, 80, 160)
        styled_button.add_event_handler("clicked", self.on_styled_button_clicked)
        parent.add_child(styled_button)
        
        # Disabled button
        disabled_button = Button(
            pygame.Rect(300, 120, 120, 40),
            "Disabled",
            name="disabled_button"
        )
        disabled_button.enabled = False
        parent.add_child(disabled_button)
        
        # Click counter
        self.click_counter = Label(
            pygame.Rect(20, 170, 300, 25),
            f"Button clicks: {self.button_clicks}",
            name="click_counter"
        )
        self.click_counter.text_color = pygame.Color(200, 200, 200)
        parent.add_child(self.click_counter)
        
    def setup_sliders(self, parent: Widget) -> None:
        """Setup slider demonstrations."""
        # Section title
        slider_title = Label(
            pygame.Rect(20, 220, 200, 30),
            "Sliders:",
            name="slider_title"
        )
        slider_title.text_color = pygame.Color(255, 255, 0)
        parent.add_child(slider_title)
        
        # Horizontal slider
        self.main_slider = Slider(
            pygame.Rect(20, 260, 200, 30),
            min_value=0.0,
            max_value=1.0,
            value=self.slider_value,
            name="main_slider"
        )
        self.main_slider.add_event_handler("value_changed", self.on_slider_changed)
        parent.add_child(self.main_slider)
        
        # Slider value display
        self.slider_value_label = Label(
            pygame.Rect(240, 260, 100, 30),
            f"{self.slider_value:.2f}",
            name="slider_value"
        )
        self.slider_value_label.text_color = pygame.Color(255, 255, 255)
        parent.add_child(self.slider_value_label)
        
        # Volume slider (demonstrates different range)
        volume_label = Label(
            pygame.Rect(20, 300, 80, 25),
            "Volume:",
            name="volume_label"
        )
        volume_label.text_color = pygame.Color(200, 200, 200)
        parent.add_child(volume_label)
        
        volume_slider = Slider(
            pygame.Rect(100, 300, 150, 25),
            min_value=0.0,
            max_value=100.0,
            value=75.0,
            name="volume_slider"
        )
        volume_slider.handle_color = pygame.Color(0, 255, 0)
        volume_slider.add_event_handler("value_changed", self.on_volume_changed)
        parent.add_child(volume_slider)
        
        self.volume_display = Label(
            pygame.Rect(260, 300, 60, 25),
            "75%",
            name="volume_display"
        )
        self.volume_display.text_color = pygame.Color(255, 255, 255)
        parent.add_child(self.volume_display)
        
    def setup_labels(self, parent: Widget) -> None:
        """Setup label demonstrations."""
        # Section title
        label_title = Label(
            pygame.Rect(450, 80, 200, 30),
            "Labels:",
            name="label_title"
        )
        label_title.text_color = pygame.Color(255, 255, 0)
        parent.add_child(label_title)
        
        # Different alignments
        left_label = Label(
            pygame.Rect(450, 120, 200, 25),
            "Left aligned",
            name="left_label"
        )
        left_label.align_x = 'left'
        left_label.text_color = pygame.Color(255, 255, 255)
        parent.add_child(left_label)
        
        center_label = Label(
            pygame.Rect(450, 150, 200, 25),
            "Center aligned",
            name="center_label"
        )
        center_label.align_x = 'center'
        center_label.text_color = pygame.Color(255, 255, 255)
        parent.add_child(center_label)
        
        right_label = Label(
            pygame.Rect(450, 180, 200, 25),
            "Right aligned",
            name="right_label"
        )
        right_label.align_x = 'right'
        right_label.text_color = pygame.Color(255, 255, 255)
        parent.add_child(right_label)
        
        # Colored labels
        red_label = Label(
            pygame.Rect(450, 220, 200, 25),
            "Red text",
            name="red_label"
        )
        red_label.text_color = pygame.Color(255, 100, 100)
        parent.add_child(red_label)
        
        green_label = Label(
            pygame.Rect(450, 245, 200, 25),
            "Green text",
            name="green_label"
        )
        green_label.text_color = pygame.Color(100, 255, 100)
        parent.add_child(green_label)
        
        blue_label = Label(
            pygame.Rect(450, 270, 200, 25),
            "Blue text",
            name="blue_label"
        )
        blue_label.text_color = pygame.Color(100, 100, 255)
        parent.add_child(blue_label)
        
    def setup_input_demo(self, parent: Widget) -> None:
        """Setup input demonstration area."""
        # Section title
        input_title = Label(
            pygame.Rect(20, 350, 200, 30),
            "Interactive Demo:",
            name="input_title"
        )
        input_title.text_color = pygame.Color(255, 255, 0)
        parent.add_child(input_title)
        
        # Toggle button
        self.toggle_button = Button(
            pygame.Rect(20, 390, 100, 35),
            "OFF",
            name="toggle_button"
        )
        self.toggle_button.add_event_handler("clicked", self.on_toggle_clicked)
        self.toggle_state = False
        parent.add_child(self.toggle_button)
        
        # Reset button
        reset_button = Button(
            pygame.Rect(140, 390, 100, 35),
            "Reset",
            name="reset_button"
        )
        reset_button.add_event_handler("clicked", self.on_reset_clicked)
        reset_button.colors[WidgetState.NORMAL]['background'] = pygame.Color(150, 50, 50)
        reset_button.colors[WidgetState.HOVER]['background'] = pygame.Color(180, 60, 60)
        parent.add_child(reset_button)
        
        # Status display
        self.status_label = Label(
            pygame.Rect(20, 435, 400, 25),
            "Status: Ready",
            name="status_label"
        )
        self.status_label.text_color = pygame.Color(200, 200, 200)
        parent.add_child(self.status_label)
        
        # Instructions
        instructions = Label(
            pygame.Rect(20, 480, 600, 60),
            "Instructions:\n• Click buttons to interact\n• Drag sliders to change values\n• Use ESC to quit",
            name="instructions"
        )
        instructions.text_color = pygame.Color(150, 150, 150)
        instructions.align_y = 'top'
        parent.add_child(instructions)
        
    def on_basic_button_clicked(self, event: UIEvent) -> None:
        """Handle basic button click."""
        self.button_clicks += 1
        self.click_counter.set_text(f"Button clicks: {self.button_clicks}")
        self.status_label.set_text("Status: Basic button clicked!")
        
    def on_styled_button_clicked(self, event: UIEvent) -> None:
        """Handle styled button click."""
        self.button_clicks += 1
        self.click_counter.set_text(f"Button clicks: {self.button_clicks}")
        self.status_label.set_text("Status: Styled button clicked!")
        
    def on_slider_changed(self, event: UIEvent) -> None:
        """Handle main slider value change."""
        self.slider_value = event.data
        self.slider_value_label.set_text(f"{self.slider_value:.2f}")
        self.status_label.set_text(f"Status: Slider value = {self.slider_value:.2f}")
        
    def on_volume_changed(self, event: UIEvent) -> None:
        """Handle volume slider change."""
        volume = int(event.data)
        self.volume_display.set_text(f"{volume}%")
        self.status_label.set_text(f"Status: Volume = {volume}%")
        
    def on_toggle_clicked(self, event: UIEvent) -> None:
        """Handle toggle button click."""
        self.toggle_state = not self.toggle_state
        
        if self.toggle_state:
            self.toggle_button.set_text("ON")
            self.toggle_button.colors[WidgetState.NORMAL]['background'] = pygame.Color(0, 150, 0)
            self.toggle_button.colors[WidgetState.HOVER]['background'] = pygame.Color(0, 180, 0)
            self.status_label.set_text("Status: Toggle is ON")
        else:
            self.toggle_button.set_text("OFF")
            self.toggle_button.colors[WidgetState.NORMAL]['background'] = pygame.Color(100, 100, 100)
            self.toggle_button.colors[WidgetState.HOVER]['background'] = pygame.Color(120, 120, 120)
            self.status_label.set_text("Status: Toggle is OFF")
            
    def on_reset_clicked(self, event: UIEvent) -> None:
        """Handle reset button click."""
        # Reset values
        self.button_clicks = 0
        self.slider_value = 0.5
        self.toggle_state = False
        
        # Update UI
        self.click_counter.set_text(f"Button clicks: {self.button_clicks}")
        self.slider_value_label.set_text(f"{self.slider_value:.2f}")
        self.main_slider.value = self.slider_value
        
        self.toggle_button.set_text("OFF")
        self.toggle_button.colors[WidgetState.NORMAL]['background'] = pygame.Color(100, 100, 100)
        self.toggle_button.colors[WidgetState.HOVER]['background'] = pygame.Color(120, 120, 120)
        
        # Reset volume slider
        volume_slider = self.ui_manager.find_widget("volume_slider")
        if volume_slider:
            volume_slider.value = 75.0
        self.volume_display.set_text("75%")
        
        self.status_label.set_text("Status: Reset complete")
        
    def update(self, dt: float) -> None:
        super().update(dt)
        
        # Update UI
        if self.ui_manager:
            self.ui_manager.update(dt)
            
    def render(self, screen: pygame.Surface) -> None:
        # Gradient background
        self.background_color = pygame.Color(30, 30, 50)
        super().render(screen)
        
        # Render UI
        if self.ui_manager:
            self.ui_manager.render(screen)
            
    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        
        # Handle UI events first
        if self.ui_manager:
            if self.ui_manager.handle_event(event):
                return  # UI handled the event
                
        # Handle other events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.game:
                    self.game.quit()

def main():
    """Main function to run the UI demo."""
    # Create game
    game = Game(800, 600, "Wicked Wizard Washdown - UI Demo")
    
    # Create and add the demo scene
    demo_scene = UIDemo()
    game.add_scene("ui_demo", demo_scene)
    game.load_scene("ui_demo")
    
    # Run the game
    game.run()

if __name__ == "__main__":
    main()
