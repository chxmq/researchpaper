"""
Progressive Paper Generator
Generates research papers component-by-component to avoid token limits
"""

import os
from typing import Dict, Any, List
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class ProgressivePaperGenerator:
    """Generates research papers section by section"""
    
    def __init__(self):
        # Hardcoded API key for immediate functionality
        api_key = os.getenv('GEMINI_API_KEY') or 'AIzaSyCLhkBuuaMEsiiuDYM20hcRF1Ei1GiJu9Q'
        if api_key:
            genai.configure(api_key=api_key)
            try:
                # Use the latest flash model
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                print("✅ Using gemini-2.0-flash-exp model")
            except Exception as e:
                try:
                    self.model = genai.GenerativeModel('gemini-2.5-flash')
                    print("✅ Using gemini-2.5-flash model")
                except Exception as e2:
                    print(f"❌ Model initialization failed: {e}, {e2}")
                    self.model = None
        else:
            self.model = None
            print("❌ No API key found")
        
        # Define available templates - ONLY IEEE for now
        self.templates = {
            'ieee_conference': {
                'name': 'IEEE Conference Paper',
                'description': 'IEEE Xplore conference proceedings format',
                'format': 'latex'
            },
            'ieee_journal': {
                'name': 'IEEE Journal Paper',
                'description': 'IEEE Transactions journal format',
                'format': 'latex'
            }
        }
    
    def generate_paper(self, analysis: Dict[str, Any], template_name: str, 
                       page_count: int, authors: List[Dict[str, str]]) -> str:
        """Generate complete paper component by component"""
        
        print(f"📝 Starting component-wise generation for {page_count}-page paper...")
        
        # Step 1: Generate title
        print("  ✍️  Generating title...")
        title = self._generate_title(analysis)
        
        # Step 2: Generate abstract
        print("  ✍️  Generating abstract...")
        abstract = self._generate_abstract(analysis, page_count)
        
        # Step 3: Generate keywords
        print("  ✍️  Generating keywords...")
        keywords = self._generate_keywords(analysis)
        
        # Step 4: Generate introduction
        print("  ✍️  Generating introduction...")
        introduction = self._generate_introduction(analysis, page_count)
        
        # Step 5: Generate methodology
        print("  ✍️  Generating methodology...")
        methodology = self._generate_methodology(analysis, page_count)
        
        # Step 6: Generate implementation
        print("  ✍️  Generating implementation...")
        implementation = self._generate_implementation(analysis, page_count)
        
        # Step 7: Generate results
        print("  ✍️  Generating results...")
        results = self._generate_results(analysis, page_count)
        
        # Step 8: Generate discussion
        print("  ✍️  Generating discussion...")
        discussion = self._generate_discussion(analysis, page_count)
        
        # Step 9: Generate conclusion
        print("  ✍️  Generating conclusion...")
        conclusion = self._generate_conclusion(analysis, page_count)
        
        # Step 10: Generate references
        print("  ✍️  Generating references...")
        references = self._generate_references(analysis, page_count)
        
        # Step 11: Assemble paper with journal boilerplate
        print("  📋 Assembling paper with journal template...")
        paper = self._assemble_paper(
            template_name, title, authors, abstract, keywords,
            introduction, methodology, implementation, results,
            discussion, conclusion, references
        )
        
        print("✅ Paper generation complete!")
        return paper
    
    def _generate_title(self, analysis: Dict[str, Any]) -> str:
        """Generate paper title"""
        if not self.model:
            return f"Analysis of {analysis['repo_name']}: A {analysis['project_type']} Study"
        
        prompt = f"""Generate an academic research paper title for this software project:

Project: {analysis['repo_name']}
Type: {analysis['project_type']}
Technologies: {', '.join(analysis.get('technologies', [])[:5])}
Description: {analysis.get('ai_insights', {}).get('project_description', 'Software project')}

Requirements:
- Concise (10-15 words)
- Academic and professional
- Highlights main contribution
- Follows standard research title format

Generate ONLY the title, nothing else."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return f"A Comprehensive Analysis of {analysis['repo_name']}: Implementation and Evaluation"
    
    def _generate_abstract(self, analysis: Dict[str, Any], page_count: int) -> str:
        """Generate abstract"""
        word_count = min(350, 200 + (page_count - 4) * 30)
        
        # Prefer model with compact, structured context
        if self.model:
            try:
                compact = self._build_compact_context(analysis, limit_files=10, include_patterns=True)
                topics = self._infer_topics(analysis)
                prompt = f"""Write an IEEE-style abstract using ONLY the compact implementation context below.

PROJECT: {analysis['repo_name']} | TYPE: {analysis['project_type']} | TARGET LENGTH: {word_count} words max
DOMAINS: {', '.join(topics)}

COMPACT CONTEXT (no full code; per-file facts with line numbers where present):
{compact}

