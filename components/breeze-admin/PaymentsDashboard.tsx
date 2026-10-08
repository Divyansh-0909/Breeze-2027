"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import type { ColumnMap } from "@/lib/payments/statements";

type Account = { id: string; label: string; bankName: string; accountLast4: string; upiId: string; payeeName: string; active: boolean; noteMatchingVerified: boolean; _count?: { transactions: number } };
type Order = { token: string; name: string; email: string; amount: string; paymentReference: string; paymentStatus: string; paymentReviewReason?: string; claimedBankReference?: string; bankReference?: string; approved: boolean; rejected: boolean; paymentAccount?: { label: string }; paymentEmails: { kind: string; status: string; attempts: number }[]; paymentAudits: { action: string; createdAt: string }[] };
type Draft = { statementId: string; accountId: string; reviewed: boolean; headers: string[]; rows: string[][]; rowCount: number; warnings: string[]; sourceText: string; columns: ColumnMap; format: string };
type Preview = { normalized: { sourceRow: number; bookedAt: string; amountPaise: string; direction: string; bankReference: string; orderReferences: string[] }[]; offset: number; transactionCount: number; errors: { row: number; message: string }[]; errorCount: number; ignored: number };
const emptyColumns: ColumnMap = { date: -1, description: -1, credit: -1, debit: -1, amount: -1, direction: -1, reference: -1 };
const canonicalColumns: ColumnMap = { date: 0, description: 1, credit: 2, debit: 3, reference: 4, amount: -1, direction: -1 };
const fieldClass = "w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-purple-500";
const buttonClass = "rounded-lg bg-[#202020] px-4 py-2 text-sm font-medium text-white disabled:opacity-40";
const sectionClass = "rounded-2xl border border-gray-200 bg-white p-5 sm:p-7";

const sampleAccount: Account = { id: "preview-account", label: "Sample receiving account", bankName: "Example Bank", accountLast4: "0000", upiId: "demo@invalid", payeeName: "Sample recipient", active: true, noteMatchingVerified: false, _count: { transactions: 1 } };
const sampleOrder: Order = { token: "preview", name: "Example student", email: "student@example.invalid", amount: "800", paymentReference: "BZ27ABCDEFGHJK", paymentStatus: "AWAITING_STATEMENT", approved: false, rejected: false, paymentAccount: { label: sampleAccount.label }, paymentEmails: [], paymentAudits: [] };

