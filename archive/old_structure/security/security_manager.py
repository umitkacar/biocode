import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class ThreatLevel(Enum):
    """Tehdit seviyeleri"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ThreatPattern:
    """Tehdit pattern tanımı"""

    pattern_id: str
    pattern_type: str  # sql_injection, xss, buffer_overflow, etc.
    regex: Optional[re.Pattern] = None
    keywords: List[str] = field(default_factory=list)
    severity: ThreatLevel = ThreatLevel.MEDIUM
    detected_count: int = 0
    last_detected: Optional[datetime] = None
    auto_expire: Optional[timedelta] = None

    def matches(self, data: Any) -> bool:
        """Check if data matches this pattern"""
        if isinstance(data, str):
            # Check regex
            if self.regex and self.regex.search(data):
                return True

            # Check keywords
            data_lower = data.lower()
            return any(keyword.lower() in data_lower for keyword in self.keywords)

        return False


@dataclass
class SecurityEvent:
    """Güvenlik olayı"""

    event_id: str
    threat_type: str
    threat_level: ThreatLevel
    source: str
    target: Optional[str]
    pattern_matched: Optional[str]
    timestamp: datetime
    blocked: bool
    details: Dict[str, Any] = field(default_factory=dict)


class DynamicSecurityManager:
    """Dynamic security pattern management"""

    def __init__(self, manager_name: str):
        self.manager_name = manager_name
        self.threat_patterns: Dict[str, ThreatPattern] = {}
        self.security_events: List[SecurityEvent] = []
        self.pattern_learning_enabled = True
        self.auto_pattern_threshold = 5  # Auto-create pattern after N detections
        self.suspicious_activity: Dict[str, int] = defaultdict(int)

        # Initialize base patterns
        self._initialize_base_patterns()

        # Pattern update callbacks
        self.pattern_update_callbacks: List[Callable] = []

        # Learning cache
        self.learning_cache: Dict[str, List[Any]] = defaultdict(list)

    def _initialize_base_patterns(self):
        """Initialize base security patterns"""
        # SQL Injection patterns
        self.add_pattern(
            ThreatPattern(
                pattern_id="sql_injection_basic",
                pattern_type="sql_injection",
                regex=re.compile(
                    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION)\b.*\b(FROM|INTO|WHERE)\b)",
                    re.IGNORECASE,
                ),
                keywords=["'; DROP TABLE", "' OR '1'='1", "UNION SELECT"],
                severity=ThreatLevel.HIGH,
            )
        )

        # XSS patterns
        self.add_pattern(
            ThreatPattern(
                pattern_id="xss_script_tag",
                pattern_type="xss",
                regex=re.compile(
                    r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL
                ),
                keywords=["<script>", "javascript:", "onerror="],
                severity=ThreatLevel.HIGH,
            )
        )

        # Command injection
        self.add_pattern(
            ThreatPattern(
                pattern_id="command_injection",
                pattern_type="command_injection",
                keywords=["; rm -rf", "| nc ", "&& wget", "`whoami`"],
                severity=ThreatLevel.CRITICAL,
            )
        )

        # Path traversal
        self.add_pattern(
            ThreatPattern(
                pattern_id="path_traversal",
                pattern_type="path_traversal",
                regex=re.compile(r"\.\.[\\/]"),
                keywords=["../../../", "..\\..\\..\\"],
                severity=ThreatLevel.MEDIUM,
            )
        )

    def add_pattern(self, pattern: ThreatPattern) -> bool:
        """Add new threat pattern"""
        if pattern.pattern_id in self.threat_patterns:
            return False

        self.threat_patterns[pattern.pattern_id] = pattern

        # Notify callbacks
        for callback in self.pattern_update_callbacks:
            callback("add", pattern)

        logging.info(f"Added threat pattern: {pattern.pattern_id}")
        return True

    def update_pattern(self, pattern_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing pattern"""
        if pattern_id not in self.threat_patterns:
            return False

        pattern = self.threat_patterns[pattern_id]

        # Update fields
        for key, value in updates.items():
            if hasattr(pattern, key):
                setattr(pattern, key, value)

        # Notify callbacks
        for callback in self.pattern_update_callbacks:
            callback("update", pattern)

        return True

    def remove_pattern(self, pattern_id: str) -> bool:
        """Remove threat pattern"""
        if pattern_id not in self.threat_patterns:
            return False

        pattern = self.threat_patterns.pop(pattern_id)

        # Notify callbacks
        for callback in self.pattern_update_callbacks:
            callback("remove", pattern)

        return True

    async def check_threat(
        self, data: Any, source: str, target: Optional[str] = None
    ) -> Optional[SecurityEvent]:
        """Check data against threat patterns"""
        for pattern in self.threat_patterns.values():
            if pattern.matches(data):
                # Threat detected
                pattern.detected_count += 1
                pattern.last_detected = datetime.now()

                event = SecurityEvent(
                    event_id=f"{self.manager_name}_{datetime.now().timestamp()}",
                    threat_type=pattern.pattern_type,
                    threat_level=pattern.severity,
                    source=source,
                    target=target,
                    pattern_matched=pattern.pattern_id,
                    timestamp=datetime.now(),
                    blocked=True,
                    details={"data_sample": str(data)[:100]},
                )

                self.security_events.append(event)

                # Learn from detection
                if self.pattern_learning_enabled:
                    await self._learn_from_threat(data, pattern)

                return event

        # No threat detected, but track for learning
        if self.pattern_learning_enabled:
            self.learning_cache[source].append(data)

        return None

    async def _learn_from_threat(self, data: Any, pattern: ThreatPattern):
        """Learn from detected threats"""
        # Track suspicious sources
        if isinstance(data, dict) and "source" in data:
            source = data["source"]
            self.suspicious_activity[source] += 1

            # Auto-block after threshold
            if self.suspicious_activity[source] >= self.auto_pattern_threshold:
                # Create source-specific pattern
                new_pattern = ThreatPattern(
                    pattern_id=f"auto_block_{source}",
                    pattern_type="suspicious_source",
                    keywords=[source],
                    severity=ThreatLevel.HIGH,
                    auto_expire=timedelta(hours=24),  # Auto-expire after 24h
                )
                self.add_pattern(new_pattern)

    def clean_expired_patterns(self):
        """Remove expired patterns"""
        now = datetime.now()
        expired = []

        for pattern_id, pattern in self.threat_patterns.items():
            if pattern.auto_expire and pattern.last_detected:
                if now - pattern.last_detected > pattern.auto_expire:
                    expired.append(pattern_id)

        for pattern_id in expired:
            self.remove_pattern(pattern_id)

        return len(expired)

    def get_threat_statistics(self) -> Dict[str, Any]:
        """Get security statistics"""
        stats = {
            "total_patterns": len(self.threat_patterns),
            "total_events": len(self.security_events),
            "events_by_type": defaultdict(int),
            "events_by_level": defaultdict(int),
            "top_patterns": [],
            "suspicious_sources": [],
        }

        # Count events by type and level
        for event in self.security_events:
            stats["events_by_type"][event.threat_type] += 1
            stats["events_by_level"][event.threat_level.value] += 1

        # Top patterns by detection count
        top_patterns = sorted(
            self.threat_patterns.values(), key=lambda p: p.detected_count, reverse=True
        )[:5]

        stats["top_patterns"] = [
            {
                "pattern_id": p.pattern_id,
                "type": p.pattern_type,
                "detections": p.detected_count,
            }
            for p in top_patterns
        ]

        # Top suspicious sources
        top_sources = sorted(
            self.suspicious_activity.items(), key=lambda x: x[1], reverse=True
        )[:5]

        stats["suspicious_sources"] = [
            {"source": source, "count": count} for source, count in top_sources
        ]

        return stats

    def export_patterns(self) -> List[Dict[str, Any]]:
        """Export patterns for sharing/backup"""
        return [
            {
                "pattern_id": p.pattern_id,
                "pattern_type": p.pattern_type,
                "regex": p.regex.pattern if p.regex else None,
                "keywords": p.keywords,
                "severity": p.severity.value,
                "detected_count": p.detected_count,
            }
            for p in self.threat_patterns.values()
        ]

    def import_patterns(self, patterns: List[Dict[str, Any]]) -> int:
        """Import patterns from export"""
        imported = 0

        for pattern_data in patterns:
            try:
                # Create pattern
                pattern = ThreatPattern(
                    pattern_id=pattern_data["pattern_id"],
                    pattern_type=pattern_data["pattern_type"],
                    keywords=pattern_data.get("keywords", []),
                    severity=ThreatLevel(pattern_data.get("severity", "medium")),
                )

                # Add regex if present
                if pattern_data.get("regex"):
                    pattern.regex = re.compile(pattern_data["regex"])

                if self.add_pattern(pattern):
                    imported += 1

            except Exception as e:
                logging.error(
                    f"Failed to import pattern {pattern_data.get('pattern_id')}: {e}"
                )

        return imported


