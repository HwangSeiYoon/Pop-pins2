import { Input, type InputProps } from "@heroui/react";
import type {
  Control,
  FieldPath,
  FieldValues,
  RegisterOptions,
} from "react-hook-form";
import { useController } from "react-hook-form";

type HookFormInputProps<T extends FieldValues> = Omit<
  InputProps,
  "value" | "onChange" | "onBlur" | "ref"
> & {
  name: FieldPath<T>;
  control: Control<T>;
  rules?: RegisterOptions<T, FieldPath<T>>;
};

export const HookFormInput = <T extends FieldValues>({
  name,
  control,
  rules,
  ...inputProps
}: HookFormInputProps<T>) => {
  const {
    field,
    fieldState: { error, invalid },
  } = useController({
    name,
    control,
    rules,
  });

  return (
    <Input
      {...field}
      {...inputProps}
      errorMessage={error?.message}
      isInvalid={invalid}
      value={field.value ?? ""}
      variant="bordered"
    />
  );
};
