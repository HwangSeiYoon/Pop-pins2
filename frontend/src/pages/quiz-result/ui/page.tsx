import { Button, tv } from "@heroui/react";
import { Link } from "@tanstack/react-router";
import { ArrowLeftIcon, CheckCircle2Icon, XCircleIcon } from "lucide-react";

import { Card, Section } from "@/shared/ui";

const style = tv({
  slots: {
    index: [
      "flex h-10 w-10 items-center justify-center rounded-full text-lg font-semibold",
      "bg-secondary text-secondary-foreground",
    ],
    statusIcon: "h-5 w-5",
    statusText: "text-sm font-medium",
    feedbackContainer: "rounded-lg p-4",
    feedbackTitle: "mb-2 text-sm font-semibold",
    feedbackContent: "text-sm whitespace-pre-wrap",
  },
  variants: {
    isCorrect: {
      true: {
        index: "bg-primary/90 text-primary-foreground",
        statusIcon: "text-primary",
        statusText: "text-primary",
        feedbackContainer: "bg-primary/15",
        feedbackTitle: "text-primary",
      },
      false: {
        index: "bg-danger/90 text-danger-foreground",
        statusIcon: "text-danger",
        statusText: "text-danger",
        feedbackContainer: "bg-danger/15",
        feedbackTitle: "text-danger",
      },
    },
  },
});

interface QuizResult {
  questionId: number;
  question: string;
  userAnswer: string;
  isCorrect: boolean;
  feedback?: string;
  correctAnswer?: string;
}

interface QuizResultPageProps {
  results?: QuizResult[];
  totalScore?: number;
  totalQuestions?: number;
}

const QuizResultPage = ({
  results,
  totalScore,
  totalQuestions,
}: QuizResultPageProps) => {
  // 기본 예시 데이터 (실제로는 API에서 받아올 것)
  // 챕터 4: "분산의 실전 활용" 주제에 맞춘 결과
  const defaultResults: QuizResult[] = [
    {
      questionId: 1,
      question:
        "실제 데이터 분석에서 분산이 큰 값을 가진 경우, 이를 어떻게 해석하고 활용할 수 있나요?",
      userAnswer:
        "분산이 크다는 것은 데이터의 변동성이 크다는 의미입니다. 이를 통해 데이터의 불안정성을 파악하고, 리스크 관리나 품질 관리 등에 활용할 수 있습니다.",
      isCorrect: true,
      feedback:
        "정답입니다! 분산이 크면 데이터의 분산이 크고 불안정하다는 의미이므로, 이를 분석하여 위험 요소나 개선점을 찾을 수 있습니다.",
    },
    {
      questionId: 2,
      question:
        "다양한 상황에서 분산을 계산할 때 고려해야 할 주요 요소들은 무엇인가요?",
      userAnswer:
        "표본 크기, 데이터의 특성, 이상치의 존재 여부, 그리고 분석 목적 등을 고려해야 합니다.",
      isCorrect: true,
      feedback:
        "정답입니다! 이러한 요소들을 고려하여 적절한 분산 계산 방법을 선택해야 합니다.",
    },
    {
      questionId: 3,
      question:
        "분산을 활용한 실제 데이터 분석 사례에서, 분산의 값이 작을 때와 클 때 각각 어떤 의미를 가지나요?",
      userAnswer: "작을 때는 좋고 클 때는 나쁩니다.",
      isCorrect: false,
      feedback:
        "분산의 크기는 상황에 따라 다르게 해석됩니다. 작은 분산은 데이터가 평균 주변에 집중되어 있음을, 큰 분산은 데이터가 넓게 퍼져있음을 의미합니다.",
      correctAnswer:
        "분산이 작으면 데이터가 평균 주변에 집중되어 있고 일관성이 높으며, 클수록 데이터가 넓게 분산되어 있어 변동성이 크다는 의미입니다. 이는 상황에 따라 장점일 수도 단점일 수도 있습니다.",
    },
  ];

  const quizResults = results || defaultResults;
  const correctCount =
    totalScore ?? quizResults.filter((r) => r.isCorrect).length;
  const total = totalQuestions ?? quizResults.length;
  const percentage = Math.round((correctCount / total) * 100);

  return (
    <Section subtitle="퀴즈 채점 결과입니다" title="채점 결과">
      <div className="flex flex-col gap-6">
        {/* 점수 요약 */}
        <Card className="p-8">
          <div className="flex flex-col items-center gap-4">
            <div className="bg-secondary text-secondary-foreground flex h-32 w-32 items-center justify-center rounded-full text-4xl font-bold">
              {percentage}점
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold">
                {correctCount} / {total}
              </p>
              <p className="text-default-500 text-sm">정답 수</p>
            </div>
          </div>
        </Card>

        {/* 각 문제별 결과 */}
        <div className="flex flex-col gap-6">
          {quizResults.map((result) => {
            const styles = style({
              isCorrect: result.isCorrect,
            });
            const Icon = result.isCorrect ? CheckCircle2Icon : XCircleIcon;
            const statusText = result.isCorrect ? "정답" : "오답";

            return (
              <Card key={result.questionId} className="p-6">
                <div className="flex items-start gap-3">
                  <div className={styles.index()}>{result.questionId}</div>
                  <div className="flex flex-1 flex-col gap-4">
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-foreground flex-1 text-base leading-6 font-medium">
                        {result.question}
                      </p>
                      <div className="flex items-center gap-1">
                        <Icon className={styles.statusIcon()} />
                        <span className={styles.statusText()}>
                          {statusText}
                        </span>
                      </div>
                    </div>

                    {/* 사용자 답변 */}
                    <div className="bg-default-50 dark:bg-default-100 rounded-lg p-4">
                      <p className="text-default-600 mb-2 text-sm font-semibold">
                        내 답변
                      </p>
                      <p className="text-foreground text-sm whitespace-pre-wrap">
                        {result.userAnswer}
                      </p>
                    </div>

                    {/* 피드백 */}
                    {result.feedback && (
                      <div className={styles.feedbackContainer()}>
                        <p className={styles.feedbackTitle()}>
                          {result.isCorrect ? "피드백" : "오답 설명"}
                        </p>
                        <p className={styles.feedbackContent()}>
                          {result.feedback}
                        </p>
                      </div>
                    )}

                    {/* 정답 (오답인 경우만) */}
                    {!result.isCorrect && result.correctAnswer && (
                      <div
                        className={styles.feedbackContainer({
                          isCorrect: true,
                        })}
                      >
                        <p
                          className={styles.feedbackTitle({
                            isCorrect: true,
                          })}
                        >
                          정답
                        </p>
                        <p
                          className={styles.feedbackContent({
                            isCorrect: true,
                          })}
                        >
                          {result.correctAnswer}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            );
          })}
        </div>

        {/* 하단 버튼 */}
        <div className="flex justify-between">
          <Button
            as={Link}
            startContent={<ArrowLeftIcon className="h-4 w-4" />}
            variant="light"
          >
            뒤로 가기
          </Button>
          <Button as={Link} color="secondary">
            다시 풀기
          </Button>
        </div>
      </div>
    </Section>
  );
};

export default QuizResultPage;
