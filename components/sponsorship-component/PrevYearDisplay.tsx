'use client';

import React from "react";
import { SetStateAction, useState } from "react";

function YearNumDiv() {
    const [selectedYear, setSelectedYear] = useState<number|null>(null);

    const handleClick = (id:number) => {
        setSelectedYear(id);
    };

    const years = [
        { yearNum: "2020", id: 0 },
        { yearNum: "2021", id: 1 },
        { yearNum: "2022", id: 2 },
        { yearNum: "2023", id: 3 }
    ];

    return (
        <div className="inline-flex flex-row gap-[30px] ml-[112px]">
            {years.map(year => {
                return (
                    <span 
                        onClick={() => handleClick(year.id)} 
                        className={`text-[#FFFFFF] cursor-pointer text-[31.415px] ${selectedYear === year.id ? 'opacity-[1]' : 'opacity-[0.4]'}`} 
                        key={year.id}
                    >
                        {year.yearNum}
                    </span>
                );
            })}
        </div>
    );
}


function Canvas(){
    return(
        <div className="w-[1789] shrink-0 rounded-[50px] h-[981px] bg-[#FFFFFF] border-[#E6287D] border-[10px]"></div>
    )
}


export default function PrevYear(){
    return(
        <div className="ml-[68px] mr-[69px] mt-[77px] bg-[#111]">
            <YearNumDiv></YearNumDiv>
            <Canvas></Canvas>
        </div>
    )

}