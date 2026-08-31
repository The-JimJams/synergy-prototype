# Synergy Prototype

Multi-agent Autonomous Mobile Robot (AMR) orchestration and logistics simulation framework.

## Project Structure

```
synergy-prototype/
├── gazebo/             # Gazebo Simulation Environment (Worlds, AMR Models, Physics, Launchers)
│   ├── simulation/     # Worlds (SDF) and modular 3D models
│   ├── scripts/        # Cross-platform simulation execution scripts (Python / Shell / Batch / PowerShell)
│   └── README.md       # Gazebo module detailed documentation
```

## Modules

- **[`gazebo/`](./gazebo/README.md)**: Gazebo Harmonic / Fortress warehouse simulation environment featuring 3 autonomous mobile robots (AMR A, B, C) with differential drive physics, 2D planar LiDAR sensor streaming, and interactive logistics staging zones.
