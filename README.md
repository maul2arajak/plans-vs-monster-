Plans vs Monster — Haunted LawnGame tower defense 2D berbasis Python (pygame) dengan tema bertahan dari serangan monster di halaman malam (Haunted Lawn). Pemain harus mempertahankan markas mulai pukul 01:00 hingga 06:00 (durasi permainan 5 menit) dengan menanam kombinasi tanaman pertahanan dan mengisi amunisi penembak secara manual menggunakan biji kopi.Fitur UtamaArena Grid 5×9 (1280×720, 60 FPS): Lima jalur (lane) serangan monster dengan panduan grid dan pratinjau penempatan (ghost preview).Mekanisme Amunisi Biji Kopi (Drag & Drop): Tanaman penembak tidak menembak tanpa peluru; pemain perlu menarik biji kopi dari Coffee Plant lalu melepasnya ke Shooter Plant untuk menambah amunisi.Tingkat Kesulitan Progresif: Terbagi menjadi tiga fase berdasarkan waktu permainan:Mudah (01:00 – 03:00 / 2 menit pertama)Sedang (03:00 – 05:00 / 2 menit berikutnya)Sulit (05:00 – 06:00 / 1 menit terakhir, interval kemunculan lebih cepat dan monster datang berkelompok)Cutscene Video & Audio: Dilengkapi video pembuka, video menang, dan video kalah (opencv-python), musik latar, serta efek suara untuk tembakan, ledakan, dan serangan monster.Penerapan Pemrograman Berorientasi Objek (PBO): Menerapkan abstraction, encapsulation, inheritance, polymorphism, dan Factory Pattern.Daftar Tanaman & MusuhTanamanTanamanHPBatas KuotaFungsi & KemampuanCoffee Plant905Menghasilkan biji kopi setiap 5 detik (maksimal 3 biji aktif per tanaman). Setiap biji yang diberikan ke Shooter menambah +3 amunisi.Shooter Plant907Menembakkan peluru kopi (28 damage, cooldown 0,98 detik) ke monster di jalur yang sama selama memiliki amunisi.Bomb Plant703Ranjau peledak instan yang langsung menghabisi monster di sekitarnya saat monster mendekat di jalur yang sama.Shield Plant3004Tanaman pelindung ber-HP tinggi untuk menahan laju serangan monster.Catatan Kuota: Menghapus tanaman secara manual menggunakan Sekop (Hapus) akan mengembalikan kuota kartu. Jika tanaman hancur diserang monster atau Bomb Plant meledak, kuota kartu tetap terpakai.MusuhMonster: Memiliki 185 HP, berjalan dari kanan ke kiri, dan menyerang tanaman di depannya sebesar 18 damage setiap 0,65 detik. Jika monster berhasil melewati batas kiri halaman, nyawa markas (3 hati) berkurang 1.Cara Bermain & KontrolAksiKontrolMenanam tanamanKlik dan tahan kartu tanaman di kiri atas, lalu lepas di kotak rumputMengisi amunisi penembakKlik dan tarik biji kopi, lalu lepas tepat di atas Shooter PlantMenghapus tanamanKlik ikon Sekop (Hapus) di kanan bawah, lalu klik tanaman di gridMemilih slot tanamanTombol 1–4 atau A / DMelewati (skip) cutsceneSPACEKeluar dari permainanESCPrasyaratPython 3.10 – 3.13 (disarankan Python 3.11; jika dijalankan menggunakan Python 3.14+, main.py akan mencoba menjalankan ulang melalui py -3.11).Library Python pada requirements.txt:pygame>=2.5.0pytmx>=3.32opencv-python>=4.8.0Instalasi & Menjalankan GameClone repositori ini:git clone https://github.com/maul2arajak/plans-vs-monster-.git
cd plans-vs-monster-
Pasang dependensi:pip install -r requirements.txt
Jalankan game:python main.py
main.py juga memiliki pengecekan otomatis yang akan mencoba menginstal dependensi yang kurang apabila belum terpasang.Struktur Proyekplans-vs-monster-/
├── main.py                # Titik masuk program & pengecekan dependensi/versi Python
├── requirements.txt       # Daftar library Python yang dibutuhkan
├── maps/
│   └── night_forest.tmx   # Data peta permainan
├── assets/
│   ├── audio/             # Musik latar (.mp3) dan efek suara (.wav)
│   ├── effects/           # Frame animasi ledakan
│   ├── fonts/             # Font antarmuka (m6x11.ttf, LycheeSoda.ttf)
│   ├── monster/           # Sprite animasi berjalan & menyerang monster
│   ├── plants/            # Sprite tanaman, animasi, biji kopi, dan peluru
│   ├── tiles/             # Aset tile lingkungan
│   ├── ui/                # Kartu tanaman, ikon hati, dan sekop
│   ├── videos/            # Video cutscene pembuka, menang, dan kalah (.mp4 & .mp3)
│   └── world/             # Gambar latar belakang arena
└── src/
    ├── game.py            # Loop utama, logika gelombang monster, dan kontrol input
    ├── settings.py        # Konstanta layar, grid, stat tanaman/monster, dan path aset
    ├── ui.py              # Tampilan HUD (kartu, jam, nyawa, sekop, dan petunjuk drag)
    ├── cutscene.py        # Pemutar cutscene video layar penuh dengan audio terpisah
    ├── tilemap.py         # Renderer latar belakang arena
    ├── support.py         # Utilitas pemuatan gambar, frame animasi, dan teks
    └── entities/
        ├── base.py        # Abstract base class (GameEntity & DamageableEntity)
        ├── factory.py     # PlantFactory untuk instansiasi tanaman
        ├── plants.py      # Implementasi CoffeePlant, ShooterPlant, BombPlant, ShieldPlant
        ├── monsters.py    # Implementasi Monster
        ├── items.py       # Implementasi CoffeeBean & Explosion
        └── projectiles.py # Implementasi Projectile
Kredit AsetLatar belakang arena dan konsep kartu benih (seed card) merujuk pada PythonPlantsVsZombies-master.zip, sedangkan logika permainan Coffee vs Monster merupakan implementasi kustom.
