import grpc
import cv2
import numpy as np
import time
import vision_pb2
import vision_pb2_grpc

# 🚨 替换为你笔记本的 Tailscale IP
PC_IP = "100.X.X.X" 

def generate_mock_frames():
    print("🎬 虚拟摄像头已启动，开始生成模拟视频流...")
    frame_count = 0
    while True:
        # 1. 凭空生成一张 640x480 的黑色幕布
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # 2. 在幕布上画上跳动的帧数和提示，证明这是动态的流
        text1 = f"Mock Frame: {frame_count}"
        text2 = "No Physical Camera"
        cv2.putText(frame, text1, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        cv2.putText(frame, text2, (50, 280), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # 3. 压缩成 JPEG 数据流
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
        result, buffer = cv2.imencode('.jpg', frame, encode_param)

        # 4. 封装进 gRPC 的 VideoFrame 协议里发送
        yield vision_pb2.VideoFrame(
            image_data=buffer.tobytes(),
            width=640,
            height=480,
            timestamp=time.time(),
            quality=80
        )
        
        frame_count += 1
        # 放慢发送速度（一秒2帧），方便你肉眼观察日志跳动
        time.sleep(0.5) 

def run():
    print(f"正在连接 PC 视觉中枢: {PC_IP}:50051...")
    # 建立与 PC 的双向流通道
    with grpc.insecure_channel(f'{PC_IP}:50051') as channel:
        stub = vision_pb2_grpc.VisionServiceStub(channel)
        try:
            # 树莓派不断发 mock 图像，并接收 PC 传回的模拟检测框
            responses = stub.StreamVideo(generate_mock_frames())
            for response in responses:
                if response.detections:
                    det = response.detections[0]
                    print(f"👁️ [PC 大脑反馈] 看到: {det.label} (置信度 {det.confidence:.2f})")
        except grpc.RpcError as e:
            print(f"gRPC 通信中断: {e.details()}")

if __name__ == '__main__':
    run()