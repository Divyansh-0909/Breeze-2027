import { redirect } from "next/navigation";

// The Aftermovie lives on the cypher screen in the walkable gully.
export default function AftermoviePage() {
  redirect("/?start=aftermovie");
}
