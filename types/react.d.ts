declare module "react/jsx-runtime" {
  export function jsx(
    type: any,
    props: any,
    key?: string | number
  ): any;
  
  export function jsxs(
    type: any,
    props: any,
    key?: string | number
  ): any;
  
  export const Fragment: any;
}

declare namespace JSX {
  interface IntrinsicElements {
    [elemName: string]: any;
  }
  type Element = any;
}






