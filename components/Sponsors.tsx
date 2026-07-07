import SponsComp from "./sponsorship-component/SponsImage";

import TopText from "@/components/sponsorship-component/TopTesx";

export default function Sponsors() {
  return (
    <div>
      <div className="bg-muted">
        <div className="flex flex-col justify-center  sm:my-20 shrink-0  max-w-[full] overflow-hidden my-10 lg:mb-28  bg-muted">
          <TopText></TopText>
          <SponsComp></SponsComp>
        </div>
      </div>
    </div>
  );
}
