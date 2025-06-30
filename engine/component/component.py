from abc import ABC, abstractmethod

from ..actor.actor import Actor

class Component(ABC):
    """
    Base class for all components in the game engine.
    Components are used to add functionality to actors.
    """

    def __init__(self):
        self.enabled = True  # Indicates if the component is active
        self.actor: Actor = None  # Reference to the actor this component is attached to

    def setActor(self, actor: Actor):
        """
        Set the actor this component is attached to.
        This method is called by the actor when the component is added.
        """
        self.actor = actor

    def update(self, delta_time):
        """
        Update the component with the given delta time.
        Override this method in derived classes to implement specific behavior.
        """
        pass

    def render(self, surface):
        """
        Render the component on the given surface.
        Override this method in derived classes to implement specific rendering behavior.
        """
        pass
