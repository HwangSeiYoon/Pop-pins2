import { Button, Progress } from "@heroui/react";
import { motion } from "framer-motion";

import { Card } from "@/shared/ui";

interface Props {
  description: string;
}

const CourseCard = ({ description }: Props) => {
  return (
    <motion.div transition={{ duration: 0.2 }} whileHover={{ y: -4 }}>
      <Card className="flex flex-col gap-3 px-6 py-5">
        <div className="flex grow justify-between gap-4">
          <div className="mb-2 flex flex-col gap-1">
            <h4 className="text-2xl font-semibold">벡터 기초 1주 완성</h4>
            <div className="text-default-500 line-clamp-2">{description}</div>
          </div>
          <div className="flex h-full min-w-[72px] flex-col items-end justify-end text-right">
            <div className="text-lg font-bold">100%</div>
            <div className="text-default-500 text-xs">1/4 단계</div>
          </div>
        </div>
        <Progress
          classNames={{
            indicator: "dark:bg-primary transition-background",
          }}
          color="secondary"
          size="sm"
          value={25}
        />
        <div className="mt-2 flex flex-wrap gap-2">
          <Button className="w-full" color="secondary" radius="sm">
            학습 하기
          </Button>
        </div>
      </Card>
    </motion.div>
  );
};

export default CourseCard;
