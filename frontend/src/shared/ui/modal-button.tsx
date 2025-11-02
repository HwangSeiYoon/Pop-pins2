import {
  Button,
  type ButtonProps,
  Modal,
  ModalContent,
  type ModalContentProps,
  useDisclosure,
} from "@heroui/react";

export const ModalButton = ({
  modalContent,
  ...props
}: Omit<ButtonProps, "onPress" | "onClick"> & {
  modalContent: ModalContentProps["children"];
}) => {
  const { isOpen, onOpen, onOpenChange } = useDisclosure();

  return (
    <>
      <Button {...props} onPress={onOpen} />
      <Modal isOpen={isOpen} onOpenChange={onOpenChange}>
        <ModalContent>{modalContent}</ModalContent>
      </Modal>
    </>
  );
};
