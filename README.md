# SMART PARKING SIMULATOR

**Aplikasi Simulasi Pengelolaan Area Parkir Berbasis Python dan PySide6**

Smart Parking Simulator merupakan aplikasi desktop untuk merancang area parkir serta mensimulasikan perjalanan kendaraan dan pejalan kaki. Proyek ini menerapkan konsep Matematika Diskrit, terutama **Teori Graf (Graph Theory)** dan **Algoritma Dijkstra**, untuk menentukan lintasan dengan total bobot jarak terkecil.

---

## Tentang Proyek

Smart Parking Simulator memungkinkan pengguna membuat peta area parkir, membangun jaringan jalan menggunakan node dan edge, memilih gedung tujuan serta gerbang masuk, kemudian menjalankan simulasi kendaraan menuju slot parkir dan pedestrian menuju gedung.

Aplikasi ini merupakan simulator edukatif berbasis peta yang dirancang menggunakan Python. Aplikasi belum terhubung dengan sensor parkir, kamera, GPS, atau perangkat IoT pada area parkir nyata.

## Daftar Isi

1. [Fitur Utama](#fitur-utama)
2. [Konsep Matematika Diskrit](#konsep-matematika-diskrit)
3. [Teknologi yang Digunakan](#teknologi-yang-digunakan)
4. [Persyaratan](#persyaratan)
5. [Instalasi dan Menjalankan Aplikasi](#instalasi-dan-menjalankan-aplikasi)
6. [Alur Penggunaan](#alur-penggunaan)
7. [Struktur Proyek](#struktur-proyek)
8. [Pengujian](#pengujian)
9. [Batasan Proyek](#batasan-proyek)
10. [Pengembangan Selanjutnya](#pengembangan-selanjutnya)

---

## Fitur Utama

### 1. Map Editor

Melalui Design Mode, pengguna dapat membuat dan mengatur tata letak area parkir dengan menambahkan objek:

| Objek | Fungsi |
|---|---|
| Parking Slot | Merepresentasikan tempat parkir kendaraan. |
| Building | Merepresentasikan gedung tujuan pedestrian. |
| Entrance Gate | Merepresentasikan gerbang masuk kendaraan. |
| Car Placeholder | Objek visual kendaraan pada peta. |
| Graph Node | Titik simpul dalam jaringan graf. |
| Vehicle Road | Jalur yang digunakan kendaraan. |
| Pedestrian Path | Jalur yang digunakan pejalan kaki. |

Pengguna dapat menghubungkan node untuk membentuk jaringan jalan yang digunakan dalam simulasi.

### 2. Vehicle Network dan Pedestrian Network

Aplikasi memiliki dua jaringan yang dibedakan berdasarkan fungsi:

- **Vehicle Network:** digunakan untuk perjalanan kendaraan dari gerbang masuk menuju slot parkir.
- **Pedestrian Network:** digunakan untuk perjalanan pejalan kaki dari area parkir menuju gedung tujuan.

Pemisahan jaringan memastikan pencarian rute menggunakan jalur yang sesuai dengan jenis perjalanan.

### 3. Parking Assignment

Fitur Parking Assignment digunakan untuk menentukan dan mengalokasikan slot parkir.

Pengguna memilih gedung tujuan dan gerbang masuk secara manual. Sistem kemudian memeriksa slot pada gedung yang dipilih dan mengalokasikan slot yang tersedia.

Setelah slot ditentukan, sistem menghitung rute kendaraan menuju lokasi parkir dan rute pedestrian menuju gedung.

### 4. Algoritma Dijkstra

Algoritma Dijkstra digunakan untuk mencari lintasan dengan total bobot jarak terkecil pada jaringan yang dipilih.

Dalam proyek ini, Dijkstra diterapkan pada dua jenis perjalanan:

- **Rute kendaraan:** menghitung lintasan dari gerbang masuk menuju slot parkir.
- **Rute pedestrian:** menghitung lintasan dari area parkir menuju gedung tujuan.

Hasil pencarian mencakup urutan node dan edge yang dilalui serta total jarak perjalanan.

Dengan demikian, kendaraan dan pedestrian bergerak mengikuti jaringan yang telah dirancang, bukan bergerak langsung menuju titik tujuan.

### 5. Vehicle Simulation

Kendaraan disimulasikan bergerak mengikuti urutan node pada Vehicle Network menuju slot parkir yang telah dialokasikan.

Ketika kendaraan mencapai slot tujuan, sistem memperbarui status slot sesuai kondisi parkir.

### 6. Pedestrian Simulation

Setelah kendaraan mencapai slot parkir, simulasi pedestrian dijalankan untuk menggambarkan perjalanan pejalan kaki dari area parkir menuju gedung melalui Pedestrian Network.

Jalur pedestrian divisualisasikan secara terpisah dari jalur kendaraan.

### 7. Status Parkir dan Multi-Vehicle

Setiap slot parkir memiliki tiga status utama:

| Status | Keterangan |
|---|---|
| AVAILABLE | Slot tersedia dan dapat dialokasikan. |
| RESERVED | Slot telah dialokasikan untuk kendaraan. |
| OCCUPIED | Slot telah ditempati kendaraan. |

Aplikasi mendukung simulasi beberapa kendaraan secara berurutan selama kapasitas parkir masih tersedia.

### 8. Dashboard Statistics

Dashboard menampilkan ringkasan kondisi peta dan simulasi, antara lain:

- Jumlah slot parkir.
- Jumlah slot berdasarkan status AVAILABLE, RESERVED, dan OCCUPIED.
- Jumlah gedung dan gerbang.
- Jumlah node dan edge.
- Jumlah kendaraan yang telah disimulasikan.
- Total jarak perjalanan kendaraan.

### 9. Save dan Load Layout

Fitur Save Layout digunakan untuk menyimpan tata letak area parkir yang telah dibuat.

Fitur Load Layout digunakan untuk memuat kembali tata letak yang sebelumnya disimpan sehingga pengguna dapat melanjutkan atau mengulang simulasi tanpa membuat peta dari awal.

---

## Konsep Matematika Diskrit

Smart Parking Simulator menerapkan beberapa konsep Matematika Diskrit berikut:

| Konsep | Penerapan dalam Proyek |
|---|---|
| Himpunan (Set Theory) | Pengelompokan node, edge, dan objek pada area parkir. |
| Teori Graf (Graph Theory) | Merepresentasikan jaringan jalan menggunakan vertex dan edge. |
| Weighted Graph | Memberikan bobot jarak pada setiap edge. |
| Path | Merepresentasikan lintasan dari satu node ke node lainnya. |
| Shortest Path | Menentukan lintasan dengan total bobot terkecil. |
| Algoritma Dijkstra | Menghitung lintasan terpendek pada jaringan berbobot nonnegatif. |
| Shortest Path Tree | Merepresentasikan hubungan predecessor dari hasil pencarian Dijkstra. |
| Logika Boolean | Memeriksa kondisi slot parkir, keberhasilan assignment, dan ketersediaan rute. |

### Cara Kerja Dijkstra dalam Proyek

Jaringan jalan direpresentasikan sebagai graf yang terdiri dari kumpulan node dan edge. Setiap edge memiliki bobot yang menunjukkan jarak antara dua node.

Dijkstra menghitung jarak sementara dari node awal ke node lainnya. Pada setiap tahap, algoritma memilih node yang memiliki jarak sementara terkecil, kemudian memperbarui jarak node tetangganya apabila ditemukan lintasan dengan total bobot yang lebih kecil.

Proses tersebut menghasilkan lintasan dengan total bobot minimum dari titik awal menuju titik tujuan, selama bobot setiap edge tidak negatif.

---

## Teknologi yang Digunakan

| Teknologi | Kegunaan |
|---|---|
| Python | Bahasa pemrograman utama aplikasi. |
| PySide6 / Qt | Membangun antarmuka desktop dan komponen grafis. |
| QGraphicsScene | Mengelola objek dan elemen visual pada peta. |
| QGraphicsView | Menampilkan serta menyediakan interaksi pengguna dengan kanvas peta. |
| JSON | Format penyimpanan layout apabila digunakan oleh mekanisme Save/Load proyek. |

---

## Persyaratan

Sebelum menjalankan aplikasi, pastikan perangkat telah memiliki:

1. Python yang kompatibel dengan versi PySide6 yang digunakan.
2. Source code proyek secara lengkap.
3. Package atau library PySide6.
4. File layout atau data yang ingin digunakan, jika ada.

Visual Studio Code atau editor kode lainnya bersifat opsional. Aplikasi dapat dijalankan melalui terminal.

## Instalasi dan Menjalankan Aplikasi

Panduan berikut menggunakan Windows PowerShell.

### 1. Buka Folder Proyek

Buka terminal pada folder utama SMART_PARKING, yaitu folder yang berisi file `main.py`.

### 2. Buat Virtual Environment

```powershell
python -m venv .venv
```

### 3. Aktifkan Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

Jika PowerShell menolak aktivasi karena kebijakan eksekusi skrip, gunakan Command Prompt:

```bat
.venv\Scripts\activate.bat
```

### 4. Instal Dependensi

Jalankan perintah berikut:

```powershell
python -m pip install -r requirements.txt
```

Jika belum tersedia file requirements.txt, instal PySide6 secara langsung:

```powershell
python -m pip install PySide6
```

### 5. Jalankan Aplikasi

Setelah dependensi berhasil dipasang, jalankan:

```powershell
python main.py
```

Jika aplikasi tidak terbuka, periksa pesan error pada terminal. Pastikan virtual environment aktif, dependensi telah terpasang, dan perintah dijalankan dari folder yang berisi main.py.

---

## Alur Penggunaan

1. Jalankan aplikasi menggunakan `python main.py`.
2. Masuk ke Design Mode.
3. Buat tata letak area parkir dengan menambahkan gedung, gerbang, slot parkir, dan objek lainnya.
4. Buat Graph Node dan hubungkan node menggunakan edge.
5. Pastikan jaringan kendaraan dan pedestrian dibuat sesuai fungsinya.
6. Simpan layout jika ingin menggunakannya kembali.
7. Masuk ke Simulation Mode.
8. Pilih gedung tujuan dan gerbang masuk.
9. Jalankan proses Parking Assignment.
10. Amati kendaraan mengikuti rute hasil perhitungan Dijkstra menuju slot parkir.
11. Setelah kendaraan berhenti, amati simulasi pedestrian menuju gedung.
12. Periksa perubahan status slot dan informasi pada Dashboard Statistics.

---

## Struktur Proyek

Berikut struktur direktori utama proyek:

```text
SMART_PARKING/
│
├── README.md
├── main.py
├── requirements.txt
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py
│   └── panels.py
│
└── editor/
    ├── __init__.py
    ├── graph_algorithms.py
    ├── graph_items.py
    ├── layout_manager.py
    ├── map_items.py
    ├── map_scene.py
    ├── map_view.py
    ├── parking_assignment.py
    ├── route_visualizer.py
    └── vehicle_simulator.py
```

### Penjelasan Modul

| File / Folder | Fungsi |
|---|---|
| `main.py` | Titik masuk untuk menjalankan aplikasi. |
| `ui/main_window.py` | Mengatur jendela utama dan integrasi antarmuka. |
| `ui/panels.py` | Menyediakan komponen panel antarmuka. |
| `editor/map_scene.py` | Mengelola scene dan objek pada peta. |
| `editor/map_view.py` | Mengatur tampilan serta interaksi pengguna dengan peta. |
| `editor/graph_algorithms.py` | Menangani algoritma graf dan pencarian rute. |
| `editor/route_visualizer.py` | Memvisualisasikan jalur dan hasil pencarian rute. |
| `editor/parking_assignment.py` | Menangani proses alokasi slot parkir. |
| `editor/vehicle_simulator.py` | Menangani simulasi pergerakan kendaraan. |
| `editor/layout_manager.py` | Mengelola penyimpanan dan pemuatan layout. |
| `editor/graph_items.py` dan `editor/map_items.py` | Menyediakan objek graf dan objek peta. |

---

## Pengujian

Skenario pengujian fungsional selama pengembangan meliputi:

- Simulasi kendaraan secara berurutan.
- Pengujian kapasitas ketika slot parkir penuh.
- Pencarian rute kendaraan menggunakan Dijkstra.
- Pencarian rute pedestrian menggunakan Dijkstra.
- Pengujian pemilihan lintasan alternatif berdasarkan bobot.
- Pengujian alur kendaraan menuju slot parkir yang dilanjutkan dengan perjalanan pedestrian menuju gedung.

## Batasan Proyek

Beberapa batasan pada versi aplikasi ini adalah:

- Tata letak dan jaringan jalan dibuat secara manual oleh pengguna.
- Pemilihan gedung tujuan dan gerbang masuk dilakukan secara manual.
- Jarak dihitung berdasarkan koordinat kanvas dan skala simulasi.
- Bobot rute berfokus pada jarak dan belum memperhitungkan kemacetan atau waktu tempuh aktual.
- Aplikasi belum terhubung dengan sensor okupansi atau perangkat IoT.
- Hasil simulasi bergantung pada kelengkapan dan ketepatan koneksi node serta edge yang dibuat pengguna.

## Pengembangan Selanjutnya

Beberapa pengembangan yang dapat dipertimbangkan untuk versi berikutnya:

- Integrasi sensor atau IoT untuk membaca status slot parkir secara langsung.
- Pemilihan gedung atau slot parkir secara otomatis.
- Pembobotan rute berdasarkan waktu tempuh dan kondisi jalan.
- Penyimpanan riwayat simulasi dan penggunaan parkir.
- Kalibrasi skala peta berdasarkan ukuran area sebenarnya.

---

## Lisensi dan Penggunaan

Ketentuan distribusi, modifikasi, dan penggunaan ulang source code mengikuti lisensi yang ditetapkan oleh pemilik proyek.

## 📌 Tentang Proyek

**Smart Parking Simulator** merupakan aplikasi desktop yang dikembangkan
menggunakan **Python** dan **PySide6** untuk merancang area parkir serta
mensimulasikan perjalanan kendaraan dan pejalan kaki.

Pengguna dapat membuat peta area parkir, membangun jaringan jalan
menggunakan **node** dan **edge**, memilih gedung tujuan serta gerbang
masuk, kemudian menjalankan simulasi kendaraan menuju slot parkir dan
pedestrian menuju gedung.

Proyek ini menerapkan konsep Matematika Diskrit, terutama **Teori Graf
(Graph Theory)** dan **Algoritma Dijkstra**, untuk menentukan lintasan
dengan total bobot jarak terkecil pada jaringan yang telah dibuat.

> **Catatan:** Smart Parking Simulator merupakan simulator edukatif
> berbasis peta yang disusun oleh pengguna. Aplikasi belum terhubung
> dengan sensor parkir, kamera, GPS, atau perangkat IoT pada area parkir
> nyata.

## 📑 Daftar Isi

-   [Fitur Utama](#-fitur-utama)
-   [Konsep Matematika Diskrit](#-konsep-matematika-diskrit)
-   [Teknologi yang Digunakan](#-teknologi-yang-digunakan)
-   [Persyaratan](#-persyaratan)
-   [Instalasi dan Menjalankan
    Aplikasi](#-instalasi-dan-menjalankan-aplikasi)
-   [Alur Penggunaan](#-alur-penggunaan)
-   [Struktur Proyek](#-struktur-proyek)
-   [Pengujian](#-pengujian)
-   [Batasan Proyek](#-batasan-proyek)
-   [Pengembangan Selanjutnya](#-pengembangan-selanjutnya)
-   [Lisensi dan Penggunaan](#-lisensi-dan-penggunaan)

------------------------------------------------------------------------

## 🚀 Fitur Utama

### 1. Map Editor

Melalui **Design Mode**, pengguna dapat membuat dan mengatur tata letak
area parkir dengan menambahkan objek berikut:

  Objek             Fungsi
  ----------------- ---------------------------------------------
  Parking Slot      Merepresentasikan tempat parkir kendaraan.
  Building          Merepresentasikan gedung tujuan pedestrian.
  Entrance Gate     Merepresentasikan gerbang masuk kendaraan.
  Car Placeholder   Objek visual kendaraan pada peta.
  Graph Node        Titik simpul dalam jaringan graf.
  Vehicle Road      Jalur yang digunakan kendaraan.
  Pedestrian Path   Jalur yang digunakan pejalan kaki.

Pengguna dapat menghubungkan node untuk membentuk jaringan jalan yang
akan digunakan dalam simulasi.

### 2. Vehicle Network dan Pedestrian Network

Aplikasi memiliki dua jaringan yang dibedakan berdasarkan fungsi:

-   **Vehicle Network** --- digunakan untuk perjalanan kendaraan dari
    gerbang masuk menuju slot parkir.
-   **Pedestrian Network** --- digunakan untuk perjalanan pejalan kaki
    dari area parkir menuju gedung tujuan.

Pemisahan jaringan memastikan proses pencarian rute menggunakan jalur
yang sesuai dengan jenis perjalanan.

### 3. Parking Assignment

Fitur **Parking Assignment** digunakan untuk menentukan dan
mengalokasikan slot parkir.

Pengguna memilih gedung tujuan dan gerbang masuk secara manual. Sistem
kemudian memeriksa slot pada gedung yang dipilih dan mengalokasikan slot
yang tersedia.

Setelah slot ditentukan, sistem dapat menghitung rute kendaraan menuju
lokasi parkir dan rute pedestrian menuju gedung.

### 4. Algoritma Dijkstra

Algoritma **Dijkstra** digunakan untuk mencari lintasan dengan total
bobot jarak terkecil pada jaringan yang dipilih.

Dalam proyek ini, Dijkstra diterapkan pada dua jenis perjalanan:

-   **Rute kendaraan:** menghitung lintasan dari gerbang masuk menuju
    slot parkir.
-   **Rute pedestrian:** menghitung lintasan dari area parkir menuju
    gedung tujuan.

Hasil pencarian mencakup urutan node dan edge yang dilalui serta total
jarak perjalanan. Dengan demikian, kendaraan dan pedestrian bergerak
mengikuti jaringan yang telah dirancang, bukan sekadar bergerak langsung
menuju titik tujuan.

### 5. Vehicle Simulation

Fitur ini mensimulasikan pergerakan kendaraan mengikuti urutan node pada
**Vehicle Network** menuju slot parkir yang telah dialokasikan.

Ketika kendaraan mencapai slot tujuan, sistem memperbarui status slot
sesuai kondisi parkir.

### 6. Pedestrian Simulation

Setelah kendaraan mencapai slot parkir, simulasi pedestrian dijalankan
untuk menggambarkan perjalanan pejalan kaki dari area parkir menuju
gedung melalui **Pedestrian Network**.

Jalur pedestrian divisualisasikan secara terpisah dari jalur kendaraan.

### 7. Status Parkir dan Multi-Vehicle

Setiap slot parkir memiliki tiga status utama:

  Status        Keterangan
  ------------- ------------------------------------------
  `AVAILABLE`   Slot tersedia dan dapat dialokasikan.
  `RESERVED`    Slot telah dialokasikan untuk kendaraan.
  `OCCUPIED`    Slot telah ditempati kendaraan.

Aplikasi mendukung simulasi beberapa kendaraan secara berurutan selama
kapasitas parkir masih tersedia. Slot yang sudah ditempati tidak
seharusnya dialokasikan kembali kepada kendaraan berikutnya.

### 8. Dashboard Statistics

Dashboard menampilkan ringkasan kondisi peta dan simulasi, antara lain:

-   Jumlah slot parkir.
-   Jumlah slot berdasarkan status `AVAILABLE`, `RESERVED`, dan
    `OCCUPIED`.
-   Jumlah gedung dan gerbang.
-   Jumlah node dan edge.
-   Jumlah kendaraan yang telah disimulasikan.
-   Total jarak perjalanan kendaraan.

### 9. Save dan Load Layout

Fitur **Save Layout** digunakan untuk menyimpan tata letak area parkir
yang telah dibuat.

Fitur **Load Layout** digunakan untuk memuat kembali tata letak yang
sebelumnya disimpan sehingga pengguna dapat melanjutkan atau mengulang
simulasi tanpa harus membuat peta dari awal.

------------------------------------------------------------------------

## 🧠 Konsep Matematika Diskrit

Smart Parking Simulator menerapkan beberapa konsep Matematika Diskrit
berikut:

  -----------------------------------------------------------------------
  Konsep                              Penerapan dalam Proyek
  ----------------------------------- -----------------------------------
  **Himpunan (Set Theory)**           Pengelompokan node, edge, dan objek
                                      pada area parkir.

  **Teori Graf (Graph Theory)**       Merepresentasikan jaringan jalan
                                      menggunakan vertex dan edge.

  **Weighted Graph**                  Memberikan bobot jarak pada setiap
                                      edge.

  **Path**                            Merepresentasikan lintasan dari
                                      satu node ke node lainnya.

  **Shortest Path**                   Menentukan lintasan dengan total
                                      bobot terkecil.

  **Algoritma Dijkstra**              Menghitung lintasan terpendek pada
                                      jaringan berbobot nonnegatif.

  **Shortest Path Tree**              Memvisualisasikan hubungan
                                      predecessor dari hasil pencarian
                                      Dijkstra.

  **Logika Boolean**                  Memeriksa kondisi slot parkir,
                                      keberhasilan assignment, dan
                                      ketersediaan rute.
  -----------------------------------------------------------------------

### Bagaimana Dijkstra Bekerja dalam Proyek Ini?

Jaringan jalan direpresentasikan sebagai graf yang terdiri dari kumpulan
node dan edge. Setiap edge memiliki bobot yang menunjukkan jarak antara
dua node.

Dijkstra menghitung jarak sementara dari node awal ke node lainnya. Pada
setiap tahap, algoritma memilih node yang memiliki jarak sementara
terkecil, kemudian memperbarui jarak node tetangganya apabila ditemukan
lintasan dengan total bobot yang lebih kecil.

Proses tersebut menghasilkan lintasan dengan total bobot minimum dari
titik awal menuju titik tujuan, selama bobot setiap edge tidak negatif.

------------------------------------------------------------------------

## 🛠️ Teknologi yang Digunakan

  -----------------------------------------------------------------------
  Teknologi                           Kegunaan
  ----------------------------------- -----------------------------------
  **Python**                          Bahasa pemrograman utama aplikasi.

  **PySide6 / Qt**                    Membangun antarmuka desktop dan
                                      komponen grafis.

  **QGraphicsScene**                  Mengelola objek dan elemen visual
                                      pada peta.

  **QGraphicsView**                   Menampilkan serta menyediakan
                                      interaksi pengguna dengan kanvas
                                      peta.

  **JSON**                            Format penyimpanan layout apabila
                                      digunakan oleh mekanisme Save/Load
                                      proyek.
  -----------------------------------------------------------------------

## 💻 Persyaratan

Sebelum menjalankan aplikasi, pastikan perangkat telah memiliki:

1.  **Python** yang kompatibel dengan versi PySide6 yang digunakan.
2.  Source code proyek secara lengkap.
3.  Package atau library **PySide6**.
4.  File layout atau data yang ingin digunakan, jika ada.

**Visual Studio Code** atau editor kode lainnya bersifat opsional.
Aplikasi dapat dijalankan melalui terminal.

## ⚙️ Instalasi dan Menjalankan Aplikasi

Panduan berikut menggunakan **Windows PowerShell**.

### 1. Buka Folder Proyek

Buka terminal pada folder utama `SMART_PARKING`, yaitu folder yang
berisi file `main.py`.

### 2. Buat Virtual Environment

Virtual environment digunakan untuk memisahkan library proyek dari
instalasi Python lainnya.

``` powershell
python -m venv .venv
```

### 3. Aktifkan Virtual Environment

``` powershell
.\.venv\Scripts\Activate.ps1
```

Jika PowerShell menolak aktivasi karena kebijakan eksekusi skrip,
gunakan Command Prompt:

``` bat
.venv\Scripts\activate.bat
```

### 4. Instal Dependensi

Jika proyek menyediakan file `requirements.txt`, jalankan:

``` powershell
python -m pip install -r requirements.txt
```

Jika file `requirements.txt` belum tersedia, instal PySide6 secara
langsung:

``` powershell
python -m pip install PySide6
```

### 5. Jalankan Aplikasi

Setelah dependensi berhasil dipasang, jalankan:

``` powershell
python main.py
```

Jika aplikasi tidak terbuka, periksa pesan error pada terminal. Pastikan
virtual environment aktif, dependensi telah terpasang, dan perintah
dijalankan dari folder yang berisi `main.py`.

------------------------------------------------------------------------

## 🕹️ Alur Penggunaan

Berikut langkah penggunaan Smart Parking Simulator secara umum:

1.  Jalankan aplikasi menggunakan `python main.py`.
2.  Masuk ke **Design Mode**.
3.  Buat tata letak area parkir dengan menambahkan gedung, gerbang, slot
    parkir, dan objek lainnya.
4.  Buat **Graph Node** dan hubungkan node menggunakan edge.
5.  Pastikan jaringan kendaraan dan pedestrian dibuat sesuai fungsinya.
6.  Simpan layout jika ingin menggunakannya kembali.
7.  Masuk ke **Simulation Mode**.
8.  Pilih gedung tujuan dan gerbang masuk.
9.  Jalankan proses **Parking Assignment**.
10. Amati kendaraan mengikuti rute hasil perhitungan Dijkstra menuju
    slot parkir.
11. Setelah kendaraan berhenti, amati simulasi pedestrian menuju gedung.
12. Periksa perubahan status slot dan informasi pada **Dashboard
    Statistics**.

------------------------------------------------------------------------

## 📁 Struktur Proyek

Berikut gambaran struktur modul utama berdasarkan susunan proyek:

``` text
SMART_PARKING/
│
├── README.md
├── main.py
├── requirements.txt
│
├── ui/
│   └── main_window.py
│
└── editor/
    ├── map_scene.py
    ├── map_view.py
    ├── graph_algorithms.py
    ├── route_visualizer.py
    ├── parking_assignment.py
    └── vehicle_simulator.py
```

### Penjelasan Modul

  -----------------------------------------------------------------------
  File / Folder                       Fungsi
  ----------------------------------- -----------------------------------
  `main.py`                           Titik masuk untuk menjalankan
                                      aplikasi.

  `ui/main_window.py`                 Mengatur jendela utama dan
                                      integrasi antarmuka.

  `editor/map_scene.py`               Mengelola scene dan objek pada
                                      peta.

  `editor/map_view.py`                Mengatur tampilan serta interaksi
                                      pengguna dengan peta.

  `editor/graph_algorithms.py`        Menangani algoritma graf dan
                                      pencarian rute apabila ditempatkan
                                      pada modul ini.

  `editor/route_visualizer.py`        Memvisualisasikan jalur dan hasil
                                      pencarian rute.

  `editor/parking_assignment.py`      Menangani proses alokasi slot
                                      parkir.

  `editor/vehicle_simulator.py`       Menangani simulasi pergerakan
                                      kendaraan.
  -----------------------------------------------------------------------

> Struktur di atas merupakan gambaran modul utama. Pastikan nama file
> dan folder disesuaikan dengan source code yang disertakan pada
> repository.

## 🧪 Pengujian

Skenario pengujian fungsional yang telah dilakukan selama pengembangan
meliputi:

-   Simulasi kendaraan secara berurutan.
-   Pengujian kapasitas ketika slot parkir penuh.
-   Pencarian rute kendaraan menggunakan Dijkstra.
-   Pencarian rute pedestrian menggunakan Dijkstra.
-   Pengujian pemilihan lintasan alternatif berdasarkan bobot.
-   Pengujian alur kendaraan menuju slot parkir yang dilanjutkan dengan
    perjalanan pedestrian menuju gedung.

Pengujian dilakukan untuk memastikan fitur utama bekerja sesuai alur
simulasi yang dirancang.

## ⚠️ Batasan Proyek

Beberapa batasan pada versi aplikasi ini adalah:

-   Tata letak dan jaringan jalan dibuat secara manual oleh pengguna.
-   Pemilihan gedung tujuan dan gerbang masuk dilakukan secara manual.
-   Jarak dihitung berdasarkan koordinat kanvas dan skala simulasi.
-   Bobot rute berfokus pada jarak dan belum memperhitungkan kemacetan
    atau waktu tempuh aktual.
-   Aplikasi belum terhubung dengan sensor okupansi atau perangkat IoT.
-   Hasil simulasi bergantung pada kelengkapan dan ketepatan koneksi
    node serta edge yang dibuat pengguna.

## 🔮 Pengembangan Selanjutnya

Beberapa pengembangan yang dapat dipertimbangkan untuk versi berikutnya:

-   Integrasi sensor atau IoT untuk membaca status slot parkir secara
    langsung.
-   Pemilihan gedung atau slot parkir secara otomatis.
-   Pembobotan rute berdasarkan waktu tempuh dan kondisi jalan.
-   Penyimpanan riwayat simulasi dan penggunaan parkir.
-   Kalibrasi skala peta berdasarkan ukuran area sebenarnya.

## 📄 Lisensi dan Penggunaan

Ketentuan distribusi, modifikasi, dan penggunaan ulang source code
mengikuti lisensi yang ditetapkan oleh pemilik proyek.
