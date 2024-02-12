// hooks/useMessages.js
import { useState } from "react";
import { v4 as uuidv4 } from "uuid";
import {
  ConversationResponseStatusEnum,
  Message,
  MessageRoleEnum,
} from "@/lib/types/conversation";

const useMessages = (channelId: string) => {
  const [messages, setMessages] = useState<Message[]>([]);

  const userSendMessage = (content: string) => {
    setMessages((prevMessages) => [
      ...prevMessages,
      {
        id: uuidv4(),
        content,
        role: MessageRoleEnum.USER,
        channelId: channelId,
        created_at: new Date(),
        status: ConversationResponseStatusEnum.IN_PROGRESS,
      },
    ]);
  };

  const systemSendMessage = (message: Message) => {
    setMessages((prevMessages) => {
      const existingMessageIndex = prevMessages.findIndex(
        (msg) => msg.id === message.id || msg.id === "initial"
      );
      // Update the existing message
      if (existingMessageIndex > -1) {
        const updatedMessages = [...prevMessages];
        updatedMessages[existingMessageIndex] = message;
        return updatedMessages;
      }

      // Add a new message if it doesn't exist
      return [...prevMessages, message];
    });
  };

  return {
    messages,
    userSendMessage,
    setMessages,
    systemSendMessage,
  };
};

export default useMessages;
