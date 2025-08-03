# ik_project

This project aims to provide forward and inverse kinematics solutions for robot models described in URDF. The results can be visualized using [Rerun](https://www.rerun.io/).

## Setup

Install the project in an isolated environment:

```bash
python -m pip install -e .
```

This will pull in the dependencies specified in `pyproject.toml`.

If you prefer not to install the package, you can run the module directly by
adding the `src` directory to `PYTHONPATH`:

```bash
PYTHONPATH=src python -m ik_project.franka_visualizer
```

The first time you run the visualizer it will download the official
`franka_description` repository.  If internet access is not available, you can
download the repository manually and pass the path with the `--repo_dir`
option.

## Visualizing the Franka Emika arm

To visualize the robot with Rerun after installing the dependencies, simply run

```bash
python -m ik_project.franka_visualizer
```

The command above downloads the URDF and mesh files (if not already cached),
saves a recording, and attempts to open a browser window pointing at the Rerun
web viewer. If the viewer does not open automatically you can start it
manually:

```bash
rerun --web-viewer /tmp/franka_robot.rrd
```

Use the `--repo_dir` option to point to an existing `franka_description`
checkout if you do not have internet access during execution.
