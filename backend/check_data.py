#!/usr/bin/env python3
"""
데이터베이스에서 생성된 강의와 챕터 확인 스크립트
"""

import sys
import os

# 현재 디렉토리를 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.database import get_db_session
from db.models import Course, Chapter

def check_courses_and_chapters():
    """생성된 강의와 챕터 데이터 확인"""
    session = next(get_db_session())
    
    try:
        print("=== 최근 생성된 강의 목록 ===")
        courses = session.query(Course).order_by(Course.created_at.desc()).limit(5).all()
        
        if not courses:
            print("생성된 강의가 없습니다.")
            return
            
        for course in courses:
            print(f"\n강의 ID: {course.id}")
            print(f"제목: {course.title}")
            print(f"설명: {course.description}")
            print(f"난이도: {course.difficulty}")
            print(f"생성일: {course.created_at}")
            print(f"작성자 ID: {course.created_by}")
            
            # 해당 강의의 챕터들 조회
            chapters = session.query(Chapter).filter(Chapter.course_id == course.id).all()
            print(f"챕터 수: {len(chapters)}")
            
            if chapters:
                print("챕터 목록:")
                for chapter in chapters:
                    print(f"  - 챕터 ID: {chapter.id}")
                    print(f"    제목: {chapter.title}")
                    print(f"    설명: {chapter.description}")
                    print(f"    순서: {chapter.order}")
                    print()
            else:
                print("  챕터가 없습니다.")
            print("-" * 50)
                
    except Exception as e:
        print(f"데이터베이스 조회 중 오류 발생: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    check_courses_and_chapters()