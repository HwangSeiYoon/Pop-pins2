import { createFileRoute } from "@tanstack/react-router";

import LoginPage from "@/pages/login";
import { ROUTE } from "@/shared/constants";

export const Route = createFileRoute(ROUTE.login)({
  component: LoginPage,
});
