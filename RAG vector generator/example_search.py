#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
생성된 벡터 DB를 사용하여 검색하는 예제

참고: API 키는 환경 변수 또는 .env 파일에서 자동으로 로드됩니다.
.env 파일을 사용하려면 스크립트 디렉토리에 .env 파일을 생성하고
GEMINI_API_KEY (또는 GOOGLE_API_KEY) 또는 OPENAI_API_KEY를 설정하세요.
"""

import os
from pathlib import Path
from langchain_community.vectorstores import FAISS

# .env 파일 로드 (선택사항)
try:
    from dotenv import load_dotenv

    script_dir = Path(__file__).parent.resolve()
    env_path = script_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

# 임베딩 모델 import
try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from langchain_openai import OpenAIEmbeddings

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def load_vector_db(
    db_name: str = "python_textbook_db", embedding_model: str = "gemini"
):
    """
    벡터 DB를 로드합니다.

    Args:
        db_name: 벡터 DB 이름
        embedding_model: 사용할 임베딩 모델 (생성 시 사용한 것과 동일해야 함)
    """
    script_dir = Path(__file__).parent.resolve()
    db_path = script_dir / "vector_db" / db_name

    if not db_path.exists():
        raise FileNotFoundError(f"벡터 DB를 찾을 수 없습니다: {db_path}")

    # 임베딩 모델 초기화
    if embedding_model == "gemini":
        if not GEMINI_AVAILABLE:
            raise ImportError("langchain-google-genai 패키지가 필요합니다.")

        # GEMINI_API_KEY 또는 GOOGLE_API_KEY 둘 다 지원
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY 또는 GOOGLE_API_KEY 환경 변수가 설정되지 않았습니다."
            )

        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001", google_api_key=api_key
        )

    elif embedding_model == "openai":
        if not OPENAI_AVAILABLE:
            raise ImportError("langchain-openai 패키지가 필요합니다.")

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")

        # text-embedding-3-small 사용 (더 정확하고 저렴함)
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small", openai_api_key=api_key
        )

    else:
        raise ValueError(f"지원하지 않는 임베딩 모델: {embedding_model}")

    # 벡터 DB 로드
    vector_store = FAISS.load_local(
        str(db_path), embeddings, allow_dangerous_deserialization=True
    )

    return vector_store


def search_examples():
    """검색 예제"""

    # 벡터 DB 로드
    print("벡터 DB 로드 중...")
    vector_store = load_vector_db(
        db_name="python_textbook_db", embedding_model="gemini"
    )
    print("벡터 DB 로드 완료!\n")

    # 검색할 질문들
    queries = [
        "파이썬 리스트와 튜플의 차이점은?",
        "데코레이터는 어떻게 사용하나요?",
        "클래스 상속에 대해 설명해주세요",
        "예외 처리는 어떻게 하나요?",
    ]

    for query in queries:
        print("=" * 60)
        print(f"질문: {query}")
        print("=" * 60)

        # 유사 문서 검색 (상위 3개)
        docs = vector_store.similarity_search(query, k=3)

        for i, doc in enumerate(docs, 1):
            print(f"\n[결과 {i}]")
            print(f"출처: {doc.metadata.get('file_name', 'Unknown')}")
            print(f"내용 미리보기:")
            # 처음 300자만 표시
            content = doc.page_content[:300]
            if len(doc.page_content) > 300:
                content += "..."
            print(content)
            print("-" * 50)

        print("\n")


def similarity_search_with_score():
    """유사도 점수와 함께 검색하는 예제"""

    print("=" * 60)
    print("유사도 점수와 함께 검색")
    print("=" * 60)

    vector_store = load_vector_db()

    query = "파이썬 제너레이터는 무엇인가요?"

    # 유사도 점수와 함께 검색
    docs_with_scores = vector_store.similarity_search_with_score(query, k=3)

    print(f"질문: {query}\n")

    for i, (doc, score) in enumerate(docs_with_scores, 1):
        print(f"[결과 {i}] (유사도 점수: {score:.4f})")
        print(f"출처: {doc.metadata.get('file_name', 'Unknown')}")
        print(f"내용: {doc.page_content[:200]}...")
        print("-" * 50)


if __name__ == "__main__":
    try:
        # 기본 검색 예제
        search_examples()

        # 유사도 점수와 함께 검색
        similarity_search_with_score()

    except FileNotFoundError as e:
        print(f"❌ 오류: {e}")
        print(
            "먼저 python_textbook_rag_generator.py를 실행하여 벡터 DB를 생성해주세요."
        )
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
