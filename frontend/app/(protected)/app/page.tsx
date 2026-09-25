import { Suspense } from "react";

import { ChatPanel } from "@/components/chat/ChatPanel";

export default function AskDataPage() {
  return (
    <Suspense fallback={null}>
      <ChatPanel />
    </Suspense>
  );
}
