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

## Hướng dẫn cài đặt

1. Cài Python 3.x
2. Cài các package trong requirements.txt
3. Chạy server: `python server/main.py`
4. Chạy client: `python client/main.py`
