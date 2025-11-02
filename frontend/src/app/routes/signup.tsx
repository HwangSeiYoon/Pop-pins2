import { createFileRoute } from "@tanstack/react-router";

import SignupPage from "@/pages/signup";
import { ROUTE } from "@/shared/constants";

export const Route = createFileRoute(ROUTE.signup)({
  component: SignupPage,
});
