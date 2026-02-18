import subprocess
import os
import sys
from pathlib import Path

sys.path.append(os.path.join(os.path.expanduser("~"), "lerobot/src"))

try:
    from lerobot.scripts.lerobot_teleoperate import teleoperate, TeleoperateConfig
    from lerobot.robots.so_follower.config_so_follower import SOFollowerRobotConfig
    from lerobot.teleoperators.so_leader.config_so_leader import SOLeaderTeleopConfig
    from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def launch_rerun_server(port=9876, web_port=9090):
    cmd = [
        "rerun", 
        "--serve-web", 
        "--port", str(port), 
        "--web-viewer-port", str(web_port),
        "--memory-limit", "500MB"
    ]
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    HOST = "so101-pi5.local"
    PORT = 9876
    WEB_PORT = 9090
    
    CAM_INNOMAKER = "/dev/v4l/by-id/usb-Innomaker_Innomaker-U20CAM-1080p-S1_SN0001-video-index0"
    CAM_WED = "/dev/v4l/by-id/usb-Wed_Camera_Wed_Camera_20240420112206-video-index0"

    server_process = launch_rerun_server(PORT, WEB_PORT)
    
    print("-" * 60)
    print(f"VISUALIZATION URL: \nhttp://{HOST}:{WEB_PORT}/?url=rerun%2Bhttp://{HOST}:{PORT}/proxy&latency=low")
    print("-" * 60)

    cameras = {
        "wrist_cam": OpenCVCameraConfig(
            index_or_path=Path(CAM_INNOMAKER),
            fps=30,
            width=640,
            height=480
        ),
        "context_cam": OpenCVCameraConfig(
            index_or_path=Path(CAM_WED),
            fps=30,
            width=640,
            height=480
        ),
    }

    FOLLOWER_PATH = "/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AB9068718-if00"
    LEADER_PATH   = "/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AB9068718-if00"

    robot_cfg = SOFollowerRobotConfig(
        id="follower",
        port=FOLLOWER_PATH,
        cameras=cameras
    )

    teleop_cfg = SOLeaderTeleopConfig(
        id="leader",
        port=LEADER_PATH
    )

    cfg = TeleoperateConfig(
        robot=robot_cfg,
        teleop=teleop_cfg,
        display_data=True,
        display_ip="127.0.0.1",
        display_port=PORT,
        display_compressed_images=True,
        fps=60
    )

    try:
        teleoperate(cfg)
    except KeyboardInterrupt:
        print("\nShutdown signal received.")
    finally:
        server_process.terminate()
        print("Cleanup complete.")

if __name__ == "__main__":
    main()
