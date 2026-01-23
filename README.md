# ❌⭕ Caro Online (Python Socket Game)

> Dự án game Cờ Caro (Gomoku) trực tuyến nhiều người chơi, sử dụng kiến trúc Client-Server với Python, Socket và Tkinter.

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![GUI](https://img.shields.io/badge/GUI-Tkinter-green.svg)
![Database](https://img.shields.io/badge/Database-SQLite3-orange.svg)
![Network](https://img.shields.io/badge/Network-TCP%2FSocket-red.svg)

## 📖 Mục lục

- [Giới thiệu](#-giới-thiệu)
- [Tính năng](#-tính-năng)
- [Cài đặt & Chạy](#-cài-đặt--chạy)
- [Cấu trúc dự án](#-cấu-trúc-dự-án)
- [Hướng dẫn chơi](#-hướng-dẫn-chơi)
- [Thành viên nhóm](#-thành-viên-nhóm)

---

## 📝 Giới thiệu

**Caro Online** là một ứng dụng game desktop cho phép hai người chơi kết nối và thi đấu với nhau qua mạng LAN hoặc Internet. Dự án được xây dựng hoàn toàn bằng **Python**, áp dụng các kỹ thuật lập trình mạng (Socket Programming), đa luồng (Multi-threading) và cơ sở dữ liệu (SQLite).

Mục tiêu của dự án là xây dựng một hệ thống game hoàn chỉnh từ khâu đăng ký, đăng nhập, tìm phòng chơi cho đến việc lưu trữ kết quả và xếp hạng.

---

## ✨ Tính năng

### 🎮 Gameplay (Lối chơi)

- **Bàn cờ chuẩn:** Kích thước 15x15 ô.
- **Luật chơi:** Người thắng là người đầu tiên xếp được 5 quân liên tiếp (Ngang, Dọc, Chéo).
- **Turn-based:** Hệ thống quản lý lượt đi chặt chẽ (Server-authoritative), ngăn chặn gian lận.
- **Chức năng bổ trợ:**
  - 🏳️ **Đầu hàng (Surrender):** Xin thua để kết thúc sớm.
  - 🔄 **Tái đấu (Rematch):** Chơi ván mới ngay lập tức không cần ra sảnh.

### 🌐 Hệ thống & Kết nối

- **Real-time Multiplayer:** Sử dụng TCP Socket để truyền tải nước đi tức thời.
- **Game Lobby (Sảnh chờ):**
  - Xem danh sách các phòng đang chờ.
  - Tạo phòng mới.
  - Làm mới danh sách (Refresh).
  - Tham gia phòng (Join).
- **Chat trong phòng:** Nhắn tin trò chuyện trực tiếp với đối thủ.

### 💾 Dữ liệu & Người dùng

- **Hệ thống tài khoản:** Đăng ký và Đăng nhập bảo mật (Mật khẩu được mã hóa SHA-256).
- **Lưu trữ tự động:** Tự động tạo Database SQLite khi chạy lần đầu.
- **Bảng xếp hạng (Leaderboard):** Xem Top người chơi có điểm số cao nhất.
- **Hồ sơ cá nhân (Profile):** Xem thống kê số trận thắng/thua, tỉ lệ thắng.

---

## ⚙️ Cài đặt & Chạy

### Yêu cầu

- Python 3.x trở lên.
- Các thư viện chuẩn của Python (đã có sẵn): `tkinter`, `socket`, `threading`, `sqlite3`, `json`.

### Các bước thực hiện

1.  **Clone dự án về máy:**

    ```bash
    git clone https://github.com/TrongPhucX5/caro-online.git
    cd caro-online
    ```

2.  **Khởi động Server (Bắt buộc chạy trước):**
    Mở terminal (CMD/PowerShell) tại thư mục gốc và chạy:

    ```bash
    python server/main.py
    ```

    Server sẽ khởi tạo database và lắng nghe tại `127.0.0.1:5555`.

3.  **Khởi động Client (Người chơi):**
    Mở một (hoặc nhiều) terminal mới và chạy:
    ```bash
    python client/main.py
    ```

---

## 📂 Cấu trúc dự án

```
caro-online/
├── server/
│   ├── main.py          # Server trung tâm (Socket, Threading)
│   ├── game_server.py   # (Optional) Xử lý logic game riêng biệt
│   └── room_manager.py  # (Optional) Quản lý phòng
├── client/
│   ├── main.py          # Entry point (nếu dùng)
│   ├── network.py       # Class xử lý kết nối mạng (Gửi/Nhận JSON)
│   └── app.py           # Giao diện đồ họa chính (Tkinter, Lobby, Board)
├── shared/
│   ├── protocol.py      # (Optional) Định nghĩa protocol
│   ├── game.py          # (Optional) Logic game chung
│   └── board.py         # Logic bàn cờ & kiểm tra thắng thua
├── database/
│   ├── database.py      # Class xử lý SQLite (Auth, Save Game, Leaderboard)
│   └── caro.db          # File dữ liệu (Tự sinh ra khi chạy)
├── assets/              # Hình ảnh, icon (nếu có)
├── requirements.txt     # Các thư viện cần thiết
└── README.md            # Tài liệu hướng dẫn
```

---

## 📖 Hướng dẫn chơi

1.  **Đăng nhập:** Nhập Username và Password. Nếu tài khoản chưa tồn tại, hệ thống sẽ tự động đăng ký.
2.  **Sảnh chờ (Lobby):**
    - Bấm `Create Room` để tạo phòng và đợi.
    - Hoặc chọn một phòng có trạng thái `waiting` từ danh sách và bấm `Join Selected`.
3.  **Trong game:**
    - Người tạo phòng cầm quân `X` (đi trước).
    - Người vào phòng cầm quân `O`.
    - Sử dụng khung chat để trò chuyện.
4.  **Kết thúc:**
    - Khi có người thắng, bảng thông báo sẽ hiện ra.
    - Điểm số sẽ được cộng vào hệ thống xếp hạng.

---

## 👥 Thành viên nhóm 15

| STT | Thành viên         | Vai trò          | Nhiệm vụ chính                                       |
| :-: | :----------------- | :--------------- | :--------------------------------------------------- |
|  1  | Lê Trọng Phúc      | Server & Network | Xây dựng Socket Server, Protocol, Room Management.   |
|  2  | Trần Ghi Đông      | Game Logic & AI  | Viết logic bàn cờ (Board), check win, thuật toán AI. |
|  3  | Võ Minh Quân       | GUI & Frontend   | Thiết kế giao diện Tkinter, Lobby, Animation bàn cờ. |
|  4  | Nguyễn Minh Phụng  | Database & User  | Thiết kế CSDL SQLite, Auth System, Leaderboard.      |
|  5  | Nguyễn Hoàng Phụng | Testing & DevOps | Kiểm thử, viết Unit Test, đóng gói dự án.            |
