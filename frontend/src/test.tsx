import { BarChart3, BookOpen, Check, Circle, Clipboard, Download, FolderOpen, Home, Layers, ListChecks, PieChart, Play, Repeat, X } from "lucide-react";
import React from "react";

/***************************
 * Utils: routing & storage
 ***************************/
const parseHash = () => {
  const raw =
    (typeof window !== "undefined" ? window.location.hash.slice(1) : "") ||
    "/dashboard";
  const [path, query] = raw.split("?");
  const params = new URLSearchParams(query || "");
  return { path, params };
};

const useHashRoute = () => {
  const [route, setRoute] = React.useState(parseHash());
  React.useEffect(() => {
    if (typeof window === "undefined") return;
    const onHash = () => setRoute(parseHash());
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);
  return route;
};

// Storage keys
const K_PLANS = "pop.pins.plans"; // array of plans
const K_PROGRESS_PREFIX = "pop.pins.progress."; // + planId (overall step progress)
const K_CONCEPT_PROGRESS_PREFIX = "pop.pins.cprogress."; // + planId + '.' + concept
const K_QUIZ_PREFIX = "pop.pins.quiz."; // + planId

// Plan helpers
const loadPlans = () => {
  try {
    return JSON.parse(localStorage.getItem(K_PLANS) || "[]");
  } catch {
    return [];
  }
};
const savePlans = (plans) => {
  try {
    localStorage.setItem(K_PLANS, JSON.stringify(plans));
  } catch {}
};
const upsertPlan = (plan) => {
  const list = loadPlans();
  const idx = list.findIndex((p) => p.id === plan.id);
  if (idx >= 0) list[idx] = plan;
  else list.push(plan);
  savePlans(list);
};

// Overall Progress = { stepsDone:number, totalSteps:number, updatedAt:number }
const loadProgress = (planId) => {
  try {
    return JSON.parse(
      localStorage.getItem(K_PROGRESS_PREFIX + planId) || "null",
    );
  } catch {
    return null;
  }
};
const saveProgress = (planId, prog) => {
  try {
    localStorage.setItem(K_PROGRESS_PREFIX + planId, JSON.stringify(prog));
  } catch {}
};

// Concept-level Progress = { done:number, total:number, updatedAt:number }
const loadConceptProgress = (planId, concept) => {
  try {
    return JSON.parse(
      localStorage.getItem(
        K_CONCEPT_PROGRESS_PREFIX + planId + "." + concept,
      ) || "null",
    );
  } catch {
    return null;
  }
};
const saveConceptProgress = (planId, concept, prog) => {
  try {
    localStorage.setItem(
      K_CONCEPT_PROGRESS_PREFIX + planId + "." + concept,
      JSON.stringify(prog),
    );
  } catch {}
};

// Quiz payload stored per plan
const loadQuiz = (planId) => {
  try {
    return JSON.parse(localStorage.getItem(K_QUIZ_PREFIX + planId) || "null");
  } catch {
    return null;
  }
};
const saveQuiz = (planId, payload) => {
  try {
    localStorage.setItem(K_QUIZ_PREFIX + planId, JSON.stringify(payload));
  } catch {}
};

/***************************
 * Shared UI
 ***************************/
const Section = ({ id, title, subtitle, children }) => (
  <section
    className="mx-auto w-full max-w-6xl px-6 py-12 md:px-8 md:py-16"
    id={id}
  >
    {title && (
      <div className="mb-8">
        <h2 className="text-2xl font-bold tracking-tight md:text-4xl">
          {title}
        </h2>
        {subtitle && (
          <p className="text-default-500/80 mt-2 text-base md:text-lg">
            {subtitle}
          </p>
        )}
      </div>
    )}
    {children}
  </section>
);

const Card = ({ children, className = "" }) => (
  <div
    className={`bg-background/60 rounded-2xl border shadow-sm backdrop-blur transition-shadow hover:shadow-md ${className}`}
  >
    {children}
  </div>
);

const Nav = () => (
  <header className="bg-background/70 supports-[backdrop-filter]:bg-background/60 sticky top-0 z-40 border-b backdrop-blur">
    <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-6 md:px-8">
      <a
        className="text-lg font-extrabold tracking-tight md:text-xl"
        href="#/dashboard"
      >
        POP<span className="text-primary">.PINS</span>
      </a>
      <nav className="hidden items-center gap-6 text-sm md:flex">
        <a className="hover:text-primary" href="#/dashboard">
          대시보드
        </a>
        <a className="hover:text-primary" href="#/concepts">
          개념
        </a>
        <a className="hover:text-primary" href="#/study">
          학습
        </a>
        <a className="hover:text-primary" href="#/quiz">
          퀴즈
        </a>
        <a className="hover:text-primary" href="#/report">
          리포트
        </a>
      </nav>
    </div>
  </header>
);

/***************************
 * Seed demo plans if empty (Vector & Probability)
 ***************************/
function useSeedPlans() {
  React.useEffect(() => {
    const has = loadPlans();
    if (has.length > 0) return;
    const now = Date.now();
    const demo = [
      {
        id: "vector",
        title: "벡터 기초 1주 완성",
        start: "2025-10-22",
        end: "2025-10-29",
        level: "intermediate",
        steps: 4,
        withQuiz: true,
        topics: ["벡터", "내적", "외적"],
        resources: ["https://example.com/vector"],
        createdAt: now,
        status: "active",
      },
      {
        id: "prob",
        title: "확률과 통계 2주 완성",
        start: "2025-10-22",
        end: "2025-11-05",
        level: "beginner",
        steps: 3,
        withQuiz: true,
        topics: ["확률", "분산", "표준편차", "가설검정"],
        resources: ["https://example.com/prob"],
        createdAt: now,
        status: "active",
      },
    ];
    savePlans(demo);
    saveProgress("vector", { stepsDone: 1, totalSteps: 4, updatedAt: now });
    saveProgress("prob", { stepsDone: 2, totalSteps: 3, updatedAt: now });
  }, []);
}

/***************************
 * Dashboard (All plans overview)
 ***************************/
const ProgressBar = ({ value }) => (
  <div className="bg-muted h-2 overflow-hidden rounded-full">
    <div
      className="bg-primary h-full"
      style={{ width: `${Math.max(0, Math.min(100, value))}%` }}
    />
  </div>
);

function DashboardPage() {
  useSeedPlans();
  const [plans, setPlans] = React.useState([]);
  React.useEffect(() => {
    setPlans(loadPlans());
  }, []);

  const computeProgress = (p) => {
    const prog = loadProgress(p.id) || { stepsDone: 0, totalSteps: p.steps };
    const percent = Math.round(
      (prog.stepsDone / (prog.totalSteps || p.steps || 1)) * 100,
    );
    return { ...prog, percent };
  };

  const active = plans.filter((p) => p.status !== "completed");
  const completed = plans.filter((p) => p.status === "completed");

  const totalStudyHours = Math.round((active.length * 90) / 60); // demo metric
  const avgScore = (() => {
    const scores = plans
      .map((p) => loadQuiz(p.id)?.grading)
      .filter(Boolean)
      .map((g) => Math.round((g.correctCount / g.total) * 100));
    if (!scores.length) return 0;
    return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
  })();

  return (
    <div className="bg-background text-foreground min-h-screen">
      <Nav />
      <Section
        id="overview"
        subtitle="진행중인 모든 학습을 한눈에 관리하세요"
        title="내 학습 대시보드"
      >
        {/* Top KPIs */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Card className="p-6">
            <div className="text-default-500 text-sm">진행 중</div>
            <div className="text-3xl font-bold">{active.length}</div>
          </Card>
          <Card className="p-6">
            <div className="text-default-500 text-sm">완료</div>
            <div className="text-3xl font-bold">{completed.length}</div>
          </Card>
          <Card className="p-6">
            <div className="text-default-500 text-sm">주간 학습(가)</div>
            <div className="text-3xl font-bold">{totalStudyHours}h</div>
          </Card>
          <Card className="p-6">
            <div className="text-default-500 text-sm">평균 정답률</div>
            <div className="text-3xl font-bold">{avgScore}%</div>
          </Card>
        </div>

        {/* Active plans */}
        <div className="mt-10">
          <h3 className="mb-4 flex items-center gap-2 text-xl font-semibold">
            <Layers className="h-5 w-5" /> 진행 중 학습
          </h3>
          {active.length === 0 ? (
            <Card className="text-default-500 p-6 text-sm">
              진행 중인 학습이 없습니다.{" "}
              <a className="underline" href="#/study">
                새 학습을 시작하세요.
              </a>
            </Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {active.map((p) => {
                const prog = computeProgress(p);
                const dday = (() => {
                  const left = Math.ceil(
                    (new Date(p.end) - new Date()) / 86400000,
                  );
                  return isNaN(left)
                    ? "-"
                    : left >= 0
                      ? `D-${left}`
                      : `D+${Math.abs(left)}`;
                })();
                return (
                  <Card key={p.id} className="flex flex-col gap-3 p-5">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <div className="text-default-500 text-sm">
                          {p.level} · {p.start} ~ {p.end} · {dday}
                        </div>
                        <h4 className="mt-1 text-lg font-semibold">
                          {p.title}
                        </h4>
                      </div>
                      <div className="min-w-[72px] text-right">
                        <div className="text-lg font-bold">{prog.percent}%</div>
                        <div className="text-default-500 text-xs">
                          {prog.stepsDone}/{prog.totalSteps} 단계
                        </div>
                      </div>
                    </div>
                    <ProgressBar value={prog.percent} />
                    <div className="mt-2 flex flex-wrap gap-2">
                      <a
                        className="hover:bg-accent rounded-xl border px-3 py-1.5 text-sm"
                        href={`#/concepts?id=${p.id}`}
                      >
                        개념 목록
                      </a>
                      <a
                        className="bg-primary text-primary-foreground rounded-xl px-3 py-1.5 text-sm"
                        href={`#/study?id=${p.id}`}
                      >
                        학습 계속
                      </a>
                      <a
                        className="hover:bg-accent rounded-xl border px-3 py-1.5 text-sm"
                        href={`#/quiz?id=${p.id}`}
                      >
                        퀴즈
                      </a>
                      <a
                        className="hover:bg-accent rounded-xl border px-3 py-1.5 text-sm"
                        href={`#/report?id=${p.id}`}
                      >
                        리포트
                      </a>
                    </div>
                  </Card>
                );
              })}
            </div>
          )}
        </div>

        {/* Completed plans */}
        {completed.length > 0 && (
          <div className="mt-10">
            <h3 className="mb-4 text-xl font-semibold">완료한 학습</h3>
            <div className="grid gap-4 md:grid-cols-2">
              {completed.map((p) => (
                <Card
                  key={p.id}
                  className="flex items-center justify-between p-5"
                >
                  <div>
                    <div className="text-default-500 text-sm">
                      {p.start} ~ {p.end}
                    </div>
                    <h4 className="text-lg font-semibold">{p.title}</h4>
                  </div>
                  <a
                    className="hover:bg-accent rounded-xl border px-3 py-1.5 text-sm"
                    href={`#/report?id=${p.id}`}
                  >
                    리포트
                  </a>
                </Card>
              ))}
            </div>
          </div>
        )}
      </Section>
    </div>
  );
}

/***************************
 * Concepts List (per-plan topics as first-class)
 ***************************/
function ConceptsPage({ planId }) {
  const plan = loadPlans().find((p) => p.id === planId) || null;
  const topics = plan?.topics || [];

  const conceptPercent = (topic) => {
    const cp = loadConceptProgress(planId, topic) || { done: 0, total: 3 };
    return Math.round((cp.done / (cp.total || 3)) * 100);
  };

  return (
    <div className="bg-background text-foreground min-h-screen">
      <Nav />
      <Section
        id="concepts"
        subtitle="개념을 선택해 개념정리→실습과제→형성평가 순으로 진행하세요"
        title={`개념 목록 · ${plan?.title || planId || ""}`}
      >
        {!plan ? (
          <Card className="text-default-500 p-6 text-sm">
            플랜을 찾을 수 없습니다. 대시보드에서 플랜을 선택하세요.
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {topics.map((t) => (
              <Card key={t} className="flex items-center justify-between p-5">
                <div>
                  <div className="text-default-500 text-sm">개념</div>
                  <div className="text-lg font-semibold">{t}</div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <div className="text-lg font-bold">
                      {conceptPercent(t)}%
                    </div>
                    <div className="text-default-500 text-xs">진행률</div>
                  </div>
                  <a
                    className="bg-primary text-primary-foreground rounded-xl px-3 py-1.5 text-sm"
                    href={`#/concept?id=${planId}&topic=${encodeURIComponent(t)}`}
                  >
                    이어하기
                  </a>
                </div>
              </Card>
            ))}
          </div>
        )}
        <div className="mt-8">
          <a
            className="hover:bg-accent rounded-xl border px-3 py-1.5 text-sm"
            href="#/dashboard"
          >
            대시보드로
          </a>
        </div>
      </Section>
    </div>
  );
}

/***************************
 * Concept Study (topic → 3-steps flow like Today's Study)
 ***************************/
const ConceptStepCard = ({
  index,
  title,
  desc,
  isActive,
  onPrimary,
  onComplete,
}) => (
  <Card
    className={`p-6 transition-all ${isActive ? "ring-primary ring-2" : ""}`}
  >
    <div className="flex items-start justify-between gap-4">
      <div className="flex items-center gap-3">
        <div
          className={`flex h-8 w-8 items-center justify-center rounded-full font-semibold ${isActive ? "bg-primary text-primary-foreground" : "bg-muted text-foreground/70"}`}
        >
          {index}
        </div>
        <div>
          <h4 className="text-lg font-semibold">{title}</h4>
          <p className="text-default-500 mt-1 text-sm">{desc}</p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        {onPrimary}
        <button
          className={`hover:bg-accent rounded-full border px-3 py-1 text-xs ${isActive ? "bg-primary text-primary-foreground border-primary" : ""}`}
          onClick={onComplete}
        >
          {isActive ? "완료" : "진행"}
        </button>
      </div>
    </div>
  </Card>
);

function ConceptStudyPage({ planId, topic }) {
  const [activeIndex, setActiveIndex] = React.useState(0);
  const steps = [
    { title: "개념 정리", desc: `${topic} 핵심 이론 요약` },
    { title: "실습 과제", desc: `${topic} 관련 연습 문제 풀이` },
    { title: "형성평가", desc: `${topic} 개념 확인 퀴즈` },
  ];

  const prog = loadConceptProgress(planId, topic) || {
    done: 0,
    total: steps.length,
    updatedAt: 0,
  };
  React.useEffect(() => {
    setActiveIndex(Math.min(prog.done, steps.length - 1));
  }, []);

  const completeStep = (i) => {
    const cur = loadConceptProgress(planId, topic) || {
      done: 0,
      total: steps.length,
    };
    const done = Math.max(cur.done || 0, i + 1);
    saveConceptProgress(planId, topic, {
      done,
      total: steps.length,
      updatedAt: Date.now(),
    });
    if (i < steps.length - 1) setActiveIndex(i + 1);
  };

  return (
    <div className="bg-background text-foreground min-h-screen">
      <Nav />
      <Section
        id="concept-study"
        subtitle={`개념별 단계 진행 · ${loadConceptProgress(planId, topic)?.done || 0}/${steps.length}`}
        title={`오늘의 학습 · ${topic}`}
      >
        <div className="grid gap-6 md:grid-cols-3">
          <div className="space-y-6 md:col-span-2">
            {steps.map((s, i) => (
              <ConceptStepCard
                key={i}
                desc={s.desc}
                index={i + 1}
                isActive={i === activeIndex}
                title={s.title}
                onComplete={() => completeStep(i)}
                onPrimary={
                  i === 0 ? (
                    <a
                      className="hover:bg-accent rounded-full border px-3 py-1 text-xs"
                      href={`#/concept-detail?id=${planId}&topic=${encodeURIComponent(topic || "")}`}
                    >
                      개념 보기
                    </a>
                  ) : i === 1 ? (
                    <a
                      className="hover:bg-accent rounded-full border px-3 py-1 text-xs"
                      href={`#/concept-practice?id=${planId}&topic=${encodeURIComponent(topic || "")}`}
                    >
                      실습 시작
                    </a>
                  ) : null
                }
              />
            ))}
          </div>
          <div className="md:col-span-1">
            <Card className="sticky top-20 p-6">
              <h4 className="mb-4 flex items-center gap-2 text-lg font-semibold">
                <BookOpen className="h-5 w-5" /> {topic}
              </h4>
              <ul className="space-y-2 text-sm">
                {steps.map((s, i) => {
                  const d = loadConceptProgress(planId, topic)?.done || 0;
                  const done = i < d;
                  return (
                    <li key={i} className="flex items-center gap-2">
                      {done ? (
                        <Check className="text-primary h-4 w-4" />
                      ) : (
                        <Circle className="text-default-500 h-4 w-4" />
                      )}
                      <span
                        className={
                          done ? "text-foreground" : "text-default-500"
                        }
                      >
                        Step {i + 1}: {s.title}
                      </span>
                    </li>
                  );
                })}
              </ul>
              <div className="mt-6 grid gap-2">
                <a
                  className="hover:bg-accent inline-flex items-center justify-center gap-2 rounded-xl border px-4 py-2 text-sm"
                  href={`#/quiz?id=${planId}`}
                >
                  형성평가로 이동
                </a>
                <a
                  className="hover:bg-accent inline-flex items-center justify-center gap-2 rounded-xl border px-4 py-2 text-sm"
                  href={`#/concepts?id=${planId}`}
                >
                  개념 목록
                </a>
              </div>
            </Card>
          </div>
        </div>
      </Section>
    </div>
  );
}

/***************************
 * Concept Detail Page (topic overview content)
 ***************************/
function getConceptContent(topic) {
  const base = {
    요약: `${topic}의 핵심 개념을 직관적으로 정리합니다.`,
    핵심포인트: [
      `${topic}의 정의와 직관`,
      `${topic}을(를) 사용하는 상황/문제 유형`,
      `자주 하는 실수와 주의점`,
    ],
    공식: `${topic} 관련 기본 공식/표현을 한 눈에: e.g., P(A)=|A|/|Ω|`,
    예시: `${topic}을(를) 적용한 간단 예시 문제와 풀이 스케치`,
  };
  return base;
}

function ConceptDetailPage({ planId, topic }) {
  const content = getConceptContent(topic || "개념");
  const markDone = () => {
    const cur = loadConceptProgress(planId, topic) || { done: 0, total: 3 };
    const next = {
      done: Math.max(cur.done || 0, 1),
      total: 3,
      updatedAt: Date.now(),
    };
    saveConceptProgress(planId, topic, next);
    if (typeof window !== "undefined")
      window.location.hash = `#/concept?id=${planId}&topic=${encodeURIComponent(topic || "")}`;
  };
  return (
    <div className="bg-background text-foreground min-h-screen">
      <Nav />
      <Section
        id="concept-detail"
        subtitle="핵심 요약 · 공식 · 예시"
        title={`개념 정리 · ${topic}`}
      >
        <Card className="p-6">
          <h4 className="mb-2 text-lg font-semibold">요약</h4>
          <p className="text-default-500 text-sm">{content.요약}</p>
        </Card>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <Card className="p-6">
            <h4 className="mb-2 text-lg font-semibold">핵심 포인트</h4>
            <ul className="ml-6 list-disc space-y-1 text-sm">
              {content.핵심포인트.map((k, i) => (
                <li key={i}>{k}</li>
              ))}
            </ul>
          </Card>
          <Card className="p-6">
            <h4 className="mb-2 text-lg font-semibold">공식 / 표현</h4>
            <pre className="bg-muted/40 overflow-auto rounded-xl p-3 text-sm whitespace-pre-wrap">
              {content.공식}
            </pre>
          </Card>
        </div>
        <Card className="mt-4 p-6">
          <h4 className="mb-2 text-lg font-semibold">예시</h4>
          <p className="text-default-500 text-sm">{content.예시}</p>
        </Card>
        <div className="mt-6 flex flex-wrap gap-2">
          <button
            className="bg-primary text-primary-foreground rounded-xl px-4 py-2 text-sm"
            onClick={markDone}
          >
            이해했어요 (1단계 완료)
          </button>
          <a
            className="hover:bg-accent rounded-xl border px-4 py-2 text-sm"
            href={`#/concept?id=${planId}&topic=${encodeURIComponent(topic || "")}`}
          >
            개념 흐름으로 돌아가기
          </a>
        </div>
      </Section>
    </div>
  );
}

/***************************
 * Study (per-plan overall steps, kept for compatibility)
 ***************************/
const StepCard = ({
  index,
  title,
  desc,
  resources = [],
  isActive,
  onComplete,
}) => (
  <Card
    className={`p-6 transition-all ${isActive ? "ring-primary ring-2" : ""}`}
  >
    <div className="flex items-start justify-between">
      <div className="flex items-center gap-3">
        <div
          className={`flex h-8 w-8 items-center justify-center rounded-full font-semibold ${isActive ? "bg-primary text-primary-foreground" : "bg-muted text-foreground/70"}`}
        >
          {index}
        </div>
        <div>
          <h4 className="text-lg font-semibold">{title}</h4>
          <p className="text-default-500 mt-1 text-sm">{desc}</p>
        </div>
      </div>
      <button
        className={`hover:bg-accent ml-4 rounded-full border px-3 py-1 text-xs ${isActive ? "bg-primary text-primary-foreground border-primary" : ""}`}
        onClick={onComplete}
      >
        {isActive ? "완료" : "시작"}
      </button>
    </div>
    {resources.length > 0 && (
      <div className="text-default-500 mt-4 text-sm">
        <div className="mb-1 font-medium">참고 자료</div>
        <ul className="ml-6 list-disc space-y-1">
          {resources.map((r, i) => (
            <li key={i}>
              <a
                className="hover:underline"
                href={r}
                rel="noreferrer noopener"
                target="_blank"
              >
                {r}
              </a>
            </li>
          ))}
        </ul>
      </div>
    )}
  </Card>
);

function ConceptPracticePage({ planId, topic }) {
  const [checks, setChecks] = React.useState([false, false, false]);
  const [shortAnswer, setShortAnswer] = React.useState("");
  const [code, setCode] =
    React.useState(`// 여기에 의사코드 또는 풀이 스텝을 적어보세요
function solve() {
  // 예: 확률 P(A) = |A|/|Ω|
  return true;
}`);

  const allDone = checks.every(Boolean) && shortAnswer.trim().length >= 10;
  const toggle = (i) =>
    setChecks((prev) => prev.map((v, idx) => (idx === i ? !v : v)));

  const submitPractice = () => {
    if (!allDone) {
      alert("체크리스트와 짧은 답변을 완료해주세요.");
      return;
    }
    const cur = loadConceptProgress(planId, topic) || { done: 0, total: 3 };
    const next = {
      done: Math.max(cur.done || 0, 2),
      total: 3,
      updatedAt: Date.now(),
    };
    saveConceptProgress(planId, topic, next);
    if (typeof window !== "undefined") {
      window.location.hash = `#/concept?id=${planId}&topic=${encodeURIComponent(topic || "")}`;
    }
  };

  return (
    <div className="bg-background text-foreground min-h-screen">
      <Nav />
      <Section
        id="concept-practice"
        subtitle="체크리스트를 완료하고 짧은 답변을 제출하면 2단계가 완료됩니다"
        title={`실습 과제 · ${topic}`}
      >
        <div className="grid gap-4 md:grid-cols-2">
          <Card className="p-6">
            <h4 className="mb-3 font-semibold">체크리스트</h4>
            <ul className="space-y-2 text-sm">
              {[
                "핵심 공식/정의 재작성",
                "예시 문제 1개 풀이",
                "오답/오해 포인트 정리",
              ].map((t, i) => (
                <li key={i} className="flex items-center gap-2">
                  <input
                    checked={checks[i]}
                    type="checkbox"
                    onChange={() => toggle(i)}
                  />
                  <span>{t}</span>
                </li>
              ))}
            </ul>
            <div className="mt-4">
              <label className="text-sm font-medium">
                짧은 답변(최소 10자)
              </label>
              <textarea
                className="bg-background mt-1 w-full rounded-xl border px-3 py-2 text-sm"
                placeholder={`${topic}에서 가장 헷갈렸던 점은 무엇이었나요?`}
                rows={4}
                value={shortAnswer}
                onChange={(e) => setShortAnswer(e.target.value)}
              />
            </div>
          </Card>
          <Card className="p-6">
            <h4 className="mb-3 font-semibold">풀이 스케치</h4>
            <textarea
              className="bg-background w-full rounded-xl border px-3 py-2 font-mono text-sm"
              rows={12}
              value={code}
              onChange={(e) => setCode(e.target.value)}
            />
            <p className="text-default-500 mt-2 text-xs">
              * 실제 서비스에서는 코드 실행/파일 업로드/템플릿 주입 등을
              연결합니다.
            </p>
          </Card>
        </div>
        <div className="mt-6 flex gap-2">
          <button
            className={`rounded-xl px-4 py-2 text-sm ${allDone ? "bg-primary text-primary-foreground" : "text-default-500 border"}`}
            onClick={submitPractice}
          >
            제출하고 2단계 완료
          </button>
          <a
            className="hover:bg-accent rounded-xl border px-4 py-2 text-sm"
            href={`#/concept?id=${planId}&topic=${encodeURIComponent(topic || "")}`}
          >
            개념 흐름으로 돌아가기
          </a>
        </div>
      </Section>
    </div>
  );
}

function StudyPage({ planId }) {
  const [plan, setPlan] = React.useState(null);
  const [activeIndex, setActiveIndex] = React.useState(0);
  const [steps, setSteps] = React.useState([]);

  React.useEffect(() => {
    const all = loadPlans();
    const p = all.find((pl) => pl.id === planId) || all[0] || null;
    setPlan(p);
    if (!p) return;
    const prog = loadProgress(planId || p.id) || {
      stepsDone: 0,
      totalSteps: p.steps || 3,
    };
    const titles = Array.from({ length: p.steps || 3 }, (_, i) => [
      `Step ${i + 1}`,
      ["개념 정리", "실습 과제", "형성평가", "응용 문제"][i] || `단계 ${i + 1}`,
    ]);
    const arr = titles.map(([t, d], idx) => ({
      title: t,
      desc: d,
      done: idx < (prog.stepsDone || 0),
      resources: p.resources || [],
    }));
    setSteps(arr);
    setActiveIndex(Math.min(prog.stepsDone || 0, arr.length - 1));
  }, [planId]);

  const handleComplete = (i) => {
    const next = steps.map((s, idx) => (idx === i ? { ...s, done: true } : s));
    setSteps(next);
    const done = next.filter((s) => s.done).length;
    saveProgress(planId || plan?.id || "default", {
      stepsDone: done,
      totalSteps: next.length,
      updatedAt: Date.now(),
    });
    if (i < next.length - 1) setActiveIndex(i + 1);
  };

  if (!plan)
    return (
      <div className="bg-background text-foreground min-h-screen">
        <Nav />
        <Section subtitle="계획을 먼저 생성해주세요" title="학습" />
      </div>
    );

  const prog = loadProgress(planId || plan.id) || {
    stepsDone: 0,
    totalSteps: plan.steps,
  };

  return (
    <div className="bg-background text-foreground min-h-screen">
      <Nav />
      <Section
        id="study"
        subtitle={`${plan.start} ~ ${plan.end} · ${prog.stepsDone}/${prog.totalSteps} 단계 진행 중`}
        title={`${plan.title}`}
      >
        <div className="mb-6">
          <a
            className="hover:bg-accent inline-flex items-center gap-2 rounded-xl border px-3 py-1.5 text-sm"
            href={`#/concepts?id=${plan.id}`}
          >
            <FolderOpen className="h-4 w-4" /> 개념 목록으로
          </a>
        </div>
        <div className="grid gap-6 md:grid-cols-3">
          <div className="space-y-6 md:col-span-2">
            {steps.map((s, i) => (
              <StepCard
                key={i}
                desc={s.desc}
                index={i + 1}
                isActive={i === activeIndex}
                resources={s.resources}
                title={s.title}
                onComplete={() => handleComplete(i)}
              />
            ))}
          </div>
          <div className="md:col-span-1">
            <Card className="sticky top-20 p-6">
              <h4 className="mb-4 flex items-center gap-2 text-lg font-semibold">
                <ListChecks className="h-5 w-5" /> 진행 상황
              </h4>
              <ul className="space-y-2 text-sm">
                {steps.map((s, i) => (
                  <li key={i} className="flex items-center gap-2">
                    {s.done ? (
                      <Check className="text-primary h-4 w-4" />
                    ) : (
                      <Play className="text-default-500 h-4 w-4" />
                    )}
                    <span
                      className={
                        s.done ? "text-foreground" : "text-default-500"
                      }
                    >
                      Step {i + 1}: {s.desc}
                    </span>
                  </li>
                ))}
              </ul>
              <div className="mt-6 flex gap-2">
                <a
                  className="hover:bg-accent inline-flex w-full items-center justify-center gap-2 rounded-xl border px-4 py-2 text-sm"
                  href={`#/quiz?id=${planId || plan.id}`}
                >
                  퀴즈로 이동
                </a>
              </div>
            </Card>
          </div>
        </div>
      </Section>
    </div>
  );
}

/***************************
 * Quiz (per-plan)
 ***************************/
const QUIZ_ITEMS = [
  {
    id: 1,
    type: "multiple",
    question: "확률의 정의로 옳은 것은?",
    options: [
      "가능한 사건의 수를 전체 경우의 수로 나눈 값",
      "임의의 수를 더한 값",
      "항상 1보다 큰 값",
      "무작위로 결정되는 값",
    ],
    correct: 0,
  },
  {
    id: 2,
    type: "short",
    question: "표준편차에서 루트를 씌우는 이유는?",
    correctAnswer: "분산의 단위를 원래 데이터의 단위로 맞추기 위해",
  },
  {
    id: 3,
    type: "descriptive",
    question: "표본평균의 추정 성능을 설명하시오.",
    rubric: "표준오차 또는 신뢰구간 관련 서술",
  },
];

function gradeQuiz(answers) {
  let correctCount = 0;
  const per = QUIZ_ITEMS.map((q) => {
    let ok = false;
    if (q.type === "multiple") ok = answers[q.id] === q.correct;
    else if (q.type === "short") {
      const u = (answers[q.id] || "").trim();
      ok = !!u && q.correctAnswer.includes(u.slice(0, 2));
    } else {
      const u = (answers[q.id] || "").trim();
      ok = u.length > 30;
    }
    if (ok) correctCount++;
    return { id: q.id, correct: ok };
  });
  return { correctCount, total: QUIZ_ITEMS.length, per };
}

function QuizPage({ planId }) {
  const [answers, setAnswers] = React.useState({});
  const [submitted, setSubmitted] = React.useState(false);
  const startedAtRef = React.useRef(Date.now());

  const handleSelect = (id, val) =>
    setAnswers((prev) => ({ ...prev, [id]: val }));
  const handleSubmit = () => {
    setSubmitted(true);
    const grading = gradeQuiz(answers);
    const payload = {
      planId,
      answers,
      startedAt: startedAtRef.current,
      submittedAt: Date.now(),
      elapsedMs: Date.now() - startedAtRef.current,
      grading,
    };
    saveQuiz(planId || "default", payload);
  };

  return (
    <div className="bg-background text-foreground min-h-screen">
      <Nav />
      <Section
        id="quiz"
        subtitle="학습한 내용을 바탕으로 문제를 풀어보세요"
        title={`형성평가 ${planId ? `· ${planId}` : ""}`}
      >
        <div className="space-y-8">
          {QUIZ_ITEMS.map((q, i) => (
            <Card key={q.id} className="p-6">
              <div className="mb-4 flex items-center gap-3">
                <div className="bg-primary text-primary-foreground grid h-8 w-8 place-items-center rounded-full font-semibold">
                  {i + 1}
                </div>
                <h4 className="text-lg font-semibold">{q.question}</h4>
              </div>
              {q.type === "multiple" && (
                <ul className="space-y-2">
                  {q.options.map((opt, idx) => {
                    const sel = answers[q.id] === idx;
                    return (
                      <li key={idx}>
                        <button
                          className={`w-full rounded-xl border px-3 py-2 text-left text-sm ${sel ? "bg-primary text-primary-foreground border-primary" : "hover:bg-accent"}`}
                          disabled={submitted}
                          onClick={() => handleSelect(q.id, idx)}
                        >
                          {opt}
                        </button>
                      </li>
                    );
                  })}
                </ul>
              )}
              {(q.type === "short" || q.type === "descriptive") && (
                <textarea
                  className="bg-background mt-2 w-full rounded-xl border px-3 py-2 text-sm"
                  disabled={submitted}
                  placeholder={
                    q.type === "short"
                      ? "한두 문장으로 입력"
                      : "자유롭게 서술하세요."
                  }
                  rows={q.type === "short" ? 3 : 5}
                  value={answers[q.id] || ""}
                  onChange={(e) => handleSelect(q.id, e.target.value)}
                />
              )}
              {submitted && (
                <div className="mt-2 text-sm">
                  {q.type === "multiple" ? (
                    answers[q.id] === q.correct ? (
                      <span className="text-green-600">정답입니다!</span>
                    ) : (
                      <span className="text-red-600">
                        오답입니다. 정답: {q.options[q.correct]}
                      </span>
                    )
                  ) : q.type === "short" ? (
                    (answers[q.id] || "").trim().slice(0, 2) &&
                    q.correctAnswer.includes(
                      (answers[q.id] || "").trim().slice(0, 2),
                    ) ? (
                      <span className="text-green-600">
                        핵심 개념이 드러났어요!
                      </span>
                    ) : (
                      <span className="text-yellow-600">
                        조금 더 구체적으로 적어보세요.
                      </span>
                    )
                  ) : (answers[q.id] || "").trim().length > 30 ? (
                    <span className="text-green-600">충분히 구체적입니다.</span>
                  ) : (
                    <span className="text-blue-600">
                      예시/근거를 덧붙여보세요.
                    </span>
                  )}
                </div>
              )}
            </Card>
          ))}
        </div>
        <div className="mt-8 flex justify-end">
          {!submitted ? (
            <button
              className="bg-primary text-primary-foreground rounded-xl px-4 py-2 text-sm"
              onClick={handleSubmit}
            >
              제출하기
            </button>
          ) : (
            <a
              className="hover:bg-accent rounded-xl border px-4 py-2 text-sm"
              href={`#/report?id=${planId || "default"}`}
            >
              결과 확인하기
            </a>
          )}
        </div>
      </Section>
    </div>
  );
}

/***************************
 * Report (per-plan)
 ***************************/
const Ring = ({ percent = 0 }) => (
  <div className="relative h-24 w-24">
    <div
      className="absolute inset-0 rounded-full"
      style={{
        background: `conic-gradient(hsl(var(--primary)) ${percent}%, hsl(var(--muted)) ${percent}%)`,
      }}
    />
    <div className="bg-background absolute inset-2 grid place-items-center rounded-full text-sm font-bold">
      {percent}%
    </div>
  </div>
);
const MiniBars = ({ data }) => (
  <div className="grid h-24 grid-cols-5 items-end gap-3">
    {data.map((v, i) => (
      <div
        key={i}
        className="bg-primary/20 rounded-md"
        style={{ height: `${Math.max(12, v)}%` }}
      >
        <div
          className="bg-primary w-full rounded-md"
          style={{ height: `${v}%` }}
        />
      </div>
    ))}
  </div>
);

function ReportPage({ planId }) {
  const [payload, setPayload] = React.useState(null);
  const plan = loadPlans().find((p) => p.id === planId) || null;
  React.useEffect(() => {
    setPayload(loadQuiz(planId || "default"));
  }, [planId]);
  const grading = payload?.grading || {
    correctCount: 0,
    total: QUIZ_ITEMS.length,
    per: [],
  };
  const percent = Math.round(
    (grading.correctCount / (grading.total || 1)) * 100,
  );

  const exportJSON = () => {
    const blob = new Blob([JSON.stringify(payload || {}, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `report-${planId || "default"}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };
  const copySummary = async () => {
    const t = `계획: ${plan?.title || planId}\n점수: ${percent}% (${grading.correctCount}/${grading.total})`;
    try {
      await navigator.clipboard.writeText(t);
    } catch {}
  };

  return (
    <div className="bg-background text-foreground min-h-screen">
      <Nav />
      <Section
        id="report"
        subtitle="형성평가 결과를 요약·표·그래프로 제공합니다"
        title={`학습 리포트${plan ? ` · ${plan.title}` : ""}`}
      >
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Card className="grid place-items-center p-6 text-center">
            <Ring percent={percent} />
            <p className="text-default-500 mt-3 text-sm">정답률</p>
          </Card>
          <Card className="p-6">
            <div className="text-3xl font-bold">
              {grading.correctCount}/{grading.total}
            </div>
            <p className="text-default-500 mt-1 text-sm">정답/문항</p>
          </Card>
          <Card className="p-6">
            <div className="text-3xl font-bold">
              {Math.round((payload?.elapsedMs || 0) / 1000)}s
            </div>
            <p className="text-default-500 mt-1 text-sm">소요 시간</p>
          </Card>
          <Card className="p-6">
            <div className="text-3xl font-bold">
              {payload ? new Date(payload.submittedAt).toLocaleString() : "-"}
            </div>
            <p className="text-default-500 mt-1 text-sm">제출 시각</p>
          </Card>
        </div>
        <Card className="mt-8 p-6">
          <h4 className="mb-4 font-semibold">문항별 결과</h4>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="text-default-500 text-left">
                <tr>
                  <th className="py-2 pr-4">번호</th>
                  <th className="py-2 pr-4">문항</th>
                  <th className="py-2 pr-4">형식</th>
                  <th className="py-2 pr-4">정오답</th>
                </tr>
              </thead>
              <tbody>
                {QUIZ_ITEMS.map((q, i) => {
                  const ok = grading.per.find((p) => p.id === q.id)?.correct;
                  return (
                    <tr key={q.id} className="border-t">
                      <td className="py-3 pr-4">{i + 1}</td>
                      <td className="py-3 pr-4">{q.question}</td>
                      <td className="py-3 pr-4">{q.type}</td>
                      <td className="py-3 pr-4">
                        {ok ? (
                          <Check className="inline h-4 w-4 text-green-600" />
                        ) : (
                          <X className="inline h-4 w-4 text-red-600" />
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
        <div className="mt-8 grid gap-4 md:grid-cols-2">
          <Card className="p-6">
            <div className="mb-3 flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              <span className="font-semibold">문항별 분포</span>
            </div>
            <MiniBars
              data={QUIZ_ITEMS.map((q) =>
                grading.per.find((p) => p.id === q.id)?.correct ? 100 : 40,
              )}
            />
          </Card>
          <Card className="p-6">
            <div className="mb-3 flex items-center gap-2">
              <PieChart className="h-4 w-4" />
              <span className="font-semibold">정답률</span>
            </div>
            <div className="grid place-items-center">
              <Ring percent={percent} />
            </div>
          </Card>
        </div>
        <div className="mt-8 flex flex-wrap gap-2">
          <a
            className="hover:bg-accent inline-flex items-center gap-2 rounded-xl border px-4 py-2 text-sm"
            href={`#/quiz?id=${planId || "default"}`}
          >
            <Repeat className="h-4 w-4" /> 다시 풀기
          </a>
          <a
            className="hover:bg-accent inline-flex items-center gap-2 rounded-xl border px-4 py-2 text-sm"
            href={`#/study?id=${planId || ""}`}
          >
            <Home className="h-4 w-4" /> 학습으로
          </a>
          <button
            className="bg-primary text-primary-foreground inline-flex items-center gap-2 rounded-xl px-4 py-2 text-sm"
            onClick={exportJSON}
          >
            <Download className="h-4 w-4" /> JSON 내보내기
          </button>
          <button
            className="hover:bg-accent inline-flex items-center gap-2 rounded-xl border px-4 py-2 text-sm"
            onClick={copySummary}
          >
            <Clipboard className="h-4 w-4" /> 요약 복사
          </button>
        </div>
      </Section>
    </div>
  );
}

/***************************
 * App Router
 ***************************/
export default function POPPINS_App() {
  const { path, params } = useHashRoute();
  const planId = params.get("id") || undefined;
  const topic = params.get("topic") || undefined;
  if (path.startsWith("/concepts")) return <ConceptsPage planId={planId} />;
  if (path.startsWith("/concept-detail"))
    return <ConceptDetailPage planId={planId} topic={topic} />;
  if (path.startsWith("/concept-practice"))
    return <ConceptPracticePage planId={planId} topic={topic} />;
  if (path.startsWith("/concept"))
    return <ConceptStudyPage planId={planId} topic={topic} />;
  if (path.startsWith("/study")) return <StudyPage planId={planId} />;
  if (path.startsWith("/quiz")) return <QuizPage planId={planId} />;
  if (path.startsWith("/report")) return <ReportPage planId={planId} />;
  return <DashboardPage />;
}

/***************************
 * Smoke tests (existing + new)
 ***************************/
function runSmoke() {
  // seed check
  const list = loadPlans();
  console.assert(Array.isArray(list), "plans should be array");
  // progress guards
  saveProgress("TEST", { stepsDone: 2, totalSteps: 5, updatedAt: Date.now() });
  const p = loadProgress("TEST");
  console.assert(p && p.totalSteps === 5, "progress save/load failed");
  // router parse
  const r = (() => {
    const old = typeof window !== "undefined" ? window.location.hash : "";
    if (typeof window !== "undefined") window.location.hash = "#/study?id=prob";
    const val = parseHash();
    if (typeof window !== "undefined") window.location.hash = old;
    return val;
  })();
  console.assert(
    r.path === "/study" && r.params.get("id") === "prob",
    "router parse failed",
  );
  // grading basic
  const g = gradeQuiz({
    1: 0,
    2: "분산의",
    3: "충분히 자세한 서술문장을 아주 길게 작성해봅니다.",
  });
  console.assert(g.total === 3 && g.correctCount >= 2, "grading basic failed");
  // concept progress save/load
  saveConceptProgress("TESTPLAN", "확률", {
    done: 2,
    total: 3,
    updatedAt: Date.now(),
  });
  const cp = loadConceptProgress("TESTPLAN", "확률");
  console.assert(
    cp && cp.done === 2 && cp.total === 3,
    "concept progress save/load failed",
  );
  // topic route parse
  const r2 = (() => {
    const old = typeof window !== "undefined" ? window.location.hash : "";
    if (typeof window !== "undefined")
      window.location.hash = "#/concept?id=prob&topic=%ED%99%95%EB%A5%A0";
    const val = parseHash();
    if (typeof window !== "undefined") window.location.hash = old;
    return val;
  })();
  console.assert(
    r2.path === "/concept" &&
      r2.params.get("id") === "prob" &&
      !!r2.params.get("topic"),
    "concept route parse failed",
  );
  // concept-detail route parse
  const r3 = (() => {
    const old = typeof window !== "undefined" ? window.location.hash : "";
    if (typeof window !== "undefined")
      window.location.hash =
        "#/concept-detail?id=prob&topic=%ED%99%95%EB%A5%A0";
    const val = parseHash();
    if (typeof window !== "undefined") window.location.hash = old;
    return val;
  })();
  console.assert(
    r3.path === "/concept-detail" &&
      r3.params.get("id") === "prob" &&
      !!r3.params.get("topic"),
    "concept-detail route parse failed",
  );
  const r4 = (() => {
    const old = typeof window !== "undefined" ? window.location.hash : "";
    if (typeof window !== "undefined")
      window.location.hash =
        "#/concept-practice?id=prob&topic=%ED%99%95%EB%A5%A0";
    const val = parseHash();
    if (typeof window !== "undefined") window.location.hash = old;
    return val;
  })();
  console.assert(
    r4.path === "/concept-practice" &&
      r4.params.get("id") === "prob" &&
      !!r4.params.get("topic"),
    "concept-practice route parse failed",
  );
}

if (typeof window !== "undefined" && !window.__POP_PINS_MULTI_SMOKE__) {
  try {
    runSmoke();
  } catch (e) {
    console.warn(e);
  }
  window.__POP_PINS_MULTI_SMOKE__ = true;
}
