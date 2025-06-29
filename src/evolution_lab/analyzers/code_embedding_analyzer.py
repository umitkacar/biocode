"""
Code Embedding Analyzer - Semantic Code Understanding & Similarity Detection
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.

Creates semantic embeddings for code elements to enable:
- Semantic code search
- Duplicate/clone detection (Type 1-4)
- Function similarity analysis
- Code clustering by functionality
- Cross-project code matching
"""

import ast
import os
import re
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple, Optional, Union
from collections import defaultdict
from dataclasses import dataclass, field
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import json

from .base import BaseAnalyzer, AnalysisResult


@dataclass
class CodeElement:
    """Represents a code element with its embedding"""
    id: str
    name: str
    type: str  # 'function', 'class', 'method'
    file_path: str
    line_start: int
    line_end: int
    code: str
    docstring: Optional[str] = None
    signature: Optional[str] = None
    ast_hash: Optional[str] = None
    embedding: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SimilarityMatch:
    """Represents a similarity match between code elements"""
    source_id: str
    target_id: str
    similarity_score: float
    clone_type: str  # 'type1', 'type2', 'type3', 'type4'
    confidence: float
    

class CodeEmbeddingAnalyzer(BaseAnalyzer):
    """
    Analyzes code to create semantic embeddings for similarity detection.
    
    Features:
    - Multi-level embeddings (token, AST, semantic)
    - Clone detection (Type 1-4)
    - Semantic code search
    - Function similarity matrix
    - Cross-file duplicate detection
    """
    
    def __init__(self, project_path: str, model_name: str = "microsoft/codebert-base"):
        super().__init__(project_path)
        
        # Initialize embedding model
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer(model_name)
        except Exception as e:
            # Fallback to TF-IDF based embeddings if sentence-transformers not available
            if hasattr(self, 'logger'):
                self.logger.warning(f"Sentence transformers not available: {e}")
                self.logger.warning("Using TF-IDF based embeddings as fallback")
            self.embedding_model = None
        
        # Storage for code elements and embeddings
        self.code_elements: Dict[str, CodeElement] = {}
        self.embeddings_matrix: Optional[np.ndarray] = None
        self.element_ids: List[str] = []
        
        # TF-IDF for token-based similarity
        self.tfidf_vectorizer = TfidfVectorizer(
            token_pattern=r'[a-zA-Z_][a-zA-Z0-9_]*',  # Identifiers
            lowercase=False,
            max_features=1000
        )
        
        # Cache for performance
        self.cache_file = Path(project_path) / '.biocode_embeddings_cache.pkl'
        
    async def analyze(self) -> AnalysisResult:
        """Perform code embedding analysis"""
        # Phase 1: Extract code elements
        self._extract_code_elements()
        
        # Phase 2: Generate embeddings
        self._generate_embeddings()
        
        # Phase 3: Detect clones and similarities
        similarities = self._detect_similarities()
        
        # Phase 4: Analyze patterns
        metrics = self._analyze_embedding_metrics(similarities)
        
        # Phase 5: Detect issues
        issues = self._detect_embedding_issues(similarities)
        
        # Phase 6: Generate suggestions
        suggestions = self._generate_suggestions(metrics, issues)
        
        return AnalysisResult(
            analyzer_name="CodeEmbeddingAnalyzer",
            metrics=metrics,
            issues=issues,
            suggestions=suggestions
        )
        
    def _extract_code_elements(self):
        """Extract all functions, methods, and classes from the project"""
        python_files = self._get_python_files()
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                tree = ast.parse(content)
                relative_path = os.path.relpath(file_path, self.project_path)
                
                # Extract elements using visitor
                visitor = CodeElementVisitor(
                    file_path=relative_path,
                    file_content=content,
                    analyzer=self
                )
                visitor.visit(tree)
                
            except Exception as e:
                self.logger.error(f"Error extracting from {file_path}: {e}")
                
    def _generate_embeddings(self):
        """Generate embeddings for all code elements"""
        if not self.code_elements:
            return
            
        # Check cache first
        if self._load_cache():
            return
            
        # Prepare texts for embedding
        texts = []
        self.element_ids = []
        
        for elem_id, element in self.code_elements.items():
            # Combine code, docstring, and signature for richer embedding
            text_parts = []
            
            # Add signature
            if element.signature:
                text_parts.append(f"Signature: {element.signature}")
                
            # Add docstring
            if element.docstring:
                text_parts.append(f"Description: {element.docstring}")
                
            # Add cleaned code
            cleaned_code = self._clean_code_for_embedding(element.code)
            text_parts.append(f"Code: {cleaned_code}")
            
            combined_text = " ".join(text_parts)
            texts.append(combined_text)
            self.element_ids.append(elem_id)
            
        # Generate embeddings
        if texts:
            self.logger.info(f"Generating embeddings for {len(texts)} code elements...")
            
            if self.embedding_model is not None:
                # Use sentence transformers
                embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
                self.embeddings_matrix = np.array(embeddings)
            else:
                # Fallback to TF-IDF embeddings
                self.logger.info("Using TF-IDF embeddings as fallback")
                vectorizer = TfidfVectorizer(max_features=384, stop_words='english')
                tfidf_matrix = vectorizer.fit_transform(texts)
                self.embeddings_matrix = tfidf_matrix.toarray()
            
            # Store embeddings in elements
            for i, elem_id in enumerate(self.element_ids):
                self.code_elements[elem_id].embedding = self.embeddings_matrix[i]
                
            # Save cache
            self._save_cache()
            
    def _detect_similarities(self) -> List[SimilarityMatch]:
        """Detect similar code elements using multiple techniques"""
        similarities = []
        
        if self.embeddings_matrix is None or len(self.element_ids) < 2:
            return similarities
            
        # 1. Semantic similarity using embeddings
        semantic_similarities = self._detect_semantic_similarities()
        similarities.extend(semantic_similarities)
        
        # 2. Token-based similarity using TF-IDF
        token_similarities = self._detect_token_similarities()
        similarities.extend(token_similarities)
        
        # 3. AST-based similarity
        ast_similarities = self._detect_ast_similarities()
        similarities.extend(ast_similarities)
        
        # Merge and deduplicate
        similarities = self._merge_similarities(similarities)
        
        return similarities
        
    def _detect_semantic_similarities(self) -> List[SimilarityMatch]:
        """Detect semantically similar code using embeddings"""
        similarities = []
        
        # Compute cosine similarity matrix
        similarity_matrix = cosine_similarity(self.embeddings_matrix)
        
        # Find similar pairs (above threshold)
        threshold = 0.8  # High threshold for semantic similarity
        
        for i in range(len(self.element_ids)):
            for j in range(i + 1, len(self.element_ids)):
                score = similarity_matrix[i, j]
                
                if score >= threshold:
                    source_id = self.element_ids[i]
                    target_id = self.element_ids[j]
                    
                    # Skip if same file and overlapping lines
                    source = self.code_elements[source_id]
                    target = self.code_elements[target_id]
                    
                    if not self._is_valid_match(source, target):
                        continue
                        
                    # Determine clone type based on score and code comparison
                    clone_type = self._determine_clone_type(source, target, score)
                    
                    similarities.append(SimilarityMatch(
                        source_id=source_id,
                        target_id=target_id,
                        similarity_score=float(score),
                        clone_type=clone_type,
                        confidence=float(score)
                    ))
                    
        return similarities
        
    def _detect_token_similarities(self) -> List[SimilarityMatch]:
        """Detect token-level similarities using TF-IDF"""
        similarities = []
        
        if len(self.code_elements) < 2:
            return similarities
            
        # Prepare code texts
        texts = []
        element_ids = []
        
        for elem_id, element in self.code_elements.items():
            # Extract identifiers from code
            identifiers = self._extract_identifiers(element.code)
            if identifiers:
                texts.append(" ".join(identifiers))
                element_ids.append(elem_id)
                
        if len(texts) < 2:
            return similarities
            
        # Compute TF-IDF
        try:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # Find similar pairs
            threshold = 0.9  # High threshold for token similarity
            
            for i in range(len(element_ids)):
                for j in range(i + 1, len(element_ids)):
                    score = similarity_matrix[i, j]
                    
                    if score >= threshold:
                        source_id = element_ids[i]
                        target_id = element_ids[j]
                        
                        source = self.code_elements[source_id]
                        target = self.code_elements[target_id]
                        
                        if not self._is_valid_match(source, target):
                            continue
                            
                        similarities.append(SimilarityMatch(
                            source_id=source_id,
                            target_id=target_id,
                            similarity_score=float(score),
                            clone_type='type2',  # Token similarity suggests Type 2
                            confidence=float(score) * 0.9  # Slightly lower confidence
                        ))
                        
        except Exception as e:
            self.logger.warning(f"Token similarity detection failed: {e}")
            
        return similarities
        
    def _detect_ast_similarities(self) -> List[SimilarityMatch]:
        """Detect AST-level similarities"""
        similarities = []
        
        # Group elements by AST hash
        ast_groups = defaultdict(list)
        
        for elem_id, element in self.code_elements.items():
            if element.ast_hash:
                ast_groups[element.ast_hash].append(elem_id)
                
        # Find exact AST matches (Type 1 clones)
        for ast_hash, element_ids in ast_groups.items():
            if len(element_ids) > 1:
                # All elements with same AST hash are Type 1 clones
                for i in range(len(element_ids)):
                    for j in range(i + 1, len(element_ids)):
                        source_id = element_ids[i]
                        target_id = element_ids[j]
                        
                        source = self.code_elements[source_id]
                        target = self.code_elements[target_id]
                        
                        if not self._is_valid_match(source, target):
                            continue
                            
                        similarities.append(SimilarityMatch(
                            source_id=source_id,
                            target_id=target_id,
                            similarity_score=1.0,
                            clone_type='type1',
                            confidence=1.0
                        ))
                        
        return similarities
        
    def _merge_similarities(self, similarities: List[SimilarityMatch]) -> List[SimilarityMatch]:
        """Merge and deduplicate similarity matches"""
        # Group by source-target pair
        pair_matches = defaultdict(list)
        
        for match in similarities:
            key = tuple(sorted([match.source_id, match.target_id]))
            pair_matches[key].append(match)
            
        # Merge matches for each pair
        merged = []
        
        for pair, matches in pair_matches.items():
            # Sort by confidence and take the best match
            best_match = max(matches, key=lambda m: m.confidence)
            
            # Adjust clone type based on all detections
            clone_types = [m.clone_type for m in matches]
            if 'type1' in clone_types:
                best_match.clone_type = 'type1'
            elif 'type2' in clone_types and best_match.clone_type != 'type1':
                best_match.clone_type = 'type2'
                
            merged.append(best_match)
            
        return merged
        
    def _determine_clone_type(self, source: CodeElement, target: CodeElement, score: float) -> str:
        """Determine the type of code clone"""
        # Type 1: Exact match (except whitespace/comments)
        if self._normalize_code(source.code) == self._normalize_code(target.code):
            return 'type1'
            
        # Type 2: Renamed (identifier changes only)
        if score > 0.95 and self._is_renamed_clone(source.code, target.code):
            return 'type2'
            
        # Type 3: Modified (statements added/removed)
        if score > 0.85:
            return 'type3'
            
        # Type 4: Semantic (different syntax, same functionality)
        return 'type4'
        
    def _is_renamed_clone(self, code1: str, code2: str) -> bool:
        """Check if two code snippets are renamed clones"""
        # Simple heuristic: normalize identifiers and compare
        norm1 = re.sub(r'[a-zA-Z_][a-zA-Z0-9_]*', 'ID', code1)
        norm2 = re.sub(r'[a-zA-Z_][a-zA-Z0-9_]*', 'ID', code2)
        
        return norm1 == norm2
        
    def _normalize_code(self, code: str) -> str:
        """Normalize code for exact comparison"""
        # Remove comments
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
        
        # Normalize whitespace
        code = re.sub(r'\s+', ' ', code)
        
        return code.strip()
        
    def _is_valid_match(self, source: CodeElement, target: CodeElement) -> bool:
        """Check if two elements are valid for comparison"""
        # Skip if same element
        if source.id == target.id:
            return False
            
        # Skip if same file and overlapping lines
        if source.file_path == target.file_path:
            if (source.line_start <= target.line_end and 
                target.line_start <= source.line_end):
                return False
                
        return True
        
    def _extract_identifiers(self, code: str) -> List[str]:
        """Extract identifiers from code"""
        # Simple regex-based extraction
        identifiers = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', code)
        
        # Filter out Python keywords
        keywords = {'def', 'class', 'if', 'else', 'elif', 'for', 'while', 
                   'return', 'import', 'from', 'as', 'try', 'except', 
                   'finally', 'with', 'pass', 'break', 'continue'}
        
        return [id for id in identifiers if id not in keywords]
        
    def _clean_code_for_embedding(self, code: str) -> str:
        """Clean code for embedding generation"""
        # Remove excessive whitespace
        code = re.sub(r'\n\s*\n', '\n', code)
        
        # Truncate if too long
        max_length = 512  # Token limit
        if len(code) > max_length:
            code = code[:max_length] + "..."
            
        return code
        
    def _analyze_embedding_metrics(self, similarities: List[SimilarityMatch]) -> Dict[str, Any]:
        """Analyze metrics from embeddings and similarities"""
        metrics = {
            'total_elements': len(self.code_elements),
            'total_embeddings': len(self.element_ids),
            'embedding_model': self.embedding_model.__class__.__name__ if self.embedding_model else 'TfidfVectorizer',
            'embedding_dimension': self.embeddings_matrix.shape[1] if self.embeddings_matrix is not None else 0,
        }
        
        # Clone statistics
        clone_stats = {
            'total_clones': len(similarities),
            'type1_clones': len([s for s in similarities if s.clone_type == 'type1']),
            'type2_clones': len([s for s in similarities if s.clone_type == 'type2']),
            'type3_clones': len([s for s in similarities if s.clone_type == 'type3']),
            'type4_clones': len([s for s in similarities if s.clone_type == 'type4']),
        }
        metrics['clone_statistics'] = clone_stats
        
        # Calculate duplication ratio
        unique_elements = len(self.code_elements)
        duplicated_elements = len(set(s.source_id for s in similarities) | 
                                set(s.target_id for s in similarities))
        
        metrics['duplication_ratio'] = duplicated_elements / max(1, unique_elements)
        
        # Similarity distribution
        if similarities:
            scores = [s.similarity_score for s in similarities]
            metrics['similarity_distribution'] = {
                'min': min(scores),
                'max': max(scores),
                'mean': sum(scores) / len(scores),
                'median': sorted(scores)[len(scores) // 2],
            }
            
        # Top similar functions
        similarity_counts = defaultdict(int)
        for match in similarities:
            similarity_counts[match.source_id] += 1
            similarity_counts[match.target_id] += 1
            
        top_duplicated = sorted(similarity_counts.items(), 
                              key=lambda x: x[1], reverse=True)[:10]
        
        metrics['top_duplicated_elements'] = [
            {
                'element': self.code_elements[elem_id].name,
                'file': self.code_elements[elem_id].file_path,
                'duplicate_count': count
            }
            for elem_id, count in top_duplicated
        ]
        
        # Embedding quality metrics
        if self.embeddings_matrix is not None and len(self.embeddings_matrix) > 1:
            # Average pairwise distance
            pairwise_distances = 1 - cosine_similarity(self.embeddings_matrix)
            avg_distance = np.mean(pairwise_distances[np.triu_indices_from(pairwise_distances, k=1)])
            
            metrics['embedding_quality'] = {
                'average_distance': float(avg_distance),
                'embedding_variance': float(np.var(self.embeddings_matrix)),
                'embedding_coverage': len(self.element_ids) / max(1, len(self.code_elements)),
            }
            
        # Code quality score based on duplication
        quality_score = 100 * (1 - metrics['duplication_ratio'])
        metrics['code_quality_score'] = max(0, min(100, quality_score))
        
        return metrics
        
    def _detect_embedding_issues(self, similarities: List[SimilarityMatch]) -> List[Dict[str, Any]]:
        """Detect issues based on code similarities"""
        issues = []
        
        # High duplication issue
        if len(similarities) > 10:
            issues.append({
                'type': 'high_duplication',
                'severity': 'high',
                'message': f"High code duplication detected: {len(similarities)} duplicate code blocks",
                'count': len(similarities)
            })
            
        # Exact clones (Type 1)
        type1_clones = [s for s in similarities if s.clone_type == 'type1']
        if type1_clones:
            issues.append({
                'type': 'exact_clones',
                'severity': 'medium',
                'message': f"Found {len(type1_clones)} exact code clones that should be refactored",
                'clones': [
                    {
                        'source': self.code_elements[s.source_id].name,
                        'target': self.code_elements[s.target_id].name,
                    }
                    for s in type1_clones[:5]  # First 5
                ]
            })
            
        # Complex duplication patterns
        element_duplication_count = defaultdict(int)
        for match in similarities:
            element_duplication_count[match.source_id] += 1
            element_duplication_count[match.target_id] += 1
            
        highly_duplicated = [elem_id for elem_id, count in element_duplication_count.items() if count >= 3]
        
        if highly_duplicated:
            issues.append({
                'type': 'pattern_duplication',
                'severity': 'medium',
                'message': f"Found {len(highly_duplicated)} code patterns duplicated 3+ times",
                'elements': [
                    {
                        'name': self.code_elements[elem_id].name,
                        'file': self.code_elements[elem_id].file_path,
                        'duplicates': element_duplication_count[elem_id]
                    }
                    for elem_id in highly_duplicated[:5]
                ]
            })
            
        # Large similar code blocks
        large_clones = []
        for match in similarities:
            source = self.code_elements[match.source_id]
            target = self.code_elements[match.target_id]
            
            source_lines = source.line_end - source.line_start
            target_lines = target.line_end - target.line_start
            
            if min(source_lines, target_lines) > 20:  # More than 20 lines
                large_clones.append(match)
                
        if large_clones:
            issues.append({
                'type': 'large_duplicates',
                'severity': 'high',
                'message': f"Found {len(large_clones)} large duplicate code blocks (>20 lines)",
                'examples': [
                    {
                        'source': self.code_elements[m.source_id].name,
                        'target': self.code_elements[m.target_id].name,
                        'similarity': m.similarity_score
                    }
                    for m in large_clones[:3]
                ]
            })
            
        return issues
        
    def _generate_suggestions(self, metrics: Dict[str, Any], issues: List[Dict[str, Any]]) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        # Based on duplication ratio
        dup_ratio = metrics.get('duplication_ratio', 0)
        if dup_ratio > 0.2:
            suggestions.append(f"Refactor duplicated code: {dup_ratio:.1%} of functions have duplicates")
            suggestions.append("Consider extracting common functionality into shared utilities")
            
        # Based on clone types
        clone_stats = metrics.get('clone_statistics', {})
        
        if clone_stats.get('type1_clones', 0) > 0:
            suggestions.append("Extract exact duplicate functions into a shared module")
            
        if clone_stats.get('type2_clones', 0) > 0:
            suggestions.append("Parameterize similar functions to reduce code duplication")
            
        if clone_stats.get('type3_clones', 0) > 0:
            suggestions.append("Use template methods or strategy pattern for similar logic")
            
        if clone_stats.get('type4_clones', 0) > 0:
            suggestions.append("Review semantically similar functions for potential consolidation")
            
        # Based on top duplicated elements
        top_dups = metrics.get('top_duplicated_elements', [])
        if top_dups:
            most_dup = top_dups[0]
            suggestions.append(f"Priority refactor: '{most_dup['element']}' has {most_dup['duplicate_count']} duplicates")
            
        # General suggestions
        suggestions.append("Use code embedding search to find similar implementations before writing new code")
        suggestions.append("Set up duplicate detection in CI/CD pipeline")
        suggestions.append("Create a shared library for commonly duplicated patterns")
        
        # Based on embedding quality
        embedding_quality = metrics.get('embedding_quality', {})
        if embedding_quality.get('average_distance', 1) < 0.3:
            suggestions.append("Code elements are very similar - consider more modular design")
            
        return suggestions
        
    def semantic_search(self, query: str, top_k: int = 10) -> List[Tuple[CodeElement, float]]:
        """Search for code elements using semantic similarity"""
        if self.embeddings_matrix is None or len(self.embeddings_matrix) == 0:
            self.logger.warning("No embeddings available for search")
            return []
            
        # Encode the query
        if self.embedding_model is not None:
            query_embedding = self.embedding_model.encode([query])[0]
        else:
            # Use TF-IDF for query encoding
            vectorizer = TfidfVectorizer(max_features=384, stop_words='english')
            all_texts = [query] + [self._clean_code_for_embedding(elem.code) for elem in self.code_elements.values()]
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            query_embedding = tfidf_matrix[0].toarray()[0]
            self.embeddings_matrix = tfidf_matrix[1:].toarray()
        
        # Compute similarities
        similarities = cosine_similarity([query_embedding], self.embeddings_matrix)[0]
        
        # Get top k results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            elem_id = self.element_ids[idx]
            element = self.code_elements[elem_id]
            score = float(similarities[idx])
            
            if score > 0.3:  # Minimum threshold
                results.append((element, score))
                
        return results
        
    def find_similar_code(self, code_snippet: str, top_k: int = 5) -> List[Tuple[CodeElement, float]]:
        """Find similar code to a given snippet"""
        if self.embeddings_matrix is None or len(self.embeddings_matrix) == 0:
            self.logger.warning("No embeddings available for similarity search")
            return []
            
        # Create embedding for the snippet
        if self.embedding_model is not None:
            snippet_embedding = self.embedding_model.encode([code_snippet])[0]
        else:
            # Use TF-IDF for snippet encoding
            vectorizer = TfidfVectorizer(max_features=384, stop_words='english')
            all_texts = [code_snippet] + [self._clean_code_for_embedding(elem.code) for elem in self.code_elements.values()]
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            snippet_embedding = tfidf_matrix[0].toarray()[0]
            self.embeddings_matrix = tfidf_matrix[1:].toarray()
        
        # Compute similarities
        similarities = cosine_similarity([snippet_embedding], self.embeddings_matrix)[0]
        
        # Get top k results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            elem_id = self.element_ids[idx]
            element = self.code_elements[elem_id]
            score = float(similarities[idx])
            
            if score > 0.5:  # Higher threshold for code similarity
                results.append((element, score))
                
        return results
        
    def get_element_embedding(self, element_id: str) -> Optional[np.ndarray]:
        """Get embedding for a specific code element"""
        element = self.code_elements.get(element_id)
        if element:
            return element.embedding
        return None
        
    def _get_python_files(self) -> List[str]:
        """Get all Python files in the project"""
        python_files = []
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        return python_files
        
    def _save_cache(self):
        """Save embeddings to cache"""
        try:
            cache_data = {
                'embeddings_matrix': self.embeddings_matrix,
                'element_ids': self.element_ids,
                'code_elements': {k: v for k, v in self.code_elements.items()}  # Serialize
            }
            
            with open(self.cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
                
            self.logger.info(f"Saved embeddings cache to {self.cache_file}")
            
        except Exception as e:
            self.logger.warning(f"Failed to save cache: {e}")
            
    def _load_cache(self) -> bool:
        """Load embeddings from cache"""
        if not self.cache_file.exists():
            return False
            
        try:
            with open(self.cache_file, 'rb') as f:
                cache_data = pickle.load(f)
                
            self.embeddings_matrix = cache_data['embeddings_matrix']
            self.element_ids = cache_data['element_ids']
            
            # Restore embeddings to elements
            for elem_id in self.element_ids:
                if elem_id in self.code_elements:
                    idx = self.element_ids.index(elem_id)
                    self.code_elements[elem_id].embedding = self.embeddings_matrix[idx]
                    
            self.logger.info(f"Loaded embeddings cache from {self.cache_file}")
            return True
            
        except Exception as e:
            self.logger.warning(f"Failed to load cache: {e}")
            return False
            
    def export_embeddings(self, output_path: str):
        """Export embeddings and metadata"""
        data = {
            'elements': [],
            'embeddings': self.embeddings_matrix.tolist() if self.embeddings_matrix is not None else [],
            'metadata': {
                'model': self.embedding_model.__class__.__name__ if self.embedding_model else 'TfidfVectorizer',
                'dimension': self.embeddings_matrix.shape[1] if self.embeddings_matrix is not None else 0,
                'total_elements': len(self.code_elements)
            }
        }
        
        for elem_id in self.element_ids:
            element = self.code_elements[elem_id]
            data['elements'].append({
                'id': element.id,
                'name': element.name,
                'type': element.type,
                'file': element.file_path,
                'lines': f"{element.line_start}-{element.line_end}",
                'docstring': element.docstring
            })
            
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
            
        self.logger.info(f"Exported embeddings to {output_path}")


class CodeElementVisitor(ast.NodeVisitor):
    """AST visitor to extract code elements"""
    
    def __init__(self, file_path: str, file_content: str, analyzer: CodeEmbeddingAnalyzer):
        self.file_path = file_path
        self.file_content = file_content
        self.file_lines = file_content.split('\n')
        self.analyzer = analyzer
        self.current_class = None
        
    def visit_FunctionDef(self, node):
        """Extract function definitions"""
        self._extract_function(node)
        self.generic_visit(node)
        
    def visit_AsyncFunctionDef(self, node):
        """Extract async function definitions"""
        self._extract_function(node, is_async=True)
        self.generic_visit(node)
        
    def visit_ClassDef(self, node):
        """Extract class definitions"""
        class_id = f"{self.file_path}:class:{node.name}:{node.lineno}"
        
        # Get class code
        code = self._get_node_source(node)
        
        # Create class element
        element = CodeElement(
            id=class_id,
            name=node.name,
            type='class',
            file_path=self.file_path,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            code=code,
            docstring=ast.get_docstring(node),
            signature=f"class {node.name}",
            ast_hash=self._compute_ast_hash(node)
        )
        
        self.analyzer.code_elements[class_id] = element
        
        # Visit methods
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
        
    def _extract_function(self, node, is_async=False):
        """Extract function or method"""
        if self.current_class:
            func_type = 'method'
            func_id = f"{self.file_path}:method:{self.current_class}.{node.name}:{node.lineno}"
            full_name = f"{self.current_class}.{node.name}"
        else:
            func_type = 'function'
            func_id = f"{self.file_path}:function:{node.name}:{node.lineno}"
            full_name = node.name
            
        # Get function code
        code = self._get_node_source(node)
        
        # Build signature
        signature = self._build_function_signature(node, is_async)
        
        # Create element
        element = CodeElement(
            id=func_id,
            name=full_name,
            type=func_type,
            file_path=self.file_path,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            code=code,
            docstring=ast.get_docstring(node),
            signature=signature,
            ast_hash=self._compute_ast_hash(node),
            metadata={
                'is_async': is_async,
                'parent_class': self.current_class
            }
        )
        
        self.analyzer.code_elements[func_id] = element
        
    def _get_node_source(self, node) -> str:
        """Get source code for an AST node"""
        if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
            start_line = node.lineno - 1
            end_line = node.end_lineno
            
            if 0 <= start_line < len(self.file_lines) and end_line <= len(self.file_lines):
                return '\n'.join(self.file_lines[start_line:end_line])
                
        # Fallback to ast.unparse
        try:
            return ast.unparse(node)
        except:
            return ""
            
    def _build_function_signature(self, node, is_async=False) -> str:
        """Build function signature string"""
        parts = []
        
        if is_async:
            parts.append("async")
            
        parts.append("def")
        parts.append(node.name)
        
        # Arguments
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
            
        parts.append(f"({', '.join(args)})")
        
        # Return type
        if node.returns:
            try:
                return_type = ast.unparse(node.returns)
                parts.append(f"-> {return_type}")
            except:
                pass
                
        return " ".join(parts)
        
    def _compute_ast_hash(self, node) -> str:
        """Compute hash of AST structure (ignoring identifiers)"""
        # Normalize AST by replacing identifiers
        normalized = self._normalize_ast(node)
        
        # Convert to string and hash
        try:
            ast_str = ast.dump(normalized, annotate_fields=False)
            return hashlib.md5(ast_str.encode()).hexdigest()[:16]
        except:
            return ""
            
    def _normalize_ast(self, node):
        """Normalize AST for structural comparison"""
        # Simple normalization - replace all names with 'ID'
        class Normalizer(ast.NodeTransformer):
            def visit_Name(self, node):
                return ast.Name(id='ID', ctx=node.ctx)
                
        return Normalizer().visit(node)