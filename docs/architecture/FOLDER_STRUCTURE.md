# 📁 Code Organism - Klasör Yapısı

## 🏗️ Organizasyon Felsefesi

Proje yapısı, biyolojik hiyerarşiyi ve yazılım mühendisliği best practice'lerini birleştirerek organize edilmiştir.

```
Code-Snippet/
│
├── 📄 README.md                    # Ana proje dokümantasyonu
│
├── 🔧 config/                      # Konfigürasyon dosyaları
│   ├── requirements.txt            # Python bağımlılıkları
│   └── setup.py                    # Paket kurulum dosyası
│
├── 📚 docs/                        # Dokümantasyon
│   ├── 🏗️ architecture_diagram.md  # Mimari diyagramlar
│   ├── 🔄 ASYNC_STYLE_GUIDE.md    # Async/Sync kullanım rehberi
│   ├── 🧬 biological_features_analysis.md # Biyolojik özellikler
│   ├── 📊 dashboard_examples.md    # Dashboard JSON örnekleri
│   ├── 💿 INSTALL.md              # Kurulum kılavuzu
│   └── 📋 PROJECT_STRUCTURE.md    # Proje yapısı detayları
│
├── 🔬 examples/                    # Örnek uygulamalar
│   ├── __init__.py
│   ├── 🔐 auth_tissue_demo.py     # Authentication tissue örneği
│   └── 🎯 basic_usage.py          # Basit kullanım örneği
│
├── 🧬 src/                         # Kaynak kodlar
│   ├── __init__.py
│   │
│   ├── 🧫 core/                   # Çekirdek biyolojik bileşenler
│   │   ├── __init__.py
│   │   ├── codecell_example.py    # [Legacy] Basit Cell
│   │   ├── enhanced_codecell.py   # 🧬 Gelişmiş Cell (organelles)
│   │   ├── advanced_codetissue.py # 🧪 Tissue implementasyonu
│   │   ├── stem_cell_system.py    # 🏦 Stem cell banking
│   │   ├── code_organ.py          # 🫀 Organ katmanı
│   │   └── code_system.py         # 🧠 System katmanı
│   │
│   ├── 🔩 components/             # Destek bileşenleri
│   │   ├── __init__.py
│   │   ├── tissue_components.py   # ECM, Homeostasis, Vascularization
│   │   └── system_managers.py     # Boot, Maintenance, Memory managers
│   │
│   ├── 📊 monitoring/             # İzleme ve metrikler
│   │   ├── __init__.py
│   │   └── performance_metrics.py # Metrik toplama ve dashboard
│   │
│   └── 🔒 security/               # Güvenlik bileşenleri
│       ├── __init__.py
│       └── security_manager.py    # Dynamic pattern management
│
└── 🧪 tests/                      # Test suite (gelecek)
    └── __init__.py
```

## 📦 Paket Hiyerarşisi

### 1. **Core Package** (`src.core`)
Biyolojik hiyerarşinin temel taşları:

```python
from src.core import (
    EnhancedCodeCell,    # Cell layer
    AdvancedCodeTissue,  # Tissue layer
    CodeOrgan,           # Organ layer
    CodeSystem           # System layer
)
```

### 2. **Components Package** (`src.components`)
Destek sistemleri:

```python
from src.components import (
    ExtracellularMatrix,      # Tissue matrix
    HomeostasisController,    # Balance control
    VascularizationSystem,    # Resource flow
    SystemBootManager,        # Boot management
    MaintenanceManager        # Maintenance ops
)
```

### 3. **Monitoring Package** (`src.monitoring`)
Performans ve sağlık takibi:

```python
from src.monitoring import (
    MetricsCollector,    # Metrik toplama
    CellMetrics,        # Cell-level metrics
    TissueMetrics,      # Tissue-level metrics
    MetricsDashboard    # Dashboard system
)
```

### 4. **Security Package** (`src.security`)
Güvenlik ve tehdit yönetimi:

```python
from src.security import (
    DynamicSecurityManager,  # Pattern management
    ThreatPattern,          # Threat definitions
    ImmuneSystemCell        # Enhanced immune cell
)
```

## 🎯 Kullanım Örnekleri

### Basit Kullanım
```python
# Basic cell creation
from src.core import EnhancedCodeCell

cell = EnhancedCodeCell("my_cell")
```

### Tissue Oluşturma
```python
from src.core import AdvancedCodeTissue
from src.components import ExtracellularMatrix

tissue = AdvancedCodeTissue("MyTissue")
tissue.ecm = ExtracellularMatrix("MyTissue")
```

### System Kurulumu
```python
from src.core import CodeSystem
from src.components import SystemBootManager

system = CodeSystem("MySystem")
boot_manager = SystemBootManager("MySystem")
await boot_manager.boot_system(system)
```

## 🔄 Import Paths

### Internal Imports (within src/)
```python
# In src/core/code_organ.py
from ..components.tissue_components import ExtracellularMatrix
from ..monitoring.performance_metrics import MetricsCollector
```

### External Imports (from examples/)
```python
# In examples/demo.py
import sys
sys.path.append('..')

from src.core import CodeSystem
from src.monitoring import MetricsDashboard
```

## 📊 Klasör İstatistikleri

| Kategori | Dosya Sayısı | Amaç |
|----------|--------------|------|
| Core | 6 | Temel biyolojik bileşenler |
| Components | 2 | Destek sistemleri |
| Monitoring | 1 | Performans takibi |
| Security | 1 | Güvenlik yönetimi |
| Examples | 2 | Kullanım örnekleri |
| Docs | 6 | Dokümantasyon |
| Config | 2 | Konfigürasyon |

## 🚀 Avantajlar

1. **Clear Separation**: Her paketin net bir sorumluluğu var
2. **Scalability**: Yeni modüller kolayca eklenebilir
3. **Maintainability**: İlgili kodlar bir arada
4. **Discoverability**: Dosya konumları mantıklı ve tahmin edilebilir
5. **Professional**: Endüstri standartlarına uygun

## 🎨 Renk Kodlaması

- 🧬 **Biyolojik Bileşenler**: Core package
- 🔩 **Altyapı**: Components package
- 📊 **İzleme**: Monitoring package
- 🔒 **Güvenlik**: Security package
- 🔬 **Örnekler**: Examples
- 📚 **Dokümantasyon**: Docs
- 🔧 **Konfigürasyon**: Config

Bu yapı ile proje artık:
- ✅ Modüler
- ✅ Ölçeklenebilir
- ✅ Bakımı kolay
- ✅ Profesyonel
- ✅ Takip edilebilir