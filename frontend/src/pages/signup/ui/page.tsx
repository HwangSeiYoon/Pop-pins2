import { Button, Form } from "@heroui/react";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useNavigate } from "@tanstack/react-router";
import { useForm } from "react-hook-form";

import { ROUTE } from "@/shared/constants";
import { formStyle } from "@/shared/styles";
import { HookFormInput, Section } from "@/shared/ui";

import { signup } from "../api";
import { signupSchema } from "../model/schema";
import type { SignupFormData } from "../model/types";

const SignupPage = () => {
  const navigate = useNavigate();

  const {
    control,
    handleSubmit,
    formState: { isSubmitting, isValid },
  } = useForm<SignupFormData>({
    resolver: zodResolver(signupSchema),
    mode: "onBlur",
    defaultValues: {
      name: "",
      email: "",
      password: "",
    },
  });

  const onSubmit = async (data: SignupFormData) => {
    try {
      const { status } = await signup(data);
      if (status === 200) {
        navigate({ to: ROUTE.login, replace: true });
      }
    } catch (error) {
      console.debug(error);
    }
  };

  const styles = formStyle();

  return (
    <Section>
      <div className={styles.wrapper()}>
        <div className="text-center">
          <h1 className={styles.title()}>회원가입</h1>
          <p className="text-default-500 mt-2 text-sm">
            새 계정을 만들어 학습을 시작하세요
          </p>
        </div>

        <Form className={styles.form()} onSubmit={handleSubmit(onSubmit)}>
          <HookFormInput
            isRequired
            control={control}
            label="이름"
            name="name"
            type="text"
          />

          <HookFormInput
            isRequired
            control={control}
            label="이메일"
            name="email"
            type="email"
          />

          <HookFormInput
            isRequired
            control={control}
            description="8자 이상 20자 이하의 비밀번호를 입력해주세요"
            label="비밀번호"
            name="password"
            type="password"
          />

          <Button
            className="w-full"
            color="primary"
            isDisabled={!isValid}
            isLoading={isSubmitting}
            type="submit"
          >
            회원가입
          </Button>
        </Form>

        <div className="text-center text-sm">
          <p className="text-default-500">
            이미 계정이 있으신가요?{" "}
            <Link className="text-primary hover:underline" to={ROUTE.login}>
              로그인
            </Link>
          </p>
        </div>
      </div>
    </Section>
  );
};

export default SignupPage;
