import { createFileRoute } from "@tanstack/react-router";

import CoursePage from "@/pages/course";

export const Route = createFileRoute("/study/$courseId/")({
  component: () => {
    const { courseId } = Route.useParams();
    return <CoursePage courseId={courseId} />;
  },
});
