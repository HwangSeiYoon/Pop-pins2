import { createFileRoute } from "@tanstack/react-router";

import QuizResultPage from "@/pages/quiz-result";

export const Route = createFileRoute("/lesson/$chapterId/result")({
  component: QuizResultPage,
});

