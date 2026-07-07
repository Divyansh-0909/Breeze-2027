export default function Header() {
    return (
      <div className="top flex flex-col items-center text-center">
        <h2 className="head mt-8 text-[1.5rem] sm:text-[2.5rem] lg:text-[2.5rem] font-medium">Meet the Dream Team</h2>
        <h1 className="lg:text-[4rem] text-[2rem] sm:text-[3rem] font-semibold mb-4 font-fraunces-italic-bold">
          The People That Made Breeze Possible!
        </h1>
        <p className="toptext text-base text-muted-foreground w-[90%] lg:max-w-[65%] sm:w-[65%] font-medium">
          Venture into the inner sanctum of Breeze, the magnetic college fest of
          Shiv Nadar University, where innovation thrives and inspiration reigns.
          Get to know the alchemists who blend passion, dedication, and artistry
          to bring this spectacular event to life!
        </p>
      </div>
    );
  }
  