"use client";
import { usePathname, useRouter } from "next/navigation";
import React, { useState } from "react";

type Props = {
  children: React.ReactNode;
};

const DashboardLayout = ({ children }: Props) => {
  const [redirected, setRedirected] = useState(false);
  const pathname = usePathname();

  // handle submit
  const router = useRouter();
  const handleSubmit = async () => {
    // redirect to conversation
    // TODO: Add channel id validation and redirect to the correct channel
    // We can use pathname to validate that pathname is not the current one
    if (
      !redirected &&
      pathname !== "/conversation/c/UCKZozRVHRYsYHGEyNKuhhdA"
    ) {
      setRedirected(true);
      router.push(`conversation/c/UCKZozRVHRYsYHGEyNKuhhdA`);
    }
  };
  return (
    <div className="overflow-hidden w-full h-[100dvh] flex  text-zinc-300">
      <div className="h-full hidden md:w-[280px] md:flex flex-col flex-shrink-0 bg-zinc-900 min-h-[100dvh]">
        {/* Some sample conversations which will redirect on click */}
        <div
          onClick={handleSubmit}
          className="p-4 border-b border-zinc-800 cursor-pointer"
        >
          <div className="flex items-center justify-between p-4">
            <div className="flex items-center space-x-2">
              <div>
                {/* Channel details */}
                <div className="text-sm font-semibold">Sample channel</div>
                <div className="text-xs">Sample channel</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="w-full">{children}</div>
    </div>
  );
};

export default DashboardLayout;
