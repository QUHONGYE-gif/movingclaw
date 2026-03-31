import grpc
from concurrent import futures
import cv2
import numpy as np
import vision_pb2
import vision_pb2_grpc

class VisionServicer(vision_pb2_grpc.VisionServiceServicer):
    def StreamVideo(self, request_iterator, context):
        print("💡 树莓派眼睛已连接，开始接收视频流...")
        try:
            for frame in request_iterator:
                # 1. 接收并解码 JPEG 图像数据
                nparr = np.frombuffer(frame.image_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                # 2. 在电脑屏幕上实时显示树莓派拍到的画面
                cv2.imshow("PC Vision Server (RTX 5060 Ready)", img)
                cv2.waitKey(1) # 1毫秒刷新，保持流畅
                
                # 3. 模拟大模型推理：构造返回的 BoundingBox
                response = vision_pb2.VisionResponse()
                bbox = response.detections.add()
                bbox.x, bbox.y, bbox.width, bbox.height = 100, 100, 50, 50
                bbox.label = "target_pen"
                bbox.confidence = 0.98
                
                # 返回识别结果流给树莓派
                yield response
                
        except Exception as e:
            print(f"连接断开或发生错误: {e}")
        finally:
            cv2.destroyAllWindows()

def serve():
    # 启动 gRPC 服务
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    vision_pb2_grpc.add_VisionServiceServicer_to_server(VisionServicer(), server)
    server.add_insecure_port('[::]:50051') # 监听所有网络接口的 50051 端口
    print("🚀 视觉中枢已启动，监听 50051 端口...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()