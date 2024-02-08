import React from "react";

type Props = {
  children: React.ReactNode;
};

const DashboardLayout = async ({ children }: Props) => {
  return (
    <div className="overflow-hidden w-full h-[100dvh] flex  text-white">
      <div className="h-full hidden md:w-[280px] md:flex flex-col flex-shrink-0 bg-zinc-900 min-h-[100dvh]">
        <p>SideBar</p>
      </div>
      <div className="w-full">{children}</div>
    </div>
  );
};

export default DashboardLayout;
