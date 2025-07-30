import io
import zipfile
from pathlib import Path
from typing import Optional
import tempfile
import subprocess

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


def create_simple_franka_urdf(repo_dir: Path, robot_model: str = "fr3") -> Path:
    """Create a simple URDF for Franka robot using available meshes.
    
    Available models: fr3, fr3v2, fp3, fer
    """
    # Verify robot model exists
    mesh_dir = repo_dir / "meshes" / "robot_arms" / robot_model
    if not mesh_dir.exists():
        raise FileNotFoundError(f"Robot model {robot_model} not found. Available models: fr3, fr3v2, fp3, fer")
    
    # Simple URDF template for Franka robot
    urdf_content = f'''<?xml version="1.0"?>
<robot name="franka_{robot_model}">
  
  <link name="base_link">
    <visual>
      <geometry>
        <mesh filename="{mesh_dir}/visual/link0.dae"/>
      </geometry>
    </visual>
  </link>
  
  <link name="link1">
    <visual>
      <geometry>
        <mesh filename="{mesh_dir}/visual/link1.dae"/>
      </geometry>
    </visual>
  </link>
  
  <link name="link2">
    <visual>
      <geometry>
        <mesh filename="{mesh_dir}/visual/link2.dae"/>
      </geometry>
    </visual>
  </link>
  
  <link name="link3">
    <visual>
      <geometry>
        <mesh filename="{mesh_dir}/visual/link3.dae"/>
      </geometry>
    </visual>
  </link>
  
  <link name="link4">
    <visual>
      <geometry>
        <mesh filename="{mesh_dir}/visual/link4.dae"/>
      </geometry>
    </visual>
  </link>
  
  <link name="link5">
    <visual>
      <geometry>
        <mesh filename="{mesh_dir}/visual/link5.dae"/>
      </geometry>
    </visual>
  </link>
  
  <link name="link6">
    <visual>
      <geometry>
        <mesh filename="{mesh_dir}/visual/link6.dae"/>
      </geometry>
    </visual>
  </link>
  
  <link name="link7">
    <visual>
      <geometry>
        <mesh filename="{mesh_dir}/visual/link7.dae"/>
      </geometry>
    </visual>
  </link>
  
  <joint name="joint1" type="revolute">
    <parent link="base_link"/>
    <child link="link1"/>
    <origin xyz="0 0 0.333" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-2.8973" upper="2.8973" effort="87" velocity="2.1750"/>
  </joint>
  
  <joint name="joint2" type="revolute">
    <parent link="link1"/>
    <child link="link2"/>
    <origin xyz="0 0 0" rpy="-1.57079632679 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-1.7628" upper="1.7628" effort="87" velocity="2.1750"/>
  </joint>
  
  <joint name="joint3" type="revolute">
    <parent link="link2"/>
    <child link="link3"/>
    <origin xyz="0 -0.316 0" rpy="1.57079632679 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-2.8973" upper="2.8973" effort="87" velocity="2.1750"/>
  </joint>
  
  <joint name="joint4" type="revolute">
    <parent link="link3"/>
    <child link="link4"/>
    <origin xyz="0.0825 0 0" rpy="1.57079632679 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-3.0718" upper="-0.0698" effort="87" velocity="2.1750"/>
  </joint>
  
  <joint name="joint5" type="revolute">
    <parent link="link4"/>
    <child link="link5"/>
    <origin xyz="-0.0825 0.384 0" rpy="-1.57079632679 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-2.8973" upper="2.8973" effort="12" velocity="2.6100"/>
  </joint>
  
  <joint name="joint6" type="revolute">
    <parent link="link5"/>
    <child link="link6"/>
    <origin xyz="0 0 0" rpy="1.57079632679 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-0.0175" upper="3.7525" effort="12" velocity="2.6100"/>
  </joint>
  
  <joint name="joint7" type="revolute">
    <parent link="link6"/>
    <child link="link7"/>
    <origin xyz="0.088 0 0" rpy="1.57079632679 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-2.8973" upper="2.8973" effort="12" velocity="2.6100"/>
  </joint>
  
</robot>
'''
    
    # Save to temporary file
    temp_urdf = tempfile.NamedTemporaryFile(mode='w', suffix='.urdf', delete=False)
    temp_urdf.write(urdf_content)
    temp_urdf.close()
    
    return Path(temp_urdf.name)


def visualize_franka(repo_dir: Optional[Path] = None, robot_model: str = "fr3") -> None:
    """Visualize the Franka Emika arm URDF using Rerun.

    If ``repo_dir`` is ``None`` the franka_description repo is downloaded
    automatically using :func:`download_franka_description`.
    
    Args:
        repo_dir: Path to franka_description repository
        robot_model: Robot model to visualize (fr3, fr3v2, fp3, fer)
    """

    if repo_dir is None:
        repo_dir = download_franka_description(Path.home()/".cache"/"franka_description")

    urdf_path = create_simple_franka_urdf(repo_dir, robot_model)
    robot = URDF.load(urdf_path)

    # Initialize rerun and log robot data
    rr.init("franka_urdf")
    
    print("Loading robot model and generating visualization data...")
    
    fk = robot.link_fk()

    for link, tf in fk.items():
        for i, visual in enumerate(link.visuals):
            geom = visual.geometry
            node_path = f"/{link.name}/{i}"
            
            # Apply transform
            transform_matrix = tf @ visual.origin
            rr.log(node_path, rr.Transform3D(mat3x3=transform_matrix[:3, :3], translation=transform_matrix[:3, 3]))
            
            if geom.mesh is not None:
                mesh_path = repo_dir / geom.mesh.filename
                try:
                    mesh = trimesh.load_mesh(mesh_path)
                    rr.log(
                        node_path,
                        rr.Mesh3D(
                            vertex_positions=mesh.vertices,
                            triangle_indices=mesh.faces,
                        ),
                    )
                    print(f"Loaded mesh for {link.name}")
                except Exception as e:
                    print(f"Warning: Could not load mesh {mesh_path}: {e}")
    
    # Save recording to file
    rrd_path = "/tmp/franka_robot.rrd"
    rr.save(rrd_path)
    print(f"✅ Robot visualization saved to: {rrd_path}")
    
    # For WSL users - provide instructions
    print("\n🔧 To view in WSL:")
    print("1. Run: rerun --web-viewer --port 9092")
    print("2. Open: http://localhost:9092 in your browser")
    print(f"3. Drag and drop: {rrd_path} into the web viewer")
    print("\n🚀 Alternative - direct web viewer:")
    print(f"   Run: rerun --web-viewer {rrd_path}")
    
    print("\n✨ Robot model successfully loaded and ready for visualization!")


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
    parser.add_argument(
        "--robot_model",
        type=str,
        default="fr3",
        choices=["fr3", "fr3v2", "fp3", "fer"],
        help="Robot model to visualize (default: fr3)",
    )
    args = parser.parse_args()
    visualize_franka(args.repo_dir, args.robot_model)
