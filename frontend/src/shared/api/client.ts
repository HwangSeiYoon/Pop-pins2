import { getDefaultStore } from "jotai";
import ky from "ky";

import { tokenAtom } from "@/shared/store";

import * as HEADER from "./constants/headers";

const apiClient = ky.create({
  prefixUrl: import.meta.env.VITE_API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  hooks: {
    beforeRequest: [
      (request) => {
        if (request.headers.get(HEADER.SKIP_AUTH)) {
          request.headers.delete(HEADER.SKIP_AUTH);
          return;
        }

        const store = getDefaultStore();
        const token = store.get(tokenAtom);
        if (token) {
          request.headers.set("Authorization", `Bearer ${token}`);
        }
      },
    ],
  },
});

export const api = {
  get: async <T = unknown>(url: string, options?: RequestInit) => {
    const response = await apiClient.get(url, options);
    return {
      status: response.status,
      data: await response.json<T>(),
    };
  },

  post: async <T = unknown, D = unknown>(
    url: string,
    data: D,
    options?: RequestInit,
  ) => {
    const response = await apiClient.post(url, { json: data, ...options });
    return {
      status: response.status,
      data: await response.json<T>(),
    };
  },

  put: async <T = unknown, D = unknown>(
    url: string,
    data: D,
    options?: RequestInit,
  ) => {
    const response = await apiClient.put(url, { json: data, ...options });
    return {
      status: response.status,
      data: await response.json<T>(),
    };
  },

  patch: async <T = unknown, D = unknown>(
    url: string,
    data: D,
    options?: RequestInit,
  ) => {
    const response = await apiClient.patch(url, { json: data, ...options });
    return {
      status: response.status,
      data: await response.json<T>(),
    };
  },

  delete: async <T = unknown>(url: string, options?: RequestInit) => {
    const response = await apiClient.delete(url, options);
    return {
      status: response.status,
      data: await response.json<T>(),
    };
  },
};
