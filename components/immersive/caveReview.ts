import {carryScannedMaterialReview} from './scannedRockSampling';

/** Explicit private gate; ordinary URLs keep the existing public environment. */
export function naturalCaveReview(search: string, allowed: boolean) {
  return allowed && ['natural-cave', 'deep-rock', 'material-study'].includes(new URLSearchParams(search).get('entranceReview') ?? '');
}
export function carryCaveReview(href: string, search: string, allowed: boolean) {
  const carried = carryScannedMaterialReview(href, search, allowed);
  if (!naturalCaveReview(search, allowed)) return carried;
  const url = new URL(carried, 'https://gullyverse.invalid');
  url.hash = new URL(href, url.origin).hash;
  url.searchParams.set('entranceReview', new URLSearchParams(search).get('entranceReview')!);
  url.searchParams.set('quarryReview', 'geology-fidelity');
  if (new URLSearchParams(search).get('entranceReview') === 'material-study') {
    for (const key of ['caveMaterial','caveFeatureScale','caveGeometry']) {
      const value = new URLSearchParams(search).get(key);
      if (value) url.searchParams.set(key,value);
    }
  }
  return url.pathname + url.search + url.hash;
}
