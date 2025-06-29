"""
User Interface system with widgets and event handling.
"""

import pygame
from typing import Dict, List, Optional, Callable, Any, Tuple
from abc import ABC, abstractmethod
from enum import Enum

class UIEvent:
    """UI event data structure."""
    
    def __init__(self, event_type: str, widget: 'Widget', data: Any = None):
        self.type = event_type
        self.widget = widget
        self.data = data

class WidgetState(Enum):
    """Widget visual states."""
    NORMAL = "normal"
    HOVER = "hover"
    PRESSED = "pressed"
    DISABLED = "disabled"

class Widget(ABC):
    """
    Base class for all UI widgets.
    """
    
    def __init__(self, rect: pygame.Rect, name: str = ""):
        self.rect = pygame.Rect(rect)
        self.name = name
        
        # Hierarchy
        self.parent: Optional['Widget'] = None
        self.children: List['Widget'] = []
        
        # State
        self.visible = True
        self.enabled = True
        self.state = WidgetState.NORMAL
        
        # Layout
        self.anchor = pygame.Vector2(0, 0)  # 0-1 relative to parent
        self.margin = pygame.Rect(0, 0, 0, 0)  # left, top, right, bottom
        self.padding = pygame.Rect(0, 0, 0, 0)
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Input state
        self.mouse_inside = False
        self.mouse_pressed = False
        
    def add_child(self, child: 'Widget') -> None:
        """Add a child widget."""
        if child.parent:
            child.parent.remove_child(child)
        child.parent = self
        self.children.append(child)
        
    def remove_child(self, child: 'Widget') -> None:
        """Remove a child widget."""
        if child in self.children:
            child.parent = None
            self.children.remove(child)
            
    def find_child(self, name: str) -> Optional['Widget']:
        """Find a child widget by name."""
        for child in self.children:
            if child.name == name:
                return child
            # Search recursively
            result = child.find_child(name)
            if result:
                return result
        return None
        
    def add_event_handler(self, event_type: str, handler: Callable) -> None:
        """Add an event handler."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        
    def remove_event_handler(self, event_type: str, handler: Callable) -> None:
        """Remove an event handler."""
        if event_type in self.event_handlers:
            if handler in self.event_handlers[event_type]:
                self.event_handlers[event_type].remove(handler)
                
    def emit_event(self, event_type: str, data: Any = None) -> None:
        """Emit a UI event."""
        event = UIEvent(event_type, self, data)
        
        # Call local handlers
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                handler(event)
                
        # Bubble up to parent
        if self.parent:
            self.parent.handle_child_event(event)
            
    def handle_child_event(self, event: UIEvent) -> None:
        """Handle events from child widgets."""
        # Can be overridden by subclasses
        pass
        
    def get_world_rect(self) -> pygame.Rect:
        """Get widget rectangle in world coordinates."""
        if self.parent:
            parent_rect = self.parent.get_content_rect()
            world_rect = pygame.Rect(
                parent_rect.x + self.rect.x,
                parent_rect.y + self.rect.y,
                self.rect.width,
                self.rect.height
            )
            return world_rect
        return pygame.Rect(self.rect)
        
    def get_content_rect(self) -> pygame.Rect:
        """Get the content area (excluding padding)."""
        world_rect = self.get_world_rect()
        return pygame.Rect(
            world_rect.x + self.padding.left,
            world_rect.y + self.padding.top,
            world_rect.width - self.padding.left - self.padding.right,
            world_rect.height - self.padding.top - self.padding.bottom
        )
        
    def contains_point(self, point: pygame.Vector2) -> bool:
        """Check if a point is inside this widget."""
        world_rect = self.get_world_rect()
        return world_rect.collidepoint(int(point.x), int(point.y))
        
    def update(self, dt: float) -> None:
        """Update widget logic."""
        if not self.visible:
            return
            
        # Update children
        for child in self.children:
            child.update(dt)
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events. Returns True if event was handled."""
        if not self.visible or not self.enabled:
            return False
            
        # Handle children first (front to back)
        for child in reversed(self.children):
            if child.handle_event(event):
                return True
        
        # Handle mouse events for this widget only if children didn't handle it
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.Vector2(event.pos)
            was_inside = self.mouse_inside
            self.mouse_inside = self.contains_point(mouse_pos)
            
            if self.mouse_inside and not was_inside:
                self.state = WidgetState.HOVER
                self.emit_event("mouse_enter")
            elif not self.mouse_inside and was_inside:
                self.state = WidgetState.NORMAL if not self.mouse_pressed else WidgetState.PRESSED
                self.emit_event("mouse_leave")
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = pygame.Vector2(event.pos)
                if self.contains_point(mouse_pos):
                    self.mouse_pressed = True
                    self.state = WidgetState.PRESSED
                    self.emit_event("mouse_down", event)
                    return True
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                if self.mouse_pressed:
                    self.mouse_pressed = False
                    mouse_pos = pygame.Vector2(event.pos)
                    
                    if self.contains_point(mouse_pos):
                        self.state = WidgetState.HOVER
                        self.emit_event("clicked", event)
                    else:
                        self.state = WidgetState.NORMAL
                        
                    self.emit_event("mouse_up", event)
                    return True
                
        return False
        
    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        """Render the widget."""
        pass

