import paho.mqtt.client as mqtt
import time
import json

# 这里填你 Windows 笔记本的 Tailscale IP！
PC_TAILSCALE_IP = "100.X.X.X" 

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"树莓派已成功连接到 PC 大脑! 状态码: {reason_code}")
    # 树莓派订阅来自 PC 的控制指令主题
    client.subscribe("moving-claw/control")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"\n[收到 PC 指令] {payload}")
    
    try:
        data = json.loads(payload)
        # 计算单向延迟（PC发出到树莓派收到的时间差）
        latency = (time.time() - data['timestamp']) * 1000
        print(f"当前网络延迟: {latency:.2f} ms")
        
        # 模拟执行完毕，向 PC 发送反馈包
        feedback = {"status": "success", "echo_seq": data.get("sequence_id")}
        print(f"[树莓派发送反馈] -> {feedback}")
        client.publish("moving-claw/heartbeat", json.dumps(feedback))
    except Exception as e:
        print(f"解析出错: {e}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

print(f"正在寻找 PC 大脑 ({PC_TAILSCALE_IP})...")
# 连接 PC 上的 Broker
client.connect(PC_TAILSCALE_IP, 1883, 60)
client.loop_forever()  # 阻塞运行，持续监听