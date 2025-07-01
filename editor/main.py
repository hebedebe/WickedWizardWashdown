# Standalone Scene Editor for WickedWizardWashdown
import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyQt5 import QtWidgets, QtCore
from engine.scene.scene import Scene
from engine.actor.actor import Actor
from engine.component import *
from engine.component.builtin import *
from engine.ui.uiManager import UIManager
from engine.logger import Logger

class DummyGame:
    width = 1200
    height = 700
    _instance = None

# Patch Game._instance if not set (for editor-only usage)
try:
    from engine import Game
    if Game._instance is None:
        Game._instance = DummyGame()
except ImportError:
    pass

# --- Data Model Wrappers for Editor ---
class SceneEditorModel:
    def __init__(self):
        self.scene = Scene()

    def to_dict(self):
        return self.scene.serialize()

    def from_dict(self, data):
        self.scene.deserialize(data)

    def save_to_file(self, path):
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    def load_from_file(self, path):
        with open(path, 'r') as f:
            data = json.load(f)
        self.from_dict(data)

# --- PyQt5 GUI ---
class SceneEditorWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Scene Editor - WickedWizardWashdown')
        self.resize(1200, 700)
        self.model = SceneEditorModel()
        self._setup_ui()
        self._refresh_actor_tree()

    def _setup_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QHBoxLayout(central)

        # Actor Tree
        self.actor_tree = QtWidgets.QTreeWidget()
        self.actor_tree.setHeaderLabel('Actors')
        self.actor_tree.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.actor_tree.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.actor_tree.dropEvent = self._on_actor_tree_drop
        self.actor_tree.itemSelectionChanged.connect(self._on_actor_selected)
        layout.addWidget(self.actor_tree, 2)

        # Components List
        comp_layout = QtWidgets.QVBoxLayout()
        self.comp_list = QtWidgets.QListWidget()
        self.comp_list.currentRowChanged.connect(self._on_component_selected)
        comp_layout.addWidget(QtWidgets.QLabel('Components'))
        comp_layout.addWidget(self.comp_list)
        self.add_comp_btn = QtWidgets.QPushButton('Add Component')
        self.add_comp_btn.clicked.connect(self._add_component)
        self.remove_comp_btn = QtWidgets.QPushButton('Remove Component')
        self.remove_comp_btn.clicked.connect(self._remove_component)
        comp_layout.addWidget(self.add_comp_btn)
        comp_layout.addWidget(self.remove_comp_btn)
        layout.addLayout(comp_layout, 1)

        # Inspector
        self.inspector = QtWidgets.QFormLayout()
        self.inspector_widget = QtWidgets.QWidget()
        self.inspector_widget.setLayout(self.inspector)
        layout.addWidget(self.inspector_widget, 2)

        # Menu
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        file_menu.addAction('New Scene', self._new_scene)
        file_menu.addAction('Open Scene...', self._open_scene)
        file_menu.addAction('Save Scene...', self._save_scene)
        file_menu.addSeparator()
        file_menu.addAction('Exit', self.close)

        # Actor controls
        actor_toolbar = QtWidgets.QToolBar('Actor')
        self.addToolBar(actor_toolbar)
        add_actor = QtWidgets.QAction('Add Actor', self)
        add_actor.triggered.connect(self._add_actor)
        actor_toolbar.addAction(add_actor)
        remove_actor = QtWidgets.QAction('Remove Actor', self)
        remove_actor.triggered.connect(self._remove_actor)
        actor_toolbar.addAction(remove_actor)
        parent_actor = QtWidgets.QAction('Set Parent', self)
        parent_actor.triggered.connect(self._set_parent)
        actor_toolbar.addAction(parent_actor)
        unparent_actor = QtWidgets.QAction('Unparent', self)
        unparent_actor.triggered.connect(self._unparent_actor)
        actor_toolbar.addAction(unparent_actor)

    # --- Scene/Actor/Component Operations ---
    def _refresh_actor_tree(self):
        self.actor_tree.clear()
        def add_actor_item(actor, parent_item=None):
            item = QtWidgets.QTreeWidgetItem([actor.name])
            item.setData(0, QtCore.Qt.UserRole, actor)
            if parent_item:
                parent_item.addChild(item)
            else:
                self.actor_tree.addTopLevelItem(item)
            for child in actor.getChildren():
                add_actor_item(child, item)
        for actor in self.model.scene.actors:
            if not actor.getParent():
                add_actor_item(actor)
        self.actor_tree.expandAll()

    def _on_actor_selected(self):
        items = self.actor_tree.selectedItems()
        if not items:
            self.comp_list.clear()
            self._clear_inspector()
            return
        actor = items[0].data(0, QtCore.Qt.UserRole)
        self.comp_list.clear()
        for comp in actor.components:
            self.comp_list.addItem(type(comp).__name__)
        self._show_actor_inspector(actor)

    def _on_component_selected(self, idx):
        items = self.actor_tree.selectedItems()
        if not items or idx < 0:
            self._clear_inspector()
            return
        actor = items[0].data(0, QtCore.Qt.UserRole)
        comp = actor.components[idx]
        self._show_component_inspector(comp)

    def _show_actor_inspector(self, actor):
        self._clear_inspector()
        # Name
        name_edit = QtWidgets.QLineEdit(actor.name)
        name_edit.editingFinished.connect(lambda: self._set_actor_name(actor, name_edit.text()))
        self.inspector.addRow('Name', name_edit)
        # Transform
        pos_edit = QtWidgets.QLineEdit(str(actor.transform.position))
        pos_edit.editingFinished.connect(lambda: self._set_actor_pos(actor, pos_edit.text()))
        self.inspector.addRow('Position', pos_edit)
        rot_edit = QtWidgets.QLineEdit(str(actor.transform.rotation))
        rot_edit.editingFinished.connect(lambda: self._set_actor_rot(actor, rot_edit.text()))
        self.inspector.addRow('Rotation', rot_edit)
        scale_edit = QtWidgets.QLineEdit(str(actor.transform.scale))
        scale_edit.editingFinished.connect(lambda: self._set_actor_scale(actor, scale_edit.text()))
        self.inspector.addRow('Scale', scale_edit)
        # Tags
        tags_edit = QtWidgets.QLineEdit(','.join(actor.tags))
        tags_edit.editingFinished.connect(lambda: self._set_actor_tags(actor, tags_edit.text()))
        self.inspector.addRow('Tags', tags_edit)

    def _show_component_inspector(self, comp):
        self._clear_inspector()
        for key, value in comp.__dict__.items():
            if key == 'actor' or key.startswith('_'):
                continue
            edit = QtWidgets.QLineEdit(str(value))
            edit.editingFinished.connect(lambda k=key, e=edit: self._set_component_prop(comp, k, e.text()))
            self.inspector.addRow(key, edit)

    def _clear_inspector(self):
        while self.inspector.rowCount():
            self.inspector.removeRow(0)

    def _set_actor_name(self, actor, name):
        actor.setName(name)
        self._refresh_actor_tree()

    def _set_actor_pos(self, actor, text):
        try:
            pos = eval(text)
            actor.transform.setPosition(*pos)
        except:
            pass

    def _set_actor_rot(self, actor, text):
        try:
            rot = float(text)
            actor.transform.setRotation(rot)
        except:
            pass

    def _set_actor_scale(self, actor, text):
        try:
            scale = eval(text)
            actor.transform.setScale(*scale)
        except:
            pass

    def _set_actor_tags(self, actor, text):
        actor.tags = set([t.strip() for t in text.split(',') if t.strip()])

    def _set_component_prop(self, comp, key, value):
        try:
            # Try to eval for numbers/tuples, else string
            val = eval(value)
        except:
            val = value
        setattr(comp, key, val)

    def _add_actor(self):
        name, ok = QtWidgets.QInputDialog.getText(self, 'Add Actor', 'Actor name:')
        if ok and name:
            actor = Actor(name)
            self.model.scene.addActor(actor)
            self._refresh_actor_tree()

    def _remove_actor(self):
        items = self.actor_tree.selectedItems()
        if not items:
            return
        actor = items[0].data(0, QtCore.Qt.UserRole)
        self.model.scene.removeActor(actor)
        self._refresh_actor_tree()

    def _set_parent(self):
        items = self.actor_tree.selectedItems()
        if len(items) != 2:
            QtWidgets.QMessageBox.warning(self, 'Set Parent', 'Select child then parent (Ctrl+Click)')
            return
        child = items[0].data(0, QtCore.Qt.UserRole)
        parent = items[1].data(0, QtCore.Qt.UserRole)
        child.setParent(parent)
        self._refresh_actor_tree()

    def _unparent_actor(self):
        items = self.actor_tree.selectedItems()
        if not items:
            return
        actor = items[0].data(0, QtCore.Qt.UserRole)
        actor.setParent(None)
        self._refresh_actor_tree()

    def _add_component(self):
        items = self.actor_tree.selectedItems()
        if not items:
            return
        actor = items[0].data(0, QtCore.Qt.UserRole)
        # List available component types
        comp_types = [cls for cls in Component.__subclasses__()]
        comp_types += [SpriteComponent, TextComponent, PhysicsComponent, AudioComponent, InputComponent, CircleRendererComponent, DampedSpringComponent]
        comp_types = list({c.__name__:c for c in comp_types}.values())
        items_str = [c.__name__ for c in comp_types]
        idx, ok = QtWidgets.QInputDialog.getItem(self, 'Add Component', 'Component type:', items_str, 0, False)
        if ok:
            comp_cls = comp_types[items_str.index(idx)]
            comp = comp_cls()
            actor.addComponent(comp)
            self._on_actor_selected()

    def _remove_component(self):
        items = self.actor_tree.selectedItems()
        idx = self.comp_list.currentRow()
        if not items or idx < 0:
            return
        actor = items[0].data(0, QtCore.Qt.UserRole)
        comp = actor.components[idx]
        actor.removeComponent(comp)
        self._on_actor_selected()

    def _new_scene(self):
        self.model = SceneEditorModel()
        self._refresh_actor_tree()

    def _open_scene(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Scene', '', 'Scene Files (*.json)')
        if path:
            self.model.load_from_file(path)
            self._refresh_actor_tree()

    def _save_scene(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Scene', '', 'Scene Files (*.json)')
        if path:
            self.model.save_to_file(path)

    def _on_actor_tree_drop(self, event):
        # Call the default drop event to move the item visually
        QtWidgets.QTreeWidget.dropEvent(self.actor_tree, event)
        # After drop, update parent/child relationships in the data model
        self._update_actor_hierarchy_from_tree()
        self._refresh_actor_tree()

    def _update_actor_hierarchy_from_tree(self):
        def update_parent(item, parent_actor):
            actor = item.data(0, QtCore.Qt.UserRole)
            if actor.getParent() != parent_actor:
                actor.setParent(parent_actor)
            for i in range(item.childCount()):
                update_parent(item.child(i), actor)
        for i in range(self.actor_tree.topLevelItemCount()):
            update_parent(self.actor_tree.topLevelItem(i), None)

# --- Main Entry ---
def main():
    app = QtWidgets.QApplication(sys.argv)
    win = SceneEditorWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
