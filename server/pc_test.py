import paho.mqtt.client as mqtt
import time
import json

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"PC端已连接本地 Broker! 状态码: {reason_code}")
    # PC 订阅来自树莓派的心跳/反馈主题
    client.subscribe("moving-claw/heartbeat") 

def on_message(client, userdata, msg):
    # 打印树莓派发回来的消息
    print(f"[收到树莓派反馈] {msg.payload.decode()}")

# 使用与 SOP 一致的 v2 API
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

# 连接本地邮局
client.connect("127.0.0.1", 1883, 60)
client.loop_start()  # 开启后台线程监听接收

try:
    sequence_id = 0
    while True:
        sequence_id += 1
        # 构造符合你项目结构的 JSON 指令
        cmd = {
            "timestamp": time.time(),
            "action": "test_ping",
            "sequence_id": sequence_id
        }
        print(f"\n[PC 发送指令] -> sequence_id: {sequence_id}")
        # 发布到控制主题
        client.publish("moving-claw/control", json.dumps(cmd))
        time.sleep(3)  # 每 3 秒发一次
except KeyboardInterrupt:
    print("\n测试结束，断开连接。")
    client.disconnect()