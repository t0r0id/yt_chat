"use client";

import React, { useEffect, useState } from "react";

import { useForm } from "react-hook-form";
import * as z from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { SendHorizonalIcon } from "lucide-react";
import { Form, FormControl, FormField, FormItem } from "@/components/ui/form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApiClient } from "@/lib/api/conversation";

import {
  ConversationResponseType,
  ConversationType,
  ConversationResponseStatusEnum,
  MessageRoleEnum,
} from "@/lib/types/conversation";

import { ChannelType, ThumbnailType } from "@/lib/types/yt";

const formSchema = z.object({
  message: z.string().min(1, { message: "Please enter a message" }),
});

type Props = {
  activeChannel: ChannelType;
  setActiveChannel: (channel: ChannelType) => void;
};

const ConversationComponent = ({ activeChannel, setActiveChannel }: Props) => {
  const [conversation, setConversation] = useState<ConversationType>();
  const [lastResponse, setLastResponse] =
    useState<ConversationResponseType | null>(null);

  useEffect(() => {
    const startConversation = async () => {
      const { data: conversationId } = await ApiClient.getConversationId(
        activeChannel.id
        // "UCKZozRVHRYsYHGEyNKuhhdA"
      );

      if (conversationId) {
        let conversationHistory: ConversationResponseType[] = [];
        const response = await ApiClient.getConversationHistory(conversationId);
        if (response.data) {
          conversationHistory = response.data as ConversationResponseType[];
        }
        setConversation({
          id: conversationId,
          conversationHistory: conversationHistory,
        });
      }
    };
    startConversation();
  }, [activeChannel]);

  useEffect(() => {
    setLastResponse(null);
  }, [conversation]);

  const resetConversation = async () => {
    const { data: conversationId } = await ApiClient.initiateConversation(
      activeChannel.id
    );
    if (conversationId) {
      setConversation({
        id: conversationId,
        conversationHistory: [],
      });
    }
  };

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      message: "",
    },
  });

  const isLoading = form.formState.isSubmitting;
  const handleMessageSubmit = async (values: z.infer<typeof formSchema>) => {
    console.log(values.message);
  };

  return (
    <>
      <div className="flex flex-col h-[100dvh] bg-zinc-800 items-center">
        <div className="border-b relative border-zinc-700 px-4 w-full">
          NavBar
        </div>
        <div className="flex-grow overflow-y-auto w-full lg:w-5/6">
          Conversation
        </div>
        <div className="w-full lg:w-5/6">
          <Form {...form}>
            <form
              onSubmit={form.handleSubmit(handleMessageSubmit)}
              className="w-full my-4 p-3 mx-auto relative
               flex items-center justify-between bg-gray-700 rounded-lg border border-zinc-500"
            >
              <FormField
                control={form.control}
                name="message"
                render={({ field }) => (
                  <FormItem className="w-[90%]">
                    <FormControl>
                      <Input
                        disabled={isLoading}
                        placeholder="Type your message..."
                        type="text"
                        className="bg-[inherit] text-md outline-none border-0"
                        {...field}
                      />
                    </FormControl>
                  </FormItem>
                )}
              ></FormField>
              <Button
                disabled={isLoading}
                type="submit"
                className="bg-[inherit] text-inherit"
              >
                <SendHorizonalIcon />
              </Button>
            </form>
          </Form>
        </div>
      </div>
    </>
  );
};

export default ConversationComponent;
