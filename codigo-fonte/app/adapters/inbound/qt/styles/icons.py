

from PySide6.QtGui import QIcon

from app.adapters.outbound.resources.resource_resolver import get_resource_path


def scientific_icon(name: str) -> QIcon:
    
    return QIcon(str(get_resource_path(f"assets/icons/tabler/{name}.svg")))
