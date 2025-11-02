import { createFileRoute } from "@tanstack/react-router";

import ConceptPage from "@/pages/concept";

export const Route = createFileRoute("/lesson/$chapterId/exercise")({
  component: ConceptPage,
});
