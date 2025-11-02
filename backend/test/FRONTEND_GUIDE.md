# 🎓 DOCGODAI Frontend Demo 사용 가이드

## 📁 파일 구성

- **frontend_demo.html** - 학생용 학습 플랫폼 UI
- **webhook_simulator.html** - n8n AI 응답 시뮬레이터 (개발/테스트용)

## 🚀 실행 방법

### 1. 백엔드 서버 실행

```bash
cd /Users/parkjunseo/Hack-DOCGODAI/backend
python3 main.py
```

서버가 `http://localhost:8000` 에서 실행됩니다.

### 2. 프론트엔드 열기

**방법 1: 브라우저에서 직접 열기**
```bash
# 학생용 UI
open frontend_demo.html

# Webhook 시뮬레이터
open webhook_simulator.html
```

**방법 2: 파일 탐색기에서 더블클릭**
- `frontend_demo.html` 더블클릭 → 브라우저에서 열림
- `webhook_simulator.html` 더블클릭 → 브라우저에서 열림

---

## 📝 전체 플로우 테스트

### Step 1: 회원가입 및 로그인 (frontend_demo.html)

1. `frontend_demo.html` 열기
2. **회원가입** 섹션에서:
   - 이메일: `student@example.com`
   - 비밀번호: `password123`
   - "회원가입" 버튼 클릭
3. **로그인** 섹션에서:
   - 동일한 이메일/비밀번호 입력
   - "로그인" 버튼 클릭

✅ **결과**: 상단에 "로그인: student@example.com" 표시되고 Socket.IO 연결됨

---

### Step 2: 질문 등록 (frontend_demo.html)

1. **질문하기** 섹션에서:
   - 질문: `파이썬 리스트와 튜플 차이가 뭐예요?`
   - 추가 설명: `자세히 알려주세요` (선택)
   - "질문 등록" 버튼 클릭

2. **실시간 처리 현황** 섹션에서 다음 이벤트 확인:
   ```
   [시간] chapter_processing_started  챕터 생성 시작
   [시간] concept_processing         개념 정리 AI 생성 중...
   [시간] exercise_processing        실습 과제 AI 생성 중...
   [시간] quiz_processing            퀴즈 AI 생성 중...
   ```

✅ **결과**: Chapter ID가 생성되고, 학습 페이지에 "AI 생성 중" 상태 표시

---

### Step 3: AI 콘텐츠 생성 시뮬레이션 (webhook_simulator.html)

**새 브라우저 탭에서** `webhook_simulator.html` 열기

1. **Chapter ID 입력**:
   - Step 2에서 생성된 Chapter ID 입력 (예: `1`)

2. **모든 Webhook 한번에 전송** 버튼 클릭
   - 3초 간격으로 순차 전송됨:
     - 개념 정리 → 실습 과제 → 퀴즈

3. **frontend_demo.html 탭으로 돌아가기**
   - **실시간 처리 현황**에서 다음 이벤트 확인:
     ```
     [시간] concept_completed   ✅ 개념 정리 완료!
     [시간] exercise_completed  ✅ 실습 과제 완료!
     [시간] quiz_completed      ✅ 퀴즈 완료!
     [시간] all_completed       🎉 모든 콘텐츠 생성 완료!
     ```

✅ **결과**: 학습 페이지가 자동으로 업데이트되고 모든 콘텐츠 표시됨

---

### Step 4: 학습 페이지 확인 (frontend_demo.html)

**학습 페이지** 섹션에서 생성된 콘텐츠 확인:

#### 🎓 개념 정리
```
리스트 vs 튜플

리스트는 mutable(가변)이고 튜플은 immutable(불변)입니다.
리스트는 [ ] 로 선언하며 요소를 추가, 삭제, 수정할 수 있습니다.
튜플은 ( ) 로 선언하며 한번 생성되면 내용을 변경할 수 없습니다.
```

#### 💻 실습 과제
```
문제: 다음 리스트를 튜플로 변환하는 코드를 작성하세요:
my_list = [1, 2, 3, 4, 5]
```

#### ✅ 퀴즈
```
튜플은 수정이 가능한가요?
○ 가능하다
○ 불가능하다
```

---

### Step 5: 퀴즈 제출 (frontend_demo.html)

