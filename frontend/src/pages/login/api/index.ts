import { HEADER, api } from "@/shared/api";

import type { LoginFormData } from "../model/types";

interface LoginResponse {
  state: string;
  access_token: string;
  token_type: string;
  member: {
    id: number;
    email: string;
    created_at: string;
  };
}

export const login = async (data: LoginFormData) => {
  console.log("🔄 로그인 API 호출 시작");
  console.log("🔄 요청 URL:", `${import.meta.env.VITE_API_BASE_URL}/member/login`);
  console.log("🔄 요청 데이터:", data);
  
  try {
    const result = await api.post<LoginResponse>("member/login", data, {
      headers: {
        [HEADER.SKIP_AUTH]: "true",
      },
    });
    console.log("🔄 로그인 API 호출 성공:", result);
    return result;
  } catch (error) {
    console.error("🔄 로그인 API 호출 실패:", error);
    throw error;
  }
};

