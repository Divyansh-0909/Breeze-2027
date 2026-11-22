/**
 * `/` now opens the walkable gully and cypher. The original quarry hub stays
 * available at `/?hub=classic`; its own navigation writes `/?arrival=…`, so
 * those URLs keep the classic hub as well.
 */
export function wantsClassicHub(params: URLSearchParams | Readonly<Record<string, string | string[] | undefined>>) {
  const get = (key: string) => params instanceof URLSearchParams ? params.get(key) : params[key];
  return get("hub") === "classic" || get("arrival") !== undefined && get("arrival") !== null;
}
