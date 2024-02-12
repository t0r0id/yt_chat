import { create } from "zustand";

interface useSearchCardStore {
  isOpen: boolean;
  onOpen: () => void;
  onClose: () => void;
}

export const useSearchCard = create<useSearchCardStore>((set) => ({
  isOpen: false,
  onOpen: () => set({ isOpen: true }),
  onClose: () => set({ isOpen: false }),
}));
