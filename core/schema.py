"""
HomiCraft Core Schema
Defines the data models and serialization for projects and UI scenes.
"""

from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional


@dataclass
class ProjectConfig:
    name: str = "HomiCraft App"
    version: str = "0.1.0"
    entry_scene: str = "main.ui.json"
    window_title: str = "My HomiCraft App"
    window_width: int = 600
    window_height: int = 400
    window_resizable: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ProjectConfig:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class WidgetNode:
    id: str
    type: str  # Button, Label, LineEdit, CheckBox, Slider, ProgressBar, etc.
    x: int = 0
    y: int = 0
    width: int = 120
    height: int = 36
    script: Optional[str] = None  # Optional attached script path (e.g. "button_1.py")
    properties: Dict[str, Any] = field(default_factory=dict)
    signals: Dict[str, str] = field(default_factory=dict)  # signal_name -> callback_name
    children: List[WidgetNode] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "type": self.type,
            "geometry": [self.x, self.y, self.width, self.height],
            "script": self.script,
            "properties": self.properties,
            "signals": self.signals,
            "children": [c.to_dict() for c in self.children]
        }
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> WidgetNode:
        geom = data.get("geometry", [0, 0, 120, 36])
        children = [cls.from_dict(c) for c in data.get("children", [])]
        return cls(
            id=data.get("id", "widget"),
            type=data.get("type", "Widget"),
            x=geom[0] if len(geom) > 0 else 0,
            y=geom[1] if len(geom) > 1 else 0,
            width=geom[2] if len(geom) > 2 else 120,
            height=geom[3] if len(geom) > 3 else 36,
            script=data.get("script", None),
            properties=data.get("properties", {}),
            signals=data.get("signals", {}),
            children=children
        )


def save_project_config(path: str, config: ProjectConfig) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config.to_dict(), f, indent=2)


def load_project_config(path: str) -> ProjectConfig:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return ProjectConfig.from_dict(data)


def save_scene(path: str, root_node: WidgetNode) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(root_node.to_dict(), f, indent=2)


def load_scene(path: str) -> WidgetNode:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return WidgetNode.from_dict(data)
