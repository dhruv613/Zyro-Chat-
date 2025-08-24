# Welcome to Zyro

A powerful PDF chat application built with Streamlit and LlamaIndex, powered by Google's Gemini AI. Upload PDFs and chat with them using natural language.

## ✨ Features

- **PDF Upload & Processing**: Drag and drop PDF files for automatic indexing
- **AI-Powered Chat**: Ask questions about your documents using Google Gemini AI
- **Automatic Indexing**: Documents are automatically processed and indexed
- **Persistent Storage**: Indexes are saved and reused between sessions
- **Streaming Responses**: Real-time AI responses as you type
- **File Validation**: Automatic PDF validation and size checking
- **Error Handling**: Comprehensive error handling and logging

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API key

### Installation

1. **Clone the repository:**
   ```bash
   git clone git remote add origin https://github.com/dhruv613/Zyro-Chat-.git
   cd YOUR_REPO_NAME
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key:**
   
   **Option A: Environment Variable (Recommended)**
   ```bash
   # Windows
   set GOOGLE_API_KEY=your_api_key_here
   
   # Linux/Mac
   export GOOGLE_API_KEY=your_api_key_here
   ```
   
   **Option B: Config File**
   - Edit `config.py` and add your API key
   - **Note**: This is less secure for production use

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser:**
   - Navigate to `http://localhost:8501`
   - Start uploading PDFs and chatting!

## 🔧 Configuration

### API Key Setup

The application looks for your Google Gemini API key in this order:
1. Environment variable `GOOGLE_API_KEY`
2. `config.py` file
3. `.env` file (if you create one)

### File Limits

- **File Types**: PDF only
- **File Size**: Maximum 50MB per file
- **Storage**: Files are stored in the `data/` directory
- **Indexes**: Stored in the `storage/` directory

## 📁 Project Structure

```
Welcome-to-Zyro/
├── app.py              # Main application file
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── data/              # PDF storage directory
├── storage/           # Index storage directory
└── .venv/             # Virtual environment
```

## 🐛 Recent Fixes Applied

### Critical Issues Fixed:
1. ✅ **Deprecated Streamlit Function**: Replaced `st.experimental_rerun()` with `st.rerun()`
2. ✅ **Deprecated LlamaIndex Classes**: Updated to latest `google-genai` packages with correct class names
3. ✅ **Missing Environment Variables**: Added fallback to config file
4. ✅ **Title Inconsistency**: Fixed page title vs. displayed title mismatch
5. ✅ **Import Errors**: Fixed incorrect import paths for GoogleGenAI classes
6. ✅ **File Path Display**: Now shows only filenames, not full paths

### Code Quality Improvements:
1. ✅ **Error Handling**: Added comprehensive try-catch blocks
2. ✅ **File Validation**: Added PDF type and size validation
3. ✅ **Logging System**: Added structured logging for debugging
4. ✅ **Race Conditions**: Fixed inefficient index loading logic
5. ✅ **Input Validation**: Added file upload validation
6. ✅ **Performance**: Optimized file path operations

### Security & Reliability:
1. ✅ **File Size Limits**: Added 50MB file size restriction
2. ✅ **Type Safety**: Added proper type hints and validation
3. ✅ **Exception Handling**: Specific exception handling instead of broad catches
4. ✅ **Resource Management**: Proper file handling and cleanup

## 🚨 Troubleshooting

### Common Issues:

1. **"GOOGLE_API_KEY is not set"**
   - Set your API key in environment variables or config.py
   - Restart the application

2. **"Module not found" errors**
   - Run `pip install -r requirements.txt`
   - Ensure you're in the correct virtual environment

3. **PDF upload fails**
   - Check file size (max 50MB)
   - Ensure file is a valid PDF
   - Check console logs for specific errors

4. **Indexing fails**
   - Check if PDFs are corrupted
   - Ensure sufficient disk space
   - Check console logs for detailed error messages

### Logs

The application logs important events to the console. If you encounter issues:
1. Check the terminal/console output
2. Look for ERROR or WARNING messages
3. Verify file permissions and disk space

## 🔒 Security Notes

- **API Keys**: Never commit API keys to version control
- **File Uploads**: Only PDF files are accepted and processed
- **File Size**: 50MB limit prevents abuse
- **Storage**: Files are stored locally on your machine

## 📈 Performance Tips

1. **Large Documents**: Break very large PDFs into smaller chunks
2. **Index Reuse**: The application automatically reuses existing indexes
3. **File Management**: Remove old PDFs to free up storage space
4. **Memory**: Large documents may require more RAM during processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review console logs for error messages
3. Ensure all dependencies are properly installed
4. Verify your API key is valid and has sufficient quota

---

**Welcome to Zyro! 🚀**