class ImmuneSystemCell:
    """Enhanced immune cell with dynamic learning"""

    def __init__(self, cell_name: str):
        self.cell_name = cell_name
        self.security_manager = DynamicSecurityManager(f"immune_{cell_name}")
        self.antibody_memory: Dict[str, datetime] = {}  # Pattern -> first_seen
        self.threat_response_strategies: Dict[str, Callable] = {
            "isolate": self._isolate_threat,
            "neutralize": self._neutralize_threat,
            "alert": self._alert_threat,
        }

    async def scan_for_threats(self, data: Any, source: str) -> Optional[SecurityEvent]:
        """Scan data for threats"""
        event = await self.security_manager.check_threat(data, source, self.cell_name)

        if event:
            # Execute response strategy
            strategy = self._select_response_strategy(event)
            await self.threat_response_strategies[strategy](event)

        return event

    def _select_response_strategy(self, event: SecurityEvent) -> str:
        """Select appropriate response strategy"""
        if event.threat_level == ThreatLevel.CRITICAL:
            return "isolate"
        elif event.threat_level == ThreatLevel.HIGH:
            return "neutralize"
        else:
            return "alert"

    async def _isolate_threat(self, event: SecurityEvent):
        """Isolate the threat source"""
        logging.warning(f"ISOLATING threat from {event.source}")
        # In real implementation, would quarantine the source

    async def _neutralize_threat(self, event: SecurityEvent):
        """Neutralize the threat"""
        logging.warning(f"NEUTRALIZING threat: {event.threat_type}")
        # In real implementation, would clean/sanitize data

    async def _alert_threat(self, event: SecurityEvent):
        """Alert about threat"""
        logging.info(f"ALERT: {event.threat_type} detected from {event.source}")

    def learn_new_antibody(self, pattern: ThreatPattern):
        """Learn new threat pattern (antibody)"""
        self.security_manager.add_pattern(pattern)
        self.antibody_memory[pattern.pattern_id] = datetime.now()

    def forget_old_antibodies(self, older_than: timedelta = timedelta(days=30)):
        """Forget old, unused antibodies"""
        cutoff = datetime.now() - older_than

        forgotten = []
        for pattern_id, first_seen in self.antibody_memory.items():
            if first_seen < cutoff:
                pattern = self.security_manager.threat_patterns.get(pattern_id)
                if pattern and pattern.detected_count == 0:
                    self.security_manager.remove_pattern(pattern_id)
                    forgotten.append(pattern_id)

        for pattern_id in forgotten:
            del self.antibody_memory[pattern_id]

        return len(forgotten)
