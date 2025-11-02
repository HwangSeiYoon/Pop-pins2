import { useAtomValue } from "jotai";

import { socketAtom } from "./store";

export const useSocket = () => useAtomValue(socketAtom);
