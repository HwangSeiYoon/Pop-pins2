import { useEffect, useState } from "react";
import ChapterCard from "@/pages/course/ui/chapter-card.tsx";
import { Section } from "@/shared/ui";
import { getCourseById, getChaptersByOwnerId, callCourseMaker, type Chapter as ApiChapter, type CourseMakerRequest } from "../api";

interface CoursePageProps {
  courseId: string;
}

// UI에서 사용하는 Chapter 타입 (ChapterCard에서 요구하는 구조)
interface UIChapter {
  id: number;
  title: string;
  description: string;
  lastStepIndex: number;
}

const CoursePage = ({ courseId }: CoursePageProps) => {
  const [chapters, setChapters] = useState<UIChapter[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [courseMakerLoading, setCourseMakerLoading] = useState(false);

  // CourseMaker N8N 워크플로우 호출 함수
  const handleCourseMaker = async () => {
    try {
      setCourseMakerLoading(true);
      
      // 사용자로부터 코스 정보 입력받기
      const courseTitle = prompt("강의 제목을 입력하세요:");
      if (!courseTitle?.trim()) return;
      
      const courseDescription = prompt("강의 설명을 입력하세요:");
      if (!courseDescription?.trim()) return;
      
      const maxChapters = prompt("최대 챕터 수를 입력하세요 (예: 5):");
      if (!maxChapters?.trim()) return;
      
      const courseMakerData: CourseMakerRequest = {
        courseTitle: courseTitle.trim(),
        courseDescription: courseDescription.trim(),
        prompt: "AI가 체계적인 학습 커리큘럼을 설계해주세요",
        maxchapters: parseInt(maxChapters) || 5,
        link: [],
        difficulty: "medium"
      };
      
      console.log("🤖 CourseMaker 호출 데이터:", courseMakerData);
      
      // N8N CourseMaker 워크플로우 호출
      const result = await callCourseMaker(courseMakerData);
      console.log("🤖 CourseMaker 결과:", result);
      
      alert(`✅ 커리큘럼 생성 완료!\n생성된 챕터 수: ${result.course.chapters.length}개\n페이지를 새로고침하여 확인해보세요.`);
      
      // 페이지 새로고침으로 새로 생성된 챕터들 표시
      window.location.reload();
      
    } catch (error) {
      console.error("🤖 CourseMaker 호출 실패:", error);
      alert("AI 커리큘럼 생성에 실패했습니다. 다시 시도해주세요.");
    } finally {
      setCourseMakerLoading(false);
    }
  };

  useEffect(() => {
    const fetchCourseAndChapters = async () => {
      try {
        console.log("📚 코스 페이지 - courseId:", courseId);
        
        // 1. 먼저 Course 정보 조회 (Course의 owner_id 가져오기)
        const courseResponse = await getCourseById(courseId);
        console.log("📚 받은 코스 데이터:", courseResponse.data);
        
        // 백엔드에서 { course: {...} } 형태로 응답하므로
        const courseData = (courseResponse.data as any).course || courseResponse.data;
        const ownerId = courseData.owner_id;
        
        console.log("📚 코스 소유자 ID:", ownerId);
        
        // 2. 해당 소유자의 Chapter들 조회
        const chaptersResponse = await getChaptersByOwnerId(ownerId.toString());
        console.log("📚 받은 챕터 데이터:", chaptersResponse.data);
        
        // API 데이터를 UI 형식으로 변환
        const uiChapters: UIChapter[] = chaptersResponse.data.map((apiChapter: ApiChapter) => ({
          id: apiChapter.id,
          title: apiChapter.title,
          description: apiChapter.description || "설명이 없습니다.",
          lastStepIndex: apiChapter.status === "completed" ? 3 : 0, // 완료된 챕터는 3, 아니면 0
        }));
        
        setChapters(uiChapters);
        console.log("📚 UI용 챕터 데이터:", uiChapters);
      } catch (err) {
        console.error("📚 코스/챕터 데이터 로딩 실패:", err);
        setError("코스 또는 챕터 데이터를 불러오는데 실패했습니다.");
      } finally {
        setLoading(false);
      }
    };

    fetchCourseAndChapters();
  }, [courseId]);

  if (loading) {
    return (
      <Section title="로딩 중..." subtitle="챕터 데이터를 불러오고 있습니다.">
        <div className="text-center py-8">데이터를 로딩 중입니다...</div>
      </Section>
    );
  }

  if (error) {
    return (
      <Section title="오류 발생" subtitle={error}>
        <div className="text-center py-8 text-red-500">{error}</div>
      </Section>
    );
  }

  if (chapters.length === 0) {
    return (
      <Section 
        title={`사용자 ${courseId}의 학습 내역`} 
        subtitle="아직 생성된 챕터가 없습니다."
      >
        <div className="text-center py-8 space-y-4">
          <p>생성된 챕터가 없습니다. AI가 전체 커리큘럼을 설계하거나 개별 질문을 등록할 수 있습니다.</p>
          
          <div className="space-y-3">
            <button 
              onClick={handleCourseMaker}
              disabled={courseMakerLoading}
              className={`px-6 py-3 rounded-lg transition-colors block mx-auto text-white ${
                courseMakerLoading 
                  ? "bg-gray-400 cursor-not-allowed" 
                  : "bg-green-500 hover:bg-green-600"
              }`}
            >
              {courseMakerLoading ? "🔄 AI가 커리큘럼 생성 중..." : "🤖 AI가 전체 커리큘럼 설계하기"}
            </button>
            
            <p className="text-gray-500">또는</p>
            
            <button 
              onClick={() => {
                const question = prompt("궁금한 것을 질문해보세요! (예: 표준편차가 뭐야?)");
                if (question?.trim()) {
                  console.log("🤔 새 질문:", question);
                  alert(`"${question}" 질문으로 AI가 학습 자료를 생성합니다!\n(아직 API 연결 전 - 다음 단계에서 구현)`);
                }
              }}
              className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition-colors block mx-auto"
            >
              💭 개별 질문 등록하기
            </button>
          </div>
        </div>
      </Section>
    );
  }

  return (
    <Section
      subtitle={`사용자 ${courseId}님이 생성한 ${chapters.length}개의 학습 챕터입니다. 각 챕터를 클릭해서 학습을 진행해보세요.`}
      title={`학습 대시보드 (사용자 ID: ${courseId})`}
    >
      <div className="grid gap-4 lg:grid-cols-2">
        {chapters.map((chapter) => (
          <ChapterCard key={chapter.id} chapter={chapter} />
        ))}
      </div>
    </Section>
  );
};

export default CoursePage;