class Panel(Widget):
    """
    Basic panel widget for layout and grouping.
    """
    
    def __init__(self, rect: pygame.Rect, name: str = "", 
                 background_color: pygame.Color = None,
                 border_color: pygame.Color = None,
                 border_width: int = 0):
        super().__init__(rect, name)
        self.background_color = background_color or pygame.Color(100, 100, 100, 200)
        self.border_color = border_color or pygame.Color(200, 200, 200)
        self.border_width = border_width
        
    def render(self, screen: pygame.Surface) -> None:
        """Render the panel."""
        if not self.visible:
            return
            
        world_rect = self.get_world_rect()
        
        # Draw background
        if self.background_color.a > 0:
            if self.background_color.a < 255:
                # Create surface for alpha blending
                surf = pygame.Surface((world_rect.width, world_rect.height), pygame.SRCALPHA)
                surf.fill(self.background_color)
                screen.blit(surf, world_rect.topleft)
            else:
                pygame.draw.rect(screen, self.background_color, world_rect)
                
        # Draw border
        if self.border_width > 0:
            pygame.draw.rect(screen, self.border_color, world_rect, self.border_width)
            
        # Render children
        for child in self.children:
            child.render(screen)

class Label(Widget):
    """
    Text label widget.
    """
    
    def __init__(self, rect: pygame.Rect, text: str = "", 
                 font: pygame.font.Font = None,
                 text_color: pygame.Color = None,
                 background_color: pygame.Color = None,
                 name: str = ""):
        super().__init__(rect, name)
        self.text = text
        
        # Use default font if none provided
        if font is None:
            try:
                from .. import Game
                game = Game.get_instance()
                font = game.asset_manager.get_default_font()
            except:
                font = pygame.font.Font(None, 24)
                
        self.font = font
        self.text_color = text_color or pygame.Color(255, 255, 255)
        self.background_color = background_color or pygame.Color(0, 0, 0, 0)
        
        # Text alignment
        self.align_x = 'center'  # 'left', 'center', 'right'
        self.align_y = 'center'  # 'top', 'center', 'bottom'
        
        # Cached rendered text
        self._rendered_text: Optional[pygame.Surface] = None
        self._last_text = ""
        
    def set_text(self, text: str) -> None:
        """Set the label text."""
        if text != self.text:
            self.text = text
            self._rendered_text = None  # Invalidate cache
            
    def _render_text(self) -> pygame.Surface:
        """Render the text surface."""
        if self._rendered_text is None or self._last_text != self.text:
            self._rendered_text = self.font.render(self.text, True, self.text_color)
            self._last_text = self.text
        return self._rendered_text
        
    def render(self, screen: pygame.Surface) -> None:
        """Render the label."""
        if not self.visible:
            return
            
        world_rect = self.get_world_rect()
        
        # Draw background
        if self.background_color.a > 0:
            if self.background_color.a < 255:
                surf = pygame.Surface((world_rect.width, world_rect.height), pygame.SRCALPHA)
                surf.fill(self.background_color)
                screen.blit(surf, world_rect.topleft)
            else:
                pygame.draw.rect(screen, self.background_color, world_rect)
                
        # Draw text
        if self.text:
            text_surface = self._render_text()
            text_rect = text_surface.get_rect()
            
            # Align horizontally
            if self.align_x == 'left':
                text_rect.left = world_rect.left + self.padding.left
            elif self.align_x == 'right':
                text_rect.right = world_rect.right - self.padding.right
            else:  # center
                text_rect.centerx = world_rect.centerx
                
            # Align vertically
            if self.align_y == 'top':
                text_rect.top = world_rect.top + self.padding.top
            elif self.align_y == 'bottom':
                text_rect.bottom = world_rect.bottom - self.padding.bottom
            else:  # center
                text_rect.centery = world_rect.centery
                
            screen.blit(text_surface, text_rect)
            
        # Render children
        for child in self.children:
            child.render(screen)

