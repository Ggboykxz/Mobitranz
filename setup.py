# ============================================================
# Setup script pour MobiTranz Admin
# ============================================================

from cx_Freeze import setup, Executable
import os

build_exe_options = {
    "packages": [],
    "excludes": ["tkinter", "test", "pytest", "unittest", "matplotlib.tests"],
    "include_files": [],
    "optimize": 2,
}

executables = [
    Executable(
        "desktop_admin/main.py",
        target_name="MobiTranzAdmin.exe",
    )
]

setup(
    name="MobiTranzAdmin",
    version="1.0.0",
    description="MobiTranz - Administration Desktop Application",
    options={"build_exe": build_exe_options},
    executables=executables,
)