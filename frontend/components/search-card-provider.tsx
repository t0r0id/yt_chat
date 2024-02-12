"use client";

import { useEffect, useState } from "react";
import SearchCard from "@/components/search-card";
export const SearchCardProvider = () => {
  const [isMounted, setIsMounted] = useState(false);
  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) return null;

  return (
    <>
      <SearchCard />
    </>
  );
};
