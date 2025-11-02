import { createFileRoute } from "@tanstack/react-router";

import QuizPage from "@/pages/quiz";

export const Route = createFileRoute("/lesson/$chapterId/quiz")({
  component: () => {
    const { chapterId } = Route.useParams();

    return <QuizPage chapterId={chapterId} />;
  },
});
