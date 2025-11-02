import { atom } from "jotai";
import type { Socket } from "socket.io-client";
import { io } from "socket.io-client";

import { tokenAtom } from "@/shared/store";

export const socketAtom = atom<Socket>((get) => {
  const token = get(tokenAtom);
  const baseURL = import.meta.env.VITE_SOCKET_BASE_URL || "";

  const socket = io(baseURL, {
    autoConnect: true,
    auth: token ? { token } : undefined,
    reconnectionAttempts: 5,
  });

  socket.io.on("reconnect_failed", () => {
    console.debug("서버 연결에 실패했습니다. 네트워크 상태를 확인해주세요.");
  });

  socket.on("connect", () => {
    console.debug("서버 연결에 성공했습니다.");
  });

  socket.on("disconnect", () => {
    console.debug("서버 연결이 끊어졌습니다.");
  });

  return socket;
});
