# 🚀 PDDIKTI REST API

REST API wrapper untuk mengakses data PDDIKTI (Pangkalan Data Pendidikan Tinggi) Indonesia.

## 📋 Quick Start

### Instalasi Dependencies
```bash
pip install -r requirements.txt
```

### Menjalankan Server
```bash
# Development mode
python app.py

# Production mode dengan Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Server akan berjalan di: **http://localhost:5000**

## 🔗 API Endpoints

### 🏛️ **Universities (Perguruan Tinggi)**

#### 1. Cari Kampus
```
GET /api/v1/universities/search?q=<keyword>
```
**Contoh**: `GET /api/v1/universities/search?q=Universitas Indonesia`

#### 2. Detail Kampus
```
GET /api/v1/universities/<university_id>
```

#### 3. Program Studi Kampus
```
GET /api/v1/universities/<university_id>/programs?semester=<YYYYS>
```
**Contoh**: `GET /api/v1/universities/xxx/programs?semester=20241`

#### 4. Logo Kampus
```
GET /api/v1/universities/<university_id>/logo
```

#### 5. Statistik Kampus
```
GET /api/v1/universities/<university_id>/stats
```

### 👨‍🎓 **Students (Mahasiswa)**

#### 1. Cari Mahasiswa
```
GET /api/v1/students/search?q=<keyword>
```

#### 2. Detail Mahasiswa
```
GET /api/v1/students/<student_id>
```

### 👨‍🏫 **Lecturers (Dosen)**

#### 1. Cari Dosen
```
GET /api/v1/lecturers/search?q=<keyword>
```

#### 2. Profil Dosen
```
GET /api/v1/lecturers/<lecturer_id>
```

#### 3. Riset & Aktivitas Dosen
```
GET /api/v1/lecturers/<lecturer_id>/research
```

### 📚 **Programs (Program Studi)**

#### 1. Cari Program Studi
```
GET /api/v1/programs/search?q=<keyword>
```

#### 2. Detail Program Studi
```
GET /api/v1/programs/<program_id>
```

### 🔍 **Global Search**

#### Pencarian Universal
```
GET /api/v1/search?q=<keyword>
```

### 📊 **Statistics**

#### 1. Statistik Nasional
```
GET /api/v1/statistics/counts
```

#### 2. Data Visualisasi
```
GET /api/v1/statistics/visualizations?category=<universities|students|lecturers|programs>
```

## 📝 Format Response

### Success Response
```json
{
  "success": true,
  "message": "Success message",
  "data": {
    // Response data
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "data": null
}
```

## 💻 Contoh Penggunaan

### 1. Cari Daftar Kampus
```bash
curl "http://localhost:5000/api/v1/universities/search?q=Universitas"
```

### 2. JavaScript/Fetch
```javascript
// Cari kampus
const response = await fetch('http://localhost:5000/api/v1/universities/search?q=ITB');
const data = await response.json();

if (data.success) {
  console.log('Kampus ditemukan:', data.data);
} else {
  console.error('Error:', data.error);
}
```

### 3. Python requests
```python
import requests

# Cari kampus
response = requests.get('http://localhost:5000/api/v1/universities/search', 
                       params={'q': 'Institut Teknologi Bandung'})
data = response.json()

if data['success']:
    print(f"Ditemukan {len(data['data']['data'])} kampus")
    for kampus in data['data']['data']:
        print(f"- {kampus['nama']}")
```

## 🌐 CORS Support

API ini sudah mengaktifkan CORS, sehingga dapat diakses dari frontend web application.

## 🔧 Configuration

### Environment Variables
```bash
export FLASK_ENV=development  # untuk development
export FLASK_ENV=production   # untuk production
```

### Production Deployment
```bash
# Dengan Gunicorn (recommended)
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# Dengan uWSGI
uwsgi --http :8000 --wsgi-file app.py --callable app --processes 4
```

## 📊 Response Data Structure

### University Search Response
```json
{
  "success": true,
  "message": "Found 5 universities matching 'ITB'",
  "data": {
    "data": [
      {
        "id": "university_id_base64",
        "kode": "001234",
        "nama_singkat": "ITB",
        "nama": "Institut Teknologi Bandung"
      }
    ]
  }
}
```

### University Detail Response
```json
{
  "success": true,
  "message": "University details retrieved successfully",
  "data": {
    "nama_pt": "Institut Teknologi Bandung",
    "alamat": "Jl. Ganesha No. 10, Bandung",
    "website": "https://www.itb.ac.id",
    "email": "humas@itb.ac.id",
    "akreditasi_pt": "A",
    "status_pt": "Aktif"
  }
}
```

## 🚀 URL Endpoints Summary

**Base URL**: `http://localhost:5000` 

### Untuk Daftar Kampus (yang Anda minta):
- **Cari Kampus**: `GET /api/v1/universities/search?q=<keyword>`
- **Detail Kampus**: `GET /api/v1/universities/<university_id>`
- **Program Studi**: `GET /api/v1/universities/<university_id>/programs?semester=20241`
- **Logo Kampus**: `GET /api/v1/universities/<university_id>/logo`
- **Statistik**: `GET /api/v1/universities/<university_id>/stats`

### Test Endpoint
Akses `http://localhost:5000/` untuk melihat daftar lengkap semua endpoint.