export default function PaymentsDashboard({ previewOnly = false }: { previewOnly?: boolean }) {
  const [ready, setReady] = useState(false);
  const [accounts, setAccounts] = useState<Account[]>(previewOnly ? [sampleAccount] : []);
  const [orders, setOrders] = useState<Order[]>(previewOnly ? [sampleOrder] : []);
  const [statements, setStatements] = useState<{ id: string; filename: string; reviewed: boolean; account: { label: string } }[]>([]);
  const [accountId, setAccountId] = useState(previewOnly ? sampleAccount.id : "");
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [draft, setDraft] = useState<Draft | null>(null);
  const [columns, setColumns] = useState<ColumnMap>(emptyColumns);
  const [dateOrder, setDateOrder] = useState<"DMY" | "MDY">("DMY");
  const [correctedCsv, setCorrectedCsv] = useState("");
  const [normalized, setNormalized] = useState<Preview | null>(null);
  const [accountConfirmed, setAccountConfirmed] = useState(false);
  const [extractionConfirmed, setExtractionConfirmed] = useState(false);
  const [jevConfigured, setJevConfigured] = useState(false);
  const [jevNotice, setJevNotice] = useState("");
  const [filter, setFilter] = useState("ALL");

  const request = useCallback(async (url: string, options?: RequestInit) => {
    const response = await fetch(url, options);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "The request failed.");
    return data;
  }, []);
  const reload = useCallback(async () => {
    if (previewOnly) return;
    const [accountData, paymentData] = await Promise.all([request("/api/breeze-admin/payments/accounts"), request("/api/breeze-admin/payments")]);
    setAccounts(accountData.accounts); setOrders(paymentData.orders); setStatements(paymentData.statements); setJevConfigured(paymentData.jevConfigured);
  }, [previewOnly, request]);
  useEffect(() => { setReady(true); void reload().catch(error => setError(error.message)); }, [reload]);
  const post = (url: string, body: unknown, method = "POST") => request(url, { method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });

  async function addAccount(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); const form = event.currentTarget; setBusy("account"); setError("");
    try {
      const values = Object.fromEntries(new FormData(form).entries());
      if (previewOnly) setAccounts(existing => [...existing, { ...values, id: `preview-${Date.now()}`, active: false, noteMatchingVerified: false } as unknown as Account]);
      else { await post("/api/breeze-admin/payments/accounts", values); await reload(); }
      form.reset(); setNotice(previewOnly ? "Preview account added locally." : "Account saved. Activate it when ready to receive new orders.");
    } catch (error) { setError(error.message); } finally { setBusy(""); }
  }

  async function accountAction(account: Account, action: string) {
    if (action === "verifyNotes" && !window.confirm("Have you checked a real payment from each supported UPI app and found its COMPLETE Breeze order reference in this account's bank statement? Enabling this allows automatic order-note matching.")) return;
    setBusy("account"); setError("");
    try {
      if (previewOnly) setAccounts(items => items.map(item => ({ ...item, active: action === "activate" ? item.id === account.id : action === "deactivate" && item.id === account.id ? false : item.active, noteMatchingVerified: item.id === account.id && ["verifyNotes", "disableNotes"].includes(action) ? action === "verifyNotes" : item.noteMatchingVerified })));
      else { await post("/api/breeze-admin/payments/accounts", { id: account.id, action, confirmed: action === "verifyNotes" }, "PATCH"); await reload(); }
      setNotice("Account updated. Existing orders keep their original receiving account.");
    } catch (error) { setError(error.message); } finally { setBusy(""); }
  }

  function sampleStatement() {
    const sample: Draft = { statementId: "preview-statement", accountId: sampleAccount.id, reviewed: false, headers: ["Date", "Description", "Credit", "Debit", "Bank Reference"], rows: [["07/10/2026", "UPI BREEZE BZ27ABCDEFGHJK", "800.00", "", "627912345678"]], rowCount: 1, warnings: ["Fictional statement for preview only."], sourceText: "Example statement", columns: canonicalColumns, format: "CSV" };
    setDraft(sample); setColumns(sample.columns); setNormalized(null); setAccountConfirmed(false); setExtractionConfirmed(false);
  }

  async function uploadStatement(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy("extract"); setError(""); setNormalized(null); setDraft(null);
    setAccountConfirmed(false); setExtractionConfirmed(false); setCorrectedCsv("");
    try {
      const form = new FormData(event.currentTarget); form.set("accountId", accountId);
      const data = await request("/api/breeze-admin/payments/statements", { method: "POST", body: form });
      setDraft(data); setColumns(data.columns); setNotice(data.reviewed ? "This file has already been imported. You can run matching again without creating duplicate credits." : "Statement extracted. Map columns and preview before importing.");
    } catch (error) { setError(error.message); } finally { setBusy(""); }
  }

  async function previewStatement(useCanonical = false, offset = 0) {
    setBusy("preview"); setError(""); setExtractionConfirmed(false);
    try {
      if (previewOnly) { setNormalized({ normalized: [{ sourceRow: 2, bookedAt: "2026-10-07T00:00:00.000Z", amountPaise: "80000", direction: "CREDIT", bankReference: "627912345678", orderReferences: ["BZ27ABCDEFGHJK"] }], offset: 0, transactionCount: 1, errors: [], errorCount: 0, ignored: 0 }); return; }
      const mapping = useCanonical ? canonicalColumns : columns;
      const data = await post("/api/breeze-admin/payments/statements", { action: "preview", statementId: draft.statementId, columns: mapping, dateOrder, correctedCsv: correctedCsv || undefined, offset });
      setColumns(mapping); setDraft(current => ({ ...current, headers: data.headers })); setNormalized(data);
    } catch (error) { setError(error.message); } finally { setBusy(""); }
  }

  async function runMatching(id: string) {
    if (previewOnly) { setNotice("Preview only: an exact reference + ₹800 incoming credit would be eligible after account note testing. No real order was approved."); return; }
    let afterToken: string | undefined, approved = 0, review = 0, waiting = 0;
    do {
      const result = await post("/api/breeze-admin/payments", { action: "reconcile", accountId: id, afterToken });
      approved += result.approved; review += result.review; waiting += result.waiting;
      setNotice(`Matching: ${approved} approved, ${review} need review, ${waiting} waiting for a statement.`);
      afterToken = result.hasMore ? result.nextCursor : undefined;
    } while (afterToken);
    const email = await post("/api/breeze-admin/payments", { action: "emails" });
    setNotice(`${approved} approved, ${review} need review, ${waiting} waiting. ${email.configured ? `${email.sent} confirmation email(s) sent; remaining emails stay queued.` : "Email is not configured; confirmations are queued."}`);
    await reload();
  }

  async function importStatement() {
    setBusy("import"); setError("");
    try {
      if (previewOnly) { setDraft(current => ({ ...current, reviewed: true })); await runMatching(draft.accountId); return; }
      const result = await post("/api/breeze-admin/payments/statements", { action: "commit", statementId: draft.statementId, columns, dateOrder, correctedCsv: correctedCsv || undefined, accountConfirmed, extractionConfirmed });
      setDraft(current => ({ ...current, reviewed: true }));
      setNotice(`${result.imported} entries imported; ${result.duplicates} duplicates skipped; ${result.conflicts} conflicts held for review.`);
      await runMatching(result.accountId);
    } catch (error) { setError(error.message); } finally { setBusy(""); }
  }

  async function runAction(action: () => Promise<void>) {
    setBusy("action"); setError("");
    try { await action(); } catch (error) { setError(error.message); } finally { setBusy(""); }
  }

  const selected = accounts.find(account => account.id === (draft?.accountId || accountId));
  const visibleOrders = orders.filter(order => filter === "ALL" || (filter === "REVIEW" ? order.paymentStatus.includes("REVIEW") : filter === "APPROVED" ? order.approved : !order.approved && !order.rejected));
  return (
    <div className="space-y-7 text-[#202020]">
      <fieldset disabled={!ready} className="min-w-0 space-y-7">
      <div><p className="text-sm font-medium text-purple-700">Breeze 2027 · Payments</p><h1 className="mt-2 text-3xl font-semibold">Bank statement matching</h1><p className="mt-2 max-w-3xl text-gray-600">Assign a receiving account, import its bank statement, and automatically confirm exact payment matches. Uncertain payments stay available for team review.</p></div>
      {previewOnly && <p className="rounded-xl border border-amber-300 bg-amber-50 p-4">Preview only: fictional records, no database writes, and no real payment approvals. <Link href="/payments/preview" className="underline">Open customer preview</Link>.</p>}
      {error && <p role="alert" className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">{error}</p>}
      {notice && <p role="status" className="rounded-xl bg-purple-50 p-4 text-purple-900">{notice}</p>}

      <section className={sectionClass}>
        <h2 className="text-xl font-semibold">Receiving accounts</h2><p className="mt-2 text-sm text-gray-600">Account details are permanent. Add a new record when the UPI ID or receiving bank changes. Activating an account applies to new checkouts.</p>
        <div className="mt-5 grid gap-4 xl:grid-cols-2">{accounts.map(account => <div key={account.id} className="rounded-xl border border-gray-200 p-4">
          <div className="flex flex-wrap justify-between gap-2"><strong>{account.label}</strong><span className={account.active ? "text-sm text-green-700" : "text-sm text-gray-500"}>{account.active ? "Active for new orders" : "Inactive"}</span></div>
          <p className="mt-2 text-sm">{account.bankName} · account ending {account.accountLast4}</p><p className="mt-1 break-all text-sm text-gray-600">{account.payeeName} · {account.upiId}</p>
          <p className="mt-3 text-sm">{account.noteMatchingVerified ? "Order-note matching verified" : "Order notes need a real payment test"}</p>
          <div className="mt-4 flex flex-wrap gap-2"><button className={buttonClass} disabled={Boolean(busy)} onClick={() => void accountAction(account, account.active ? "deactivate" : "activate")}>{account.active ? "Pause new payments" : "Use for new orders"}</button><button className="rounded-lg border border-gray-300 px-3 py-2 text-sm disabled:opacity-40" disabled={Boolean(busy)} onClick={() => void accountAction(account, account.noteMatchingVerified ? "disableNotes" : "verifyNotes")}>{account.noteMatchingVerified ? "Disable note matching" : "Confirm note test"}</button></div>
        </div>)}</div>
        <details className="mt-5"><summary className="cursor-pointer font-medium text-purple-700">Add receiving account</summary><form className="mt-4 grid gap-4 sm:grid-cols-2" onSubmit={addAccount}>
          {[["label", "Account label", "Festival collection A"], ["bankName", "Bank name", "Receiving bank"], ["accountLast4", "Last four account digits", "1234"], ["upiId", "Receiving UPI ID", "recipient@bank"], ["payeeName", "Recipient name shown in UPI", "Account holder name"]].map(([name, label, placeholder]) => <label key={name} className="text-sm">{label}<input className={fieldClass + " mt-1"} name={name} placeholder={placeholder} required maxLength={name === "accountLast4" ? 4 : 150} pattern={name === "accountLast4" ? "[0-9]{4}" : undefined} /></label>)}
          <div className="flex items-end"><button className={buttonClass} disabled={Boolean(busy)}>Save account</button></div>
        </form></details>
      </section>

      <section className={sectionClass}>
        <h2 className="text-xl font-semibold">Import a bank statement</h2><p className="mt-2 text-sm text-gray-600">PDF or CSV · up to 10 MB. Text PDFs support up to 100 pages; scanned PDFs support up to 10 pages with OCR. Keep the original open while checking extraction.</p>
        <form onSubmit={uploadStatement} className="mt-5 flex flex-col gap-4 lg:flex-row lg:items-end">
          <label className="flex-1 text-sm">Receiving account<select className={fieldClass + " mt-1"} value={accountId} onChange={event => { setAccountId(event.target.value); setDraft(null); setNormalized(null); }} required><option value="">Choose account</option>{accounts.map(account => <option key={account.id} value={account.id}>{account.label} · {account.bankName} · {account.accountLast4}</option>)}</select></label>
          {!previewOnly && <label className="flex-1 text-sm">Bank export<input type="file" name="file" accept=".csv,.pdf,text/csv,application/pdf" required className="mt-2 block w-full text-sm" /></label>}
          {previewOnly ? <button type="button" className={buttonClass} onClick={sampleStatement}>Load sample statement</button> : <button className={buttonClass} disabled={Boolean(busy) || !accountId}>{busy === "extract" ? "Extracting statement…" : "Extract and preview"}</button>}
        </form>
        {draft && <div className="mt-6 space-y-5">
          <div className="rounded-lg bg-amber-50 p-3 text-sm">{draft.warnings.map(warning => <p key={warning}>{warning}</p>)}<p className="mt-2">Receiving account: <strong>{selected?.label} · {selected?.bankName} · {selected?.accountLast4}</strong></p></div>
          {draft.headers.length > 0 && <><p className="text-sm text-gray-600">{draft.rowCount} extracted rows. Map the columns below; no payments are approved during preview.</p><div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            {(Object.keys(columns) as (keyof ColumnMap)[]).map(key => <label className="text-sm capitalize" key={key}>{key === "reference" ? "Bank reference / UTR" : key}<select className={fieldClass + " mt-1"} value={columns[key]} onChange={event => { setColumns(previous => ({ ...previous, [key]: Number(event.target.value) })); setNormalized(null); setExtractionConfirmed(false); }}><option value={-1}>Not present</option>{draft.headers.map((header, index) => <option key={index} value={index}>{index + 1}. {header || "Unnamed column"}</option>)}</select></label>)}
            <label className="text-sm">Date order<select className={fieldClass + " mt-1"} value={dateOrder} onChange={event => { setDateOrder(event.target.value as "DMY" | "MDY"); setNormalized(null); setExtractionConfirmed(false); }}><option value="DMY">Day / month / year</option><option value="MDY">Month / day / year</option></select></label>
          </div><div className="overflow-x-auto"><table className="w-full text-left text-xs"><thead><tr>{draft.headers.map((header, index) => <th className="border-b p-2" key={index}>{header}</th>)}</tr></thead><tbody>{draft.rows.slice(0, 8).map((row, index) => <tr key={index}>{row.map((cell, column) => <td key={column} className="max-w-xs border-b p-2">{cell}</td>)}</tr>)}</tbody></table></div></>}
          <details open={!draft.headers.length}><summary className="cursor-pointer text-sm font-medium">Extracted text and corrected CSV</summary><pre className="mt-3 max-h-52 overflow-auto whitespace-pre-wrap rounded-lg bg-gray-50 p-3 text-xs">{draft.sourceText}</pre><p className="my-3 text-sm">If columns or wrapped lines were not read correctly, paste corrected CSV using this exact header: <code>Date,Description,Credit,Debit,Bank Reference</code>. Preserve every credit and debit. Check all values against the bank export.</p><textarea className={fieldClass + " min-h-36 font-mono"} value={correctedCsv} onChange={event => { setCorrectedCsv(event.target.value); setNormalized(null); setExtractionConfirmed(false); }} placeholder={'Date,Description,Credit,Debit,Bank Reference\n07/10/2026,UPI BREEZE BZ27ABCDEFGHJK,800.00,,627912345678'} /><button type="button" className={buttonClass + " mt-3"} disabled={Boolean(busy) || !correctedCsv.trim()} onClick={() => void previewStatement(true)}>Preview corrected CSV</button></details>
          {draft.headers.length > 0 && <button className={buttonClass} disabled={Boolean(busy)} onClick={() => void previewStatement()}>Validate mapped rows</button>}
          {normalized && <div className="space-y-3"><p className="text-sm"><strong>{normalized.transactionCount}</strong> transactions · {normalized.errorCount} invalid rows · {normalized.ignored} zero/summary rows ignored. Showing {normalized.transactionCount ? normalized.offset + 1 : 0}–{Math.min(normalized.offset + 100, normalized.transactionCount)}.</p>
            {normalized.errors.map(error => <p className="text-sm text-red-700" key={error.row}>Row {error.row}: {error.message}</p>)}
            <div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead><tr>{["Row", "Date", "Direction", "Amount", "Bank reference", "Order code"].map(label => <th className="border-b p-2" key={label}>{label}</th>)}</tr></thead><tbody>{normalized.normalized.map(row => <tr key={row.sourceRow}><td className="border-b p-2">{row.sourceRow}</td><td className="border-b p-2">{row.bookedAt.slice(0, 10)}</td><td className="border-b p-2">{row.direction}</td><td className="border-b p-2">₹{(Number(row.amountPaise) / 100).toFixed(2)}</td><td className="border-b p-2">{row.bankReference || "Missing — review"}</td><td className="border-b p-2 font-mono">{row.orderReferences.join(", ") || "Not present"}</td></tr>)}</tbody></table></div>
            {normalized.transactionCount > 100 && <div className="flex gap-3"><button className={buttonClass} disabled={Boolean(busy) || normalized.offset === 0} onClick={() => void previewStatement(false, Math.max(0, normalized.offset - 100))}>Previous 100 rows</button><button className={buttonClass} disabled={Boolean(busy) || normalized.offset + 100 >= normalized.transactionCount} onClick={() => void previewStatement(false, normalized.offset + 100)}>Next 100 rows</button></div>}
            <label className="flex items-start gap-2 text-sm"><input type="checkbox" checked={accountConfirmed} onChange={event => setAccountConfirmed(event.target.checked)} />This is the bank statement for {selected?.label}, account ending {selected?.accountLast4}.</label>
            <label className="flex items-start gap-2 text-sm"><input type="checkbox" checked={extractionConfirmed} onChange={event => setExtractionConfirmed(event.target.checked)} />I checked all extracted rows, references, dates, and credit/debit amounts against the original statement.</label>
            <p className="text-sm text-gray-600">Importing starts automatic matching. Exact eligible credits confirm orders; conflicts and missing references stay for review.</p>
            <button className={buttonClass} disabled={Boolean(busy) || draft.reviewed || !accountConfirmed || !extractionConfirmed || normalized.errorCount > 0 || normalized.transactionCount === 0} onClick={() => void importStatement()}>{busy === "import" ? "Importing and matching…" : draft.reviewed ? "Statement already imported" : "Import and automatically match payments"}</button>
          </div>}
          <div><button className="text-sm text-purple-700 underline disabled:opacity-40" disabled={Boolean(busy) || !draft.rows.length || (!jevConfigured && !previewOnly)} onClick={() => void runAction(async () => { if (previewOnly) { setJevNotice("Preview: Jev supplies a review suggestion; it cannot approve an order."); return; } const result = await post("/api/breeze-admin/payments/statements", { action: "jev", statementId: draft.statementId, rowIndex: 0, correctedCsv: correctedCsv || undefined }); setJevNotice(result.enabled ? `First row: ${result.classification}, confidence ${(result.confidence * 100).toFixed(1)}%, ${result.inputTokens} input tokens. Suggestion only.` : result.message); })}>Ask Jev about the first extracted row</button><p className="mt-2 text-xs text-gray-500">{jevNotice || (jevConfigured ? "Jev is configured. Review suggestions never override exact matching rules." : "Add TYPESAFE_API_KEY in the server environment to enable optional Jev review.")}</p></div>
        </div>}
      </section>

      <section className={sectionClass}><div className="flex flex-wrap justify-between gap-3"><h2 className="text-xl font-semibold">Payment queue</h2><div className="flex gap-2"><select className={fieldClass} aria-label="Filter orders" value={filter} onChange={event => setFilter(event.target.value)}><option value="ALL">Latest 100 orders</option><option value="PENDING">Awaiting confirmation</option><option value="REVIEW">Needs review</option><option value="APPROVED">Approved</option></select><button className={buttonClass} disabled={Boolean(busy)} onClick={() => void runAction(reload)}>Refresh</button></div></div>
        <div className="my-4 flex flex-wrap gap-2">{accounts.map(account => <button key={account.id} className="rounded-lg border border-gray-300 px-3 py-2 text-sm disabled:opacity-40" disabled={Boolean(busy)} onClick={() => void runAction(() => runMatching(account.id))}>Recheck {account.label}</button>)}<button className="rounded-lg border border-gray-300 px-3 py-2 text-sm disabled:opacity-40" disabled={Boolean(busy)} onClick={() => void runAction(async () => { if (previewOnly) { setNotice("Preview: no emails sent."); return; } const result = await post("/api/breeze-admin/payments", { action: "emails" }); setNotice(result.configured ? `${result.sent} emails sent; ${result.failed} failed.` : "Configure email credentials to send queued confirmations."); await reload(); })}>Send queued emails</button></div>
        <div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead><tr>{["Order / customer", "Account / amount", "Status / evidence", "Review"].map(label => <th className="border-b p-3" key={label}>{label}</th>)}</tr></thead><tbody>{visibleOrders.map(order => <tr key={order.token} className="align-top"><td className="border-b p-3"><p className="font-mono font-semibold">{order.paymentReference || "Legacy order"}</p><p className="mt-1">{order.name}</p><p className="text-gray-500">{order.email}</p></td><td className="border-b p-3"><p>{order.paymentAccount?.label || "Legacy account"}</p><p className="mt-1">₹{order.amount}</p></td><td className="border-b p-3"><p>{order.paymentStatus.replaceAll("_", " ")}</p><p className="mt-1 text-xs text-gray-600">{order.paymentReviewReason}</p><p className="mt-2 font-mono text-xs">Bank: {order.bankReference || order.claimedBankReference || "Not supplied"}</p><details className="mt-2 text-xs"><summary className="cursor-pointer">Audit and email status</summary>{order.paymentAudits.map((audit, index) => <p key={index}>{audit.action} · {new Date(audit.createdAt).toLocaleString("en-IN")}</p>)}{order.paymentEmails.map(email => <div key={email.kind}><p>{email.kind}: {email.status}</p>{email.status === "FAILED" && <button className="text-purple-700 underline" disabled={Boolean(busy)} onClick={() => void runAction(async () => { const result = await post("/api/breeze-admin/payments", { action: "retryEmail", token: order.token, kind: email.kind }); setNotice(result.emailSent ? "Email sent." : result.emailError); await reload(); })}>Retry email</button>}</div>)}</details></td><td className="border-b p-3"><Link className="text-purple-700 underline" href={previewOnly ? "/payments/preview" : `/checkout?token=${order.token}`}>View checkout</Link>{order.approved && !previewOnly && <Link className="mt-2 block text-purple-700 underline" href={`/reciept/${order.token}`}>Receipt</Link>}{!order.approved && !order.rejected && !previewOnly && <Link className="mt-2 block text-purple-700 underline" href="/admin/breeze-admin">Review proof / approve manually</Link>}</td></tr>)}</tbody></table>{!visibleOrders.length && <p className="py-6 text-gray-500">No orders in this view.</p>}</div>
      </section>
      {statements.length > 0 && <section className={sectionClass}><h2 className="text-xl font-semibold">Recent statement imports</h2><ul className="mt-3 space-y-2 text-sm">{statements.map(statement => <li key={statement.id}>{statement.filename} · {statement.account.label} · {statement.reviewed ? "Imported" : "Draft preview"}</li>)}</ul></section>}
      </fieldset>
    </div>
  );
}
