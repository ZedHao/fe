#!/bin/bash
cd "$(dirname "$0")"

# 获取本机局域网IP
IP=$(ipconfig getifaddr en0 2>/dev/null || ifconfig | grep 'inet ' | grep -v 127.0.0.1 | awk '{print $2}' | head -1)
PORT=3000

# 先启动服务器
node server.js &
SERVER_PID=$!
sleep 3

echo "========================"
echo "  🐷 猪猪基金 折溢价查询"
echo "========================"
echo ""
echo "  Mac 本地:  http://localhost:$PORT"
echo "  同WiFi:    http://$IP:$PORT"
echo ""

# 询问是否开启外网穿透
echo -n "  是否开启外网访问（手机在外也能用）？[y/N] "
read -t 10 yn
if [[ "$yn" =~ ^[Yy]$ ]]; then
  echo ""
  echo "  ⏳ 正在建立外网通道..."
  echo ""
  
  # Serveo - 纯SSH隧道，无需装任何东西
  echo "  📡 连接中..."
  ssh -o StrictHostKeyChecking=no -R 80:localhost:$PORT serveo.net 2>&1 &
  SSH_PID=$!
  
  # 等待拿到URL
  sleep 5
  
  # 从日志中提取URL
  TUNNEL_URL=$(ps -p $SSH_PID 2>/dev/null && echo "获取中...")
  
  echo "========================"
  echo "  📱 外网访问地址如下 ↓"
  echo "  （看上面绿色文字，https://xxx.serveousercontent.com）"
  echo "========================"
  echo "  ⚠️  首次访问会显示一个提示页，"
  echo "     【不要输IP】直接点击页面上的"
  echo "     'Click to Continue' 按钮即可"
  echo "  ⚠️  关闭此窗口 = 断开外网"
  echo ""

  # 自动打开浏览器显示Mac端
  open "http://localhost:$PORT"
  
  wait $SERVER_PID $SSH_PID 2>/dev/null
else
  echo "  仅限内网使用"
  echo "  关闭此窗口即可停止服务器"
  echo ""
  open "http://localhost:$PORT"
  wait $SERVER_PID
fi
