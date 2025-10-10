"""
New GitHub Repository Analyzer
File-based analysis system with individual file processing
"""

import os
import tempfile
import shutil
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import git
import google.generativeai as genai
from dotenv import load_dotenv
from .file_analyzer import FileAnalyzer, FileInfo

load_dotenv()


@dataclass
class RepositoryInfo:
    """Data class for repository information"""
    name: str
    url: str
    type: str
    technologies: List[str]
    file_count: int
    line_count: int
    complexity_score: int
    has_tests: bool
    has_docs: bool
    main_files: List[str]
    file_analyses: List[FileInfo]


class NewGitHubAnalyzer:
    """New file-based GitHub repository analyzer"""
    
    def __init__(self):
        # Hardcoded API key for immediate functionality
        api_key = os.getenv('GEMINI_API_KEY') or 'AIzaSyCLhkBuuaMEsiiuDYM20hcRF1Ei1GiJu9Q'
        if api_key:
            genai.configure(api_key=api_key)
            try:
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            except Exception:
                try:
                    self.model = genai.GenerativeModel('gemini-2.5-flash')
                except Exception:
                    self.model = None
        else:
            self.model = None
        self.temp_dir: Optional[str] = None
        self.file_analyzer = FileAnalyzer()
        self._code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.rs', '.go', '.php', '.rb'}
    
    def analyze_repository(self, repo_url: str, page_count: int = 6) -> Dict[str, Any]:
        """
        Analyze a GitHub repository using file-based approach
        
        Args:
            repo_url: GitHub repository URL
            page_count: Target page count for paper
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Clone repository
            repo_path = self._clone_repository(repo_url)
            
            # Extract all files
            print("📁 Extracting files from repository...")
            files = self.file_analyzer.extract_all_files(repo_path)
            print(f"✅ Found {len(files)} files")
            
            # Analyze each file individually
            print("🔍 Analyzing individual files...")
            file_analyses = []
            for i, file_info in enumerate(files):
                if file_info['is_code']:  # Only analyze code files
                    print(f"  Analyzing {i+1}/{len([f for f in files if f['is_code']])}: {file_info['file_path']}")
                    try:
                        file_analysis = self.file_analyzer.analyze_file(
                            file_info['file_path'], 
                            repo_path, 
                            file_info
                        )
                        file_analyses.append(file_analysis)
                    except Exception as e:
                        print(f"    ⚠️  Error analyzing {file_info['file_path']}: {e}")
                        continue
            
            print(f"✅ Analyzed {len(file_analyses)} files")
            
            # Save file analyses to JSON
            analysis_file = os.path.join('generated_papers', f'file_analysis_{Path(repo_url).name}.json')
            os.makedirs('generated_papers', exist_ok=True)
            self.file_analyzer.save_file_analysis(file_analyses, analysis_file)
            print(f"💾 Saved file analyses to {analysis_file}")
            
            # Generate overall repository analysis
            print("🧠 Generating overall repository analysis...")
            repo_analysis = self._generate_repository_analysis(repo_url, files, file_analyses, page_count)
            
            # Clean up
            self._cleanup()
            
            return repo_analysis
            
        except Exception as e:
            self._cleanup()
            raise Exception(f"Repository analysis failed: {str(e)}")
    
    def _clone_repository(self, repo_url: str) -> str:
        """Clone GitHub repository to temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
        
        try:
            print(f"📥 Cloning repository: {repo_url}")
            git.Repo.clone_from(repo_url, self.temp_dir)
            print("✅ Repository cloned successfully")
            return self.temp_dir
        except Exception as e:
            raise Exception(f"Failed to clone repository: {str(e)}")
    
    def _generate_repository_analysis(self, repo_url: str, files: List[Dict], file_analyses: List[FileInfo], page_count: int) -> Dict[str, Any]:
        """Generate overall repository analysis from file analyses"""
        try:
            # Basic statistics
            repo_name = Path(repo_url).name
            total_files = len(files)
            code_files = len(file_analyses)
            # Count lines only from analyzed code files, not all files
            total_lines = sum(f.line_count for f in file_analyses)
            
            # Extract technologies
            # Only include meaningful code technologies
            allowed = {
                'Python','JavaScript','TypeScript','Java','C++','C','Rust','Go','PHP','Ruby','Swift','Kotlin','Scala','R','Objective-C','C#','HTML','CSS','SQL'
            }
            technologies = sorted(list(set(f.language for f in file_analyses if f.language in allowed)))
            
            # Determine project type
            project_type = self._determine_project_type(file_analyses)
            
            # Calculate complexity
            avg_complexity = sum(f.complexity_score for f in file_analyses) / len(file_analyses) if file_analyses else 0
            
            # Check for tests and docs
            has_tests = any('test' in f.file_name.lower() or 'spec' in f.file_name.lower() for f in file_analyses)
            has_docs = any('readme' in f.file_name.lower() or 'doc' in f.file_name.lower() for f in file_analyses)
            
            # Get main files
            main_files = [f.file_path for f in file_analyses if f.purpose in ['Main Application', 'Backend/Logic']]
            
            # Generate AI insights from all file analyses
            ai_insights = self._generate_ai_insights_from_files(repo_name, file_analyses, page_count)
            
            return {
                'repo_name': repo_name,
                'repo_url': repo_url,
                'project_type': project_type,
                'technologies': technologies,
                'file_count': total_files,
                'code_file_count': code_files,
                'line_count': total_lines,
                'complexity_score': int(avg_complexity),
                'has_tests': has_tests,
                'has_docs': has_docs,
                'main_files': main_files[:10],  # Top 10 main files
                'file_analyses': file_analyses,
                'page_count': page_count,
                'ai_insights': ai_insights
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate repository analysis: {str(e)}")
    
    def _determine_project_type(self, file_analyses: List[FileInfo]) -> str:
        """Determine project type from file analyses"""
        if not file_analyses:
            return "Unknown"
        
        # Count file purposes
        purposes = [f.purpose for f in file_analyses]
        
        if 'Frontend' in purposes and 'Backend/Logic' in purposes:
            return "Full-Stack Web Application"
        elif 'Frontend' in purposes:
            return "Frontend Application"
        elif 'Backend/Logic' in purposes:
            return "Backend Service/API"
        elif 'Testing' in purposes:
            return "Test Suite"
        elif 'Documentation' in purposes:
            return "Documentation Project"
        else:
            return "Software Library/Tool"
    
    def _generate_ai_insights_from_files(self, repo_name: str, file_analyses: List[FileInfo], page_count: int) -> Dict[str, str]:
        """Generate AI insights from all file analyses"""
        try:
            if not self.model:
                return self._get_default_insights(repo_name, file_analyses)
            
            # Prepare file summaries for AI
            file_summaries = []
            for f in file_analyses[:20]:  # Limit to top 20 files
                file_summaries.append(f"""
File: {f.file_path}
Language: {f.language}
Purpose: {f.purpose}
Lines: {f.line_count}
Complexity: {f.complexity_score}/10
Key Functions: {', '.join(f.key_functions[:5])}
AI Analysis: {f.ai_analysis[:200]}...
""")
            
            file_summary_text = "\n".join(file_summaries)
            
            # Count technologies
            tech_counts = {}
            for f in file_analyses:
                tech_counts[f.language] = tech_counts.get(f.language, 0) + 1
            
            # Generate comprehensive prompt
            prompt = f"""
            Analyze this software project for research paper generation based on individual file analyses:
            
            Project: {repo_name}
            Total Files Analyzed: {len(file_analyses)}
            Technologies: {', '.join(tech_counts.keys())}
            Target Paper Length: {page_count} pages
            
            File Analysis Summary:
            {file_summary_text}
            
            Provide comprehensive insights for a {page_count}-page research paper:
            
            1. Project Description (2-3 sentences): What this project does and its main purpose
            2. Technical Contributions (3-4 bullet points): Key technical innovations and contributions
            3. Research Potential (2-3 sentences): Why this project is worthy of academic research
            4. Key Findings (3-4 bullet points): Important discoveries and insights from the analysis
            5. Methodology Insights (2-3 sentences): Notable approaches and patterns used
            6. Innovation Areas (2-3 bullet points): Areas where this project shows innovation
            
            Format your response as:
            PROJECT_DESCRIPTION: [description]
            TECHNICAL_CONTRIBUTIONS: [bullet points]
            RESEARCH_POTENTIAL: [potential]
            KEY_FINDINGS: [findings]
            METHODOLOGY_INSIGHTS: [insights]
            INNOVATION_AREAS: [innovations]
            """
            
            response = self.model.generate_content(prompt)
            insights_text = response.text.strip()
            
            # Parse the response
            insights = self._parse_ai_response(insights_text)
            return insights
            
        except Exception as e:
            print(f"AI analysis failed: {e}")
            return self._get_default_insights(repo_name, file_analyses)
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, str]:
        """Parse AI response into structured insights"""
        insights = {}
        lines = response_text.split('\n')
        
        current_key = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if line.endswith(':'):
                # Save previous content
                if current_key and current_content:
                    insights[current_key] = '\n'.join(current_content).strip()
                
                # Start new section
                current_key = line[:-1].lower().replace(' ', '_')
                current_content = []
            elif current_key and line:
                current_content.append(line)
        
        # Save last section
        if current_key and current_content:
            insights[current_key] = '\n'.join(current_content).strip()
        
        return insights
    
    def _get_default_insights(self, repo_name: str, file_analyses: List[FileInfo]) -> Dict[str, str]:
        """Get default insights when AI is not available"""
        technologies = list(set(f.language for f in file_analyses if f.language != 'Unknown'))
        
        return {
            'project_description': f"{repo_name} is a software project implemented using {', '.join(technologies[:3])} technologies. The project demonstrates modern software development practices and contains {len(file_analyses)} analyzed files.",
            'technical_contributions': [
                "Modular architecture with clear separation of concerns",
                f"Implementation using {', '.join(technologies[:2])} technologies",
                "Professional code organization and structure"
            ],
            'research_potential': f"This project provides valuable insights into modern software development practices and could serve as a case study for academic research in software engineering.",
            'key_findings': [
                f"Project contains {len(file_analyses)} code files",
                f"Uses {len(technologies)} different programming languages",
                "Demonstrates professional development practices"
            ],
            'methodology_insights': "The project follows standard software development methodologies with clear file organization and modular design patterns.",
            'innovation_areas': [
                "Code organization and architecture",
                "Technology stack integration",
                "Development workflow implementation"
            ]
        }
    
    def _cleanup(self):
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                print("🧹 Cleaned up temporary files")
            except Exception as e:
                print(f"Warning: Could not clean up temporary files: {e}")
            finally:
                self.temp_dir = None
