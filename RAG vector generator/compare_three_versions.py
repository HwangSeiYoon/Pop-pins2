#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
세 가지 RAG Vector DB 버전 비교 스크립트 (자동 실행 버전)
Legacy vs Filtered vs Semantic
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# .env 파일 로드 (여러 경로 시도)
script_dir = Path(__file__).parent.resolve()
env_paths = [
    script_dir / ".env",
    script_dir.parent / "app" / ".env",
]
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        break
else:
    load_dotenv()  # 기본 경로에서 찾기

# 테스트 쿼리 목록
TEST_QUERIES = [
    "파이썬에서 리스트와 튜플의 차이점은 무엇인가요?",
    "딥러닝에서 과적합(overfitting)을 방지하는 방법",
    "pandas DataFrame에서 결측치를 처리하는 방법",
    "객체 지향 프로그래밍의 핵심 개념",
    "머신러닝 모델 평가 지표",
]

class ResultLogger:
    """결과를 콘솔과 파일에 동시 출력"""
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, 'w', encoding='utf-8')
    
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    
    def flush(self):
        self.terminal.flush()
        self.log.flush()
    
    def close(self):
        self.log.close()

def load_vector_db(db_path: str, embeddings):
    """벡터 DB 로드"""
    return FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)

def search_and_display(vector_store, query: str, version_name: str, k: int = 3):
    """검색 및 결과 출력"""
    print(f"\n{'='*80}")
    print(f"🔍 버전: {version_name}")
    print(f"📝 쿼리: {query}")
    print(f"{'='*80}")
    
    results = vector_store.similarity_search_with_score(query, k=k)
    
    for i, (doc, score) in enumerate(results, 1):
        print(f"\n[결과 {i}] 유사도 점수: {score:.4f}")
        print(f"📄 출처: {doc.metadata.get('file_name', 'Unknown')}")
        if 'section' in doc.metadata:
            print(f"📌 섹션: {doc.metadata['section']}")
        print(f"📖 내용 (처음 300자):\n{doc.page_content[:300]}...")
        print("-" * 80)
    
    return results

def main():
    # 결과 파일 설정
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"comparison_results_{timestamp}.txt"
    
    # 출력 리다이렉션
    logger = ResultLogger(result_file)
    sys.stdout = logger
    
    try:
        print("🚀 세 가지 RAG Vector DB 버전 비교 시작")
        print(f"📅 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 경로 설정
        root_dir = Path(__file__).parent.parent.resolve()
        vector_db_dir = root_dir / "vector_db"
        
        db_paths = {
            "Legacy (v1.0 - Simple Chunking)": vector_db_dir / "python_textbook_gemini_db_legacy",
            "Filtered (v1.4 - Page Filtering + Cleaning)": vector_db_dir / "python_textbook_gemini_db_filtered",
            "Semantic (v1.5 - Semantic Chunking)": root_dir / "RAG vector generator" / "vector_db" / "python_textbook_gemini_db_semantic",
        }
        
        # 임베딩 모델 초기화
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY 또는 GOOGLE_API_KEY 환경 변수가 필요합니다.")
        
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004", 
            google_api_key=api_key
        )
        
        # 벡터 DB 로드
        print("📚 벡터 DB 로딩 중...\n")
        vector_stores = {}
        for name, path in db_paths.items():
            if path.exists():
                print(f"✅ {name}: {path}")
                vector_stores[name] = load_vector_db(str(path), embeddings)
            else:
                print(f"❌ {name}: 경로를 찾을 수 없음 - {path}")
        
        if len(vector_stores) != 3:
            print(f"\n⚠️ 경고: 일부 벡터 DB를 찾을 수 없습니다. (발견: {len(vector_stores)}/3)")
            return
        
        print("\n" + "="*80)
        print("🎯 테스트 쿼리별 비교 시작")
        print("="*80)
        
        # 각 쿼리에 대해 세 버전 비교
        for query_idx, query in enumerate(TEST_QUERIES, 1):
            print(f"\n\n{'#'*80}")
            print(f"# 쿼리 {query_idx}/{len(TEST_QUERIES)}: {query}")
            print(f"{'#'*80}")
            
            for version_name, vector_store in vector_stores.items():
                search_and_display(vector_store, query, version_name, k=3)
        
        print("\n\n" + "="*80)
        print("✅ 비교 완료!")
        print("="*80)
        print(f"\n📄 결과가 '{result_file}' 파일에 저장되었습니다.")
        print("\n💡 분석 포인트:")
        print("  1. 유사도 점수가 낮을수록 더 유사함 (거리 기반)")
        print("  2. Semantic 버전은 의미적으로 더 관련성 높은 청크를 반환하는지 확인")
        print("  3. Filtered 버전은 노이즈(목차, 색인 등)가 제거되었는지 확인")
        print("  4. Legacy 버전과 비교하여 개선 정도 파악")
        
    finally:
        # 출력 복원
        sys.stdout = logger.terminal
        logger.close()
        print(f"\n✅ 결과가 '{result_file}' 파일에 저장되었습니다.")

if __name__ == "__main__":
    main()
