import { useSearchCard } from "@/hooks/useSearchCard";
import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

type Props = {};

const SearchCard = (props: Props) => {
  const searchCard = useSearchCard();
  const [loading, setLoading] = useState(false);
  return (
    <>
      <Dialog open={searchCard.isOpen} onOpenChange={searchCard.onClose}>
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

export default SearchCard;
