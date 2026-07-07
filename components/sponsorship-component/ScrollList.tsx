import Image from "next/image"
import React from "react"

export default function ScrollList(){
    return(
        <div className="inline-flex justify-center align-center gap-[47px]">
            <ul className={`flex items-center shrink-0 justify-center md:justify-start gap-[47px] animate-infinite-scroll`}>
                <li>
                    <Image src="/images/scrollbar_asterick.png" alt="asterick" height={33} width={34}/>
                </li>
                <li>
                    <span className="text-white font-fatal text-[44.16px] leading-[42px]">Hungama</span>
                </li>
                <li>
                    <Image src="/images/scrollbar_asterick.png" alt="asterick" height={33} width={34}/>
                </li>
                <li>
                    <div className="text-[44px] text-[#7A7A7A] font-acid leading-[41px]">14<sup>th</sup> February 2025</div>
                </li>
                <li>
                    <Image src="/images/scrollbar_asterick.png" alt="asterick" height={33} width={34}/>
                </li>
                <li>
                    <span className="text-white font-fatal text-[44.16px] leading-[42px]">Hungama</span>
                </li>
                <li>
                    <Image src="/images/scrollbar_asterick.png" alt="asterick" height={33} width={34}/>
                </li>
                <li>
                    <div className="text-[44px] text-[#7A7A7A] font-acid leading-[41px]">14<sup>th</sup> February 2025</div>
                </li>

            </ul>
            
        </div>
             
        
    )
}