REQUIREMENTS:
- State the problem/context in 1-2 sentences based on detected domains
- Summarize the implemented approach grounded in the files/functions
- Highlight 2-3 concrete technical contributions (mention files or functions)
- Include 1-2 quantitative facts (files, LOC, complexity) from context
- Avoid generic phrases; do not invent features
Output ONLY the abstract text (no heading).
"""
                return self.model.generate_content(prompt).text.strip()
            except Exception:
                pass
        
        # Fallback: data-driven abstract from analysis only
            # Create detailed abstract from analysis data even without AI
            repo_name = analysis.get('repo_name', 'Unknown Repository')
            project_type = analysis.get('project_type', 'Software Project')
            technologies = analysis.get('technologies', [])
            file_count = analysis.get('file_count', 0)
            code_file_count = analysis.get('code_file_count', 0)
            line_count = analysis.get('line_count', 0)
            complexity = analysis.get('complexity_score', 0)
            
            # Get file analysis details for better content
            file_analyses = analysis.get('file_analyses', [])
            purposes = list(set(f.purpose for f in file_analyses if hasattr(f, 'purpose')))[:4]
            
            abstract = f"""This paper presents a comprehensive technical analysis of {repo_name}, """
            
            if project_type != 'Unknown':
                abstract += f"a {project_type} implementation. "
            else:
                abstract += f"a software system. "
            
            if technologies:
                abstract += f"The system is implemented using {', '.join(technologies[:4])} technologies "
            
            if code_file_count > 0:
                abstract += f"and comprises {code_file_count} analyzed code files containing {line_count:,} lines of implementation. "
            else:
                abstract += f"and consists of {file_count} total files. "
            
            if purposes:
                abstract += f"The architecture includes components for {', '.join(purposes[:3])}. "
            
            if complexity > 0:
                abstract += f"Code complexity analysis reveals an average complexity score of {complexity}/10, "
                if complexity >= 7:
                    abstract += "indicating sophisticated implementation patterns. "
                elif complexity >= 4:
                    abstract += "demonstrating moderate technical complexity. "
                else:
                    abstract += "showing well-structured, maintainable code. "
            
            abstract += f"Our systematic analysis examines the software architecture, implementation strategies, and technical contributions. "
            abstract += f"The findings provide insights into modern software development practices and demonstrate the system's technical merit for academic study."""
            
            return abstract
        
        # Get actual file information for context - focus on IMPLEMENTATION files
        file_analyses = analysis.get('file_analyses', [])
        
        # Filter for meaningful implementation files (not tests, docs, configs)
        impl_files = [f for f in file_analyses if hasattr(f, 'file_path') and 
                     f.purpose in ['Main Application', 'Backend/Logic', 'Frontend', 'API/Routes', 'Utility'] and
                     'test' not in f.file_path.lower() and 'readme' not in f.file_path.lower() and
                     f.line_count > 10][:15]  # Top 15 implementation files
        
        file_details = []
        for f in impl_files:
            detail = f"- {f.file_path} ({f.language}): {f.purpose}\n"
            detail += f"  Lines: {f.line_count}, Complexity: {f.complexity_score}/10\n"
            if f.key_functions:
                detail += f"  Key Functions: {', '.join(f.key_functions[:5])}\n"
            if f.dependencies:
                detail += f"  Dependencies: {', '.join(f.dependencies[:5])}\n"
            # Include a snippet of AI analysis for context
            if f.ai_analysis and len(f.ai_analysis) > 50:
                detail += f"  Analysis: {f.ai_analysis[:150]}...\n"
            file_details.append(detail)
        
        file_details_text = "\n".join(file_details)
        
        prompt = f"""Write an academic research paper abstract based on DETAILED CODE ANALYSIS:

PROJECT OVERVIEW:
- Name: {analysis['repo_name']}
- Type: {analysis['project_type']}
- Implementation Files: {len(impl_files)} analyzed
- Total Lines: {analysis.get('line_count', 0)}
- Technologies: {', '.join(analysis.get('technologies', [])[:8])}
- Average Complexity: {analysis.get('complexity_score', 0)}/10

DETAILED FILE ANALYSIS:
{file_details_text}

AI INSIGHTS FROM ACTUAL CODE:
{analysis.get('ai_insights', {}).get('project_description', 'Advanced software implementation')}

TECHNICAL CONTRIBUTIONS IDENTIFIED:
{chr(10).join(analysis.get('ai_insights', {}).get('technical_contributions', ['Modern architecture', 'Scalable design'])[:4])}

Based on this COMPREHENSIVE ANALYSIS of actual code files, write a {word_count}-word abstract:

1. BACKGROUND: Describe the technical problem this software solves (infer from file purposes and functions)
2. METHODOLOGY: Describe the actual implementation approach (based on technologies and architecture)
3. IMPLEMENTATION: Highlight key technical components (mention specific files/functions where relevant)
4. RESULTS: Present quantifiable findings ({len(impl_files)} files, {analysis.get('line_count', 0)} lines, complexity metrics)
5. SIGNIFICANCE: Explain the technical contributions and research value

Be SPECIFIC and TECHNICAL. Reference actual implementation details, not generic software descriptions."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"AI failed for abstract, using detailed fallback: {e}")
            # Use the detailed fallback logic when AI fails
            return self._generate_abstract({'repo_name': analysis['repo_name'], 'project_type': analysis['project_type'], 'technologies': analysis.get('technologies', []), 'file_count': analysis.get('file_count', 0), 'code_file_count': 0, 'line_count': analysis.get('line_count', 0), 'complexity_score': analysis.get('complexity_score', 0), 'file_analyses': analysis.get('file_analyses', [])}, word_count)
    
    def _generate_keywords(self, analysis: Dict[str, Any]) -> str:
        """Generate keywords"""
        keywords = set()
        keywords.update(analysis.get('technologies', [])[:5])
        keywords.add(analysis.get('project_type', 'Software'))
        keywords.update(['software engineering', 'implementation', 'analysis'])
        return ', '.join(list(keywords)[:8])
    
    def _generate_introduction(self, analysis: Dict[str, Any], page_count: int) -> str:
        """Generate introduction section"""
        word_count = min(1000, 400 + (page_count - 4) * 120)
        
        # Prefer model with compact, structured context
        if self.model:
            try:
                compact = self._build_compact_context(analysis, limit_files=14, include_patterns=True)
                topics = self._infer_topics(analysis)
                prompt = f"""Write an IEEE Introduction using ONLY the context below. Use LaTeX subsections.

PROJECT: {analysis['repo_name']} | TYPE: {analysis['project_type']} | TARGET: ~{word_count} words
DOMAINS: {', '.join(topics)}

CONTEXT:
{compact}

