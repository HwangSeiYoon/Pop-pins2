import { Button, Form } from "@heroui/react";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useNavigate } from "@tanstack/react-router";
import { useSetAtom } from "jotai";
import { useForm } from "react-hook-form";

import { ROUTE } from "@/shared/constants";
import { tokenAtom } from "@/shared/store";
import { formStyle } from "@/shared/styles";
import { HookFormInput, Section } from "@/shared/ui";

import { login } from "../api";
import { loginSchema } from "../model/schema";
import type { LoginFormData } from "../model/types";

const LoginPage = () => {
  const navigate = useNavigate();
  const setToken = useSetAtom(tokenAtom);

  const {
    control,
    handleSubmit,
    formState: { isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      console.log("🔐 로그인 시도 데이터:", data);
      console.log("🔐 API 기본 URL:", import.meta.env.VITE_API_BASE_URL);
      
      const response = await login(data);
      console.log("🔐 로그인 응답:", response);
      
      if (response.status === 200 && response.data) {
        console.log("✅ 로그인 성공!");
        
        // 백엔드 응답 구조에 따라 토큰 추출
        const token = response.data.access_token;
        if (token) {
          setToken(token);
          navigate({ to: ROUTE.dashboard, replace: true });
        } else {
          console.error("❌ 토큰이 응답에 없습니다:", response.data);
        }
      } else {
        console.log("❌ 로그인 실패:", response.status);
      }
    } catch (error) {
      console.error("🚨 로그인 오류:", error);
    }
  };

  const styles = formStyle();

  return (
    <Section>
      <div className={styles.wrapper()}>
        <div className="flex flex-col gap-2 text-center">
          <h1 className={styles.title()}>로그인</h1>
          <p className="text-default-500 text-sm">
            계정에 로그인하여 학습을 시작하세요
          </p>
        </div>

        <Form className={styles.form()} onSubmit={handleSubmit(onSubmit)}>
          <HookFormInput
            control={control}
            label="이메일"
            name="email"
            type="email"
          />

          <HookFormInput
            control={control}
            label="비밀번호"
            name="password"
            type="password"
          />

          <Button
            className="w-full"
            color="primary"
            isLoading={isSubmitting}
            type="submit"
          >
            로그인
          </Button>
        </Form>

        <div className="text-center text-sm">
          <p className="text-default-500">
            계정이 없으신가요?{" "}
            <Link className="text-primary hover:underline" to={ROUTE.signup}>
              회원가입
            </Link>
          </p>
        </div>
      </div>
    </Section>
  );
};

export default LoginPage;
