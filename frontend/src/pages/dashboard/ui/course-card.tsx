import { Button, Progress } from "@heroui/react";
import { useNavigate } from "@tanstack/react-router";
import { motion } from "framer-motion";

import { ROUTE } from "@/shared/constants";
import { Card } from "@/shared/ui";

interface Props {
  course: Course;
}

const CourseCard = ({ course }: Props) => {
  const navigate = useNavigate();

  const progress = Math.round(
    (course.completedSteps / course.totalSteps) * 100,
  );

  return (
    <motion.div transition={{ duration: 0.2 }} whileHover={{ y: -4 }}>
      <Card className="flex flex-col gap-3 px-6 py-5">
        <div className="flex grow justify-between gap-4">
          <div className="mb-2 flex flex-col gap-1">
            <h4 className="text-2xl font-semibold">{course.title}</h4>
            <div className="text-default-500 line-clamp-2">
              {course.description}
            </div>
          </div>
          <div className="flex h-full min-w-[72px] flex-col items-end justify-end text-right">
            <div className="text-lg font-bold">{progress}%</div>
            <div className="text-default-500 text-xs">{`${course.completedSteps}/${course.totalSteps} 단계`}</div>
          </div>
        </div>
        <Progress
          classNames={{
            indicator: "dark:bg-primary transition-background",
          }}
          color="secondary"
          size="sm"
          value={progress}
        />
        <div className="mt-2 flex flex-wrap gap-2">
          <Button
            className="w-full"
            color="secondary"
            radius="sm"
            onPress={() =>
              navigate({
                to: ROUTE.course,
                params: { courseId: course.id.toString() },
              })
            }
          >
            학습 하기
          </Button>
        </div>
      </Card>
    </motion.div>
  );
};

export default CourseCard;