STRUCTURE:
\\subsection{Background} - describe the technical problem/domain this code addresses
\\subsection{Motivation} - why this approach/stack matters for the domain
\\subsection{Contributions} - 3-5 bullet points referencing real files/functions/patterns
\\subsection{Organization} - map of remaining sections

RULES:
- Cite specific files and functions with line numbers where provided (e.g., core/rag.py: generate_solution@142)
- Avoid generic wording; no invented features
Output ONLY the section body (no top-level section header).
"""
                return self.model.generate_content(prompt).text.strip()
            except Exception:
                pass
        
        # Fallback: data-driven intro from analysis
            # Create detailed introduction from analysis data even without AI
            repo_name = analysis.get('repo_name', 'Unknown Repository')
            project_type = analysis.get('project_type', 'Software Project')
            technologies = analysis.get('technologies', [])
            file_count = analysis.get('file_count', 0)
            code_file_count = analysis.get('code_file_count', 0)
            line_count = analysis.get('line_count', 0)
            complexity_score = analysis.get('complexity_score', 0)
            
            # Get detailed file analysis for better content
            file_analyses = analysis.get('file_analyses', [])
            purposes = list(set(f.purpose for f in file_analyses if hasattr(f, 'purpose')))
            languages = list(set(f.language for f in file_analyses if hasattr(f, 'language') and f.language != 'Unknown'))
            
            intro = f"""\\subsection{{Background and Context}}
The {repo_name} project represents """
            
            if project_type != 'Unknown':
                intro += f"a {project_type} implementation that demonstrates "
            else:
                intro += f"a software system that showcases "
            
            if technologies:
                intro += f"modern development practices using {', '.join(technologies[:3])} technologies. "
            else:
                intro += f"contemporary software engineering principles. "
            
            if code_file_count > 0:
                intro += f"The system comprises {code_file_count} analyzed code files with {line_count:,} lines of implementation, "
                if languages:
                    intro += f"primarily developed in {', '.join(languages[:3])}. "
                else:
                    intro += f"representing a substantial codebase. "
            
            intro += f"""

\\subsection{{Problem Statement and Motivation}}
In the contemporary software development landscape, the analysis of existing systems provides valuable insights into architectural patterns, implementation strategies, and technical innovations. """
            
            if purposes:
                intro += f"The {repo_name} project addresses software engineering challenges through components handling {', '.join(purposes[:3])}, "
            
            intro += f"""making it an excellent candidate for academic study and technical evaluation.

\\subsection{{Research Objectives}}
The primary objectives of this comprehensive analysis are to:
\\begin{{itemize}}
\\item Examine the software architecture and design patterns employed in {repo_name}"""
            
            if code_file_count > 0:
                intro += f"""
\\item Analyze code quality metrics and complexity patterns across {code_file_count} implementation files
\\item Evaluate the technical sophistication and innovation present in the {line_count:,}-line codebase"""
            
            if technologies:
                intro += f"""
\\item Assess the integration and utilization of {len(technologies)} identified technologies: {', '.join(technologies[:4])}"""
            
            intro += f"""
\\item Document architectural decisions and their implications for system maintainability
\\end{{itemize}}

\\subsection{{Key Contributions}}
This analysis provides several significant contributions to the understanding of modern software systems:
\\begin{{itemize}}"""
            
            if code_file_count > 0:
                intro += f"""
\\item Systematic analysis of {code_file_count} code files totaling {line_count:,} lines of implementation"""
            
            if technologies:
                intro += f"""
\\item Technical evaluation of {len(technologies)} technologies: {', '.join(technologies[:5])}"""
            
            if complexity_score > 0:
                intro += f"""
\\item Complexity assessment revealing an average score of {complexity_score}/10, """
                if complexity_score >= 7:
                    intro += "indicating sophisticated architectural patterns"
                elif complexity_score >= 4:
                    intro += "demonstrating balanced complexity management"
                else:
                    intro += "showing well-structured, maintainable design"
            
            if purposes:
                intro += f"""
\\item Architectural analysis of components spanning {', '.join(purposes[:4])} functionality"""
            
            intro += f"""
\\item Documentation of implementation strategies and design decisions suitable for academic reference
\\end{{itemize}}

\\subsection{{Paper Organization}}
The remainder of this paper is structured as follows: Section II presents the systematic methodology employed for code analysis and evaluation, Section III details the implementation architecture and technical components, Section IV presents quantitative results and qualitative findings, Section V discusses the implications and significance of the analysis, and Section VI concludes with key insights and future research directions."""
            
            return intro
        
        # Get actual file details - focus on IMPLEMENTATION, not docs
        file_analyses = analysis.get('file_analyses', [])[:20]
        
        # Get IMPLEMENTATION files (exclude tests, docs, configs)
        impl_files = [f for f in file_analyses if hasattr(f, 'purpose') and 
                     f.purpose in ['Main Application', 'Backend/Logic', 'Frontend/UI', 'API/Routes'] and
                     'test' not in f.file_path.lower() and 'readme' not in f.file_path.lower()][:10]
        
        # Build detailed code context
        code_details = []
        for f in impl_files:
            if hasattr(f, 'file_path'):
                details = f"FILE: {f.file_path} ({f.line_count} lines)\n"
                details += f"  Language: {f.language}\n"
                details += f"  Purpose: {f.purpose}\n"
                if f.key_functions:
                    details += f"  Key Functions: {', '.join(f.key_functions[:5])}\n"
                if f.dependencies:
                    details += f"  Dependencies: {', '.join(f.dependencies[:5])}\n"
                code_details.append(details)
        
        code_context = "\n".join(code_details)
        
        prompt = f"""Write IEEE conference paper introduction based on ACTUAL CODE IMPLEMENTATION (NOT README):

PROJECT METADATA:
- Name: {analysis['repo_name']}
- Type: {analysis['project_type']}
- Languages: {', '.join(analysis.get('technologies', [])[:5])}
- Code Files: {analysis.get('code_file_count', 0)}
- Total Lines: {analysis.get('line_count', 0)}
- Complexity: {analysis.get('complexity_score', 0)}/10

