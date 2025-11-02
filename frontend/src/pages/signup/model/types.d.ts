import type { z } from "zod";

import type { signupSchema } from "./schema";

export type SignupFormData = z.infer<typeof signupSchema>;
