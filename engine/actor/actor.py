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

    def serialize(self) -> dict:
        """Serialize the actor to a dictionary."""
        data = {
            "name": self.name,
            "tags": list(self.tags),
            "transform": self.transform.serialize(),
            "components": [component.serialize() for component in self.components]
        }
        return data

    def deserialize(self, data: dict) -> None:
        """Deserialize the actor from a dictionary."""
        from ..component.component import Component
        self.name = data.get("name", "Actor")
        self.tags = set(data.get("tags", []))
        self.transform.deserialize(data.get("transform", {}))
        self.components = [Component.deserialize(compData) for compData in data.get("components", [])]

    @staticmethod
    def createFromSerializedData(data: dict):
        """
        Create an actor instance from serialized data.
        """
        from ..component.component import Component
        actor = Actor()
        
        # Deserialize basic actor properties
        actor.name = data.get("name", "Actor")
        actor.tags = set(data.get("tags", []))
        actor.transform.deserialize(data.get("transform", {}))
        
        # Deserialize and add components
        for component_data in data.get("components", []):
            component = Component.createFromData(component_data)
            actor.addComponent(component)
        return actor

    def handleEvent(self, event) -> bool:
        """Handle an event and forward to components."""
        # Forward event to all components that can handle events
        for component in self.components:
            if component.enabled and hasattr(component, 'handle_event'):
                if component.handle_event(event):
                    return True  # Event was handled
        return False