ACTUAL IMPLEMENTATION FILES (focus on these):
{code_context}

INSTRUCTIONS:
Write a {word_count}-word IEEE-style introduction with proper LaTeX formatting:

\\subsection{{Background}}
- Describe the technical problem this code solves
- Based on actual functions and dependencies shown above

\\subsection{{Motivation}}  
- Why this implementation matters (based on technologies used)
- Real-world applications (infer from code structure)

\\subsection{{Contributions}}
- Specific technical contributions (based on actual files/functions)
- Quantifiable metrics: {analysis.get('code_file_count', 0)} files, {analysis.get('line_count', 0)} LOC

\\subsection{{Organization}}
- Paper structure overview

CRITICAL: Use ONLY information from the actual code files above. Do NOT make up features or capabilities."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"AI failed for introduction, using detailed fallback: {e}")
            # Use the detailed fallback logic when AI fails
            return self._generate_introduction({'repo_name': analysis['repo_name'], 'project_type': analysis['project_type'], 'technologies': analysis.get('technologies', []), 'file_count': analysis.get('file_count', 0), 'code_file_count': 0, 'line_count': analysis.get('line_count', 0), 'complexity_score': analysis.get('complexity_score', 0), 'file_analyses': analysis.get('file_analyses', [])}, page_count)
    
    def _generate_methodology(self, analysis: Dict[str, Any], page_count: int) -> str:
        """Generate methodology section"""
        word_count = min(1200, 500 + (page_count - 4) * 140)
        
        if not self.model:
            return "Methodology section."
        
        prompt = f"""Write a detailed methodology section for this research paper:

Project: {analysis['repo_name']}
Files Analyzed: {analysis.get('code_file_count', 0)}
Total Lines: {analysis.get('line_count', 0)}
Target Word Count: {word_count} words

Include:
1. Research approach and framework
2. Data collection methods (code extraction, file analysis)
3. Analysis techniques and tools
4. Evaluation criteria and metrics
5. Quality assurance procedures

Use academic language and include LaTeX subsections. Write ONLY the methodology content."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return "Our methodology involved comprehensive code analysis and evaluation."
    
    def _generate_implementation(self, analysis: Dict[str, Any], page_count: int) -> str:
        """Generate implementation section"""
        word_count = min(1400, 600 + (page_count - 4) * 160)
        # Prefer model with compact per-file summaries including line numbers
        if self.model:
            try:
                compact = self._build_compact_context(analysis, limit_files=12, include_patterns=True)
                topics = self._infer_topics(analysis)
                prompt = f"""Write the Implementation section using ONLY the compact context below. Use LaTeX subsections.

PROJECT: {analysis['repo_name']} | TYPE: {analysis['project_type']} | TARGET: ~{word_count} words
DOMAINS: {', '.join(topics)}

CONTEXT (per-file summaries with functions@line, imports@line, patterns):
{compact}

STRUCTURE:
\\subsection{{System Architecture}} - actual file organization and responsibilities
\\subsection{{Core Components}} - per-file descriptions; cite functions with line numbers
\\subsection{{Technology Integration}} - how the stack is used in code
\\subsection{{Implementation Patterns}} - patterns detected (e.g., event_handling xN)
\\subsection{{Technical Challenges}} - inferred from complexity and structure

RULES:
- Do NOT invent features; use only the provided summaries
- Cite specific files and functions with line numbers where available
Output ONLY the section body.
"""
                return self.model.generate_content(prompt).text.strip()
            except Exception:
                pass

        # Fallback: data-driven section from analysis
            # Create detailed implementation section from analysis data
            repo_name = analysis.get('repo_name', 'Unknown Repository')
            project_type = analysis.get('project_type', 'Software Project')
            technologies = analysis.get('technologies', [])
            file_analyses = analysis.get('file_analyses', [])
            
            impl = f"""\\subsection{{System Architecture Overview}}
The {repo_name} project implements a comprehensive {project_type.lower()} architecture utilizing {', '.join(technologies[:3])} technologies. """
            
            if len(file_analyses) > 0:
                total_lines = sum(getattr(f, 'line_count', 0) for f in file_analyses)
                impl += f"The system comprises {len(file_analyses)} analyzed files containing {total_lines:,} lines of code, demonstrating substantial implementation effort and technical sophistication."
            
            impl += f"""

\\subsection{{Technical Implementation Details}}
The codebase analysis reveals a well-structured implementation with the following key components:"""
            
            # Add detailed analysis of each file
            for i, file_info in enumerate(file_analyses[:5]):
                if hasattr(file_info, 'file_path'):
                    file_path = file_info.file_path
                    purpose = file_info.purpose
                    key_functions = file_info.key_functions
                    language = file_info.language
                    line_count = file_info.line_count
                    complexity = file_info.complexity_score
                    
                    impl += f"""

\\subsubsection{{{file_path} - {language} Implementation}}
This {language} file ({line_count} lines, complexity: {complexity}/10) serves as the primary {purpose.lower()} component. """
                    
                    if key_functions:
                        impl += f"The implementation includes {len(key_functions)} key functions: {', '.join(key_functions[:5])}. "
                    
                    if complexity >= 7:
                        impl += "The high complexity score indicates sophisticated algorithmic implementations and advanced programming patterns."
                    elif complexity >= 4:
                        impl += "The moderate complexity demonstrates balanced code organization with clear functional separation."
                    else:
                        impl += "The low complexity reflects clean, maintainable code structure following best practices."
            
            impl += f"""
\\subsection{{Technology Stack Details}}
The implementation leverages a comprehensive technology stack including:
\\begin{{itemize}}
\\item Primary Languages: {', '.join(set([f.get('language', 'Unknown') for f in file_analyses if isinstance(f, dict)]))[:3]}
\\item Key Technologies: {', '.join(technologies[:5])}
\\item Development Framework: Modern software engineering practices
\\end{{itemize}}

