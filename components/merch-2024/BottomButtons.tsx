import React from "react";
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";

const BottomButtons = ({ currentPage, totalItems}) => {
  const totalPages = Math.ceil(totalItems/8);
  const getPaginationItems = () => {
    const items = [];
    for (let i = 1; i <= totalPages; i++) {
      items.push(
        <PaginationItem key={i}>
          <PaginationLink href={`?page=${i}`} isActive={i === currentPage}>
            {i}
          </PaginationLink>
        </PaginationItem>
      );
    }
    return items;
  };

  return (
    <Pagination className="my-5">
      <PaginationContent>
        <PaginationItem>
          {/* disable is not working for some reason so had to use opacity */}
          <PaginationPrevious
            href={`?page=${currentPage - 1}`}
            className={currentPage <= 1 ? "cursor-not-allowed opacity-50" : ""}
            aria-disabled={currentPage <= 1 ? "true" : "false"}
          />
        </PaginationItem>
        {getPaginationItems()}
        <PaginationItem>
          <PaginationNext
            href={`?page=${currentPage + 1}`}
            className={currentPage >= totalPages ? "cursor-not-allowed opacity-50" : ""}
            aria-disabled={currentPage >= totalPages ? "true" : "false"}
          />
        </PaginationItem>
      </PaginationContent>
    </Pagination>
  );
};

export default BottomButtons;