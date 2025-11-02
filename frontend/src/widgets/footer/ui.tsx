import { tv } from "@heroui/react";
import { Link } from "@tanstack/react-router";

import { ROUTE } from "@/shared/constants";
import { sectionStyle } from "@/shared/styles";

const footerLinks = {
  product: [
    { label: "기능 소개", href: "#features" },
    { label: "작동 방식", href: "#how-it-works" },
    { label: "요금제", href: "#pricing" },
  ],
  company: [
    { label: "회사 소개", href: "#about" },
    { label: "블로그", href: "#blog" },
    { label: "채용", href: "#careers" },
  ],
  legal: [
    { label: "이용약관", href: "#terms" },
    { label: "개인정보처리방침", href: "#privacy" },
    { label: "고객센터", href: "#support" },
  ],
};
const footerStyle = tv({
  slots: {
    root: "border-zinc-800 bg-zinc-900",
    container: sectionStyle({ class: "py-8 md:py-12" }),
    grid: "grid gap-6 md:grid-cols-4 md:gap-8",
    brandSection: "md:col-span-1",
    brand: "text-primary text-lg font-extrabold tracking-tight md:text-xl",
    description: "mt-4 text-sm text-zinc-400",
    heading: [
      "mb-4 text-sm font-semibold text-zinc-100",
      "border-zinc-800 max-md:border-t max-md:pt-6",
    ],
    linkList: "space-y-2",
    link: "hover:text-primary text-sm text-zinc-400 transition-colors",
    bottomSection:
      "mt-6 flex flex-col items-center justify-between gap-4 border-t border-zinc-800 pt-8 md:mt-8 md:flex-row",
    copyright: "text-sm text-zinc-400",
    bottomLinks: "flex gap-4",
  },
});

const Footer = () => {
  const styles = footerStyle();

  return (
    <footer className={styles.root()}>
      <div className={styles.container()}>
        <div className={styles.grid()}>
          {/* Brand Section */}
          <div className={styles.brandSection()}>
            <Link to="/">
              <span className={styles.brand()}>POPPINS</span>
            </Link>
            <p className={styles.description()}>
              AI 기반 맞춤형 학습 플랫폼으로
              <br />더 스마트하게 학습하세요
            </p>
          </div>

          {/* Links Sections */}
          <div>
            <h3 className={styles.heading()}>제품</h3>
            <ul className={styles.linkList()}>
              {footerLinks.product.map((link) => (
                <li key={link.label}>
                  <a className={styles.link()} href={link.href}>
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className={styles.heading()}>회사</h3>
            <ul className={styles.linkList()}>
              {footerLinks.company.map((link) => (
                <li key={link.label}>
                  <a className={styles.link()} href={link.href}>
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className={styles.heading()}>법적 고지</h3>
            <ul className={styles.linkList()}>
              {footerLinks.legal.map((link) => (
                <li key={link.label}>
                  <a className={styles.link()} href={link.href}>
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Section */}
        <div className={styles.bottomSection()}>
          <p className={styles.copyright()}>
            © 2025 POPPINS. All rights reserved.
          </p>
          <div className={styles.bottomLinks()}>
            <Link className={styles.link()} to={ROUTE.login}>
              로그인
            </Link>
            <Link className={styles.link()} to={ROUTE.signup}>
              회원가입
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
