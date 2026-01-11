# Caro Online

## Mô tả

Dự án Caro Online gồm server, client, chia sẻ logic, và database. Hỗ trợ chơi caro trực tuyến nhiều phòng.

## Cấu trúc thư mục

```
caro-online/
├── server/
│   ├── main.py          # Server chính
│   ├── game_server.py   # Xử lý game
│   └── room_manager.py  # Quản lý phòng
├── client/
│   ├── main.py          # Client chính
│   ├── network.py       # Kết nối mạng
│   └── gui.py           # Giao diện Tkinter
├── shared/
│   ├── protocol.py      # Message protocol
│   ├── game.py          # Logic game
│   └── board.py         # Bàn cờ 15x15
├── database/
│   └── database.py      # SQLite database
├── assets/
│   └── (hình ảnh nếu cần)
├── requirements.txt
└── README.md
```

## ✨ Tính năng
- 🎯 Bàn cờ 15x15 với win condition 5 thẳng hàng
- 🌐 Multiplayer real-time qua socket
- 👤 Đăng nhập/đăng ký người dùng
- 💬 Chat trong phòng chơi
- 📊 Leaderboard và thống kê người chơi
- 🧪 Unit tests và integration tests

## 👥 Thành viên nhóm
1. **Người 1** - Server & Network
2. **Người 2** - Game Logic & AI
3. **Người 3** - GUI & Frontend
4. **Người 4** - Database & User System
5. **Người 5** - Testing & DevOps
