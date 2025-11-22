import { api } from "@/shared/api";

export interface Course {
  id: number;
  title: string;
  description: string;
  difficulty: string;
  owner_id: number;
  created_at: string;
}

export interface Chapter {
  id: number;
  title: string;
  description: string;
  status: string;
  is_active: boolean;
  created_at: string;
}

// 코스 정보 조회
export const getCourseById = async (courseId: string) => {
  console.log("🔄 코스 정보 API 호출 시작 - courseId:", courseId);
  
  try {
    const result = await api.get<Course>(`course/${courseId}`);
    console.log("🔄 코스 정보 API 호출 성공:", result);
    return result;
  } catch (error) {
    console.error("🔄 코스 정보 API 호출 실패:", error);
    throw error;
  }
};

// 특정 사용자(owner_id)의 챕터 목록 조회
// 현재 백엔드 구조상 Course와 Chapter가 직접 연결되어 있지 않아서
// owner_id로 해당 사용자의 모든 챕터를 가져옵니다
export const getChaptersByOwnerId = async (ownerId: string) => {
  console.log("🔄 챕터 목록 API 호출 시작 - owner_id:", ownerId);
  
  try {
    const result = await api.get<Chapter[]>(`chapter?owner_id=${ownerId}`);
    console.log("🔄 챕터 목록 API 호출 성공:", result);
    return result;
  } catch (error) {
    console.error("🔄 챕터 목록 API 호출 실패:", error);
    throw error;
  }
};

// CourseMaker N8N 워크플로우 호출 타입 정의
export interface CourseMakerRequest {
  courseTitle: string;
  courseDescription: string;
  prompt: string;
  maxchapters: number;
  link: string[];
  difficulty: string;
  userToken?: string; // JWT 토큰 (선택적)
}

export interface GeneratedChapter {
  chapterId: number;
  chapterTitle: string;
  chapterDescription: string;
}

export interface CourseMakerResponse {
  course: {
    id: number;
    chapters: GeneratedChapter[];
  };
}

// CourseMaker N8N 워크플로우 호출
export const callCourseMaker = async (courseData: CourseMakerRequest): Promise<CourseMakerResponse> => {
  console.log("🤖 CourseMaker N8N 워크플로우 호출 시작:", courseData);
  
  try {
    // 로컬스토리지에서 JWT 토큰 가져오기
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('인증 토큰이 없습니다. 다시 로그인해주세요.');
    }
    
    // 요청 데이터에 토큰 추가
    const requestData = {
      ...courseData,
      userToken: token
    };
    
    // N8N CourseMaker 웹훅 엔드포인트 호출
    const response = await fetch('http://localhost:5678/webhook/course', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    });
    
    if (!response.ok) {
      throw new Error(`CourseMaker API 호출 실패: ${response.status}`);
    }
    
    const result = await response.json();
    console.log("🤖 CourseMaker N8N 워크플로우 호출 성공:", result);
    return result;
  } catch (error) {
    console.error("🤖 CourseMaker N8N 워크플로우 호출 실패:", error);
    throw error;
  }
};