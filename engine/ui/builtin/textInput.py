import pygame
from ..widget import Widget

class TextInput(Widget):
    """
    Text input widget for entering text values.
    """
    
    def __init__(self, rect: pygame.Rect, initial_text: str = "", 
                 placeholder: str = "", font: pygame.font.Font = None,
                 name: str = "text_input"):
        super().__init__(rect, name)
        
        # Text properties
        self.text = initial_text
        self.placeholder = placeholder
        self.font = font or pygame.font.Font(None, 24)
        self.cursor_pos = len(self.text)
        self.selection_start = 0
        self.selection_end = 0
        
        # Visual properties
        self.background_color = pygame.Color(255, 255, 255)
        self.border_color = pygame.Color(128, 128, 128)
        self.text_color = pygame.Color(0, 0, 0)
        self.placeholder_color = pygame.Color(128, 128, 128)
        self.border_width = 2
        self.padding = 8
        
        # Focus state
        self.focused = False
        self.cursor_visible = True
        self.cursor_blink_time = 0
        self.cursor_blink_interval = 0.5
        
        # Input constraints
        self.max_length = None
        self.allowed_chars = None  # None for all, or set of allowed characters
        
    def set_focus(self, focused: bool) -> None:
        """Set focus state."""
        if self.focused != focused:
            self.focused = focused
            if focused:
                self.emit_event("focus_gained")
            else:
                self.emit_event("focus_lost")
    
    def insert_text(self, text: str) -> None:
        """Insert text at cursor position."""
        if not self.enabled:
            return
            
        # Filter allowed characters
        if self.allowed_chars:
            text = ''.join(c for c in text if c in self.allowed_chars)
        
        # Check max length
        if self.max_length and len(self.text) + len(text) > self.max_length:
            remaining = self.max_length - len(self.text)
            text = text[:remaining]
        
        if text:
            # Insert text at cursor
            self.text = self.text[:self.cursor_pos] + text + self.text[self.cursor_pos:]
            self.cursor_pos += len(text)
            self.emit_event("text_changed", self.text)
    
    def delete_char(self, direction: int = -1) -> None:
        """Delete character. direction: -1 for backspace, 1 for delete."""
        if not self.enabled or not self.text:
            return
            
        if direction == -1 and self.cursor_pos > 0:  # Backspace
            self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
            self.cursor_pos -= 1
        elif direction == 1 and self.cursor_pos < len(self.text):  # Delete
            self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
        
        self.emit_event("text_changed", self.text)
    
    def move_cursor(self, direction: int) -> None:
        """Move cursor. direction: -1 for left, 1 for right."""
        if direction == -1:
            self.cursor_pos = max(0, self.cursor_pos - 1)
        else:
            self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
    
    def get_text(self) -> str:
        """Get current text value."""
        return self.text
    
    def set_text(self, text: str) -> None:
        """Set text value."""
        self.text = text
        self.cursor_pos = min(self.cursor_pos, len(text))
        self.emit_event("text_changed", self.text)
    
    def clear(self) -> None:
        """Clear all text."""
        self.set_text("")
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        if not self.visible or not self.enabled:
            return False
        
        # Handle mouse clicks for focus
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.rect.collidepoint(event.pos):
                    self.set_focus(True)
                    # Position cursor based on click position
                    relative_x = event.pos[0] - self.rect.x - self.padding
                    text_width = 0
                    self.cursor_pos = 0
                    for i, char in enumerate(self.text):
                        char_width = self.font.size(char)[0]
                        if text_width + char_width // 2 > relative_x:
                            break
                        text_width += char_width
                        self.cursor_pos = i + 1
                    return True
                else:
                    self.set_focus(False)
        
        # Handle keyboard input when focused
        if self.focused and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.delete_char(-1)
            elif event.key == pygame.K_DELETE:
                self.delete_char(1)
            elif event.key == pygame.K_LEFT:
                self.move_cursor(-1)
            elif event.key == pygame.K_RIGHT:
                self.move_cursor(1)
            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0
            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.text)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                self.emit_event("enter_pressed", self.text)
                self.set_focus(False)
            elif event.unicode and event.unicode.isprintable():
                self.insert_text(event.unicode)
            return True
        
        return False
    
    def update(self, dt: float) -> None:
        """Update text input state."""
        super().update(dt)
        
        # Update cursor blinking
        if self.focused:
            self.cursor_blink_time += dt
            if self.cursor_blink_time >= self.cursor_blink_interval:
                self.cursor_visible = not self.cursor_visible
                self.cursor_blink_time = 0
        else:
            self.cursor_visible = False
    
    def render(self, screen: pygame.Surface) -> None:
        """Render the text input."""
        if not self.visible:
            return
        
        # Background
        pygame.draw.rect(screen, self.background_color, self.rect)
        
        # Border (thicker when focused)
        border_width = self.border_width + (1 if self.focused else 0)
        border_color = pygame.Color(0, 120, 215) if self.focused else self.border_color
        pygame.draw.rect(screen, border_color, self.rect, border_width)
        
        # Text content
        text_rect = pygame.Rect(
            self.rect.x + self.padding,
            self.rect.y + self.padding,
            self.rect.width - 2 * self.padding,
            self.rect.height - 2 * self.padding
        )
        
        # Render text or placeholder
        display_text = self.text if self.text else self.placeholder
        text_color = self.text_color if self.text else self.placeholder_color
        
        if display_text:
            # Clip text to fit in the input area
            text_surface = self.font.render(display_text, True, text_color)
            
            # Calculate text offset for scrolling if text is too long
            text_width = text_surface.get_width()
            if text_width > text_rect.width:
                # Calculate cursor position in pixels
                cursor_text = self.text[:self.cursor_pos]
                cursor_pixel_pos = self.font.size(cursor_text)[0]
                
                # Scroll to keep cursor visible
                if cursor_pixel_pos > text_rect.width - 10:
                    text_offset = text_rect.width - cursor_pixel_pos - 10
                else:
                    text_offset = 0
            else:
                text_offset = 0
            
            # Create clipping surface
            clipped_surface = pygame.Surface((text_rect.width, text_rect.height))
            clipped_surface.fill(self.background_color)
            clipped_surface.blit(text_surface, (text_offset, 0))
            
            # Render to screen
            screen.blit(clipped_surface, text_rect.topleft)
        
        # Render cursor
        if self.focused and self.cursor_visible and self.text:
            cursor_text = self.text[:self.cursor_pos]
            cursor_x = text_rect.x + self.font.size(cursor_text)[0]
            
            # Apply text offset for scrolling
            if display_text and self.font.size(display_text)[0] > text_rect.width:
                cursor_text = self.text[:self.cursor_pos]
                cursor_pixel_pos = self.font.size(cursor_text)[0]
                if cursor_pixel_pos > text_rect.width - 10:
                    cursor_x = text_rect.x + text_rect.width - 10
            
            pygame.draw.line(screen, self.text_color,
                           (cursor_x, text_rect.y + 2),
                           (cursor_x, text_rect.bottom - 2), 1)
        elif self.focused and self.cursor_visible and not self.text:
            # Cursor at start when no text
            pygame.draw.line(screen, self.text_color,
                           (text_rect.x, text_rect.y + 2),
                           (text_rect.x, text_rect.bottom - 2), 1)