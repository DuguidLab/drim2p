import click

from drim2p.extract import signal


@click.group()
def extract() -> None:
    """Extracts signals."""


extract.add_command(signal.extract_signal_command, "signal")
