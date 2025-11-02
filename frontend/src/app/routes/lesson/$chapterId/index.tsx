import { createFileRoute } from "@tanstack/react-router";

import ChapterPage from "@/pages/chapter";

export const Route = createFileRoute("/lesson/$chapterId/")({
  component: () => {
    return <ChapterPage />;
  },
});
