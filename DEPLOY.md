# Menjalankan Spicy Dollz di server sendiri

Tujuan: semua koin, akun, dan unggahan tersimpan permanen di disk server milik Anda, dengan backup otomatis.

## 1. Siapkan
- Sebuah VPS yang syaratnya (Acceptable Use Policy) mengizinkan konten dewasa legal secara tertulis. Minimal 2 vCPU, 4 GB RAM, disk 80 GB atau lebih (video cepat memakan ruang).
- Sebuah domain (misalnya spicydollz.com). Arahkan record A domain ke IP VPS.

## 2. Pasang
```
sudo apt update && sudo apt install -y docker.io docker-compose-plugin sqlite3
# upload folder spicy-dollz ke server, lalu:
cd spicy-dollz
cp .env.example .env      # isi DOMAIN, SECRET_KEY, ADMIN_EMAILS
mkdir -p data
# pindahkan data lama: ekstrak file backup dari Settings > Backup ke ./data
#   spicy.db  -> data/spicy.db
#   media/    -> data/media/
sudo docker compose up -d --build
```
Buka https://DOMAIN-ANDA. Sertifikat HTTPS dibuat otomatis.

## 3. Backup otomatis setiap malam
```
crontab -e
# tambahkan:
30 3 * * * /path/ke/spicy-dollz/deploy/backup.sh >> /var/log/spicy-backup.log 2>&1
```
Simpan juga salinan di luar server (rclone ke penyimpanan lain), supaya data aman walau VPS rusak.

## 4. Pembaruan aplikasi
Ganti file `server.py` dan folder `public/`, lalu `sudo docker compose up -d --build`. Folder `data/` tidak disentuh, jadi koin dan unggahan tetap ada.
