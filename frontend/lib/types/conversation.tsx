import { dict } from "@/lib/types/common";

export enum ConversationResponseStatusEnum {
  COMPLETED = "completed",
  IN_PROGRESS = "in_progress",
  REJECTED = "rejected",
  REGENRATED = "regenerated",
  FAILED = "failed",
}

export enum MessageRoleEnum {
  USER = "user",
  ASSISTANT = "assistant",
}

export interface ConversationResponseType {
  id: string;
  role: MessageRoleEnum;
  content: string;
  additional_kwargs: dict;
  status: ConversationResponseStatusEnum;
  status_reason: string;
}

export interface ConversationType {
  _id: string;
  conversationHistory?: ConversationResponseType[];
}

//TODO Remove duplicate interface Message
export interface Message {
  id: string;
  content: string;
  role: MessageRoleEnum;
  channelId: string;
  created_at: Date;
  status: ConversationResponseStatusEnum;
}
