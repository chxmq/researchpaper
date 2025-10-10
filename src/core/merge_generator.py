"""
Merge-based Paper Generator
Generates research papers by merging individual file analyses into journal templates
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass
import google.generativeai as genai
from dotenv import load_dotenv
from .file_analyzer import FileInfo

load_dotenv()


@dataclass
class PaperTemplate:
    """Data class for paper template information"""
    name: str
    description: str
    sections: List[str]
    format: str


class MergePaperGenerator:
    """Paper generator that merges file analyses into journal templates"""
    
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            try:
                self.model = genai.GenerativeModel('gemini-1.5-pro')
            except Exception:
                self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
        self.templates = self._load_templates()
    
    def generate_paper(self, analysis: Dict[str, Any], template_name: str) -> str:
        """
        Generate research paper by merging file analyses into template
        
        Args:
            analysis: Repository analysis with file analyses
            template_name: Name of the journal template
            
        Returns:
            Generated paper content
        """
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = self.templates[template_name]
        file_analyses = analysis.get('file_analyses', [])
        
        # Generate sections by merging file analyses
        sections = self._generate_sections_from_files(analysis, file_analyses, template)
        
        # Render template with sections
        return self._render_template(template, sections)

    def save_paper(self, content: str, filepath: str, format_type: str = 'latex') -> None:
        """Save paper to disk; if pdf, requires pdflatex installed"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        if format_type == 'latex' or filepath.endswith('.tex'):
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return
        if format_type == 'pdf' or filepath.endswith('.pdf'):
            # lightweight converter using a temp .tex and pdflatex
            import tempfile, subprocess, shutil
            with tempfile.TemporaryDirectory() as t:
                tex_path = os.path.join(t, 'paper.tex')
                with open(tex_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                try:
                    subprocess.run(['pdflatex','-interaction=nonstopmode','paper.tex'], cwd=t, check=True, capture_output=True)
                    shutil.copy2(os.path.join(t,'paper.pdf'), filepath)
                except FileNotFoundError:
                    raise Exception('pdflatex not found. Install a LaTeX distribution to compile PDFs.')
                except subprocess.CalledProcessError as e:
                    raise Exception('LaTeX compilation failed')
    
    def _generate_sections_from_files(self, analysis: Dict[str, Any], file_analyses: List[FileInfo], template: PaperTemplate) -> Dict[str, str]:
        """Generate paper sections by merging file analyses"""
        sections = {}
        
        for section in template.sections:
            if section == 'title':
                sections[section] = self._generate_title_from_files(analysis, file_analyses)
            elif section == 'abstract':
                sections[section] = self._generate_abstract_from_files(analysis, file_analyses)
            elif section == 'keywords':
                sections[section] = self._generate_keywords_from_files(analysis, file_analyses)
            elif section == 'introduction':
                sections[section] = self._generate_introduction_from_files(analysis, file_analyses)
            elif section == 'related_work':
                sections[section] = self._generate_related_work_from_files(analysis, file_analyses)
            elif section == 'methodology':
                sections[section] = self._generate_methodology_from_files(analysis, file_analyses)
            elif section == 'implementation':
                sections[section] = self._generate_implementation_from_files(analysis, file_analyses)
            elif section == 'results':
                sections[section] = self._generate_results_from_files(analysis, file_analyses)
            elif section == 'discussion':
                sections[section] = self._generate_discussion_from_files(analysis, file_analyses)
            elif section == 'conclusion':
                sections[section] = self._generate_conclusion_from_files(analysis, file_analyses)
            elif section == 'references':
                sections[section] = self._generate_references_from_files(analysis, file_analyses)
            else:
                sections[section] = self._generate_default_section_from_files(analysis, file_analyses, section)
        
        return sections
    
    def _generate_title_from_files(self, analysis: Dict[str, Any], file_analyses: List[FileInfo]) -> str:
        """Generate title based on file analyses"""
        try:
            if not self.model:
                return f"Analysis of {analysis['repo_name']}: A {analysis['project_type']} Implementation"
            
            # Get key files for title generation
            key_files = [f for f in file_analyses if f.purpose in ['Main Application', 'Backend/Logic']][:5]
            
            file_summary = "\n".join([
                f"- {f.file_path} ({f.language}): {f.purpose}"
                for f in key_files
            ])
            
            prompt = f"""
            Generate a research paper title for this software project based on file analysis:
            
            Project: {analysis['repo_name']}
            Type: {analysis['project_type']}
            Technologies: {', '.join(analysis['technologies'])}
            Key Files:
            {file_summary}
            
            Create a concise, academic title that highlights the main technical contribution.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except:
            return f"Analysis of {analysis['repo_name']}: A {analysis['project_type']} Implementation"
    
    def _generate_abstract_from_files(self, analysis: Dict[str, Any], file_analyses: List[FileInfo]) -> str:
        """Generate abstract based on file analyses"""
        try:
            if not self.model:
                return self._get_default_abstract(analysis, file_analyses)
            
            # Prepare file analysis summary
            file_summary = self._prepare_file_summary(file_analyses)
            
            prompt = f"""
            Write a high-quality research paper abstract for this software project based on detailed file analysis:
            
            Project: {analysis['repo_name']}
            Type: {analysis['project_type']}
            Technologies: {', '.join(analysis['technologies'])}
            Total Files: {len(file_analyses)}
            Page Count: {analysis.get('page_count', 6)}
            
            Detailed File Analysis Summary:
            {file_summary}
            
            Write a comprehensive, academic-quality abstract (300-400 words) that includes:
            1. Clear problem statement and research motivation
            2. Detailed project overview and system architecture
            3. Specific technical contributions and innovations
            4. Concrete findings and performance results
            5. Research significance and implications
            6. Novel approaches and methodologies used
            
            Make it sound like a professional academic paper with specific technical details and measurable outcomes.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except:
            return self._get_default_abstract(analysis, file_analyses)
    
    def _generate_keywords_from_files(self, analysis: Dict[str, Any], file_analyses: List[FileInfo]) -> str:
        """Generate keywords based on file analyses"""
        keywords = set(analysis['technologies'])
        
        # Add keywords from file purposes
        purposes = [f.purpose for f in file_analyses]
        if 'Frontend' in purposes:
            keywords.add('web development')
        if 'Backend/Logic' in purposes:
            keywords.add('software architecture')
        if 'Testing' in purposes:
            keywords.add('software testing')
        if 'Documentation' in purposes:
            keywords.add('software documentation')
        
        # Add keywords from languages
        languages = [f.language for f in file_analyses if f.language != 'Unknown']
        keywords.update(languages[:5])
        
        # Add general keywords
        keywords.update(['software engineering', 'code analysis', 'research'])
        
        return ', '.join(list(keywords)[:10])
    
    def _generate_introduction_from_files(self, analysis: Dict[str, Any], file_analyses: List[FileInfo]) -> str:
        """Generate introduction based on file analyses"""
        try:
            if not self.model:
                return self._get_default_introduction(analysis, file_analyses)
            
            file_summary = self._prepare_file_summary(file_analyses)
            
            prompt = f"""
            Write a detailed, academic-quality introduction section for a research paper about this software project:
            
            Project: {analysis['repo_name']}
            Type: {analysis['project_type']}
            Technologies: {', '.join(analysis['technologies'])}
            File Count: {len(file_analyses)}
            Page Count: {analysis.get('page_count', 6)}
            
            Detailed File Analysis Summary:
            {file_summary}
            
            Write a comprehensive introduction (600-1000 words) that includes:
            1. Background and research context with specific industry challenges
            2. Clear problem statement with concrete examples
            3. Detailed project overview and system scope
            4. Specific technical contributions and innovations
            5. Research objectives and methodology overview
            6. Paper organization and structure
            7. Related work positioning and gaps addressed
            
            Use specific technical terminology, include quantitative metrics where possible, and make it sound like a professional academic publication.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except:
            return self._get_default_introduction(analysis, file_analyses)
    
    def _generate_methodology_from_files(self, analysis: Dict[str, Any], file_analyses: List[FileInfo]) -> str:
        """Generate methodology based on file analyses"""
        try:
            if not self.model:
                return self._get_default_methodology(analysis, file_analyses)
            
            # Group files by purpose for methodology
            files_by_purpose = {}
            for f in file_analyses:
                if f.purpose not in files_by_purpose:
                    files_by_purpose[f.purpose] = []
                files_by_purpose[f.purpose].append(f)
            
            purpose_summary = "\n".join([
                f"- {purpose}: {len(files)} files"
                for purpose, files in files_by_purpose.items()
            ])
            
            prompt = f"""
            Write a comprehensive, academic-quality methodology section for a research paper about this software project:
            
            Project: {analysis['repo_name']}
            Type: {analysis['project_type']}
            Technologies: {', '.join(analysis['technologies'])}
            Total Files: {len(file_analyses)}
            
            Files by Purpose:
            {purpose_summary}
            
            Write a detailed methodology (800-1200 words) that includes:
            1. Research methodology and analysis framework
            2. Detailed file categorization and classification system
            3. Code analysis techniques and tools used
            4. Evaluation criteria and metrics
            5. Data collection and processing methodology
            6. Quality assurance and validation procedures
            7. Statistical analysis methods
            8. Experimental design and setup
            9. Limitations and assumptions
            10. Reproducibility considerations
            
            Use specific technical terminology, include detailed procedures, and make it sound like a rigorous academic research methodology.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except:
            return self._get_default_methodology(analysis, file_analyses)
    
    def _generate_implementation_from_files(self, analysis: Dict[str, Any], file_analyses: List[FileInfo]) -> str:
        """Generate implementation section based on file analyses"""
        try:
            if not self.model:
                return self._get_default_implementation(analysis, file_analyses)
            
            # Get key implementation files
            impl_files = [f for f in file_analyses if f.purpose in ['Main Application', 'Backend/Logic', 'Frontend']]
            
            file_details = "\n".join([
                f"- {f.file_path} ({f.language}): {f.ai_analysis[:150]}..."
                for f in impl_files[:10]
            ])
            
            prompt = f"""
            Write an implementation section for a research paper about this software project:
            
            Project: {analysis['repo_name']}
            Type: {analysis['project_type']}
            Technologies: {', '.join(analysis['technologies'])}
            
            Key Implementation Files:
            {file_details}
            
            Write a detailed implementation section (600-1000 words) that includes:
            - System architecture overview
            - Key components and modules
            - Technology stack details
            - Implementation patterns
            - Design decisions
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except:
            return self._get_default_implementation(analysis, file_analyses)
    
    def _generate_results_from_files(self, analysis: Dict[str, Any], file_analyses: List[FileInfo]) -> str:
        """Generate results section based on file analyses"""
        try:
            if not self.model:
                return self._get_default_results(analysis, file_analyses)
            
            # Prepare metrics from file analyses
            metrics = self._prepare_metrics_summary(file_analyses)
            
            prompt = f"""
            Write a results section for a research paper about this software project:
            
            Project: {analysis['repo_name']}
            Type: {analysis['project_type']}
            Technologies: {', '.join(analysis['technologies'])}
            
            Analysis Metrics:
            {metrics}
            
            Write a comprehensive results section (500-800 words) that includes:
            - Analysis findings
            - Code quality metrics
            - Technical achievements
            - Performance insights
            - Comparative analysis
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except:
            return self._get_default_results(analysis, file_analyses)
    
    def _generate_discussion_from_files(self, analysis: Dict[str, Any], file_analyses: List[FileInfo]) -> str:
        """Generate discussion section based on file analyses"""
        try:
            if not self.model:
                return self._get_default_discussion(analysis, file_analyses)
            
            # Get insights from file analyses
            insights = analysis.get('ai_insights', {})
            
            prompt = f"""
            Write a discussion section for a research paper about this software project:
            
            Project: {analysis['repo_name']}
            Type: {analysis['project_type']}
            Technologies: {', '.join(analysis['technologies'])}
            File Count: {len(file_analyses)}
            
            Key Insights:
            - Technical Contributions: {insights.get('technical_contributions', 'N/A')}
            - Research Potential: {insights.get('research_potential', 'N/A')}
            - Key Findings: {insights.get('key_findings', 'N/A')}
            
            Write a comprehensive discussion (500-800 words) that includes:
            - Interpretation of results
            - Implications of findings
            - Comparison with related work
            - Limitations and challenges
            - Future research directions
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except:
            return self._get_default_discussion(analysis, file_analyses)
    
    def _generate_conclusion_from_files(self, analysis: Dict[str, Any], file_analyses: List[FileInfo]) -> str:
        """Generate conclusion based on file analyses"""
        try:
            if not self.model:
                return self._get_default_conclusion(analysis, file_analyses)
            
            insights = analysis.get('ai_insights', {})
            
            prompt = f"""
            Write a conclusion section for a research paper about this software project:
            
            Project: {analysis['repo_name']}
            Type: {analysis['project_type']}
            Technologies: {', '.join(analysis['technologies'])}
            File Count: {len(file_analyses)}
            
            Key Insights:
            - Technical Contributions: {insights.get('technical_contributions', 'N/A')}
            - Key Findings: {insights.get('key_findings', 'N/A')}
            
            Write a comprehensive conclusion (300-500 words) that includes:
            - Summary of contributions
            - Key findings and insights
            - Impact and significance
            - Future work recommendations
            - Final remarks
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except:
            return self._get_default_conclusion(analysis, file_analyses)
    
    def _generate_references_from_files(self, analysis: Dict[str, Any], file_analyses: List[FileInfo]) -> str:
        """Generate references based on file analyses"""
        references = [
            "[1] GitHub Inc. (2023). GitHub: Where the world builds software. https://github.com",
            "[2] Software Engineering Institute. (2023). Software Architecture: Principles and Practices. Carnegie Mellon University.",
            "[3] IEEE Computer Society. (2023). IEEE Standard for Software Quality Assurance Processes. IEEE Std 730-2014."
        ]
        
        # Add technology-specific references
        technologies = analysis.get('technologies', [])
        if 'Python' in technologies:
            references.append("[4] Van Rossum, G. (2023). Python Programming Language. Python Software Foundation.")
        if 'JavaScript' in technologies:
            references.append("[5] Mozilla Developer Network. (2023). JavaScript Guide. Mozilla Foundation.")
        if 'Java' in technologies:
            references.append("[6] Oracle Corporation. (2023). Java Platform Documentation. Oracle Corporation.")
        
        return '\n'.join(references)
    
    def _generate_related_work_from_files(self, analysis: Dict[str, Any], file_analyses: List[FileInfo]) -> str:
        """Generate related work section"""
        return f"Previous work in {analysis['project_type']} has focused on various aspects of software development and implementation. This work builds upon existing methodologies while introducing novel approaches specific to {', '.join(analysis['technologies'][:2])} technologies."
    
    def _generate_default_section_from_files(self, analysis: Dict[str, Any], file_analyses: List[FileInfo], section: str) -> str:
        """Generate default section content"""
        return f"This section provides detailed analysis of the {analysis['repo_name']} project, focusing on its technical implementation and contributions to the field of software engineering."
    
    def _prepare_file_summary(self, file_analyses: List[FileInfo]) -> str:
        """Prepare summary of file analyses for AI prompts"""
        summary_lines = []
        for f in file_analyses[:15]:  # Limit to top 15 files
            summary_lines.append(f"""
File: {f.file_path}
Language: {f.language}
Purpose: {f.purpose}
Lines: {f.line_count}
Complexity: {f.complexity_score}/10
Key Functions: {', '.join(f.key_functions[:3])}
Analysis: {f.ai_analysis[:100]}...
""")
        return "\n".join(summary_lines)
    
    def _prepare_metrics_summary(self, file_analyses: List[FileInfo]) -> str:
        """Prepare metrics summary from file analyses"""
        total_lines = sum(f.line_count for f in file_analyses)
        avg_complexity = sum(f.complexity_score for f in file_analyses) / len(file_analyses) if file_analyses else 0
        
        languages = {}
        for f in file_analyses:
            languages[f.language] = languages.get(f.language, 0) + 1
        
        purposes = {}
        for f in file_analyses:
            purposes[f.purpose] = purposes.get(f.purpose, 0) + 1
        
        return f"""
Total Files: {len(file_analyses)}
Total Lines: {total_lines}
Average Complexity: {avg_complexity:.1f}/10
Languages: {', '.join(f'{k} ({v})' for k, v in languages.items())}
Purposes: {', '.join(f'{k} ({v})' for k, v in purposes.items())}
"""
    
    def _get_default_abstract(self, analysis: Dict[str, Any], file_analyses: List[FileInfo]) -> str:
        """Get default abstract when AI is not available"""
        return f"This paper presents a comprehensive analysis of {analysis['repo_name']}, a {analysis['project_type']} implementation. The project consists of {len(file_analyses)} files across {', '.join(analysis['technologies'][:3])} technologies, demonstrating modern software development practices and architectural patterns."
    
    def _get_default_introduction(self, analysis: Dict[str, Any], file_analyses: List[FileInfo]) -> str:
        """Get default introduction when AI is not available"""
        return f"This paper presents a detailed analysis of {analysis['repo_name']}, a {analysis['project_type']} implementation. The project demonstrates significant technical contributions in {', '.join(analysis['technologies'][:2])} and provides valuable insights into modern software development practices."
    
    def _get_default_methodology(self, analysis: Dict[str, Any], file_analyses: List[FileInfo]) -> str:
        """Get default methodology when AI is not available"""
        return f"Our methodology involved a comprehensive analysis of the {analysis['repo_name']} codebase using static code analysis techniques. We examined {len(file_analyses)} files containing {sum(f.line_count for f in file_analyses)} lines of code across {', '.join(analysis['technologies'])} technologies."
    
    def _get_default_implementation(self, analysis: Dict[str, Any], file_analyses: List[FileInfo]) -> str:
        """Get default implementation when AI is not available"""
        return f"The {analysis['repo_name']} implementation utilizes a {analysis['project_type'].lower()} architecture built with {', '.join(analysis['technologies'])}. The system consists of {len(file_analyses)} files organized in a modular structure."
    
    def _get_default_results(self, analysis: Dict[str, Any], file_analyses: List[FileInfo]) -> str:
        """Get default results when AI is not available"""
        avg_complexity = sum(f.complexity_score for f in file_analyses) / len(file_analyses) if file_analyses else 0
        return f"Our analysis of {analysis['repo_name']} revealed significant technical achievements. The project demonstrates an average complexity score of {avg_complexity:.1f}/10 across {len(file_analyses)} files."
    
    def _get_default_discussion(self, analysis: Dict[str, Any], file_analyses: List[FileInfo]) -> str:
        """Get default discussion when AI is not available"""
        return f"The analysis of {analysis['repo_name']} reveals several important technical contributions and research opportunities. The project demonstrates significant technical achievements and provides valuable insights into modern software development practices."
    
    def _get_default_conclusion(self, analysis: Dict[str, Any], file_analyses: List[FileInfo]) -> str:
        """Get default conclusion when AI is not available"""
        return f"This paper presented a comprehensive analysis of {analysis['repo_name']}, a {analysis['project_type']} implementation. Our study revealed significant technical contributions and demonstrated valuable insights into modern software development practices."
    
    def _load_templates(self) -> Dict[str, PaperTemplate]:
        """Load available paper templates"""
        return {
            'ieee_conference': PaperTemplate(
                name='IEEE Conference Paper',
                description='IEEE Xplore conference paper format',
                sections=['title', 'abstract', 'keywords', 'introduction', 'methodology', 
                         'implementation', 'results', 'discussion', 'conclusion', 'references'],
                format='latex'
            ),
            'ieee_journal': PaperTemplate(
                name='IEEE Journal Article',
                description='IEEE Xplore journal article format',
                sections=['title', 'abstract', 'keywords', 'introduction', 'related_work', 'methodology', 
                         'implementation', 'results', 'discussion', 'conclusion', 'references'],
                format='latex'
            ),
            'acm_conference': PaperTemplate(
                name='ACM Conference Paper',
                description='ACM Digital Library conference format',
                sections=['title', 'abstract', 'keywords', 'introduction', 'methodology',
                         'implementation', 'results', 'discussion', 'conclusion', 'references'],
                format='latex'
            ),
            'springer_conference': PaperTemplate(
                name='Springer Conference Paper',
                description='Springer conference proceedings format',
                sections=['title', 'abstract', 'keywords', 'introduction', 'methodology',
                         'implementation', 'results', 'discussion', 'conclusion', 'references'],
                format='latex'
            )
        }
    
    def _render_template(self, template: PaperTemplate, sections: Dict[str, str]) -> str:
        """Render template with generated content"""
        if 'ieee' in template.name.lower():
            return self._render_ieee_latex_template(sections, 'conference' in template.name.lower())
        elif 'acm' in template.name.lower():
            return self._render_acm_latex_template(sections)
        elif 'springer' in template.name.lower():
            return self._render_springer_latex_template(sections)
        else:
            return self._render_default_latex_template(sections)
    
    def _render_ieee_latex_template(self, sections: Dict[str, str], is_conference: bool = True) -> str:
        """Render IEEE LaTeX template"""
        return f"""\\documentclass[conference]{{IEEEtran}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{graphicx}}
\\usepackage{{cite}}
\\usepackage{{url}}

\\begin{{document}}

\\title{{{sections['title']}}}

\\author{{
\\IEEEauthorblockN{{Your Name}}
\\IEEEauthorblockA{{Department of Computer Science\\\\
University Name\\\\
City, Country\\\\
Email: your.email@university.edu}}
}}

\\maketitle

\\begin{{abstract}}
{sections['abstract']}
\\end{{abstract}}

\\begin{{IEEEkeywords}}
{sections['keywords']}
\\end{{IEEEkeywords}}

\\section{{Introduction}}
{sections['introduction']}

\\section{{Methodology}}
{sections['methodology']}

\\section{{Implementation}}
{sections['implementation']}

\\section{{Results}}
{sections['results']}

\\section{{Discussion}}
{sections['discussion']}

\\section{{Conclusion}}
{sections['conclusion']}

\\bibliographystyle{{IEEEtran}}
\\bibliography{{references}}

{sections['references']}

\\end{{document}}
"""
    
    def _render_acm_latex_template(self, sections: Dict[str, str]) -> str:
        """Render ACM LaTeX template"""
        return f"""\\documentclass{{acmart}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{graphicx}}

\\acmJournal{{ACM Journal}}
\\acmVolume{{1}}
\\acmNumber{{1}}
\\acmArticle{{1}}
\\acmYear{{2024}}
\\acmMonth{{January}}
\\acmDOI{{10.1145/0000000.0000000}}

\\begin{{document}}

\\title{{{sections['title']}}}

\\author{{Your Name}}
\\affiliation{{\\institution{{University Name}}}}
\\email{{your.email@university.edu}}

\\begin{{abstract}}
{sections['abstract']}
\\end{{abstract}}

\\keywords{{{sections['keywords']}}}

\\maketitle

\\section{{Introduction}}
{sections['introduction']}

\\section{{Methodology}}
{sections['methodology']}

\\section{{Implementation}}
{sections['implementation']}

\\section{{Results}}
{sections['results']}

\\section{{Discussion}}
{sections['discussion']}

\\section{{Conclusion}}
{sections['conclusion']}

\\bibliographystyle{{ACM-Reference-Format}}
\\bibliography{{references}}

{sections['references']}

\\end{{document}}
"""
    
    def _render_springer_latex_template(self, sections: Dict[str, str]) -> str:
        """Render Springer LaTeX template"""
        return f"""\\documentclass{{svjour3}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{graphicx}}

\\begin{{document}}

\\title{{{sections['title']}}}

\\author{{Your Name}}
\\institute{{University Name\\\\
Department of Computer Science\\\\
City, Country\\\\
\\email{{your.email@university.edu}}}}

\\date{{}}

\\maketitle

\\begin{{abstract}}
{sections['abstract']}
\\end{{abstract}}

\\keywords{{{sections['keywords']}}}

\\section{{Introduction}}
{sections['introduction']}

\\section{{Methodology}}
{sections['methodology']}

\\section{{Implementation}}
{sections['implementation']}

\\section{{Results}}
{sections['results']}

\\section{{Discussion}}
{sections['discussion']}

\\section{{Conclusion}}
{sections['conclusion']}

\\bibliographystyle{{spbasic}}
\\bibliography{{references}}

{sections['references']}

\\end{{document}}
"""
    
    def _render_default_latex_template(self, sections: Dict[str, str]) -> str:
        """Render default LaTeX template"""
        return f"""\\documentclass{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{graphicx}}

\\begin{{document}}

\\title{{{sections['title']}}}

\\author{{Your Name}}
\\affiliation{{University Name, Department of Computer Science, City, Country}}

\\begin{{abstract}}
{sections['abstract']}
\\end{{abstract}}

\\maketitle

\\section{{Introduction}}
{sections['introduction']}

\\section{{Methodology}}
{sections['methodology']}

\\section{{Implementation}}
{sections['implementation']}

\\section{{Results}}
{sections['results']}

\\section{{Discussion}}
{sections['discussion']}

\\section{{Conclusion}}
{sections['conclusion']}

\\bibliographystyle{{plain}}
\\bibliography{{references}}

{sections['references']}

\\end{{document}}
"""
