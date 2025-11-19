#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
파이썬 교재 PDF RAG 벡터 생성기 사용 예제

참고: API 키는 환경 변수 또는 .env 파일에서 자동으로 로드됩니다.
.env 파일을 사용하려면 스크립트 디렉토리에 .env 파일을 생성하고
GEMINI_API_KEY (또는 GOOGLE_API_KEY), OPENAI_API_KEY 등을 설정하세요.
"""

from python_textbook_rag_generator import PythonTextbookRAGGenerator
import os

def main():
    """예제 사용법"""
    
    # 방법 1: 기본 설정으로 사용 (Gemini)
    print("=" * 60)
    print("방법 1: 기본 설정으로 벡터 DB 생성")
    print("=" * 60)
    
    generator = PythonTextbookRAGGenerator(
        embedding_model="gemini",  # 또는 "openai", "bedrock"
        chunk_size=1000,
        chunk_overlap=200
    )
    
    generator.generate_vector_db(
        db_name="python_textbook_db",
        source_dir="./pdfs",      # PDF 파일들이 있는 디렉토리
        output_dir="./vector_db"  # 벡터 DB를 저장할 디렉토리
    )
    
    # 방법 2: OpenAI 사용
    print("\n" + "=" * 60)
    print("방법 2: OpenAI 임베딩 사용")
    print("=" * 60)
    
    # OpenAI API 키가 환경 변수에 설정되어 있어야 함
    if os.getenv("OPENAI_API_KEY"):
        generator_openai = PythonTextbookRAGGenerator(
            embedding_model="openai",
            chunk_size=1000,
            chunk_overlap=200
        )
        
        generator_openai.generate_vector_db(
            db_name="python_textbook_db_openai"
        )
    else:
        print("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
    
    # 방법 3: 커스텀 설정
    print("\n" + "=" * 60)
    print("방법 3: 커스텀 청크 크기로 생성")
    print("=" * 60)
    
    generator_custom = PythonTextbookRAGGenerator(
        embedding_model="gemini",
        chunk_size=1500,      # 더 큰 청크
        chunk_overlap=300     # 더 많은 오버랩
    )
    
    generator_custom.generate_vector_db(
        db_name="python_textbook_db_large_chunks"
    )


if __name__ == "__main__":
    main()

