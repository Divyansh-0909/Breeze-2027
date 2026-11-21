"use client";

import { useEffect, useRef, type KeyboardEvent, type RefObject } from "react";
import { mountContactForm } from "./contact-form.js";

export type ContactPlacement = "window" | "sheet" | null;

export function CypherContactDialog({ host, placement, canSend, onClose }: {
  host: RefObject<HTMLDivElement | null>;
  placement: ContactPlacement;
  canSend: boolean;
  onClose: () => void;
}) {
  const form = useRef<ReturnType<typeof mountContactForm> | null>(null);
  const visible = placement !== null;
  useEffect(() => {
    const element = host.current;
    if (!element) return;
    const mounted = mountContactForm(element, {
      onClose,
      submit: async fields => {
        if (!canSend) throw new Error("Sending is unavailable in this preview.");
        const response = await fetch("/api/preview-contact", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(fields),
        });
        const body = await response.json().catch(() => null);
        if (!response.ok || body?.success !== true) {
          throw new Error("Your message could not be saved. Your draft is still here.");
        }
        return body;
      },
    });
    if (!canSend) element.querySelector<HTMLButtonElement>(".send-message")!.disabled = true;
    form.current = mounted;
    return () => { form.current = null; mounted.dispose(); };
  }, [host, canSend, onClose]);
  useEffect(() => {
    if (visible) form.current?.focus();
  }, [visible]);

  function handleKeys(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key === "Escape") {
      event.preventDefault();
      onClose();
    }
    if (event.key !== "Tab") return;
    const controls = event.currentTarget.querySelectorAll<HTMLElement>("input, textarea, button:not(:disabled)");
    const first = controls[0], last = controls[controls.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last?.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first?.focus();
    }
  }

  return <>
    <div ref={host} className="native-form" role="dialog" aria-modal="true" aria-label="Contact enquiry"
      hidden={!visible} data-flat={placement === "sheet"} onKeyDown={handleKeys} />
    {visible && <p className="native-test-note">{canSend ? "Private test database" : "Private preview · sending is unavailable"}</p>}
  </>;
}
