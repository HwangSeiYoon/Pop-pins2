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
      const {
        status,
        data: { token },
      } = await login(data);

      if (status === 200 && token) {
        setToken(token);
        navigate({ to: ROUTE.dashboard, replace: true });
      }
    } catch (error) {
      console.debug(error);
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
