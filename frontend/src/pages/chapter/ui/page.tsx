import { Button } from "@heroui/react";
import { CheckIcon, ListChecksIcon, PlayIcon } from "lucide-react";

import StepCard from "@/pages/chapter/ui/step-card.tsx";
import { Card, Section } from "@/shared/ui";

const ChapterPage = () => {
  return (
    <Section
      subtitle="Chapter Description · 0/3 단계 진행 중"
      title="Chapter Name"
    >
      <div className="flex flex-col-reverse gap-6 md:grid md:grid-cols-3">
        <div className="space-y-6 md:col-span-2">
          <StepCard isActive />
          <StepCard />
        </div>
        <div className="md:col-span-1">
          <Card className="sticky top-20 p-6">
            <h4 className="mb-4 flex items-center gap-2 text-lg font-semibold">
              <ListChecksIcon className="h-5 w-5" /> 진행 상황
            </h4>
            <ul className="space-y-2 text-sm">
              <li className="text-default-500 flex items-center gap-2">
                <CheckIcon className="h-4 w-4" />
                <span>Step 1: 개념정리</span>
              </li>
              <li className="text-foreground flex items-center gap-2">
                <PlayIcon className="h-4 w-4" />
                <span>Step 2: 실습과제</span>
              </li>
              <li className="text-foreground flex items-center gap-2">
                <PlayIcon className="h-4 w-4" />
                <span>Step 3: 형성평가</span>
              </li>
            </ul>
            <div className="mt-6 grid gap-2">
              <Button color="primary" variant="flat">
                실습과제로 이동
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </Section>
  );
};

export default ChapterPage;
