import { Button, type ButtonProps, tv } from "@heroui/react";
import { MoonIcon, SunIcon } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

const buttonProps = {
  isIconOnly: true,
  size: "sm",
  radius: "full",
  variant: "bordered",
} satisfies ButtonProps;

const style = tv({
  slots: {
    icon: "text-content4 size-5",
  },
});

export function ThemeSwitcher() {
  const [mounted, setMounted] = useState(false);
  const { theme, setTheme } = useTheme();
  const styles = style();

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <Button {...buttonProps} disabled>
        <SunIcon className={styles.icon()} />
      </Button>
    );
  }

  if (theme === "dark") {
    return (
      <Button {...buttonProps} onPress={() => setTheme("light")}>
        <SunIcon className={styles.icon()} />
      </Button>
    );
  }

  return (
    <Button {...buttonProps} onPress={() => setTheme("dark")}>
      <MoonIcon className={styles.icon()} />
    </Button>
  );
}
