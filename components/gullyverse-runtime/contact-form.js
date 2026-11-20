export function mountContactForm(host, { submit, onClose = () => {} } = {}) {
  const post =
    submit ??
    (async (data) => {
      const response = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok || body.success !== true)
        throw new Error("Your message could not be sent. Please try again.");
      return body;
    });
  host.innerHTML = `<form class="contact-enquiry-form"><div class="form-heading"><strong>Leave a message</strong><button class="close-form" type="button" aria-label="Close contact form">×</button></div><div class="identity-fields"><label>Name<input name="name" autocomplete="name" required minlength="2" maxlength="50" placeholder="Your name"></label><label>Email<input name="email" type="email" autocomplete="email" required maxlength="100" placeholder="you@example.com"></label><label>Phone<input name="phone" type="tel" autocomplete="tel" required minlength="10" maxlength="15" placeholder="+91 …"></label></div><label class="message-field">Message<textarea name="message" required minlength="10" maxlength="500" placeholder="Tell us how we can help…"></textarea></label><div class="form-bottom"><p class="form-status" role="status" aria-live="polite">Talk to the crew</p><button class="send-message" type="submit">Send message</button></div></form>`;
  const form = host.querySelector("form"),
    button = host.querySelector(".send-message"),
    status = host.querySelector(".form-status");
  let pending = false,
    disposed = false;
  host.querySelector(".close-form").addEventListener("click", onClose);
  form.addEventListener("input", () => {
    if (status.dataset.state === "success") {
      status.textContent = "Talk to the crew";
      status.dataset.state = "ready";
    }
  });
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (pending || !form.reportValidity()) return;
    pending = true;
    button.disabled = true;
    button.textContent = "Sending…";
    status.textContent = "Sending your message…";
    status.dataset.state = "pending";
    const data = Object.fromEntries(new FormData(form));
    try {
      await post(data);
      if (disposed) return;
      form.reset();
      status.textContent = "Message received. We’ll get back to you.";
      status.dataset.state = "success";
    } catch (error) {
      if (disposed) return;
      status.textContent =
        error?.message || "Please try again. Your message is still here.";
      status.dataset.state = "error";
    } finally {
      pending = false;
      if (!disposed) {
        button.disabled = false;
        button.textContent = "Send message";
      }
    }
  });
  return {
    focus: () => host.querySelector("input").focus(),
    dispose() {
      disposed = true;
      host.replaceChildren();
    },
  };
}
