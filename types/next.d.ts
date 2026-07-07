declare module "next/image" {
  interface StaticImageData {
    src: string;
    height: number;
    width: number;
    blurDataURL?: string;
  }
  
  interface ImageProps {
    src: string | StaticImageData;
    alt: string;
    width?: number;
    height?: number;
    fill?: boolean;
    className?: string;
    priority?: boolean;
    quality?: number;
    placeholder?: "blur" | "empty";
    blurDataURL?: string;
    unoptimized?: boolean;
    loader?: (props: { src: string; width: number; quality?: number }) => string;
    sizes?: string;
    onLoad?: (event: any) => void;
    onError?: (event: any) => void;
    [key: string]: any;
  }
  
  const Image: {
    (props: ImageProps): JSX.Element;
    displayName?: string;
  };
  export default Image;
  export type { StaticImageData };
}
