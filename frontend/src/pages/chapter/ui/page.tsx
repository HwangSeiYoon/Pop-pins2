import { Button } from "@heroui/react";
import { CheckIcon, ListChecksIcon, PlayIcon } from "lucide-react";

import StepCard from "@/pages/chapter/ui/step-card.tsx";
import { Card, Section } from "@/shared/ui";

const contents: Content[] = [
  {
    type: "concept",
    title: "분산의 실전 활용 기초",
    description: [
      "분산이 큰 값을 가진 데이터의 의미와 해석 방법",
      "실제 데이터 분석에서 분산을 활용하는 전략",
      "다양한 상황에서 분산 계산 시 고려사항",
    ],
    isCompleted: true,
  },
  {
    type: "exercise",
    title: "실제 데이터로 분산 계산 및 해석",
    description: [
      "실제 데이터셋을 활용한 분산 계산 실습",
      "분산 값의 크기에 따른 데이터 해석 연습",
      "다양한 상황에서 분산을 활용한 분석 사례 연구",
    ],
    isCompleted: false,
  },
  {
    type: "quiz",
    title: "분산의 실전 활용 평가",
    description: [
      "분산의 실전 활용에 대한 이해도 평가",
      "실제 데이터 분석 상황에서의 분산 해석 능력 검증",
    ],
    isCompleted: false,
  },
];

const ChapterPage = () => {
  const activeIndex = contents.findIndex((content) => !content.isCompleted);

  return (
    <Section
      subtitle="분산을 활용한 실제 데이터 분석 사례를 학습합니다. 다양한 상황에서 분산을 계산하고 해석하는 방법을 실습을 통해 익힙니다."
      title="분산의 실전 활용"
    >
      <div className="flex flex-col-reverse gap-6 md:grid md:grid-cols-3">
        <div className="space-y-6 md:col-span-2">
          {contents.map((content, index) => (
            <StepCard
              key={content.title}
              content={content}
              index={index + 1}
              isActive={index === activeIndex}
            />
          ))}
        </div>
        <div className="md:col-span-1">
          <Card className="sticky top-20 p-6">
            <h4 className="mb-4 flex items-center gap-2 text-lg font-semibold">
              <ListChecksIcon className="h-5 w-5" /> 진행 상황
            </h4>
            <ul className="space-y-2 text-sm">
              {contents.map((content, index) => {
                const isCompleted = content.isCompleted;
                const Icon = isCompleted ? CheckIcon : PlayIcon;
                const stepNames = ["개념 정리", "실습 과제", "퀴즈"];

                return (
                  <li
                    key={index}
                    className={`flex items-center gap-2 ${
                      isCompleted ? "text-default-500" : "text-foreground"
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span>
                      Step {index + 1}: {stepNames[index]}
                    </span>
                  </li>
                );
              })}
            </ul>
            <div className="mt-6 grid gap-2">
              <Button color="primary" variant="flat">
                {contents[0].isCompleted
                  ? "실습 과제로 이동"
                  : "개념 정리로 이동"}
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </Section>
  );
};

export default ChapterPage;
