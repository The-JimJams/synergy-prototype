#!/usr/bin/env python3
"""
==============================================================================
Multi-AMR Warehouse Simulation - Universal Cross-Platform Launcher
Works on: macOS (Darwin), Linux (Ubuntu/Debian), Windows (Native & WSL2)
==============================================================================
"""

import os
import sys
import time
import platform
import subprocess
import argparse
import signal

def get_project_paths():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    world_path = os.path.join(project_root, "simulation", "worlds", "warehouse.sdf")
    models_path = os.path.join(project_root, "simulation", "models")
    return project_root, world_path, models_path

def setup_environment(models_path):
    env = os.environ.copy()
    
    # Set Gazebo IP loopback for reliable local IPC
    env["GZ_IP"] = "127.0.0.1"
    
    # Append models directory to Gazebo resource search path
    existing_resource_path = env.get("GZ_SIM_RESOURCE_PATH", "")
    if existing_resource_path:
        env["GZ_SIM_RESOURCE_PATH"] = f"{models_path}{os.pathsep}{existing_resource_path}"
    else:
        env["GZ_SIM_RESOURCE_PATH"] = models_path
        
    return env

def main():
    parser = argparse.ArgumentParser(
        description="Launch Multi-AMR Warehouse Gazebo Simulation across all platforms."
    )
    parser.add_argument(
        "--server", "-s", action="store_true",
        help="Run in headless (server-only) physics mode."
    )
    parser.add_argument(
        "--gui", "-g", action="store_true",
        help="Run GUI client only (connects to an already running server)."
    )
    parser.add_argument(
        "--world", "-w", type=str, default=None,
        help="Custom world SDF path (default: simulation/worlds/warehouse.sdf)."
    )
    args = parser.parse_args()

    project_root, default_world_path, models_path = get_project_paths()
    world_path = args.world if args.world else default_world_path
    
    if not os.path.exists(world_path):
        print(f"[-] Error: World file not found at: {world_path}", file=sys.stderr)
        sys.exit(1)

    env = setup_environment(models_path)
    current_os = platform.system()  # 'Darwin', 'Linux', 'Windows'

    print("=" * 60)
    print(" 🤖 Multi-AMR Warehouse Simulation Launcher")
    print(f" Operating System : {current_os} ({platform.machine()})")
    print(f" Project Directory: {project_root}")
    print(f" World File       : {os.path.relpath(world_path, project_root)}")
    print(f" Models Path      : {os.path.relpath(models_path, project_root)}")
    print("=" * 60)

    # 1. Server-Only (Headless)
    if args.server:
        print("[+] Launching Gazebo Server (Headless)...")
        try:
            subprocess.run(["gz", "sim", "-s", "-r", world_path], env=env, check=True)
        except KeyboardInterrupt:
            print("\n[+] Server stopped.")
        return

    # 2. GUI-Only Client
    if args.gui:
        print("[+] Launching Gazebo GUI Client...")
        try:
            subprocess.run(["gz", "sim", "-g"], env=env, check=True)
        except KeyboardInterrupt:
            print("\n[+] GUI closed.")
        return

    # 3. Full Simulation (Server + GUI)
    if current_os == "Darwin":
        # macOS dual-process architecture to avoid thread conflicts (gz-sim issue #44)
        print("[+] macOS detected: Spawning server in background + GUI in foreground...")
        server_proc = None
        try:
            server_proc = subprocess.Popen(
                ["gz", "sim", "-s", "-r", world_path],
                env=env
            )
            time.sleep(1.5)  # Wait for server socket initialization
            
            subprocess.run(["gz", "sim", "-g"], env=env)
        except KeyboardInterrupt:
            print("\n[!] Interrupt received.")
        finally:
            if server_proc and server_proc.poll() is None:
                print("[+] Shutting down background physics server...")
                server_proc.terminate()
                try:
                    server_proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    server_proc.kill()
            print("[+] Simulation closed cleanly.")
    else:
        # Linux and Windows (Single unified invocation or subprocess)
        print("[+] Launching Full Simulation (Server + GUI)...")
        try:
            subprocess.run(["gz", "sim", "-r", world_path], env=env, check=True)
        except KeyboardInterrupt:
            print("\n[+] Simulation stopped.")

if __name__ == "__main__":
    main()
