import { Button } from "@heroui/react";
import { useNavigate } from "@tanstack/react-router";
import { useState } from "react";

import { callCourseMaker } from "../api";
import CreateCourseForm from "@/pages/create-course/ui/form.tsx";
import { ROUTE } from "@/shared/constants";
import { Section } from "@/shared/ui";

const CreateCoursePage = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    // DOM에서 폼 데이터 직접 수집 (임시 방법)
    const titleInput = document.querySelector('input[placeholder*="확률과 통계"]') as HTMLInputElement;
    const goalInput = document.querySelector('input[placeholder*="고1 확률"]') as HTMLInputElement;
    const promptTextarea = document.querySelector('textarea[placeholder*="확률 개념"]') as HTMLTextAreaElement;
    const requestTextarea = document.querySelector('textarea[placeholder*="30분 분량"]') as HTMLTextAreaElement;
    const linksTextarea = document.querySelector('textarea[placeholder*="https://blog"]') as HTMLTextAreaElement;
    const maxChaptersInput = document.querySelector('input[type="number"]') as HTMLInputElement;
    
    const courseTitle = titleInput?.value || "제목 없음";
    const courseDescription = goalInput?.value || "설명 없음";
    const prompt = promptTextarea?.value || "기본 학습자";
    const request = requestTextarea?.value || "";
    const linksText = linksTextarea?.value || "";
    const maxchapters = parseInt(maxChaptersInput?.value || "5") || 5;
    
    if (!courseTitle.trim() || courseTitle === "제목 없음") {
      alert("제목을 입력해주세요!");
      return;
    }

    // 링크 배열로 변환
    const links = linksText.trim() 
      ? linksText.split('\n').map(link => link.trim()).filter(link => link)
      : [];

    // 프롬프트와 요청사항 결합
    const fullPrompt = [prompt, request].filter(text => text.trim()).join('\n\n');

    const courseMakerData = {
      courseTitle: courseTitle.trim(),
      courseDescription: courseDescription.trim(),
      prompt: fullPrompt,
      maxchapters,
      link: links,
      difficulty: "medium"
    };

    try {
      setIsLoading(true);
      console.log("🚀 CourseMaker로 AI 강의 생성 시작:", courseMakerData);
      
      const response = await callCourseMaker(courseMakerData);
      console.log("✅ AI 강의 생성 성공:", response);
      
      alert(`"${courseMakerData.courseTitle}" AI 강의가 생성되었습니다!\n챕터 ${response.chapters?.length || 0}개가 포함되어 있습니다.`);
      navigate({ to: ROUTE.dashboard });
    } catch (error) {
      console.error("❌ AI 강의 생성 실패:", error);
      alert("AI 강의 생성에 실패했습니다. 로그인 상태를 확인하고 다시 시도해주세요.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Section subtitle="학습 계획 만들어보세요" title="학습 계획 만들기">
      <CreateCourseForm />
      <div className="mt-3 flex w-full justify-end">
        <Button
          className="max-sm:w-full"
          color="primary"
          isLoading={isLoading}
          onPress={handleSubmit}
        >
          생성
        </Button>
      </div>
    </Section>
  );
};

export default CreateCoursePage;
