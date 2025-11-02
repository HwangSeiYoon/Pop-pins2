import { Button } from "@heroui/react";

import { Card } from "@/shared/ui";

interface Props {
  description: string;
}

const ChapterCard = ({ description }: Props) => {
  return (
    <Card className="flex flex-row items-center justify-between gap-8 p-5">
      <div className="flex h-full flex-col justify-start gap-1">
        <div className="line-clamp-1 text-2xl font-semibold">Chapter 1</div>
        <div className="text-default-500 line-clamp-2 font-light">
          {description}
        </div>
      </div>
      <div className="flex items-center gap-4">
        <div className="text-right">
          <div className="text-lg font-bold">67%</div>
          <div className="text-default-500 text-xs">진행률</div>
        </div>
        <Button color="secondary" radius="full">
          이어하기
        </Button>
      </div>
    </Card>
  );
};

export default ChapterCard;
