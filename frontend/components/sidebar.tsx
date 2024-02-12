"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import Link from "next/link";
import { Trash2 } from "lucide-react";

import { ChannelStatusEnum, ChannelType } from "@/lib/types/yt";
import { YtApiClient } from "@/lib/api/yt";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Avatar, AvatarFallback, AvatarImage } from "@radix-ui/react-avatar";
import AddChannelButton from "./add-channel-button";
import ChannelCard from "./channel-card";

type Props = {};

const Sidebar = (props: Props) => {
  const [channels, setChannels] = useState<ChannelType[]>([]);
  const [dialougeOpen, setDialougeOpen] = useState(false);
  const pathName = usePathname();
  useEffect(() => {
    (async () => {
      const { data } = await YtApiClient.getUserChannels();
      if (data) {
        const channels = data as ChannelType[];
        setChannels(channels);
      }
    })();
  }, [dialougeOpen]);

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
        <AddChannelButton open={dialougeOpen} setOpen={setDialougeOpen} />
      </div>
      <div className="flex-grow overflow-y-auto mx-2 pb-2 space-y-1">
        {channels.map((channel) => (
          <div className="relative group" key={channel._id}>
            <Link
              href={
                channel.status === ChannelStatusEnum.ACTIVE
                  ? `/conversation/c/${channel._id}`
                  : ""
              }
              className={cn(
                `text-md group flex p-3 w-full 
            justify-start font-medium cursor-pointerrounded-lg`,
                channel.status === ChannelStatusEnum.ACTIVE
                  ? "hover:text-white hover:bg-white/10 transition-colors duration-200"
                  : "opacity-50",
                pathName.split("/").at(-1) === channel._id
                  ? "bg-white/10 text-white"
                  : "text-inherit"
              )}
            >
              <ChannelCard
                title={channel.title}
                thumbnail={channel.thumbnails?.[0]?.url}
                status={channel.status}
              />
            </Link>

            <TooltipProvider delayDuration={200}>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    className="absolute right-1 top-1 p-1
                              text-inherit space-x-1 bg-inherit
                              hover:text-red-500
                              rounded-md group-hover:block"
                    onClick={() => handleChannelRemoval(channel._id)}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p className="text-xs text-inherit">Remove channel</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Sidebar;
