from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional

IS_COMPONENTS_V2 = 1 << 15


class Component:
    type: int
    def to_dict(self):
        raise NotImplementedError


def _d(obj):
    return obj.to_dict() if hasattr(obj, "to_dict") else obj


@dataclass
class ActionRow(Component):
    components: list[Any]
    id: Optional[int] = None
    type: int = 1
    def to_dict(self):
        d = {"type": self.type, "components": [_d(x) for x in self.components]}
        if self.id is not None: d["id"] = self.id
        return d


@dataclass
class Button(Component):
    label: Optional[str] = None
    custom_id: Optional[str] = None
    style: int = 1
    url: Optional[str] = None
    sku_id: Optional[str] = None
    emoji: Optional[dict] = None
    disabled: bool = False
    id: Optional[int] = None
    type: int = 2
    def to_dict(self):
        d = {"type": self.type, "style": self.style}
        for k in ("label", "custom_id", "url", "sku_id", "emoji", "id"):
            v = getattr(self, k)
            if v is not None: d[k] = v
        if self.disabled: d["disabled"] = True
        return d


@dataclass
class StringSelect(Component):
    custom_id: str
    options: list[dict]
    placeholder: Optional[str] = None
    min_values: int = 1
    max_values: int = 1
    required: Optional[bool] = None
    disabled: bool = False
    id: Optional[int] = None
    type: int = 3
    def to_dict(self):
        d = {"type": self.type, "custom_id": self.custom_id, "options": self.options,
             "min_values": self.min_values, "max_values": self.max_values}
        if self.placeholder is not None: d["placeholder"] = self.placeholder
        if self.required is not None: d["required"] = self.required
        if self.disabled: d["disabled"] = True
        if self.id is not None: d["id"] = self.id
        return d


@dataclass
class TextInput(Component):
    custom_id: str
    style: int = 1
    label: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    required: bool = True
    value: Optional[str] = None
    placeholder: Optional[str] = None
    id: Optional[int] = None
    type: int = 4
    def to_dict(self):
        d = {"type": self.type, "custom_id": self.custom_id, "style": self.style, "required": self.required}
        for k in ("label", "min_length", "max_length", "value", "placeholder", "id"):
            v = getattr(self, k)
            if v is not None: d[k] = v
        return d


@dataclass
class AutoSelect(Component):
    custom_id: str
    type: int
    placeholder: Optional[str] = None
    min_values: int = 1
    max_values: int = 1
    required: Optional[bool] = None
    disabled: bool = False
    channel_types: Optional[list[int]] = None
    default_values: Optional[list[dict]] = None
    id: Optional[int] = None
    def to_dict(self):
        d = {"type": self.type, "custom_id": self.custom_id,
             "min_values": self.min_values, "max_values": self.max_values}
        for k in ("placeholder", "required", "channel_types", "default_values", "id"):
            v = getattr(self, k)
            if v is not None: d[k] = v
        if self.disabled: d["disabled"] = True
        return d


def UserSelect(custom_id, **kwargs): return AutoSelect(custom_id=custom_id, type=5, **kwargs)
def RoleSelect(custom_id, **kwargs): return AutoSelect(custom_id=custom_id, type=6, **kwargs)
def MentionableSelect(custom_id, **kwargs): return AutoSelect(custom_id=custom_id, type=7, **kwargs)
def ChannelSelect(custom_id, **kwargs): return AutoSelect(custom_id=custom_id, type=8, **kwargs)


@dataclass
class Section(Component):
    components: list[Any]
    accessory: Any
    id: Optional[int] = None
    type: int = 9
    def to_dict(self):
        d = {"type": self.type, "components": [_d(x) for x in self.components], "accessory": _d(self.accessory)}
        if self.id is not None: d["id"] = self.id
        return d


@dataclass
class TextDisplay(Component):
    content: str
    id: Optional[int] = None
    type: int = 10
    def to_dict(self):
        d = {"type": self.type, "content": self.content}
        if self.id is not None: d["id"] = self.id
        return d


@dataclass
class Thumbnail(Component):
    media: dict
    description: Optional[str] = None
    spoiler: bool = False
    id: Optional[int] = None
    type: int = 11
    def to_dict(self):
        d = {"type": self.type, "media": self.media}
        if self.description is not None: d["description"] = self.description
        if self.spoiler: d["spoiler"] = True
        if self.id is not None: d["id"] = self.id
        return d


@dataclass
class MediaGallery(Component):
    items: list[dict]
    id: Optional[int] = None
    type: int = 12
    def to_dict(self):
        d = {"type": self.type, "items": self.items}
        if self.id is not None: d["id"] = self.id
        return d


@dataclass
class FileComponent(Component):
    file: dict
    spoiler: bool = False
    id: Optional[int] = None
    type: int = 13
    def to_dict(self):
        d = {"type": self.type, "file": self.file}
        if self.spoiler: d["spoiler"] = True
        if self.id is not None: d["id"] = self.id
        return d


@dataclass
class Separator(Component):
    divider: bool = True
    spacing: int = 1
    id: Optional[int] = None
    type: int = 14
    def to_dict(self):
        d = {"type": self.type, "divider": self.divider, "spacing": self.spacing}
        if self.id is not None: d["id"] = self.id
        return d


@dataclass
class Container(Component):
    components: list[Any]
    accent_color: Optional[int] = None
    spoiler: bool = False
    id: Optional[int] = None
    type: int = 17
    def to_dict(self):
        d = {"type": self.type, "components": [_d(x) for x in self.components]}
        if self.accent_color is not None: d["accent_color"] = self.accent_color
        if self.spoiler: d["spoiler"] = True
        if self.id is not None: d["id"] = self.id
        return d


@dataclass
class Label(Component):
    label: str
    component: Any
    description: Optional[str] = None
    id: Optional[int] = None
    type: int = 18
    def to_dict(self):
        d = {"type": self.type, "label": self.label, "component": _d(self.component)}
        if self.description is not None: d["description"] = self.description
        if self.id is not None: d["id"] = self.id
        return d


@dataclass
class FileUpload(Component):
    custom_id: str
    min_values: int = 1
    max_values: int = 1
    required: bool = True
    id: Optional[int] = None
    type: int = 19
    def to_dict(self):
        d = {"type": self.type, "custom_id": self.custom_id, "min_values": self.min_values,
             "max_values": self.max_values, "required": self.required}
        if self.id is not None: d["id"] = self.id
        return d


@dataclass
class RadioGroup(Component):
    custom_id: str
    options: list[dict]
    required: bool = True
    id: Optional[int] = None
    type: int = 21
    def to_dict(self):
        d = {"type": self.type, "custom_id": self.custom_id, "options": self.options, "required": self.required}
        if self.id is not None: d["id"] = self.id
        return d


@dataclass
class CheckboxGroup(Component):
    custom_id: str
    options: list[dict]
    min_values: int = 1
    max_values: Optional[int] = None
    required: bool = True
    id: Optional[int] = None
    type: int = 22
    def to_dict(self):
        d = {"type": self.type, "custom_id": self.custom_id, "options": self.options,
             "min_values": self.min_values, "required": self.required}
        if self.max_values is not None: d["max_values"] = self.max_values
        if self.id is not None: d["id"] = self.id
        return d


@dataclass
class Checkbox(Component):
    custom_id: str
    label: str
    description: Optional[str] = None
    required: bool = True
    id: Optional[int] = None
    type: int = 23
    def to_dict(self):
        d = {"type": self.type, "custom_id": self.custom_id, "label": self.label, "required": self.required}
        if self.description is not None: d["description"] = self.description
        if self.id is not None: d["id"] = self.id
        return d
