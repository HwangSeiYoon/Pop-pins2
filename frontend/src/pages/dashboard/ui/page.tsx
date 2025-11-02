import { motion } from "framer-motion";
import { BookOpenTextIcon, CircleCheckIcon } from "lucide-react";

import CourseCard from "@/pages/dashboard/ui/course-card.tsx";
import NewCourse from "@/pages/dashboard/ui/new-course.tsx";
import { Card, Section } from "@/shared/ui";

const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.4 },
};

const staggerContainer = {
  initial: { opacity: 0 },
  animate: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const staggerItem = {
  initial: { opacity: 0, y: 10 },
  animate: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.3 },
  },
};

const DashboardPage = () => {
  return (
    <Section
      subtitle="진행중인 모든 학습을 한눈에 관리하세요"
      title="내 학습 대시보드"
    >
      <motion.div
        animate="animate"
        className="grid grid-cols-2 gap-4 md:grid-cols-4"
        initial="initial"
        variants={staggerContainer}
      >
        {[
          { label: "진행 중", value: "2" },
          { label: "완료", value: null },
          { label: "주간 학습(가)", value: null },
          { label: "평균 정답률", value: null },
        ].map((stat, index) => (
          <motion.div key={stat.label} variants={staggerItem}>
            <Card className="p-6">
              <div className="text-default-500 text-sm">{stat.label}</div>
              <div className="text-3xl font-bold">{stat.value || "-"}</div>
            </Card>
          </motion.div>
        ))}
      </motion.div>

      <motion.h3
        animate={{ opacity: 1 }}
        className="mt-10 mb-4 flex items-center gap-2 text-xl font-semibold"
        initial={{ opacity: 0 }}
        transition={{ delay: 0.3, duration: 0.4 }}
      >
        <BookOpenTextIcon className="text-primary" /> 진행 중 학습
      </motion.h3>
      <motion.div
        animate="animate"
        className="grid gap-4 md:grid-cols-2"
        initial="initial"
        variants={staggerContainer}
      >
        <motion.div variants={staggerItem}>
          <CourseCard description="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris n" />
        </motion.div>
        <motion.div variants={staggerItem}>
          <NewCourse />
        </motion.div>
      </motion.div>

      <motion.h3
        animate={{ opacity: 1 }}
        className="mt-10 mb-4 flex items-center gap-2 text-xl font-semibold"
        initial={{ opacity: 0 }}
        transition={{ delay: 0.5, duration: 0.4 }}
      >
        <CircleCheckIcon className="text-primary" />
        완료한 학습
      </motion.h3>
    </Section>
  );
};

export default DashboardPage;
