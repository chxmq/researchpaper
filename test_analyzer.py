#!/usr/bin/env python3
"""
Test script to verify the improved analyzer generates better content
"""

import sys
import os
sys.path.append('src')

from core.new_analyzer import NewGitHubAnalyzer
from core.progressive_generator import ProgressivePaperGenerator

def test_analyzer():
    print("🧪 Testing improved analyzer...")
    
    # Test with a sample repository
    analyzer = NewGitHubAnalyzer()
    generator = ProgressivePaperGenerator()
    
    # Use a simple repository for testing
    test_repo = "https://github.com/octocat/Hello-World.git"
    
    try:
        print(f"📥 Analyzing repository: {test_repo}")
        analysis = analyzer.analyze_repository(test_repo, page_count=6)
        
        print("\n📊 Analysis Results:")
        print(f"- Repository: {analysis['repo_name']}")
        print(f"- Project Type: {analysis['project_type']}")
        print(f"- Technologies: {', '.join(analysis['technologies'])}")
        print(f"- Files Analyzed: {analysis['code_file_count']}")
        print(f"- Total Lines: {analysis['line_count']}")
        print(f"- Complexity: {analysis['complexity_score']}/10")
        
        if analysis.get('file_analyses'):
            print(f"\n📁 Sample File Analysis:")
            for i, file_info in enumerate(analysis['file_analyses'][:3]):
                print(f"  {i+1}. {file_info.file_path} ({file_info.language})")
                print(f"     Purpose: {file_info.purpose}")
                print(f"     Functions: {', '.join(file_info.key_functions[:3])}")
                print(f"     AI Analysis: {file_info.ai_analysis[:100]}...")
        
        print("\n📝 Generating paper...")
        authors = [{"name": "Test Author", "affiliation": "Test University", "email": "test@example.com"}]
        paper = generator.generate_paper(analysis, 'ieee_conference', 6, authors)
        
        # Save the test paper
        output_file = "generated_papers/test_paper.tex"
        os.makedirs("generated_papers", exist_ok=True)
        generator.save_paper(paper, output_file)
        
        print(f"✅ Test paper generated: {output_file}")
        print(f"📄 Paper length: {len(paper)} characters")
        
        # Show a preview of the abstract
        if "\\begin{abstract}" in paper and "\\end{abstract}" in paper:
            start = paper.find("\\begin{abstract}") + len("\\begin{abstract}")
            end = paper.find("\\end{abstract}")
            abstract = paper[start:end].strip()
            print(f"\n📋 Generated Abstract Preview:")
            print(abstract[:300] + "..." if len(abstract) > 300 else abstract)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_analyzer()
    sys.exit(0 if success else 1)
