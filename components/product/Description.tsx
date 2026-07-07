const Description = ({ description }: { description: string }) => {
  return (
    <div className="mt-8 ml-0 sm:ml-14 px-5 sm:px-12 mt-10">
      <p className="text-black text-3xl">Description</p>
      <p className="mt-5">{description}</p>
    </div>
  );
};

export default Description;
  