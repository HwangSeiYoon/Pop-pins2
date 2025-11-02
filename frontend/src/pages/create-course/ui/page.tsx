import { ModalBody, ModalHeader } from "@heroui/react";

import CreateCourseForm from "@/pages/create-course/ui/form.tsx";
import { ModalButton, Section } from "@/shared/ui";

const CreateCoursePage = () => {
  return (
    <Section subtitle="학습 계획 만들어보세요" title="학습 계획 만들기">
      <CreateCourseForm />
      <div className="mt-3 flex w-full justify-end">
        <ModalButton
          className="max-sm:w-full"
          color="primary"
          modalContent={(onClose) => (
            <>
              <ModalHeader />
              <ModalBody>테스트</ModalBody>
            </>
          )}
        >
          생성
        </ModalButton>
      </div>
    </Section>
  );
};

export default CreateCoursePage;
