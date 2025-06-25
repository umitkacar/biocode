"""
Digital Evolution Demo - Simple examples for all concepts
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.evolution.digital_life import (
    DigitalDNA, SelfReplicatingCell, ApoptoticCell, 
    AdaptiveCell, HiveMindCell, CollectiveIntelligence,
    EvolutionSimulator
)
import time
import random


def demo_evolution():
    """1. EVRIM - Kodlar çoğalıyor ve mutasyona uğruyor"""
    print("\n=== 1. EVRİM DEMO ===")
    
    # Ana hücre oluştur
    parent = SelfReplicatingCell()
    print(f"Ana hücre: {parent.id}")
    print(f"DNA: {parent.dna.genes['behavior']}, Gen: {parent.dna.generation}")
    
    # 5 çocuk üret
    children = []
    for i in range(5):
        child = parent.mitosis()
        if child:
            children.append(child)
            print(f"Çocuk {i+1}: {child.id}, Davranış: {child.dna.genes['behavior']}, Gen: {child.dna.generation}")


def demo_adaptation():
    """2. ADAPTASYON - Kod ortama uyum sağlıyor"""
    print("\n=== 2. ADAPTASYON DEMO ===")
    
    cell = AdaptiveCell()
    print(f"Başlangıç davranışı: {cell.dna.genes['behavior']}")
    print(f"Başlangıç metabolizması: {cell.dna.genes['metabolism']}")
    
    # Ortamı algıla ve adapte ol
    env = cell.sense_environment()
    print(f"\nOrtam: CPU: {env['cpu_percent']}%, Bellek: {env['memory_percent']}%")
    
    cell.adapt_to_environment()
    print(f"Adaptasyon sonrası davranış: {cell.dna.genes['behavior']}")
    print(f"Adaptasyon sonrası metabolizma: {cell.dna.genes['metabolism']}")


def demo_collective_intelligence():
    """3. KOLEKTİF ZEKA - Hücreler bilgi paylaşıyor"""
    print("\n=== 3. KOLEKTİF ZEKA DEMO ===")
    
    # İki hücre oluştur
    cell1 = HiveMindCell()
    cell2 = HiveMindCell()
    
    print(f"Hücre 1: {cell1.id}")
    print(f"Hücre 2: {cell2.id}")
    
    # Hücre 1 bir keşif paylaşıyor
    cell1.share_discovery('food_source', {'location': 'kuzey', 'miktar': 100})
    print(f"\nHücre 1 besin kaynağı keşfetti ve paylaştı")
    
    # Hücre 2 tehlike sinyali veriyor
    cell2.signal_danger('predator')
    print(f"Hücre 2 tehlike sinyali verdi")
    
    # Hücre 1 koloniden öğreniyor
    cell1.learn_from_others()
    print(f"\nHücre 1 koloniden öğrendi")
    
    # Feromon seviyeleri
    pheromones = CollectiveIntelligence.sense_pheromones()
    print(f"Feromon seviyeleri: {pheromones}")


def demo_file_system_replication():
    """4. DOSYA SİSTEMİ - Hücre kendini dosya olarak çoğaltıyor"""
    print("\n=== 4. DOSYA SİSTEMİ DEMO ===")
    
    cell = SelfReplicatingCell()
    print(f"Ana hücre: {cell.id}")
    
    # Dosyaya kaydet
    child = cell.mitosis(save_to_file=True)
    if child:
        print(f"Çocuk hücre dosyaya kaydedildi: {child.id}")
        print("Kontrol edin: digital_life_forms/ klasörü")


def demo_memory_replication():
    """5. BELLEK (RAM) - Sadece bellekte çoğalma"""
    print("\n=== 5. BELLEK DEMO ===")
    
    # Hafif siklet hücreler - sadece bellekte
    cells = []
    parent = SelfReplicatingCell()
    cells.append(parent)
    
    print(f"Başlangıç: 1 hücre")
    
    # 3 nesil çoğalma
    for gen in range(3):
        new_cells = []
        for cell in cells:
            child = cell.mitosis(save_to_file=False)  # Dosyaya kaydetme
            if child:
                new_cells.append(child)
        cells.extend(new_cells)
        print(f"Nesil {gen+1}: {len(cells)} hücre (sadece RAM'de)")


def demo_visualization():
    """6. GÖRSELLEŞTİRME - Popülasyon istatistikleri"""
    print("\n=== 6. GÖRSELLEŞTİRME DEMO ===")
    
    # Mini popülasyon oluştur
    population = [HiveMindCell() for _ in range(10)]
    
    # Davranış dağılımı
    behaviors = {}
    for cell in population:
        b = cell.dna.genes['behavior']
        behaviors[b] = behaviors.get(b, 0) + 1
    
    print("Popülasyon Davranış Dağılımı:")
    for behavior, count in behaviors.items():
        print(f"  {behavior}: {'█' * count} ({count})")
    
    # Metabolizma dağılımı
    metabolisms = {}
    for cell in population:
        m = cell.dna.genes['metabolism']
        metabolisms[m] = metabolisms.get(m, 0) + 1
    
    print("\nPopülasyon Metabolizma Dağılımı:")
    for metabolism, count in metabolisms.items():
        print(f"  {metabolism}: {'█' * count} ({count})")


def demo_background_simulation():
    """7. ARKA PLAN SİMÜLASYONU - Evrim döngüsü"""
    print("\n=== 7. ARKA PLAN SİMÜLASYONU DEMO ===")
    
    # Küçük bir simülasyon
    sim = EvolutionSimulator(initial_population=5)
    
    print("5 hücre ile başlıyoruz...")
    
    # 5 nesil simüle et
    for i in range(5):
        sim.run_generation()
        
        if sim.population:
            print(f"\nNesil {i+1}:")
            print(f"  Popülasyon: {len(sim.population)} hücre")
            
            # En yaygın davranış
            behaviors = {}
            for cell in sim.population:
                b = cell.dna.genes['behavior']
                behaviors[b] = behaviors.get(b, 0) + 1
            
            if behaviors:
                dominant = max(behaviors, key=behaviors.get)
                print(f"  Baskın davranış: {dominant}")
        else:
            print(f"\nNesil {i+1}: Popülasyon yok oldu!")
            break


def demo_apoptosis():
    """8. APOPTOZİS - Programlı hücre ölümü"""
    print("\n=== 8. APOPTOZİS DEMO ===")
    
    cell = ApoptoticCell()
    print(f"Hücre {cell.id} oluşturuldu")
    print(f"Başlangıç durumu: {cell.state}")
    
    # Ölüm sinyalleri gönder
    print("\nÖlüm sinyalleri gönderiliyor...")
    cell.receive_death_signal("DNA hasarı")
    cell.receive_death_signal("Oksijen eksikliği")
    cell.receive_death_signal("Toksin maruziyeti")
    
    print(f"Son durum: {cell.state}")
    print("Genetik hafıza kaydedildi: genetic_memory/ klasörü")


def main():
    """Tüm demolari çalıştır"""
    print("BioCode Digital Life - Basit Örnekler")
    print("=" * 50)
    
    demos = [
        ("Evrim", demo_evolution),
        ("Adaptasyon", demo_adaptation),
        ("Kolektif Zeka", demo_collective_intelligence),
        ("Dosya Sistemi", demo_file_system_replication),
        ("Bellek", demo_memory_replication),
        ("Görselleştirme", demo_visualization),
        ("Simülasyon", demo_background_simulation),
        ("Apoptozis", demo_apoptosis)
    ]
    
    for name, demo_func in demos:
        try:
            demo_func()
            time.sleep(1)  # Demoları ayırmak için
        except Exception as e:
            print(f"\n{name} demo hatası: {e}")
    
    print("\n" + "=" * 50)
    print("Demo tamamlandı!")


if __name__ == "__main__":
    main()