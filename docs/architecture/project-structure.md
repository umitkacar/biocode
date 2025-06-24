# 📁 Proje Yapısı ve Modül İlişkileri

## 🏗️ Dizin Yapısı

```
code-organism/
├── 📄 README.md                    # Ana dokümantasyon
├── 📄 INSTALL.md                   # Kurulum kılavuzu
├── 📄 PROJECT_STRUCTURE.md         # Bu dosya
├── 📄 requirements.txt             # Python bağımlılıkları
├── 📄 setup.py                     # Paket kurulum dosyası
│
├── 📊 docs/                        # Dokümantasyon
│   ├── architecture_diagram.md     # Mimari diyagramlar
│   ├── dashboard_examples.md       # Dashboard örnekleri
│   └── biological_features_analysis.md  # Özellik analizi
│
├── 🧬 core/                        # Core modüller
│   ├── __init__.py
│   ├── codecell_example.py         # Basit CodeCell [LEGACY]
│   ├── enhanced_codecell.py        # Gelişmiş CodeCell ⭐
│   ├── advanced_codetissue.py      # CodeTissue implementasyonu
│   └── stem_cell_system.py         # Stem cell ve banking
│
├── 📈 monitoring/                  # Monitoring ve metrics
│   ├── __init__.py
│   └── performance_metrics.py      # Metrik toplama sistemi
│
├── 🔬 examples/                    # Örnek uygulamalar
│   ├── __init__.py
│   └── auth_tissue_demo.py         # Authentication demo
│
├── 🧪 tests/                       # Test dosyaları
│   ├── __init__.py
│   ├── test_codecell.py
│   ├── test_codetissue.py
│   └── test_stem_cells.py
│
└── 🔧 config/                      # Konfigürasyon
    ├── default_config.yaml
    └── logging_config.yaml
```

## 🔗 Modül Bağımlılık Grafiği

```
┌─────────────────────────────────────────────────────────┐
│                    enhanced_codecell.py                  │
│  • EnhancedCodeCell (base class)                       │
│  • CellMembrane, Organelles                            │
│  • CellState enum                                      │
└────────────────────┬────────────────────────────────────┘
                     │ imports
        ┌────────────┴────────────┬─────────────────────┐
        ▼                         ▼                     ▼
┌───────────────────┐   ┌──────────────────┐  ┌──────────────────┐
│stem_cell_system.py│   │advanced_tissue.py │  │performance_metrics│
│ • StemCell        │   │ • AdvancedTissue  │  │ • MetricsCollector│
│ • StemCellBank    │   │ • Transaction     │  │ • CellMetrics    │
│ • Specialized     │   │ • Quarantine      │  │ • TissueMetrics  │
└───────────────────┘   └──────────┬────────┘  └──────────────────┘
                                   │
                                   ▼
                        ┌──────────────────┐
                        │auth_tissue_demo.py│
                        │ • Demo application│
                        │ • Real example    │
                        └──────────────────┘
```

## 📦 Modül Detayları

### 1. **enhanced_codecell.py** (Core Foundation)
```python
# Ana bileşenler:
- EnhancedCodeCell: Temel hücre sınıfı
- CellMembrane: Hücre zarı (interface control)
- Organelles: Mitochondria, Nucleus, Lysosome
- CellState: Hücre durumları enum

# Kullanım:
from core.enhanced_codecell import EnhancedCodeCell, CellState
```

### 2. **advanced_codetissue.py** (Container Layer)
```python
# Ana bileşenler:
- AdvancedCodeTissue: Cell container
- TissueTransaction: Atomik operasyonlar
- Quarantine sistemi
- Dependency injection

# Bağımlılıklar:
- enhanced_codecell.py

# Kullanım:
from core.advanced_codetissue import AdvancedCodeTissue
```

### 3. **stem_cell_system.py** (Template & Banking)
```python
# Ana bileşenler:
- StemCell: Farklılaşabilen hücreler
- StemCellBank: Template storage
- Specialized cells: NeuronCell, MuscleCell, ImmuneCell

# Bağımlılıklar:
- enhanced_codecell.py

# Kullanım:
from core.stem_cell_system import StemCell, StemCellBank
```

### 4. **performance_metrics.py** (Monitoring)
```python
# Ana bileşenler:
- MetricsCollector: Metrik toplama
- CellMetrics: Cell-level metrics
- TissueMetrics: Tissue-level metrics
- MetricsDashboard: Merkezi dashboard

# Bağımlılıklar:
- Bağımsız modül

# Kullanım:
from monitoring.performance_metrics import CellMetrics, TissueMetrics
```

### 5. **auth_tissue_demo.py** (Example)
```python
# Ana bileşenler:
- LoginCell, TokenCell, PermissionCell
- Demo authentication flow

# Bağımlılıklar:
- enhanced_codecell.py
- advanced_codetissue.py
- pyjwt (external)

# Kullanım:
python examples/auth_tissue_demo.py
```

