import { Button } from "@/components/ui/button";
import Link from "next/link";
import Image from "next/image";

export default function Box(props) {
  return (
    <div className=" grid w-[266.4px]  h-[381px] grid-cols-[2fr_1fr_1fr] grid-rows-[16fr_1fr_1fr] lg:w-[280px] lg:h-[401px] xl:w-[333px] xl:h-[477px] group transition-transform duration-300 hover:-translate-y-2">
      <div className="border-2 mb-4 rounded-[15px] col-start-1 col-end-4">
        <Image
          src={props.img}
          alt={props.name}
          width={333}
          height={400}
          className="rounded-[13.5px]"
        />
      </div>
      <div className="text-sm  font-normal text-muted-foreground">
        {props.title}
      </div>
      <div className="col-start-2 col-end-3 row-start-2 row-end-4 text-center self-center">
        <Link href={`tel:${props.number}`}>
          <Button
            variant="outline"
            className="font-bold rounded-xl border-2 p-[15px]"
          >
            Call
          </Button>
        </Link>
      </div>
      <div className=" col-start-3 col-end-4 row-start-2 row-end-4 text-center self-center">
        <Link href={`mailto:${props.email}`}>
          <Button
            variant="outline"
            className="font-bold rounded-xl border-2  p-[15px]"
          >
            Mail
          </Button>
        </Link>
      </div>
      <div className=" font-bold text-sm">{props.name}</div>
    </div>
  );
}
