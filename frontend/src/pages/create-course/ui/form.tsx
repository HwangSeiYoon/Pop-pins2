import {
  DatePicker,
  Input,
  NumberInput,
  Radio,
  RadioGroup,
  Textarea,
  tv,
} from "@heroui/react";

import { Card } from "@/shared/ui";

const style = tv({
  slots: {
    card: [
      "desktop:py-6 desktop:px-5 gap-6 transition-none",
      "max-desktop:border-0 max-desktop:shadow-none max-desktop:hover:shadow-none max-desktop:bg-transparent max-desktop:rounded-none",
    ],
    label: "text-foreground text-small font-semibold",
    radio: "w-full",
    radioWrapper: "flex items-center gap-3",
    inputWrapper: "border px-4 shadow-xs",
  },
});

const styleProps = {
  classNames: {
    label: style.slots.label,
    inputWrapper: style.slots.inputWrapper,
    segment: "mx-1",
  },
  labelPlacement: "outside",
  variant: "bordered",
  isRequired: true,
} as const;

const textAreaProp = {
  ...styleProps,
  disableAutosize: true,
  isRequired: false,
  classNames: {
    label: style.slots.label,
    inputWrapper: style().inputWrapper({ class: "pb-3 pr-3 pt-2.5" }),
    input: "resize-y min-h-16",
  },
};

const CreateCourseForm = () => {
  const styles = style();

  return (
    <div className="desktop:grid desktop:gap-4 flex grid-cols-2 flex-col gap-6">
      <Card className={styles.card()}>
        <Input
          {...styleProps}
          label="제목"
          labelPlacement="outside-top"
          placeholder="예) 확률과 통계 2주 완성"
        />
        <Input
          {...styleProps}
          label="학습 목표/주제"
          labelPlacement="outside-top"
          placeholder="예) 고1 확률과 통계 중간고사 대비"
        />
        <div className="flex flex-col gap-6 sm:flex-row sm:gap-3">
          <DatePicker {...styleProps} label="시작일" />
          <DatePicker {...styleProps} label="종료일" />
        </div>
        <RadioGroup
          isRequired
          classNames={{
            label: styles.label(),
          }}
          label="최대 학습 과정 갯수"
        >
          <div
            className={styles.radioWrapper({
              className: "sm:max-desktop:w-1/2 max-desktop:pr-1.5 gap-4",
            })}
          >
            <Radio className={styles.radio()} size="sm" value="0">
              AI에게 맡기기
            </Radio>
            <div className={styles.radioWrapper()}>
              <Radio className={styles.radio()} size="sm" value="0">
                직접 설정
              </Radio>
              <NumberInput {...styleProps} />
            </div>
          </div>
        </RadioGroup>
      </Card>
      <Card className={styles.card()}>
        <Textarea
          {...textAreaProp}
          description="최대한 자세히 입력해주세요"
          label="현재 학습 상황"
          placeholder="예) 확률 개념은 익순하나 분산/표준편차 계산에서 실수가 많음"
        />
        <Textarea
          {...textAreaProp}
          label="요청 사항"
          placeholder="예) 매일 30분 분량으로 쪼개 주세요"
        />
        <Textarea
          {...textAreaProp}
          description="줄바꿈으로 여러 개 입력 가능"
          label="참고 링크"
          placeholder="예) https://blog.example.com/prob-basics"
        />
      </Card>
    </div>
  );
};

export default CreateCourseForm;
