#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
파이썬 교재 PDF RAG 벡터 생성기
PDF 파일들을 읽어 임베딩하여 FAISS 벡터 데이터베이스에 저장합니다.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

# .env 파일 로드
try:
    from dotenv import load_dotenv

    # 스크립트 디렉토리의 .env 파일 로드
    script_dir = Path(__file__).parent.resolve()
    env_path = script_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # .env 파일이 없어도 환경 변수는 계속 사용 가능
        load_dotenv()  # 현재 디렉토리와 상위 디렉토리에서 .env 찾기
except ImportError:
    # python-dotenv가 설치되지 않은 경우 환경 변수만 사용
    pass

from langchain_community.document_loaders import PyPDFLoader

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ImportError:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings

# 임베딩 모델 import는 동적으로 처리
try:
    import boto3
    from langchain_aws import BedrockEmbeddings

    BEDROCK_AVAILABLE = True
except ImportError:
    BEDROCK_AVAILABLE = False
    boto3 = None

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

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# .env 파일 로드 확인 메시지
script_dir_for_log = Path(__file__).parent.resolve()
env_path_for_log = script_dir_for_log / ".env"
if env_path_for_log.exists():
    logger.info(f".env 파일 발견 및 로드 완료: {env_path_for_log}")


class PythonTextbookRAGGenerator:
    """파이썬 교재 PDF RAG 벡터 생성기 클래스"""

    def __init__(
        self,
        embedding_model: str = "gemini",
        api_key: Optional[str] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        """
        Args:
            embedding_model: 사용할 임베딩 모델 ("bedrock", "gemini", or "openai")
            api_key: API 키 (None이면 환경 변수에서 가져옴)
            chunk_size: 텍스트 청크 크기
            chunk_overlap: 청크 간 겹치는 문자 수
        """
        self.embedding_model_type = embedding_model.lower()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # 임베딩 모델 초기화
        self.embeddings = self._initialize_embeddings(api_key)

        # 텍스트 분할기 초기화
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

        logger.info(
            f"PythonTextbookRAGGenerator 초기화 완료 (임베딩 모델: {self.embedding_model_type})"
        )

    def _initialize_embeddings(self, api_key: Optional[str] = None) -> Embeddings:
        """임베딩 모델 초기화"""
        if (
            self.embedding_model_type == "bedrock"
            or self.embedding_model_type == "titan"
        ):
            if not BEDROCK_AVAILABLE:
                raise ImportError(
                    "AWS Bedrock 임베딩 모델을 사용하려면 'boto3'와 'langchain-aws' 패키지가 필요합니다.\n"
                    "설치: pip install boto3 langchain-aws"
                )

            # AWS 자격 증명 정보 가져오기
            access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
            secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY") or os.getenv(
                "AWS_BEDROCK_API_KEY"
            )
            region = os.getenv("AWS_DEFAULT_REGION", "ap-northeast-2")

            # AWS 자격 증명 확인
            if not access_key_id or not secret_access_key:
                raise ValueError(
                    "AWS Bedrock 자격 증명이 필요합니다. "
                    "환경 변수를 설정하세요:\n"
                    "  - AWS_ACCESS_KEY_ID\n"
                    "  - AWS_SECRET_ACCESS_KEY 또는 AWS_BEDROCK_API_KEY\n"
                    "  - AWS_DEFAULT_REGION (선택사항, 기본값: ap-northeast-2)"
                )

            # Bedrock 클라이언트 생성
            bedrock_client = boto3.client(
                "bedrock-runtime",
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                region_name=region,
            )

            return BedrockEmbeddings(
                client=bedrock_client, model_id="amazon.titan-embed-text-v2:0"
            )

        elif self.embedding_model_type == "gemini":
            if not GEMINI_AVAILABLE:
                raise ImportError(
                    "Gemini 임베딩 모델을 사용하려면 'langchain-google-genai' 패키지가 필요합니다.\n"
                    "설치: pip install langchain-google-genai"
                )

            # GEMINI_API_KEY 또는 GOOGLE_API_KEY 둘 다 지원
            api_key = (
                api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            )
            if not api_key:
                raise ValueError(
                    "Gemini API 키가 필요합니다. "
                    "환경 변수 'GEMINI_API_KEY' 또는 'GOOGLE_API_KEY'를 설정하거나 api_key 파라미터를 제공하세요."
                )

            return GoogleGenerativeAIEmbeddings(
                model="models/embedding-001", google_api_key=api_key
            )

        elif self.embedding_model_type == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError(
                    "OpenAI 임베딩 모델을 사용하려면 'langchain-openai' 패키지가 필요합니다.\n"
                    "설치: pip install langchain-openai"
                )

            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "OpenAI API 키가 필요합니다. "
                    "환경 변수 'OPENAI_API_KEY'를 설정하거나 api_key 파라미터를 제공하세요."
                )

            # text-embedding-3-small 사용 (더 정확하고 저렴함)
            # max_retries를 늘려서 rate limit 발생 시 자동 재시도
            return OpenAIEmbeddings(
                model="text-embedding-3-small",
                openai_api_key=api_key,
                max_retries=10,  # rate limit 발생 시 재시도 횟수 증가
            )

        else:
            raise ValueError(
                f"지원하지 않는 임베딩 모델입니다: {self.embedding_model_type}\n"
                f"지원 모델: 'bedrock', 'gemini', 'openai'"
            )

    def _get_file_hash(self, file_path: Path) -> str:
        """파일의 해시값을 계산하여 고유 식별자로 사용"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _load_processed_files(self, metadata_file: Path) -> Dict[str, Any]:
        """처리된 파일 목록 로드"""
        if metadata_file.exists():
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                logger.warning(
                    f"메타데이터 파일 읽기 실패: {e}. 새로운 메타데이터로 시작합니다."
                )
                return {}
        return {}

    def _save_processed_files(
        self, metadata_file: Path, processed_files: Dict[str, Any]
    ):
        """처리된 파일 목록 저장"""
        metadata_file.parent.mkdir(parents=True, exist_ok=True)
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(processed_files, f, ensure_ascii=False, indent=2)

    def _load_pdf_files(self, source_dir: Path) -> List[Path]:
        """PDF 파일 목록 로드"""
        if not source_dir.exists():
            raise FileNotFoundError(f"소스 디렉토리를 찾을 수 없습니다: {source_dir}")

        pdf_files = list(source_dir.rglob("*.pdf"))
        if not pdf_files:
            raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {source_dir}")

        logger.info(f"발견된 PDF 파일 수: {len(pdf_files)}")
        return pdf_files

    def _process_pdf(self, pdf_path: Path) -> List[Any]:
        """단일 PDF 파일 처리"""
        try:
            logger.info(f"PDF 처리 중: {pdf_path.name}")
            loader = PyPDFLoader(str(pdf_path))
            documents = loader.load()

            # 메타데이터에 파일 경로 추가
            for doc in documents:
                doc.metadata["source_file"] = str(pdf_path)
                doc.metadata["file_name"] = pdf_path.name

            # 문서 분할
            texts = self.text_splitter.split_documents(documents)
            logger.info(f"  → {len(documents)} 페이지에서 {len(texts)} 개 청크 생성")

            return texts

        except Exception as e:
            logger.error(f"PDF 파일 처리 실패 ({pdf_path.name}): {e}")
            raise

    def generate_vector_db(
        self,
        db_name: str = "python_textbook_db",
        source_dir: Optional[str] = None,
        output_dir: Optional[str] = None,
    ):
        """
        벡터 데이터베이스 생성 또는 업데이트

        Args:
            db_name: 벡터 DB 이름 (파일명)
            source_dir: PDF 소스 디렉토리 경로 (None이면 기본 경로 사용)
            output_dir: 벡터 DB 저장 디렉토리 (None이면 기본 경로 사용)
        """
        # 경로 설정 - standalone으로 동작하도록 현재 스크립트 위치 기준으로 설정
        script_dir = Path(__file__).parent.resolve()
        project_root = script_dir.parent  # Pop-pins2 폴더

        # 기본 경로 설정
        default_source_dir = script_dir / "pdfs"  # PDF 파일들을 넣을 디렉토리
        default_output_dir = (
            project_root / "vector_db"
        )  # 벡터 DB 저장 디렉토리 (Pop-pins2/vector_db)

        source_path = Path(source_dir) if source_dir else default_source_dir
        output_path = Path(output_dir) if output_dir else default_output_dir

        db_path = output_path / db_name
        metadata_file = output_path / f"{db_name}_metadata.json"

        logger.info("=" * 60)
        logger.info("파이썬 교재 PDF 벡터 데이터베이스 생성 시작")
        logger.info(f"  DB 이름: {db_name}")
        logger.info(f"  소스 디렉토리: {source_path}")
        logger.info(f"  출력 디렉토리: {output_path}")
        logger.info("=" * 60)

        # 처리된 파일 목록 로드
        processed_files = self._load_processed_files(metadata_file)

        # PDF 파일 목록 로드
        all_pdf_files = self._load_pdf_files(source_path)

        # 새로 처리할 파일 필터링
        new_pdf_files = []
        for pdf_file in all_pdf_files:
            file_hash = self._get_file_hash(pdf_file)
            file_stat = pdf_file.stat()

            # 파일이 이미 처리되었는지 확인 (해시와 수정 시간 비교)
            if file_hash in processed_files:
                stored_info = processed_files[file_hash]
                if (
                    stored_info.get("mtime") == file_stat.st_mtime
                    and stored_info.get("size") == file_stat.st_size
                ):
                    logger.info(f"이미 처리된 파일 건너뛰기: {pdf_file.name}")
                    continue

            new_pdf_files.append(pdf_file)

        if not new_pdf_files:
            logger.info("처리할 새로운 파일이 없습니다.")
            return

        logger.info(f"새로 처리할 파일 수: {len(new_pdf_files)}")

        # 기존 벡터 DB 로드 또는 새로 생성
        vector_store = None

        if db_path.exists():
            try:
                logger.info(f"기존 벡터 DB 로드: {db_path}")
                vector_store = FAISS.load_local(
                    str(db_path), self.embeddings, allow_dangerous_deserialization=True
                )
                logger.info("기존 벡터 DB 로드 완료")
            except Exception as e:
                logger.warning(f"기존 벡터 DB 로드 실패: {e}")
                logger.info("새로운 벡터 DB로 시작합니다.")
                vector_store = None

        # 새로운 벡터 DB 생성이 필요한 경우
        if vector_store is None:
            if not new_pdf_files:
                raise ValueError("처리할 파일이 없고 기존 벡터 DB도 없습니다.")

            logger.info("새로운 벡터 DB 생성")
            # 첫 문서로 벡터 스토어 초기화
            first_pdf = new_pdf_files[0]
            first_texts = self._process_pdf(first_pdf)
            vector_store = FAISS.from_documents(first_texts, self.embeddings)
            new_pdf_files = new_pdf_files[1:]

            # 첫 파일의 메타데이터 업데이트
            first_hash = self._get_file_hash(first_pdf)
            first_stat = first_pdf.stat()
            processed_files[first_hash] = {
                "file_path": str(first_pdf),
                "file_name": first_pdf.name,
                "mtime": first_stat.st_mtime,
                "size": first_stat.st_size,
                "chunks": len(first_texts),
            }

            logger.info("새로운 벡터 DB 생성 완료")

        # 나머지 PDF 파일 처리 및 추가
        all_new_texts = []
        for pdf_file in new_pdf_files:
            try:
                texts = self._process_pdf(pdf_file)
                all_new_texts.extend(texts)

                # 메타데이터 업데이트
                file_hash = self._get_file_hash(pdf_file)
                file_stat = pdf_file.stat()
                processed_files[file_hash] = {
                    "file_path": str(pdf_file),
                    "file_name": pdf_file.name,
                    "mtime": file_stat.st_mtime,
                    "size": file_stat.st_size,
                    "chunks": len(texts),
                }

            except Exception as e:
                logger.error(f"파일 처리 중 오류 발생 ({pdf_file.name}): {e}")
                continue

        # 벡터 DB에 추가
        if all_new_texts:
            logger.info(f"벡터 DB에 {len(all_new_texts)} 개 청크 추가 중...")
            vector_store.add_documents(all_new_texts)
            logger.info("벡터 DB 업데이트 완료")

        # 벡터 DB 저장
        output_path.mkdir(parents=True, exist_ok=True)
        vector_store.save_local(str(db_path))
        logger.info(f"벡터 DB 저장 완료: {db_path}")

        # 메타데이터 저장
        self._save_processed_files(metadata_file, processed_files)
        logger.info(f"메타데이터 저장 완료: {metadata_file}")

        logger.info("=" * 60)
        logger.info("벡터 데이터베이스 생성 완료!")
        logger.info("=" * 60)


def main():
    """메인 함수 - 명령줄 인터페이스"""
    import argparse

    parser = argparse.ArgumentParser(
        description="파이썬 교재 PDF RAG 벡터 생성기 - PDF 파일을 벡터 데이터베이스로 변환"
    )
    parser.add_argument(
        "--db-name",
        type=str,
        default="python_textbook_db",
        help="벡터 데이터베이스 이름 (기본값: python_textbook_db)",
    )
    parser.add_argument(
        "--source-dir",
        type=str,
        default=None,
        help="PDF 소스 디렉토리 경로 (기본값: ./pdfs)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="벡터 DB 저장 디렉토리 (기본값: ./vector_db)",
    )
    parser.add_argument(
        "--embedding-model",
        type=str,
        choices=["bedrock", "gemini", "openai"],
        default="gemini",
        help="사용할 임베딩 모델 (기본값: gemini)",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="API 키 (기본값: 환경 변수에서 가져옴)",
    )
    parser.add_argument(
        "--chunk-size", type=int, default=1000, help="텍스트 청크 크기 (기본값: 1000)"
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="청크 간 겹치는 문자 수 (기본값: 200)",
    )

    args = parser.parse_args()

    try:
        # RAG 데이터 생성기 초기화
        generator = PythonTextbookRAGGenerator(
            embedding_model=args.embedding_model,
            api_key=args.api_key,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
        )

        # 벡터 DB 생성
        generator.generate_vector_db(
            db_name=args.db_name, source_dir=args.source_dir, output_dir=args.output_dir
        )

        logger.info("✅ 작업이 성공적으로 완료되었습니다!")

    except KeyboardInterrupt:
        logger.warning("\n사용자에 의해 작업이 중단되었습니다.")
    except Exception as e:
        logger.error(f"❌ 오류 발생: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
