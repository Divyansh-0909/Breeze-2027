import * as THREE from 'three';

const channels = ['map', 'normalMap', 'roughnessMap', 'metalnessMap', 'aoMap'] as const;

// GLTFLoader may provide distinct ORM wrappers for one Source. Reuse only
// identical sampler/channel/colour interpretations; UV1 and sRGB views stay
// independent even when they happen to share the same underlying pixels.
function equivalentView(a: THREE.Texture, b: THREE.Texture) {
  return a.source === b.source && a.channel === b.channel && a.colorSpace === b.colorSpace &&
    a.wrapS === b.wrapS && a.wrapT === b.wrapT && a.magFilter === b.magFilter &&
    a.minFilter === b.minFilter && a.anisotropy === b.anisotropy && a.format === b.format &&
    a.type === b.type && a.flipY === b.flipY && a.premultiplyAlpha === b.premultiplyAlpha &&
    a.unpackAlignment === b.unpackAlignment && a.generateMipmaps === b.generateMipmaps &&
    a.rotation === b.rotation && a.repeat.equals(b.repeat) && a.offset.equals(b.offset) &&
    a.center.equals(b.center);
}

/** Cave-local transforms own sampler wrappers, never source images. Three's
 * Source remains shared. UV1, normal orientation, offsets and colour spaces
 * stay intact. Repeat is divided ONCE relative to the borrowed quarry map. */
export class CaveTextureSampling {
  private readonly maps = new Map<THREE.Texture, THREE.Texture>();
  private featureScale = 2;

  apply(material: THREE.MeshStandardMaterial, scale = this.featureScale) {
    this.featureScale = scale;
    for (const key of channels) {
      const borrowed = material[key];
      if (!borrowed) continue;
      // Re-applying a diagnostic scale must not clone or compound the scale.
      const existing = [...this.maps].find(([, owned]) => owned === borrowed);
      const source = existing?.[0] ?? borrowed;
      let owned = this.maps.get(source) ?? [...this.maps].find(([parent]) => equivalentView(parent, source))?.[1];
      if (!owned) {
        owned = source.clone();
        owned.name = 'Cave_Local_Sampling_' + source.name;
      }
      this.maps.set(source, owned);
      owned.repeat.copy(source.repeat).divideScalar(scale);
      owned.updateMatrix();
      material[key] = owned;
    }
  }

  diagnostics() {
    return {featureScale: this.featureScale, ownedTextureWrappers: new Set(this.maps.values()).size, borrowedTextureWrappers: this.maps.size,
      newSourceImages: 0, quarryTexturesMutated: false,
      channels: [...this.maps].map(([source, owned]) => ({source: source.source.uuid,
        sharedSource: source.source === owned.source, sourceRepeat: source.repeat.toArray(),
        caveRepeat: owned.repeat.toArray(), offset: owned.offset.toArray(),
        channel: owned.channel, colourSpace: owned.colorSpace}))};
  }

  dispose() {
    new Set(this.maps.values()).forEach(texture => texture.dispose());
    this.maps.clear();
    // The parent quarry owner exclusively closes ImageBitmaps.
  }
}
