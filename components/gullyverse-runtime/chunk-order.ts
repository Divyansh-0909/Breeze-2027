export type Chunk = "cypher-gate" | "cypher-approach" | "market-south" | "market-north" | "cypher-plaza" | "cypher-audience";
export const laneChunks: Chunk[] = ["market-south", "market-north", "cypher-approach", "cypher-gate"];
export const plazaChunks: Chunk[] = ["cypher-gate", "cypher-approach", "cypher-plaza", "cypher-audience"];
const all: Chunk[] = ["cypher-gate", "cypher-approach", "market-south", "market-north", "cypher-plaza", "cypher-audience"];

/** The chunks around the arrival pose load first (the plaza begins at about z = -8); the rest stream after. */
export function chunkOrder(z: number) {
  const near = z > -8 ? laneChunks : plazaChunks;
  return { near, later: all.filter(name => !near.includes(name)) };
}
