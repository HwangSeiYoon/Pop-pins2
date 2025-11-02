import { sectionStyle } from "../styles";

interface Props {
  title?: string;
  subtitle?: string;
  children?: React.ReactNode;
}

export const Section = ({ title, subtitle, children }: Props) => (
  <section className={sectionStyle({ class: "py-12 md:py-16" })}>
    {title && (
      <div className="mb-8">
        <h2 className="text-foreground-800 text-2xl font-bold tracking-tight md:text-4xl">
          {title}
        </h2>
        {subtitle && (
          <p className="text-foreground-400 mt-2 text-base md:text-lg">
            {subtitle}
          </p>
        )}
      </div>
    )}
    {children}
  </section>
);
