# 🚩 Flagfall Arena

**Flagfall Arena** adalah game *Capture the Flag* (CTF) bertema MOBA 2D yang dibangun menggunakan Python dan Pygame. Pilih kelas karakter favoritmu, susun strategi dengan bot tim, dan rebut bendera musuh di berbagai arena yang menantang!

## 🎮 Fitur Utama

* **Sistem Kelas Karakter**: 
    * 🗡️ **Assassin**: Pergerakan cepat dan serangan mematikan.
    * 🛡️ **Knight**: Pertahanan tinggi dengan kemampuan melempar perisai boomerang.
    * 🧱 **Tank**: HP sangat tebal dan mampu melempar batu besar.
    * 🧙 **Wizard**: Menembakkan Cahaya Suci dan Meteor Strike.
    * 😇 **Support**: Memberikan perlindungan shield dan menyembuhkan rekan tim.
* **Beragam Map**: Bertarung di *Floating Mystic Forest*, *Desert Outpost*, atau *Frozen Floating Peak*.
* **Mekanik Canggih**: Sistem kamera dinamis, AI bot yang cerdas, proyektil khusus tiap karakter, dan sistem respawn (5 detik).
* **Audio Imersif**: Musik latar berbeda untuk Menu dan Battle, serta efek suara kemenangan, kekalahan, dan kehidupan.

## 🕹️ Kontrol Permainan

| Tombol | Aksi |
| :--- | :--- |
| **W, A, S, D** | Bergerak (Atas, Kiri, Bawah, Kanan) |
| **F** | Serangan Jarak Dekat (Melee) |
| **G** | Kemampuan Jarak Jauh (Ranged) / Skill Spesial |
| **H** | Kemampuan Bertahan (Defense/Shield/Blink) |
| **J** | Kemampuan Ultimate |
| **ESC** | Pause Game |

## 🛠️ Persyaratan Sistem

* Python 3.x
* Library Pygame

## 🚀 Cara Menjalankan

1.  Pastikan kamu sudah menginstal Python. Jika belum punya Pygame, instal lewat terminal/CMD:
    ```bash
    pip install pygame
    ```
2.  Jalankan file utama:
    ```bash
    python main.py
    ```

## 📂 Struktur File
* `main.py`: Entry point aplikasi dan sistem UI.
* `mechanism.py`: Logika tempur, proyektil, AI, dan manajemen pertandingan.
* `character_*.py`: Definisi logika dan visual masing-masing kelas karakter.
* `map_*.py`: Desain lingkungan dan efek visual map.
* `setting.py`: Konfigurasi konstanta game (Resolusi, FPS, Warna).

---
