# RAG Update Log

**Date**: 2025-11-23
**Status**: ⚠️ Pending (API Quota Exceeded)

## 📝 Summary
RAG vector database regeneration was attempted to apply new text filtering and cleaning logic. However, the process was halted because the Google Gemini API daily quota for embedding models (`text-embedding-004`) was exceeded.

## 🛠️ Implemented Changes (Ready to Apply)
The following changes have been implemented in `RAG vector generator/python_textbook_rag_generator.py` and are ready to be applied:

1.  **Page Filtering (`_is_valid_page`)**:
    - Automatically excludes pages containing keywords like "Contents", "Index", "Copyright", "Preface".
    - Excludes pages with very little content (< 50 characters).

2.  **Text Cleaning (`_clean_page_content`)**:
    - Removes headers and footers (page numbers, repeated titles) from the top and bottom 3 lines of each page.
    - Normalizes excessive whitespace and line breaks.

## 🛑 Issue Encountered
- **Error**: `429 Resource has been exhausted (e.g. check quota)`
- **Reason**: The free tier of Gemini API allows ~1,500 requests/day. Regenerating the DB for multiple PDFs requires thousands of requests (1 request per chunk).

## ⏭️ Next Steps (To Do)
Please execute the following commands **after the API quota resets** (usually 24 hours):

### 1. Regenerate Vector DB
```bash
cd "RAG vector generator"
python python_textbook_rag_generator.py --db-name python_textbook_gemini_db --embedding-model gemini
```

### 2. Compare Performance
A script has been prepared to compare the old (backup) DB with the new one.
```bash
cd ..
python compare_rag_performance.py
```

## 📂 Backup Info
- The previous working Vector DB has been restored to: `vector_db/python_textbook_gemini_db`
- A backup copy also exists at: `vector_db/.vector_db-oldver/python_textbook_gemini_db`
