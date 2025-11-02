"""
테스트 데이터 삽입 스크립트
MySQL 컨테이너가 정상 작동하면 실행
"""
from db.database import SessionLocal
from db.models import Member, Chapter, Concept
from datetime import datetime

def insert_test_data():
    db = SessionLocal()
    try:
        # 1. 테스트 회원 추가
        member = db.query(Member).filter(Member.email == "test@example.com").first()
        if not member:
            member = Member(
                email="test@example.com",
                password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIxF6k4j7u",  # 해시된 "password123"
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(member)
            db.commit()
            db.refresh(member)
            print(f"✅ Member created: ID={member.id}, email={member.email}")
        else:
            print(f"ℹ️  Member already exists: ID={member.id}, email={member.email}")

        # 2. 테스트 챕터 추가
        chapter = db.query(Chapter).filter(
            Chapter.title == "파이썬 기초 학습"
        ).first()

        if not chapter:
            chapter = Chapter(
                owner_id=member.id,
                title="파이썬 기초 학습",
                description="변수와 자료형에 대해 배웁니다",
                status="completed",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(chapter)
            db.commit()
            db.refresh(chapter)
            print(f"✅ Chapter created: ID={chapter.id}, title={chapter.title}")
        else:
            print(f"ℹ️  Chapter already exists: ID={chapter.id}, title={chapter.title}")

        # 3. 개념정리 추가
        concept = db.query(Concept).filter(
            Concept.chapter_id == chapter.id
        ).first()

        if not concept:
            concept = Concept(
                chapter_id=chapter.id,
                title="변수와 자료형",
                content="""파이썬에서 변수는 값을 저장하는 공간입니다.

## 주요 자료형

1. **정수형 (int)**: 1, 2, 3
2. **실수형 (float)**: 3.14, 2.5
3. **문자열 (str)**: "hello", "world"
4. **불린형 (bool)**: True, False

## 변수 선언 예시

```python
x = 10
name = "Python"
is_valid = True
```

변수명은 의미 있는 이름을 사용하는 것이 좋습니다.""",
                is_complete=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(concept)
            db.commit()
            db.refresh(concept)
            print(f"✅ Concept created: ID={concept.id}, title={concept.title}, chapter_id={concept.chapter_id}")
        else:
            print(f"ℹ️  Concept already exists: ID={concept.id}, title={concept.title}")

        print("\n🎉 Test data inserted successfully!")
        print(f"\nYou can now test:")
        print(f"  GET /v1/concept/{chapter.id}")
        print(f"  PATCH /v1/concept/{chapter.id}")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    insert_test_data()
