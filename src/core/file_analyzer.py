"""
File Analysis System
Individual file analysis and information extraction
"""

import os
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


@dataclass
class FileInfo:
    """Data class for individual file information"""
    file_path: str
    file_name: str
    file_type: str
    file_size: int
    line_count: int
    language: str
    purpose: str
    key_functions: List[str]
    dependencies: List[str]
    complexity_score: int
    ai_analysis: str
    technical_contributions: List[str]
    research_potential: str
    # Detailed per-line and structure analysis used for high-fidelity paper generation
    line_analysis: Dict[str, Any] | None = None


class FileAnalyzer:
    """Individual file analysis system"""
    
    def __init__(self):
        # Hardcoded API key for immediate functionality
        api_key = os.getenv('GEMINI_API_KEY') or 'AIzaSyCLhkBuuaMEsiiuDYM20hcRF1Ei1GiJu9Q'
        if api_key:
            genai.configure(api_key=api_key)
            # Use a supported Gemini model
            try:
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            except Exception:
                try:
                    self.model = genai.GenerativeModel('gemini-2.5-flash')
                except Exception:
                    self.model = None
        else:
            self.model = None
        
        self.code_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript', 
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.h': 'C/C++ Header',
            '.rs': 'Rust',
            '.go': 'Go',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.r': 'R',
            '.m': 'Objective-C',
            '.cs': 'C#',
            '.vb': 'VB.NET',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.sass': 'Sass',
            '.xml': 'XML',
            '.json': 'JSON',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.toml': 'TOML',
            '.ini': 'INI',
            '.cfg': 'Config',
            '.conf': 'Config',
            '.md': 'Markdown',
            '.txt': 'Text',
            '.sql': 'SQL',
            '.sh': 'Shell Script',
            '.bat': 'Batch Script',
            '.ps1': 'PowerShell',
            '.dockerfile': 'Dockerfile',
            '.dockerignore': 'Docker Ignore',
            '.gitignore': 'Git Ignore',
            '.gitattributes': 'Git Attributes'
        }
        # Languages that represent actual code for deeper AI analysis
        self._code_language_names = {
            'Python','JavaScript','TypeScript','Java','C++','C','C/C++ Header','Rust','Go','PHP','Ruby',
            'Swift','Kotlin','Scala','R','Objective-C','C#','HTML','CSS','SCSS','Sass','SQL','Shell Script'
        }
    
    def extract_all_files(self, repo_path: str) -> List[Dict[str, Any]]:
        """Extract all files from repository with basic information"""
        files = []
        
        for root, dirs, filenames in os.walk(repo_path):
            # Skip common directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '__pycache__', 'build', 'dist']]
            
            for filename in filenames:
                if filename.startswith('.'):
                    continue
                    
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, repo_path)
                
                try:
                    file_size = os.path.getsize(file_path)
                    file_ext = Path(filename).suffix.lower()
                    language = self.code_extensions.get(file_ext, 'Unknown')
                    
                    # Count lines for text files
                    line_count = 0
                    if language != 'Unknown':
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                line_count = sum(1 for _ in f)
                        except:
                            line_count = 0
                    
                    file_info = {
                        'file_path': relative_path,
                        'file_name': filename,
                        'file_type': file_ext,
                        'file_size': file_size,
                        'line_count': line_count,
                        'language': language,
                        'is_code': (language in self._code_language_names) and file_size > 0
                    }
                    
                    files.append(file_info)
                    
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    continue
        
        return files
    
    def analyze_file(self, file_path: str, repo_path: str, file_info: Dict[str, Any]) -> FileInfo:
        """Analyze individual file with AI and line-by-line analysis"""
        full_path = os.path.join(repo_path, file_path)
        
        try:
            # Read file content
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            content = ""
        
        # Basic analysis
        purpose = self._determine_file_purpose(file_info, content)
        key_functions = self._extract_key_functions(content, file_info['language'])
        dependencies = self._extract_dependencies(content, file_info['language'])
        complexity_score = self._calculate_complexity(content, file_info)
        
        # Line-by-line analysis for code files
        line_analysis = self._analyze_lines_detailed(content, file_info['language'], file_path)
        
        # Enhanced AI analysis with line-by-line context
        ai_analysis = self._analyze_with_ai_enhanced(file_path, content, file_info, line_analysis)
        
        return FileInfo(
            file_path=file_path,
            file_name=file_info['file_name'],
            file_type=file_info['file_type'],
            file_size=file_info['file_size'],
            line_count=file_info['line_count'],
            language=file_info['language'],
            purpose=purpose,
            key_functions=key_functions,
            dependencies=dependencies,
            complexity_score=complexity_score,
            ai_analysis=ai_analysis,
            technical_contributions=[],
            research_potential="",
            line_analysis=line_analysis
        )
    
    def _determine_file_purpose(self, file_info: Dict[str, Any], content: str) -> str:
        """Determine file purpose based on name and content"""
        filename = file_info['file_name'].lower()
        language = file_info['language']
        
        if 'test' in filename or 'spec' in filename:
            return 'Testing'
        elif 'config' in filename or 'settings' in filename:
            return 'Configuration'
        elif 'readme' in filename or 'doc' in filename:
            return 'Documentation'
        elif filename in ['main.py', 'app.py', 'index.js', 'main.js', 'server.js']:
            return 'Main Application'
        elif filename in ['requirements.txt', 'package.json', 'pom.xml', 'build.gradle']:
            return 'Dependencies'
        elif language in ['HTML', 'CSS', 'JavaScript']:
            return 'Frontend'
        elif language in ['Python', 'Java', 'C++', 'C#', 'Go', 'Rust']:
            return 'Backend/Logic'
        elif language in ['SQL']:
            return 'Database'
        elif language in ['Dockerfile', 'YAML', 'JSON']:
            return 'Infrastructure'
        else:
            return 'Utility'
    
    def _extract_key_functions(self, content: str, language: str) -> List[str]:
        """Extract key functions/classes from file content"""
        functions = []
        
        if language == 'Python':
            import re
            # Find function definitions
            func_pattern = r'def\s+(\w+)\s*\('
            functions.extend(re.findall(func_pattern, content))
            
            # Find class definitions
            class_pattern = r'class\s+(\w+)'
            functions.extend(re.findall(class_pattern, content))
            
        elif language == 'JavaScript':
            import re
            # Find function declarations
            func_pattern = r'function\s+(\w+)\s*\('
            functions.extend(re.findall(func_pattern, content))
            
            # Find arrow functions
            arrow_pattern = r'const\s+(\w+)\s*=\s*\('
            functions.extend(re.findall(arrow_pattern, content))
            
        elif language == 'Java':
            import re
            # Find method definitions
            method_pattern = r'(?:public|private|protected)?\s*(?:static\s+)?\w+\s+(\w+)\s*\('
            functions.extend(re.findall(method_pattern, content))
            
            # Find class definitions
            class_pattern = r'class\s+(\w+)'
            functions.extend(re.findall(class_pattern, content))
            
        return functions[:10]  # Limit to 10 most important
    
    def _extract_dependencies(self, content: str, language: str) -> List[str]:
        """Extract dependencies from file content"""
        dependencies = []
        
        if language == 'Python':
            import re
            # Find import statements
            import_pattern = r'import\s+(\w+)'
            from_pattern = r'from\s+(\w+)'
            dependencies.extend(re.findall(import_pattern, content))
            dependencies.extend(re.findall(from_pattern, content))
            
        elif language == 'JavaScript':
            import re
            # Find require statements
            require_pattern = r'require\([\'"]([^\'"]+)[\'"]\)'
            dependencies.extend(re.findall(require_pattern, content))
            
            # Find import statements
            import_pattern = r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]'
            dependencies.extend(re.findall(import_pattern, content))
            
        elif language == 'Java':
            import re
            # Find import statements
            import_pattern = r'import\s+([\w.]+)'
            dependencies.extend(re.findall(import_pattern, content))
            
        return list(set(dependencies))[:15]  # Remove duplicates and limit
    
    def _calculate_complexity(self, content: str, file_info: Dict[str, Any]) -> int:
        """Calculate file complexity score (1-10)"""
        score = 1
        
        # Base score from line count
        if file_info['line_count'] > 1000:
            score += 3
        elif file_info['line_count'] > 500:
            score += 2
        elif file_info['line_count'] > 100:
            score += 1
        
        # Add score for file size
        if file_info['file_size'] > 100000:  # 100KB
            score += 2
        elif file_info['file_size'] > 10000:  # 10KB
            score += 1
        
        # Add score for complexity indicators
        complexity_indicators = ['if', 'for', 'while', 'try', 'catch', 'switch', 'case']
        for indicator in complexity_indicators:
            score += content.count(indicator) // 10
        
        return min(score, 10)
    
    def _analyze_with_ai(self, file_path: str, content: str, file_info: Dict[str, Any]) -> str:
        """Analyze file with AI"""
        try:
            if not self.model:
                return f"Basic analysis: {file_info['language']} file with {file_info['line_count']} lines implementing {self._determine_file_purpose(file_info, content)} functionality."
            
            # Truncate content if too long but keep important parts
            max_content_length = 6000
            if len(content) > max_content_length:
                # Keep first 3000 and last 1000 chars to preserve structure
                content = content[:3000] + "\n\n... [middle section truncated] ...\n\n" + content[-1000:]
            
            # Extract key patterns for better analysis
            key_functions = self._extract_key_functions(content, file_info['language'])
            dependencies = self._extract_dependencies(content, file_info['language'])
            
            prompt = f"""
            Analyze this {file_info['language']} code file for academic research paper generation. Provide SPECIFIC technical insights:
            
            FILE: {file_path}
            PURPOSE: {self._determine_file_purpose(file_info, content)}
            SIZE: {file_info['line_count']} lines, {file_info['file_size']} bytes
            KEY FUNCTIONS: {', '.join(key_functions[:8])}
            DEPENDENCIES: {', '.join(dependencies[:8])}
            
            CODE CONTENT:
            {content}
            
            Provide a detailed technical analysis (300-400 words) covering:
            
            1. FUNCTIONALITY: What specific functionality does this file implement? Be precise about what it does.
            
            2. TECHNICAL APPROACH: What algorithms, data structures, or design patterns are used? Identify specific technical concepts.
            
            3. ARCHITECTURE ROLE: How does this file fit into the larger system architecture? What is its responsibility?
            
            4. COMPLEXITY ANALYSIS: What makes this code complex or sophisticated? Identify challenging aspects.
            
            5. INNOVATION/CONTRIBUTIONS: What notable technical decisions, optimizations, or innovations are present?
            
            6. RESEARCH VALUE: Why would this code be interesting from an academic/research perspective?
            
            Focus on CONCRETE technical details, not generic descriptions. Mention specific functions, classes, algorithms, and patterns you observe.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            # Provide a more detailed fallback analysis
            key_functions = self._extract_key_functions(content, file_info['language'])
            dependencies = self._extract_dependencies(content, file_info['language'])
            purpose = self._determine_file_purpose(file_info, content)
            
            analysis = f"Technical Analysis of {file_path}:\n\n"
            analysis += f"This {file_info['language']} file implements {purpose} functionality with {file_info['line_count']} lines of code. "
            
            if key_functions:
                analysis += f"Key components include: {', '.join(key_functions[:5])}. "
            
            if dependencies:
                analysis += f"The file utilizes dependencies: {', '.join(dependencies[:5])}. "
            
            analysis += f"The code demonstrates {self._assess_complexity_level(file_info)} complexity "
            analysis += f"and follows {file_info['language']} best practices. "
            
            if 'class' in content.lower():
                analysis += "The implementation uses object-oriented programming principles. "
            
            if any(pattern in content.lower() for pattern in ['async', 'await', 'promise', 'callback']):
                analysis += "Asynchronous programming patterns are employed. "
            
            if any(pattern in content.lower() for pattern in ['test', 'assert', 'expect', 'mock']):
                analysis += "Testing methodologies and quality assurance practices are implemented. "
            
            analysis += f"AI analysis failed: {str(e)}"
            
            return analysis
    
    def _analyze_lines_detailed(self, content: str, language: str, file_path: str) -> Dict[str, Any]:
        """Perform detailed line-by-line analysis of code"""
        if not content.strip():
            return {"total_lines": 0, "analysis": {}}
        
        lines = content.split('\n')
        line_analysis = {
            "total_lines": len(lines),
            "analysis": {},
            "code_blocks": [],
            "functions": [],
            "classes": [],
            "imports": [],
            "variables": [],
            "comments": [],
            "technical_patterns": []
        }
        
        current_function = None
        current_class = None
        indent_level = 0
        
        for i, line in enumerate(lines, 1):
            line_info = self._analyze_single_line(line, i, language, current_function, current_class)
            line_analysis["analysis"][i] = line_info
            
            # Track code structures
            if line_info["type"] == "function_definition":
                current_function = line_info["function_name"]
                line_analysis["functions"].append({
                    "name": current_function,
                    "line": i,
                    "parameters": line_info.get("parameters", []),
                    "description": line_info["description"]
                })
            elif line_info["type"] == "class_definition":
                current_class = line_info["class_name"]
                line_analysis["classes"].append({
                    "name": current_class,
                    "line": i,
                    "description": line_info["description"]
                })
            elif line_info["type"] == "import":
                line_analysis["imports"].append({
                    "module": line_info["module"],
                    "line": i,
                    "description": line_info["description"]
                })
            elif line_info["type"] == "variable_assignment":
                line_analysis["variables"].append({
                    "name": line_info["variable_name"],
                    "line": i,
                    "value_type": line_info.get("value_type", "unknown"),
                    "description": line_info["description"]
                })
            elif line_info["type"] == "comment":
                line_analysis["comments"].append({
                    "line": i,
                    "content": line_info["content"],
                    "type": line_info.get("comment_type", "regular")
                })
            
            # Detect technical patterns
            if line_info.get("technical_pattern"):
                line_analysis["technical_patterns"].append({
                    "pattern": line_info["technical_pattern"],
                    "line": i,
                    "description": line_info["description"]
                })
        
        return line_analysis
    
    def _analyze_single_line(self, line: str, line_num: int, language: str, current_function: str, current_class: str) -> Dict[str, Any]:
        """Analyze a single line of code in detail"""
        stripped = line.strip()
        
        if not stripped:
            return {
                "type": "empty",
                "content": line,
                "description": "Empty line for code organization"
            }
        
        # Language-specific analysis
        if language == "JavaScript":
            return self._analyze_javascript_line(stripped, line_num, current_function)
        elif language == "Python":
            return self._analyze_python_line(stripped, line_num, current_function)
        elif language == "HTML":
            return self._analyze_html_line(stripped, line_num)
        elif language == "CSS":
            return self._analyze_css_line(stripped, line_num)
        else:
            return self._analyze_generic_line(stripped, line_num, language)
    
    def _analyze_javascript_line(self, line: str, line_num: int, current_function: str) -> Dict[str, Any]:
        """Analyze JavaScript line in detail"""
        import re
        
        # Function definitions
        if re.match(r'function\s+\w+', line) or re.match(r'const\s+\w+\s*=\s*\(.*\)\s*=>', line):
            func_match = re.search(r'function\s+(\w+)|const\s+(\w+)\s*=', line)
            func_name = func_match.group(1) or func_match.group(2) if func_match else "anonymous"
            return {
                "type": "function_definition",
                "function_name": func_name,
                "content": line,
                "description": f"Defines function '{func_name}' - a reusable code block that encapsulates specific functionality",
                "technical_pattern": "function_declaration"
            }
        
        # Variable declarations
        elif re.match(r'(let|const|var)\s+\w+', line):
            var_match = re.search(r'(let|const|var)\s+(\w+)', line)
            var_name = var_match.group(2) if var_match else "unknown"
            var_type = var_match.group(1) if var_match else "var"
            return {
                "type": "variable_assignment",
                "variable_name": var_name,
                "declaration_type": var_type,
                "content": line,
                "description": f"Declares {var_type} variable '{var_name}' - {self._get_js_var_description(var_type)}",
                "technical_pattern": "variable_declaration"
            }
        
        # Event listeners
        elif "addEventListener" in line:
            event_match = re.search(r"addEventListener\(['\"](\w+)['\"]", line)
            event_type = event_match.group(1) if event_match else "unknown"
            return {
                "type": "event_listener",
                "event_type": event_type,
                "content": line,
                "description": f"Attaches event listener for '{event_type}' event - enables interactive user interface behavior",
                "technical_pattern": "event_handling"
            }
        
        # DOM manipulation
        elif any(dom_method in line for dom_method in ["getElementById", "querySelector", "createElement"]):
            return {
                "type": "dom_manipulation",
                "content": line,
                "description": "DOM manipulation - dynamically modifies HTML document structure and content",
                "technical_pattern": "dom_interaction"
            }
        
        # Comments
        elif line.startswith("//") or line.startswith("/*"):
            return {
                "type": "comment",
                "content": line,
                "description": "Code documentation - explains implementation details for maintainability"
            }
        
        # Control structures
        elif re.match(r'(if|for|while|switch)\s*\(', line):
            control_type = re.match(r'(\w+)', line).group(1)
            return {
                "type": "control_structure",
                "control_type": control_type,
                "content": line,
                "description": f"Control flow statement ({control_type}) - manages program execution logic and decision making",
                "technical_pattern": "control_flow"
            }
        
        else:
            return self._analyze_generic_line(line, line_num, "JavaScript")
    
    def _analyze_python_line(self, line: str, line_num: int, current_function: str) -> Dict[str, Any]:
        """Analyze Python line in detail"""
        import re
        
        # Function definitions
        if line.startswith("def "):
            func_match = re.search(r'def\s+(\w+)', line)
            func_name = func_match.group(1) if func_match else "unknown"
            return {
                "type": "function_definition",
                "function_name": func_name,
                "content": line,
                "description": f"Defines function '{func_name}' - encapsulates reusable logic with defined input/output interface",
                "technical_pattern": "function_definition"
            }
        
        # Class definitions
        elif line.startswith("class "):
            class_match = re.search(r'class\s+(\w+)', line)
            class_name = class_match.group(1) if class_match else "unknown"
            return {
                "type": "class_definition",
                "class_name": class_name,
                "content": line,
                "description": f"Defines class '{class_name}' - blueprint for object-oriented programming with encapsulated data and methods",
                "technical_pattern": "oop_design"
            }
        
        # Imports
        elif line.startswith("import ") or line.startswith("from "):
            module_match = re.search(r'import\s+(\w+)|from\s+(\w+)', line)
            module_name = (module_match.group(1) or module_match.group(2)) if module_match else "unknown"
            return {
                "type": "import",
                "module": module_name,
                "content": line,
                "description": f"Imports module '{module_name}' - extends functionality by including external libraries and dependencies",
                "technical_pattern": "dependency_management"
            }
        
        else:
            return self._analyze_generic_line(line, line_num, "Python")
    
    def _analyze_html_line(self, line: str, line_num: int) -> Dict[str, Any]:
        """Analyze HTML line in detail"""
        import re
        
        # HTML tags
        tag_match = re.search(r'<(\w+)', line)
        if tag_match:
            tag_name = tag_match.group(1)
            return {
                "type": "html_element",
                "tag": tag_name,
                "content": line,
                "description": f"HTML element <{tag_name}> - {self._get_html_tag_description(tag_name)}",
                "technical_pattern": "markup_structure"
            }
        
        return self._analyze_generic_line(line, line_num, "HTML")
    
    def _analyze_css_line(self, line: str, line_num: int) -> Dict[str, Any]:
        """Analyze CSS line in detail"""
        import re
        
        # CSS selectors
        if line.endswith("{") or re.match(r'^[.#]?\w+.*{?$', line):
            return {
                "type": "css_selector",
                "content": line,
                "description": "CSS selector - targets HTML elements for styling and visual presentation",
                "technical_pattern": "styling_rules"
            }
        
        # CSS properties
        elif ":" in line and line.endswith(";"):
            prop_match = re.search(r'(\w+[-\w]*)\s*:', line)
            property_name = prop_match.group(1) if prop_match else "unknown"
            return {
                "type": "css_property",
                "property": property_name,
                "content": line,
                "description": f"CSS property '{property_name}' - controls visual styling and layout behavior",
                "technical_pattern": "visual_styling"
            }
        
        return self._analyze_generic_line(line, line_num, "CSS")
    
    def _analyze_generic_line(self, line: str, line_num: int, language: str) -> Dict[str, Any]:
        """Generic line analysis for any language"""
        return {
            "type": "code_statement",
            "content": line,
            "description": f"{language} code statement - implements specific program logic and functionality",
            "technical_pattern": "implementation_logic"
        }
    
    def _get_js_var_description(self, var_type: str) -> str:
        """Get description for JavaScript variable types"""
        descriptions = {
            "const": "immutable constant value that cannot be reassigned",
            "let": "block-scoped variable that can be reassigned within its scope",
            "var": "function-scoped variable with hoisting behavior"
        }
        return descriptions.get(var_type, "variable declaration")
    
    def _get_html_tag_description(self, tag: str) -> str:
        """Get description for HTML tags"""
        descriptions = {
            "div": "generic container element for grouping and styling content",
            "span": "inline container for styling text or small content sections",
            "p": "paragraph element for text content organization",
            "h1": "primary heading element for document structure hierarchy",
            "h2": "secondary heading element for content organization",
            "h3": "tertiary heading element for subsection titles",
            "a": "anchor element for hyperlinks and navigation",
            "img": "image element for displaying visual content",
            "button": "interactive button element for user actions",
            "input": "form input element for user data collection",
            "form": "form container for user input and data submission",
            "ul": "unordered list container for bullet-point content",
            "li": "list item element within ordered or unordered lists",
            "nav": "navigation container for site navigation links",
            "header": "page header section for top-level content",
            "footer": "page footer section for bottom content",
            "main": "main content area of the document",
            "section": "thematic content section for document organization"
        }
        return descriptions.get(tag.lower(), "HTML element for document structure and content")
    
    def _analyze_with_ai_enhanced(self, file_path: str, content: str, file_info: Dict[str, Any], line_analysis: Dict[str, Any]) -> str:
        """Enhanced AI analysis using line-by-line context"""
        try:
            if not self.model:
                return self._create_detailed_fallback_analysis(file_path, file_info, line_analysis)
            
            # Create summary of line analysis for AI context
            analysis_summary = self._create_line_analysis_summary(line_analysis)
            
            # Truncate content if too long but keep important parts
            max_content_length = 4000
            if len(content) > max_content_length:
                content = content[:2000] + "\n\n... [middle section truncated] ...\n\n" + content[-1000:]
            
            prompt = f"""
            Analyze this {file_info['language']} code file using DETAILED LINE-BY-LINE ANALYSIS for research paper generation:
            
            FILE: {file_path}
            LANGUAGE: {file_info['language']}
            TOTAL LINES: {line_analysis['total_lines']}
            
            DETAILED LINE ANALYSIS SUMMARY:
            - Functions Found: {len(line_analysis['functions'])}
            - Classes Found: {len(line_analysis['classes'])}
            - Import Statements: {len(line_analysis['imports'])}
            - Variables Declared: {len(line_analysis['variables'])}
            - Technical Patterns: {len(line_analysis['technical_patterns'])}
            
            KEY FUNCTIONS IDENTIFIED:
            {chr(10).join([f"- Line {f['line']}: {f['name']} - {f['description']}" for f in line_analysis['functions'][:5]])}
            
            TECHNICAL PATTERNS DETECTED:
            {chr(10).join([f"- Line {p['line']}: {p['pattern']} - {p['description']}" for p in line_analysis['technical_patterns'][:8]])}
            
            IMPORTS AND DEPENDENCIES:
            {chr(10).join([f"- Line {i['line']}: {i['module']} - {i['description']}" for i in line_analysis['imports'][:5]])}
            
            CODE CONTENT:
            {content}
            
            Based on this DETAILED LINE-BY-LINE ANALYSIS, provide a comprehensive technical analysis (400-500 words):
            
            1. IMPLEMENTATION ANALYSIS: Describe what specific functionality each major code section implements
            2. TECHNICAL ARCHITECTURE: Explain how the code is structured and organized
            3. ALGORITHMIC APPROACH: Detail the algorithms and logic patterns used
            4. CODE QUALITY ASSESSMENT: Evaluate the technical sophistication and best practices
            5. RESEARCH SIGNIFICANCE: Explain why this implementation is academically interesting
            
            Focus on SPECIFIC technical details from the line analysis. Mention actual function names, patterns, and implementation techniques.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            return self._create_detailed_fallback_analysis(file_path, file_info, line_analysis)
    
    def _create_line_analysis_summary(self, line_analysis: Dict[str, Any]) -> str:
        """Create a summary of line analysis for AI context"""
        summary = f"File contains {line_analysis['total_lines']} lines with detailed analysis:\n"
        
        if line_analysis['functions']:
            summary += f"Functions ({len(line_analysis['functions'])}): "
            summary += ", ".join([f"{f['name']} (line {f['line']})" for f in line_analysis['functions'][:3]])
            summary += "\n"
        
        if line_analysis['technical_patterns']:
            summary += f"Technical Patterns: "
            summary += ", ".join(list(set([p['pattern'] for p in line_analysis['technical_patterns']])))
            summary += "\n"
        
        return summary
    
    def _create_detailed_fallback_analysis(self, file_path: str, file_info: Dict[str, Any], line_analysis: Dict[str, Any]) -> str:
        """Create detailed fallback analysis using line-by-line data"""
        analysis = f"Detailed Technical Analysis of {file_path}:\n\n"
        
        analysis += f"IMPLEMENTATION OVERVIEW:\n"
        analysis += f"This {file_info['language']} file contains {line_analysis['total_lines']} lines implementing "
        
        if line_analysis['functions']:
            analysis += f"{len(line_analysis['functions'])} functions: "
            analysis += ", ".join([f"'{f['name']}'" for f in line_analysis['functions'][:5]])
            analysis += ". "
        
        if line_analysis['classes']:
            analysis += f"The code defines {len(line_analysis['classes'])} classes: "
            analysis += ", ".join([f"'{c['name']}'" for c in line_analysis['classes'][:3]])
            analysis += ". "
        
        analysis += f"\n\nTECHNICAL ARCHITECTURE:\n"
        if line_analysis['imports']:
            analysis += f"Dependencies include {len(line_analysis['imports'])} modules: "
            analysis += ", ".join([i['module'] for i in line_analysis['imports'][:5]])
            analysis += ". "
        
        if line_analysis['technical_patterns']:
            patterns = list(set([p['pattern'] for p in line_analysis['technical_patterns']]))
            analysis += f"Technical patterns implemented: {', '.join(patterns[:5])}. "
        
        analysis += f"\n\nCODE QUALITY METRICS:\n"
        analysis += f"- Total executable lines: {line_analysis['total_lines']}\n"
        analysis += f"- Function modularity: {len(line_analysis['functions'])} discrete functions\n"
        analysis += f"- Documentation: {len(line_analysis['comments'])} comment lines\n"
        analysis += f"- Variable management: {len(line_analysis['variables'])} declared variables\n"
        
        analysis += f"\n\nRESEARCH SIGNIFICANCE:\n"
        analysis += f"This implementation demonstrates {file_info['language']} best practices with "
        analysis += f"structured code organization and {self._assess_complexity_level(file_info)} complexity patterns."
        
        return analysis
    
    def _assess_complexity_level(self, file_info: Dict[str, Any]) -> str:
        """Assess complexity level based on file metrics"""
        complexity = self._calculate_complexity("", file_info)
        if complexity >= 8:
            return "high"
        elif complexity >= 5:
            return "moderate"
        else:
            return "low"
    
    def save_file_analysis(self, file_analyses: List[FileInfo], output_path: str) -> None:
        """Save file analyses to JSON with detailed line analysis"""
        data = {
            'total_files': len(file_analyses),
            'analysis_timestamp': str(Path().cwd()),
            'files': [asdict(file_info) for file_info in file_analyses],
            'detailed_analysis_available': True,
            'analysis_features': [
                'line_by_line_analysis',
                'function_detection',
                'technical_pattern_recognition',
                'dependency_mapping',
                'code_quality_metrics'
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Also save detailed line analysis separately for reference
        detailed_output_path = output_path.replace('.json', '_detailed.json')
        self._save_detailed_line_analysis(file_analyses, detailed_output_path)
    
    def _save_detailed_line_analysis(self, file_analyses: List[FileInfo], output_path: str) -> None:
        """Save detailed line-by-line analysis to separate JSON file"""
        detailed_data = {
            'analysis_type': 'detailed_line_analysis',
            'total_files': len(file_analyses),
            'files': {}
        }
        
        for file_info in file_analyses:
            if hasattr(file_info, 'ai_analysis') and 'DETAILED LINE ANALYSIS SUMMARY' in file_info.ai_analysis:
                detailed_data['files'][file_info.file_path] = {
                    'language': file_info.language,
                    'line_count': file_info.line_count,
                    'complexity': file_info.complexity_score,
                    'functions': file_info.key_functions,
                    'dependencies': file_info.dependencies,
                    'detailed_analysis': file_info.ai_analysis
                }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(detailed_data, f, indent=2, ensure_ascii=False)
    
    def load_file_analysis(self, input_path: str) -> List[FileInfo]:
        """Load file analyses from JSON"""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return [FileInfo(**file_data) for file_data in data['files']]
