declare module '*.png' {
  const value: import('next/image').StaticImageData;
  export default value;
}

declare module '*.module.css' {
  const classes: { [key: string]: string };
  export default classes;
}

