"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { ComboBoxItemType, SearchCombobox } from "./search-combobox";
import { ChannelType } from "@/lib/types/yt";
import { YtApiClient } from "@/lib/api/yt";
import toast from "react-hot-toast";

type Props = {
  open: boolean;
  setOpen: (isOpen: boolean) => void;
};

const AddChannelButton = ({ open, setOpen }: Props) => {
  const [loading, setLoading] = useState(false);
  const [channels, setChannels] = useState<ComboBoxItemType[]>([]);
  const [selectedChannel, setSelectedChannel] = useState<string | undefined>(
    undefined
  );

  const handleChannelAddition = async () => {
    if (selectedChannel !== undefined) {
      setLoading(true);

      await YtApiClient.initiateOnboardingRequest(selectedChannel)
        .then(() => {
          toast("Channel Onboarding Request Sent..🚀");
        })
        .catch((error) => {
          toast.error("Channel Onboarding Request Failed");
        })
        .finally(() => {
          setLoading(false);
          setSelectedChannel(undefined);
          setChannels([]);
          setOpen(false);
        });
    }
  };

  const handleChannelSearchChanged = async (query: string) => {
    if (query.length <= 3) {
      setChannels([]);
    } else {
      const response = await YtApiClient.searchChannels(query);
      if (response && response.data) {
        setChannels(
          response.data?.map((channel: ChannelType) => ({
            value: channel._id.toString(),
            label: channel.title,
            thumbnail: channel.thumbnails?.[0]?.url,
          })) || []
        );
      }
    }
  };

  return (
    <>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger asChild>
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
        </DialogTrigger>
        <DialogContent className="bg-zinc-900 border border-zinc-800 shadow-lg p-4 rounded-md w-full max-w-[520px] mx-auto">
          <DialogHeader>
            <DialogTitle className="flex items-left flex-col gap-y-4 pb-2">
              <div className="flex items-center gap-x-2 font-bold py-1 text-zinc-400">
                Add a new channel
              </div>
            </DialogTitle>
          </DialogHeader>
          <DialogFooter>
            <div className="flex flex-col gap-5 w-full">
              <SearchCombobox
                searchPlaceholder="Search channels"
                noResultsMsg="No channels found"
                selectItemMsg="Select a channel"
                className="w-full bg-zinc-700 text-zinc-400"
                items={channels}
                onSelect={(value) => {
                  setSelectedChannel(value);
                }}
                onSearchChange={handleChannelSearchChanged}
                value={selectedChannel}
              />
              <Button
                size="lg"
                className="w-full px-4 py-2 
          flex-grow overflow-hidden h-11 
          text-sm rounded-md border cursor-pointer border-white/20
          bg-inherit text-zinc-400
          hover:text-white hover:bg-white/10
          transition-colors duration-200"
                disabled={loading}
                onClick={async () => {
                  handleChannelAddition();
                }}
              >
                Add
              </Button>
            </div>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default AddChannelButton;
