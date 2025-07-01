"""
Example custom UI elements for the Scene Editor

This file demonstrates how to create custom UI widgets that can be imported
into the Scene Editor for use in your game's user interface.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pygame
from engine.ui.widget import Widget, WidgetState
from typing import Optional, Callable, List


class ProgressBar(Widget):
    """A progress bar widget for showing completion status."""
    
    def __init__(self, rect: pygame.Rect, name: str = "ProgressBar"):
        super().__init__(rect, name)
        self.value = 0.5  # 0.0 to 1.0
        self.background_color = pygame.Color(50, 50, 50)
        self.fill_color = pygame.Color(0, 200, 0)
        self.border_color = pygame.Color(255, 255, 255)
        self.border_width = 2
        self.show_text = True
        self.text_color = pygame.Color(255, 255, 255)
        self.font_size = 16
        self._font = None
        
    def setValue(self, value: float):
        """Set the progress value (0.0 to 1.0)."""
        self.value = max(0.0, min(1.0, value))
        
    def getValue(self) -> float:
        """Get the current progress value."""
        return self.value
        
    def render(self, surface: pygame.Surface):
        """Render the progress bar."""
        if not self.visible:
            return
            
        # Draw background
        pygame.draw.rect(surface, self.background_color, self.rect)
        
        # Draw fill
        fill_width = int(self.rect.width * self.value)
        if fill_width > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
            pygame.draw.rect(surface, self.fill_color, fill_rect)
            
        # Draw border
        if self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, self.rect, self.border_width)
            
        # Draw text
        if self.show_text:
            if not self._font:
                self._font = pygame.font.Font(None, self.font_size)
            
            percentage = int(self.value * 100)
            text = f"{percentage}%"
            text_surface = self._font.render(text, True, self.text_color)
            
            # Center text
            text_rect = text_surface.get_rect()
            text_rect.center = self.rect.center
            surface.blit(text_surface, text_rect)


class Tooltip(Widget):
    """A tooltip widget that appears on hover."""
    
    def __init__(self, rect: pygame.Rect, text: str = "", name: str = "Tooltip"):
        super().__init__(rect, name)
        self.text = text
        self.background_color = pygame.Color(40, 40, 40, 230)  # Semi-transparent
        self.text_color = pygame.Color(255, 255, 255)
        self.border_color = pygame.Color(100, 100, 100)
        self.border_width = 1
        self.padding = 5
        self.font_size = 14
        self._font = None
        self.auto_size = True
        
    def setText(self, text: str):
        """Set the tooltip text."""
        self.text = text
        if self.auto_size:
            self._updateSize()
            
    def _updateSize(self):
        """Update the tooltip size based on text."""
        if not self._font:
            self._font = pygame.font.Font(None, self.font_size)
            
        if self.text:
            text_surface = self._font.render(self.text, True, self.text_color)
            self.rect.width = text_surface.get_width() + self.padding * 2
            self.rect.height = text_surface.get_height() + self.padding * 2
            
    def render(self, surface: pygame.Surface):
        """Render the tooltip."""
        if not self.visible or not self.text:
            return
            
        if not self._font:
            self._font = pygame.font.Font(None, self.font_size)
            
        # Create semi-transparent surface
        tooltip_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # Draw background
        pygame.draw.rect(tooltip_surface, self.background_color, (0, 0, self.rect.width, self.rect.height))
        
        # Draw border
        if self.border_width > 0:
            pygame.draw.rect(tooltip_surface, self.border_color, 
                           (0, 0, self.rect.width, self.rect.height), self.border_width)
            
        # Draw text
        text_surface = self._font.render(self.text, True, self.text_color)
        text_x = self.padding
        text_y = self.padding
        tooltip_surface.blit(text_surface, (text_x, text_y))
        
        # Blit to main surface
        surface.blit(tooltip_surface, self.rect)


class ContextMenu(Widget):
    """A context menu widget with clickable options."""
    
    def __init__(self, rect: pygame.Rect, name: str = "ContextMenu"):
        super().__init__(rect, name)
        self.options = []  # List of {"text": str, "callback": callable, "enabled": bool}
        self.background_color = pygame.Color(60, 60, 60)
        self.text_color = pygame.Color(255, 255, 255)
        self.disabled_color = pygame.Color(128, 128, 128)
        self.hover_color = pygame.Color(80, 80, 80)
        self.border_color = pygame.Color(100, 100, 100)
        self.border_width = 1
        self.item_height = 25
        self.padding = 5
        self.font_size = 14
        self._font = None
        self.hovered_index = -1
        
    def addOption(self, text: str, callback: Callable = None, enabled: bool = True):
        """Add an option to the context menu."""
        self.options.append({
            "text": text,
            "callback": callback,
            "enabled": enabled
        })
        self._updateSize()
        
    def addSeparator(self):
        """Add a separator line."""
        self.options.append({
            "text": "---",
            "callback": None,
            "enabled": False
        })
        self._updateSize()
        
    def clear(self):
        """Clear all options."""
        self.options.clear()
        self._updateSize()
        
    def _updateSize(self):
        """Update menu size based on options."""
        if not self._font:
            self._font = pygame.font.Font(None, self.font_size)
            
        max_width = 100
        for option in self.options:
            if option["text"] != "---":
                text_surface = self._font.render(option["text"], True, self.text_color)
                max_width = max(max_width, text_surface.get_width() + self.padding * 2)
                
        self.rect.width = max_width
        self.rect.height = len(self.options) * self.item_height + self.border_width * 2
        
    def handleEvent(self, event):
        """Handle mouse events."""
        if not self.visible or not self.enabled:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            if self.rect.collidepoint(mouse_pos):
                # Calculate which item is hovered
                relative_y = mouse_pos[1] - self.rect.y - self.border_width
                self.hovered_index = relative_y // self.item_height
                if self.hovered_index >= len(self.options):
                    self.hovered_index = -1
                return True
            else:
                self.hovered_index = -1
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = event.pos
                if self.rect.collidepoint(mouse_pos):
                    relative_y = mouse_pos[1] - self.rect.y - self.border_width
                    clicked_index = relative_y // self.item_height
                    
                    if 0 <= clicked_index < len(self.options):
                        option = self.options[clicked_index]
                        if option["enabled"] and option["callback"] and option["text"] != "---":
                            option["callback"]()
                            self.visible = False  # Hide menu after selection
                            return True
                else:
                    self.visible = False  # Hide if clicked outside
                    
        return False
        
    def render(self, surface: pygame.Surface):
        """Render the context menu."""
        if not self.visible:
            return
            
        if not self._font:
            self._font = pygame.font.Font(None, self.font_size)
            
        # Draw background
        pygame.draw.rect(surface, self.background_color, self.rect)
        
        # Draw border
        if self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, self.rect, self.border_width)
            
        # Draw options
        y_offset = self.border_width
        for i, option in enumerate(self.options):
            item_rect = pygame.Rect(
                self.rect.x + self.border_width,
                self.rect.y + y_offset,
                self.rect.width - self.border_width * 2,
                self.item_height
            )
            
            # Draw hover background
            if i == self.hovered_index and option["enabled"]:
                pygame.draw.rect(surface, self.hover_color, item_rect)
                
            # Draw text or separator
            if option["text"] == "---":
                # Draw separator line
                line_y = item_rect.centery
                pygame.draw.line(surface, self.border_color, 
                               (item_rect.left + 5, line_y), 
                               (item_rect.right - 5, line_y))
            else:
                # Draw text
                color = self.text_color if option["enabled"] else self.disabled_color
                text_surface = self._font.render(option["text"], True, color)
                text_x = item_rect.x + self.padding
                text_y = item_rect.y + (self.item_height - text_surface.get_height()) // 2
                surface.blit(text_surface, (text_x, text_y))
                
            y_offset += self.item_height


class ImageButton(Widget):
    """A button widget that displays an image."""
    
    def __init__(self, rect: pygame.Rect, image_path: str = "", name: str = "ImageButton"):
        super().__init__(rect, name)
        self.image_path = image_path
        self.image = None
        self.clicked_callback = None
        self.background_color = pygame.Color(70, 70, 70)
        self.hover_color = pygame.Color(90, 90, 90)
        self.pressed_color = pygame.Color(50, 50, 50)
        self.border_color = pygame.Color(100, 100, 100)
        self.border_width = 2
        self.scale_image = True
        self._load_image()
        
    def _load_image(self):
        """Load the button image."""
        if self.image_path and os.path.exists(self.image_path):
            try:
                self.image = pygame.image.load(self.image_path)
                if self.scale_image:
                    # Scale image to fit button
                    padding = 4
                    target_size = (self.rect.width - padding * 2, self.rect.height - padding * 2)
                    self.image = pygame.transform.scale(self.image, target_size)
            except Exception as e:
                print(f"Failed to load button image {self.image_path}: {e}")
                self.image = None
                
    def setImage(self, image_path: str):
        """Set a new image for the button."""
        self.image_path = image_path
        self._load_image()
        
    def setClickCallback(self, callback: Callable):
        """Set the callback function for when the button is clicked."""
        self.clicked_callback = callback
        
    def handleEvent(self, event):
        """Handle mouse events."""
        if not self.visible or not self.enabled:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.rect.collidepoint(event.pos):
                    self.state = WidgetState.PRESSED
                    return True
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.state == WidgetState.PRESSED:
                    if self.rect.collidepoint(event.pos):
                        # Button was clicked
                        if self.clicked_callback:
                            self.clicked_callback()
                    self.state = WidgetState.NORMAL
                    return True
                    
        elif event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                if self.state != WidgetState.PRESSED:
                    self.state = WidgetState.HOVER
            else:
                if self.state != WidgetState.PRESSED:
                    self.state = WidgetState.NORMAL
                    
        return False
        
    def render(self, surface: pygame.Surface):
        """Render the image button."""
        if not self.visible:
            return
            
        # Choose background color based on state
        bg_color = self.background_color
        if self.state == WidgetState.HOVER:
            bg_color = self.hover_color
        elif self.state == WidgetState.PRESSED:
            bg_color = self.pressed_color
        elif self.state == WidgetState.DISABLED:
            bg_color = pygame.Color(40, 40, 40)
            
        # Draw background
        pygame.draw.rect(surface, bg_color, self.rect)
        
        # Draw image
        if self.image:
            # Center the image
            image_rect = self.image.get_rect()
            image_rect.center = self.rect.center
            surface.blit(self.image, image_rect)
            
        # Draw border
        if self.border_width > 0:
            border_color = self.border_color
            if self.state == WidgetState.DISABLED:
                border_color = pygame.Color(60, 60, 60)
            pygame.draw.rect(surface, border_color, self.rect, self.border_width)


class LoadingSpinner(Widget):
    """A spinning loading indicator widget."""
    
    def __init__(self, rect: pygame.Rect, name: str = "LoadingSpinner"):
        super().__init__(rect, name)
        self.rotation = 0.0
        self.rotation_speed = 180.0  # degrees per second
        self.color = pygame.Color(100, 150, 255)
        self.background_color = pygame.Color(30, 30, 30)
        self.thickness = 4
        self.spinning = True
        
    def setSpinning(self, spinning: bool):
        """Set whether the spinner is spinning."""
        self.spinning = spinning
        
    def update(self, delta_time):
        """Update the spinner rotation."""
        if self.spinning:
            self.rotation += self.rotation_speed * delta_time
            self.rotation %= 360
            
    def render(self, surface: pygame.Surface):
        """Render the loading spinner."""
        if not self.visible:
            return
            
        center = self.rect.center
        radius = min(self.rect.width, self.rect.height) // 2 - self.thickness
        
        # Draw background circle
        pygame.draw.circle(surface, self.background_color, center, radius, self.thickness)
        
        # Draw spinning arc
        if self.spinning:
            import math
            arc_length = 90  # degrees
            start_angle = math.radians(self.rotation)
            end_angle = math.radians(self.rotation + arc_length)
            
            # Draw the arc (this is a simplified version - you might want to use pygame.gfxdraw for better arcs)
            arc_points = []
            steps = 20
            for i in range(steps + 1):
                angle = start_angle + (end_angle - start_angle) * i / steps
                x = center[0] + math.cos(angle) * radius
                y = center[1] + math.sin(angle) * radius
                arc_points.append((x, y))
                
            if len(arc_points) > 1:
                pygame.draw.lines(surface, self.color, False, arc_points, self.thickness)
