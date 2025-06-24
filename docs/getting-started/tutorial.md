# BioCode Tutorial: Building a Living Application

This tutorial will guide you through building a complete application using BioCode's biological architecture. We'll create a simple web scraper that demonstrates self-healing, adaptation, and organic growth.

## Table of Contents

1. [Understanding the Biology](#understanding-the-biology)
2. [Building the Scraper](#building-the-scraper)
3. [Adding Self-Healing](#adding-self-healing)
4. [Implementing Adaptation](#implementing-adaptation)
5. [System Evolution](#system-evolution)

## Understanding the Biology

BioCode uses biological metaphors to create resilient, adaptive software:

- **Cells**: Basic units of computation
- **Tissues**: Collections of cells working together
- **Organs**: Specialized tissue groups with specific functions
- **Systems**: Complete organisms with consciousness and learning

## Building the Scraper

Let's build a web scraper that can heal itself and adapt to changes.

### Step 1: Create Specialized Cells

```python
from biocode.core import EnhancedCodeCell
import aiohttp
import asyncio
from bs4 import BeautifulSoup

class FetcherCell(EnhancedCodeCell):
    """Cell specialized in fetching web content"""
    
    def __init__(self, name: str):
        super().__init__(name, cell_type="fetcher")
        self.session = None
        
    async def initialize(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def fetch_url(self, url: str) -> str:
        """Fetch content from URL"""
        try:
            async with self.session.get(url) as response:
                content = await response.text()
                self.operations_count += 1
                return content
        except Exception as e:
            self.infect(e)
            raise
            
    async def cleanup(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()

class ParserCell(EnhancedCodeCell):
    """Cell specialized in parsing HTML"""
    
    def __init__(self, name: str):
        super().__init__(name, cell_type="parser")
        
    def parse_html(self, html: str, selector: str) -> list:
        """Parse HTML and extract data"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            elements = soup.select(selector)
            self.operations_count += 1
            return [elem.text.strip() for elem in elements]
        except Exception as e:
            self.infect(e)
            raise

class StorageCell(EnhancedCodeCell):
    """Cell specialized in storing data"""
    
    def __init__(self, name: str):
        super().__init__(name, cell_type="storage")
        self.data_store = []
        
    def store_data(self, data: list):
        """Store parsed data"""
        try:
            self.data_store.extend(data)
            self.operations_count += 1
            return len(self.data_store)
        except Exception as e:
            self.infect(e)
            raise
```

### Step 2: Create a Scraper Tissue

```python
from biocode.core import AdvancedCodeTissue

class ScraperTissue(AdvancedCodeTissue):
    """Tissue for web scraping operations"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self._setup_cells()
        
    def _setup_cells(self):
        """Set up specialized cells"""
        # Register cell types
        self.register_cell_type(FetcherCell)
        self.register_cell_type(ParserCell)
        self.register_cell_type(StorageCell)
        
        # Grow cells
        self.fetcher = self.grow_cell("fetcher_1", "FetcherCell")
        self.parser = self.grow_cell("parser_1", "ParserCell")
        self.storage = self.grow_cell("storage_1", "StorageCell")
        
        # Connect cells in a pipeline
        self.connect_cells("fetcher_1", "parser_1")
        self.connect_cells("parser_1", "storage_1")
        
    async def scrape_url(self, url: str, selector: str) -> int:
        """Scrape URL and store results"""
        with self.transaction(f"scrape_{url}") as tx:
            try:
                # Initialize fetcher
                await self.fetcher.initialize()
                
                # Fetch content
                html = await self.fetcher.fetch_url(url)
                
                # Parse content
                data = self.parser.parse_html(html, selector)
                
                # Store data
                count = self.storage.store_data(data)
                
                # Clean up
                await self.fetcher.cleanup()
                
                return count
                
            except Exception as e:
                # Transaction will rollback automatically
                self.logger.error(f"Scraping failed: {e}")
                raise
```

### Step 3: Create a Scraper Organ

```python
from biocode.core import CodeOrgan, OrganType, CompatibilityType

class ScraperOrgan(CodeOrgan):
    """Organ for managing multiple scraper tissues"""
    
    def __init__(self, name: str):
        super().__init__(
            name,
            OrganType.PROCESSING,
            CompatibilityType.TYPE_A
        )
        self.url_queue = asyncio.Queue()
        self.results = []
        
    async def add_scraper_tissue(self, tissue_name: str):
        """Add a new scraper tissue"""
        tissue = ScraperTissue(tissue_name)
        self.add_tissue(tissue)
        
    async def queue_url(self, url: str, selector: str):
        """Queue URL for scraping"""
        await self.url_queue.put((url, selector))
        
    async def process_queue(self):
        """Process URLs from queue"""
        while not self.url_queue.empty():
            url, selector = await self.url_queue.get()
            
            # Find healthy tissue
            for tissue in self.tissues.values():
                if tissue.calculate_tissue_health() > 80:
                    try:
                        count = await tissue.scrape_url(url, selector)
                        self.results.append({
                            'url': url,
                            'count': count,
                            'tissue': tissue.name
                        })
                        break
                    except Exception as e:
                        self.logger.error(f"Tissue {tissue.name} failed: {e}")
                        continue
```

## Adding Self-Healing

### Step 4: Implement Recovery Mechanisms

```python
class ResilientFetcherCell(FetcherCell):
    """Fetcher cell with self-healing capabilities"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.retry_count = 3
        self.timeout = 30
        
    async def fetch_url(self, url: str) -> str:
        """Fetch with retry and healing"""
        for attempt in range(self.retry_count):
            try:
                timeout = aiohttp.ClientTimeout(total=self.timeout)
                async with self.session.get(url, timeout=timeout) as response:
                    if response.status == 200:
                        content = await response.text()
                        self.heal(10)  # Successful fetch heals the cell
                        return content
                    else:
                        raise Exception(f"HTTP {response.status}")
                        
            except Exception as e:
                self.infect(e)
                self.stress_level += 20
                
                # Try to heal before next attempt
                if attempt < self.retry_count - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    self.heal(5)
                else:
                    # Final attempt failed
                    if self.health_score < 30:
                        self.trigger_apoptosis()  # Cell death
                    raise

class AdaptiveScraperTissue(ScraperTissue):
    """Tissue that adapts to failures"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.failure_threshold = 3
        self.failures = 0
        
    async def scrape_url(self, url: str, selector: str) -> int:
        """Scrape with adaptation"""
        try:
            result = await super().scrape_url(url, selector)
            self.failures = 0  # Reset on success
            return result
            
        except Exception as e:
            self.failures += 1
            
            if self.failures >= self.failure_threshold:
                # Adapt by growing new cells
                await self._regenerate_cells()
                
            raise
            
    async def _regenerate_cells(self):
        """Regenerate damaged cells"""
        # Find and remove dead cells
        dead_cells = [
            name for name, cell in self.cells.items()
            if cell.state.value == "dead"
        ]
        
        for cell_name in dead_cells:
            del self.cells[cell_name]
            
        # Grow new cells
        if "fetcher_1" in dead_cells:
            self.fetcher = self.grow_cell("fetcher_2", "ResilientFetcherCell")
            self.connect_cells("fetcher_2", "parser_1")
```

## Implementing Adaptation

### Step 5: Add Learning Capabilities

```python
from biocode.core import CodeSystem
import json

class LearningScraper(CodeSystem):
    """Scraper system that learns from experience"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.scraper_organ = ScraperOrgan("main_scraper")
        self.add_organ(self.scraper_organ)
        self.pattern_memory = {}
        
    async def learn_from_failure(self, url: str, error: Exception):
        """Learn from scraping failures"""
        domain = url.split('/')[2]
        
        # Record failure pattern
        self.neural_ai.observe_pattern(
            "failure_pattern",
            {
                "domain": domain,
                "error_type": type(error).__name__,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Adapt strategy
        if domain not in self.pattern_memory:
            self.pattern_memory[domain] = {"failures": 0, "strategy": "default"}
            
        self.pattern_memory[domain]["failures"] += 1
        
        # Change strategy after multiple failures
        if self.pattern_memory[domain]["failures"] > 5:
            self.pattern_memory[domain]["strategy"] = "careful"
            await self._adapt_scraping_strategy(domain, "careful")
            
    async def _adapt_scraping_strategy(self, domain: str, strategy: str):
        """Adapt scraping strategy for domain"""
        if strategy == "careful":
            # Create specialized tissue for difficult domains
            tissue_name = f"careful_scraper_{domain.replace('.', '_')}"
            careful_tissue = AdaptiveScraperTissue(tissue_name)
            
            # Configure for careful scraping
            careful_tissue.fetcher.timeout = 60  # Longer timeout
            careful_tissue.fetcher.retry_count = 5  # More retries
            
            await self.scraper_organ.add_tissue(careful_tissue)
            
    async def intelligent_scrape(self, urls: list, selector: str):
        """Scrape URLs with learning"""
        results = []
        
        for url in urls:
            domain = url.split('/')[2]
            
            # Check if we have learned patterns for this domain
            if domain in self.pattern_memory:
                strategy = self.pattern_memory[domain]["strategy"]
                self.logger.info(f"Using {strategy} strategy for {domain}")
                
            try:
                # Queue for processing
                await self.scraper_organ.queue_url(url, selector)
                
            except Exception as e:
                # Learn from failure
                await self.learn_from_failure(url, e)
                
        # Process all queued URLs
        await self.scraper_organ.process_queue()
        
        return self.scraper_organ.results
```

## System Evolution

### Step 6: Enable System Evolution

```python
class EvolvingScraperSystem(LearningScraper):
    """Scraper that evolves over time"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.generation = 1
        self.fitness_scores = []
        
    async def evaluate_fitness(self):
        """Evaluate system fitness"""
        total_ops = sum(
            cell.operations_count 
            for organ in self.organs.values()
            for tissue in organ.tissues.values()
            for cell in tissue.cells.values()
        )
        
        total_errors = sum(
            cell.error_count
            for organ in self.organs.values()
            for tissue in organ.tissues.values()
            for cell in tissue.cells.values()
        )
        
        # Calculate fitness score
        if total_ops > 0:
            fitness = (total_ops - total_errors) / total_ops
        else:
            fitness = 0
            
        self.fitness_scores.append({
            'generation': self.generation,
            'fitness': fitness,
            'timestamp': datetime.now()
        })
        
        return fitness
        
    async def evolve(self):
        """Evolve to next generation"""
        fitness = await self.evaluate_fitness()
        
        if fitness < 0.7:
            # Low fitness - major evolution needed
            await self._major_evolution()
        elif fitness < 0.9:
            # Medium fitness - minor adjustments
            await self._minor_evolution()
            
        self.generation += 1
        
    async def _major_evolution(self):
        """Major evolutionary changes"""
        # Replace poorly performing organs
        for organ_name, organ in list(self.organs.items()):
            organ_fitness = await self._calculate_organ_fitness(organ)
            
            if organ_fitness < 0.5:
                # Remove and replace organ
                self.remove_organ(organ_name)
                
                # Create evolved version
                new_organ = ScraperOrgan(f"{organ_name}_gen{self.generation}")
                
                # Apply evolutionary improvements
                new_organ.data_flow_controller.max_buffer_size *= 2
                new_organ.data_flow_controller.backpressure_threshold = 0.9
                
                self.add_organ(new_organ)
                
    async def _minor_evolution(self):
        """Minor evolutionary adjustments"""
        # Optimize existing organs
        for organ in self.organs.values():
            # Increase efficiency of healthy tissues
            for tissue in organ.tissues.values():
                if tissue.calculate_tissue_health() > 90:
                    # Reward healthy tissues with more resources
                    for cell in tissue.cells.values():
                        cell.energy_level = min(100, cell.energy_level + 10)
```

## Putting It All Together

```python
async def main():
    # Create evolving scraper system
    scraper = EvolvingScraperSystem("bio_scraper")
    
    # Boot the system
    await scraper.boot()
    
    # URLs to scrape
    urls = [
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3",
    ]
    
    # Scrape with learning
    results = await scraper.intelligent_scrape(urls, "h2.title")
    
    print(f"Scraped {len(results)} URLs")
    print(f"System fitness: {await scraper.evaluate_fitness()}")
    
    # Let system evolve based on performance
    await scraper.evolve()
    print(f"Evolved to generation {scraper.generation}")
    
    # Save learned patterns
    with open("scraper_memory.json", "w") as f:
        json.dump({
            "patterns": scraper.pattern_memory,
            "fitness": scraper.fitness_scores,
            "generation": scraper.generation
        }, f, indent=2)
    
    # Shutdown
    await scraper.shutdown()

# Run the scraper
if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Concepts

### Stem Cell Banking

```python
from biocode.core import StemCellBank

# Create stem cell bank
bank = StemCellBank("scraper_bank")

# Store successful cell templates
bank.store_template("resilient_fetcher", ResilientFetcherCell)
bank.store_template("adaptive_parser", ParserCell)

# Clone successful cells
new_fetcher = bank.create_cell_from_template(
    "resilient_fetcher", 
    "fetcher_clone_1"
)
```

### Immune System

```python
from biocode.security import SecurityManager, ThreatType

# Add immune system to scraper
security = SecurityManager("scraper_immune")

# Define threat patterns
security.add_threat_pattern({
    'pattern': r'captcha|cloudflare',
    'threat_type': ThreatType.BLOCKED,
    'action': 'switch_tissue'
})

# Monitor for threats
threat_detected = security.scan_content(html_content)
if threat_detected:
    # Immune response
    await tissue.quarantine_infected_cells()
```

## Best Practices

1. **Cell Specialization**: Keep cells focused on single responsibilities
2. **Tissue Cooperation**: Design tissues for specific workflows
3. **Organ Compatibility**: Use blood types to control organ interactions
4. **System Learning**: Let systems learn from both success and failure
5. **Evolution Strategy**: Balance stability with adaptability

## Exercises

1. **Add Caching**: Implement a caching cell to reduce redundant fetches
2. **Parallel Processing**: Modify the organ to process multiple URLs concurrently
3. **Error Analysis**: Create cells that analyze error patterns
4. **Performance Metrics**: Add monitoring for scraping performance
5. **Data Validation**: Implement validation cells to ensure data quality

## Summary

In this tutorial, we've built a complete web scraper using BioCode's biological architecture. The scraper can:

- **Self-heal** from errors
- **Adapt** to website changes
- **Learn** from experience
- **Evolve** to improve performance

This demonstrates how biological principles create more resilient and adaptive software systems.

## Next Steps

- Explore [Advanced Features](advanced-features.md)
- Read about [Security Patterns](security-patterns.md)
- Learn about [Performance Optimization](performance-guide.md)
- Check out more [Examples](../examples/)

Happy evolving! 🧬