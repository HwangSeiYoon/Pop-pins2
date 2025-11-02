import { Button, tv } from "@heroui/react";
import { useNavigate } from "@tanstack/react-router";

import { ROUTE } from "@/shared/constants";
import { Card } from "@/shared/ui";

const style = tv({
  slots: {
    card: "p-6 transition-all",
    index: [
      "flex h-10 w-10 items-center justify-center rounded-full text-lg font-semibold",
      "bg-default text-default-600",
    ],
    description: ["flex list-disc flex-col gap-1 pl-6", "text-default-500"],
    title: ["text-xl font-semibold", "text-foreground-600"],
  },
  variants: {
    isActive: {
      true: {
        card: "ring-primary ring-2",
        index: "bg-primary text-primary-foreground",
        description: "text-foreground",
        title: "text-foreground",
      },
    },
  },
});

interface Props {
  content: Content;
  index: number;
  isActive: boolean;
}

const getTypeText = (type: Content["type"]) => {
  switch (type) {
    case "concept":
      return "개념 정리";
    case "exercise":
      return "실습 과제";
    case "quiz":
      return "퀴즈";
    default:
      return "";
  }
};

const StepCard = ({ content, index, isActive }: Props) => {
  const navigate = useNavigate();
  const styles = style({ isActive });

  return (
    <Card className={styles.card()}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex flex-col gap-4">
          <span className="flex items-center gap-3">
            <div className={styles.index()}>{index}</div>
            <div>
              <p className="text-default-500 text-sm">
                {getTypeText(content.type)}
              </p>
              <h4 className={styles.title()}>{content.title}</h4>
            </div>
          </span>
          <ul className={styles.description()}>
            {content.description.map((description) => (
              <li key={description}>{description}</li>
            ))}
          </ul>
        </div>
        <div className="flex items-center gap-2">
          <Button
            color={isActive ? "primary" : "default"}
            radius="full"
            size="sm"
            variant={isActive ? "solid" : "ghost"}
            onPress={() => navigate({ to: ROUTE[content.type] })}
          >
            {content.isCompleted ? "다시보기" : "학습하기"}
          </Button>
        </div>
      </div>
    </Card>
  );
};

export default StepCard;