## 🔄 Import İlişkileri

```python
# Doğru import sırası ve örnekler:

# 1. Base imports
from core.enhanced_codecell import EnhancedCodeCell, CellState, CellMembrane

# 2. Container imports
from core.advanced_codetissue import AdvancedCodeTissue, TissueTransaction

# 3. Specialized imports
from core.stem_cell_system import StemCell, StemCellBank, NeuronCell

# 4. Monitoring imports
from monitoring.performance_metrics import CellMetrics, TissueMetrics, MetricsDashboard

# 5. Example usage
from examples.auth_tissue_demo import authentication_tissue_demo
```

## 🎯 Modül Sorumlulukları

### Core Layer (Temel Katman)
| Modül | Sorumluluk | Bağımlılık |
|-------|------------|------------|
| enhanced_codecell | Cell tanımı ve yaşam döngüsü | None |
| advanced_codetissue | Cell organizasyonu ve koordinasyon | enhanced_codecell |
| stem_cell_system | Template yönetimi ve farklılaşma | enhanced_codecell |

### Monitoring Layer (İzleme Katmanı)
| Modül | Sorumluluk | Bağımlılık |
|-------|------------|------------|
| performance_metrics | Metrik toplama ve raporlama | None |

### Application Layer (Uygulama Katmanı)
| Modül | Sorumluluk | Bağımlılık |
|-------|------------|------------|
| auth_tissue_demo | Örnek authentication uygulaması | core + pyjwt |

## 🔧 Modül Kullanım Örnekleri

### Basit Cell Oluşturma
```python
from core.enhanced_codecell import EnhancedCodeCell

# Basit cell
cell = EnhancedCodeCell("my_cell", cell_type="generic")
print(cell.get_health_report())
```

### Tissue Oluşturma
```python
from core.advanced_codetissue import AdvancedCodeTissue
from core.enhanced_codecell import EnhancedCodeCell

# Tissue oluştur
tissue = AdvancedCodeTissue("MyTissue")

# Cell tipi kaydet
tissue.register_cell_type(EnhancedCodeCell)

# Cell grow et
cell = tissue.grow_cell("cell_1", "EnhancedCodeCell")
```

### Stem Cell Kullanımı
```python
from core.stem_cell_system import StemCell, NeuronCell

# Stem cell oluştur
stem = StemCell("stem_001")

# Farklılaştır
neuron = stem.differentiate(NeuronCell)
```

### Metrics Entegrasyonu
```python
from monitoring.performance_metrics import CellMetrics, monitor_performance

# Cell metrics
metrics = CellMetrics("my_cell")

# Decorator kullanımı
@monitor_performance(metrics, "my_operation")
def my_operation():
    # İşlem kodları
    pass
```

## 🚀 Yeni Modül Ekleme Rehberi

1. **Modül Yerleşimi**: Uygun dizine yerleştir
   - Core functionality → `core/`
   - Monitoring → `monitoring/`
   - Examples → `examples/`

2. **Import Yapısı**: Circular import'tan kaçın
   ```python
   # ✅ Doğru
   from core.enhanced_codecell import EnhancedCodeCell
   
   # ❌ Yanlış (circular import)
   # enhanced_codecell.py içinde:
   from core.advanced_codetissue import AdvancedCodeTissue
   ```

3. **Bağımlılık Yönetimi**: Minimal bağımlılık ilkesi
   - Core modüller bağımsız olmalı
   - Container'lar core'a bağımlı olabilir
   - Application layer her şeye bağımlı olabilir

4. **Test Dosyası**: Her modül için test ekle
   ```python
   # tests/test_my_module.py
   import pytest
   from core.my_module import MyClass
   
   def test_my_class():
       instance = MyClass()
       assert instance is not None
   ```

## 📋 Modül Checklist

- [ ] **enhanced_codecell.py**: Cell base implementation ✅
- [ ] **advanced_codetissue.py**: Tissue container ✅
- [ ] **stem_cell_system.py**: Template system ✅
- [ ] **performance_metrics.py**: Monitoring ✅
- [ ] **auth_tissue_demo.py**: Working example ✅
- [ ] **code_organ.py**: Module layer (TODO)
- [ ] **code_system.py**: System layer (TODO)
- [ ] **code_human.py**: API layer (TODO)

## 🎨 Best Practices

1. **Single Responsibility**: Her modül tek bir sorumluluğa sahip olmalı
2. **Clear Interfaces**: Public API'ler net tanımlı olmalı
3. **Type Hints**: Tüm fonksiyonlarda type hint kullan
4. **Documentation**: Her modül ve sınıf docstring içermeli
5. **Testing**: %80+ test coverage hedefle