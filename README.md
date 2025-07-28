# ik_project

This project aims to provide forward and inverse kinematics solutions for robot models described in URDF. The results can be visualized using [Rerun](https://www.rerun.io/).

## Setup

Install the project in an isolated environment:

```bash
python -m pip install -e .
```

This will pull in the dependencies specified in `pyproject.toml`.

## Visualizing the Franka Emika arm

To download the official `franka_description` package and visualize the robot in Rerun:

```bash
python -c "from ik_project.franka_visualizer import visualize_franka; visualize_franka()"
```

This will download the URDF and mesh files (if not already cached) and open a Rerun viewer showing the Panda robot.
