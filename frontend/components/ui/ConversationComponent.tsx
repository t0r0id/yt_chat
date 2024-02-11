import { Message, MessageRoleEnum } from "@/lib/types/conversation";
import React, { useEffect, useRef } from "react";
import { HiOutlineChatAlt2 } from "react-icons/hi";

interface IConversationComponent {
  messages: Message[];
}

const ConversationComponent: React.FC<IConversationComponent> = ({
  messages,
}) => {
  const lastElementRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    console.log("messages", messages);
    if (lastElementRef.current) {
      lastElementRef.current.scrollIntoView();
    }
  }, [messages]);
  const showLoading =
    messages[messages.length - 1]?.role === MessageRoleEnum.USER;
  return (
    <>
      {messages.map((message, index) => {
        return (
          <div key={message._id} className="my-2">
            {message.role === MessageRoleEnum.USER && (
              <div className="flex justify-end" key={index}>
                <div className="bg-blue-500 text-white p-2 rounded-lg">
                  {message.content}
                </div>
              </div>
            )}
            {message.role === MessageRoleEnum.ASSISTANT && (
              <div className="flex justify-start" key={index}>
                <div className="bg-gray-200 p-2 rounded-lg text-black">
                  {message.content}
                </div>
              </div>
            )}
          </div>
        );
      })}
    </>
  );
};

export default ConversationComponent;