\\subsection{{Design Patterns and Principles}}
The codebase demonstrates adherence to several important design principles:
\\begin{{itemize}}
\\item Modular architecture with clear separation of concerns
\\item Consistent coding standards and naming conventions
\\item Effective use of object-oriented programming concepts
\\item Implementation of scalable and maintainable code structures
\\end{{itemize}}

\\subsection{{Implementation Challenges}}
The development of {repo_name} involved addressing several technical challenges including complexity management, scalability considerations, and maintaining code quality across multiple components."""
            
            return impl
        
        file_analyses = analysis.get('file_analyses', [])
        
        # Get CORE implementation files with detailed analysis
        core_files = [f for f in file_analyses if hasattr(f, 'file_path') and 
                     f.purpose in ['Main Application', 'Backend/Logic', 'Frontend', 'API/Routes'] and
                     'test' not in f.file_path.lower() and 'readme' not in f.file_path.lower() and
                     f.line_count > 20][:12]  # Top 12 core files
        
        # Create comprehensive file analysis USING LINE-BY-LINE DATA
        file_summary = []
        for f in core_files:
            details = f"FILE: {f.file_path}\n"
            details += f"  Language: {f.language} | Purpose: {f.purpose} | Lines: {f.line_count} | Complexity: {f.complexity_score}/10\n"
            
            # Use detailed line analysis when available
            line_analysis = getattr(f, 'line_analysis', None)
            if line_analysis:
                # Functions with line numbers
                functions = line_analysis.get('functions', [])
                if functions:
                    fn_lines = [f"{fn['name']} (line {fn['line']})" for fn in functions[:6] if 'name' in fn and 'line' in fn]
                    details += f"  Functions: {', '.join(fn_lines)}\n"
                
                # Imports
                imports = line_analysis.get('imports', [])
                if imports:
                    imp_list = [f"{imp['module']} (line {imp['line']})" for imp in imports[:5] if 'module' in imp and 'line' in imp]
                    details += f"  Imports: {', '.join(imp_list)}\n"
                
                # Variables and comments summary
                variables_count = len(line_analysis.get('variables', []))
                comments_count = len(line_analysis.get('comments', []))
                details += f"  Variables: {variables_count} | Comments: {comments_count}\n"
                
                # Technical patterns summary (count per pattern)
                patterns = line_analysis.get('technical_patterns', [])
                if patterns:
                    pattern_counts = {}
                    for p in patterns:
                        key = p.get('pattern', 'unknown')
                        pattern_counts[key] = pattern_counts.get(key, 0) + 1
                    top_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:6]
                    details += "  Patterns: " + ", ".join([f"{k} x{v}" for k, v in top_patterns]) + "\n"
                
                # HTML/CSS specific aggregates
                try:
                    if f.language in ['HTML', 'CSS'] and 'analysis' in line_analysis:
                        type_counts = {}
                        tag_counts = {}
                        for entry in line_analysis['analysis'].values():
                            t = entry.get('type')
                            if t:
                                type_counts[t] = type_counts.get(t, 0) + 1
                            if f.language == 'HTML' and t == 'html_element':
                                tag = entry.get('tag', 'unknown')
                                tag_counts[tag] = tag_counts.get(tag, 0) + 1
                        if type_counts:
                            details += "  Elements: " + ", ".join([f"{k}:{v}" for k, v in list(type_counts.items())[:6]]) + "\n"
                        if tag_counts:
                            top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:6]
                            details += "  Top HTML tags: " + ", ".join([f"<{k}> x{v}" for k, v in top_tags]) + "\n"
                except Exception:
                    pass
            else:
                # Fallback to basic function/dependency info
                if f.key_functions:
                    details += f"  Key Functions: {', '.join(f.key_functions[:6])}\n"
                if f.dependencies:
                    details += f"  Dependencies: {', '.join(f.dependencies[:6])}\n"
            
            file_summary.append(details)
        
        file_details = "\n".join(file_summary)
        
        prompt = f"""Write a comprehensive implementation section based on DETAILED CODE ANALYSIS:

PROJECT METADATA:
- Name: {analysis['repo_name']} | Type: {analysis['project_type']}
- Core Implementation Files: {len(core_files)}
- Total Lines: {analysis.get('line_count', 0)} | Average Complexity: {analysis.get('complexity_score', 0)}/10
- Technologies: {', '.join(analysis.get('technologies', [])[:8])}

COMPREHENSIVE FILE-BY-FILE ANALYSIS:
{file_details}

AI-IDENTIFIED TECHNICAL CONTRIBUTIONS:
{chr(10).join(analysis.get('ai_insights', {}).get('technical_contributions', ['Advanced architecture'])[:5])}

INNOVATION AREAS:
{chr(10).join(analysis.get('ai_insights', {}).get('innovation_areas', ['Modern design patterns'])[:3])}

Based on this DETAILED ANALYSIS of {len(core_files)} core implementation files, write a {word_count}-word implementation section with LaTeX formatting:

\\subsection{{System Architecture}}
- Describe the actual file organization and architecture (reference specific files)
- Explain how the {len(core_files)} core files work together

\\subsection{{Core Components}}
- Detail each major component (mention specific files, their functions, and purposes)
- Explain the technical approach used in key files

\\subsection{{Technology Integration}}
- Describe how the {len(analysis.get('technologies', []))} technologies are integrated
- Reference actual dependencies and frameworks used

\\subsection{{Implementation Patterns}}
- Identify design patterns from the actual code structure
- Mention specific programming techniques observed

\\subsection{{Technical Innovations}}
- Highlight notable technical decisions and innovations
- Reference complexity metrics and sophisticated implementations

