"use client";

import { useEffect, useState } from "react";
import QRCode from "qrcode";
import Link from "next/link";
import Image from "next/image";

export type CheckoutProps = {
  token: string; amount: string; reference: string | null; prepared: boolean;
  paymentUrl?: string | null; payeeName?: string | null; upiId?: string | null;
  initialStatus?: string; noteVerified?: boolean; preview?: boolean;
};

const inputClass = "w-full rounded-xl border border-white/20 bg-black/25 px-4 py-3 text-white outline-none focus:border-[#ffbc00]";
const buttonClass = "rounded-xl bg-[#ffbc00] px-5 py-3 font-semibold text-[#31004b] disabled:opacity-50";
const labels: Record<string, string> = {
  AWAITING_PAYMENT: "Awaiting payment", AWAITING_STATEMENT: "Awaiting bank verification",
  NEEDS_REVIEW: "The team is reviewing your payment", APPROVED: "Payment verified — registration confirmed",
  APPROVED_REVIEW_REQUIRED: "The team is checking a bank update", REJECTED: "Please contact the team about this order",
};

export function CheckoutForm(props: CheckoutProps) {
  const [ready, setReady] = useState(false);
  const [prepared, setPrepared] = useState(props.prepared);
  const [paymentUrl, setPaymentUrl] = useState(props.paymentUrl || "");
  const [status, setStatus] = useState(props.initialStatus || "AWAITING_PAYMENT");
  const [reference, setReference] = useState(props.reference || "");
  const [qr, setQr] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [bankReference, setBankReference] = useState("");
  const [proof, setProof] = useState<File | null>(null);
  const [readingProof, setReadingProof] = useState(false);
  useEffect(() => { setReady(true); }, []);

  useEffect(() => {
    if (!prepared || !paymentUrl) return;
    let alive = true;
    QRCode.toDataURL(props.preview ? "https://example.invalid/breeze-preview" : paymentUrl, { width: 300, margin: 3, errorCorrectionLevel: "M" })
      .then(url => { if (alive) setQr(url); }).catch(() => { if (alive) setError("QR could not be displayed. Refresh the page or contact the team."); });
    return () => { alive = false; };
  }, [prepared, paymentUrl, props.preview]);

  useEffect(() => {
    if (!prepared || props.preview) return;
    const controller = new AbortController();
    const refresh = async () => {
      if (document.visibilityState === "hidden") return;
      try {
        const response = await fetch(`/api/payments/status?token=${props.token}`, { cache: "no-store", signal: controller.signal });
        if (response.ok) setStatus((await response.json()).paymentStatus);
      } catch { /* Status remains pending during a temporary network failure. */ }
    };
    void refresh();
    const timer = window.setInterval(refresh, 15000);
    return () => { controller.abort(); window.clearInterval(timer); };
  }, [prepared, props.token, props.preview]);

  async function saveDetails(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError("");
    const form = new FormData(event.currentTarget);
    form.set("token", props.token); form.set("stage", "prepare");
    try {
      if (props.preview) {
        setPrepared(true); setPaymentUrl("upi://pay?pa=demo@invalid");
        setReference("BZ27ABCDEFGHJK"); setNotice("Preview: details saved locally. No order or payment has been created."); return;
      }
      const response = await fetch("/api/pay", { method: "POST", body: form });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Your details could not be saved.");
      setPrepared(true); setPaymentUrl(data.paymentUrl || ""); setReference(data.reference || "");
      setNotice("Your details are saved. You can return to this checkout link if you close the page.");
    } catch (error) { setError(error instanceof Error ? error.message : "Please try again."); }
    finally { setBusy(false); }
  }

  async function readReceipt(file: File | null) {
    setProof(file); setError("");
    if (!file || props.preview) return;
    if (file.size > 5 * 1024 * 1024 || !["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
      setProof(null); setError("Choose a JPEG, PNG, or WebP receipt no larger than 5 MB."); return;
    }
    setReadingProof(true);
    try {
      const form = new FormData(); form.set("token", props.token); form.set("file", file);
      const response = await fetch("/api/payments/proof-preview", { method: "POST", body: form });
      const data = await response.json();
      if (response.ok && data.reference) { setBankReference(data.reference); setNotice("A bank reference was read from your receipt. Check the digits before submitting."); }
      else setNotice("We could not read a single bank reference. You can enter it yourself or submit the receipt for team review.");
    } catch { setNotice("Receipt reading is temporarily unavailable. You can still submit the image."); }
    finally { setReadingProof(false); }
  }

  async function reportPayment(event: React.FormEvent) {
    event.preventDefault(); setBusy(true); setError("");
    try {
      if (props.preview) { setStatus("AWAITING_STATEMENT"); setNotice("Preview: awaiting the receiving account's bank statement."); return; }
      const form = new FormData(); form.set("token", props.token); form.set("stage", "paid");
      if (bankReference.trim()) form.set("bankReference", bankReference);
      if (proof) form.set("proofImage", proof);
      const response = await fetch("/api/pay", { method: "POST", body: form });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Payment details could not be submitted.");
      setStatus(data.approved ? "APPROVED" : "AWAITING_STATEMENT");
      localStorage.removeItem("cart");
      setNotice("Payment details received. We will confirm after checking the receiving bank statement.");
    } catch (error) { setError(error instanceof Error ? error.message : "Please try again."); }
    finally { setBusy(false); }
  }

  const approved = status === "APPROVED" || status === "APPROVED_REVIEW_REQUIRED", rejected = status === "REJECTED";
  return (
    <section className="mx-auto max-w-2xl px-5 py-12 text-white">
      {props.preview && <p className="mb-6 rounded-xl border border-amber-300 p-4 text-amber-200">Preview only. Use sample details; no data is sent to the server. The QR cannot receive payments.</p>}
      <p className="text-sm uppercase tracking-[0.25em] text-[#ffbc00]">Breeze 2027 · Checkout</p>
      <h1 className="mt-3 text-3xl sm:text-4xl">Save your place. Make it official.</h1>
      <ol className="my-7 flex gap-5 text-sm" aria-label="Checkout progress">
        <li className={!prepared ? "text-[#ffbc00]" : "text-white/60"}>1. Your details</li>
        <li className={prepared && !approved ? "text-[#ffbc00]" : "text-white/60"}>2. UPI payment</li>
        <li className={approved ? "text-[#ffbc00]" : "text-white/60"}>3. Confirmation</li>
      </ol>
      <div className="rounded-2xl border border-white/15 bg-white/5 p-5 sm:p-8">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
          <p className="text-white/70">{prepared ? "Amount to pay" : "Order total"}</p>
          <strong className="text-3xl text-[#ffbc00]">₹{Number(props.amount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}</strong>
        </div>
        {error && <p role="alert" className="mb-5 rounded-lg border border-red-400/40 bg-red-900/20 p-3 text-red-200">{error}</p>}
        {notice && <p role="status" className="mb-5 rounded-lg bg-white/10 p-3 text-sm">{notice}</p>}
        {!prepared ? (
          <form onSubmit={saveDetails} className="space-y-4">
            {[
              ["name", "Full name", "text", "Your full name", "name"],
              ["email", "Email for confirmation", "email", "you@example.com", "email"],
              ["phone", "Phone number", "tel", "Your phone number", "tel"],
              ["rollNumber", "College roll number", "text", "Your roll number", "off"],
              ["college_status", "College and graduation year", "text", "Shiv Nadar University, 2027", "off"],
            ].map(([name, label, type, placeholder, autoComplete]) => (
              <label key={name} className="block text-sm"><span className="mb-2 block">{label}</span><input className={inputClass} name={name} type={type} placeholder={placeholder} autoComplete={autoComplete} required maxLength={name === "college_status" ? 200 : 254} /></label>
            ))}
            <p className="text-sm text-white/60">We save your order before payment so you can return using this checkout link.</p>
            <button className={buttonClass + " w-full"} disabled={busy || !ready}>{busy ? "Saving your order…" : Number(props.amount) === 0 ? "Confirm free registration" : "Save details and show payment QR"}</button>
          </form>
        ) : (
          <>
            <div className="mb-5 rounded-xl bg-black/20 p-4">
              <p className="text-sm text-white/60">Your order reference</p><p className="mt-1 break-all font-mono text-xl tracking-wider">{reference || "Legacy order"}</p>
              <p className="mt-3 text-sm" role="status">{labels[status] || "Awaiting verification"}</p>
            </div>
            {approved ? <div><p className="mb-5">{status === "APPROVED_REVIEW_REQUIRED" ? "The team is checking a bank update. Please do not pay again; contact the team if you need help." : "Your registration is confirmed. Keep your receipt for entry."}</p>{!props.preview && <Link className={buttonClass + " inline-block"} href={`/reciept/${props.token}`}>View receipt</Link>}</div> : rejected ? <p>Please contact the Breeze team before making another payment.</p> : paymentUrl ? (
              <>
                <p className="text-center text-sm text-white/70">Pay to <strong className="text-white">{props.payeeName || "Sample recipient"}</strong></p>
                <p className="mb-4 break-all text-center text-sm">{props.upiId || "demo@invalid"}</p>
                {qr && <Image src={qr} alt={props.preview ? "Non-payment preview QR" : "UPI QR for this order"} width={300} height={300} unoptimized className="mx-auto rounded-xl bg-white" />}
                <p className="mt-4 text-center text-sm text-white/70">Check the recipient and amount in your UPI app. Keep the note <strong className="text-white">BREEZE {reference}</strong>.</p>
                {!props.preview && <a href={paymentUrl} className="mt-5 block rounded-xl border border-[#ffbc00] px-5 py-3 text-center text-[#ffbc00]">Open UPI app on this phone</a>}
                <form onSubmit={reportPayment} className="mt-7 space-y-4">
                  <details className="rounded-xl border border-white/15 p-4" open={!props.noteVerified}>
                    <summary className="cursor-pointer font-medium">Add a bank reference or receipt</summary>
                    <p className="my-3 text-sm text-white/60">{props.noteVerified ? "Optional if your bank preserves the order note. These details help if it is missing." : "This account's order-note support is still being checked. Add your UTR or receipt to help verify payment."}</p>
                    <label className="block text-sm">UPI reference / UTR / RRN<input className={inputClass + " mt-2"} value={bankReference} onChange={event => setBankReference(event.target.value)} placeholder="Complete bank reference, not the Breeze order code" maxLength={50} /></label>
                    <label className="mt-4 block text-sm">Payment receipt (JPEG, PNG, WebP · up to 5 MB)<input className="mt-2 block w-full text-sm" type="file" accept="image/jpeg,image/png,image/webp" onChange={event => void readReceipt(event.target.files?.[0] || null)} /></label>
                    {readingProof && <p role="status" className="mt-2 text-sm">Reading the receipt…</p>}
                    <details className="mt-4 text-sm"><summary className="cursor-pointer text-[#ffbc00]">Where do I find my bank reference?</summary>
                      <ul className="mt-3 space-y-2 text-white/70">
                        <li>Google Pay: Manage your money → See transaction history → open this payment.</li>
                        <li>PhonePe: History → open this payment → UTR.</li>
                        <li>Paytm: Balance &amp; History → open this payment → UPI Reference Number.</li>
                      </ul><p className="mt-3 text-white/60">Use the bank reference, not the app's separate internal transaction ID. If it is hidden, open the full payment details or share the receipt.</p>
                    </details>
                  </details>
                  <button className={buttonClass + " w-full"} disabled={busy || readingProof || !ready}>{busy ? "Submitting…" : status === "AWAITING_STATEMENT" || status === "NEEDS_REVIEW" ? "Update payment details" : "I've paid — submit for verification"}</button>
                </form>
              </>
            ) : <p>Your free registration is being confirmed. Refresh if confirmation does not appear.</p>}
            {!approved && !rejected && <p className="mt-5 text-sm text-white/60">Confirmation follows a match in the receiving bank statement. Please keep this checkout link. Do not pay again while verification is pending.</p>}
          </>
        )}
      </div>
    </section>
  );
}
