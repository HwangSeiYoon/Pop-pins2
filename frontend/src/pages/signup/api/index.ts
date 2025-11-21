import { HEADER, api } from "@/shared/api";

import type { SignupFormData } from "../model/types";

export const signup = async (data: SignupFormData) => {
  console.log("🔄 API 호출 시작 - signup");
  console.log("🔄 요청 URL:", `${import.meta.env.VITE_API_BASE_URL}/member/signup`);
  console.log("🔄 요청 데이터:", data);
  console.log("🔄 요청 헤더:", { [HEADER.SKIP_AUTH]: "true" });
  
  try {
    const result = await api.post<unknown>("member/signup", data, {
      headers: {
        [HEADER.SKIP_AUTH]: "true",
      },
    });
    console.log("🔄 API 호출 성공:", result);
    return result;
  } catch (error) {
    console.error("🔄 API 호출 실패:", error);
    throw error;
  }
};
