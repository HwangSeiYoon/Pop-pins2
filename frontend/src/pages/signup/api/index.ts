import { HEADER, api } from "@/shared/api";

import type { SignupFormData } from "../model/types";

export const signup = async (data: SignupFormData) => {
  return api.post<unknown>("/member/signup", data, {
    headers: {
      [HEADER.SKIP_AUTH]: "true",
    },
  });
};
