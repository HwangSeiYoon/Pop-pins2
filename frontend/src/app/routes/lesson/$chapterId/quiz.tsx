import { createFileRoute } from "@tanstack/react-router";

import QuizPage from "@/pages/quiz";

export const Route = createFileRoute("/lesson/$chapterId/quiz")({
  component: QuizPage,
});

