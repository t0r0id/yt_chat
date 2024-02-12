import { SearchCardProvider } from "@/components/search-card-provider";
import Sidebar from "@/components/sidebar-2";
import React from "react";

type Props = {
  children: React.ReactNode;
};

const DashboardLayout = async ({ children }: Props) => {
  return (
    <div className="overflow-hidden w-full h-[100dvh] flex  text-zinc-400">
      <div className="h-full hidden md:w-[280px] md:flex flex-col flex-shrink-0 bg-zinc-900 min-h-[100dvh]">
        <Sidebar />
      </div>
      <div className="w-full">
        <SearchCardProvider />
        {children}
      </div>
    </div>
  );
};

export default DashboardLayout;
