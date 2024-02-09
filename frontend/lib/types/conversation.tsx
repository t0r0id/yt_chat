import { hasId, dict } from "@/lib/types/common";

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

export interface ConversationResponseType extends hasId {
  role: MessageRoleEnum;
  content: string;
  additional_kwargs: dict;
  status: ConversationResponseStatusEnum;
  status_reason: string;
}

export interface ConversationType extends hasId {
  conversationHistory?: ConversationResponseType[];
}