class Button(Widget):
    """
    Clickable button widget.
    """
    
    def __init__(self, rect: pygame.Rect, text: str = "",
                 font: pygame.font.Font = None,
                 name: str = ""):
        super().__init__(rect, name)
        self.text = text
        
        # Use default font if none provided
        if font is None:
            try:
                from .. import Game
                game = Game.get_instance()
                font = game.asset_manager.get_default_font()
            except:
                font = pygame.font.Font(None, 24)
                
        self.font = font
        
        # State-based colors
        self.colors = {
            WidgetState.NORMAL: {
                'background': pygame.Color(100, 100, 100),
                'text': pygame.Color(255, 255, 255),
                'border': pygame.Color(150, 150, 150)
            },
            WidgetState.HOVER: {
                'background': pygame.Color(120, 120, 120),
                'text': pygame.Color(255, 255, 255),
                'border': pygame.Color(200, 200, 200)
            },
            WidgetState.PRESSED: {
                'background': pygame.Color(80, 80, 80),
                'text': pygame.Color(255, 255, 255),
                'border': pygame.Color(100, 100, 100)
            },
            WidgetState.DISABLED: {
                'background': pygame.Color(60, 60, 60),
                'text': pygame.Color(100, 100, 100),
                'border': pygame.Color(80, 80, 80)
            }
        }
        
        self.border_width = 2
        
    def set_text(self, text: str) -> None:
        """Set button text."""
        self.text = text
        
    def render(self, screen: pygame.Surface) -> None:
        """Render the button."""
        if not self.visible:
            return
            
        world_rect = self.get_world_rect()
        state = WidgetState.DISABLED if not self.enabled else self.state
        colors = self.colors[state]
        
        # Draw background
        pygame.draw.rect(screen, colors['background'], world_rect)
        
        # Draw border
        if self.border_width > 0:
            pygame.draw.rect(screen, colors['border'], world_rect, self.border_width)
            
        # Draw text
        if self.text:
            text_surface = self.font.render(self.text, True, colors['text'])
            text_rect = text_surface.get_rect()
            text_rect.center = world_rect.center
            screen.blit(text_surface, text_rect)
            
        # Render children
        for child in self.children:
            child.render(screen)

