import { Button, Form, tv } from "@heroui/react";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link } from "@tanstack/react-router";
import { ArrowLeftIcon } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Card, HookFormTextarea, Section } from "@/shared/ui";

const style = tv({
  slots: {
    index: [
      "flex h-10 w-10 items-center justify-center rounded-full text-lg font-semibold",
      "bg-secondary text-secondary-foreground",
    ],
    questionCard: "p-6",
  },
});

interface QuizQuestion {
  id: number;
  question: string;
}

interface QuizPageProps {
  questions?: QuizQuestion[];
}

const QuizPage = ({ questions }: QuizPageProps) => {
  // 기본 예시 데이터 (실제로는 API에서 받아올 것)
  const defaultQuestions: QuizQuestion[] = [
    {
      id: 1,
      question: "표준편차를 구하는 식에서 루트를 씌우는 이유는 무엇인가요?",
    },
    {
      id: 2,
      question: "분산과 표준편차의 차이점을 설명해주세요.",
    },
    {
      id: 3,
      question: "표준편차가 큰 데이터셋과 작은 데이터셋의 의미는 무엇인가요?",
    },
  ];

  const quizQuestions = questions || defaultQuestions;

  // zod 스키마 생성 (동적으로 문제 개수에 맞춰 생성)
  const quizSchema = z.object({
    answers: z
      .array(
        z
          .string()
          .transform((val) => val.trim())
          .pipe(z.string().min(1, "답변을 입력해주세요.")),
      )
      .length(quizQuestions.length, "모든 문제에 답변해주세요."),
  });

  type QuizFormData = z.infer<typeof quizSchema>;

  const {
    control,
    handleSubmit,
    formState: { isSubmitting, isValid },
  } = useForm<QuizFormData>({
    resolver: zodResolver(quizSchema),
    defaultValues: {
      answers: new Array(quizQuestions.length).fill(""),
    },
  });

  const styles = style();

  const onSubmit = async (data: QuizFormData) => {
    // TODO: API로 답변 제출
    console.log("Submitted answers:", data.answers);
    // 제출 후 결과 페이지로 이동하거나 피드백 표시
  };

  return (
    <Section subtitle="문제를 풀고 제출해주세요" title="퀴즈">
      <Form onSubmit={handleSubmit(onSubmit)}>
        <div className="flex w-full flex-col gap-6">
          {quizQuestions.map((question, index) => (
            <Card key={question.id} className={styles.questionCard()}>
              <div className="flex items-start gap-3">
                <div className={styles.index()}>{question.id}</div>
                <div className="flex flex-1 flex-col gap-4">
                  <p className="text-foreground text-base leading-6 font-medium">
                    {question.question}
                  </p>
                  <HookFormTextarea
                    control={control}
                    name={`answers.${index}` as const}
                    placeholder="자유롭게 서술하세요."
                  />
                </div>
              </div>
            </Card>
          ))}

          <div className="flex justify-between">
            <Button
              as={Link}
              startContent={<ArrowLeftIcon className="h-4 w-4" />}
              variant="light"
            >
              뒤로 가기
            </Button>
            <Button
              color="primary"
              isDisabled={!isValid}
              isLoading={isSubmitting}
              type="submit"
            >
              제출하기
            </Button>
          </div>
        </div>
      </Form>
    </Section>
  );
};

export default QuizPage;
