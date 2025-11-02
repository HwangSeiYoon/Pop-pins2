import { createFileRoute } from "@tanstack/react-router";

import CreateCoursePage from "@/pages/create-course";

export const Route = createFileRoute("/create")({
  component: CreateCoursePage,
});
