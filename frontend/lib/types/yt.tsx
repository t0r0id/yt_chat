import { hasId } from "@/lib/types/common";

export interface ThumbnailType {
  url: URL;
  width: number;
  height: number;
}

export enum ChannelStatusEnum {
  ACTIVE = "active",
  INACTIVE = "inactive",
}
export interface ChannelType extends hasId {
  title: string;
  description?: string;
  url?: URL;
  thumbnails?: ThumbnailType[];
  status: ChannelStatusEnum;
}
