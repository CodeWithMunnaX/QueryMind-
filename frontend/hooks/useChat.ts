"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useCallback, useState } from "react";

import { api, ApiError } from "@/lib/api";
import { genId } from "@/lib/utils";
import type { ChatTurn } from "@/types/analytics";

export function useChat(conversationId: string) {
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (message: string) => api.chat({ message, conversation_id: conversationId }),
  });

  const ask = useCallback(
    async (message: string) => {
      const trimmed = message.trim();
      if (!trimmed) return;

      const userTurn: ChatTurn = {
        id: genId("user"),
        role: "user",
        content: trimmed,
        createdAt: new Date().toISOString(),
      };
      setTurns((prev) => [...prev, userTurn]);

      try {
        const response = await mutation.mutateAsync(trimmed);
        setTurns((prev) => [
          ...prev,
          {
            id: genId("assistant"),
            role: "assistant",
            content: response.answer,
            response,
            createdAt: new Date().toISOString(),
          },
        ]);
        queryClient.invalidateQueries({ queryKey: ["history"] });
      } catch (err) {
        const message = err instanceof ApiError ? err.message : "Something went wrong. Please try again.";
        setTurns((prev) => [
          ...prev,
          {
            id: genId("assistant-error"),
            role: "assistant",
            content: message,
            isError: true,
            createdAt: new Date().toISOString(),
          },
        ]);
      }
    },
    [mutation, queryClient]
  );

  const regenerate = useCallback(
    (question: string) => {
      ask(question);
    },
    [ask]
  );

  const reset = useCallback(() => setTurns([]), []);

  return {
    turns,
    ask,
    regenerate,
    reset,
    isLoading: mutation.isPending,
  };
}
