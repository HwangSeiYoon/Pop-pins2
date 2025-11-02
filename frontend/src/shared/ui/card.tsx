import { type CardProps, Card as HeroUICard } from "@heroui/react";

import { cn } from "@/shared/lib";

export const Card = ({ className, ...props }: Omit<CardProps, "shadow">) => {
  return (
    <HeroUICard
      className={cn(
        "border-default-200/80 border shadow-sm backdrop-blur transition-all hover:shadow-md",
        className,
      )}
      shadow="none"
      {...props}
    />
  );
};
