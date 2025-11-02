import { Navbar, NavbarBrand, NavbarContent, NavbarItem } from "@heroui/react";
import { Link, useLocation } from "@tanstack/react-router";

import { ROUTE } from "@/shared/constants";
import { sectionStyle } from "@/shared/styles";
import { ThemeSwitcher } from "@/shared/ui";

const Navigation = () => {
  const location = useLocation();
  const currentPath = location.pathname;

  // 랜딩, 로그인, 회원가입 페이지에서만 로그인/회원가입 메뉴 표시
  const showAuthMenu =
    currentPath === "/" ||
    currentPath === ROUTE.login ||
    currentPath === ROUTE.signup;

  return (
    <Navbar
      classNames={{
        wrapper: sectionStyle(),
      }}
    >
      <NavbarBrand>
        <Link to="/">
          <span className="text-primary text-lg font-extrabold tracking-tight md:text-xl">
            POPPINS
          </span>
        </Link>
      </NavbarBrand>
      <NavbarContent justify="end">
        {showAuthMenu && (
          <>
            <NavbarItem>
              <Link
                className="text-default-600 hover:text-foreground text-sm transition-colors"
                to={ROUTE.login}
              >
                로그인
              </Link>
            </NavbarItem>
            <NavbarItem>
              <Link
                className="text-primary hover:text-primary-600 text-sm font-medium transition-colors"
                to={ROUTE.signup}
              >
                회원가입
              </Link>
            </NavbarItem>
          </>
        )}
        {!showAuthMenu && (
          <NavbarItem>
            <Link
              className="text-default-600 hover:text-foreground text-sm transition-colors"
              to={ROUTE.dashboard}
            >
              대시보드
            </Link>
          </NavbarItem>
        )}
        <NavbarItem>
          <ThemeSwitcher />
        </NavbarItem>
      </NavbarContent>
    </Navbar>
  );
};

export default Navigation;
