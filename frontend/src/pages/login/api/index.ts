import { HEADER, api } from "@/shared/api";

import type { LoginFormData } from "../model/types";

export const login = async (data: LoginFormData) => {
  return api.post<{ token: string }>("/member/login", data, {
    headers: {
      [HEADER.SKIP_AUTH]: "true",
    },
  });
};

