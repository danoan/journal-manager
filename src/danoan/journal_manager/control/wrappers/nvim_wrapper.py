from pathlib import Path
import subprocess


def edit_file(filepath: str, nvim_path: str = "nvim", working_dir: str = None):
    if working_dir is None:
        working_dir = Path(filepath).parent.name

    text_editor_args = [nvim_path, "--cmd", f"cd {working_dir}", filepath]
    subprocess.run(text_editor_args)
