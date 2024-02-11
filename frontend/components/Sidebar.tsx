"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import Link from "next/link";
import { Plus, Trash2 } from "lucide-react";

import { ChannelType } from "@/lib/types/yt";
import { YtApiClient } from "@/lib/api/yt";
import { Button } from "@/components/ui/button";

type Props = {};

const Sidebar = (props: Props) => {
  const [channels, setChannels] = useState<ChannelType[]>([]);
  const pathName = usePathname();
  useEffect(() => {
    (async () => {
      const { data } = await YtApiClient.getUserChannels();
      if (data) {
        const channels = data as ChannelType[];
        setChannels(channels);
      }
    })();
  }, []);

  const handleChannelRemoval = async (channelId: string) => {
    const response = await YtApiClient.removeUserChannel(channelId);
    if (response) {
      const newChannels = channels.filter(
        (channel) => channel._id !== channelId
      );
      setChannels([...newChannels]);
    }
  };

  return (
    <div className="flex flex-col h-full w-full">
      <div className="mx-2 my-2">
        <Button
          className="flex w-full px-4 py-2 
          flex-grow overflow-hidden items-center gap-3 h-11 
          justify-start 
          text-sm rounded-md border cursor-pointer border-white/20
          bg-inherit text-inherit
          hover:text-white hover:bg-white/10
          transition-colors duration-200"
        >
          <Plus className="h-4 w-4" />
          <div>Add a new channel</div>
        </Button>
      </div>
      <div className="flex-grow overflow-y-auto mx-2 pb-2 space-y-1">
        {channels.map((channel) => (
          <div className="relative group" key={channel._id}>
            <Link
              href={`/conversation/c/${channel._id}`}
              className={cn(
                `text-md group flex p-3 w-full 
            justify-start font-medium cursor-pointer
            hover:text-white hover:bg-white/10 rounded-lg transition-colors duration-200
            `,
                pathName.split("/").at(-1) === channel._id
                  ? "bg-white/10 text-white"
                  : "text-inherit"
              )}
            >
              <div className="flex items-center flex-1">
                <img
                  src={channel.thumbnails?.[0]?.url?.toString()}
                  alt="Channel Thumbnail"
                  className="mr-2"
                />
                <div>{channel.title}</div>
              </div>
            </Link>
            <Button
              className="absolute right-1 top-1 p-1
            text-inherit space-x-1 bg-inherit
            hover:text-red-500
            rounded-md group-hover:block"
              onClick={() => handleChannelRemoval(channel._id)}
            >
              <Trash2 className="h-3 w-3" />
            </Button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Sidebar;
