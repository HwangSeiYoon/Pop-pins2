import { type TextAreaProps, Textarea } from "@heroui/react";
import type {
  Control,
  FieldPath,
  FieldValues,
  RegisterOptions,
} from "react-hook-form";
import { useController } from "react-hook-form";

export const HookFormTextarea = <T extends FieldValues>({
  name,
  control,
  rules,
  ...props
}: Omit<TextAreaProps, "value" | "onChange" | "onBlur" | "ref"> & {
  name: FieldPath<T>;
  control: Control<T>;
  rules?: RegisterOptions<T, FieldPath<T>>;
}) => {
  const {
    field,
    fieldState: { error, invalid },
  } = useController({
    name,
    control,
    rules,
  });

  return (
    <Textarea
      disableAutosize
      variant="bordered"
      {...props}
      {...field}
      classNames={{
        inputWrapper: "border p-3 pt-2.5 pl-4 shadow-xs",
        input: "resize-y min-h-16 ",
      }}
      errorMessage={error?.message}
      isInvalid={invalid}
      value={field.value ?? ""}
    />
  );
};
