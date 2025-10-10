# Research Paper Generator

Transform your GitHub repositories into professional research papers in minutes! This AI-powered tool analyzes your code, understands its functionality, and generates comprehensive research papers using various academic journal templates.

## 🚀 Features

- **AI-Powered Analysis**: Advanced AI analyzes your code structure, dependencies, and functionality
- **Multiple Journal Templates**: Support for IEEE, ACM, Springer, Elsevier, and Nature formats
- **Fast Generation**: Generate professional research papers in minutes
- **Comprehensive Analysis**: Detailed code analysis including complexity metrics and technology identification
- **Modern Web Interface**: Clean, responsive interface for easy use
- **Multiple Output Formats**: Generate papers in DOCX and TXT formats

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Git (for repository cloning)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd research-paper-generator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Create necessary directories**
   ```bash
   mkdir -p generated_papers
   ```

## 🚀 Usage

1. **Start the application**
   ```bash
   python app.py
   ```

2. **Open your browser**
   Navigate to `http://localhost:5000`

3. **Generate a research paper**
   - Enter your GitHub repository URL
   - Select a journal template (IEEE, ACM, Springer, etc.)
   - Click "Analyze Repository"
   - Review the analysis results
   - Click "Generate Research Paper"
   - Download your generated paper

## 📊 Supported Journal Templates

### IEEE Conference Paper
- Standard IEEE conference paper format
- Sections: Title, Abstract, Keywords, Introduction, Related Work, Methodology, Implementation, Results, Discussion, Conclusion, References

### ACM Conference Paper
- ACM conference paper format
- Sections: Title, Abstract, CCS Concepts, Keywords, Introduction, Related Work, Approach, Implementation, Evaluation, Results, Discussion, Conclusion, References

### Springer Journal Article
- Springer journal article format
- Sections: Title, Abstract, Keywords, Introduction, Literature Review, Methodology, System Design, Implementation, Experimental Setup, Results, Analysis, Discussion, Conclusion, References

### Elsevier Journal Article
- Elsevier journal article format
- Sections: Title, Abstract, Keywords, Introduction, Background, Methodology, System Architecture, Implementation, Experiments, Results, Discussion, Conclusion, Acknowledgments, References

### Nature-style Article
- Nature journal article format
- Sections: Title, Abstract, Introduction, Results, Discussion, Methods, Data Availability, Code Availability, References

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `FLASK_ENV`: Flask environment (development/production)
- `SECRET_KEY`: Flask secret key for sessions
- `MAX_REPO_SIZE_MB`: Maximum repository size in MB (default: 100)
- `TEMP_DIR`: Temporary directory for repository cloning
- `GENERATED_PAPERS_DIR`: Directory for generated papers
- `GITHUB_TOKEN`: GitHub token for private repositories (optional)

### Customization

You can customize the paper generation by modifying:
- `template_manager.py`: Add new journal templates
- `paper_generator.py`: Modify content generation logic
- `github_analyzer.py`: Adjust code analysis parameters

## 📁 Project Structure

```
research-paper-generator/
├── app.py                 # Main Flask application
├── github_analyzer.py     # Repository analysis logic
├── paper_generator.py     # Paper generation logic
├── template_manager.py    # Journal template management
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
├── README.md             # This file
├── templates/            # HTML templates
│   └── index.html        # Main web interface
└── generated_papers/     # Generated papers directory
```

## 🤖 AI Analysis Features

The system performs comprehensive analysis of your repository:

- **Code Structure Analysis**: Identifies main files, test files, configuration files
- **Dependency Analysis**: Analyzes package dependencies and technology stack
- **Complexity Metrics**: Calculates project complexity score (1-10)
- **Technology Identification**: Automatically detects programming languages and frameworks
- **AI-Powered Insights**: Generates project descriptions, technical contributions, and research potential

## 🔍 How It Works

1. **Repository Cloning**: Downloads your GitHub repository to a temporary directory
2. **Code Analysis**: Analyzes file structure, dependencies, and code patterns
3. **AI Processing**: Uses OpenAI's GPT models to understand project purpose and generate insights
4. **Template Selection**: Applies your chosen journal template format
5. **Content Generation**: Generates comprehensive research paper content
6. **Document Creation**: Creates formatted DOCX document ready for submission

## 🛡️ Security & Privacy

- Repositories are cloned to temporary directories and immediately deleted after analysis
- No code is permanently stored on the server
- Generated papers are stored locally and can be downloaded immediately
- OpenAI API calls are made securely with your API key

## 🚨 Limitations

- Requires public GitHub repositories (private repos need GitHub token)
- OpenAI API usage costs apply
- Large repositories may take longer to analyze
- Generated content should be reviewed and edited before submission

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:

1. Check the console output for error messages
2. Ensure your OpenAI API key is valid
3. Verify the GitHub repository URL is accessible
4. Check that all dependencies are installed

## 🔮 Future Features

- Support for more journal templates
- Integration with academic databases
- Citation management
- Collaborative editing
- Version control for generated papers
- Integration with LaTeX output
- Batch processing of multiple repositories

## 📊 Example Output

The generated research papers include:

- **Professional formatting** matching journal standards
- **Comprehensive analysis** of your codebase
- **Technical contributions** highlighting your innovations
- **Methodology sections** describing your approach
- **Results and discussion** based on code analysis
- **Proper citations** and references
- **Abstract and keywords** optimized for your field

---

**Happy Research Writing!** 🎓📚
