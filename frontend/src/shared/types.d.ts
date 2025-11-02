interface Course {
  id: number;
  title: string;
  description: string;
  totalSteps: number;
  completedSteps: number;
}

interface Chapter {
  id: number;
  title: string;
  description: string;
  lastStepIndex: number;
}

interface Content {
  title: string;
  description: string[];
  isCompleted: boolean;
  type: "concept" | "exercise" | "quiz";
}

interface ChapterContents extends Chapter {
  concept: Content;
  exercise: Content;
  quiz: Content;
}
