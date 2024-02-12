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

type Props = {};

const AddChannelButton = (props: Props) => {
  const [loading, setLoading] = useState(false);
  return (
    <>
      <Dialog>
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
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex justify-center items-center flex-col gap-y-4 pb-2">
              <div className="flex items-center gap-x-2 font-bold py-1">
                Search Channels
              </div>
            </DialogTitle>
          </DialogHeader>
          <DialogFooter>
            <Button size="lg" className="w-full" disabled={loading}>
              Search
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default AddChannelButton;
