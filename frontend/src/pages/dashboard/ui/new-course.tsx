import { motion } from "framer-motion";
import { CirclePlusIcon } from "lucide-react";

import {
  Card,
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyTitle,
} from "@/shared/ui";

const NewCourse = () => {
  return (
    <motion.div transition={{ duration: 0.2 }}>
      <Card
        isPressable
        className="hover:bg-content2 w-full border-2 border-dashed shadow-none hover:shadow-none"
      >
        <Empty>
          <EmptyHeader>
            <CirclePlusIcon className="text-foreground-700 mb-2 size-10" />
            <EmptyTitle>새로운 학습 만들기</EmptyTitle>
            <EmptyDescription>
              직접 주제를 설정하고 학습을 설계해보세요.
            </EmptyDescription>
          </EmptyHeader>
        </Empty>
      </Card>
    </motion.div>
  );
};

export default NewCourse;
