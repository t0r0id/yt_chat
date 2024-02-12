import React from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@radix-ui/react-avatar";
import { ChannelStatusEnum } from "@/lib/types/yt";
import { cn } from "@/lib/utils";

type Props = {
  thumbnail: URL | undefined;
  title: string;
  status?: ChannelStatusEnum;
};

const ChannelCard = ({
  thumbnail = undefined,
  title,
  status = ChannelStatusEnum.ACTIVE,
}: Props) => {
  return (
    <div className="flex items-center flex-1 gap-2">
      <Avatar>
        <AvatarImage
          src={thumbnail?.toString()}
          alt={title + " thumbnail"}
          className={cn("h-12 w-12 rounded-full")}
        />
        <AvatarFallback>
          <Avatar>
            <AvatarImage
              src="https://www.gstatic.com/youtube/img/branding/favicon/favicon_144x144.png"
              className={cn("h-12 w-12 rounded-full")}
            ></AvatarImage>
          </Avatar>
        </AvatarFallback>
      </Avatar>

      <div>
        <div className="line-clamp-1">{title}</div>
        {status === ChannelStatusEnum.INACTIVE && (
          <div className="text-xs text-zinc-400">(Inactive)</div>
        )}
      </div>
    </div>
  );
};

export default ChannelCard;
