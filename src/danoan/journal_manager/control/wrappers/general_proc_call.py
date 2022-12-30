import subprocess


def start(process_filepath: str, **kwargs):
    proc_args = [process_filepath, *kwargs]
    subprocess.run(proc_args)
