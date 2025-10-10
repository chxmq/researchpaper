"""
Flask Web Application
Clean, professional web interface for research paper generation
"""

import os
from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime
from typing import Dict, Any

from src.core.new_analyzer import NewGitHubAnalyzer
from src.core.progressive_generator import ProgressivePaperGenerator

app = Flask(__name__, 
           template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
           static_folder=os.path.join(os.path.dirname(__file__), '..', '..', 'static'))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Initialize components
analyzer = NewGitHubAnalyzer()
generator = ProgressivePaperGenerator()


@app.route('/')
def index():
    """Main page with clean interface"""
    templates = generator.templates
    return render_template('index.html', templates=templates)


@app.route('/api/analyze', methods=['POST'])
def analyze_repository():
    """Analyze GitHub repository using file-based approach"""
    try:
        data = request.get_json()
        repo_url = data.get('repo_url')
        page_count = data.get('page_count', 6)
        
        if not repo_url:
            return jsonify({'error': 'Repository URL is required'}), 400
        
        # Analyze repository with file-based approach
        analysis = analyzer.analyze_repository(repo_url, page_count)

        # Serialize analysis for JSON (convert dataclasses to plain dicts)
        files = analysis.get('file_analyses', [])
        serialized_files = []
        for f in files:
            try:
                serialized_files.append({
                    'file_path': f.file_path,
                    'file_name': f.file_name,
                    'file_type': f.file_type,
                    'file_size': f.file_size,
                    'line_count': f.line_count,
                    'language': f.language,
                    'purpose': f.purpose,
                    'key_functions': f.key_functions[:10],
                    'dependencies': f.dependencies[:15],
                    'complexity_score': f.complexity_score
                })
            except Exception:
                # If it's already a dict (in rare cases), keep minimal subset
                if isinstance(f, dict):
                    serialized_files.append({k: f.get(k) for k in (
                        'file_path','file_name','file_type','file_size','line_count','language','purpose','key_functions','dependencies','complexity_score'
                    ) if k in f})

        client_analysis = {k: v for k, v in analysis.items() if k != 'file_analyses'}
        client_analysis['file_analyses'] = serialized_files

        return jsonify({
            'success': True,
            'analysis': client_analysis
        })
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@app.route('/api/generate', methods=['POST'])
def generate_paper():
    """Generate research paper component-by-component"""
    try:
        data = request.get_json()
        repo_url = data.get('repo_url')
        template_name = data.get('template')
        page_count = int(data.get('page_count', 6))
        authors = data.get('authors', [])
        
        if not repo_url or not template_name:
            return jsonify({'error': 'Repository URL and template are required'}), 400
        
        if not authors:
            return jsonify({'error': 'At least one author is required'}), 400
        
        # Limit page count to 10
        page_count = min(page_count, 10)
        
        # Analyze repository with file-based approach
        analysis = analyzer.analyze_repository(repo_url, page_count)
        
        # Generate paper using progressive component-wise approach
        paper_content = generator.generate_paper(
            analysis=analysis,
            template_name=template_name,
            page_count=page_count,
            authors=authors
        )
        
        # Save generated paper as LaTeX
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"research_paper_{timestamp}.tex"
        filepath = os.path.join('generated_papers', filename)
        
        os.makedirs('generated_papers', exist_ok=True)
        generator.save_paper(paper_content, filepath, 'latex')
        
        return jsonify({
            'success': True,
            'filename': filename,
            'latex_content': paper_content,
            'preview_url': f'/api/preview/{filename}',
            'download_url': f'/api/download/{filename}'
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Generation failed: {str(e)}'}), 500

@app.route('/api/preview/<filename>')
def preview_paper(filename):
    """Preview generated paper"""
    try:
        filepath = os.path.join('generated_papers', filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return render_template('preview.html', latex_content=content, filename=filename)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/update', methods=['POST'])
def update_paper():
    """Update paper content"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        latex_content = data.get('latex_content')
        
        if not filename or not latex_content:
            return jsonify({'error': 'Filename and content are required'}), 400
        
        filepath = os.path.join('generated_papers', filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compile', methods=['POST'])
def compile_paper():
    """Compile LaTeX to PDF"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'Filename is required'}), 400
        
        tex_filepath = os.path.join('generated_papers', filename)
        pdf_filename = filename.replace('.tex', '.pdf')
        pdf_filepath = os.path.join('generated_papers', pdf_filename)
        
        if not os.path.exists(tex_filepath):
            return jsonify({'error': 'LaTeX file not found'}), 404
        
        # Read LaTeX content
        with open(tex_filepath, 'r', encoding='utf-8') as f:
            latex_content = f.read()
        
        # Generate PDF
        generator.save_paper(latex_content, pdf_filepath, 'pdf')
        
        return jsonify({
            'success': True,
            'pdf_filename': pdf_filename,
            'download_url': f'/api/download/{pdf_filename}'
        })
    
    except Exception as e:
        return jsonify({'error': f'PDF compilation failed: {str(e)}'}), 500


@app.route('/api/download/<filename>')
def download_paper(filename):
    """Download generated research paper"""
    try:
        filepath = os.path.join('generated_papers', filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/templates')
def get_templates():
    """Get available journal templates"""
    # Use templates from generator
    return jsonify(generator.templates)


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
