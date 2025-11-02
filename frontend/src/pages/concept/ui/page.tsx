import { Button } from "@heroui/react";
import { Link } from "@tanstack/react-router";
import { ArrowLeftIcon } from "lucide-react";
import type { ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { Card, Section } from "@/shared/ui";

// 방법 1: 로컬 MD 파일에서 불러오기 (현재 사용 중)
import rawMarkdownContent from "./test.md?raw";

// 방법 2: API에서 string으로 받기
// import { useEffect, useState } from "react";
// const [markdownContent, setMarkdownContent] = useState<string>("");
// useEffect(() => {
//   const fetchConcept = async () => {
//     const response = await fetch(
//       `/api/courses/${courseId}/chapters/${chapterId}/concept`
//     );
//     const data = await response.json();
//     // API 응답 예시: { content: "# 제목\n\n본문..." } 또는 단순히 string
//     setMarkdownContent(data.content || data);
//   };
//   fetchConcept();
// }, [courseId, chapterId]);

// 방법 3: API에서 파일 URL을 받아서 파일 내용을 가져오기
// import { useEffect, useState } from "react";
// const [markdownContent, setMarkdownContent] = useState<string>("");
// useEffect(() => {
//   const fetchConcept = async () => {
//     // 1단계: API에서 파일 URL 받기
//     const response = await fetch(
//       `/api/courses/${courseId}/chapters/${chapterId}/concept`
//     );
//     const data = await response.json();
//     // API 응답 예시: { fileUrl: "https://example.com/concept.md" } 또는 { filePath: "/concepts/chapter1.md" }
//     const fileUrl = data.fileUrl || data.filePath;
//
//     // 2단계: 파일 URL로 마크다운 파일 내용 가져오기
//     const fileResponse = await fetch(fileUrl);
//     const fileContent = await fileResponse.text(); // .text()로 string으로 받음
//     setMarkdownContent(fileContent);
//   };
//   fetchConcept();
// }, [courseId, chapterId]);

// 이스케이프된 \n을 실제 개행 문자로 변환 (로컬 파일의 경우)
const markdownContent = rawMarkdownContent.replace(/\\n/g, "\n");

// API로 받는 경우는 이미 실제 개행 문자로 되어 있으므로 변환 불필요
// 다만 API에서 이스케이프된 형태로 오는 경우에만 .replace(/\\n/g, "\n") 필요

const ConceptPage = () => {
  return (
    <Section subtitle="개념을 학습하고 이해하세요" title="개념 정리">
      <Card className="p-8">
        <div className="markdown-content text-foreground">
          <ReactMarkdown
            className="space-y-4"
            components={{
              h1: ({ children }: { children?: ReactNode }) => (
                <h1 className="mb-4 text-3xl font-bold">{children}</h1>
              ),
              h2: ({ children }: { children?: ReactNode }) => (
                <h2 className="mt-6 mb-3 text-2xl font-semibold">{children}</h2>
              ),
              h3: ({ children }: { children?: ReactNode }) => (
                <h3 className="mt-4 mb-2 text-xl font-semibold">{children}</h3>
              ),
              p: ({ children }: { children?: ReactNode }) => (
                <p className="mb-4 leading-7">{children}</p>
              ),
              ul: ({ children }: { children?: ReactNode }) => (
                <ul className="mb-4 ml-6 list-disc space-y-2">{children}</ul>
              ),
              ol: ({ children }: { children?: ReactNode }) => (
                <ol className="mb-4 ml-6 list-decimal space-y-2">{children}</ol>
              ),
              li: ({ children }: { children?: ReactNode }) => (
                <li className="leading-7">{children}</li>
              ),
              code: ({
                children,
                className,
              }: {
                children?: ReactNode;
                className?: string;
              }) => {
                const isInline = !className;
                return isInline ? (
                  <code className="bg-default-100 text-primary rounded px-1.5 py-0.5 text-sm">
                    {children}
                  </code>
                ) : (
                  <code className={className}>{children}</code>
                );
              },
              pre: ({ children }: { children?: ReactNode }) => (
                <pre className="bg-default-100 mb-4 overflow-x-auto rounded-lg p-4">
                  {children}
                </pre>
              ),
              blockquote: ({ children }: { children?: ReactNode }) => (
                <blockquote className="border-primary bg-default-50 mb-4 border-l-4 pl-4 italic">
                  {children}
                </blockquote>
              ),
              table: ({ children }: { children?: ReactNode }) => (
                <div className="mb-4 overflow-x-auto">
                  <table className="border-default-300 w-full border-collapse border">
                    {children}
                  </table>
                </div>
              ),
              th: ({ children }: { children?: ReactNode }) => (
                <th className="bg-default-100 border-default-300 border px-4 py-2 text-left font-semibold">
                  {children}
                </th>
              ),
              td: ({ children }: { children?: ReactNode }) => (
                <td className="border-default-300 border px-4 py-2">
                  {children}
                </td>
              ),
              a: ({
                children,
                href,
              }: {
                children?: ReactNode;
                href?: string;
              }) => (
                <a
                  className="text-primary hover:underline"
                  href={href}
                  rel="noopener noreferrer"
                  target="_blank"
                >
                  {children}
                </a>
              ),
            }}
            remarkPlugins={[remarkGfm]}
          >
            {markdownContent}
          </ReactMarkdown>
        </div>
      </Card>
      <div className="mt-6 flex justify-between">
        <Button
          as={Link}
          startContent={<ArrowLeftIcon className="h-4 w-4" />}
          variant="light"
        >
          뒤로 가기
        </Button>
        <Button color="primary">학습 완료</Button>
      </div>
    </Section>
  );
};

export default ConceptPage;
