import ChapterCard from "@/pages/course/ui/chapter-card.tsx";
import { Section } from "@/shared/ui";

const CoursePage = () => {
  // 기본 예시 데이터 (실제로는 API에서 받아올 것)
  // Course: id=1, totalSteps=5, completedSteps=3
  // 총 5개 챕터, 각 챕터는 1단계, 앞의 3개 챕터는 100% 완료
  const chapters: Chapter[] = [
    {
      id: 1,
      title: "표준편차의 기본 개념",
      description:
        "표준편차의 기본 개념과 수식의 의미를 이해합니다. 분산에서 표준편차로 변환하는 과정과 루트를 씌우는 이유를 학습하여 통계의 핵심 개념을 마스터합니다.",
      lastStepIndex: 3, // 완료 (100%)
    },
    {
      id: 2,
      title: "분산과 표준편차의 관계",
      description:
        "분산과 표준편차의 관계를 깊이 있게 탐구합니다. 두 개념의 정의, 계산 방법, 그리고 언제 어떤 지표를 사용해야 하는지 실전 예제와 함께 학습합니다.",
      lastStepIndex: 3, // 완료 (100%)
    },
    {
      id: 3,
      title: "표준편차의 계산과 해석",
      description:
        "표준편차가 큰 데이터셋과 작은 데이터셋의 의미를 이해합니다. 실제 데이터를 통해 표준편차가 데이터 해석에 미치는 영향을 실전적으로 학습합니다.",
      lastStepIndex: 3, // 완료 (100%)
    },
    {
      id: 4,
      title: "분산의 실전 활용",
      description:
        "분산을 활용한 실제 데이터 분석 사례를 학습합니다. 다양한 상황에서 분산을 계산하고 해석하는 방법을 실습을 통해 익힙니다.",
      lastStepIndex: 1, // 미시작 (0%)
    },
    {
      id: 5,
      title: "통계 지표의 종합 이해",
      description:
        "분산과 표준편차를 포함한 다양한 통계 지표들을 종합적으로 이해하고, 각 지표의 장단점과 활용 상황을 비교 분석합니다.",
      lastStepIndex: 0, // 미시작 (0%)
    },
  ];

  return (
    <Section
      subtitle="표준편차와 분산의 개념부터 실전 활용까지 체계적으로 학습합니다. 표준편차를 구하는 식에서 루트를 씌우는 이유, 분산과 표준편차의 차이점, 데이터셋 해석 방법을 배워보세요."
      title="표준편차와 분산 완전 정복"
    >
      <div className="grid gap-4 lg:grid-cols-2">
        {chapters.map((chapter) => (
          <ChapterCard key={chapter.id} chapter={chapter} />
        ))}
      </div>
    </Section>
  );
};

export default CoursePage;
