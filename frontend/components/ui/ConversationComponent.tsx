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
          <div key={message.id} className="my-2">
            {message.role === MessageRoleEnum.USER && (
              <>
                <p>You.</p>
                {/* TODO: Add user image? */}
                <div className="flex border-b border-zinc-700" key={index}>
                  <div className="text-white p-2 rounded-lg">
                    {message.content}
                  </div>
                </div>
              </>
            )}
            {message.role === MessageRoleEnum.ASSISTANT && (
              <>
                <p>Assistant.</p>
                <div className="flex border-b border-zinc-700" key={index}>
                  <div className="text-white p-2 rounded-lg">
                    {message.content}
                  </div>
                </div>
              </>
            )}
          </div>
        );
      })}
      <div ref={lastElementRef}></div>
    </>
  );
};

export default ConversationComponent;
