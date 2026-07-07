import Image from 'next/image';
import Merch from "@/Assets/Images/Men.png"

export default function Men()
{
    return (
        <div>
            <div className="m-4 flex gap-4 flex-wrap items-center justify-center">
                <Image src={Merch} alt="merch" className="rounded w-80" />
                <Image src={Merch} alt="merch" className="rounded w-80" />
                <Image src={Merch} alt="merch" className="rounded w-80" />
                <Image src={Merch} alt="merch" className="rounded w-80" />
            </div>
        </div>
    )
}