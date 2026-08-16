from __future__ import annotations

import os
from pathlib import Path
from typing import BinaryIO


def opened_path(handle: BinaryIO) -> Path:
    """Return the stable filesystem path for an already-open file handle.

    The dashboard fails closed when the host cannot provide a handle-bound path.
    This prevents a pathname validated earlier from being redirected through an
    ancestor symlink/junction before the file is opened.
    """

    if os.name == "nt":
        import ctypes
        import msvcrt
        from ctypes import wintypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        get_final_path = kernel32.GetFinalPathNameByHandleW
        get_final_path.argtypes = [wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD]
        get_final_path.restype = wintypes.DWORD
        native_handle = wintypes.HANDLE(msvcrt.get_osfhandle(handle.fileno()))
        size = get_final_path(native_handle, None, 0, 0)
        if not size:
            raise OSError(ctypes.get_last_error(), "GetFinalPathNameByHandleW failed")
        buffer = ctypes.create_unicode_buffer(size + 1)
        written = get_final_path(native_handle, buffer, len(buffer), 0)
        if not written or written >= len(buffer):
            raise OSError(ctypes.get_last_error(), "GetFinalPathNameByHandleW failed")
        rendered = buffer.value
        if rendered.startswith("\\\\?\\UNC\\"):
            rendered = "\\\\" + rendered[8:]
        elif rendered.startswith("\\\\?\\"):
            rendered = rendered[4:]
        return Path(rendered)

    proc_link = Path(f"/proc/self/fd/{handle.fileno()}")
    if proc_link.exists():
        target = os.readlink(proc_link)
        if target.endswith(" (deleted)"):
            raise OSError("opened file was deleted during validation")
        return Path(target)

    raise OSError("host cannot resolve a stable path for the opened file handle")
