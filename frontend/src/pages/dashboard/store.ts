import { atom } from "jotai";

export const courseListAtom = atom<Course[]>([
  {
    id: 1,
    title: "표준편차와 분산 완전 정복",
    description:
      "표준편차와 분산의 개념부터 실전 활용까지 체계적으로 학습합니다. 표준편차를 구하는 식에서 루트를 씌우는 이유, 분산과 표준편차의 차이점, 데이터셋 해석 방법을 배워보세요.",
    totalSteps: 5,
    completedSteps: 3,
  },
]);