CRITICAL: Use SPECIFIC file names, function names, and technical details from the analysis above. NO generic descriptions."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return "The implementation follows modern software engineering practices."
    
    def _generate_results(self, analysis: Dict[str, Any], page_count: int) -> str:
        """Generate results section"""
        word_count = min(1200, 500 + (page_count - 4) * 140)
        
        if self.model:
            try:
                compact = self._build_compact_context(analysis, limit_files=12, include_patterns=True)
                prompt = f"""Write a data-driven Results section using ONLY the context below. Use LaTeX where appropriate.

PROJECT: {analysis['repo_name']} | TARGET: ~{word_count} words

CONTEXT:
{compact}

CONTENT TO INCLUDE:
- Quantitative metrics: files, LOC, average complexity; language distribution if present
- Summaries: top technical patterns with counts; functions-per-file highlights
- Optional: one small LaTeX table listing 3–5 key files with LOC and complexity

RULES:
- Use only numbers derivable from the context
- Avoid generic phrases; be specific
Output ONLY the section body.
"""
                return self.model.generate_content(prompt).text.strip()
            except Exception:
                pass
        return "Results and analysis are derived from the code metrics and detected patterns in the repository."
    
    def _generate_discussion(self, analysis: Dict[str, Any], page_count: int) -> str:
        """Generate discussion section"""
        word_count = min(1200, 500 + (page_count - 4) * 140)
        
        if self.model:
            try:
                compact = self._build_compact_context(analysis, limit_files=10, include_patterns=True)
                topics = self._infer_topics(analysis)
                prompt = f"""Write a critical Discussion using ONLY the context below.

PROJECT: {analysis['repo_name']} | TYPE: {analysis['project_type']} | TARGET: ~{word_count} words
DOMAINS: {', '.join(topics)}

CONTEXT:
{compact}

Include:
1) Interpretation of the specific results and what they imply about the implementation
2) Relation to domain practices suggested by the detected technologies/topics
3) Realistic limitations grounded in the context (e.g., missing tests, single-tech stack)
4) Implications for maintainability or scalability based on patterns/complexity

RULES:
- No generic language; tie claims to files/functions/patterns
Output ONLY the section body.
"""
                return self.model.generate_content(prompt).text.strip()
            except Exception:
                pass
        return "The discussion interprets code-derived metrics and patterns to assess implementation trade-offs and limitations."
    
    def _generate_conclusion(self, analysis: Dict[str, Any], page_count: int) -> str:
        """Generate conclusion section"""
        word_count = min(600, 250 + (page_count - 4) * 70)
        
        if self.model:
            try:
                compact = self._build_compact_context(analysis, limit_files=8, include_patterns=True)
                prompt = f"""Write a concise Conclusion using ONLY the context below.

PROJECT: {analysis['repo_name']} | TARGET: ~{word_count} words

CONTEXT:
{compact}

Include:
- Concrete contributions grounded in the files and functions
- One-sentence recap of quantitative findings (files, LOC, complexity)
- 2–3 practical implications or future work suggestions

RULES:
- No generic filler; reference real artifacts
Output ONLY the section body.
"""
                return self.model.generate_content(prompt).text.strip()
            except Exception:
                pass
        return "The conclusion summarizes concrete code-derived contributions and outlines pragmatic next steps."
    
    def _generate_references(self, analysis: Dict[str, Any], page_count: int) -> str:
        """Generate references via model; fallback to dynamic official docs based on tech/topics."""
        if self.model:
            try:
                compact = self._build_compact_context(analysis, limit_files=10, include_patterns=False)
                topics = self._infer_topics(analysis)
                target_refs = max(8, min(12, 6 + (page_count - 4) * 2))
                prompt = f"""Produce {target_refs} IEEE-style references relevant to the technologies and implementation below.

CONTEXT (no code, facts only):
{compact}

DOMAINS: {', '.join(topics)}

REQUIREMENTS:
- Prefer authoritative sources (official docs/specs), widely cited books, and relevant peer-reviewed work
- One reference per line; no LaTeX wrappers
- No fake DOIs/URLs; no placeholders; no generic entries
Output:
<one reference per line>
"""
                lines = self.model.generate_content(prompt).text.strip().split('\n')
                refs = [l.strip('- ').strip() for l in lines if l.strip()]
                refs = list(dict.fromkeys(refs))
                refs = refs[:target_refs]
                if refs:
                    return '\n'.join([f"[{i+1}] {ref}" for i, ref in enumerate(refs)])
            except Exception:
                pass

        # Fallback: dynamic official docs by technologies/topics
        technologies = set(analysis.get('technologies', []))
        topics = set(self._infer_topics(analysis))
        dynamic = []
        tech_map = {
            'Python': ["Python Software Foundation. Python 3 Documentation."],
            'JavaScript': ["MDN Web Docs. JavaScript Guide."],
            'HTML': ["WHATWG. HTML Living Standard."],
            'CSS': ["W3C. CSS Cascading Style Sheets Snapshot."],
        }
        for t in technologies:
            dynamic.extend(tech_map.get(t, []))
        if 'RAG' in topics or 'Vector DB' in topics:
            dynamic.append("Lewis, P. et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (NeurIPS 2020).")
        if 'Graph' in topics:
            dynamic.append("Newman, M. Networks: An Introduction. Oxford University Press.")
        if 'MongoDB' in topics:
            dynamic.append("MongoDB Inc. MongoDB Manual.")
        if 'Chroma' in topics or 'Vector DB' in topics:
            dynamic.append("ChromaDB Documentation.")
        if 'Flask' in topics:
            dynamic.append("Pallets. Flask Documentation.")
        if not dynamic:
            dynamic = ["IEEE Computer Society. IEEE Style Guide."]
        dynamic = list(dict.fromkeys(dynamic))
        target = max(8, min(12, 6 + (page_count - 4) * 2))
        dynamic = dynamic[:target]
        return '\n'.join([f"[{i+1}] {ref}" for i, ref in enumerate(dynamic)])

    def _infer_topics(self, analysis: Dict[str, Any]) -> list:
        """Infer domain topics from file names, dependencies, technologies, and function names."""
        topics = set()
        files = analysis.get('file_analyses', [])
        techs = analysis.get('technologies', [])
        for t in techs:
            if t in ['Python', 'JavaScript', 'HTML', 'CSS']:
                topics.add(t)
        for f in files:
            path = getattr(f, 'file_path', '').lower()
            deps = set(getattr(f, 'dependencies', []) or [])
            funcs = set(getattr(f, 'key_functions', []) or [])
            text = ' '.join([path] + list(deps) + list(funcs))
            if any(k in text for k in ['rag', 'embedding', 'embed', 'vector', 'chroma']):
                topics.add('RAG')
                topics.add('Vector DB')
            if any(k in text for k in ['graph', 'dag']):
                topics.add('Graph')
            if any(k in text for k in ['flask', 'fastapi']):
                topics.add('Flask')
            if any(k in text for k in ['mongo']):
                topics.add('MongoDB')
            if any(k in text for k in ['frontend', 'app.py', 'templates']):
                topics.add('Web')
        return list(topics)
    
    def _assemble_paper(self, template: str, title: str, authors: List[Dict],
                        abstract: str, keywords: str, introduction: str,
                        methodology: str, implementation: str, results: str,
                        discussion: str, conclusion: str, references: str) -> str:
        """Assemble complete paper with journal boilerplate"""
        
        # Format authors for LaTeX
        author_latex = self._format_authors_latex(authors)
        
        if 'ieee' in template.lower():
            if 'journal' in template.lower():
                return self._ieee_journal_template(title, author_latex, abstract, keywords,
                                                   introduction, methodology, implementation,
                                                   results, discussion, conclusion, references)
            return self._ieee_template(title, author_latex, abstract, keywords,
                                       introduction, methodology, implementation,
                                       results, discussion, conclusion, references)
        elif 'acm' in template.lower():
            return self._acm_template(title, author_latex, abstract, keywords,
                                      introduction, methodology, implementation,
                                      results, discussion, conclusion, references)
        elif 'springer' in template.lower():
            return self._springer_template(title, author_latex, abstract, keywords,
                                           introduction, methodology, implementation,
                                           results, discussion, conclusion, references)
        else:
            return self._default_template(title, author_latex, abstract, keywords,
                                          introduction, methodology, implementation,
                                          results, discussion, conclusion, references)
    
    def _format_authors_latex(self, authors: List[Dict]) -> str:
        """Format authors for LaTeX"""
        if len(authors) == 1:
            author = authors[0]
            return f"""\\author{{\\IEEEauthorblockN{{{author['name']}}}
\\IEEEauthorblockA{{{author['affiliation']}\\\\
Email: {author['email']}}}}}"""
        else:
            formatted = []
            for author in authors:
                formatted.append(f"""\\IEEEauthorblockN{{{author['name']}}}
\\IEEEauthorblockA{{{author['affiliation']}\\\\
Email: {author['email']}}}""")
            return f"""\\author{{{'\\\\\\and\\\\'.join(formatted)}}}"""
    
    def _ieee_template(self, title, authors, abstract, keywords, intro, 
                       method, impl, results, discuss, concl, refs) -> str:
        """IEEE conference template with proper formatting"""
        return f"""\\documentclass[conference]{{IEEEtran}}
\\IEEEoverridecommandlockouts
\\usepackage[utf8]{{inputenc}}
\\usepackage{{cite}}
\\usepackage{{amsmath,amssymb,amsfonts}}
\\usepackage{{algorithmic}}
\\usepackage{{graphicx}}
\\usepackage{{textcomp}}
\\usepackage{{xcolor}}
\\def\\BibTeX{{\\rm B\\kern-.05em{{\\sc i\\kern-.025em b}}\\kern-.08em
    T\\kern-.1667em\\lower.7ex\\hbox{{E}}\\kern-.125emX}}

\\begin{{document}}

\\title{{{title}}}

{authors}

\\maketitle

\\begin{{abstract}}
{abstract}
\\end{{abstract}}

\\begin{{IEEEkeywords}}
{keywords}
\\end{{IEEEkeywords}}

\\section{{Introduction}}
{intro}

\\section{{Methodology}}
{method}

\\section{{Implementation}}
{impl}

\\section{{Results and Analysis}}
{results}

\\section{{Discussion}}
{discuss}

\\section{{Conclusion and Future Work}}
{concl}

\\begin{{thebibliography}}{{00}}
{refs}
\\end{{thebibliography}}

\\end{{document}}"""

    def _ieee_journal_template(self, title, authors, abstract, keywords, intro,
                               method, impl, results, discuss, concl, refs) -> str:
        """IEEE journal template (richer preamble)"""
        return f"""\\documentclass[journal]{{IEEEtran}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{cite}}
\\usepackage{{amsmath,amssymb,amsfonts}}
\\usepackage{{algorithm}}
\\usepackage{{algorithmic}}
\\usepackage{{graphicx}}
\\usepackage{{xcolor}}
\\usepackage{{booktabs}}
\\usepackage{{multirow}}
\\usepackage{{hyperref}}

\\begin{{document}}

\\title{{{title}}}

{authors}

\\maketitle

\\begin{{abstract}}
{abstract}
\\end{{abstract}}

\\begin{{IEEEkeywords}}
{keywords}
\\end{{IEEEkeywords}}

\\section{{Introduction}}
{intro}

\\section{{Methodology}}
{method}

\\section{{Implementation}}
{impl}

\\section{{Results and Analysis}}
{results}

\\section{{Discussion}}
{discuss}

\\section{{Conclusion and Future Work}}
{concl}

\\begin{{thebibliography}}{{00}}
{refs}
\\end{{thebibliography}}

\\end{{document}}"""
    
    def _acm_template(self, title, authors, abstract, keywords, intro,
                      method, impl, results, discuss, concl, refs) -> str:
        """ACM template"""
        return f"""\\documentclass{{acmart}}
\\usepackage[utf8]{{inputenc}}

\\begin{{document}}

\\title{{{title}}}

{authors}

\\begin{{abstract}}
{abstract}
\\end{{abstract}}

\\keywords{{{keywords}}}

\\maketitle

\\section{{Introduction}}
{intro}

\\section{{Methodology}}
{method}

\\section{{Implementation}}
{impl}

\\section{{Results}}
{results}

\\section{{Discussion}}
{discuss}

\\section{{Conclusion}}
{concl}

\\begin{{thebibliography}}{{99}}
{refs}
\\end{{thebibliography}}

\\end{{document}}"""
    
    def _springer_template(self, title, authors, abstract, keywords, intro,
                          method, impl, results, discuss, concl, refs) -> str:
        """Springer template"""
        return f"""\\documentclass{{svjour3}}
\\usepackage[utf8]{{inputenc}}

\\begin{{document}}

\\title{{{title}}}

{authors}

\\maketitle

\\begin{{abstract}}
{abstract}
\\end{{abstract}}

\\keywords{{{keywords}}}

\\section{{Introduction}}
{intro}

\\section{{Methodology}}
{method}

\\section{{Implementation}}
{impl}

\\section{{Results}}
{results}

\\section{{Discussion}}
{discuss}

\\section{{Conclusion}}
{concl}

\\begin{{thebibliography}}{{99}}
{refs}
\\end{{thebibliography}}

\\end{{document}}"""
    
    def _default_template(self, title, authors, abstract, keywords, intro,
                         method, impl, results, discuss, concl, refs) -> str:
        """Default template"""
        return self._ieee_template(title, authors, abstract, keywords, intro,
                                   method, impl, results, discuss, concl, refs)
    
    def save_paper(self, content: str, filepath: str, format_type: str = 'latex') -> None:
        """Save paper to file or compile to PDF"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        if format_type == 'latex':
            # Save LaTeX file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        elif format_type == 'pdf':
            # Compile LaTeX to PDF
            self._compile_latex_to_pdf(content, filepath)
        else:
            # Default to LaTeX
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def _compile_latex_to_pdf(self, latex_content: str, pdf_filepath: str) -> None:
        """Compile LaTeX content to PDF using pdflatex"""
        import subprocess
        import tempfile
        import shutil
        
        # Create temporary directory for compilation
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write LaTeX content to temporary file
            tex_file = os.path.join(temp_dir, 'paper.tex')
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            try:
                # Run pdflatex twice (for references and citations)
                for _ in range(2):
                    result = subprocess.run([
                        'pdflatex', 
                        '-interaction=nonstopmode',
                        '-output-directory', temp_dir,
                        tex_file
                    ], capture_output=True, text=True, cwd=temp_dir)
                    
                    if result.returncode != 0:
                        print(f"pdflatex error: {result.stderr}")
                        # If pdflatex fails, create a simple error PDF
                        self._create_error_pdf(pdf_filepath, result.stderr)
                        return
                
                # Copy generated PDF to target location
                temp_pdf = os.path.join(temp_dir, 'paper.pdf')
                if os.path.exists(temp_pdf):
                    shutil.copy2(temp_pdf, pdf_filepath)
                    print(f"✅ PDF compiled successfully: {pdf_filepath}")
                else:
                    print("❌ PDF file not generated")
                    self._create_error_pdf(pdf_filepath, "PDF compilation completed but no output file generated")
                    
            except FileNotFoundError:
                print("❌ pdflatex not found. Please install LaTeX distribution (e.g., MacTeX, TeX Live)")
                self._create_error_pdf(pdf_filepath, "pdflatex not found. Please install LaTeX distribution.")
            except Exception as e:
                print(f"❌ PDF compilation error: {e}")
                self._create_error_pdf(pdf_filepath, str(e))
    
    def _create_error_pdf(self, pdf_filepath: str, error_message: str) -> None:
        """Create a simple PDF with error message using reportlab"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            c = canvas.Canvas(pdf_filepath, pagesize=letter)
            width, height = letter
            
            # Title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "PDF Compilation Error")
            
            # Error message
            c.setFont("Helvetica", 12)
            y_position = height - 100
            lines = error_message.split('\n')
            for line in lines[:20]:  # Limit to 20 lines
                c.drawString(50, y_position, line[:80])  # Limit line length
                y_position -= 20
            
            # Instructions
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_position - 40, "To fix this issue:")
            c.setFont("Helvetica", 10)
            c.drawString(50, y_position - 60, "1. Install LaTeX: brew install --cask mactex (on macOS)")
            c.drawString(50, y_position - 80, "2. Or download the .tex file and compile manually")
            c.drawString(50, y_position - 100, "3. You can also use online LaTeX editors like Overleaf")
            
            c.save()
            print(f"✅ Error PDF created: {pdf_filepath}")
            
        except ImportError:
            print("❌ reportlab not installed. Cannot create error PDF.")
            # Create a simple text file instead
            txt_filepath = pdf_filepath.replace('.pdf', '_error.txt')
            with open(txt_filepath, 'w') as f:
                f.write(f"PDF Compilation Error:\n\n{error_message}\n\n")
                f.write("To fix this issue:\n")
                f.write("1. Install LaTeX: brew install --cask mactex (on macOS)\n")
                f.write("2. Or download the .tex file and compile manually\n")
                f.write("3. You can also use online LaTeX editors like Overleaf\n")
        except Exception as e:
            print(f"❌ Failed to create error PDF: {e}")

