declare module "gsap" {
  interface GSAPConfig {
    autoSleep?: number;
    force3D?: string | boolean;
    nullTargetWarn?: boolean;
    trialWarn?: boolean;
    units?: { [key: string]: string };
  }

  interface TweenVars {
    [key: string]: any;
  }

  interface TimelineVars {
    [key: string]: any;
  }

  interface ScrollTriggerVars {
    trigger?: string | Element | null;
    start?: string | number | (() => string | number);
    end?: string | number | (() => string | number);
    scrub?: boolean | number;
    pin?: boolean | string | Element;
    [key: string]: any;
  }

  class ScrollTrigger {
    static create(vars?: ScrollTriggerVars): ScrollTrigger;
    static refresh(): void;
    static getAll(): ScrollTrigger[];
    static killAll(): void;
    kill(): void;
    refresh(): void;
    [key: string]: any;
  }

  interface Context {
    revert(): void;
    add(vars?: TweenVars): any;
    [key: string]: any;
  }

  interface GSAP {
    to(targets: any, vars: TweenVars): any;
    from(targets: any, vars: TweenVars): any;
    fromTo(targets: any, fromVars: TweenVars, toVars: TweenVars): any;
    set(targets: any, vars: TweenVars): any;
    timeline(vars?: TimelineVars): any;
    context(callback: () => void, scope?: any): Context;
    registerPlugin(...plugins: any[]): void;
    [key: string]: any;
  }

  const gsap: GSAP;
  export default gsap;
  export { ScrollTrigger };
}

declare module "gsap/ScrollTrigger" {
  import { ScrollTrigger } from "gsap";
  const ScrollTriggerDefault: typeof ScrollTrigger;
  export default ScrollTriggerDefault;
  export { ScrollTrigger };
}
