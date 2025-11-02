import { Button, tv } from "@heroui/react";

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
  isActive?: boolean;
}

const StepCard = ({ isActive }: Props) => {
  const styles = style({ isActive });

  return (
    <Card className={styles.card()}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex flex-col gap-4">
          <span className="flex items-center gap-3">
            <div className={styles.index()}>{1}</div>
            <div>
              <p className="text-default-500 text-sm">개념정리</p>
              <h4 className={styles.title()}>제목</h4>
            </div>
          </span>
          <ul className={styles.description()}>
            <li>설명 1</li>
            <li>설명 2</li>
          </ul>
        </div>
        <div className="flex items-center gap-2">
          <Button
            color={isActive ? "primary" : "default"}
            radius="full"
            size="sm"
            variant={isActive ? "solid" : "ghost"}
          >
            {isActive ? "시작" : "완료"}
          </Button>
        </div>
      </div>
    </Card>
  );
};

export default StepCard;
