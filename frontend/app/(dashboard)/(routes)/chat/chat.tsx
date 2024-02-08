"use client";

import React from "react";

import { Form, FormControl, FormField, FormItem } from "@/components/ui/form";
import { useForm } from "react-hook-form";

type Props = {};

const Chat = (props: Props) => {
  return (
    <>
      <div className="flex flex-col h-[100dvh] bg-zinc-800">
        <div className="border-b relative border-zinc-700 px-4">NavBar</div>
        <div className="flex-grow overflow-y-auto"> Conversation</div>
        <div>Form</div>
      </div>
    </>
  );
};

export default Chat;
