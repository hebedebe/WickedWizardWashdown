from .transform import Transform

class Actor:
    def __init__(self, name: str = "Actor"):
        self.transform = Transform()
        self.name = name
        self.tags = set()  # Using a set for unique tags
        self.components = []

    def setName(self, name: str) -> None:
        """Set the name of the actor."""
        self.name = name

    def addComponent(self, component) -> None:
        """Add a component to the actor."""
        assert component not in self.components, "Component already exists in actor"
        component.setActor(self)
        self.components.append(component)

    def removeComponent(self, component) -> None:
        """Remove a component from the actor."""
        if component in self.components:
            self.components.remove(component)
            component.setActor(None)

    def getComponent(self, component_type):
        """Get a component of a specific type from the actor."""
        for comp in self.components:
            if isinstance(comp, component_type):
                return comp
        return None

    def addTag(self, tag: str) -> None:
        """Add a tag to the actor."""
        self.tags.add(tag)

    def removeTag(self, tag: str) -> None:
        """Remove a tag from the actor."""
        self.tags.discard(tag)

    def handleUpdate(self, dt: float) -> None:
        """Handle the update logic for the actor."""
        # Update all components
        for component in self.components:
            if component.enabled:
                component.update(dt)
        # Update the actor's own state
        self.update(dt)

    def update(self, dt: float) -> None:
        """Update the actor's state."""
        # Update logic for the actor
        pass

    def handleRender(self, surface) -> None:
        """Handle the rendering of the actor."""
        # Render all components
        for component in self.components:
            if component.enabled:
                component.render(surface)
        # Render the actor itself
        self.render(surface)

    def render(self, surface) -> None:
        """Render the actor on the given surface."""
        # Render logic for the actor
        pass