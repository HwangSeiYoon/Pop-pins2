import { Button } from "@heroui/react";
import { useNavigate } from "@tanstack/react-router";
import { useState } from "react";

import CreateCourseForm from "@/pages/create-course/ui/form.tsx";
import { ROUTE } from "@/shared/constants";
import { Section } from "@/shared/ui";

const CreateCoursePage = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);

  return (
    <Section subtitle="학습 계획 만들어보세요" title="학습 계획 만들기">
      <CreateCourseForm />
      <div className="mt-3 flex w-full justify-end">
        <Button
          className="max-sm:w-full"
          color="primary"
          isLoading={isLoading}
          onPress={async () => {
            setIsLoading(true);
            await new Promise((resolve) => setTimeout(resolve, 2000));
            navigate({ to: ROUTE.dashboard });
          }}
        >
          생성
        </Button>
      </div>
    </Section>
  );
};

export default CreateCoursePage;
