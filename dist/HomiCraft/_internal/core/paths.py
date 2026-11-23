"""
HomiCraft Paths Module
Centralized path resolution for source and frozen PyInstaller environments.
"""

import os
import sys


def get_homi_root() -> str:
    """Returns the root directory of HomiCraft (source or bundled)."""
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        internal_dir = os.path.join(exe_dir, "_internal")
        if os.path.isdir(internal_dir):
            return internal_dir
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass and os.path.isdir(meipass):
            return meipass
        return exe_dir
    else:
        # Relative to core/
        return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def resolve_resource_path(*relative_parts: str) -> str:
    """Finds a resource path in source or frozen environments."""
    root = get_homi_root()
    cand = os.path.join(root, *relative_parts)
    if os.path.exists(cand):
        return cand

    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        cand_exe = os.path.join(exe_dir, *relative_parts)
        if os.path.exists(cand_exe):
            return cand_exe

    # Fallback to source relative
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", *relative_parts))
