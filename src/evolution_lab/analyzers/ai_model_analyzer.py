"""
AI/ML Model Analyzer for Machine Learning Projects
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import os
import re
from typing import Any, Dict, List, Optional
from pathlib import Path
from collections import defaultdict

from .base import BaseAnalyzer, AnalysisResult


class AIModelAnalyzer(BaseAnalyzer):
    """Analyzes AI/ML projects, models, and datasets"""
    
    # Common ML frameworks and their file extensions
    MODEL_EXTENSIONS = {
        '.h5': 'keras/tensorflow',
        '.hdf5': 'keras/tensorflow',
        '.pb': 'tensorflow',
        '.pth': 'pytorch',
        '.pt': 'pytorch',
        '.pkl': 'scikit-learn/general',
        '.joblib': 'scikit-learn',
        '.onnx': 'onnx',
        '.caffemodel': 'caffe',
        '.tflite': 'tensorflow-lite',
        '.mlmodel': 'coreml',
    }
    
    # Common dataset formats
    DATASET_PATTERNS = {
        'image': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'],
        'audio': ['.wav', '.mp3', '.flac', '.m4a'],
        'video': ['.mp4', '.avi', '.mov', '.mkv'],
        'text': ['.txt', '.csv', '.json', '.xml'],
        'numpy': ['.npy', '.npz'],
        'tensorflow': ['.tfrecord'],
    }
    
    def analyze(self) -> AnalysisResult:
        """Analyze AI/ML project structure and components"""
        self.start_timer()
        
        metrics = {
            'model_files': self._find_model_files(),
            'frameworks': self._detect_ml_frameworks(),
            'dataset_analysis': self._analyze_datasets(),
            'training_scripts': self._find_training_scripts(),
            'preprocessing': self._analyze_preprocessing(),
            'architecture': self._analyze_architecture(),
            'metrics_found': self._find_metrics(),
            'deployment': self._analyze_deployment_readiness(),
        }
        
        # For ear segmentation specific analysis
        if 'ear' in str(self.project_path).lower() or 'segmentation' in str(self.project_path).lower():
            metrics['segmentation_specific'] = self._analyze_segmentation_project()
            
        metrics['analysis_time'] = self.get_elapsed_time()
        
        issues = self._detect_ml_issues(metrics)
        suggestions = self._generate_ml_suggestions(metrics)
        
        return AnalysisResult(
            analyzer_name=self.name,
            metrics=metrics,
            issues=issues,
            suggestions=suggestions,
            metadata={
                'project_path': str(self.project_path),
                'ml_project': True,
            },
        )
        
    def _find_model_files(self) -> Dict[str, Any]:
        """Find and analyze model files"""
        model_info = {
            'count': 0,
            'files': [],
            'total_size': 0,
            'frameworks_detected': set()
        }
        
        for ext, framework in self.MODEL_EXTENSIONS.items():
            for file_path in self.scan_files([ext]):
                file_info = self.get_file_info(file_path)
                model_info['files'].append({
                    'path': file_info['path'],
                    'size': file_info['size'],
                    'framework': framework,
                    'modified': file_info['modified'],
                })
                model_info['count'] += 1
                model_info['total_size'] += file_info['size']
                model_info['frameworks_detected'].add(framework)
                
        model_info['frameworks_detected'] = list(model_info['frameworks_detected'])
        return model_info
        
    def _detect_ml_frameworks(self) -> Dict[str, bool]:
        """Detect which ML frameworks are used"""
        frameworks = {
            'tensorflow': False,
            'pytorch': False,
            'keras': False,
            'scikit-learn': False,
            'opencv': False,
            'pandas': False,
            'numpy': False,
        }
        
        # Check Python imports
        python_files = self.scan_files(['.py'])
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Check imports
                if re.search(r'import\s+tensorflow|from\s+tensorflow', content):
                    frameworks['tensorflow'] = True
                if re.search(r'import\s+torch|from\s+torch', content):
                    frameworks['pytorch'] = True
                if re.search(r'import\s+keras|from\s+keras', content):
                    frameworks['keras'] = True
                if re.search(r'import\s+sklearn|from\s+sklearn', content):
                    frameworks['scikit-learn'] = True
                if re.search(r'import\s+cv2|import\s+opencv', content):
                    frameworks['opencv'] = True
                if re.search(r'import\s+pandas|from\s+pandas', content):
                    frameworks['pandas'] = True
                if re.search(r'import\s+numpy|from\s+numpy', content):
                    frameworks['numpy'] = True
                    
            except Exception:
                pass
                
        # Check requirements files
        req_files = ['requirements.txt', 'environment.yml', 'Pipfile']
        for req_file in req_files:
            req_path = self.project_path / req_file
            if req_path.exists():
                try:
                    content = req_path.read_text().lower()
                    for framework in frameworks:
                        if framework.replace('-', '') in content:
                            frameworks[framework] = True
                except Exception:
                    pass
                    
        return frameworks
        
    def _analyze_datasets(self) -> Dict[str, Any]:
        """Analyze dataset structure and properties"""
        dataset_info = {
            'data_directories': [],
            'data_types': defaultdict(int),
            'total_files': 0,
            'total_size': 0,
            'structure': {},
        }
        
        # Common data directory names
        data_dirs = ['data', 'dataset', 'datasets', 'images', 'train', 'test', 'val', 'validation']
        
        for dir_name in data_dirs:
            for root, dirs, files in os.walk(self.project_path):
                if dir_name in Path(root).name.lower():
                    dataset_info['data_directories'].append(str(Path(root).relative_to(self.project_path)))
                    
                    # Analyze files in data directory
                    for file in files:
                        file_path = Path(root) / file
                        ext = file_path.suffix.lower()
                        
                        # Categorize by type
                        for data_type, extensions in self.DATASET_PATTERNS.items():
                            if ext in extensions:
                                dataset_info['data_types'][data_type] += 1
                                dataset_info['total_files'] += 1
                                dataset_info['total_size'] += file_path.stat().st_size
                                break
                                
        # Analyze structure (train/test/val split)
        for data_dir in dataset_info['data_directories']:
            dir_path = self.project_path / data_dir
            if dir_path.exists():
                subdirs = [d.name for d in dir_path.iterdir() if d.is_dir()]
                if any(split in subdirs for split in ['train', 'test', 'val', 'validation']):
                    dataset_info['structure']['split_found'] = True
                    dataset_info['structure']['splits'] = subdirs
                    
        return dataset_info
        
    def _find_training_scripts(self) -> List[Dict[str, Any]]:
        """Find and analyze training scripts"""
        training_scripts = []
        training_patterns = ['train', 'training', 'fit', 'model.fit', 'trainer', 'experiment']
        
        python_files = self.scan_files(['.py'])
        for file_path in python_files:
            # Check filename
            if any(pattern in file_path.stem.lower() for pattern in training_patterns):
                script_info = self._analyze_training_script(file_path)
                if script_info:
                    training_scripts.append(script_info)
                    
        return training_scripts
        
    def _analyze_training_script(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Analyze a potential training script"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            script_info = {
                'path': str(file_path.relative_to(self.project_path)),
                'metrics': [],
                'optimizers': [],
                'loss_functions': [],
                'callbacks': [],
                'gpu_usage': False,
            }
            
            # Find metrics
            metric_patterns = ['accuracy', 'precision', 'recall', 'f1', 'iou', 'dice', 'mse', 'mae']
            for metric in metric_patterns:
                if metric in content.lower():
                    script_info['metrics'].append(metric)
                    
            # Find optimizers
            optimizer_patterns = ['adam', 'sgd', 'rmsprop', 'adamw', 'optimizer']
            for opt in optimizer_patterns:
                if opt in content.lower():
                    script_info['optimizers'].append(opt)
                    
            # Find loss functions
            loss_patterns = ['crossentropy', 'mse', 'mae', 'bce', 'focal', 'dice_loss']
            for loss in loss_patterns:
                if loss in content.lower():
                    script_info['loss_functions'].append(loss)
                    
            # Check GPU usage
            if 'cuda' in content or 'gpu' in content.lower():
                script_info['gpu_usage'] = True
                
            return script_info
            
        except Exception:
            return None
            
    def _analyze_preprocessing(self) -> Dict[str, Any]:
        """Analyze data preprocessing methods"""
        preprocessing_info = {
            'augmentation': [],
            'normalization': False,
            'resize_operations': False,
            'custom_transforms': [],
        }
        
        # Look for preprocessing in Python files
        python_files = self.scan_files(['.py'])
        for file_path in python_files:
            if 'preprocess' in file_path.stem.lower() or 'augment' in file_path.stem.lower():
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    # Check for augmentation techniques
                    aug_patterns = ['rotate', 'flip', 'crop', 'zoom', 'shift', 'brightness', 'contrast']
                    for aug in aug_patterns:
                        if aug in content.lower():
                            preprocessing_info['augmentation'].append(aug)
                            
                    # Check for normalization
                    if 'normalize' in content.lower() or '/255' in content:
                        preprocessing_info['normalization'] = True
                        
                    # Check for resize
                    if 'resize' in content.lower() or 'reshape' in content.lower():
                        preprocessing_info['resize_operations'] = True
                        
                except Exception:
                    pass
                    
        return preprocessing_info
        
    def _analyze_architecture(self) -> Dict[str, Any]:
        """Analyze model architecture"""
        architecture_info = {
            'type': 'unknown',
            'layers_found': [],
            'backbone': None,
            'custom_model': False,
        }
        
        # Common architecture patterns
        architecture_patterns = {
            'cnn': ['conv2d', 'convolution', 'maxpool', 'avgpool'],
            'rnn': ['lstm', 'gru', 'rnn', 'recurrent'],
            'transformer': ['attention', 'transformer', 'bert', 'gpt'],
            'gan': ['generator', 'discriminator', 'gan'],
            'autoencoder': ['encoder', 'decoder', 'autoencoder'],
            'segmentation': ['unet', 'segnet', 'deeplabv3', 'mask_rcnn'],
        }
        
        # Common backbones
        backbone_patterns = ['resnet', 'vgg', 'efficientnet', 'mobilenet', 'densenet', 'inception']
        
        python_files = self.scan_files(['.py'])
        for file_path in python_files:
            if 'model' in file_path.stem.lower() or 'network' in file_path.stem.lower():
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        
                    # Detect architecture type
                    for arch_type, patterns in architecture_patterns.items():
                        if any(pattern in content for pattern in patterns):
                            architecture_info['type'] = arch_type
                            architecture_info['layers_found'].extend(
                                [p for p in patterns if p in content],
                            )
                            
                    # Detect backbone
                    for backbone in backbone_patterns:
                        if backbone in content:
                            architecture_info['backbone'] = backbone
                            
                    # Check if custom model
                    if 'class' in content and ('model' in content or 'network' in content):
                        architecture_info['custom_model'] = True
                        
                except Exception:
                    pass
                    
        return architecture_info
        
    def _find_metrics(self) -> Dict[str, List[str]]:
        """Find evaluation metrics used in the project"""
        metrics_found = {
            'classification': [],
            'segmentation': [],
            'detection': [],
            'regression': [],
        }
        
        # Metric patterns by type
        metric_patterns = {
            'classification': ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc', 'confusion_matrix'],
            'segmentation': ['iou', 'dice', 'jaccard', 'pixel_accuracy', 'mean_iou'],
            'detection': ['map', 'average_precision', 'precision', 'recall'],
            'regression': ['mse', 'mae', 'rmse', 'r2_score', 'mape'],
        }
        
        python_files = self.scan_files(['.py'])
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    
                for metric_type, patterns in metric_patterns.items():
                    for pattern in patterns:
                        if pattern in content:
                            metrics_found[metric_type].append(pattern)
                            
            except Exception:
                pass
                
        # Remove duplicates
        for metric_type in metrics_found:
            metrics_found[metric_type] = list(set(metrics_found[metric_type]))
            
        return metrics_found
        
    def _analyze_deployment_readiness(self) -> Dict[str, Any]:
        """Analyze if the model is ready for deployment"""
        deployment_info = {
            'api_found': False,
            'dockerfile': False,
            'requirements': False,
            'model_serving': [],
            'cloud_ready': False,
        }
        
        # Check for API implementations
        api_patterns = ['flask', 'fastapi', 'django', 'streamlit', 'gradio']
        python_files = self.scan_files(['.py'])
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    
                for api in api_patterns:
                    if api in content:
                        deployment_info['api_found'] = True
                        deployment_info['model_serving'].append(api)
                        
            except Exception:
                pass
                
        # Check for deployment files
        if (self.project_path / 'Dockerfile').exists():
            deployment_info['dockerfile'] = True
            
        if (self.project_path / 'requirements.txt').exists():
            deployment_info['requirements'] = True
            
        # Check for cloud deployment files
        cloud_files = ['app.yaml', 'serverless.yml', '.github/workflows', 'kubernetes.yaml']
        for cloud_file in cloud_files:
            if (self.project_path / cloud_file).exists():
                deployment_info['cloud_ready'] = True
                break
                
        return deployment_info
        
    def _analyze_segmentation_project(self) -> Dict[str, Any]:
        """Specific analysis for segmentation projects"""
        seg_info = {
            'mask_format': None,
            'classes_found': [],
            'annotation_tool': None,
            'evaluation_metrics': [],
        }
        
        # Check for common segmentation patterns
        python_files = self.scan_files(['.py'])
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Check mask format
                if 'binary_mask' in content or 'binary mask' in content.lower():
                    seg_info['mask_format'] = 'binary'
                elif 'multi_class' in content or 'multiclass' in content.lower():
                    seg_info['mask_format'] = 'multi-class'
                    
                # Check for annotation tools
                if 'labelme' in content.lower():
                    seg_info['annotation_tool'] = 'LabelMe'
                elif 'cvat' in content.lower():
                    seg_info['annotation_tool'] = 'CVAT'
                elif 'labelbox' in content.lower():
                    seg_info['annotation_tool'] = 'Labelbox'
                    
            except Exception:
                pass
                
        return seg_info
        
    def _detect_ml_issues(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect ML-specific issues"""
        issues = []
        
        # No model files found
        if metrics['model_files']['count'] == 0:
            issues.append({
                'severity': 'info',
                'type': 'model',
                'message': 'No trained model files found in the project',
            })
            
        # Large model files
        for model in metrics['model_files']['files']:
            if model['size'] > 100 * 1024 * 1024:  # 100MB
                issues.append({
                    'severity': 'medium',
                    'type': 'size',
                    'message': f"Large model file ({model['size'] // (1024*1024)}MB): {model['path']}",
                })
                
        # No data found
        if metrics['dataset_analysis']['total_files'] == 0:
            issues.append({
                'severity': 'high',
                'type': 'data',
                'message': 'No dataset files found in common data directories',
            })
            
        # No training scripts
        if not metrics['training_scripts']:
            issues.append({
                'severity': 'medium',
                'type': 'training',
                'message': 'No training scripts detected',
            })
            
        return issues
        
    def _generate_ml_suggestions(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate ML-specific suggestions"""
        suggestions = []
        
        # Model optimization
        if metrics['model_files']['total_size'] > 50 * 1024 * 1024:
            suggestions.append("Consider model compression techniques (pruning, quantization) to reduce model size")
            
        # Data organization
        if not metrics['dataset_analysis']['structure'].get('split_found'):
            suggestions.append("Organize data into train/validation/test splits for proper evaluation")
            
        # Deployment
        if not metrics['deployment']['api_found']:
            suggestions.append("Add a REST API or web interface for model deployment")
            
        if not metrics['deployment']['dockerfile']:
            suggestions.append("Create a Dockerfile for containerized deployment")
            
        # Metrics
        if not metrics['metrics_found']['segmentation'] and 'segmentation' in metrics.get('segmentation_specific', {}):
            suggestions.append("Implement segmentation metrics (IoU, Dice coefficient) for better evaluation")
            
        return suggestions