"""CLI commands for EdgeCraft quantum hall edge simulation."""

import click
import importlib.util
import sys
from pathlib import Path
from typing import Optional

from edgecraft.runner import run_simulation


@click.group()
@click.version_option()
def cli():
    """EdgeCraft: Quantum Hall edge deformation simulator for analog universe experiments."""
    pass


@cli.command()
@click.argument('config_file', type=click.Path(exists=True, path_type=Path))
@click.option('--output-dir', '-o', type=click.Path(path_type=Path), 
              help='Output directory for results (default: current directory)')
def run(config_file: Path, output_dir: Optional[Path] = None):
    """Run EdgeCraft simulation with the specified configuration file.
    
    CONFIG_FILE: Python configuration file defining simulation parameters.
    """
    if output_dir is None:
        output_dir = Path.cwd()
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
    
    click.echo(f"Loading configuration from: {config_file}")
    
    # Load configuration by importing the Python file
    spec = importlib.util.spec_from_file_location("config_module", config_file)
    if spec is None or spec.loader is None:
        click.echo(f"Error: Could not load configuration file {config_file}", err=True)
        sys.exit(1)
    
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)
    
    # Get the config object
    if not hasattr(config_module, 'config'):
        click.echo("Error: Configuration file must define a 'config' variable", err=True)
        sys.exit(1)
    
    config = config_module.config
    
    click.echo("Setting up simulation...")
    click.echo(f"Running simulation with {config.frames} frames...")
    
    # Create progress tracking
    progress_data = {'current': 0}
    
    def update_progress(frame):
        progress_data['current'] = frame
    
    # Run simulation
    with click.progressbar(length=config.frames, label="Simulating") as bar:
        def progress_callback(frame):
            bar.update(frame - progress_data['current'])
            progress_data['current'] = frame
        
        edge_lengths_path, gate_potential_path = run_simulation(config, output_dir, progress_callback)
    
    click.echo(f"Simulation completed successfully!")
    click.echo(f"Results saved to:")
    click.echo(f"  Edge lengths: {edge_lengths_path}")
    click.echo(f"  Gate potential: {gate_potential_path}")


if __name__ == '__main__':
    cli()