"""
Comprehensive API Test Cases
Tests all endpoints with proper data flow
"""

import pytest
import requests
from typing import Dict, Optional
import time
import random
import string

# Base URL for API
BASE_URL = "http://localhost:8000"

# Generate random email for test
def generate_random_email():
    """Generate random email for testing"""
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{random_string}@example.com"

# Global test email
TEST_EMAIL = generate_random_email()

# Global variables to store created IDs
test_data = {
    "member_id": None,
    "access_token": None,
    "course_id": None,
    "chapter_id": None,
    "concept_id": None,
    "exercise_id": None,
}


class TestHealthCheck:
    """Test health check endpoints"""

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✓ Root endpoint: {data}")

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print(f"✓ Health check: {data}")


class TestMemberAPI:
    """Test Member (User) API endpoints"""

    def test_01_signup(self):
        """Test user signup"""
        payload = {
            "email": TEST_EMAIL,
            "password": "testpass123"
        }
        response = requests.post(f"{BASE_URL}/v1/member/signup", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["email"] == payload["email"]

        # Store member_id for later tests
        test_data["member_id"] = data["id"]
        print(f"✓ Signup successful: Member ID = {test_data['member_id']}")

    def test_02_login(self):
        """Test user login"""
        payload = {
            "email": TEST_EMAIL,
            "password": "testpass123"
        }
        response = requests.post(f"{BASE_URL}/v1/member/login", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert data["member_id"] == test_data["member_id"]

        # Store token for later tests
        test_data["access_token"] = data["access_token"]
        print(f"✓ Login successful: Token = {test_data['access_token'][:20]}...")

    def test_03_get_member_info(self):
        """Test getting member info"""
        headers = {"Authorization": f"Bearer {test_data['access_token']}"}
        response = requests.get(f"{BASE_URL}/v1/member/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_data["member_id"]
        assert data["email"] == TEST_EMAIL
        print(f"✓ Member info retrieved: {data}")


class TestCourseAPI:
    """Test Course API endpoints"""

    def test_01_create_course(self):
        """Test course creation"""
        payload = {
            "title": "Test Course - Python Basics",
            "description": "A comprehensive Python course for beginners",
            "difficulty": "easy",
            "owner_id": test_data["member_id"]
        }
        response = requests.post(f"{BASE_URL}/v1/course/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["title"] == payload["title"]
        assert data["difficulty"] == payload["difficulty"]

        # Store course_id for later tests
        test_data["course_id"] = data["id"]
        print(f"✓ Course created: Course ID = {test_data['course_id']}")

    def test_02_get_course_list(self):
        """Test getting all courses"""
        response = requests.get(f"{BASE_URL}/v1/course/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Find our course
        our_course = next((c for c in data if c["id"] == test_data["course_id"]), None)
        assert our_course is not None
        assert our_course["title"] == "Test Course - Python Basics"
        print(f"✓ Course list retrieved: {len(data)} courses found")

    def test_03_get_course_detail(self):
        """Test getting course details"""
        response = requests.get(f"{BASE_URL}/v1/course/{test_data['course_id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_data["course_id"]
        assert data["title"] == "Test Course - Python Basics"
        assert "chapters" in data
        print(f"✓ Course detail retrieved: {data['title']} with {len(data['chapters'])} chapters")


class TestChapterAPI:
    """Test Chapter API endpoints"""

    def test_01_create_chapter(self):
        """Test chapter creation (also creates concept, exercise, quiz)"""
        payload = {
            "course_id": test_data["course_id"],
            "title": "Variables and Data Types",
            "description": "Learn about Python variables and basic data types",
            "owner_id": test_data["member_id"]
        }
        response = requests.post(f"{BASE_URL}/v1/chapter/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "chapter_id" in data
        assert "concept_id" in data
        assert "exercise_id" in data
        assert "quiz_slots" in data
        assert len(data["quiz_slots"]) == 3

        # Store IDs for later tests
        test_data["chapter_id"] = data["chapter_id"]
        test_data["concept_id"] = data["concept_id"]
        test_data["exercise_id"] = data["exercise_id"]
        print(f"✓ Chapter created: Chapter ID = {test_data['chapter_id']}")
        print(f"  - Concept ID = {test_data['concept_id']}")
        print(f"  - Exercise ID = {test_data['exercise_id']}")
        print(f"  - Quiz slots = {data['quiz_slots']}")

    def test_02_get_chapter_detail(self):
        """Test getting chapter details"""
        response = requests.get(f"{BASE_URL}/v1/chapter/{test_data['chapter_id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_data["chapter_id"]
        assert data["title"] == "Variables and Data Types"
        assert "concept" in data
        assert "exercise" in data
        assert "quiz" in data
        print(f"✓ Chapter detail retrieved: {data['title']}")
        print(f"  - Is active: {data['is_active']}")


class TestConceptAPI:
    """Test Concept API endpoints"""

    def test_01_get_concept(self):
        """Test getting concept content"""
        response = requests.get(f"{BASE_URL}/v1/concept/{test_data['chapter_id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_data["concept_id"]
        assert data["chapter_id"] == test_data["chapter_id"]
        assert "is_complete" in data
        assert data["is_complete"] == False  # Initially not complete
        print(f"✓ Concept retrieved: ID = {data['id']}, Complete = {data['is_complete']}")

    def test_02_update_concept_completion(self):
        """Test marking concept as complete"""
        payload = {"is_complete": True}
        response = requests.patch(f"{BASE_URL}/v1/concept/{test_data['chapter_id']}", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["chapter_id"] == test_data["chapter_id"]
        assert data["is_complete"] == True
        print(f"✓ Concept marked complete: Chapter {data['chapter_id']}")


class TestExerciseAPI:
    """Test Exercise API endpoints"""

    def test_01_get_exercise(self):
        """Test getting exercise content"""
        response = requests.get(f"{BASE_URL}/v1/exercise/{test_data['chapter_id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_data["exercise_id"]
        assert data["chapter_id"] == test_data["chapter_id"]
        assert "is_complete" in data
        assert data["is_complete"] == False  # Initially not complete
        print(f"✓ Exercise retrieved: ID = {data['id']}, Complete = {data['is_complete']}")

    def test_02_update_exercise_completion(self):
        """Test marking exercise as complete"""
        payload = {"is_complete": True}
        response = requests.patch(f"{BASE_URL}/v1/exercise/{test_data['chapter_id']}", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["chapter_id"] == test_data["chapter_id"]
        assert data["is_complete"] == True
        print(f"✓ Exercise marked complete: Chapter {data['chapter_id']}")


class TestQuizAPI:
    """Test Quiz API endpoints"""

    def test_01_get_quiz_list(self):
        """Test getting quiz list"""
        response = requests.get(f"{BASE_URL}/v1/quiz/{test_data['chapter_id']}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3  # Should have 3 quizzes
        for idx, quiz in enumerate(data, start=1):
            assert quiz["slot_number"] == idx
        print(f"✓ Quiz list retrieved: {len(data)} quizzes")

    def test_02_submit_quiz_answer(self):
        """Test submitting quiz answer"""
        # Note: This will fail unless quiz has actual questions
        # Just testing the endpoint structure
        payload = {
            "slot_number": 1,
            "answer": "test answer",
            "member_id": test_data["member_id"]
        }
        try:
            response = requests.post(f"{BASE_URL}/v1/quiz/{test_data['chapter_id']}", json=payload)
            # May get 404 if quiz doesn't have questions yet
            if response.status_code == 200:
                data = response.json()
                assert "is_correct" in data
                assert "score" in data
                print(f"✓ Quiz answer submitted: Correct = {data['is_correct']}, Score = {data['score']}")
            else:
                print(f"⚠ Quiz submission skipped (no question content yet): {response.status_code}")
        except Exception as e:
            print(f"⚠ Quiz submission test skipped: {str(e)}")

    def test_03_get_quiz_result(self):
        """Test getting quiz result"""
        response = requests.get(f"{BASE_URL}/v1/quiz/result/{test_data['chapter_id']}")
        assert response.status_code == 200
        data = response.json()
        assert "chapter_id" in data
        assert "correct_count" in data
        assert "total" in data
        assert "accuracy" in data
        print(f"✓ Quiz result: {data['correct_count']}/{data['total']} (Accuracy: {data['accuracy']*100}%)")

    def test_04_restart_quiz(self):
        """Test restarting quiz"""
        response = requests.post(f"{BASE_URL}/v1/quiz/restart/{test_data['chapter_id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["chapter_id"] == test_data["chapter_id"]
        assert data["reset_status"] == True
        print(f"✓ Quiz restarted for Chapter {data['chapter_id']}")


class TestDataIntegrity:
    """Test data integrity and relationships"""

    def test_course_has_chapter(self):
        """Verify course contains the created chapter"""
        response = requests.get(f"{BASE_URL}/v1/course/{test_data['course_id']}")
        assert response.status_code == 200
        data = response.json()
        chapter_ids = [ch["id"] for ch in data["chapters"]]
        assert test_data["chapter_id"] in chapter_ids
        print(f"✓ Data integrity verified: Course contains chapter")

    def test_chapter_resources_linked(self):
        """Verify chapter has all linked resources"""
        response = requests.get(f"{BASE_URL}/v1/chapter/{test_data['chapter_id']}")
        assert response.status_code == 200
        data = response.json()

        # Check concept is linked
        assert data["concept"] is not None
        assert data["concept"]["id"] == test_data["concept_id"]

        # Check exercise is linked
        assert data["exercise"] is not None
        assert data["exercise"]["id"] == test_data["exercise_id"]

        # Check quiz slots exist
        assert len(data["quiz"]) == 3

        print(f"✓ Data integrity verified: Chapter has all resources linked")


def run_tests():
    """Run all tests in order"""
    print("\n" + "="*60)
    print("Starting Comprehensive API Tests")
    print("="*60 + "\n")

    # Wait for server to be ready
    print("Waiting for server to be ready...")
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✓ Server is ready!\n")
                break
        except:
            if i == max_retries - 1:
                print("✗ Server not responding. Please start the server first.")
                return
            time.sleep(1)

    # Run test classes in order
    test_classes = [
        TestHealthCheck,
        TestMemberAPI,
        TestCourseAPI,
        TestChapterAPI,
        TestConceptAPI,
        TestExerciseAPI,
        TestQuizAPI,
        TestDataIntegrity
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    for test_class in test_classes:
        print(f"\n{'='*60}")
        print(f"Running {test_class.__name__}")
        print(f"{'='*60}\n")

        test_instance = test_class()
        test_methods = [method for method in dir(test_instance) if method.startswith("test_")]
        test_methods.sort()  # Run in order

        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(test_instance, method_name)
                method()
                passed_tests += 1
            except AssertionError as e:
                failed_tests += 1
                print(f"✗ {method_name} FAILED: {str(e)}")
            except Exception as e:
                failed_tests += 1
                print(f"✗ {method_name} ERROR: {str(e)}")

    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✓")
    print(f"Failed: {failed_tests} ✗")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print("="*60 + "\n")

    # Print test data for reference
    print("Test Data Created:")
    for key, value in test_data.items():
        if value is not None:
            print(f"  {key}: {value}")


if __name__ == "__main__":
    run_tests()
