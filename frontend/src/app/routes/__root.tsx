import { HeroUIProvider } from "@heroui/react";
import { Outlet, createRootRoute } from "@tanstack/react-router";
import { ThemeProvider } from "next-themes";

import Navigation from "@/widgets/navigation";

export const Route = createRootRoute({
  component: () => (
    <HeroUIProvider>
      <ThemeProvider attribute="class">
        <Navigation />
        <Outlet />
      </ThemeProvider>
    </HeroUIProvider>
  ),
});
