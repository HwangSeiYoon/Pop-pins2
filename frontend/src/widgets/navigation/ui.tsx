import { Navbar, NavbarBrand, NavbarContent, NavbarItem } from "@heroui/react";
import { Link } from "@tanstack/react-router";

import { ROUTE } from "@/shared/constants";
import { sectionStyle } from "@/shared/styles";
import { ThemeSwitcher } from "@/shared/ui";

const Navigation = () => {
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
        <NavbarItem>
          <ThemeSwitcher />
        </NavbarItem>
      </NavbarContent>
    </Navbar>
  );
};

export default Navigation;
