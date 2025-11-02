import { Button } from "@heroui/react";
import { Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import {
  BookOpenIcon,
  CheckCircleIcon,
  GraduationCapIcon,
  SparklesIcon,
} from "lucide-react";

import { ROUTE } from "@/shared/constants";
import { sectionStyle } from "@/shared/styles";
import { Card } from "@/shared/ui";
import Footer from "@/widgets/footer";

const features = [
  {
    icon: SparklesIcon,
    title: "AI 기반 학습 계획",
    description:
      "AI가 당신의 학습 목표와 시간에 맞춰 최적화된 학습 계획을 자동으로 생성합니다.",
  },
  {
    icon: BookOpenIcon,
    title: "체계적인 학습 과정",
    description:
      "개념 정리부터 실습, 평가까지 단계별로 구성된 체계적인 학습 과정을 제공합니다.",
  },
  {
    icon: GraduationCapIcon,
    title: "개인화된 학습 추적",
    description:
      "학습 진행 상황과 성과를 실시간으로 추적하고, 맞춤형 피드백을 제공합니다.",
  },
  {
    icon: CheckCircleIcon,
    title: "성과 분석 리포트",
    description:
      "상세한 학습 리포트를 통해 자신의 학습 패턴과 성장을 분석할 수 있습니다.",
  },
];

const fadeInUp = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6 },
};

const staggerContainer = {
  initial: { opacity: 0 },
  animate: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2,
    },
  },
};

const staggerItem = {
  initial: { opacity: 0, y: 20 },
  animate: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5 },
  },
};

