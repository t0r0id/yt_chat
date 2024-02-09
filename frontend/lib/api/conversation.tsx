import axios, { AxiosResponse, AxiosError } from "axios";
axios.defaults.withCredentials = true;

export class ApiClient {
  public static async initiateConversation(
    channelId: string,
    headers?: any
  ): Promise<AxiosResponse> {
    let requestConfig = {
      method: "post",
      url: `${process.env.NEXT_PUBLIC_BACKEND_URL}/chat/initiate`,
      data: {
        channel_id: channelId,
      },
      headers: headers,
    };
    return await axios.request(requestConfig);
  }

  public static async getConversationId(
    channelId: string,
    headers?: any
  ): Promise<AxiosResponse> {
    let requestConfig = {
      method: "post",
      url: `${process.env.NEXT_PUBLIC_BACKEND_URL}/chat/get_chat_id`,
      data: {
        channel_id: channelId,
      },
      headers: headers,
    };
    return await axios.request(requestConfig);
  }

  public static async getConversationHistory(
    conversationId: string,
    headers?: any
  ): Promise<AxiosResponse> {
    let requestConfig = {
      method: "post",
      url: `${process.env.NEXT_PUBLIC_BACKEND_URL}/chat/history`,
      data: {
        chat_id: conversationId,
      },
      headers: headers,
    };
    return await axios.request(requestConfig);
  }
}
