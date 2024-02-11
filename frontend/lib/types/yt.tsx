import { hasBaseId, hasId } from "@/lib/types/common";

export interface ThumbnailType {
  url: URL;
  width: number;
  height: number;
}
export interface ChannelType extends hasBaseId {
  title: string;
  description?: string;
  url?: URL;
  thumbnails?: ThumbnailType[];
}
