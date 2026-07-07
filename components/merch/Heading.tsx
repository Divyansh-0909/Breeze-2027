export default function Heading()
{
    return (
        <div>
            <div className="m-4 text-7xl max-sm:text-4xl">
                <div className="font-satoshi font-medium flex max-sm:flex max-sm:flex-col max-sm:items-center ">
                    <div>
                        Merch
                        <span className="font-fraunces font-semibold italic mx-4">Improving</span>
                    </div><div>
                        The Look
                    </div>
                    <div>
                        <button className="border border-black rounded-3xl px-4 bg-black text-white font-satoshi font-medium h-10 text-sm sm:hidden">
                            SHOP NOW
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}