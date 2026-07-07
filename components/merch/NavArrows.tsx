import RightArrow from "@/Assets/SVG/-_.svg";
import LeftArrow from "@/Assets/SVG/leftArrow.svg";
export default function NavArrows()
{
    return (
        <div>
            <div className="flex gap-4 mx-4 max-sm:hidden">
                <div className="bg-zinc-100	p-3 w-12 h-12 rounded-full">
                    <LeftArrow />
                </div>
                <div className="bg-black p-3 w-12 h-12 rounded-full">
                    <RightArrow />
                </div>
            </div>

        </div>
    )
}