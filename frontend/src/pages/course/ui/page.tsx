import ChapterCard from "@/pages/course/ui/chapter-card.tsx";
import { Section } from "@/shared/ui";

const CoursePage = () => {
  return (
    <Section subtitle="Course Description" title="Course Title">
      <div className="grid gap-4 lg:grid-cols-2">
        <ChapterCard description="Chapter Description" />
        <ChapterCard description="Lorem ipsum dolor sit amet, consectetur adipiscing elit." />
        <ChapterCard description="Chapter Description" />
      </div>
    </Section>
  );
};

export default CoursePage;
