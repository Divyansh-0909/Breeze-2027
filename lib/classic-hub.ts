/**
 * `/` opens the walkable gully and cypher. The original quarry hub stays
 * available only through an explicit `?hub=classic`, so old `/?arrival=…`
 * URLs from earlier visits still open the new journey.
 */
export function wantsClassicHub(params: URLSearchParams | Readonly<Record<string, string | string[] | undefined>>) {
  return (params instanceof URLSearchParams ? params.get("hub") : params.hub) === "classic";
}

/** Carries `hub=classic` onto the URLs the original hub writes while it navigates. */
export function keepClassicHub(href: string, search: string) {
  if (!wantsClassicHub(new URLSearchParams(search))) return href;
  const url = new URL(href, "https://gullyverse.invalid");
  url.searchParams.set("hub", "classic");
  return url.pathname + url.search + url.hash;
}