class Slider(Widget):
    """
    Slider widget for value selection.
    """
    
    def __init__(self, rect: pygame.Rect, min_value: float = 0.0, 
                 max_value: float = 1.0, value: float = 0.5,
                 name: str = ""):
        super().__init__(rect, name)
        self.min_value = min_value
        self.max_value = max_value
        self._value = value
        
        # Visual properties
        self.track_color = pygame.Color(100, 100, 100)
        self.handle_color = pygame.Color(200, 200, 200)
        self.handle_size = 20
        
        # Interaction
        self.dragging = False
        
    @property
    def value(self) -> float:
        """Get the current value."""
        return self._value
        
    @value.setter
    def value(self, val: float) -> None:
        """Set the current value."""
        old_value = self._value
        self._value = max(self.min_value, min(self.max_value, val))
        if old_value != self._value:
            self.emit_event("value_changed", self._value)
            
    def get_handle_rect(self) -> pygame.Rect:
        """Get the handle rectangle."""
        world_rect = self.get_world_rect()
        
        # Calculate handle position
        range_val = self.max_value - self.min_value
        if range_val > 0:
            ratio = (self._value - self.min_value) / range_val
        else:
            ratio = 0
            
        handle_x = world_rect.x + ratio * (world_rect.width - self.handle_size)
        handle_y = world_rect.centery - self.handle_size // 2
        
        return pygame.Rect(handle_x, handle_y, self.handle_size, self.handle_size)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle slider-specific events."""
        if not self.visible or not self.enabled:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = pygame.Vector2(event.pos)
                handle_rect = self.get_handle_rect()
                
                if handle_rect.collidepoint(int(mouse_pos.x), int(mouse_pos.y)):
                    self.dragging = True
                    return True
                elif self.contains_point(mouse_pos):
                    # Click on track - move handle to mouse position
                    self._update_value_from_mouse(mouse_pos)
                    self.dragging = True
                    return True
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging:
                self.dragging = False
                return True
                
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_pos = pygame.Vector2(event.pos)
                self._update_value_from_mouse(mouse_pos)
                return True
                
        return super().handle_event(event)
        
    def _update_value_from_mouse(self, mouse_pos: pygame.Vector2) -> None:
        """Update value based on mouse position."""
        world_rect = self.get_world_rect()
        
        # Calculate ratio
        ratio = (mouse_pos.x - world_rect.x) / world_rect.width
        ratio = max(0, min(1, ratio))
        
        # Update value
        new_value = self.min_value + ratio * (self.max_value - self.min_value)
        self.value = new_value
        
    def render(self, screen: pygame.Surface) -> None:
        """Render the slider."""
        if not self.visible:
            return
            
        world_rect = self.get_world_rect()
        
        # Draw track
        track_rect = pygame.Rect(
            world_rect.x, 
            world_rect.centery - 2,
            world_rect.width,
            4
        )
        pygame.draw.rect(screen, self.track_color, track_rect)
        
        # Draw handle
        handle_rect = self.get_handle_rect()
        handle_color = self.handle_color
        
        if self.state == WidgetState.HOVER or self.dragging:
            handle_color = pygame.Color(min(255, handle_color.r + 50),
                                      min(255, handle_color.g + 50),
                                      min(255, handle_color.b + 50))
        elif self.state == WidgetState.PRESSED:
            handle_color = pygame.Color(max(0, handle_color.r - 50),
                                      max(0, handle_color.g - 50),
                                      max(0, handle_color.b - 50))
            
        pygame.draw.circle(screen, handle_color, handle_rect.center, self.handle_size // 2)
        
        # Render children
        for child in self.children:
            child.render(screen)

class FPSDisplay(Label):
    """
    FPS display widget that automatically updates with current frame rate.
    """
    
    def __init__(self, rect: pygame.Rect, font: pygame.font.Font = None,
                 name: str = "fps_display", update_interval: float = 0.5):
        super().__init__(rect, "FPS: --", font, name)
        
        # FPS tracking
        self.frame_times = []
        self.update_interval = update_interval  # How often to update FPS display
        self.last_update = 0
        self.current_fps = 0
        
        # Default styling for FPS display
        self.text_color = pygame.Color(255, 255, 0)  # Yellow text
        self.align_x = 'left'
        self.align_y = 'top'
        
    def update(self, dt: float) -> None:
        """Update FPS calculation and display."""
        super().update(dt)
        
        # Track frame time
        if dt > 0:
            self.frame_times.append(dt)
            
        # Keep only recent frame times (last 60 frames)
        if len(self.frame_times) > 60:
            self.frame_times.pop(0)
            
        # Update display periodically
        self.last_update += dt
        if self.last_update >= self.update_interval and self.frame_times:
            # Calculate average FPS
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            self.current_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
            
            # Update text
            self.set_text(f"FPS: {self.current_fps:.1f}")
            self.last_update = 0
            
    def get_fps(self) -> float:
        """Get the current FPS value."""
        return self.current_fps

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
        
class UIManager:
    """
    Manages the UI system and widget hierarchy.
    """
    
    def __init__(self, screen_size: Tuple[int, int]):
        self.screen_size = screen_size
        self.root_widgets: List[Widget] = []
        self.focused_widget: Optional[Widget] = None
        
    def add_widget(self, widget: Widget) -> None:
        """Add a root-level widget."""
        self.root_widgets.append(widget)
        
    def remove_widget(self, widget: Widget) -> None:
        """Remove a root-level widget."""
        if widget in self.root_widgets:
            self.root_widgets.remove(widget)
            
    def find_widget(self, name: str) -> Optional[Widget]:
        """Find a widget by name."""
        for widget in self.root_widgets:
            if widget.name == name:
                return widget
            result = widget.find_child(name)
            if result:
                return result
        return None
        
    def update(self, dt: float) -> None:
        """Update all widgets."""
        for widget in self.root_widgets:
            widget.update(dt)
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for all widgets."""
        # Process widgets in reverse order (front to back)
        for widget in reversed(self.root_widgets):
            if widget.handle_event(event):
                return True
        return False
        
    def render(self, screen: pygame.Surface) -> None:
        """Render all widgets."""
        for widget in self.root_widgets:
            widget.render(screen)
