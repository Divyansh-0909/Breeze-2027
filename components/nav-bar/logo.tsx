import Image from "next/image";
import React from "react";

const Logo = () =>{
    return(
        <div>
        <Image 
          src="/images/logo/logo.png" 
          className="md:w-[90px] md:h-[50px] w-[60px] h-[60px] object-contain" 
          alt="logo1" 
          width={100} 
          height={100}
          
        />
      </div>
      
    )
}
export default Logo;