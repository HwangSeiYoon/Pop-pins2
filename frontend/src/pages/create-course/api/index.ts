import { api } from "@/shared/api";

export interface CreateCourseData {
  title: string;
  description: string;
  difficulty: "easy" | "medium" | "hard";
}

export interface CourseResponse {
  id: number;
  title: string;
  description: string;
  difficulty: string;
  owner_id: number;
  created_at: string;
}

// CourseMaker 요청 데이터 인터페이스
export interface CourseMakerRequest {
  courseTitle: string;
  courseDescription: string;
  prompt: string;
  maxchapters: number;
  link: string[];
  difficulty: string;
  userToken: string;
}

// CourseMaker 응답 데이터 인터페이스
export interface CourseMakerResponse {
  id: number;
  title: string;
  description: string;
  difficulty: string;
  owner_id: number;
  created_at: string;
  chapters: Array<{
    id: number;
    title: string;
    description: string;
    status: string;
  }>;
}

export const createCourse = async (data: CreateCourseData) => {
  console.log("🔄 코스 생성 API 호출 시작");
  console.log("🔄 요청 데이터:", data);
  
  try {
    // JWT 토큰이 자동으로 포함됨 (SKIP_AUTH 헤더 제거)
    const result = await api.post<CourseResponse>("course", data);
    console.log("🔄 코스 생성 API 호출 성공:", result);
    return result;
  } catch (error) {
    console.error("🔄 코스 생성 API 호출 실패:", error);
    throw error;
  }
};

// CourseMaker N8N 웹훅 호출 함수
export const callCourseMaker = async (data: Omit<CourseMakerRequest, 'userToken'>) => {
  console.log("🚀 CourseMaker 호출 시작");
  console.log("🚀 요청 데이터:", data);
  
  try {
    // localStorage에서 JWT 토큰 가져오기 (atomWithStorage의 JSON 처리 고려)
    let token = localStorage.getItem('token');
    if (!token || token === 'null') {
      throw new Error('로그인이 필요합니다');
    }
    
    // atomWithStorage는 JSON.stringify로 저장하므로 JSON.parse 필요
    try {
      token = JSON.parse(token);
    } catch (e) {
      // 이미 문자열인 경우 그대로 사용
    }
    
    // 혹시 여전히 따옴표가 있다면 제거
    if (typeof token === 'string' && token.startsWith('"') && token.endsWith('"')) {
      token = token.slice(1, -1);
    }
    
    console.log("🔍 정제된 토큰:", token?.substring(0, 50) + "...");

    const requestData: CourseMakerRequest = {
      ...data,
      userToken: token
    };

    console.log("🔍 N8N으로 보내는 요청 데이터:", JSON.stringify(requestData, null, 2));

    // N8N 웹훅 호출
    const response = await fetch('http://localhost:5678/webhook/course', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData)
    });

    console.log("🔍 N8N 응답 상태:", response.status, response.statusText);
    console.log("🔍 N8N 응답 헤더:", Object.fromEntries(response.headers.entries()));

    if (!response.ok) {
      throw new Error(`CourseMaker 호출 실패: ${response.status}`);
    }

    // 응답 텍스트를 먼저 확인
    const responseText = await response.text();
    console.log("🔍 N8N 원시 응답:", responseText);

    if (!responseText || responseText.trim() === '') {
      throw new Error('N8N에서 빈 응답을 받았습니다');
    }

    let result: CourseMakerResponse;
    try {
      result = JSON.parse(responseText) as CourseMakerResponse;
    } catch (parseError) {
      console.error("🔍 JSON 파싱 실패:", responseText);
      throw new Error(`N8N 응답 파싱 실패: ${parseError}`);
    }
    console.log("🚀 CourseMaker 호출 성공:", result);
    return result;
  } catch (error) {
    console.error("🚀 CourseMaker 호출 실패:", error);
    throw error;
  }
};