# 🧬 BioCode - Living Code Architecture

### *Where Code Comes Alive*

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 📋 İçindekiler
1. [Konsept Tanıtım](#konsept-tanıtım)
2. [Mimari Yapı](#mimari-yapı)
3. [Çalışan Örnek](#çalışan-örnek)
4. [Kullanım Kılavuzu](#kullanım-kılavuzu)
5. [Gelecek Adımlar](#gelecek-adımlar)

---

## 🧪 Konsept Tanıtım

**BioCode**, yazılım mimarisine **biyolojik organizma** yaklaşımı getiren devrim niteliğinde bir framework'tür. Geleneksel class/module yapısı yerine, kodunuz canlı hücreler (cells), dokular (tissues), organlar (organs) ve sistemler (systems) olarak organize edilir - tıpkı gerçek bir organizma gibi!

### 🎯 Neden Bu Yaklaşım?

1. **Self-Healing**: Kodun kendini iyileştirme yeteneği
2. **Dynamic Growth**: Runtime'da yeni özellikler eklenebilmesi
3. **Organic Communication**: Bileşenler arası doğal iletişim
4. **Health Monitoring**: Kod sağlığının sürekli takibi
5. **Isolation & Recovery**: Hatalı bileşenlerin izolasyonu ve iyileştirilmesi

---

## 🏗️ Mimari Yapı

### 1️⃣ CodeCell (Temel Birim - Class)
```python
# Her class bir hücre gibi davranır
class CodeCell:
    - DNA (unique genetic code)
    - Health Score (0-100)
    - Mutations tracking
    - Self-healing ability
    - Cell division (instance creation)
    - Infection & immune response
```

**Özellikler:**
- Her cell'in benzersiz bir DNA'sı var (class source code hash)
- Health score ile sağlık durumu takibi
- Mutation'lar kaydediliyor
- Hata durumunda infection state'e geçiş
- Self-healing mekanizması

### 2️⃣ CodeTissue (Multi-Class Container)
```python
# Birden fazla cell'i organize eden doku yapısı
class AdvancedCodeTissue:
    - Cell registry & type management
    - Inter-cell communication
    - Quarantine system
    - Transaction support
    - Performance metrics
    - Dependency injection
```

**Özellikler:**
- Runtime'da yeni cell tipleri eklenebilir
- Cell'ler arası mesajlaşma protokolü
- Enfekte cell'leri karantinaya alma
- Atomik operasyonlar için transaction desteği
- Performans metrikleri (throughput, latency, error rate)
- Dependency injection container

### 3️⃣ CodeOrgan (Module)
```python
# Birden fazla tissue'dan oluşan organ
class CodeOrgan:
    - tissues: Dict[str, AdvancedCodeTissue]
    - data_flow_controller: DataFlowController
    - compatibility_type: CompatibilityType
    - health_monitoring: OrganHealth
    
    def add_tissue(...)
    def predict_failure(...)
    def hot_swap_tissue(...)
    def prepare_for_transplant(...)
```

**Özellikler:**
- **DataFlowController**: Kanal bazlı veri akışı, backpressure yönetimi
- **BloodTypeCompatibility**: Organ uyumluluk kontrolü (A, B, AB, O)
- **OrganHealth**: Blood flow, oxygen level, toxin level takibi
- **Hot-swap**: Runtime'da tissue değiştirme
- **Failure Prediction**: Proaktif hata tahmini

### 4️⃣ CodeSystem (System)
```python
# Organların oluşturduğu sistem
class CodeSystem:
    - organs: Dict[str, CodeOrgan]
    - neural_ai: SystemAI
    - memory: SystemMemory
    - circadian: CircadianScheduler
    - consciousness_level: ConsciousnessLevel
    
    def add_organ(...)
    def broadcast(...)
    def self_diagnose(...)
    def optimize(...)
```

**Özellikler:**
- **SystemAI**: Neural pathway learning, pattern recognition
- **SystemMemory**: Short-term, long-term, working memory
- **CircadianScheduler**: Peak/off-peak/sleep phase management
- **ConsciousnessLevel**: Dormant → Awakening → Aware → Focused → Hyperaware → Dreaming
- **Dream State**: Deep optimization ve memory consolidation

### 🧪 Tissue Components
```python
# ExtracellularMatrix (ECM)
- Shared resources ve standards
- Security barriers
- Connective proteins (utilities)
- Matrix health (integrity, viscosity, permeability)

# HomeostasisController
- Parameter balance maintenance
- Feedback loops
- Auto-regulation

# VascularizationSystem
- Resource distribution channels
- Flow rate control
- Pressure management
```

---

## 🚀 Çalışan Örnek: Authentication Tissue

### Kurulum
```bash
# Gerekli bağımlılığı yükle
pip install -r config/requirements.txt

# Demo'yu çalıştır
python examples/auth_tissue_demo.py

# Veya basit kullanım örneği
python examples/basic_usage.py
```

### Örnek Senaryo

Authentication Tissue, 3 farklı cell tipinden oluşur:

1. **LoginCell**: Kullanıcı giriş işlemleri
   - Username/password doğrulama
   - Failed attempt tracking
   - Account lockout mekanizması

2. **TokenCell**: JWT token yönetimi
   - Token üretimi
   - Token doğrulama
   - Token iptal etme

3. **PermissionCell**: Yetki kontrolü
   - Role-based permissions
   - Permission checking

### Demo Akışı

```python
# 1. Tissue oluştur
auth_tissue = AdvancedCodeTissue("AuthenticationTissue")

# 2. Cell tiplerini kaydet
auth_tissue.register_cell_type(LoginCell)
auth_tissue.register_cell_type(TokenCell)
auth_tissue.register_cell_type(PermissionCell)

# 3. Cell'leri grow et
login_cell = auth_tissue.grow_cell("main_login", "LoginCell")
token_cell = auth_tissue.grow_cell("jwt_handler", "TokenCell")
perm_cell = auth_tissue.grow_cell("permission_checker", "PermissionCell")

# 4. Cell'leri bağla
auth_tissue.connect_cells("main_login", "jwt_handler")
auth_tissue.connect_cells("jwt_handler", "permission_checker")
```

### Demo Çıktısı
```
🧬 Authentication Tissue Demo Starting...

✅ Tissue Created Successfully!
Active Cells: 3

🔐 Testing Authentication Flow...
Login Result: {'success': True, 'user_id': '123', ...}
Token Generated: eyJ0eXAiOiJKV1QiLCJhbGc...
Token Verification: Valid=True
Can Delete: True
User Permissions: ['admin', 'write', 'delete', 'read']

🦠 Testing Error Handling...
Attempt 1-3: Invalid credentials
Attempt 4: Account locked!

📊 Tissue Diagnostics:
Health Score: 100.0
Infected Cells: 1 (login cell infected due to errors)
Cell States: {'main_login': 'infected', 'jwt_handler': 'healthy', ...}
```

---

## 📚 Kullanım Kılavuzu

### 1. Yeni Cell Tipi Oluşturma

```python
from src.core.enhanced_codecell import EnhancedCodeCell

class MyCustomCell(EnhancedCodeCell):
    def __init__(self, name: str, **kwargs):
        super().__init__(name)
        # Cell'e özel özellikler
        
    async def my_operation(self, data: Any) -> Any:
        try:
            # İşlem yap
            return result
        except Exception as e:
            self.infect(e)  # Hata durumunda enfekte ol
            raise
```

### 2. Tissue'ya Cell Ekleme

```python
from src.core.advanced_codetissue import AdvancedCodeTissue

# Tissue oluştur
my_tissue = AdvancedCodeTissue("MyTissue")

# Cell tipini kaydet
my_tissue.register_cell_type(MyCustomCell)

# Dependency inject et (opsiyonel)
my_tissue.inject_dependency('db_connection', db)

# Cell grow et
cell = my_tissue.grow_cell("cell_1", "MyCustomCell")
```

### 3. Cell'ler Arası İletişim

```python
# Sinyal gönder
await my_tissue.send_signal(
    from_cell="cell_1",
    to_cell="cell_2", 
    signal={'type': 'data', 'content': 'Hello'}
)
```

### 4. Transaction Kullanımı

```python
with my_tissue.transaction("critical_operation") as tx:
    # Atomik operasyonlar
    tx.affected_cells.add("cell_1")
    tx.affected_cells.add("cell_2")
    
    # Operasyonları gerçekleştir
    # Hata durumunda otomatik rollback
```

### 5. Health Monitoring

```python
# Tissue diagnostics
diagnostics = my_tissue.get_tissue_diagnostics()
print(f"Health: {diagnostics['metrics']['health_score']}")
print(f"Error Rate: {diagnostics['metrics']['error_rate']}")
print(f"Quarantined: {diagnostics['quarantine']}")
```

---

## 🔮 Gelecek Adımlar

### CodeOrgan İmplementasyonu
- Multiple tissue coordination
- Organ-level health monitoring
- Hot-swappable organs
- Inter-organ communication protocols

### CodeSystem İmplementasyonu
- System-wide consciousness
- Memory consolidation
- Background optimization (dream states)
- Self-learning capabilities

### CodeHuman (Production API)
- Complete organism
- Personality traits
- Social intelligence (multi-API coordination)
- Experience-based learning

---

## 🏃 Hızlı Başlangıç

```bash
# 1. Projeyi klonla
git clone https://github.com/umityigitbsrn/biocode.git
cd biocode

# 2. Bağımlılıkları yükle
pip install -r config/requirements.txt

# 3. Demo'yu çalıştır
python examples/auth_tissue_demo.py

# 4. Basit örneği dene
python examples/basic_usage.py

# 5. Kendi tissue'nu oluştur!
```

### 🎯 Pip ile Kurulum (Yakında)

```bash
pip install biocode

# Tüm özelliklerle
pip install biocode[all]
```

---

## 📁 Dosya Yapısı

```
Code-Snippet/
├── 📄 README.md                    # Ana dokümantasyon
├── 📋 FOLDER_STRUCTURE.md          # Detaylı klasör yapısı
│
├── 🔧 config/                      # Konfigürasyon dosyaları
│   ├── requirements.txt            # Python bağımlılıkları
│   └── setup.py                    # Paket kurulum dosyası
│
├── 📚 docs/                        # Dokümantasyon
│   ├── architecture_diagram.md     # Mimari diyagramlar
│   ├── ASYNC_STYLE_GUIDE.md       # Async/Sync rehberi
│   ├── biological_features_analysis.md
│   ├── dashboard_examples.md       # Dashboard örnekleri
│   ├── INSTALL.md                  # Kurulum kılavuzu
│   └── PROJECT_STRUCTURE.md        # Proje yapısı
│
├── 🔬 examples/                    # Örnek uygulamalar
│   ├── auth_tissue_demo.py         # Authentication demo
│   └── basic_usage.py              # Basit kullanım örneği
│
├── 🧬 src/                         # Kaynak kodlar
│   ├── core/                       # Çekirdek bileşenler
│   │   ├── enhanced_codecell.py    # CodeCell
│   │   ├── advanced_codetissue.py  # CodeTissue
│   │   ├── stem_cell_system.py     # Stem cells
│   │   ├── code_organ.py           # CodeOrgan
│   │   └── code_system.py          # CodeSystem
│   │
│   ├── components/                 # Destek bileşenleri
│   │   ├── tissue_components.py    # ECM, Homeostasis
│   │   └── system_managers.py      # System managers
│   │
│   ├── monitoring/                 # İzleme sistemi
│   │   └── performance_metrics.py  # Metrics & dashboard
│   │
│   └── security/                   # Güvenlik
│       └── security_manager.py     # Dynamic security
│
└── 🧪 tests/                       # Test suite
    └── __init__.py
```

---

## 🎯 Sonuç

**BioCode** ile kodunuz artık sadece statik bir yapı değil - yaşayan, nefes alan, kendini iyileştiren bir organizma! Cell'ler hastalanabilir, iyileşebilir, birbirleriyle iletişim kurabilir ve tissue olarak organize bir şekilde çalışabilir.

**"We don't write code, we grow it!"** 🌱

---

## 🤝 Katkıda Bulunun

BioCode açık kaynaklı bir projedir ve katkılarınızı bekliyoruz!

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'e push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🙏 Teşekkürler

- Biyolojik sistem mimarisi için ilham veren doğaya
- Açık kaynak topluluğuna
- Tüm katkıda bulunanlara

---

<p align="center">
  Made with ❤️ by the BioCode Team<br>
  <em>Where Code Comes Alive</em>
</p>