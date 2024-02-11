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
  Message,
} from "@/lib/types/conversation";

import { ChannelType, ThumbnailType } from "@/lib/types/yt";
import Image from "next/image";
import useMessages from "@/hooks/useMessage";
import ConversationComponent from "@/components/ui/ConversationComponent";
import { BsArrowUpCircle } from "react-icons/bs";

const formSchema = z.object({
  message: z.string().min(1, { message: "Please enter a message" }),
});

type Props = {
  activeChannel: ChannelType;
  setActiveChannel: (channel: ChannelType) => void;
};

const Page = ({ params }: { params: { id: string } }) => {
  const [conversation, setConversation] = useState<ConversationType>();
  const [userMessage, setUserMessage] = useState("");

  const [activeChannel, setActiveChannel] = useState<ChannelType>();
  const [channelReady, setIsChannelReady] = useState(false);
  const [isMessagePending, setIsMessagePending] = useState(false);
  const { messages, userSendMessage, setMessages, systemSendMessage } =
    useMessages(params.id);
  useEffect(() => {
    // Initialising channel and chat
    async function fetchChannelDetails() {
      const { data: channelDetails } = await ApiClient.getChannelDetails(
        params.id
      );
      if (channelDetails) {
        setActiveChannel(channelDetails);
        setIsChannelReady(true);
      }
    }

    async function fetchChatDetails() {
      const { data: conversationId } = await ApiClient.getConversationId(
        params.id
      );
      if (conversationId) {
        const { data: conversationHistory } =
          await ApiClient.getConversationHistory(conversationId);
        setConversation({
          _id: conversationId,
          conversationHistory: conversationHistory,
        });
        setMessages(conversationHistory);
      }
    }
    fetchChannelDetails();
    fetchChatDetails();
  }, [params.id]);

  const resetConversation = async () => {
    const { data: conversationId } = await ApiClient.initiateConversation(
      params.id
    );
    if (conversationId) {
      setConversation({
        _id: conversationId,
        conversationHistory: [],
      });
      setMessages([]);
    }
  };

  useEffect(() => {
    const textarea = document.querySelector("textarea");
    if (textarea) {
      textarea.style.height = "auto";

      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  }, [userMessage]);

  const submit = () => {
    if (!userMessage || userMessage.trim().length === 0) {
      return;
    }

    setIsMessagePending(true);
    userSendMessage(userMessage);
    setUserMessage("");

    const url = `${process.env.NEXT_PUBLIC_BACKEND_URL}/chat/${
      conversation?._id
    }/message_stream?user_message=${encodeURI(userMessage)}`;
    const events = new EventSource(url);
    events.onmessage = (event: MessageEvent) => {
      const parsedData: Message = JSON.parse(event.data);
      parsedData.status =
        ConversationResponseStatusEnum[
          parsedData.status as unknown as keyof typeof ConversationResponseStatusEnum
        ];
      systemSendMessage(parsedData);

      if (
        parsedData.status === ConversationResponseStatusEnum.COMPLETED ||
        parsedData.status === ConversationResponseStatusEnum.FAILED
      ) {
        events.close();
        setIsMessagePending(false);
      }
    };
  };

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Enter") {
        event.preventDefault();
        if (!isMessagePending) {
          submit();
        }
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [submit]);

  if (!channelReady) {
    return (
      <div className="flex items-center justify-center h-screen bg-zinc-800">
        <div className="text-center text-2xl">
          Getting your conversation ready...
        </div>
      </div>
    );
  }
  return (
    <>
      <div className="flex flex-col h-[100dvh] bg-zinc-800 items-center">
        <div className="border-b relative border-zinc-700 px-4 w-full">
          <div className="flex items-center justify-between py-4 mx-20">
            <div className="flex items-center">
              <Image
                src={activeChannel?.thumbnails?.[0].url.toString()!}
                alt={activeChannel?.title!}
                className="h-12 w-12 rounded-full"
                width={48}
                height={48}
              />
              <div className="ml-2">
                <h1 className="text-lg font-bold text-white">
                  {activeChannel?.title}
                </h1>
              </div>
            </div>
            <div>
              <Button
                onClick={resetConversation}
                className="bg-zinc-700 text-white"
              >
                Reset
              </Button>
            </div>
          </div>
        </div>
        <div className="flex-grow overflow-y-auto w-full lg:w-5/6">
          <ConversationComponent messages={messages} />
        </div>
        <div className="w-full lg:w-5/6">
          <div className="relative flex h-[70px] w-full items-center ">
            <textarea
              rows={1}
              className="box-border w-full flex-grow resize-none overflow-hidden px-5 py-3 pr-10 text-gray-90 placeholder-gray-60 outline-none  bg-gray-700 rounded-lg border border-zinc-500"
              placeholder={"Start typing your question..."}
              value={userMessage}
              onChange={(e) => setUserMessage(e.target.value)}
            />
            <button
              disabled={isMessagePending || userMessage.length === 0}
              onClick={submit}
              className="z-1 absolute right-6 top-1/2 mb-1 -translate-y-1/2 transform rounded text-gray-90 opacity-80 enabled:hover:opacity-100 disabled:opacity-30"
            >
              <BsArrowUpCircle size={24} />
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default Page;