const LandingPage = () => {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Hero Section */}
      <section className="relative flex max-h-[960px] min-h-[80vh] flex-col items-center justify-center overflow-hidden py-20 text-center">
        <motion.div
          animate="animate"
          className={sectionStyle()}
          initial="initial"
          variants={staggerContainer}
        >
          <motion.h1
            className="mb-6 text-5xl font-extrabold tracking-tight md:text-6xl lg:text-7xl"
            variants={fadeInUp}
          >
            스마트한 학습,
            <br />
            <motion.span
              animate={{ opacity: 1, scale: 1 }}
              className="from-primary-400 via-primary-500 to-primary-700 bg-linear-to-r bg-clip-text text-transparent"
              initial={{ opacity: 0, scale: 0.8 }}
              transition={{ delay: 0.3, duration: 0.5 }}
            >
              POPPINS
            </motion.span>
            와 함께
          </motion.h1>
          <motion.p
            className="text-default-600 mb-10 text-lg md:text-xl"
            variants={fadeInUp}
          >
            AI가 만들어주는 맞춤형 학습 계획으로
            <br />더 효율적이고 체계적으로 학습하세요
          </motion.p>
          <motion.div
            className="flex flex-col items-center justify-center gap-4 sm:flex-row"
            variants={fadeInUp}
          >
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button
                as={Link}
                className="min-w-[200px]"
                color="primary"
                size="lg"
                to={ROUTE.signup}
              >
                무료로 시작하기
              </Button>
            </motion.div>
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button
                as={Link}
                className="min-w-[200px]"
                size="lg"
                to={ROUTE.login}
                variant="bordered"
              >
                로그인
              </Button>
            </motion.div>
          </motion.div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="bg-default-50 py-20">
        <div className={sectionStyle()}>
          <motion.div
            className="mb-16 text-center"
            initial="initial"
            variants={fadeInUp}
            viewport={{ once: true, margin: "-100px" }}
            whileInView="animate"
          >
            <h2 className="mb-4 text-3xl font-bold md:text-4xl">
              왜 POPPINS인가요?
            </h2>
            <p className="text-default-600 text-lg">
              학습의 모든 것을 한 곳에서 관리하고, AI의 도움으로 더 스마트하게
              학습하세요
            </p>
          </motion.div>
          <motion.div
            className="grid gap-6 px-6 md:grid-cols-2 lg:grid-cols-4"
            initial="initial"
            variants={staggerContainer}
            viewport={{ once: true, margin: "-50px" }}
            whileInView="animate"
          >
            {features.map((feature) => {
              const Icon = feature.icon;
              return (
                <motion.div key={feature.title} variants={staggerItem}>
                  <motion.div
                    whileHover={{ y: -8, transition: { duration: 0.2 } }}
                  >
                    <Card className="p-6">
                      <motion.div
                        className="bg-primary/10 mb-4 flex h-12 w-12 items-center justify-center rounded-lg"
                        transition={{ duration: 0.5 }}
                        whileHover={{ rotate: 360, scale: 1.1 }}
                      >
                        <Icon className="text-primary h-6 w-6" />
                      </motion.div>
                      <h3 className="mb-2 text-xl font-semibold">
                        {feature.title}
                      </h3>
                      <p className="text-default-600 text-sm">
                        {feature.description}
                      </p>
                    </Card>
                  </motion.div>
                </motion.div>
              );
            })}
          </motion.div>
        </div>
      </section>

      {/* How it works Section */}
      <section className="py-20">
        <div className={sectionStyle()}>
          <motion.div
            className="mb-16 text-center"
            initial="initial"
            variants={fadeInUp}
            viewport={{ once: true, margin: "-100px" }}
            whileInView="animate"
          >
            <h2 className="mb-4 text-3xl font-bold md:text-4xl">
              어떻게 작동하나요?
            </h2>
            <p className="text-default-600 text-lg">
              간단한 3단계로 학습을 시작하세요
            </p>
          </motion.div>
          <motion.div
            className="grid gap-8 px-6 md:grid-cols-3"
            initial="initial"
            variants={staggerContainer}
            viewport={{ once: true, margin: "-50px" }}
            whileInView="animate"
          >
            {[
              {
                number: "1",
                title: "학습 계획 생성",
                description:
                  "학습 목표와 기간을 입력하면 AI가 최적화된 학습 계획을 생성합니다",
              },
              {
                number: "2",
                title: "단계별 학습",
                description:
                  "개념 정리, 실습, 평가 등 구성된 단계를 따라 학습합니다",
              },
              {
                number: "3",
                title: "성과 확인",
                description:
                  "학습 리포트를 통해 진행 상황과 성과를 확인하고 개선합니다",
              },
            ].map((step, index) => (
              <motion.div
                key={step.number}
                className="text-center"
                variants={staggerItem}
              >
                <motion.div
                  className="text-center"
                  transition={{ duration: 0.2 }}
                  whileHover={{ scale: 1.05 }}
                >
                  <motion.div
                    className="bg-primary/10 text-primary mb-4 inline-flex h-16 w-16 items-center justify-center rounded-full text-2xl font-bold"
                    initial={{ scale: 0, rotate: -180 }}
                    transition={{
                      delay: index * 0.2,
                      type: "spring",
                      stiffness: 200,
                    }}
                    viewport={{ once: true }}
                    whileInView={{ scale: 1, rotate: 0 }}
                  >
                    {step.number}
                  </motion.div>
                  <h3 className="mb-2 text-xl font-semibold">{step.title}</h3>
                  <p className="text-default-600 text-sm">{step.description}</p>
                </motion.div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-primary/5 dark:bg-primary/10 py-20">
        <motion.div
          className={sectionStyle({
            class: "text-center",
          })}
          initial="initial"
          variants={staggerContainer}
          viewport={{ once: true, margin: "-100px" }}
          whileInView="animate"
        >
          <motion.h2
            className="mb-4 text-3xl font-bold md:text-4xl"
            variants={fadeInUp}
          >
            지금 시작하세요
          </motion.h2>
          <motion.p
            className="text-default-600 mb-8 text-lg"
            variants={fadeInUp}
          >
            POPPINS와 함께 더 스마트하고 효율적인 학습을 경험해보세요
          </motion.p>
          <motion.div
            variants={fadeInUp}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Button
              as={Link}
              className="min-w-[200px]"
              color="primary"
              size="lg"
              to={ROUTE.signup}
            >
              무료로 시작하기
            </Button>
          </motion.div>
        </motion.div>
      </section>

      {/* Footer */}
      <Footer />
    </div>
  );
};

export default LandingPage;
