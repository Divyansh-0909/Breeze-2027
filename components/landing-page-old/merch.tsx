import ProCard from "@/components/landing-page-old/procard";

export default function Merch() {
  return (
    <div className="bg-white flex flex-col justify-center py-14 lg:pl-8  ">
      <div className="text-left md:text-[20px] text-[15px] md:px-4  pl-4 mb:pb-[100px] lg:text-[25px] ]">
        OUR MERCH
      </div>
      <div className="flex justify-between items-center md:px-4 md:pb-4 pl-4 lg:pb-[0px]">
        <div className="text-left md:text-[35px] text-[23px] lg:text-[40px]">
          The Coolest Merch Around
        </div>

        <div>
          <button className="underline text-[12px] md:text-[16px] lg:text-[20px]">
            All Apparel
          </button>
          <button className=" bg-[#FABF12] rounded-[50%] md:w-[30px] md:h-[30px] w-[20px] h-[20px] text-[10px] md:text-[20px] lg:text-[25px] lg:w-[50px] lg:h-[50px]">
            {" "}
            &#8594;
          </button>
        </div>
      </div>
      <div>
        <ProCard />
      </div>
    </div>
  );
}
