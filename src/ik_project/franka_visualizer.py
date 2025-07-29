import io
import zipfile
from pathlib import Path
from typing import Optional

import requests
from urdfpy import URDF
import rerun as rr
import trimesh


def download_franka_description(dest: Path, branch: str = "main") -> Path:
    """Download the franka_description repository as a zip file.

    Parameters
    ----------
    dest:
        Destination directory where the repository will be extracted.
    branch:
        Git branch to download. Defaults to ``main``.

    Returns
    -------
    Path
        Path to the root of the extracted repository.
    """
    dest.mkdir(parents=True, exist_ok=True)
    zip_url = (
        f"https://github.com/frankarobotics/franka_description/archive/refs/heads/{branch}.zip"
    )
    try:
        resp = requests.get(zip_url)
        resp.raise_for_status()
    except Exception as exc:
        raise RuntimeError(f"Failed to download {zip_url}: {exc}") from exc
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        zf.extractall(dest)
    return dest / f"franka_description-{branch}"


def visualize_franka(repo_dir: Optional[Path] = None) -> None:
    """Visualize the Franka Emika arm URDF using Rerun.

    If ``repo_dir`` is ``None`` the franka_description repo is downloaded
    automatically using :func:`download_franka_description`.
    """

    if repo_dir is None:
        repo_dir = download_franka_description(Path.home()/".cache"/"franka_description")

    urdf_path = repo_dir / "robots" / "panda_arm_hand.urdf"
    robot = URDF.load(urdf_path)

    rr.init("franka_urdf")

    fk = robot.link_fk()

    for link, tf in fk.items():
        for i, visual in enumerate(link.visuals):
            geom = visual.geometry
            node_path = f"/{link.name}/{i}"
            rr.log(node_path, rr.Transform3D(matrix=tf @ visual.origin))
            if geom.mesh is not None:
                mesh_path = repo_dir / geom.filename
                mesh = trimesh.load_mesh(mesh_path)
                rr.log(
                    node_path,
                    rr.Mesh3D(
                        vertex_positions=mesh.vertices,
                        indices=mesh.faces.reshape(-1),
                    ),
                )
    rr.show()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Visualize the Franka Emika arm URDF using Rerun",
    )
    parser.add_argument(
        "--repo_dir",
        type=Path,
        help="Existing franka_description directory to use instead of downloading",
    )
    args = parser.parse_args()
    visualize_franka(args.repo_dir)