1. 퀴즈 섹션에서 답 선택: `불가능하다`
2. "정답 제출" 버튼 클릭

✅ **결과**:
```
정답입니다! (점수: 100점)
```

---

## 🎯 추가 테스트 시나리오

### 여러 질문 등록 테스트

1. **질문 2 등록**:
   - 질문: `파이썬 클래스와 객체 차이는?`
   - "질문 등록" 클릭

2. **질문 3 등록**:
   - 질문: `리스트 컴프리헨션이란?`
   - "질문 등록" 클릭

3. **내 질문 목록**에서 "목록 새로고침" 클릭
   - 등록한 모든 질문 확인 가능
   - 각 질문 클릭 → 해당 학습 페이지로 이동

4. **webhook_simulator.html**에서 각 Chapter ID에 대해 Webhook 전송
   - Chapter ID 2 → 모든 Webhook 전송
   - Chapter ID 3 → 모든 Webhook 전송

---

## 🔧 커스텀 데이터 테스트

**webhook_simulator.html**에서 **커스텀 데이터** 섹션을 수정하여 다른 주제로 테스트 가능:

### 예시: 파이썬 클래스

**개념 정리**:
```
클래스 vs 객체

클래스는 객체를 만들기 위한 설계도(템플릿)입니다.
객체는 클래스를 기반으로 생성된 실체(인스턴스)입니다.
```

**실습 과제**:
```
Car 클래스를 만들고 brand 속성과 drive() 메서드를 추가하세요.
```

**퀴즈**:
```
질문: 클래스와 객체의 관계로 올바른 것은?
선택지: 클래스는 객체의 템플릿이다, 객체는 클래스의 템플릿이다
정답: 클래스는 객체의 템플릿이다
```

---

## 📊 Socket.IO 이벤트 흐름

```
1. 질문 등록 (frontend_demo.html)
   ↓
2. 백엔드: Chapter + 빈 Concept/Exercise/Quiz 생성
   ↓
3. Socket.IO 이벤트 발송:
   - chapter_processing_started
   - concept_processing
   - exercise_processing
   - quiz_processing
   ↓
4. n8n 시뮬레이션 (webhook_simulator.html)
   - POST /v1/chapter/{id}/concept-finish
   - POST /v1/chapter/{id}/exercise-finish
   - POST /v1/chapter/{id}/quiz-finish
   ↓
5. Socket.IO 완료 이벤트 발송:
   - concept_completed
   - exercise_completed
   - quiz_completed
   - all_completed
   ↓
6. 프론트엔드 자동 업데이트 (frontend_demo.html)
   - 학습 페이지 리로드
   - 상태 "완료"로 변경
   - 모든 콘텐츠 표시
```

---

## 🐛 문제 해결

### Socket.IO 연결 안됨
- 백엔드 서버가 실행 중인지 확인: `http://localhost:8000/health`
- 브라우저 콘솔(F12)에서 에러 확인
- CORS 에러 발생 시 → 이미 설정되어 있으므로 서버 재시작

### Webhook 전송 실패
- Chapter ID가 존재하는지 확인
- 백엔드 로그 확인
- 올바른 데이터 형식인지 확인

### 학습 페이지 업데이트 안됨
- Socket.IO 연결 상태 확인 (초록색 점)
- 해당 챕터 룸에 참여했는지 확인
- 페이지 새로고침 후 "내 질문 목록"에서 다시 선택

---

## 🎉 완료!

이제 전체 플로우를 브라우저에서 직접 테스트할 수 있습니다:

1. ✅ 회원가입/로그인 (JWT + Redis)
2. ✅ 질문 등록 (Chapter 생성)
3. ✅ Socket.IO 실시간 진행 상황 확인
4. ✅ n8n Webhook 시뮬레이션
5. ✅ 학습 페이지 자동 업데이트
6. ✅ 퀴즈 제출 및 채점

**실제 프로덕션에서는**:
- Kafka가 챕터 생성 이벤트를 받아 n8n으로 전달
- n8n이 Gemini AI를 호출하여 실제 콘텐츠 생성
- n8n이 생성 완료 후 Webhook으로 백엔드에 전송
- 나머지 플로우는 동일하게 작동
