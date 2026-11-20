export function mountContactForm(
  host: HTMLElement,
  options?: {
    submit?: (data: Record<string, FormDataEntryValue>) => Promise<unknown>;
    onClose?: () => void;
  },
): { focus: () => void; dispose: () => void };
