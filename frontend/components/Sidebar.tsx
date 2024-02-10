"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import Link from "next/link";

import { ChannelType } from "@/lib/types/yt";
import { YtApiClient } from "@/lib/api/yt";

type Props = {};

const Sidebar = (props: Props) => {
  const [channels, setChannels] = useState<ChannelType[]>([]);
  const pathName = usePathname();
  useEffect(() => {
    (async () => {
      const { data } = await YtApiClient.getChannels();
      if (data) {
        const channels = data as ChannelType[];
        console.log(channels[0]);
        console.log(pathName.split("/").at(-1));
        setChannels(channels);
      }
    })();
  }, []);

  return (
    <>
      <div className="flex flex-col space-y-2 text-white-500">
        {channels.map((channel) => (
          <Link
            href={`/conversation/c/${channel._id}`}
            key={channel._id}
            className={cn(
              `text-md group flex p-3 w-full 
            justify-start font-medium cursor-pointer
            hover:text-white hover:bg-white/10 rounded-lg transition`,
              pathName.split("/").at(-1) === channel._id
                ? "bg-white/10 text-white"
                : "text-zinc-400"
            )}
          >
            <div className="flex items-center flex-1">
              <img
                src={channel.thumbnails?.[0]?.url?.toString()}
                alt="Channel Thumbnail"
                className="mr-2"
              />
              {channel.title}
            </div>
          </Link>
        ))}
      </div>
    </>
  );
};

export default Sidebar;
