# 🚀 Kurulum Kılavuzu

## 📋 Sistem Gereksinimleri

- **Python**: 3.8 veya üzeri
- **İşletim Sistemi**: Windows, macOS, Linux
- **RAM**: Minimum 2GB (4GB önerilir)
- **Disk Alanı**: 100MB

## 🔧 Hızlı Kurulum

### 1. Temel Kurulum (Sadece Core Features)

```bash
# Repository'yi klonla
git clone https://github.com/your-org/code-organism.git
cd code-organism

# Virtual environment oluştur (önerilir)
python -m venv venv

# Virtual environment'ı aktifle
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Temel bağımlılıkları yükle
pip install -r requirements.txt

# veya minimal kurulum için
pip install pyjwt
```

### 2. Gelişmiş Kurulum (Tüm Özellikler)

```bash
# Tüm özellikleri yükle
pip install -e ".[all]"

# veya setup.py kullanarak
python setup.py install
```

### 3. Özellik Bazlı Kurulum

```bash
# Sadece metrics özellikleri
pip install -e ".[metrics]"

# Sadece dashboard özellikleri
pip install -e ".[dashboard]"

# Distributed özellikler (Redis desteği)
pip install -e ".[distributed]"

# Development araçları
pip install -e ".[dev]"
```

## 🐳 Docker Kurulum

```dockerfile
# Dockerfile örneği
FROM python:3.11-slim

WORKDIR /app

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıkları
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodları
COPY . .

# Uygulamayı çalıştır
CMD ["python", "auth_tissue_demo.py"]
```

Docker ile çalıştırma:

```bash
# Image oluştur
docker build -t code-organism .

# Container çalıştır
docker run -it code-organism
```

## 📦 Bağımlılık Detayları

### Core Bağımlılıklar (Zorunlu)

| Paket | Versiyon | Kullanım Amacı |
|-------|----------|----------------|
| Python built-ins | - | Temel Python modülleri |
| pyjwt | >=2.8.0 | JWT token yönetimi |

### Opsiyonel Bağımlılıklar

#### Metrics & Monitoring
| Paket | Versiyon | Kullanım Amacı |
|-------|----------|----------------|
| prometheus-client | >=0.19.0 | Prometheus metrik export |
| psutil | >=5.9.6 | Sistem kaynak monitoring |

#### Dashboard & Visualization
| Paket | Versiyon | Kullanım Amacı |
|-------|----------|----------------|
| aiohttp | >=3.9.1 | Async web server |
| matplotlib | >=3.8.2 | Grafik oluşturma |
| pandas | >=2.1.4 | Veri analizi |

#### Distributed Features
| Paket | Versiyon | Kullanım Amacı |
|-------|----------|----------------|
| redis | >=5.0.1 | Distributed messaging |
| aiocache | >=0.12.2 | Async cache desteği |

#### Development Tools
| Paket | Versiyon | Kullanım Amacı |
|-------|----------|----------------|
| pytest | >=7.4.3 | Test framework |
| pytest-asyncio | >=0.23.2 | Async test desteği |
| black | >=23.12.1 | Kod formatlama |
| mypy | >=1.8.0 | Type checking |
| ruff | >=0.1.9 | Linting |
| coverage | >=7.3.4 | Test coverage |

## 🧪 Kurulumu Test Etme

```bash
# Basit test
python -c "from codecell_example import CodeCell; print('✅ Core import başarılı')"

# Demo çalıştır
python auth_tissue_demo.py

# Unit testleri çalıştır (dev tools gerekli)
pytest tests/

# Type checking
mypy .

# Linting
ruff check .
```

## 🔧 Yapılandırma

### Ortam Değişkenleri

```bash
# Logging seviyesi
export CODE_ORGANISM_LOG_LEVEL=INFO

# Metrics export
export PROMETHEUS_PORT=9090

# Redis bağlantısı (opsiyonel)
export REDIS_URL=redis://localhost:6379

# Dashboard port
export DASHBOARD_PORT=8080
```

### Konfigürasyon Dosyası

`config.yaml` örneği:

```yaml
organism:
  name: "MyOrganism"
  health_check_interval: 30
  
metrics:
  enabled: true
  export_interval: 10
  retention_hours: 24
  
dashboard:
  enabled: true
  port: 8080
  refresh_interval: 5
  
tissue_defaults:
  max_cells: 100
  quarantine_threshold: 0.3
  regeneration_enabled: true
```

## 🚨 Sorun Giderme

### ImportError: No module named 'pyjwt'
```bash
pip install pyjwt
```

### asyncio RuntimeError on Windows
```python
# main.py başına ekle
import asyncio
if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
```

### Redis Connection Error
```bash
# Redis'in çalıştığından emin ol
redis-cli ping
# PONG dönmeli

# veya Redis olmadan çalıştır
export DISABLE_REDIS=true
```

## 📚 İleri Seviye Kurulum

### Production Deployment

```bash
# Gunicorn ile dashboard servisi
pip install gunicorn
gunicorn -w 4 -k aiohttp.GunicornWebWorker dashboard:app

# Systemd service örneği
sudo cp code-organism.service /etc/systemd/system/
sudo systemctl enable code-organism
sudo systemctl start code-organism
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: code-organism
spec:
  replicas: 3
  selector:
    matchLabels:
      app: code-organism
  template:
    metadata:
      labels:
        app: code-organism
    spec:
      containers:
      - name: organism
        image: code-organism:latest
        ports:
        - containerPort: 8080
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379"
```

## ✅ Kurulum Doğrulama Checklist

- [ ] Python versiyonu 3.8+
- [ ] Virtual environment aktif
- [ ] Core bağımlılıklar yüklü
- [ ] Demo başarıyla çalışıyor
- [ ] Import testleri geçiyor
- [ ] Opsiyonel özellikler (isteğe bağlı)

## 🆘 Destek

Kurulum sorunları için:
- GitHub Issues: https://github.com/your-org/code-organism/issues
- Documentation: https://code-organism.readthedocs.io
- Discord: https://discord.gg/code-organism