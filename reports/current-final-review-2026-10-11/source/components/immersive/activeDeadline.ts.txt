/** An active-tab budget, independent of render FPS and cancellable on stale serials. */
export function activeDeadline(budgetMs: number, expire: () => void, now = () => performance.now(),
  schedule = (fn: () => void, ms: number) => setTimeout(fn, ms), cancelTimer = (id: ReturnType<typeof setTimeout>) => clearTimeout(id)) {
  let remaining = budgetMs, started = 0, timer: ReturnType<typeof setTimeout> | null = null, finished = false;
  return {
    resume() { if (finished || timer !== null) return; started = now(); timer = schedule(() => { timer = null; finished = true; expire(); }, remaining); },
    pause() { if (timer === null || finished) return; cancelTimer(timer); timer = null; remaining = Math.max(0, remaining - (now() - started)); },
    cancel() { if (timer !== null) cancelTimer(timer); timer = null; finished = true; },
  };
}
