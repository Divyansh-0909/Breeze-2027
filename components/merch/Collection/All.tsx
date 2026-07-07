import Image from 'next/image';
import Merch from "@/Assets/Images/Merch.png"

export default function All()
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